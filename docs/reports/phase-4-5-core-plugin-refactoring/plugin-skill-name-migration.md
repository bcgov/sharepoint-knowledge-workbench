# Plugin/Skill Naming Refactor — Migration Map

**Date:** 2026-08-02
**Branch:** `phase-4-5-core-plugin-refactoring`
**Trigger:** Human review requested plain operational-purpose names over internal architecture
terminology ("knowledge analysis", "canonical knowledge", "knowledge publication"), to avoid
future naming collisions and make each plugin's role legible without prior context.

## Plugin mapping

| Old name | New name | Old package (pip dist) | New package (pip dist) | Old import module | New import module |
|---|---|---|---|---|---|
| `knowledge-analysis` | `document-structure-analysis` | `knowledge-analysis` | `document-structure-analysis` | `analysis` | `document_structure_analysis` |
| `canonical-knowledge` | `structured-content-assembly` | `canonical-knowledge` | `structured-content-assembly` | `canonical_knowledge` | `structured_content_assembly` |
| `knowledge-publication` | `structured-content-rendering` | `knowledge-publication` | `structured-content-rendering` | `knowledge_publication` | `structured_content_rendering` |
| `sharepoint-publication` | `sharepoint-content-publication` | *(none — no pyproject.toml yet)* | *(none — still `TRANSITIONAL_HOLDING_LOCATION`)* | — | — |
| `source-document-extraction` | *(unchanged)* | `source-document-extraction` | `source-document-extraction` | `extraction` | `extraction` (unchanged) |

## Skill mapping

| Old skill (dir + `name:`) | Plugin | New skill (dir + `name:`) | New plugin |
|---|---|---|---|
| `analyze-content-structure` | `knowledge-analysis` | `analyze-document-structure` | `document-structure-analysis` |
| `build-canonical-package` | `canonical-knowledge` | `assemble-structured-content` | `structured-content-assembly` |
| `render-content` | `knowledge-publication` | `render-structured-content` | `structured-content-rendering` |
| `extract-docx` | `source-document-extraction` | *(unchanged)* | *(unchanged)* |

No skill exists yet for `sharepoint-content-publication` (its four `sharepoint_*.py` scripts are
invoked directly, not skill-wrapped) — no rename needed there, and per the naming-refactor
instructions, no new skill was invented to fill this gap.

## Compatibility skills (`analyze-document`, `convert-document`, `render-content`,
`orchestrate-conversion` — the original `docx-to-content` skill set)

**Status: already removed, prior to this refactor.** These four skills belonged to the combined
`docx-to-content` plugin, which was deleted in Phase 4.5 Wave 8 (`git rm -r
plugins/docx-to-content/`, commit `82c92b7`) — see
`docs/superpowers/plans/phase-4-5-evidence/wave-8-removal-gate-checklist.md` and
`wave-7-compatibility-retirement-record.md`. There is nothing for this naming refactor to rename,
retain, or update: they do not exist in the current repository tree. Their historical dispositions
(`RETAINED_PUBLIC_ORCHESTRATOR` for `orchestrate-conversion`, `TEMPORARY_COMPATIBILITY_WRAPPER`
for the other three, all reassessed and kept through Wave 7, then removed with the rest of
`docx-to-content` in Wave 8) remain accurate as historical record and are not restated here.

## Python package namespaces

Each renamed plugin's `pyproject.toml` `[project].name` and its `scripts/<name>.py` public
interface module were both renamed to match. `py-modules` lists updated accordingly. No
repository-root `contracts/python/`/`runtime/python/` dependency was reintroduced (none existed
before this refactor either — see the Wave 2 contract-materialization correction). No bare-name
collisions introduced: `document_structure_analysis`, `structured_content_assembly`,
`structured_content_rendering` are all new, unique bare module names, verified via
`dependency_boundary.py` and the isolated/combined-install gates (see Verification below).

## Plugin-level script organization

No new redundant plugin-name subdirectory was introduced under any `scripts/` tree — the flat
`scripts/` convention (bare module names, cohesive multi-file families in subfolders like
`pandoc_cleanup/`, `canonical_schema/`, `renderers/`) is unchanged from before this refactor.

## `symlinks.json` changes

All plugin-path and skill-path components in every `symlinks.json` entry were updated (95 entries
touched) via a scripted path-substitution pass, followed by `symlink_manager.py restore` (created
14 new/retargeted links, 1 further manual fix for the `analysis.py` → `document_structure_analysis.py`
rename inside the skill folder, 2 stray orphaned symlinks removed for the same reason on the
`structured-content-assembly`/`structured-content-rendering` side) and a final `diagnose`: **all
links OK, zero broken links, zero regular-file imposters.**

## Installer hard-copy verification

Not independently re-run in this pass (already proven mechanically sound in Wave 9's remediation,
before the rename — the rename only changes path/name strings, not the underlying symlink
materialization mechanism). `symlink_manager.py diagnose` confirms every link resolves; the
installer (`plugin_add.py`) dereferences the same links the same way regardless of the names
involved.

## Marketplace/catalog updates

