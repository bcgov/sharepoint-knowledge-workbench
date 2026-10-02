# Migration project setup details

## Contents

- [Public interface](#public-interface)
- [Working directory convention](#working-directory-convention)
- [Honest outcomes](#honest-outcomes)
- [Provenance](#provenance)

## Public interface

```python
from project_setup import setup_migration_project

result = setup_migration_project(
    repo_root,
    source_site_url="https://contoso.sharepoint.com/sites/old",
    target_site_url="https://contoso.sharepoint.com/sites/new",
    project_slug="acme-migration",
)
# result.outcome: Outcome.OBSERVED (paths created) or Outcome.FAILED
# (config.psd1 missing/no Connection block, or a required argument missing)
```

`check_config_psd1(repo_root)` and `project_paths(repo_root, project_slug)` are also exposed individually. The skill confirms, and never recreates, the
`config.psd1` that `workbench-setup`'s `initialize-workbench-config` skill produces; `config.psd1` has exactly one source of truth.

## Working directory convention

`runs/sharepoint-migration-planning/<project-slug>/`, holding:

- `export/`: the source-site export directory stage 2 validates.
- `generated-scripts/`: stage 3b's generated wave scripts.
- `dependency-matrix.json`: stage 3a's output (path only; this skill does not write it).
- `wave-guide.md`: stage 3b's output (path only; this skill does not write it).

This mirrors the repository's `runs/<doc-name>/` convention for the content-pipeline plugins. Directory creation is idempotent.

## Honest outcomes

A missing `config.psd1`, a `config.psd1` with no `Connection` key, or a missing required argument (`source_site_url`, `target_site_url`, `project_slug`) is
`Outcome.FAILED` with an actionable message, and no working directory is created. The skill performs no tenant I/O and never writes or edits `config.psd1`.

## Provenance

New design work, generalizing a manual process (a human hand-configuring `config/config.psd1` before running wave scripts) observed in a separate SharePoint
migration repository. Not a code port.
