# Link remediation pipeline, outcomes and write safety

## Contents

- [The three-stage pipeline](#the-three-stage-pipeline)
- [Honest outcomes](#honest-outcomes)
- [Write safety: three independent gates](#write-safety-three-independent-gates)
- [PowerShell executors](#powershell-executors)
- [Why PowerShell is not the Python callback](#why-powershell-is-not-the-python-callback)

## The three-stage pipeline

`sharepoint-extract-links` -> `sharepoint-update-page-links` -> `sharepoint-validate-link-integrity`. Two more write-capable skills
sit beside the middle stage: `sharepoint-update-links-in-documents` (links inside Office files and PDFs) and
`sharepoint-update-rich-text-image-links` (an embedded `img` reference inside a rich-text list field). Extraction and
validation are read-only.

## Honest outcomes

Every module reports an outcome, and a partial or empty result is never presented as a pass (Phase 9 spec section 13).

| Outcome | Meaning |
|---|---|
| `OBSERVED` | The intended work succeeded (links found, or all writes succeeded) |
| `EMPTY` | Content read successfully but there was nothing to do or nothing matched |
| `PARTIAL` | Some sources or writes succeeded and some failed; both lists are populated |
| `FORBIDDEN` | The writer raised `PermissionError` (never flattened into a generic failure) |
| `NOT_SUPPORTED` | At least one document was a PDF with no injected `pdf_handler` (document-content skill) |
| `FAILED` | Every attempted source or write failed |

`EMPTY` and `FAILED` are deliberately distinct: "nothing found" and "nothing could be read" must never look alike.

## Write safety: three independent gates

No autonomous production write is reachable. Every write-capable module has the same three gates:

1. **Dry-run is the default.** `apply_*(plan)` with no further arguments changes nothing and reports `would_change`.
2. **A writer or executor must be injected.** The modules ship no tenant transport. Without the callable, a real apply raises
   `WriterRequired` (page links) or `ExecutorRequired` (document content, field images), never a silent no-op or faked success.
3. **A confirmation token is required.** `dry_run=False` additionally requires `confirm=plan.confirmation_token`, derived from the
   plan's own content. A stale or absent token raises `ConfirmationRequired`, so a plan cannot be applied after the underlying
   documents have changed.

## PowerShell executors

The PowerShell scripts are the real tenant-facing counterparts. Each is dry-run by default and writes nothing without
`-Execute` plus its exact token. All accept `-PlanPath`, `-SiteUrl`, `-ConfigPath`, `-ClientId`, `-TenantId`, `-TenantAdminUrl`.

| Script | Plan from | Writes | Parameters beyond the common set | Token |
|---|---|---|---|---|
| `spo-remediate-page-links.ps1` | `RemediationPlan.to_dict()` | `Set-PnPListItem` on `-TargetField` (default `CanvasContent1`) after resolving each document's `source` to a list item with `Get-PnPListItem` | `-TargetLibrary`, `-TargetField` | `REMEDIATE-SPO-LINKS` |
| `spo-remediate-document-content-links.ps1` | `DocumentRemediationPlan.to_dict()` | `Set-PnPFileCheckedOut`, `Add-PnPFile`, `Set-PnPFileCheckedIn -CheckinType MajorCheckIn` | `-TargetLibrary`, `-CheckinComment` | `REMEDIATE-SPO-DOCUMENT-LINKS` |
| `spo-remediate-field-image-references.ps1` | `FieldImageRemediationPlan.to_dict()` | `Set-PnPListItem` on `-FieldName` of `-ListName` per `changed_items` entry (`source_id` is the item Id) | `-ListName`, `-FieldName` | `REMEDIATE-SPO-FIELD-IMAGES` |

`-ConfigPath` defaults to three directories above the script (the repository root `config.psd1`). That default does not resolve from an
installed skill, so pass `-ConfigPath`, or `-SiteUrl`, `-ClientId` and `-TenantId`, explicitly. Connection resolution uses
`Get-WorkbenchConnectionConfig.ps1`.

## Why PowerShell is not the Python callback

Python cannot call a PowerShell script as an in-process callback, so the injected `writer` / `executor` and the `.ps1` executors are two
independent paths, not composed. Each plan JSON is the script's own contract, and some need augmenting before the script can act:

- Page links: each changed document must carry its already-computed `remediated_content` text (`RemediationPlan.to_dict()` reports only
  `source`, `changed` and `changes`).
- Document content: each changed document must carry `remediated_content_path`, an absolute local path to the already-rewritten file
  bytes written by the Python caller. The OOXML rewrite is Python-only logic that PowerShell does not reimplement.
- Field images: no augmentation; `changed_items` already carries the new value.

See each script's comment-based help for the exact shape.