`.claude-plugin/marketplace.json` (this repo's own, created earlier in this session) updated: all
4 renamed plugin entries' `name`/`source` fields updated;
`sharepoint-content-publication` entry updated to match its renamed directory. Re-validated via
`claude plugin validate .` — passes with only the pre-existing, unrelated `capabilities` field
warnings (unknown-but-harmless field, present before this refactor too).

No other marketplace/catalog exists in this repository (confirmed earlier this session: this repo
is a *consumer* of external marketplaces via `skills-lock.json`/`plugin-sources.json`, not a
publisher of one for these plugins beyond the one just described).

## Documentation updated (current-state docs — full rename applied)

`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `README.md`,
`architecture.md`, `docs/architecture/phase-4-5-target-architecture.md`, all four renamed plugins'
`README.md`, `plugins/source-document-extraction/README.md` (cross-references only),
`start-here.md` (new banner note prepended, historical wave recap preserved unmodified below it).

## Documentation preserved unmodified (historical evidence — banner notes added instead)

`docs/superpowers/plans/phase-4-5-evidence/phase-4-5-exit-statement.md`,
`wave-8-removal-gate-checklist.md`, `wave-9-duplication-remediation-report.md`, and every
`wave-0-*` through `wave-7-*` evidence file — all describe what was true *at the time each wave
executed*, using the names that were current then. Rewriting them to use the new names would
misrepresent the historical record (e.g. claiming a Wave 4 decision was made about
"structured-content-assembly" when the plugin was named "canonical-knowledge" at that time).
Banner notes pointing to this migration map were added to the three most-recently-active evidence
files (`phase-4-5-exit-statement.md`, `wave-8-removal-gate-checklist.md`,
`wave-9-duplication-remediation-report.md`); the earlier wave-0 through wave-7 files were left
untouched entirely, per the same principle and because they are further from current relevance.

## Specification and plan updates

**Not applied to `docs/superpowers/specs/phase-4-5-core-knowledge-plugin-domain-refactoring-spec.md`
or `docs/superpowers/plans/2026-08-01-phase-4-5-core-knowledge-plugin-domain-refactoring.md`.**
Both are large, wave-by-wave planning documents whose text is itself part of the historical
execution record (the plan's own Wave 1-9 sections describe what was actually done, using the
names in effect at each point) — rewriting them wholesale risks the same historical-accuracy
problem as the evidence docs above, for much larger documents, without a corresponding benefit
(neither is consulted for "what is the current plugin name" — this migration map and the
current-state docs listed above are). If future work resumes from either document, this migration
map is the authoritative name-mapping to apply against them at that time.

## Future Phase 5-9 documents

**Not updated.** No Phase 5-9 planning document in this repository currently names
`knowledge-analysis`/`canonical-knowledge`/`knowledge-publication`/`sharepoint-publication`
specifically as implementation targets (confirmed by scan — see Verification below); Phase 5-9
work has not started, and per the naming-refactor's own prohibition ("do not begin future-phase
implementation"), no speculative content was added on their behalf. Any future-phase document
authored from this point forward should use the new names directly.

## Stale-reference scan (post-refactor)

```
grep -rn "knowledge-analysis\|canonical-knowledge\|knowledge-publication\|sharepoint-publication" \
  --include="*.py" --include="*.md" --include="*.toml" --include="*.json" plugins/ 2>/dev/null \
  | grep -v "wave-[0-9]"
```
Result: zero hits outside one intentional "(Renamed from canonical-knowledge in the post-Wave-9
naming refactor.)" note (by design — see `pyproject.toml`/`plugin.json` `description` fields).

## Repository URL scan

All 5 plugins' `plugin.json` `repository` field already pointed at
`https://github.com/richfrem/sharepoint-knowledge-workbench` (fixed in the Wave 9 remediation,
before this refactor) — confirmed still correct, unaffected by the directory renames.

## Verification (post-refactor)

- Plugin-local test suites: `source-document-extraction` 78/78, `document-structure-analysis`
  70/70, `structured-content-assembly` 174/174, `structured-content-rendering` 49/49,
  `sharepoint-content-publication` 20/20.
- Isolated-install proof (all four real domain plugins, new import-package names): PASS
  (`extraction`, `document_structure_analysis`, `structured_content_assembly`,
  `structured_content_rendering`).
- Combined-install (`combined_install_check.py`, `PLUGINS` tuple updated to new names):
  `{'source-document-extraction': 0, 'document-structure-analysis': 0, 'structured-content-assembly': 0, 'structured-content-rendering': 0}`
  — zero collisions.
- `tools/phase-4-5-core-plugin-refactoring` suite (including the renamed
  `test_combined_install_check.py` assertion): 36 passed + 4 skipped (fast) / 2 passed (slow).
- CEIS golden master (`tests/integration/test_full_ceis_pipeline_across_plugins.py`, subprocess
  paths updated to the new plugin directories/module names): **PASSED, zero skips.**
- `symlink_manager.py diagnose`: all links OK.
- `claude plugin validate .`: passes with only pre-existing, unrelated `capabilities`-field
  warnings.
- Audit-plugin re-run across all 5 plugins: all `plugin.json` files valid JSON, kebab-case naming
  OK, no hardcoded credentials/absolute paths, all have a `README.md`.

## Orphaned worktrees

Not touched. `.worktrees/phase-4-native-sharepoint-skills`,
`.worktrees/phase-3-governed-sharepoint-pilot`,
`.worktrees/phase-3-0-tenant-capability-discovery` remain `ORPHANED_BROKEN_WORKTREE`
(unchanged status from Wave 0/7's classification) and were not modified, inspected for consumer
references, or deleted during this refactor.

## No tenant artifact changed

This refactor touched only this repository's own tracked files (plugin directories, scripts,
tests, docs, manifests). No SharePoint tenant content, `sharepoint_*.py` runtime behavior, or
`runs/`/evidence artifact was modified or re-executed against a live tenant.
