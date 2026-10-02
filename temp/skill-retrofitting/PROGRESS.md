# Skill retrofit: progress and handoff state

Last updated: 2026-10-02 (after sharepoint-page-modernization). Read `PLAN.md` first for the how-to. This file is the live state: update it at the end of every
plugin (and whenever you stop mid-plugin, using the "In flight" section).

## Contents

- [Where we are](#where-we-are)
- [Retrofitted plugins and skills](#retrofitted-plugins-and-skills)
- [Error-fixed only](#error-fixed-only)
- [Remaining queue](#remaining-queue)
- [In flight](#in-flight)
- [Open decisions and questions for the user](#open-decisions-and-questions-for-the-user)
- [Pickup checklist for a new agent](#pickup-checklist-for-a-new-agent)
- [Log](#log)

## Where we are

- Branch: `chore/retrofit-skills-standard`, based on `origin/main` (`69809a2`). Draft PR: https://github.com/bcgov/sharepoint-knowledge-workbench/pull/7 (the user merges it when every plugin is done).
- PR #5 (`.gitignore` change) was already merged by the user; this effort continues on a new branch and PR.
- Audit snapshot: 104 skills, 104 pass, 0 fail, 0 errors; remaining warnings are layout/size items in plugins not yet retrofitted
  (the tracker has exact counts).
- **11 of 16 plugins fully retrofitted (52 of 104 skills).** All 104 skills have `evals/evals.json`; 59 have
  `evals/task-success.json`.
- Next plugin to take: **`sharepoint-page-modernization-execution`**, then the rest of the queue top to bottom (alphabetical).
  `sharepoint-agents-and-skills` is deliberately **last** (user's instruction).

## Retrofitted plugins and skills

"Retrofitted" = `SKILL.md` in the standard layout, detail in plugin-root references with symlinks, `plugin:` frontmatter
correct, `task-success.json` present, `verify-plugin.sh <plugin>` prints `RESULT: OK`. Verified 2026-10-02.

| Plugin | Skills (count) | Retrofitted skills |
|---|---|---|
| workbench-setup | 5 | `workbench-initialize-document-workflow`, `workbench-initialize-workbench-config`, `workbench-request-app-registration`, `workbench-resolve-workbench-paths`, `workbench-validate-workbench-environment` |
| sharepoint-discovery | 15 | `sharepoint-analyze-custom-forms`, `sharepoint-analyze-page-inventory`, `sharepoint-analyze-permissions`, `sharepoint-analyze-site-navigation`, `sharepoint-analyze-webpart-code`, `sharepoint-audit-managed-metadata`, `sharepoint-audit-onprem-schema-drift`, `sharepoint-audit-schema`, `sharepoint-collect-sharepoint-inventory`, `sharepoint-diff-sharepoint-schema`, `sharepoint-extract-calculated-columns`, `sharepoint-extract-choice-fields`, `sharepoint-generate-discovery-report-set`, `sharepoint-generate-sharepoint-schema-from-export`, `sharepoint-scaffold-schema-definition` |
| content-assembly | 1 | `content-assemble-structured-content` |
| content-extraction | 1 | `content-extract-docx` |
| content-rendering | 7 | `content-compare-rendered-output`, `content-create-aspx-rendering-template`, `content-create-markdown-rendering-template`, `content-render-multipage-markdown`, `content-render-sharepoint-aspx`, `content-validate-rendered-output`, `content-validate-rendering-template` |
| content-structure-analysis | 1 | `content-analyze-document-structure` |
| sharepoint-content-migration | 2 | `sharepoint-audit-list-content`, `sharepoint-migrate-sharepoint-list-content` |
| sharepoint-content-publication | 6 | `sharepoint-publish-aspx-to-sharepoint`, `sharepoint-publish-markdown-to-sharepoint`, `sharepoint-reconcile-sharepoint-publication`, `sharepoint-rollback-sharepoint-publication`, `sharepoint-upload-content`, `sharepoint-validate-publication` |
| sharepoint-link-remediation | 5 | `sharepoint-extract-links`, `sharepoint-remediate-document-content-links`, `sharepoint-remediate-field-image-references`, `sharepoint-remediate-links`, `sharepoint-validate-link-integrity` |
| sharepoint-migration-planning | 5 | `sharepoint-analyze-sharepoint-dependency-graph`, `sharepoint-discover-sharepoint-site-inventory`, `sharepoint-generate-sharepoint-wave-scripts`, `sharepoint-plan-sharepoint-deployment-waves`, `sharepoint-setup-sharepoint-migration-project` |
| sharepoint-page-modernization | 4 | `sharepoint-analyze-aspx-pages`, `sharepoint-compose-page-preview`, `sharepoint-convert-aspx-pages`, `sharepoint-generate-conversion-report` |

What was done to each retrofitted skill (details in the tracker's Change log):

- `SKILL.md` rewritten to the standard layout (<= 80 lines in nearly all cases) with Constraints up front; every fact kept,
  with long detail moved to plugin-root references linked by file-level symlinks.
- `plugin:` frontmatter corrected; `examples:` made runnable from the skill root; stale `pip install -e plugins/...`,
  repo-root `DEPENDENCIES.md` and `plugins/...` command paths removed; stale plugin names updated.
- `evals/task-success.json` added (3 scenarios, authored from the SKILL.md, **not observed**).
- Missing links to imported modules added so the installed copy imports (7 modules missing across 5 skills in 4 plugins, all fixed).
- Plugin-specific notes: `workbench-setup` validate skill now documents `test-pnp-effective-capability-probe.ps1` (the old
  `test-grant-tier-probe.ps1` no longer exists) and gained a symlink for `test-network-connectivity.ps1`;
  `sharepoint-discovery` skills' `plugin:` fixed from `sharepoint-schema`; `sharepoint-content-migration` migrate skill's
  broken `.to_dict()` example fixed; `sharepoint-content-publication` skills used `../../scripts/...` paths (escaping the skill) and had no
  scripts linked: now skill-root-relative with scripts, the config helper and the CSV-format doc symlinked in, and the executors'
  `-ConfigPath` default (does not resolve when installed) documented.

## Error-fixed only

These 7 skills had audit **errors** (now fixed) but their layout is **not yet aligned**; they are retrofitted when their
plugin comes up in the queue:

| Plugin | Skill | What was fixed |
|---|---|---|
| sharepoint-link-remediation | `sharepoint-remediate-field-image-references` | description contained `<img>` (XML-tag error) |
| sharepoint-page-modernization | `sharepoint-convert-aspx-pages` | linked missing `assets/gap-notice.template.html` (symlink to `scripts/assets/`) |
| sharepoint-page-modernization | `sharepoint-generate-conversion-report` | linked missing `assets/manifest-schema.json` |
| sharepoint-page-modernization-execution | `sharepoint-copy-page-between-sites` | real `acceptance-criteria.md` moved to plugin root and symlinked |
| sharepoint-spfx-authoring | `sharepoint-scaffold-spfx-listview-command-set` | 3 real files moved to plugin root and symlinked |
| sharepoint-spfx-authoring | `sharepoint-scaffold-spfx-react-app` | 3 missing reference links resolved with symlinks |
| sharepoint-spfx-authoring | `sharepoint-setup-spfx-workbench` | real `acceptance-criteria.md` moved to plugin root and symlinked |

Also: 27 skills in `sharepoint-discovery` (5), `sharepoint-page-modernization-execution` (3) and `sharepoint-provisioning` (19) had
neither eval file; routing + task-success evals were **authored** for them (not observed). That is why `sharepoint-provisioning`
and `sharepoint-page-modernization-execution` show `task-success.json` already even though their layout is not retrofitted.

## Remaining queue

Work top to bottom. Counts and notes are from the 2026-10-02 audit.

| # | Plugin | Skills | Line counts (current) | Plugin-specific notes |
|---|---|---|---|---|
| 1 | sharepoint-page-modernization-execution | 4 | 59 36 77 49  | All four have `plugin: sharepoint-content-publication` (wrong; set to this plugin). 3 skills (convert-page-to-modern, execute-page-bulk-migration, validate-page-migration) already have authored evals + task-success; `copy-page-between-sites` (error-fixed) has existing evals but no task-success. Real writes gated by -Execute + ConfirmToken. |
| 2 | sharepoint-provisioning | 19 | 39 39 71 39 39 39 39 39 44 39 39 39 39 39 39 39 39 39 39  | 19 skills, 18 follow one uniform dry-run template (script, -PlanPath, -Execute, exact -ConfirmToken). Evals + task-success already authored. `apply-provisioning-plan` is the odd one (dispatches to 25 scripts; 71 lines). Ideal for a shared reference describing the common safety contract. |
| 3 | sharepoint-schema-reconciliation | 4 | 80 81 102 105  | All four have `plugin: sharepoint-provisioning` (wrong). Zero tenant I/O is enforced by a test in this plugin; keep that statement. |
| 4 | sharepoint-spfx-authoring | 10 | 55 122 117 93 473 67 72 72 117 56  | 10 skills; `scaffold-spfx-form-customizer` is 473 lines (the largest SKILL.md in the repo; needs real splitting). 3 error-fixed skills. plugin.json version is 1.0.0 (others 0.1.0-alpha.1). References over 100 lines need `## Contents`. |
| 5 | sharepoint-agents-and-skills | 15 | 42 31 30 46 37 83 46 45 61 44 42 124 40 38 44  | LAST by the user's instruction. `plugin:` frontmatter missing in all 15. Includes agent/native-skill create/deploy/backup/restore skills. |

Skill names for each remaining plugin: `ls plugins/<plugin>/skills`. The per-skill table in
`docs/reports/skill-standard-alignment/tracker.md` has current open rules per skill.

## In flight

Nothing is half-done right now. Convention while working a plugin: after **each skill** passes `--strict` run
`tools/mark-skill-done.sh <skill>` (adds it to `retrofitted.txt` and refreshes the tracker) and add the skill to the checklist
below; after the **plugin** passes `tools/verify-plugin.sh`, move the plugin into `retrofitted.txt` as `plugin <name>`, update
the sections above, commit, push, and reset this section. If you stop mid-plugin, leave the checklist and any uncommitted
files listed here.

Current plugin: _(none started)_

| Skill | Status |
|---|---|
| _(none)_ | |

## Open decisions and questions for the user

1. Delete the three remaining empty old-name plugin folders (`source-document-extraction`, `structured-content-assembly`,
   `structured-content-rendering`)? Verified to hold only ignored caches; the fourth (`document-structure-analysis`) was
   already removed with approval. **Do not delete without the user's yes.**
2. Authored evals (routing + task-success) are derived from SKILL.md, not observed. The user should review them; real model
   results are not recorded anywhere yet.
3. Existing single-case `evals.json` files (a generic positive) have no negatives. Add near-miss negatives? (User has not
   asked; existing files are intentionally left untouched.)
4. `scripts/assets/` in `sharepoint-page-modernization`: relocate to plugin-root `assets/` per policy, or keep? Left as is.
5. Version bumps for retrofitted plugins: not done, not requested.
6. `audit-plugin` is broken in this install (missing `skill-authoring-contract.json`); plugin-level structure audits are not
   part of this effort. A fix belongs upstream in `agent-scaffolders`.
7. A "newer October 2026 Anthropic standard" was mentioned; no separate spec was available. Ask the user for its source if it
   should be applied.
8. `plugins/sharepoint-content-publication/.claude-plugin/plugin.json` still has `TRANSITIONAL_HOLDING_LOCATION (not a completed Phase 4.5 domain plugin...)`
   as its description; the plugin now has 6 real skills and real executors. Update the manifest description? (Not touched; the marketplace
   listing was corrected.)
9. `plugins/sharepoint-migration-planning/README.md` (lines ~90-105) still lists `spo-provision-site-columns.ps1`, `spo-provision-content-types.ps1` and `spo-provision-list.ps1` as
   scripts of that plugin; they live in `sharepoint-provisioning`. Only `spo-provision-calendar.ps1` is local. README not touched.
10. `sharepoint-page-modernization`: no script assembles the full `PageConversionManifest` (the report skill consumes one; the stage-4 CLI writes mapping + views). The README and the modernization
    agent still describe the pipeline as producing a manifest. Is a manifest-assembly step (script or agent instruction) wanted? Docs now say the caller or the agent assembles it.
11. A stale docstring in `plugins/content-structure-analysis/scripts/document_structure_analysis.py` still names the
   decommissioned `docx-to-content` orchestrator. Code change, deliberately not touched.

## Pickup checklist for a new agent

1. `git fetch origin && git checkout chore/retrofit-skills-standard && git pull` and confirm `git status` is clean.
2. Read `PLAN.md` (rules, recipe, gotchas) and this file.
3. Run `bash temp/skill-retrofitting/tools/verify-plugin.sh workbench-setup` as a smoke test of the tooling (expect `RESULT: OK`).
4. Take the first row of the [Remaining queue](#remaining-queue) not yet in `retrofitted.txt`.
5. Follow `PLAN.md` "Per-plugin procedure". After each skill run `tools/mark-skill-done.sh`; after each plugin commit and push and update this file's Log and Retrofitted sections.

## Log

| Date | Event |
|---|---|
| 2026-10-02 | Baseline audit: 104 skills, 93 pass / 11 fail, 16 errors, 643 warnings (`baseline.tsv`). |
| 2026-10-02 | PR #5 (ignore Agentic OS runtime state) merged by the user. New branch `chore/retrofit-skills-standard` cut from `origin/main`. |
| 2026-10-02 | `sharepoint-content-publication` retrofitted (6 skills), marketplace listing corrected, verified `RESULT: OK`. |
| 2026-10-02 | `sharepoint-link-remediation` retrofitted (5 skills): layout retrofit; description XML tag already fixed; validate skill now links link_rules.py (its import failed when installed); plugin independence test exemption extended to evals/task-success.json |
| 2026-10-02 | `sharepoint-migration-planning` retrofitted (5 skills): layout retrofit; wave-scripts doc corrected (3 of 4 listed executors belong to sharepoint-provisioning); all five skills now self-contained (provisioning_outcomes, assets, rules linked in); marketplace listing corrected |
| 2026-10-02 | `sharepoint-page-modernization` retrofitted (4 skills): layout retrofit; the documented CLI flags were wrong (now the real ones); stale pointer to the page-conversion executor fixed; outcomes.py linked into the report skill; marketplace listing corrected |
| 2026-10-02 | Branch pushed and draft PR #7 opened against `main`; backlog committed as 12 per-plugin commits plus a docs commit. |
| 2026-10-02 | Retrofitted 7 plugins (32 skills; an earlier version of this log said 39, which was the task-success file count), fixed 8 error skills, authored evals for 27 skills, updated marketplace `sharepoint-discovery` description. Tooling and this handoff written. |
