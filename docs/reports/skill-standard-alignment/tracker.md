# Skill Standard Alignment Tracker

Living record of auditing every skill under `plugins/` and retrofitting them to the skill authoring
standard. Update the **Per-skill table**, **Per-plugin progress** and **Change log** as work proceeds.

## Contents

- [Standard measured against](#standard-measured-against)
- [How to refresh](#how-to-refresh)
- [Summary](#summary)
- [Per-plugin progress](#per-plugin-progress)
- [Open findings by rule](#open-findings-by-rule)
- [Per-skill table](#per-skill-table)
- [Decisions and open questions](#decisions-and-open-questions)
- [Change log](#change-log)

## Standard measured against

The checks are `audit_skill.py` (the `audit-skill` skill) against its bundled
`skill-authoring-contract.json`, **contract version 1.0.0**, with the Anthropic skill-authoring
best-practices reference bundled in the same skill:

- `SKILL.md` layout: purpose, `## Contents`, `## Constraints`, `## Quick start`, `## Workflow`,
  `## Verification`, `## References`. Lean target 80 lines; Contents inside the first 100 lines;
  body under 500 lines; description at most 1024 characters, no XML tags.
- Evals: `evals/evals.json` (routing, real `should_trigger` booleans) and `evals/task-success.json`
  (`expected_behavior` lists, at least three observed scenarios).
- Packaging (`audit-skill` and `plugin-architecture-policy.md`): canonical resources at the plugin
  root, file-level managed symlinks into each skill, no directory symlinks, paths relative to the
  skill root, installed skills self-contained.

**Not verified:** a separate "Anthropic October 2026" specification. The bundled contract is the only
standard applied here. If a newer published spec exists, add its source and a gap column.

## How to refresh

Run from the repository root. Source mode audits the repo; installed mode audits a materialized copy.

```bash
python3 .agents/skills/audit-skill/scripts/audit_skill.py . --all --mode source          # per-skill report
python3 .agents/skills/audit-skill/scripts/audit_skill.py . --all --mode source --json    # summary.by_rule / by_plugin
python3 .agents/skills/audit-skill/scripts/audit_skill.py <skill-dir> --mode source --strict   # one skill, warnings fail
python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose                 # link health
```

Per-skill workflow: audit, propose bounded edits, move detail into plugin-root `references/` with
file-level symlinks (via `symlink_manager.py create`), re-audit with `--strict`, then confirm the
installed copy (symlinks resolved) also passes.

## Summary

| Measure | Baseline | Current |
|---|---|---|
| Skills audited | 104 | 104 |
| Passing | 93 | 104 |
| Failing | 11 | 0 |
| Errors | 16 | 0 |
| Warnings | 643 | 0 |

Baseline: first full audit, before any edits. Current: audit run at the time of the latest change-log entry.

## Per-plugin progress

| Plugin | Skills | Retrofitted | Errors fixed only | Not started |
|---|---|---|---|---|
| content-assembly | 1 | 1 | 0 | 0 |
| content-extraction | 1 | 1 | 0 | 0 |
| content-rendering | 7 | 7 | 0 | 0 |
| content-structure-analysis | 1 | 1 | 0 | 0 |
| sharepoint-agents-and-skills | 15 | 15 | 0 | 0 |
| sharepoint-content-migration | 2 | 2 | 0 | 0 |
| sharepoint-content-publication | 6 | 6 | 0 | 0 |
| sharepoint-discovery | 15 | 15 | 0 | 0 |
| sharepoint-link-remediation | 5 | 5 | 0 | 0 |
| sharepoint-migration-planning | 5 | 5 | 0 | 0 |
| sharepoint-page-modernization | 4 | 4 | 0 | 0 |
| sharepoint-page-modernization-execution | 4 | 4 | 0 | 0 |
| sharepoint-provisioning | 19 | 19 | 0 | 0 |
| sharepoint-schema-reconciliation | 4 | 4 | 0 | 0 |
| sharepoint-spfx-authoring | 10 | 10 | 0 | 0 |
| workbench-setup | 5 | 5 | 0 | 0 |

Statuses: **Retrofitted** = restructured to the standard layout and passes `--strict` (except missing evals); **Errors fixed** = no audit errors, layout not yet aligned; **Not started** = untouched.

## Open findings by rule

| Rule | Baseline | Current | Notes |
|---|---|---|---|
| `navigation.canonical-headings` | 522 | 0 | Missing Contents/Constraints/Quick start/Workflow/Verification/References headings |
| `size.lean` | 36 | 0 | SKILL.md over the 80-line target |
| `packaging.folder-structure` | 27 | 0 | Missing evals/ directory (and disallowed directories) |
| `evals.missing` | 27 | 0 | All skills now have evals/evals.json (see decisions: the 27 new files were authored, not observed) |
| `navigation.entry-toc` | 20 | 0 | Long entry point lacks Contents in the first 100 lines |
| `navigation.reference-toc` | 7 | 0 | Linked reference over 100 lines lacks early Contents |
| `navigation.legacy-headings` | 4 | 0 | Legacy section names to fold into canonical sections |
| `navigation.direct-reference` | 0 | 0 | Reference reached only through another reference |
| `links.resolve` | 8 | 0 | Broken local link |
| `packaging.resource` | 6 | 0 | Real file where a managed symlink belongs |
| `metadata.description` | 2 | 0 | Description empty, over 1024 characters, or contains an XML-like tag |

## Per-skill table

Columns: lines = `SKILL.md` line count now; Baseline and Now show `status errors/warnings`; Task-success evals = whether `evals/task-success.json` exists.

| Plugin | Skill | Lines | Baseline | Now | State | Task-success evals | Open rules (excluding heading warnings for retrofitted) |
|---|---|---|---|---|---|---|---|
| content-assembly | content-assemble-structured-content | 62 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| content-extraction | content-extract-docx | 56 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| content-rendering | content-compare-rendered-output | 48 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| content-rendering | content-create-aspx-rendering-template | 53 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| content-rendering | content-create-markdown-rendering-template | 52 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| content-rendering | content-render-multipage-markdown | 56 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| content-rendering | content-render-sharepoint-aspx | 58 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| content-rendering | content-validate-rendered-output | 59 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| content-rendering | content-validate-rendering-template | 54 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| content-structure-analysis | content-analyze-document-structure | 56 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-agents-and-skills | sharepoint-apply-sharepoint-agent-template | 46 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-agents-and-skills | sharepoint-backup-sharepoint-agents | 45 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-agents-and-skills | sharepoint-backup-sharepoint-native-skills | 45 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-agents-and-skills | sharepoint-configure-sharepoint-agent-knowledge | 47 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-agents-and-skills | sharepoint-create-sharepoint-agent | 47 | PASS 0/6 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-agents-and-skills | sharepoint-create-sharepoint-agent-template | 45 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-agents-and-skills | sharepoint-create-sharepoint-native-skill | 46 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-agents-and-skills | sharepoint-deploy-sharepoint-native-skill | 47 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-agents-and-skills | sharepoint-inventory-and-validate-agentassets | 46 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-agents-and-skills | sharepoint-restore-sharepoint-agents | 46 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-agents-and-skills | sharepoint-restore-sharepoint-native-skills | 45 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-agents-and-skills | sharepoint-review-manual-topics | 58 | PASS 0/8 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-agents-and-skills | sharepoint-rollback-sharepoint-native-skill | 45 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-agents-and-skills | sharepoint-update-sharepoint-agent | 46 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-agents-and-skills | sharepoint-verify-sharepoint-native-skill | 45 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-content-migration | sharepoint-audit-list-content | 68 | FAIL 1/8 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-content-migration | sharepoint-migrate-sharepoint-list-content | 64 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-content-publication | sharepoint-publish-aspx-to-sharepoint | 51 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-content-publication | sharepoint-publish-markdown-to-sharepoint | 55 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-content-publication | sharepoint-reconcile-sharepoint-publication | 52 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-content-publication | sharepoint-rollback-sharepoint-publication | 54 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-content-publication | sharepoint-upload-content | 55 | PASS 0/6 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-content-publication | sharepoint-validate-publication | 52 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-discovery | sharepoint-analyze-custom-forms | 60 | FAIL 1/6 | PASS 0/0 | Retrofitted | no | none |
| sharepoint-discovery | sharepoint-analyze-page-inventory | 61 | PASS 0/6 | PASS 0/0 | Retrofitted | no | none |
| sharepoint-discovery | sharepoint-analyze-permissions | 62 | PASS 0/6 | PASS 0/0 | Retrofitted | no | none |
| sharepoint-discovery | sharepoint-analyze-site-navigation | 60 | FAIL 1/6 | PASS 0/0 | Retrofitted | no | none |
| sharepoint-discovery | sharepoint-analyze-webpart-code | 66 | PASS 0/8 | PASS 0/0 | Retrofitted | no | none |
| sharepoint-discovery | sharepoint-audit-managed-metadata | 62 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-discovery | sharepoint-audit-onprem-schema-drift | 61 | PASS 0/8 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-discovery | sharepoint-audit-schema | 62 | PASS 0/6 | PASS 0/0 | Retrofitted | no | none |
| sharepoint-discovery | sharepoint-collect-sharepoint-inventory | 60 | PASS 0/8 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-discovery | sharepoint-diff-sharepoint-schema | 62 | PASS 0/7 | PASS 0/0 | Retrofitted | no | none |
| sharepoint-discovery | sharepoint-extract-calculated-columns | 60 | PASS 0/6 | PASS 0/0 | Retrofitted | no | none |
| sharepoint-discovery | sharepoint-extract-choice-fields | 59 | PASS 0/5 | PASS 0/0 | Retrofitted | no | none |
| sharepoint-discovery | sharepoint-generate-discovery-report-set | 58 | PASS 0/9 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-discovery | sharepoint-generate-sharepoint-schema-from-export | 60 | PASS 0/5 | PASS 0/0 | Retrofitted | no | none |
| sharepoint-discovery | sharepoint-scaffold-schema-definition | 46 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-link-remediation | sharepoint-extract-links | 55 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-link-remediation | sharepoint-remediate-document-content-links | 56 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-link-remediation | sharepoint-remediate-field-image-references | 57 | FAIL 1/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-link-remediation | sharepoint-remediate-links | 59 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-link-remediation | sharepoint-validate-link-integrity | 55 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-migration-planning | sharepoint-analyze-sharepoint-dependency-graph | 62 | PASS 0/6 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-migration-planning | sharepoint-discover-sharepoint-site-inventory | 58 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-migration-planning | sharepoint-generate-sharepoint-wave-scripts | 59 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-migration-planning | sharepoint-plan-sharepoint-deployment-waves | 53 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-migration-planning | sharepoint-setup-sharepoint-migration-project | 59 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-page-modernization | sharepoint-analyze-aspx-pages | 51 | PASS 0/6 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-page-modernization | sharepoint-compose-page-preview | 49 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-page-modernization | sharepoint-convert-aspx-pages | 55 | FAIL 1/6 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-page-modernization | sharepoint-generate-conversion-report | 49 | FAIL 2/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-page-modernization-execution | sharepoint-convert-page-to-modern | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-page-modernization-execution | sharepoint-copy-page-between-sites | 51 | FAIL 1/6 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-page-modernization-execution | sharepoint-execute-page-bulk-migration | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-page-modernization-execution | sharepoint-validate-page-migration | 48 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-provisioning | sharepoint-add-list-column | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-provisioning | sharepoint-add-list-item | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-provisioning | sharepoint-apply-provisioning-plan | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-provisioning | sharepoint-configure-column-formatting | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-provisioning | sharepoint-configure-library-settings | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-provisioning | sharepoint-create-content-type | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-provisioning | sharepoint-create-document-library | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-provisioning | sharepoint-create-list | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-provisioning | sharepoint-create-list-view | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-provisioning | sharepoint-create-site-column | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-provisioning | sharepoint-detach-content-type | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-provisioning | sharepoint-remove-content-type | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-provisioning | sharepoint-remove-list | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-provisioning | sharepoint-remove-list-column | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-provisioning | sharepoint-remove-site-column | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-provisioning | sharepoint-update-content-type | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-provisioning | sharepoint-update-list-column | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-provisioning | sharepoint-update-list-settings | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-provisioning | sharepoint-update-site-column | 49 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-schema-reconciliation | sharepoint-provision-content-types | 52 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-schema-reconciliation | sharepoint-provision-fields | 55 | PASS 0/6 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-schema-reconciliation | sharepoint-provision-list | 54 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-schema-reconciliation | sharepoint-provision-modern-calendar-list | 53 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-spfx-authoring | sharepoint-deploy-spfx-solution | 49 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-spfx-authoring | sharepoint-package-spfx-solution | 48 | PASS 0/8 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-spfx-authoring | sharepoint-publish-spfx-package | 49 | PASS 0/8 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-spfx-authoring | sharepoint-request-site-collection-app-catalog | 47 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-spfx-authoring | sharepoint-scaffold-spfx-form-customizer | 54 | PASS 0/11 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-spfx-authoring | sharepoint-scaffold-spfx-listview-command-set | 49 | FAIL 3/4 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-spfx-authoring | sharepoint-scaffold-spfx-master-detail | 48 | PASS 0/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-spfx-authoring | sharepoint-scaffold-spfx-react-app | 51 | FAIL 3/5 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-spfx-authoring | sharepoint-scaffold-spfx-webpart | 50 | PASS 0/7 | PASS 0/0 | Retrofitted | yes | none |
| sharepoint-spfx-authoring | sharepoint-setup-spfx-workbench | 47 | FAIL 1/6 | PASS 0/0 | Retrofitted | yes | none |
| workbench-setup | workbench-initialize-document-workflow | 72 | FAIL 1/6 | PASS 0/0 | Retrofitted | no | none |
| workbench-setup | workbench-initialize-workbench-config | 55 | PASS 0/5 | PASS 0/0 | Retrofitted | no | none |
| workbench-setup | workbench-request-app-registration | 80 | PASS 0/9 | PASS 0/0 | Retrofitted | no | none |
| workbench-setup | workbench-resolve-workbench-paths | 59 | PASS 0/7 | PASS 0/0 | Retrofitted | no | none |
| workbench-setup | workbench-validate-workbench-environment | 80 | PASS 0/9 | PASS 0/0 | Retrofitted | no | none |

## Decisions and open questions

- **Evals were authored, not observed.** On 2026-10-02 the 27 skills that had neither file (5 in
  `sharepoint-discovery`, 3 in `sharepoint-page-modernization-execution`, 19 in `sharepoint-provisioning`)
  received `evals/evals.json` (4 positive and 4 near-miss negative routing cases each) and
  `evals/task-success.json` (3 scenarios each). The `should_trigger` labels and `expected_behavior`
  lists were written from each skill's `SKILL.md` and its sibling skills, and have **not** been run
  against any model. Treat them as a starting contract the skill owner should review, and record real
  model results separately.
- **Task-success evals exist for only 89 of 104 skills.** The other 15 have routing evals only. Authoring
  `task-success.json` for them is the next evals step.
- **`plugin:` frontmatter does not match the owning plugin for 38 skills.** 21 omit it
  (`sharepoint-agents-and-skills` 15, `sharepoint-content-publication` 6). 13 name an old pre-rename plugin
  (`content-*` skills still say `source-document-extraction`, `structured-content-assembly`,
  `structured-content-rendering` or `document-structure-analysis`; `sharepoint-schema-reconciliation`
  says `sharepoint-provisioning`). `sharepoint-page-modernization-execution` says
  `sharepoint-content-publication`. Fix while retrofitting each plugin.
- **`scripts/assets/` in `sharepoint-page-modernization`.** Its skills symlink assets to
  `scripts/assets/` (packaged data), not to a plugin-root `assets/` as the architecture policy table
  states. Left as is; decide whether to relocate.
- **Moved files keep a prefixed name.** Where a skill held a real file, it was moved to the plugin
  root as `<skill>-<name>` (for example `references/<skill>-acceptance-criteria.md`) and linked back
  under its original name, to avoid collisions between skills.
- **`audit-plugin` is not usable here** (its install lacks `skill-authoring-contract.json`), so plugin
  level structure checks are not part of this tracker.
- **Leftover old-lineage folders** remain on disk (for example `plugins/source-document-extraction`)
  and are not audited because they hold no skills.

## Change log

| Date | Change |
|---|---|
| 2026-10-02 | Baseline audit of 104 skills in 16 plugins. |
| 2026-10-02 | `workbench-setup`: all 5 skills retrofitted (SKILL.md at or under 80 lines, detail moved to 12 plugin-root references with symlinks). |
| 2026-10-02 | `sharepoint-discovery`: all 15 skills retrofitted; `plugin:` frontmatter corrected from `sharepoint-schema`; missing import dependencies linked into `sharepoint-scaffold-schema-definition` and `sharepoint-audit-schema`. 5 still lack evals. |
| 2026-10-02 | Fixed all 8 failing skills / 13 errors: 6 real-file imposters moved to plugin roots and symlinked; 3 broken reference links and 2 broken asset links resolved with symlinks; 1 description XML-tag removed. 104 pass, 0 fail, 0 errors. |
| 2026-10-02 | Authored `evals.json` and `task-success.json` for the 27 skills that had neither. All 104 skills now have routing evals; 27 have task-success evals. `evals.missing` and `packaging.folder-structure` warnings are 0; total warnings 465. Added the `plugin:` frontmatter mismatch finding (38 skills). |
| 2026-10-02 | `content-assembly` and `content-extraction` retrofitted (1 skill each): `plugin:` frontmatter corrected from the old pre-rename names, stale `pip install -e plugins/...` and repo-root `DEPENDENCIES.md` removed, stale plugin names updated to `content-structure-analysis`, interface detail moved to a plugin-root reference, `task-success.json` added. Strict audit passes in source and installed mode; plugin tests pass (174 and 78). |
| 2026-10-02 | `content-rendering` retrofitted (7 skills): `plugin:` corrected from `structured-content-rendering`; stale `pip install -e plugins/...` and repo-root path references removed; stale plugin names updated; detail moved to 3 plugin-root references (`rendering-template-profiles.md`, `render-aspx-details.md`, `validate-rendered-output-details.md`); `task-success.json` added to all 7; linked the missing `renderers/sharepoint_aspx.py` into `content-render-multipage-markdown` (its quick-start import failed from an installed copy). Strict audit passes in source and installed mode; plugin tests pass (94, 2 skipped). |
| 2026-10-02 | `content-structure-analysis` retrofitted (1 skill): `plugin:` corrected from `document-structure-analysis`; stale install and repo-root references removed; plugin names updated to `content-extraction` and `content-assembly`; interface detail moved to `references/analysis-interface.md`; `task-success.json` added; linked the missing `identity_core.py`, `plan_verification_core.py` and `topic_boundary_core.py` into the skill (its import failed from an installed copy). Strict audit passes in source and installed mode; plugin tests pass (70). |
| 2026-10-02 | `.claude-plugin/marketplace.json` reviewed against `manage-marketplace`: all 16 entries `strict: true`, each plugin has its own `plugin.json` with an object author and no auto-discovered arrays, all sources resolve. Updated the stale `sharepoint-discovery` description to cover its collectors, auditors, report generator and schema tooling. Plugin versions left at their current values. Re-check the marketplace after each plugin retrofit. |
| 2026-10-02 | `sharepoint-content-migration` retrofitted (2 skills): `sharepoint-audit-list-content` (106 to 68 lines; commands rewritten from repo-root `plugins/...` paths to skill-root-relative; workflow, scripts table and Phase 2 section list moved to two references) and `sharepoint-migrate-sharepoint-list-content` (161 to 63 lines; API/sequencing and the real-executor notes moved to two references). Fixed a broken example (`ItemMigrationPlan` has no `to_dict()`) and linked the missing `provisioning_outcomes.py` into the migrate skill. `task-success.json` added to both. Strict audit passes in source and installed mode; plugin tests pass (34). |
| 2026-10-02 | `sharepoint-content-publication` retrofitted (6 skills): `plugin:` and `allowed-tools:` frontmatter added; every script path was `../../scripts/...` (escaping the skill), now skill-root-relative with the needed scripts, the Get-WorkbenchConnectionConfig helper and the actual-state CSV doc symlinked into each skill; 2 plugin-root references (executors/gates/corrections, upload details); `task-success.json` added to all 6. Found that the executors' `-ConfigPath` default does not resolve from an installed skill and documented passing it explicitly. Marketplace listing corrected (no "page conversion" executors here; tokens are operation-specific, not plan-derived). `plugin.json` description still says TRANSITIONAL_HOLDING_LOCATION (left for the user). Strict audit passes in source and installed mode; 38 plugin tests pass. |
| 2026-10-02 | `sharepoint-link-remediation` retrofitted (5 skills): SKILL.md rewritten for all 5 (Constraints first; shared pipeline/outcomes/write-safety reference plus one details reference per skill); task-success.json added to all 5; `link_rules.py` linked into `sharepoint-validate-link-integrity` (its import failed from an installed copy); extended `tests/test_plugin_independence.py`'s exemption set to include `task-success.json` (the new standard adds that skill-owned eval file). Documented that the executors' `-ConfigPath` default does not resolve when installed. Strict audit passes in source and installed mode; 165 plugin tests pass. |
| 2026-10-02 | `sharepoint-migration-planning` retrofitted (5 skills): SKILL.md rewritten for all 5; 6 plugin-root references (pipeline/outcomes plus one details reference per skill); `provisioning_outcomes.py`, `wave_planning.py`, the plugin rules, the JSON schemas and templates symlinked into the skills that use them (they previously pointed at `../../assets`, `../../rules`, `../../references`); `task-success.json` added to all 5. Corrected the wave-scripts doc: only `spo-provision-calendar.ps1` is local, the other three executors belong to `sharepoint-provisioning`; the plugin README still lists all four as local (left for the user). Marketplace listing corrected (`wave_planning.py` is authored in this plugin). Strict audit passes in source and installed mode; 64 plugin tests pass. |
| 2026-10-02 | `sharepoint-page-modernization` retrofitted (4 skills): SKILL.md rewritten for all 4; 5 plugin-root references (pipeline/outcomes plus one details reference per skill); the documented command lines used flags that do not exist (`--raw-html`, `--inventory`, `--classified`, `--layout ... --output manifest.json`), now the real ones (`--source-html`, `--input`, `--components`, `--output-mapping`/`--output-views`); found that no script in the plugin assembles the full PageConversionManifest (component_mapping writes mapping and views; conversion_report only consumes a manifest) and documented that; pointer to the page-conversion executor updated to `sharepoint-convert-page-to-modern` in `sharepoint-page-modernization-execution`; `outcomes.py` linked into `sharepoint-generate-conversion-report` (its import failed from an installed copy); `task-success.json` added to all 4. Marketplace listing corrected. Strict audit passes in source and installed mode; 82 plugin tests pass. |
| 2026-10-02 | `sharepoint-page-modernization-execution` retrofitted (4 skills): SKILL.md rewritten for all 4; 5 plugin-root references (shared gates/tokens/config plus one details reference per skill); `plugin:` corrected from `sharepoint-content-publication`; the copy-page skill previously described only a planning script and now documents its gated `-Execute -ConfirmToken COPY-SPO-PAGE` mode and the same-site vs cross-site flows (including the 2026-09-08 same-site bug note); `task-success.json` added to `sharepoint-copy-page-between-sites` (the other three already had authored evals). Marketplace listing already accurate. Strict audit passes in source and installed mode; the plugin has no tests. |
| 2026-10-02 | `sharepoint-provisioning` retrofitted (19 skills): Regenerated the 18 uniform executor skills from one template (the old body had corrupted code fences such as `\\\ash` and leaked escapes like `\\-Execute\\`) and rewrote `sharepoint-apply-provisioning-plan`; one shared plugin-root reference (`provisioning-executor-contract.md`: safety contract, the plan `confirmation_token` vs fixed `-ConfirmToken` distinction, connection/config, plan-shape pointers, and a 28-script executor table with tokens verified against the scripts). **Fixed wrong documentation:** three skills documented tokens the scripts reject (`DETACH-SPO-CONTENT-TYPE-FROM-LIST` -> `DETACH-SPO-CONTENT-TYPE`; `REMOVE-SPO-CONTENT-TYPE` -> `REMOVE-SPO-CONTENT-TYPES`; `UPDATE-SPO-CONTENT-TYPE` -> `UPDATE-SPO-CONTENT-TYPES`) and the `task-success.json` files I had authored for them copied the wrong tokens, now regenerated; `sharepoint-remove-site-column` claimed post-deletion verification the script does not do (description corrected); the delete skills no longer imply in-use guards the scripts lack. Found (not changed): `spo-trigger-reindex.ps1`'s header documents another script's plan shape (copy-paste). Every documented token across all 19 SKILL.md and eval files now matches the scripts. Strict audit passes in source and installed mode; the plugin has no tests. |
| 2026-10-02 | `sharepoint-schema-reconciliation` retrofitted (4 skills): SKILL.md rewritten for all 4; 5 plugin-root references (shared pipeline/write-safety/executor-locations plus one details reference per skill); `plugin:` corrected from `sharepoint-provisioning`; three skills had no scripts linked at all (the Python modules, their imports and `provisioning_outcomes.py` are now symlinked in; every quick-start was run from an installed copy); the executor pointer named a non-existent `sharepoint-migration-planning` skill, now `sharepoint-provisioning`'s `sharepoint-apply-provisioning-plan` (and the calendar executor, which lives in the migration-planning plugin, is stated accurately); removed the stale "THE ONLY WRITE-capable skill" claim (the calendar skill also has a gated apply); `task-success.json` added to all 4; `tests/test_plugin_independence.py` exemption set extended to `task-success.json`. Fixed `temp/skill-retrofitting/tools/verify-plugin.sh`, which showed a failing test count yet printed RESULT: OK (now fails on any test failure). Strict audit passes in source and installed mode; 100 plugin tests pass. |
| 2026-10-02 | `sharepoint-spfx-authoring` retrofitted (10 skills): SKILL.md rewritten for all 10 (the 473-line form-customizer skill is now ~60 lines, with the 'deployed is not associated' hard gate in Constraints); 16 plugin-root references added (shared live-write/gate table, naming and versioning, pre-flight, deploy and publish runbooks, app-catalog request runbook, three form-customizer references, and one details reference per scaffold/workbench skill); `add-contents.py` used to add Contents to 5 long existing references. **Documentation corrections:** the old docs never said that `deploy-spfx-package.ps1`, `publish-spfx-package.ps1` and `provision-sample-dossier-schema.ps1` write immediately with no dry run, or that `register-listview-command-set.ps1` has no `-Execute` (only `-WhatIf`); the form-customizer diagram numbered steps differently from the body (now consistent, 11 steps); the publish and workbench-setup skills used repo-root script paths, a real tenant/client GUID, and project-specific paths and site names (removed); the package skill repeated one command block; two skills duplicated the naming table (now one shared reference). Linked the previously unmentioned scripts into their skills (`setup-spfx-workbench.ps1` and `check-spfx-toolchain.ps1` into the workbench skill; the master-detail templates and the 18-file reference project as file-level links so 'Option A' works when installed). Both Python scaffolders were run from installed copies. `task-success.json` added to all 10. Strict audit passes in source and installed mode; 3 plugin tests pass. |
| 2026-10-02 | `sharepoint-agents-and-skills` retrofitted (15 skills): 15 skills retrofitted; last plugin |
