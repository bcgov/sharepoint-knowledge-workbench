# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes, plus project-specific context for this repo.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code/content that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use scripts.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

- Don't "improve" adjacent content, comments, or formatting.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead content, mention it — don't delete it.
- Every changed line/file should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Verify before claiming done.**

For multi-step tasks, state a brief plan and verify each step (e.g. after a doc conversion,
grep for image links / headings and confirm counts before saying it's complete).

---

## Project-Specific Context

### Purpose

This repo is Phase 1 of a broader initiative — the **AI-Assisted Structured Knowledge
Workbench** — moving Word/PDF manuals from a document-centric model (content + formatting baked
together) to a content-centric model (Content + Template + Renderer = Published Output). Phase 1's
scope is narrower than the full initiative: prove structured knowledge conversion and canonical
content on one pilot document (the **CEIS Manual**) via a self-contained plugin. The full
initiative — repository/plugin boundaries beyond Phase 1, SharePoint delivery, native skills,
agents, publication, and evaluation — is planned in
`docs/vision/master-initiative-plan-workstreams-and-phases.md` (the authoritative, phase/subphase/
stage-level master plan, reviewed across multiple rounds of external adversarial review) and
originally proposed in `docs/vision/README.md` and
`docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md`. Only Phase 1 (complete)
and Phase 2 (spec + implementation plan approved, execution not yet started — see
`docs/superpowers/specs/2026-07-28-phase2-canonical-publication-contract-hardening-design.md` and
its companion plan) are currently authorized to be built; later phases are deliberately planned at
a structural level only, gated on evidence (tenant facts, pilot outcomes) that doesn't exist yet —
see the master plan's own detail-level discipline before assuming any phase beyond 2 is ready to
implement.

The active implementation is four independently-installable domain plugins under `plugins/` —
`source-document-extraction`, `document-structure-analysis`, `structured-content-assembly`, `structured-content-rendering`
(built from scratch under TDD, see
`docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design-v3-ammendments.md`,
`docs/superpowers/specs/phase-4-5-core-knowledge-plugin-domain-refactoring-spec.md`, and their
companion plans) — chained together via a real analyze→confirm→convert→render pipeline that takes
a source `.docx` through structural analysis, human plan confirmation, cleanup/chunking/
canonicalization, validation, and rendering to a multipage Markdown package, with atomic promotion
and full test coverage at every stage. Each plugin installs and runs standalone (`pip install -e
plugins/<name>`); see `docs/architecture/phase-4-5-target-architecture.md` for the as-built
distribution graph. This decomposed architecture superseded the original combined
`plugins/docx-to-content/` plugin, decommissioned in Phase 4.5 Wave 8 — see
`docs/superpowers/plans/phase-4-5-evidence/phase-4-5-exit-statement.md`.

**Current status and how to resume:** read `start-here.md` at the repo root — it is the
authoritative, kept-current resume document for this work (supersedes any stale in-conversation
summary). Phase 1 work happened directly on `main` (no worktree). Starting with Phase 2, each
phase works in its own branch/worktree, following the Per-Phase Git & Session Workflow section of
`docs/vision/master-initiative-plan-workstreams-and-phases.md` — branch/worktree per phase, commit
per task, push each completed task commit to `origin/<feature-branch>`, and merge into `main` only once the phase's exit gate evidence exists and human approval is given. Update `start-here.md` after merge, then start the next phase in a fresh session. Task execution within a phase follows
`superpowers:subagent-driven-development` (fresh implementer + fresh reviewer per task) or
`superpowers:executing-plans`, TDD throughout.

**Phase 4.5 (complete):** `plugins/docx-to-content/` was decomposed into 4 active domain plugins:
`source-document-extraction`, `document-structure-analysis`, `structured-content-assembly`, and
`structured-content-rendering` (`knowledge-templates` and `sharepoint-content-publication` remain deferred until
working capabilities exist) — see
`docs/superpowers/plans/phase-4-5-evidence/phase-4-5-exit-statement.md`.

### Layout

```
intake/                 ← source .docx files awaiting/pending conversion (read-only inputs)
runs/<doc-name>/         ← per-document-run output (staged and promoted, via the plugin CLI)
plugins/                ← the four domain conversion plugins — see Purpose above
docs/vision/             ← broader initiative direction (naming, phases, plugin/agent boundaries)
docs/superpowers/        ← plugin design specs, implementation plans, SDD ledgers
DEPENDENCIES.md          ← running log of required external tools (non-Python) and install commands
.agent/rules/            ← authoritative rule files (see below)
.agents/skills/          ← installed skills (from richfrem/agent-plugins-skills + obra/superpowers)
```

`intake/`/`runs/` are this repo's own working directories for the Phase 1 CEIS pilot — the plugin
itself takes `--source`/`--output` as arbitrary CLI arguments and has no hardcoded dependency on
either name. A later phase (per `docs/vision/`) may reorganize per-document work under
`examples/<name>/` alongside other pilot documents; that reorganization is not authorized by this
file alone and requires its own reviewed plan (see `docs/vision/README.md`'s change-control rules).

### Conversion workflow — via the plugin (current, authoritative)

Real document conversion runs through the four domain plugins' chained public interfaces
(`extract_and_normalize` → `recommend_from_normalized` → human confirmation →
`build_canonical_package` → `render`), not a bare `pandoc` invocation — see each plugin's
`skills/*/SKILL.md` for the exact commands, preconditions, and its own README for the
`pip install -e plugins/<name>` command. The bare-`pandoc` snippet that used to live in this
section predates the plugin architecture and is superseded. Two CEIS output directories exist side
by side, deliberately, as a record of this repo's own journey: `runs/ceis-manual/` is the original
pre-plugin, known-broken output (raw TOC dump, glued images, pandoc attribute artifacts — see
`JOURNAL.md`), kept as historical evidence of the problem the plugin was built to solve.
`runs/ceis-manual-v2/` is the real Task 18 cutover — the same source document converted through the
full `analyze`/`confirm`/`convert`/`render` pipeline, validated PASS at both the canonical and
rendered stages, and reproduced byte-identically through the four-plugin architecture at Phase 4.5
Wave 6 (see `docs/superpowers/plans/phase-4-5-evidence/wave-6-golden-master-manifest.json`). Do
not treat `runs/ceis-manual/` as current or authoritative; it is retained for comparison only.

- Legacy `.emf` images (older Word documents can contain these) do not render in browsers/GitHub/most markdown viewers. `source-document-extraction`'s cleanup step converts them to `.png` via LibreOffice (`soffice`) automatically — see `DEPENDENCIES.md`.
- Verification is built into the pipeline: `structured-content-assembly` validates the staged canonical package (content-loss/duplication, media references, structural-anchor completeness, etc.) before promoting it, and `structured-content-rendering` validates rendered output before promoting that — see those plugins' `validate_canonical.py`/`renderers/validate_rendered.py`.

### Dependencies

Non-Python system tools (pandoc, LibreOffice, Poppler, the `docx`/`pdf`/`xlsx` skills) are tracked
in `DEPENDENCIES.md` — update that file whenever a new external tool is introduced. Do not
`brew install` or otherwise install system tools without checking with the user first; installs
of this kind are outside the scope of `.agent/rules/dependency-management.md` (which governs
Python `.in`/`.txt` lockfiles only) and should be confirmed explicitly.

### Skills in use

Word↔Markdown conversion in this repo is built directly on **pandoc**, not a third-party docx
skill — the Anthropic `docx` skill was evaluated and removed (2026-07-25): its read path was a
bare, unpostprocessed `pandoc -t markdown` call that produced structurally broken output on a
real document (see `JOURNAL.md`), and its license prohibits building derivative works on it
anyway. The purpose-built replacement is the four domain plugins (see Purpose above) — built
directly in this repo, from scratch under TDD, not relocated from the sibling monorepo (an
earlier plan to build them there and pull them in was superseded; see the v3.1 Deviation Notice in
the plugin design spec for why). `pdf`/`xlsx` skills remain installed for future source formats
but are not yet used.

### Skill Development Protocol — authoring/updating skills for this repo

This repo is a **consumer** of skills; it has no `plugins/` source tree of its own. Any new or
updated skill (e.g. `pandoc-docx-convert`) is authored in the sibling monorepo
`/Users/richardfremmerlid/Projects/agent-plugins-skills` (source of truth, published to GitHub
and the Claude Code marketplace) and pulled into this repo's `.agents/skills/` once merged.

Every skill create/update in that repo follows its own rules — read them there before touching
anything, they are the authoritative versions (this repo's `.agent/rules/` copies describe the
same policies but govern *this* repo, not the monorepo):

1. **TDD first** (`agent-plugins-skills/.agent/rules/test-driven-development.md` /
   this repo's `test-driven-development.md`) — write a failing test/eval before any script code.
2. **Hub-and-spoke, no directory symlinks** (`plugin-architecture-policy.md`) — new scripts/
   references land at the plugin root (`plugins/<plugin>/scripts/`) first, then get symlinked
   into the skill folder via `symlink_manager.py` — never `ln -s` directly, never a real file
   copy living only inside the skill dir. Run `diagnose` before and after
   (`symlink-cross-platform.md`).
3. **No autonomous deletions** (`self-evolution-policy.md`) — deleting a file, skill, or rule
   always requires explicit user permission; this session's removal of the `docx` skill was
   explicitly approved, not assumed.
4. Commit the change on a **feature branch** in `agent-plugins-skills`, push, and open a PR.
5. **The user reviews and merges the PR into `main` themselves** — the agent does not merge.
6. Once merged, reinstall/refresh the skill here. Before the PR merges (or for fast local
   iteration), install directly from the local monorepo path rather than waiting on GitHub:
   ```bash
   python3 .agents/skills/plugin-installer/scripts/plugin_add.py \
     /Users/richardfremmerlid/Projects/agent-plugins-skills \
     --plugins <plugin-name> -y
   ```
   After merge, the same command against the now-updated local checkout keeps this repo in sync
   without waiting for a separate GitHub-sourced reinstall.

### Plugin-Local Resource Sharing (this repo's own `plugins/*`, the four Phase 4.5 domain plugins)

Unlike the marketplace skills described above, the Phase 4.5 domain plugins
(`plugins/source-document-extraction/`, `plugins/document-structure-analysis/`,
`plugins/structured-content-assembly/`, `plugins/structured-content-rendering/`) *are* authored directly in this
repo, and
their Python code lives in a **flat `plugins/<plugin>/scripts/` directory** (bare module names,
e.g. `scripts/extraction.py`, `scripts/dependencies.py` — no `src/<import_name>/` nesting layer;
group only cohesive multi-file families into a subfolder, e.g. `scripts/pandoc/`, `scripts/schema/`
— see `docs/superpowers/plans/phase-4-5-evidence/wave-2-flat-scripts-correction.md` for the full
rule, a worked example, and a real bare-name collision it fixes). This same hub-and-spoke
convention applies to non-Python shared resources: add references/assets once at the plugin root
(`plugins/<plugin>/references/`, `plugins/<plugin>/assets/`), then, only if/when a skill actually
needs one of them, create a file-level symlink into that skill's own folder
(`plugins/<plugin>/skills/<skill>/references/...`) via
`.agents/skills/symlink-manager/scripts/symlink_manager.py create --src ... --dst ...` — never
`ln -s` directly, never a hand-copy. Run `diagnose` after any symlink change to confirm zero
broken links/real-file imposters before committing (`.agent/rules/symlink-cross-platform.md`).
This applies to reference/asset files; a plugin's installable Python package itself is always a
real file, never symlinked (a symlink pointing outside a package's `scripts/` tree does not survive
a `pip`/`setuptools` wheel build).

### Active Rule Files

Full rule definitions live in `.agent/rules/` — these are the authoritative source, this file
carries only the key non-negotiables:

- `dependency-management.md` — pip-compile workflow for Python deps; does not cover system tools
- `coding-conventions.md` — file headers, naming, documentation conventions
- `self-evolution-policy.md` — no file deletions without explicit human permission; mandatory map-debt.md tracking for all friction/learnings
- `test-driven-development.md` — TDD approach where code is involved
- `symlink-cross-platform.md` — symlink protocol if shared scripts are introduced
- `github-issue-logging-policy.md` — issue logging conventions, if/when this repo tracks issues on GitHub


### Phase 4+ SharePoint Copilot Agent Configuration

**Critical Learning (2026-07-31):** SharePoint Copilot agents require exact resource identifiers. Common failure mode is pointing agents to wrong SharePoint resource (e.g., document library instead of SitePages subfolder). Always:

1. **Extract IDs from working manual agent first** — create agent via UI as reference, download .agent JSON, extract site_id, web_id, list_id, unique_id
2. **Use SitePages path correctly** — URL must include `/SitePages/FolderName`, not just `/FolderName`
3. **Never use zero unique_id for folders** — folders have real unique_id values; zeros only for list items
4. **Verify IDs before scripting** — site_id and web_id must be non-empty (from Get-PnPSite / Get-PnPWeb)
5. **Test ASPX-only agents** — to isolate retrieval issues from ranking issues, create agent with single ASPX source and no image fallback

See `docs/research/PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md` for full discovery path, verification checklist, and Phase 5+ recommendations.

## SUB-agent usage
Use the cheapest models possible where possible.  If the job doesn't require spawning sub-agents don't do so.


### Scratch Output

Write temporary files and intermediate analysis output to a `temp/` directory — never to the
project root directly. Final conversion outputs belong under `runs/<doc-name>/`.
