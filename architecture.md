# Architecture Overview

This is a proof-of-concept repo, not a running application — there is no frontend, backend,
database, or deployed service. It exists to validate the content-centric knowledge management
vision in `vision.md` (which merges `plan.md` and `plan-part2.md`): pulling content out of Word
documents (where content and formatting are baked together) into structured, template-mapped
content that can be rendered into many outputs — and eventually ground a Copilot Studio/M365
agent. The CEIS Manual is the pilot document. Update this file as the repo's actual shape
changes — don't let it drift into describing a system that isn't here.

## 1. Project Structure

```
manual-conversion-poc/
├── sourcedocuments/        # Original .docx source files (read-only inputs, never edited)
│   └── CEIS MANUAL - working version.docx   # pilot document
├── output/                 # Conversion output, one directory per source document
│   └── ceis-manual/
│       ├── CEIS-Manual.md  # first-pass pandoc conversion (pre-plugin, known-broken — see §3)
│       └── images/media/   # images extracted from the .docx, referenced by the markdown
├── plugins/                # Self-contained plugin source tree — see §3. NOT installed skills;
│   └── docx-to-content/    #   this is authored directly in this repo, not the sibling monorepo.
├── plan.md                 # original executive proposal (content-centric model)
├── plan-part2.md           # follow-on proposal (Copilot Studio/M365 agent knowledge access)
├── vision.md                # merges plan.md + plan-part2.md into one vision, maps to the
│                            #   workflow diagram (see docs/superpowers/specs/diagrams/)
├── docs/superpowers/
│   ├── specs/               # design specs (brainstorming skill output)
│   │   ├── 2026-07-25-docx-to-content-plugin-design.md   # current, authoritative
│   │   └── diagrams/docx-to-content-workflow.{mmd,png}    # the workflow diagram
│   └── plans/                # implementation plans (writing-plans skill output)
├── architecture.md          # this file
├── JOURNAL.md               # chronological, learning-oriented log — what was tried, what broke,
│                            #   what fixed it, decisions made and why (including reversed ones)
├── DEPENDENCIES.md          # running log of required external CLI tools (pandoc, LibreOffice)
├── CLAUDE.md                 # behavioral guidelines + this repo's actual conventions
├── .gitignore                # excludes .agents/, .claude/, context/ (regenerable/session-local)
├── plugin-sources.json       # which upstream skill sources are tracked (see §3)
├── skills-lock.json           # machine-generated install record for .agents/skills/ — never hand-edit
├── .agent/rules/             # authoritative rule files (dependency management, git ops, TDD, etc.)
└── .agents/skills/            # installed skills (superpowers, agent-scaffolders, dev-utils, etc.) —
                               #   gitignored, reproducible from plugin-sources.json
```

This repo **is** a git repository (initialized 2026-07-25, remote `github.com/richfrem/
manual-conversion-poc`, not yet pushed) — that has changed since this file was first written.

There is no `src/`, `backend/`, `frontend/`, or `Dockerfile` — none of that applies. `plugins/` is
new structure, added deliberately for the reason in §3, not scaffolded speculatively.

## 2. High-Level Flow

Still no live system, no request/response cycle, no database. But the flow is now a multi-stage
pipeline, not a single conversion — see `docs/superpowers/specs/diagrams/docx-to-content-workflow.png`
for the full picture. Summarized:

```
sourcedocuments/<doc>.docx
        |
        v  pandoc + cleanup pipeline (analyze-document / convert-document skills)
        |
Raw extracted markdown  ── TRANSITORY, not the content artifact itself
        |
        v  analysis maps raw sections onto a content template's defined slots
        |
Canonical Content + Metadata (chunk_id, source_heading_path, topic)
        |
        v  render-content skill, base.py contract
        |
Published Output (Phase 1: multipage_markdown.py — a navigable folder of pages + index)
```

Later phases (not built, named in the design spec): other renderers sharing the same contract
(Word/PDF, PowerPoint, audio scripts), a destination-interview skill, an actual publish step into
SharePoint/OneDrive, and using the canonical Content (not the raw extraction) to ground a Copilot
Studio/M365 agent per `plan-part2.md`.

## 3. Plugin — self-contained in this repo, not the sibling monorepo

