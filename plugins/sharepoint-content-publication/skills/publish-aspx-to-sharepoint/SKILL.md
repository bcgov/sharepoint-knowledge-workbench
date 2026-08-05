---
name: publish-aspx-to-sharepoint
description: Builds a human-actionable publish plan for rendered content as SharePoint modern pages. Performs no tenant writes -- matches this plugin's Phase 3 package-only architecture.
---

# publish-aspx-to-sharepoint

## Purpose

Produces a `PublishPlan` for publishing rendered content as SharePoint pages. **Does not upload
or create any page itself.**

## Real platform constraint recorded

Per Phase 3.0's confirmed finding
(`docs/research/research-experimentation/tenant-discovery/field-note-sharepoint-write-capability-discovery.md` §15): raw
`.aspx` file upload is blocked (`Access denied`) on this tenant. The only confirmed-working
mechanism is the `Add-PnPPage`/`Add-PnPPageTextPart` modern-page-creation API, not a file upload.
This skill's plan records source content and target page names; it does not itself call either
mechanism, for the same package-only reason as `publish-markdown-to-sharepoint` (Stage 3.4.3 not
yet approved).

## Input boundaries

- `document_id`, a local rendered `.md` source directory, and a target site-relative path.
- Refuses to build a plan from a missing source directory or one with no `.md` files.

## Prohibited scope

- Zero tenant I/O.
- Does not attempt raw `.aspx` file upload (confirmed blocked) or call the page-creation API —
  both remain a future, separately-authorized capability once Stage 3.4.3 is approved.

## Scripts

- `../../scripts/sharepoint_publish_plan.py` (`build_aspx_publish_plan`)

## Tests

- `../../tests/unit/test_sharepoint_publish_plan.py`
