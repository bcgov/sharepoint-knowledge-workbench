# Architecture Overview

This is a proof-of-concept repo, not a running application — there is no frontend, backend,
database, or deployed service. It exists to validate the "content-centric knowledge management"
proposal in `plan.md`: pulling content out of Word documents (where content and formatting are
baked together) into structured Markdown, so content, presentation templates, and rendering can
be managed as three separate layers instead of one document. The CEIS Manual is the pilot
document. Update this file as the repo's actual shape changes — don't let it drift into
describing a system that isn't here.

## 1. Project Structure

```
manual-conversion-poc/
├── sourcedocuments/        # Original .docx source files (read-only inputs, never edited)
│   └── CEIS MANUAL - working version.docx   # pilot document from plan.md
├── output/                 # Conversion output, one directory per source document
│   └── ceis-manual/
│       ├── CEIS-Manual.md  # pandoc-converted, cleaned-up markdown
│       └── images/media/   # images extracted from the .docx, referenced by the markdown
├── plan.md                 # the executive proposal this POC is validating
├── architecture.md         # this file
├── JOURNAL.md              # chronological, learning-oriented log of the conversion process —
│                           #   what was tried, what broke, what fixed it, decisions made and why
├── DEPENDENCIES.md         # running log of required external CLI tools (pandoc, LibreOffice) —
│                           #   not Python packages, which this repo doesn't have any of
├── CLAUDE.md                # behavioral guidelines + this repo's actual conventions
├── plugin-sources.json      # which upstream skill sources are tracked (see §3)
├── skills-lock.json          # machine-generated install record for .agents/skills/ — never hand-edit
├── .agent/rules/            # authoritative rule files (dependency management, git ops, TDD, etc.)
└── .agents/skills/           # installed skills — see §3, this repo has no plugins/ source tree of
                              #   its own; everything here is a pulled-in copy
```

There is no `src/`, `backend/`, `frontend/`, `tests/`, or `Dockerfile` in this repo — none of that
applies. If this repo ever grows an actual conversion tool of its own (as opposed to consuming one
built elsewhere — see §3), that structure should be added deliberately at that point, not
scaffolded speculatively now.

## 2. High-Level Flow

This repo has one real data flow: a source Word document goes in, a cleaned-up Markdown document
(with images) comes out. There is no live system, no request/response cycle, no database.

```
sourcedocuments/<doc>.docx
        |
        v  pandoc (+ cleanup pipeline, once pandoc-docx-convert ships — see §3)
        |
output/<doc>/<Doc>.md  +  output/<doc>/images/media/*.png
```

The reverse direction (Markdown → `.docx`, rendering content back out through a style template)
is part of `plan.md`'s Content + Template = Published Output model but is not yet exercised in
this repo — it's in scope for the `pandoc-docx-convert` skill (see §3) but no `output/` artifact
has been produced that way yet.

## 3. Skills — this repo is a consumer, not a source

This repo has **no `plugins/` source tree**. It only *consumes* skills installed into
`.agents/skills/`, tracked in `plugin-sources.json` and `skills-lock.json`. The actual source of
truth for any skill used here is the sibling monorepo
`/Users/richardfremmerlid/Projects/agent-plugins-skills`, published to GitHub and the Claude Code
marketplace.

**Currently installed sources** (`plugin-sources.json`):
- `obra/superpowers` → the `superpowers` plugin (brainstorming, writing-plans, TDD, etc.)
- `richfrem/agent-plugins-skills` → `agent-agentic-os`, `agent-scaffolders`, `cli-agents`,
  `dependency-management`, `dev-utils`

**Removed:** the Anthropic `docx` skill (2026-07-25) — its `.docx`→Markdown path was a bare
`pandoc -t markdown` call with no cleanup, and its license prohibits building derivative works on
it. See `JOURNAL.md`'s 2026-07-25 Session 2 entry for the full reasoning.

**In progress:** `pandoc-docx-convert`, a new skill being authored in
`agent-plugins-skills/plugins/dev-utils/skills/pandoc-docx-convert/` (design spec:
`agent-plugins-skills/docs/superpowers/specs/2026-07-25-pandoc-docx-convert-design.md`;
implementation plan: `agent-plugins-skills/docs/superpowers/plans/2026-07-25-pandoc-docx-convert.md`).
It replaces the removed `docx` skill's read path with an independently-authored, pandoc-based
bidirectional converter, plus hard structural validation. It is built on a feature branch there,
reviewed via PR, and merged by the user — never by an agent. See `CLAUDE.md`'s "Skill Development
Protocol" section for the full cross-repo workflow, including how to reinstall it here once merged.

## 4. Dependencies

Tracked in `DEPENDENCIES.md` — all external CLI tools, not Python packages (this repo has no
Python code of its own):
- **pandoc** — the actual conversion engine
- **LibreOffice (`soffice`)** — converts legacy `.emf`/`.wmf` embedded images to `.png`

Do not install or upgrade system-level tools without checking with the user first — this is
outside the scope of `.agent/rules/dependency-management.md` (which governs Python `.in`/`.txt`
lockfiles only, used in the *sibling* `agent-plugins-skills` repo, not here).

## 5. What This Repo Deliberately Does Not Have

- No running service, no API, no database — nothing to deploy, monitor, or authenticate against.
- No CI/CD pipeline.
- No test suite of its own — any code (fix scripts, validation logic) for document conversion
  lives in the `pandoc-docx-convert` skill in `agent-plugins-skills`, tested there under that
  repo's TDD conventions, not duplicated here.
- No `plugins/` source tree — see §3.

## 6. Roadmap / Open Questions

- `pandoc-docx-convert` is mid-implementation (see §3). Once merged and reinstalled here, the CEIS
  Manual should be re-converted through it, replacing the ad-hoc script output currently sitting
  in `output/ceis-manual/`.
- `plan.md`'s "Layer 2: Templates" and "Layer 3: Rendering" — a style template `.docx` and a
  markdown→docx render pass — are designed for (`md_to_docx.py` in the plan above) but not yet
  exercised against a real template for this specific document.
- Whether `pandoc-docx-convert` stays a single skill or eventually splits (e.g. read vs. write
  direction) is explicitly left open — see `JOURNAL.md`, 2026-07-25 Session 2, §5.

## 7. Project Identification

Project Name: manual-conversion-poc

Repository: local only, no remote configured (not a git repository as of 2026-07-25)

Primary Contact: Richard Fremmerlid

Date of Last Update: 2026-07-25
