# Field image reference remediation details

## Contents

- [Why inventory-verified, not a blind rewrite](#why-inventory-verified-not-a-blind-rewrite)
- [Classification](#classification)
- [The five-step pattern](#the-five-step-pattern)
- [Usage](#usage)
- [Real executor](#real-executor)
- [Provenance](#provenance)

## Why inventory-verified, not a blind rewrite

The other remediation skills apply a rewrite rule to every match, assuming the rewrite target exists after migration. That assumption does not hold
here: not every file an old field value references necessarily migrated. Rewriting blindly would "fix" a reference to a file that was never migrated,
hiding a real data-loss problem behind an apparently successful rewrite. `classify_field_images` therefore cross-references each item's referenced
filename against a real library inventory before any rewrite is proposed.

## Classification

| Status | Meaning | Proposed fix? |
|---|---|---|
| `no_img_tag` | Field has no `img` tag at all (blank or plain text) | No |
| `img_no_src` | An `img` tag with no `src` (empty broken-image placeholder) | No: no path to fix |
| `matched` | Referenced filename exists in the inventory | Yes: rewrite the path segment |
| `missing` | Referenced filename does not exist anywhere in the inventory | No: genuinely absent, report it |

Every item is classified and reported, including ones with no proposed fix. `missing` and `img_no_src` items are never silently dropped.

## The five-step pattern

1. **Get source field data.** Read the rich-text field's stored value per item. A live-tenant read, out of scope here (caller-supplied).
2. **Extract paths.** `classify_field_images` extracts the embedded `img src` and decodes it to a bare filename.
3. **Compare to a destination inventory.** The filename is looked up case-insensitively against a caller-supplied `{filename.lower(): relative_url}`
   inventory, also caller-collected.
4. **Gap analysis.** Every item is classified and `generate_gap_report` renders the full set as a reviewer-facing Markdown report, naming every
   `missing` and `matched` item individually.
5. **Remediation.** `plan_field_image_remediation` proposes a rewrite only for `matched` items; `apply_field_image_remediation` applies it under the same
   three-gate write safety.

## Usage

```python
from link_rules import load_ruleset
from field_image_remediation import plan_field_image_remediation, generate_gap_report, apply_field_image_remediation

# items: {source_id: field_value_html}, inventory: {filename.lower(): relative_url}
plan = plan_field_image_remediation(items, inventory=inventory, ruleset=load_ruleset("rules.json"))
print(generate_gap_report(plan))  # step 4: reviewer-facing gap report, before any write
result = apply_field_image_remediation(plan, executor=my_executor, dry_run=False, confirm=plan.confirmation_token)
```

## Real executor

`scripts/link-remediation/spo-remediate-field-image-references.ps1` reads a `FieldImageRemediationPlan.to_dict()`-shaped JSON file and, per `changed_items` entry
(`source_id` is the item's Id), overwrites `-FieldName` on `-ListName` with `Set-PnPListItem`.

```bash
pwsh -File scripts/link-remediation/spo-remediate-field-image-references.ps1 -PlanPath plan.json -ListName "Authors" -FieldName "Picture" -SiteUrl "https://tenant.sharepoint.com/sites/Test" -Execute -ConfirmToken REMEDIATE-SPO-FIELD-IMAGES
```

## Provenance

Generalized from a source-repository diagnostic script (`a diagnostic script`) that cross-referenced a Authors list's embedded picture field
against a live document-library inventory. Identified in the Phase 9 exhaustive source audit (`temp/phase9-source-audit/file-tracking.json`) as a distinct,
valuable mechanism initially under-scoped there, then corrected after direct user confirmation that the pattern was used and valuable. The source's
hardcoded library-segment strings and CSV file I/O were replaced by an injected `RewriteRuleset` and in-memory dicts; the classification logic (extract
`img src`, decode URL-encoding, case-insensitive filename lookup, four-way status) is a faithful generalization. Source repository only.
