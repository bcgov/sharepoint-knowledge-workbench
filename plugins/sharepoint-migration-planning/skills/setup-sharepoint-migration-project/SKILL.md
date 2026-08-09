---
name: setup-sharepoint-migration-project
plugin: sharepoint-migration-planning
status: design-scaffold
description: >
  NOT YET IMPLEMENTED. Will interactively ask for the source and target
  SharePoint site URLs for a migration-planning run, confirm the workbench's
  own connection setup (workbench-setup's initialize-workbench-config /
  config.psd1) already exists rather than re-inventing connection config,
  and create a per-migration working folder to hold this pipeline's
  intermediate and final outputs.
allowed-tools: Bash, Read, Write
---

# Setup SharePoint Migration Project

> **Status: design scaffold, not implemented.** This file states intent; there is no working
> script behind it yet.

## Trigger and Purpose (planned)

Stage 1 of the `sharepoint-migration-planning` pipeline (see
`../../references/pipeline-overview.mmd`). Interactive: asks the operator for the source site URL
and target site URL, then **confirms** — does not recreate — that `workbench-setup`'s
`initialize-workbench-config` skill has already produced a repository-root `config.psd1`. This
skill must never generate its own competing connection config; `config.psd1` has exactly one
source of truth, established by an earlier `workbench-setup` fix this session.

## Planned behavior

1. Ask for source site URL, target site URL.
2. Check for a repository-root `config.psd1` with a `Connection` block. If absent, tell the
   operator to run `workbench-setup`'s `initialize-workbench-config` first — do not proceed by
   fabricating a config.
3. Create a per-migration working directory (exact location/naming: not yet decided) to hold this
   pipeline's outputs: the source-site export (once stage 2 exists), `dependency-matrix.json`
   (stage 3a), generated wave scripts and a wave guide (stage 3b).

## Honest outcomes (planned)

Missing `config.psd1` or missing `Connection` block must be reported clearly, not silently worked
around. This skill performs no tenant I/O itself.

## Provenance

New design work, generalizing a manual process (source: a human hand-configuring
`config/config.psd1` before running wave scripts) observed in a separate SharePoint migration
repository. Not a code port.
