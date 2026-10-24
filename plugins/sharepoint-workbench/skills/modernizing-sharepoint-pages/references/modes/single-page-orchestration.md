# Single SharePoint 2016 Page Migration

Detailed orchestration contract for one explicitly identified SharePoint 2016
classic page and one SharePoint Online target environment. The entry point is
`skills/sp-dynamic-aspx-page-migration/SKILL.md`.

## Contents

- [Scope and required input](#scope-and-required-input)
- [Orchestration stages](#orchestration-stages)
- [Safety and failure gates](#safety-and-failure-gates)
- [Capability map](#capability-map)
- [Evidence and completion](#evidence-and-completion)

## Scope and required input

This is a cross-site transformation from SharePoint 2016 to SharePoint Online,
not an in-place SPO page conversion. The skill coordinates existing discovery,
modernization, link-remediation, publication, validation, inventory, and
reporting capabilities; it does not replace them or authorize tenant writes
by itself.

Before planning, require:

- `SiteName`
- source `ServerRelativeUrl` or an unambiguous inventory handoff
- target environment: `dev`, `test`, or `prod`
- the matching `config-spo-<environment>.psd1`
- an independently bounded target page path
- permission to read the SP2016 source and, only after approval, write SPO

Resolve the page against the authoritative local inventory. Do not guess from
the title, select a nearby page, or silently reduce the requested path. Require
exactly one record. Publishing pages, home pages, custom layouts, unsupported
web parts, and unresolved dependencies need explicit disposition.

## Orchestration stages

### 1. Resolve and baseline the source page

Use `sp-page-inventory-agent` and the existing SP2016 inventory as the page
identity and source baseline. Capture source URL, page type, layout, migration
plan, web-part classification, title, modified time, visible content
expectations, links, images, and target path.

If the inventory is stale or unavailable, route to
`sp-page-inventory` first. Its config must contain `Source.SiteUrl` and
`Source.ReadOnly = $true`.

**Output:** page-scoped source baseline and unique target identity.

### 2. Assess the page and select a conversion pattern

Use `sharepoint-analyze-aspx-pages` on exported source material when component
structure is not already classified. Treat `Unknown`, `PARTIAL`, `EMPTY`, and
`FAILED` as real outcomes, not successful conversion inputs.

Choose the pattern using page type, source layout, ordered web-part signature
(including hidden/closed state), mapping results, unsupported components,
cross-site target approach, and special handling (publishing, home page, or
zero-part status). A high mapping percentage does not prove conversion fidelity.

**Output:** classified component inventory, selected pattern, and disposition
for every unsupported or unmapped component.

### 3. Extract content, links, and assets

Use the approved SP2016 read-only extraction path to obtain page and web-part
content, rendered HTML, list/view evidence, connected-consumer overrides, and
referenced images.

Use `sharepoint-extract-links` for a complete classified link inventory.
Distinguish absolute, server-relative, protocol-relative, `mailto`, anchor,
and malformed links. `EMPTY` means readable content contained no links; it is
not equivalent to `FAILED`.

Build an image/file inventory before proposing rewrites. Do not rewrite a
reference based only on a similar filename. For rich-text field images, use
inventory-verified classification from
`sharepoint-remediate-field-image-references`.

**Output:** source content package, link and image inventories, and extraction
problems or gaps.

### 4. Select layout and build the conversion manifest

Use `sharepoint-convert-aspx-pages` to evaluate declarative layout rules and
map classified components. Rules are data and must use that skill's restricted
evaluator. Name unsupported web parts and connected-consumer gaps in the
manifest.

Use site structural chrome and a page preview when available;
`sharepoint-compose-page-preview` can combine content with navigation, header,
logo, and breadcrumbs. Use `sharepoint-generate-conversion-report` for a
reviewer-facing summary of mappings, layout confidence, and every gap. These
steps do not write to the tenant.

**Output:** conversion manifest, preview when available, and conversion report.

### 5. Review and gate the package

Stop if the manifest is missing, invalid, partial without an approved
disposition, or includes unsupported components without a documented
replacement or manual action.

Require human review for publishing pages/custom publishing layouts, home-page
replacement, an existing target page, permissions or metadata copying, and
unresolved links, images, users, terms, lists, or connected consumers. Also
require review for any page pattern without a previously accepted
representative. Cross-site movement adds link, file, list, user, and taxonomy
risk; do not treat it as in-place SPO conversion.

**Output:** approved page package and explicit execution authorization, or a
blocked disposition naming the gaps.

### 6. Convert or publish with an approved executor

Select the executor based on the approved package:

- `sp-page-publish` or the repository wave publisher for the existing
  `Add-PnPPage` page-package route with mapped text/image parts.
- `sharepoint-convert-page-to-modern` when supported `ConvertTo-PnPPage` and
  caller-supplied field mappings are appropriate.
- `sharepoint-publish-aspx-to-sharepoint` only to build a plan; it does not
  perform tenant writes.

Never upload raw `.aspx` to SPO. Use supported modern-page creation or
transformation APIs. Dry-run is the default. A real write requires the selected
executor's explicit `-Execute` and confirmation-token gates.

For duplicate targets, require an explicit `Reject`, `Approve`, or `Skip`
decision. Never overwrite by implication.

**Output:** publication receipt with target URL, page and asset results,
duplicate decision, logs, and tool/configuration identity.

Accordion output (Portale-Healthy trial): the planner's `-AccordionOutput Spfx` emits the
`bc-accordion-group` web part with `columns` from `-AccordionColumns` (default 2) in
ordinary `OneColumn` sections (full-width sections accept only image/hero parts); `Native` emits collapsible sections. The publisher clears the `Home`
template's stock web parts (`$page.Sections.Clear()`). See `dynamic-page-conversion-lessons.md`.

### 7. Validate the published page independently

Owner decision: validation is by user acceptance. Do not write check scripts; ask the owner to
review the page. See `dynamic-page-conversion-lessons.md`. The checklist below lists what the owner
reviews.

Never treat a successful write command as proof of correctness. Read-only
validation must confirm target existence and identity; expected layout,
sections, columns, web parts, text, and images; required metadata and literal
field values; publication state; explicit disposition of resolved, broken,
skipped, or unresolvable links; and that no declared gap was silently dropped.

Use `sharepoint-validate-page-migration` for page/field validation and
`sharepoint-validate-link-integrity` with an appropriate resolver for links.
`UNRESOLVABLE` is not a passing result.

**Output:** independent PASS/FAIL validation report with named findings.

### 8. Remediate links only after review

If approved, use `sharepoint-remediate-links` for page-body HTML and the
caller-supplied declarative ruleset. Use
`sharepoint-remediate-document-content-links` only for links embedded inside
Office/PDF files, not page HTML. Use field-image remediation for rich-text list
fields.

All remediation is dry-run first, requires a real writer/executor and a
confirmation token, and must be followed by link-integrity validation.

**Output:** remediation plan/result, rollback information where supported, and
a new link-integrity report.

### 9. Update local inventory and report

Only after publication validation passes, invoke `sp-page-inventory`
with the source page identity and verified destination URL. It updates only
the selected environment's `Url-<env>` and derived `Status-<env>`; it does not
publish or query SharePoint.

Then synchronize the repository register and run
`page_migration_tracker.py sync` to refresh the tracker.

**Output:** updated `inventory/inventory-page.json`, migration register,
`inventory/page-migration-tracker.xlsx`, and publication/validation evidence.

## Safety and failure gates

- Never convert failed or unavailable extraction as if it were a blank page.
- Never silently drop unsupported web parts, links, images, metadata, or
  permissions.
- Never update inventory before independent publication validation.
- Never mark a page `Published` because a URL was merely planned.
- If a required capability cannot be resolved in the active runtime, stop and
  report the missing dependency; do not imitate its behavior.
- Preserve the original page until the target is accepted and rollback or
  recovery is documented.
- Keep diagnostic manifests, reports, receipts, and logs under the run's
  evidence directory; keep the real inventory workbook in `inventory/`.

## Capability map

| Concern | Capability |
| --- | --- |
| Source page identity and inventory | `sp-page-inventory-agent`, `sp-page-inventory` |
| ASPX analysis/classification | `sharepoint-analyze-aspx-pages` |
| Links and image references | `sharepoint-extract-links`, `sharepoint-remediate-links`, `sharepoint-remediate-field-image-references` |
| Layout/component mapping | `sharepoint-convert-aspx-pages` |
| Offline review | `sharepoint-compose-page-preview`, `sharepoint-generate-conversion-report` |
| SPO page creation/publication | `sp-page-publish`, `sharepoint-convert-page-to-modern` |
| Page/field validation | `sharepoint-validate-page-migration` |
| Link validation | `sharepoint-validate-link-integrity` |
| Inventory update/export | `sp-page-inventory`, `sp-page-inventory` |

## Evidence and completion

Keep the page baseline, source extraction, component mapping and gap
disposition, conversion manifest, preview/report, approvals, publication
receipt, independent validation, link-remediation evidence, and inventory
handoff traceable to the same source page and target environment.

Microsoft Learn references:

- Assessment and transformation:
  https://learn.microsoft.com/en-us/sharepoint/dev/transform/assess-sharepoint-modernization
- Transform classic pages:
  https://learn.microsoft.com/en-us/sharepoint/dev/transform/modernize-userinterface-site-pages
- .NET/page-transformation behavior:
  https://learn.microsoft.com/en-us/sharepoint/dev/transform/modernize-userinterface-site-pages-dotnet
- PnP PowerShell `ConvertTo-PnPPage`:
  https://pnp.github.io/powershell/cmdlets/ConvertTo-PnPPage.html

Microsoft treats assessment output as planning evidence and requires
representative-page validation before wave expansion. PnP Modernization is
open source and has no Microsoft support SLA. Repository skills add local
safety gates, explicit gap reporting, dry-run defaults, and inventory/register
handoffs.
