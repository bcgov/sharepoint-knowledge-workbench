---
name: publish-markdown-to-sharepoint
description: Builds a human-actionable publish plan for rendered Markdown + media to an exact SharePoint library/folder. Performs no tenant writes -- matches this plugin's Phase 3 package-only architecture.
---

# publish-markdown-to-sharepoint

## Purpose

Produces a `PublishPlan` — an exact list of source file → target library/folder/filename
mappings — for a human to execute manually. **Does not upload anything itself.**

## Why this skill produces a plan instead of uploading

This plugin's Phase 3 architecture is explicitly package-only, zero-tenant-I/O (see
`sharepoint_package.py`'s own module docstring). Real automated tenant writes for this plugin
remain gated behind Stage 3.4.3's approved-write-identity decision
(`docs/vision/master-initiative-plan-workstreams-and-phases.md`), which is **not yet approved**.
Building an automated-upload skill here would cross that established architectural boundary.
This skill stays consistent with the existing plugin's design instead of bypassing it.

## Input boundaries

- `document_id`, a local rendered source directory, and an explicit target library/folder — no
  default target.
- Refuses to build a plan from a missing or empty source directory.

## Prohibited scope

- Zero tenant I/O.
- Does not perform the upload — a human (or a future, separately-authorized skill, once Stage
  3.4.3 is approved) executes the plan.

## Scripts

- `../../scripts/sharepoint_publish_plan.py` (`build_markdown_publish_plan`)

## Tests

- `../../tests/unit/test_sharepoint_publish_plan.py`