**This is a reversal of an earlier decision, worth stating explicitly so it isn't rediscovered by
surprise:** work on a Word-conversion skill was originally started in the sibling monorepo
`/Users/richardfremmerlid/Projects/agent-plugins-skills` (source of truth for that repo's
published, shared plugins). That work — a design spec, implementation plan, and working
`pandoc_fixes/*` cleanup modules — was deliberately relocated here per explicit instruction: this
repo's actual purpose is to demonstrate the concept end-to-end, including the plugin itself, not
just consume one built elsewhere. The sibling repo was fully cleaned up (all uncommitted additions
removed, `symlinks.json` reverted) before the move.

`plugins/docx-to-content/` is scaffolded using the same structural conventions as
`agent-plugins-skills` (`.claude-plugin/plugin.json`, `plugin.yaml`, `skills/<skill>/SKILL.md`,
hub-and-spoke `scripts/` via file-level symlinks) — but it is authored, tested, and lives only in
this repo. No PR/merge/reinstall cycle applies to it (that protocol, still documented in
`CLAUDE.md`, governs the *installed* skills in `.agents/skills/`, which remain sourced from the
sibling monorepo — this plugin is a separate, first-party thing this repo builds directly).

**Three skills, Phase 1** (design: `docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design.md`):
- `analyze-document` — structural analysis + chunking/template recommendation, user confirms/overrides
- `convert-document` — executes the confirmed plan; relocated `pandoc_fixes/*`, `emf_convert.py`,
  `pandoc_validate.py` do the actual cleanup (attrs → images → toc → tables → footnotes, corrected
  order — see the spec for why that order matters)
- `render-content` — the render contract (`renderers/base.py`) plus one concrete proof renderer
  (`renderers/multipage_markdown.py`)

**Installed skills remain a separate concern:** `.agents/skills/` (superpowers, agent-scaffolders,
cli-agents, dependency-management, dev-utils) are still consumed from `agent-plugins-skills` and
`obra/superpowers` via `plugin-sources.json`/`skills-lock.json`, gitignored, reproducible via the
protocol in `CLAUDE.md`. The Anthropic `docx` skill was removed from this set (2026-07-25) — its
`.docx`→Markdown path was a bare `pandoc -t markdown` call with no cleanup, and its license
prohibits building derivative works on it. See `JOURNAL.md`, 2026-07-25 Session 2.

## 4. Dependencies

Tracked in `DEPENDENCIES.md` — external CLI tools (pandoc, LibreOffice/`soffice`), not Python
packages, for the same reason as before: do not install/upgrade system tools without checking with
the user first, outside the scope of `.agent/rules/dependency-management.md` (Python `.in`/`.txt`
lockfiles only). The plugin's own Python dependencies (pytest, test-only) follow that rule and are
tracked in `plugins/docx-to-content/requirements.in`/`.txt` once scaffolded.

## 5. What This Repo Deliberately Does Not Have (updated)

- No running service, no API, no database.
- No CI/CD pipeline.
- No preview/editing tool for content — SharePoint Online already provides native markdown
  preview/editing at the eventual destination (confirmed via a live screenshot); building one here
  would be redundant.
- No destination-interview skill, no actual publish step into SharePoint/OneDrive yet — the
  `manual-conversion-poc` folder visible in SharePoint/OneDrive today is a manually-created
  separate copy, not synced to this repo.
- No renderers beyond the one (`multipage_markdown.py`) built to prove the render contract.

## 6. Roadmap / Open Questions

- Scaffold `plugins/docx-to-content/` via `create-plugin`, relocate the proven `pandoc_fixes/*`
  code into it, and implement `analyze-document`, `convert-document`, `render-content` per the
  design spec and its (not-yet-written) implementation plan.
- Re-convert the CEIS Manual through the finished plugin, replacing the current
  `output/ceis-manual/CEIS-Manual.md` (known-broken: raw TOC dump, glued images, pandoc attribute
  artifacts — see `JOURNAL.md`).
- Later phases, explicitly deferred and named in the design spec: other renderers (Word/PDF,
  PowerPoint, audio), destination-interview skill, actual SharePoint/OneDrive publish step, and
  using canonical Content+Metadata to ground a Copilot Studio/M365 agent (`plan-part2.md`).
- Whether/when to push this repo's initial commits to `github.com/richfrem/manual-conversion-poc`
  is still open — confirm with the user before any push (per general practice, not yet done).

## 7. Project Identification

Project Name: manual-conversion-poc

Repository: git-initialized locally (`main` branch), remote `github.com/richfrem/
manual-conversion-poc` configured but not yet pushed

Primary Contact: Richard Fremmerlid

Date of Last Update: 2026-07-25
