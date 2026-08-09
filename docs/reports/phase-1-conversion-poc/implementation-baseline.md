# docx-to-content Phase 1 — Implementation Baseline (Task 0)

**Date:** 2026-07-25
**Status:** Reconnaissance complete — one blocking finding recorded and resolved by explicit user decision below.

## Verified tool versions

```text
pandoc 3.8.3 (+server +lua)
LibreOffice 26.2.5.2 (soffice)
Python 3.13.4
pytest available at /Library/Frameworks/Python.framework/Versions/3.13/bin/pytest
```

## Verified source paths

- CEIS source docx: `sourcedocuments/CEIS MANUAL - working version.docx`
- Existing unfixed output to preserve until cutover: `output/ceis-manual/CEIS-Manual.md`

## Plugin scaffold convention

No plugin scaffold (`.claude-plugin/plugin.json`, `plugin.yaml`) exists anywhere in
`manual-conversion-poc`. This repo has never authored a plugin of its own — `.agents/skills/`
contains only installed, consumed marketplace skills, not a local scaffold to copy conventions
from.

The sibling monorepo `agent-plugins-skills` does contain scaffolded plugins under `plugins/`
(e.g. `dev-utils`, `exploration-cycle-plugin`, `spec-kitty-plugin`) that may be used as a
**structural reference only** for `.claude-plugin/plugin.json` / `plugin.yaml` / `skills/<skill>/SKILL.md`
layout conventions.

## BLOCKING FINDING (resolved): cleanup pipeline code does not exist

Both the v1 spec and the v3 spec/plan describe `pandoc_fixes/{attrs,images,toc,tables,footnotes}.py`,
`emf_convert.py`, `pandoc_validate.py`, `docx_to_md.py`, `md_to_docx.py`, and their tests as
**already-built, working, tested code** from "the paused `agent-plugins-skills` work," to be
relocated into the new plugin without redesign (v3 Non-Negotiable Rule 11, v3 Task 2).

Reconnaissance searched:
- `manual-conversion-poc` (this repo) — not found, including full git history (`git log --all
  --diff-filter=A --name-only`).
- `agent-plugins-skills` (sibling monorepo) — not found in the working tree, not found across
  every local branch and every `origin/*` remote branch (`git branch -a`), not found across all
  git history on any ref, and not found in any of the 5 stashes present in that repo.
- `manual-conversion-poc/JOURNAL.md` references a design spec at
  `agent-plugins-skills/docs/superpowers/specs/2026-07-25-pandoc-docx-convert-design.md` for a
  planned `pandoc-docx-convert` skill, and states its own "Next" step as "implementation plan for
  `pandoc-docx-convert`, via `writing-plans`" — i.e. even that spec's own journal entry shows only
  a spec was reached, not an implementation plan or code. Checked directly: that spec file does
  not exist in `agent-plugins-skills` either (not in the working tree, not in git history).
- The only `md_to_docx.py` found anywhere in `agent-plugins-skills` belongs to a **different,
  unrelated** existing skill, `plugins/markdown-to-msword-converter/`, which converts markdown to
  Word documents for a different purpose — not the docx-to-content cleanup pipeline described in
  either spec.

**Resolution (explicit user decision, 2026-07-25, after this deeper check was requested and
run):** this code was never actually built, anywhere. The "already-built, paused work" framing in
both specs was aspirational — carried forward from an earlier planning conversation that reached
a design spec and stopped, not a description of real committed code.

**Consequence:** v3 Task 2 ("Relocate Cleanup Code With Provenance Guard") is invalid as written.
There is nothing to relocate. This must be redefined as new engineering work — building the
cleanup pipeline from scratch under TDD, using the four documented pandoc defect categories
(raw Word TOC dump, images glued to headings/list items, leftover pandoc attribute syntax,
legacy `.emf`/`.wmf` images) as the design target, not as a diff against existing code.

Per `.agent/rules/test-driven-development.md` and v3's own "no fabricated relocation" gate, this
finding is documented here rather than silently building placeholder code under a "relocation"
label. See the v3 spec and plan amendment notes for the resulting task/rule changes.

## Gate outcome

Task 0 gate ("stop if any required source module or test cannot be found") is satisfied: the
finding was surfaced, and the user has made an explicit call (build from scratch) rather than
having code fabricated silently. Proceeding to amend the v3 spec/plan accordingly before Task 1.
