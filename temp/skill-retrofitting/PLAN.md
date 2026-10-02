# Skill retrofit: plan and operating manual

Audience: any agent (Claude Code, Antigravity CLI, Codex, Gemini CLI, ...) taking over this work mid-stream.
Read this file first, then `PROGRESS.md` for the current state and the next plugin to take.

## Contents

- [Goal](#goal)
- [Ground rules](#ground-rules)
- [The standard](#the-standard)
- [Tools in this folder](#tools-in-this-folder)
- [Per-plugin procedure](#per-plugin-procedure)
- [Per-skill recipe](#per-skill-recipe)
- [Evals policy](#evals-policy)
- [Git and PR workflow](#git-and-pr-workflow)
- [Gotchas learned the hard way](#gotchas-learned-the-hard-way)
- [Stale-name map](#stale-name-map)
- [Definition of done](#definition-of-done)

## Goal

Bring every skill under `plugins/*/skills/*` (104 skills in 16 plugins in `bcgov/sharepoint-knowledge-workbench`) up to
the skill authoring standard, keeping behavior intact, and track it. Success means: every skill passes
`audit_skill.py --strict` in **source** and **installed** mode, imports cleanly when installed, has `evals/evals.json`
and `evals/task-success.json`, and the tracker at `docs/reports/skill-standard-alignment/tracker.md` is current.

## Ground rules

Repo rules (`AGENTS.md`, authoritative) that matter here:

1. **No file deletions without the user's explicit permission.** Moving a file is allowed; deleting is not.
   Three old-name leftover plugin folders (`plugins/source-document-extraction`, `structured-content-assembly`,
   `structured-content-rendering`) are empty shells awaiting the user's approval to delete. Do not delete them unasked.
2. **Symlinks only through `symlink_manager.py`.** Never `ln -s`. Never leave a real file where a managed symlink belongs.
   Canonical files live at the plugin root; each skill gets file-level symlinks. Directory symlinks are forbidden.
3. **Write scratch output to `temp/`**, never the repo root. `temp/` is git-ignored; this folder is force-added on purpose.
4. **Do not install system tools** (brew etc.) without asking.
5. **Do not invent eval outcomes presented as observed.** See [Evals policy](#evals-policy).
6. **Use the shipped scripts; do not write ad hoc replacements.** The audit, symlink manager and the scripts in
   `tools/` here are the tools. (A one-line shell/awk summary of their output is fine.)
7. Sub-agents: use the cheapest model that can do the job, and only if the work needs spawning at all.
8. The user merges the PR. Never merge it yourself.

## The standard

Measured by `.agents/skills/audit-skill/scripts/audit_skill.py` against its bundled `references/skill-authoring-contract.json`
(contract version 1.0.0), plus the Anthropic best-practices reference bundled in that skill. No separate "October 2026
Anthropic spec" was available; if the user supplies one, add a gap column to the tracker.

`SKILL.md` layout (sections in this order):

```
---
name: <must equal the directory name>
plugin: <must equal the owning plugin directory name>
description: <what it does + "Use when ..." ; <= 1024 chars; NO angle-bracket tags like <img> or <DocumentId>>
allowed-tools: ...
examples: (optional)
---
# Title
One or two sentences of purpose.
## Contents        (links to the sections below; must be inside the first 100 lines)
## Constraints     (safety contract, scope limits, gates, what NOT to do; the first things an agent must see)
## Quick start     (smallest working command/snippet)
## Workflow        (numbered steps)
## Verification    (observable checks)
## References      (direct links to references/*.md, each with a reading condition: "read when ...")
```

Limits: aim for <= 80 lines (advisory; hard guideline < 500 body lines); linked references over 100 lines need their own
`## Contents`; required references must be linked **directly** from `SKILL.md` (not only from another reference).
Tiny skills may omit sections that add nothing (`## References` if there are none), but keep Contents, Constraints,
Quick start, Workflow and Verification: the auditor warns on each missing heading.

Packaging (from `.agent/rules/plugin-architecture-policy.md`):

- Canonical scripts/references/assets live at the **plugin root** (`plugins/<p>/scripts|references|assets`).
- Each skill gets **file-level symlinks** to what it uses (`skills/<s>/scripts|references|assets/<file>`).
- In source mode, any *real* file inside a skill's `scripts/`, `references/` or `assets/` is an **error**
  (`packaging.resource`). Move it to the plugin root and link it back.
- Paths inside a skill are **relative to the skill root**. No repo-root paths (`plugins/<p>/...`), no `pip install -e
  plugins/<p>`, no "see DEPENDENCIES.md at the repository root". An installed skill must be self-contained.

## Tools in this folder

All run from anywhere inside the repo. Use `bash` (not zsh) for these scripts.

| Tool | Purpose |
|---|---|
| `tools/verify-plugin.sh <plugin>` | The full per-plugin gate: strict audit (source), strict audit of a materialized copy (installed), import sweep from the copy, plugin tests, symlink health, marketplace paths, eval JSON validity. Must print `RESULT: OK`. |
| `tools/refresh-tracker.sh` | Re-audits all 104 skills and rewrites the audit-derived sections of the tracker (per-skill table, per-plugin progress, summary, rule counts). Reads `retrofitted.txt` for which plugins/skills are "Retrofitted". Does not touch the tracker's Change log or Decisions. |
| `tools/gen-evals.sh <data-file>` | Generates `evals/evals.json` and `evals/task-success.json` for many uniform skills from a `|`-separated data file (see `tools/examples/provisioning-evals.dat`). Run from the plugin's `skills/` directory. Overwrites. |
| `tools/finish-plugin.py <plugin> "<note>" [--tracker-note "..."]` | After a finished plugin: updates `retrofitted.txt`, PROGRESS (queue, retrofitted table, counts, next plugin, log) and the tracker's task-success line and change log. Then run `refresh-tracker.sh`. |
| `tools/add-contents.py <file.md>...` | Adds an auditor-compatible `## Contents` block to long plugin-root references (the `navigation.reference-toc` warning). Idempotent. |
| `tools/mark-skill-done.sh <skill>...` | After each finished skill: records it in `retrofitted.txt` and refreshes the tracker tables. |
| `baseline.tsv` | The first full audit (before any edits), used for the tracker's Baseline column. Do not regenerate. |
| `retrofitted.txt` | Source of truth for which plugins/skills are retrofitted. Edit it when you finish a plugin. |

Core commands:

```bash
python3 .agents/skills/audit-skill/scripts/audit_skill.py <skill-dir> --mode source --strict      # one skill
python3 .agents/skills/audit-skill/scripts/audit_skill.py . --all --mode source                   # everything
python3 .agents/skills/symlink-manager/scripts/symlink_manager.py create --src <plugin-root file> --dst <skill file> --description "..."
python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose                        # must say "All links OK."
python3 .agents/skills/audit-plugin/scripts/audit_marketplace_sources.py .                        # marketplace source paths
```

(`audit-plugin/scripts/audit.py` is **broken** in this install: its `references/skill-authoring-contract.json` is missing.
Do not use it.)

## Per-plugin procedure

Take one plugin at a time, in the order listed in `PROGRESS.md`.

1. `ls -a plugins/<p>`; list skills; read every `SKILL.md` and each skill's `scripts/`, `references/`, `assets/` link layout
   (`ls -la ... | grep -- '->'`). Note: `plugin:` frontmatter value, repo-root paths, stale plugin names, text that
   documents scripts which are not actually linked into the skill.
2. Retrofit each skill (next section). Write plugin-root references first, then `SKILL.md`, then symlinks.
3. Run `tools/verify-plugin.sh <p>` until `RESULT: OK`. Fix import gaps by linking the missing module (see Gotchas).
4. Check `.claude-plugin/marketplace.json`: entries must stay `strict: true`, sources valid; update the entry's
   `description` if the retrofit revealed it is stale. Do not bump versions unless the user asks.
5. Add the plugin to `retrofitted.txt`; run `tools/refresh-tracker.sh`; add a Change log row (and fix the "only N of 104
   skills have task-success evals" line) in `docs/reports/skill-standard-alignment/tracker.md`.
6. Update `temp/skill-retrofitting/PROGRESS.md` (mark the plugin done, list its skills, set the next plugin).
7. Commit and push (see [Git and PR workflow](#git-and-pr-workflow)). One commit per plugin.

## Per-skill recipe

1. **Audit first**: `audit_skill.py <skill> --mode source`. Read the findings.
2. **Read everything**: `SKILL.md`, the scripts' docstrings/CLI `--help`, and any code the doc claims to describe. Verify claims
   against the code (an example that calls a method that does not exist is worse than no example).
3. **Split content** between `SKILL.md` and plugin-root references:
   - Stays in `SKILL.md`: purpose, safety/scope constraints (verbatim intent), the smallest working command, the numbered
     workflow, what to check, and linked references with reading conditions.
   - Goes to `plugins/<p>/references/<topic>.md`: API signatures and long usage, scripts tables, rationale, platform
     evidence, provenance ("source repository only"), outcome tables, long examples. Give every reference a `## Contents`
     if it is over 100 lines. Name references uniquely per topic (`<topic>-details.md`, `<skill>-<name>.md`); several
     skills may link the same reference.
   - **Nothing is deleted**: every fact in the old `SKILL.md` must land somewhere (SKILL.md or a reference).
4. **Frontmatter**: set `plugin:` to the owning plugin dir; rewrite `description` as "what it does. Use when ... . Boundaries."
   (no `<...>`; keep every boundary claim from the original); make `examples:` runnable from the skill root:
   `python3 -c "import sys; sys.path.insert(0, 'scripts'); from <module> import ..."`.
5. **Remove** `pip install -e plugins/...`, repo-root `DEPENDENCIES.md` pointers, `plugins/...` paths in commands (make them
   `scripts/...`). State external tools plainly ("pandoc must be on PATH").
6. **Symlink** each new reference into the skill: `symlink_manager.py create --src plugins/<p>/references/<f> --dst
   plugins/<p>/skills/<s>/references/<f>`. Make the `references/` dir first (`mkdir -p`).
7. **Self-containment**: build a materialized copy (`cp -RL <skill> $TMP/`) and `import` every non-hyphenated module in
   `scripts/` with `scripts/` on `sys.path`. A `ModuleNotFoundError` means a module imported by another is not linked into
   this skill's `scripts/`; link it.
8. `audit_skill.py <skill> --mode source --strict` must be clean.

## Evals policy

- Routing evals: `evals/evals.json`, a JSON array of `{"query": "...", "should_trigger": true|false}` (existing files may
  also carry `name/description/prompt/expected`; keep them). Task-success evals: `evals/task-success.json`, an array of
  `{"query": "...", "expected_behavior": ["...", "..."]}` (non-empty list of non-empty strings; optional `files`).
- **Never modify an existing `evals.json`** (its identities are part of routing). Add `task-success.json` beside it.
- When a skill has no `evals.json`, author 4 positive and 4 near-miss negative cases (negatives should be plausible prompts
  that belong to a *sibling* skill, plus at most one unrelated), and 3 task-success scenarios: a normal run, a refusal/safety
  case, a hand-off to the right skill.
- Everything authored this way is **derived from the SKILL.md, not observed from a model run**. Say so in the tracker. Never
  describe authored evals as tested.

## Git and PR workflow

- Feature branch: `chore/retrofit-skills-standard` (based on `origin/main`). PR is opened as a **draft** against `main`;
  the user merges it only when all plugins are complete. Keep pushing to the same branch after every plugin so nothing is lost.
- One commit per plugin, plus one for tracker/manifest/handoff docs. Stage by path (`git add plugins/<p>`), not `git add -A`:
  the working tree contains other changes.
- Commit message: `chore(skills): retrofit <plugin> to skill standard` with a short body (what changed, verification) and the
  trailer line for the agent that did the work (Claude: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`).
- `git push origin chore/retrofit-skills-standard`. The user authorized `--no-verify` for commits/pushes on this effort
  because the new control-plane git guards block commits from non-task branches. Use it only for this branch.
- `symlinks.json` is a shared registry edited by every symlink creation; commit it with the docs commit (or the plugin
  commit if you prefer), never lose it.
- `temp/` is git-ignored. This handoff folder is committed with `git add -f temp/skill-retrofitting` (excluding `.work/`).
- Never merge, never force-push over someone else's work, never rewrite pushed history.

## Gotchas learned the hard way

- **The shell is zsh.** Unquoted variables do not word-split; `PIPESTATUS` is `pipestatus`; `wc -l $UNSET` hangs reading
  stdin. Run helper scripts with `bash`. `sed -i ''` (BSD sed) on macOS.
- **`ls` hides dot-dirs**: `.claude-plugin/`, `.pytest_cache` do not show without `ls -a`.
- **The audit passing does not prove an installed skill works.** Five skills (in four plugins) passed the audit but failed to import when
  materialized, because a module imported by a linked script was not linked into the skill (`provisioning_outcomes`,
  `identity_core`, `plan_verification_core`, `topic_boundary_core`, `renderers/sharepoint_aspx`, `schema_definition`,
  `schema_export`). Always run the import sweep (`verify-plugin.sh` does).
- **Hyphenated scripts** (`generate-deep-forms-analysis.py`) are CLIs and cannot be imported by name; skip them in import sweeps.
- **Description XML-tag check**: `<img>`, `<DocumentId>` etc. in a description are errors. Use `{DocumentId}` or plain words.
- **Backtick paths are links to the auditor**: `` `assets/foo.md` `` in a SKILL.md body or reference resolves relative to the
  skill root and errors if missing. Either link/symlink the file or reword to "a plugin-level asset".
- **Linked references need an early `## Contents`** when > 100 lines (warning `navigation.reference-toc`). Add it to the
  canonical file at the plugin root.
- **Unique plugin-root names**: several skills used to ship a real `acceptance-criteria.md`; they were moved to
  `<skill>-acceptance-criteria.md` at the plugin root and symlinked back under the original name.
- **`scripts/assets/` convention** in `sharepoint-page-modernization`: its skills symlink assets to `scripts/assets/` (packaged
  data). Follow the sibling skills; whether to relocate to a plugin-root `assets/` is an open decision.
- `plugin:` frontmatter must equal the owning plugin directory; many skills still carry old pre-rename names or none.
- Old plugin names in text should be updated; see the map below.
- A skill's documented script list may not match what is actually linked into its `scripts/`; trust the filesystem. Some skills
  (e.g. `sharepoint-content-publication`) pointed at `../../scripts/...` (outside the skill) and had **no** scripts linked at all: link the
  script, its Python imports and any `.ps1` it dot-sources (`Get-WorkbenchConnectionConfig.ps1`) into the skill's `scripts/`.
- `.ps1` executors with `[string]$ConfigPath = (Join-Path $PSScriptRoot "..\..\..\config.psd1")` resolve to the repo root only from the plugin's
  `scripts/`; from an installed skill they do not. Document passing `-ConfigPath` or `-SiteUrl/-ClientId/-TenantId` explicitly.
- A reference can live outside `references/` at the plugin root (e.g. `docs/`); symlink it into the skill's `references/` from where it is.
- **Verify a body file is non-empty before `gh pr edit --body-file`** (a failed `sed` produced an empty file and blanked the PR description once; write PR bodies
  to `.work/pr-body.md` with a normal file write and check `wc -c`).
- **Count skills from the filesystem, not from memory**: use the plugin's `ls skills | wc -l`, or `tools/finish-plugin.py` (it computes totals). An earlier handoff
  note confused the task-success file count with the retrofitted-skill count.
- **Independence tests also scan shipped `.json`/`.py`/`.toml`/`.yaml` for forbidden strings** (e.g. `sharepoint-migration`, a source-repo marker, which also matches `sharepoint-migration-planning`). Keep such names out of
  authored eval JSON (say "the migration-planning plugin"); Markdown is not scanned. Always run the plugin's tests (`verify-plugin.sh` now fails on a test failure).
- Some plugins carry an **independence test** (`tests/test_plugin_independence.py` in `sharepoint-link-remediation` and `sharepoint-schema-reconciliation`) that
  forbids real files under `skills/` except `SKILL.md` and `evals.json`. The new standard adds `evals/task-success.json`, so the test's exemption set must include it.
- **Verify every documented token/flag against the code.** `sharepoint-provisioning` had three skills documenting `-ConfirmToken` values the scripts reject, and `sharepoint-page-modernization`
  documented CLI flags that do not exist. Grep the enforced value (`ConfirmToken -ne "..."`, `--help`) and compare; regenerate any authored eval that copied a wrong value.
- **Do not claim safety behavior the code lacks** (post-deletion verification, in-use guards). Read the script body, not just its header (headers can be stale or copy-pasted).
- The documented API in a SKILL.md can be wrong (e.g. `ItemMigrationPlan` has no `to_dict()`). Run examples before shipping them.

## Stale-name map

| Old name (in text/frontmatter) | Current |
|---|---|
| `source-document-extraction` | `content-extraction` |
| `document-structure-analysis` | `content-structure-analysis` |
| `structured-content-assembly` | `content-assembly` |
| `structured-content-rendering` | `content-rendering` |
| `sharepoint-schema` (plugin) | merged into `sharepoint-discovery` (and `sharepoint-schema-reconciliation` for provisioning-side reconciliation) |
| `docx-to-content` | decommissioned (Phase 4.5 Wave 8) |

## Definition of done

For the whole effort: `audit_skill.py . --all --mode source --strict` clean for all 104 skills; every plugin's
`verify-plugin.sh` prints `RESULT: OK`; `retrofitted.txt` lists all 16 plugins; tracker summary shows 104 pass / 0 fail / 0
errors and only expected residual warnings; marketplace valid; the draft PR is up to date on `origin`. Then tell the user it is
ready to merge. The user merges.
