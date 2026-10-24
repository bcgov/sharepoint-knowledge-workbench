# Static ASPX document-library migration orchestration contract

## Contents

- [Inputs and identity](#inputs-and-identity)
- [Source analysis, download, and design-system conversion](#source-analysis-download-and-design-system-conversion)
- [Shared design-system assets](#shared-design-system-assets)
- [Destination preflight and provisioning](#destination-preflight-and-provisioning)
- [Publication and verification](#publication-and-verification)

## Inputs and identity

Require one exact source ASPX URL, the SP2016 source config, the SPO target
config, target library, and target folder. Reuse values already provided. The
source config must identify the supplied SP2016 host and declare
`Source.ReadOnly = $true`; the target config must resolve to the explicitly
selected site. For a DEV trial, verify the resolved URL is exactly
`https://target-tenant.sharepoint.com/sites/AG-Portal-WORKSPACE-DEV`.

Before downloading, classify the source item using available library and item
metadata, page inventory, and page structure or browser-editing evidence.
Proceed only when evidence confirms it is a static, HTML-like file rather than
a native SharePoint 2016 page with browser-editable Web Parts. The `.aspx`
extension and file URL alone are insufficient to establish the type. If the
source is a native page, route it to `sp-dynamic-aspx-page-migration`. If the type
cannot be established, stop and request clarification.

The source must be the file URL, not an `EditForm.aspx` or other list-form URL.
Do not infer an alternate path from the document title. Preserve the source
unchanged and retain its URL, filename, size, and hash as run evidence.

For `https://source-tenant.example.com/Operations/Administration%20Documents/awards/criteria_processes.aspx`,
the approved target mapping is the `operations` document library, folder
`Administration Documents/awards`, and filename `criteria_processes.html`.
Preserve the source subfolder under the runbook's target folder.

## Source analysis, download, and design-system conversion

1. During source-type preflight, collect available item metadata, inventory
   evidence, and browser-editing evidence. Do not treat metadata or a rendered
   title as a substitute for analyzing the stored file content.
2. Consult the installed `standard-design-system` skill, including its complete
   token reference, canonical CSS token asset, and bundled font assets. Apply
   its static HTML guidance to the analysis and conversion. Resolve those
   resources from the installed design-system skill rather than assuming they
   exist inside this migration skill. Do not use `design-system-react` for this
   non-React page.
3. Invoke `sharepoint-download-file` with the exact source URL, the validated
   read-only source config, the on-prem platform, and raw-file mode. Run its
   dry-run first; do not overwrite an existing local source file. Execute only
   with its documented `DOWNLOAD-SPO-FILE` token.
4. Verify the downloaded bytes and retain the `.aspx` original. Do not use the
   rendered browser response in place of the stored file.
5. Analyze the downloaded source before conversion: identify its title,
   headings, body text, tables, images, links, and accessibility-relevant
   structure. Record what must be preserved and any presentation or
   accessibility issues; do not invent missing content.
6. Invoke `sharepoint-convert-legacy-aspx-to-html` on that local file, writing
   to a distinct intermediate `.html` path. This converter's wrapper is only
   an intermediate; it is not a general sanitizer or proof of Modernernment
   Design System conformance.
7. Review the intermediate output against the source analysis. Then align the
   final static HTML to the design-system skill: use its semantic color and
   typography tokens, BC Sans font faces, spacing/type scale, focus treatment
   for any interactive elements, and applicable semantic/accessibility
   patterns. Follow its sentence-case and no-emoji rules. Use the Indigenous
   acknowledgment footer when the output is a full-page layout. Preserve
   meaningful source content and links; do not apply React components or
   silently change content to satisfy styling.
8. Resolve every referenced CSS, font, image, and other asset against the
   actual target URLs. Check that required BC Sans assets are already available
   at the resolved destination or can be published through an approved
   capability. The HTML publisher handles the HTML file only; do not assume it
   uploads supporting assets. If required assets cannot be made available, or
   the design-system alignment cannot be verified, stop before publication and
   report the limitation rather than claiming conformance.
9. If conversion rejects active markup, or meaningful content is missing,
   stop. Do not weaken the guard, upload raw ASPX, or substitute guessed
   rendered content. Review title, text, tables, links, images, layout, and
   accessibility after design-system alignment.
10. If the HTML references other local files or unresolved SharePoint URLs, use
   `sharepoint-extract-links` to classify them. Do not rewrite links from
   filename similarity; stop for disposition when a dependency would be broken.

## Shared design-system assets

Before publishing the first page to a target environment, inspect its
approved shared asset location and verify whether the exact required
design-system CSS and fonts already exist. Use
[shared-design-system-assets.md](../shared-design-system-assets.md) for
Microsoft's guidance and the detailed verification contract.

- Reuse verified asset URLs and hashes for later pages on that target; do not
  upload a duplicate for each page.
- If approved assets are absent, create one package and publish it once with
  `sharepoint-publish-markdown-files`, the existing document-library file and
  asset publisher. Use its dry-run to review all exact target paths; its
  executor can overwrite existing files, so independently check for
  collisions and require explicit replacement disposition.
- Do not assume an Organization Assets Library is a CSS/font host. Do not
  assume Microsoft 365 CDN is enabled, that a URL is stable, or that an
  origin is private. Public CDN origins are anonymously accessible.
- If an asset library/folder must be provisioned, use the existing
  document-library skill for the library and the verified parent-first folder
  procedure for folders. CDN enablement, origin changes, public exposure, or
  replacing a shared asset require their own authorization.
- Verify asset identity, permissions, effective file-extension policy,
  content type, and browser retrieval, including font requests, before
  referencing the URLs from HTML. Keep CSS-relative paths valid. Use a
  versioned location when replacing/upgrading assets; never silently replace
  a file used by previously published pages.
- Stop before page publication if required assets cannot be safely published
  or retrieved. Do not claim design-system conformance while asset access is
  unverified.

`sharepoint-publish-markdown-files` is the approved file/asset upload route;
its plan builder includes source files recursively and its executor uses
`Add-PnPFile`. Run the dry-run and execute only with
`-Execute -ConfirmToken PUBLISH-SPO-MARKDOWN`. Use
`sharepoint-publish-html-page` separately for the final `.html` page.

## Destination preflight and provisioning

Connect only after validating the target config. Enumerate target lists and
match the exact library title; treat query or authorization errors as failures,
not evidence that the library is missing. Resolve and retain the library's
actual `RootFolder.ServerRelativeUrl`; do not assume the title is its URL.

- If the library is absent, invoke `sharepoint-create-document-library` and
  follow its documented plan shape, dry-run, and `PROVISION-SPO-LIST` execution
  gate. Re-query the library and verify its root folder before continuing.
- Resolve each target folder segment under the actual library root. A folder is
  missing only after a successful query establishes not-found; permission,
  network, and other errors must stop the workflow. Create only missing
  segments with `Add-PnPFolder`, one parent at a time, then re-query and verify
  each created folder. Never recreate the library or existing folders.
- Check the exact final HTML target URL. If a file already exists, ask for
  `Reject`, `Approve replacement`, or `Skip`. Do not infer overwrite approval.
  The existing `sharepoint-publish-html-page` executor replaces an existing
  file when executed, so an approved replacement must be stated plainly before
  its execution gate is used.

Source custom library metadata is not copied by this HTML workflow. Report
source fields and values that are not represented at the destination. Stop if
the user requires those fields to be preserved or mapped.

## Publication and verification

Run `sharepoint-publish-html-page` in dry-run mode with the verified target
library URL segment, folder path, and final HTML filename. Review the resolved
DEV site and target server-relative URL before any write. Execute only with
`PUBLISH-SPO-HTML` after the required target-write authorization.

Independently query the final target file and verify its identity, byte length,
and SHA-256 against the local converted HTML. Open the returned DEV URL and
review content and links. A planned URL or successful upload response alone is
not a pass. Preserve the original, converted HTML, dry-run plans, publication
receipt, and validation evidence. Do not update page inventory for this
document-library operation.
