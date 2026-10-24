# Wave Migration Orchestration Contract

This is the authoritative detailed routing contract for
`sp-migration-wave-execution`. The skill entry point links here; preserve these
scope, review, and publication controls when changing the workflow.

## Contents

- [Scope and configuration](#scope-and-configuration)
- [Inventory-owned scope](#inventory-owned-scope)
- [Wave-bound evidence and recovery](#wave-bound-evidence-and-recovery)
- [Review and publication gates](#review-and-publication-gates)
- [Completion, inventory, and optional browser cycle](#completion-and-inventory)
- [Acceptance criteria](#acceptance-criteria)

## Scope and configuration

For every request, require exactly one target environment (`dev`, `test`, or
`prod`), one wave (`Wave-1`, `Wave-2`, or `Wave-3`), and one stable wave
identifier. Include all pages selected by the inventory `Migration Plan`
value.

Resolve the selected environment before invoking any migration or publication
command:

| Environment | Configuration file (passed explicitly; default location is repository root) |
|---|---|
| `dev` | `config-spo-dev.psd1` (SPO DEV + SP2016 TEST source) |
| `test` | `config-spo-test.psd1` (SPO TEST + SP2016 TEST source) |
| `prod` | `config-spo-prod.psd1` (SPO PROD + SP2016 PROD source) |

Pass the selected file as `-ConfigPath` to every script in the run. Each
sp-migration script reads the site, ClientId, TenantId, environment name, and
SP2016 source from that file; scripts never assume a configuration location
or accept those values as separate arguments. If the selected file is missing
or any required connection value is empty, stop before contacting SPO and
report the missing configuration. Never fall back to the repository-root
`config.psd1`, environment variables, or an implicitly selected site.

## Inventory-owned scope

1. Request the complete validated wave scope from `sp-migration-wave-execution`
   (through `sp-page-inventory` / `sp-page-inventory-agent`). Consume
   only the returned wave manifest and page handoffs; do not read `inventory-page.json`
   independently, select pages, derive target paths, or independently validate inventory membership.
2. Stop if the inventory source returns an unavailable, empty, partial,
   failed, or invalid scope result. Never continue with a reduced or manually
   selected page set.
3. Before extraction, require every returned manifest page to contain
   `SiteName`, `ServerRelativeUrl`, `TargetPageServerRelativeUrl`, `Title`,
   `Url`, `Layout`, `TargetEnvironment`, and `Wave`. The wave-manifest builder
   validates this C1 scope contract; do not create a second derived scope or
   invoke `sp-dynamic-aspx-page-migration` for these entries; use that compatibility
   skill only for an individually supplied legacy handoff.
4. For `Wave-2` and `Wave-3`, return an explicit unsupported-wave result until
   a corresponding planner exists. Never pass those waves to the Wave-1
   planner.

## Wave-bound evidence and recovery

5. Before extracting anything, perform a wave-ID-scoped package lookup under
   the requested wave evidence directory. Accept only a complete, internally
   validated package set for that exact wave ID. Never search other waves,
   reuse an unscoped package directory, or infer package identity from file
   timestamps.
6. If the exact wave-ID package set is missing or incomplete, perform the
   required SP2016 read-only retrieval using the validated `Source` block
   (`Source.SiteUrl`, `Source.ReadOnly = $true`) in the selected
   `config-spo-<environment>.psd1`. Then regenerate the wave-scoped web-part
   extraction, image assets, migration plans, and publication packages. This
   recovery path is read-only against SP2016 and must finish before any SPO
   publication command is considered.
7. If the exact wave-ID package set is complete, reuse the complete package set and do not re-extract web parts or images merely because a new run was requested.
8. When recovery is required, delegate extraction to
   `sharepoint-analyze-webpart-code` in `ExtractContent` mode. Require an
   array of recorders with `PageUrl`, `WebPartId`, `WebPartTitle`, `ZoneID`,
   `PartOrder`, and `Content`. Store transient extraction output under
   `temp/`; do not duplicate its collector or read inventory artifacts
   directly.
9. Download image assets referenced by extracted HTML into `temp/` using the
   image-extraction step. Assign unique names under the future
   `SiteAssets/SitePages/` destination mapping.
10. For `Wave-1`, accept web parts classified as `CEWP` by the read-only
    collector, plus the confirmed legacy Content Editor title aliases
    `Content Editor` and `Home Intro`. Preserve the display title in the
    evidence and plan; do not treat arbitrary titles as Content Editor.
11. Invoke `sp-dynamic-aspx-page-migration` to normalize each supported Content Editor
    payload, create `ImageWebPart` mappings for downloaded images, create
    `TextWebPart` components for remaining HTML, and produce one per-page
    plan.
12. Treat plans, extracted content, and image manifests under `temp/` as
    diagnostic evidence only; they are not the wave acceptance gate.
13. Do not rewrite non-image links; link rewriting is a separate capability.

## Review and publication gates

The ordered workflow is:

1. Bind the complete scope with `sp-migration-wave-execution`.
2. Prepare the transformation plan with `sp-dynamic-aspx-page-migration`. This stage
   is local-only and does not write to a SharePoint Online tenant.
3. Stop and present the transformation plan for human review.
4. Prepare the publication package with `sp-dynamic-aspx-page-migration` only
   after plan review.
5. Stop and present the publication package for a separate human review.
6. Publish with `sp-page-publish` only after package review. It defaults to a
   no-tenant-I/O dry run; the workflow must not supply or imply execution
   authorization.
7. Reconcile the publisher's per-object result report with
   `sp-migration-wave-execution`. The result is `PASSED`, `PARTIAL`, or `FAILED`;
   reconciliation is not an owner-acceptance record.

Before any page write, `publish-spo-wave.ps1` authenticates and checks every
target page in scope against SPO. It must list all duplicate target pages and
stop with `DUPLICATE_ACTION_REQUIRED`. Ask the user to choose exactly one:
`Reject`, `Approve`, or `Skip`. `Reject` stops the complete batch; `Approve`
publishes all pages; `Skip` publishes only non-duplicate pages. Site Assets are
excluded from this preflight and may be overwritten. Rerun with
`-DuplicatePageAction <choice>` and
`-OutputPath <durable receipt path> -Execute -ConfirmToken PUBLISH-SPO-PAGE`
only after the user chooses. The workflow introduces no confirmation token
and never authorizes a tenant write on the user's behalf.

Successful PnP publication is the migration completion event. Do not run an
authenticated browser Edit -> Publish cycle before inventory update and
tracker sync; any browser cycle is a separate optional post-sync
operation.

## Completion and inventory

Mark the wave complete only when `validate-spo-wave-completion.ps1` reports
every expected page as accepted: newly published pages must be `PUBLISHED`,
while pages explicitly skipped as existing under
`DuplicatePageAction=Skip` count as `SKIPPED_EXISTING`. Pass the package
directory using `-ExpectedPackageDirectory` when the publication receipt
stores relative package paths.

After publication acceptance:

1. update the inventory target URLs for accepted publication results, using
   either the source path from the package handoff or the generated target
   path supported by the updater.
2. Then run `page_migration_tracker.py sync` (skill `sp-page-inventory`) to refresh
   `inventory/page-migration-tracker.xlsx`. Never redirect the tracker into
   `temp/`; only diagnostic JSON, receipts, manifests, and completion evidence
   belong there. Do not wait for or require a browser Edit -> Publish cycle:
   these steps happen while the pages are already successfully published.
The inventory workflow owns wave selection and target-path derivation. This
workflow validates each per-page migration handoff and owns extraction,
planning, publication, and completion validation. A successful publication
receipt is sufficient for migration completion; later user editing is not
part of the migration receipt.

All diagnostic artifacts, receipts, manifests, plans, and package files must
be written by the delegated skills under `temp/`. The page tracker
is the explicit exception and stays at
`inventory/page-migration-tracker.xlsx`.

## Acceptance criteria

- Run the complete single-wave sequence in order: manifest, migration plan,
  publication package, publish, and wave reconciliation.
- Preserve the human review checkpoint between the migration plan and
  publication-package stages.
- Preserve the separate human review checkpoint between package preparation
  and publish.
- Require the publisher's own confirmation-token gate; the workflow does not
  grant or imply authorization on the user's behalf.
- Report publish reconciliation as a result, never as owner acceptance.
