# Page copy between sites: plan and flows

## Contents

- [Identity](#identity)
- [Steps](#steps)
- [Same-site vs. cross-site flows](#same-site-vs-cross-site-flows)
- [Common failures](#common-failures)

## Identity

Plans promotion of an existing SharePoint Online Site Page from a source SPO site to a target SPO site (for example TEST to PROD). This is SPO-to-SPO page copy and promotion, not SP2016 classic page modernization.

## Steps

1. Confirm the source site URL, target site URL, page library, source page name, target page name and overwrite expectation.
2. Build the page-to-page copy plan with `scripts/spo-page-copy-plan.ps1`: `-SourcePageUrl` and `-TargetPageUrl` (full URLs under `/SitePages/`); `-Overwrite` only when the target page may be replaced.
3. Present the generated plan and the recommended human-run execution approach.
4. Do not run live tenant write commands automatically.

## Same-site vs. cross-site flows

By default the script prints the plan and does no tenant I/O. With `-Execute -ConfirmToken COPY-SPO-PAGE` it runs the reviewed PnP.PowerShell flow, treating the page as a file in the Site Pages library
(`Copy-PnPPage`'s cross-site parameter set does not exist in current PnP.PowerShell, and cross-site-collection copy through it also needs SharePoint admin-center access that `Copy-PnPFile` does not).

- **Same site** (source site URL equals target site URL), such as duplicating a page under a new name: if the final target path exists, fail unless `-Overwrite` (then recycle it first); then a single
  `Copy-PnPFile -SourceUrl <source path> -TargetUrl <target path including filename>`. No rename step. A real bug (2026-09-08) came from always using the two-step flow for same-site copies: the intermediate
  copy under the source name collided with the source file itself. Do not reintroduce the two-step flow for same-site.
- **Cross site** (different site URLs), such as TEST to PROD: if the final target path exists, fail unless `-Overwrite` (then recycle it first); `Copy-PnPFile` to the target site's SitePages **folder** (no
  filename; cross-site-collection copy requires a folder path); then `Rename-PnPFile -ServerRelativeUrl <copied file> -TargetFileName <target page name>` when the target name differs
  (`-ServerRelativeUrl` and `-OverwriteIfAlreadyExists` are the real parameter names).

`-SkipRename` is diagnostic-only (runs the copy but skips the rename) and is not part of the normal flow. `-TenantAdminUrl` is not required by the current flow.

## Common failures

- A non-`.aspx` page name is supplied.
- The target page should use a different name but no target page name was provided to the plan helper.
- The request is actually classic SP2016 modernization; route it to the page modernization skills instead.
- The user asks for raw `.aspx` upload; prefer the supported SPO page APIs and PnP page promotion patterns.
