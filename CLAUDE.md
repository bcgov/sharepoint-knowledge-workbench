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

This is a proof-of-concept for the "content-centric knowledge management" proposal in `plan.md`:
moving Word/PDF manuals from a document-centric model (content + formatting baked together) to a
content-centric model (Content + Template + Renderer = Published Output). The **CEIS Manual** is
the pilot document (`plan.md`, "Pilot Candidate" section).

Concretely, this repo currently does one thing: **convert source Word documents into structured
Markdown**, preserving structure (headings) and inline image references, as a first step toward
that content-centric model.

### Layout

```
sourcedocuments/        ← original .docx source files (read-only inputs)
output/<doc-name>/      ← conversion output per source document
  <Doc-Name>.md         ← pandoc-converted markdown
  images/media/         ← images extracted from the .docx, referenced by the markdown
plan.md                 ← the executive proposal this POC is validating
DEPENDENCIES.md         ← running log of required external tools (non-Python) and install commands
.agent/rules/           ← authoritative rule files (see below)
.agents/skills/         ← installed skills (from richfrem/agent-plugins-skills + obra/superpowers)
```

### Conversion workflow (current pattern — follow for new source documents)

```bash
mkdir -p output/<doc-name>/images
pandoc -t markdown --extract-media=output/<doc-name>/images --wrap=none \
  "sourcedocuments/<source>.docx" -o output/<doc-name>/<Doc-Name>.md
```

- `--extract-media` pulls embedded images out and rewrites the markdown links to point at them in place — this is what keeps images positioned where they appear in the original document.
- Legacy `.emf` images (older Word documents can contain these) do not render in browsers/GitHub/most markdown viewers. They require LibreOffice (`soffice`) to convert to `.png` — see `DEPENDENCIES.md`. Check for `.emf` files after every conversion:
  ```bash
  find output/<doc-name>/images -iname '*.emf'
  ```
- After converting, verify: check image link count matches extracted file count, and skim heading structure (`grep '^#'`) against the source document's TOC/section list.

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
anyway. A purpose-built replacement (`pandoc-docx-convert`) is being authored in the source
monorepo — see the protocol below. `pdf`/`xlsx` skills remain installed for future source formats
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

### Active Rule Files

Full rule definitions live in `.agent/rules/` — these are the authoritative source, this file
carries only the key non-negotiables:

- `dependency-management.md` — pip-compile workflow for Python deps; does not cover system tools
- `coding-conventions.md` — file headers, naming, documentation conventions
- `self-evolution-policy.md` — no file deletions without explicit user permission
- `test-driven-development.md` — TDD approach where code is involved
- `symlink-cross-platform.md` — symlink protocol if shared scripts are introduced
- `github-issue-logging-policy.md` — issue logging conventions, if/when this repo tracks issues on GitHub


## SUB-agent usage
Use the cheapest models possible where possible.  If the job doesn't require spawning sub-agents don't do so.


### Scratch Output

Write temporary files and intermediate analysis output to a `temp/` directory — never to the
project root directly. Final conversion outputs belong under `output/<doc-name>/`.
