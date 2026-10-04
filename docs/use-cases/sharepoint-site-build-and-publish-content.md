# Use Case: Tenant Publication

Publish converted content (Markdown or ASPX) to a live SharePoint tenant, with a dry-run upload
plan, validation, reconciliation against actual tenant state, and rollback.

## When to use this

Content has already been produced by the [Document Conversion](sharepoint-document-conversion.md) pipeline
(or another source) and is ready to go live on a real SharePoint site.

## Workflow at a glance

- `apply-page-publication-plan` — packages a rendered publication output and plans the upload.
- `publish-markdown-files` / `plan-page-publication` — format-specific publication.
- `validate-sharepoint-publication` — confirms a publication matches what was intended.
- `compare-publication-state` — compares planned state against actual live tenant state.
- `remove-publication` — reverts a publication.

Shares the same plan/apply safety contract as the other write-capable plugins: dry-run by default,
explicit executor injection, plan-derived confirmation token required for a real write.

## Full detail

[`plugins/sharepoint-site-build-and-publish/README.md`](../../plugins/sharepoint-site-build-and-publish/README.md)
— note: that README's own header text ("TRANSITIONAL_HOLDING_LOCATION," pre-Phase-4.5-decomposition
framing) is stale relative to the plugin's actual current state (its 6 publication skills and 1 agent now ship inside the consolidated
plugin, listed by that README and by the main repository README's plugin inventory); read `start-here.md`'s Phase 6/Phase 9 sections for the
plugin's real status rather than trusting that header.
