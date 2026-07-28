# Architecture Overview

This is a proof-of-concept repo, not a running application — there is no frontend, backend,
database, or deployed service. It is **Phase 1** ("Structured Knowledge Conversion and Canonical
Content POC") of a broader initiative, the **AI-Assisted Structured Knowledge Workbench**: pulling
content out of Word documents (where content and formatting are baked together) into structured,
canonical content that can be rendered into many outputs and eventually ground knowledge-access
agents. The **CEIS Manual** is the Phase 1 pilot document. Phase 1's scope is deliberately narrow
— the full initiative's direction (repository/plugin boundaries beyond Phase 1, SharePoint
delivery, native skills, agents, publication, evaluation) is described in `docs/vision/`, not here.
Update this file as the repo's actual shape changes — don't let it drift into describing a system
that isn't here.

## 1. Project Structure

```
manual-conversion-poc/
├── intake/                  # Source .docx files awaiting/pending conversion (read-only inputs)
│   └── CEIS MANUAL - working version.docx   # Phase 1 pilot document
├── runs/                    # Per-document-run conversion output
│   └── ceis-manual/
│       ├── CEIS-Manual.md   # pre-plugin, known-broken first-pass conversion — see §3
│       └── images/media/    # images extracted from the .docx, referenced by that markdown
├── plugins/
│   └── docx-to-content/     # the self-contained conversion plugin — see §3
├── docs/
│   ├── vision/               # broader-initiative direction: naming, phases, plugin/agent
│   │                          #   boundaries, open questions — see docs/vision/README.md
│   ├── research/              # product research / field notes feeding the broader vision
│   └── superpowers/
│       ├── specs/             # design specs (brainstorming skill output)
│       └── plans/             # implementation plans (writing-plans skill output)
├── architecture.md           # this file
├── JOURNAL.md                # chronological, learning-oriented log — what was tried, what broke,
│                              #   what fixed it, decisions made and why (including reversed ones)
├── start-here.md             # authoritative, kept-current resume document for Phase 1 work
├── DEPENDENCIES.md           # running log of required external CLI tools (pandoc, LibreOffice)
├── CLAUDE.md                 # behavioral guidelines + this repo's actual conventions
├── .gitignore                # excludes .agents/, .claude/, context/ (regenerable/session-local)
├── plugin-sources.json       # which upstream skill sources are tracked (see §3)
├── skills-lock.json          # machine-generated install record for .agents/skills/ — never hand-edit
├── .agent/rules/             # authoritative rule files (dependency management, git ops, TDD, etc.)
└── .agents/skills/           # installed skills (superpowers, agent-scaffolders, dev-utils, etc.) —
                               #   gitignored, reproducible from plugin-sources.json
```

`intake/`/`runs/` are Phase 1's own working directories; the plugin itself takes `--source`/
`--output` as arbitrary CLI arguments with no hardcoded dependency on either name. A later phase
(per `docs/vision/`) may reorganize per-document work under `examples/<name>/` alongside other
pilot documents — not authorized by this file alone, requires its own reviewed plan.

This repo **is** a git repository, pushed to `github.com/richfrem/manual-conversion-poc` (`main`
is the default branch).

There is no `src/`, `backend/`, `frontend/`, or `Dockerfile` — none of that applies.

## 2. High-Level Flow (Phase 1)

Still no live system, no request/response cycle, no database. The flow is a multi-stage,
CLI-driven pipeline, gated by explicit human plan confirmation between analysis and conversion:

```
intake/<doc>.docx
        |
        v  analyze-document skill: real pandoc extraction, structural analysis
        |     (headings, defect signals, statistics, proposed_topics preview),
        |     writes a DRAFT ConversionPlan
        |
Draft ConversionPlan  ── requires explicit human confirmation before proceeding
        |
        v  convert-document skill: confirm (draft -> confirmed) then convert
        |     (pandoc + cleanup pipeline -> structural-anchor reconciliation/chunking
        |      -> canonical package build -> validate_canonical.py -> atomic promotion)
        |
Canonical Content Package (manifest.json, validated chunks + sidecars, media/,
publication-map.json for the "grouped" strategy)
        |
        v  render-content skill: CanonicalPackage.load() -> a registered renderer
        |     (currently multipage-markdown) -> renderers/validate_rendered.py -> atomic promotion
        |
Published Output (a navigable folder of pages + index)
```

Three chunking strategies are supported end to end: `"single"`, `"chunked"` (one canonical chunk
per heading), and `"grouped"` (headings folded into ~topic-sized files, with per-heading identity
preserved as sidecar metadata and ordering driven by `publication-map.json`) — see
`docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design-v3-ammendments.md` and
`docs/superpowers/plans/2026-07-28-docx-to-content-topic-grouping.md`.

## 3. Plugin — self-contained in this repo, not the sibling monorepo

Word-conversion work is authored directly in this repo's `plugins/docx-to-content/`, built from
scratch under TDD, not relocated from the sibling monorepo `agent-plugins-skills` (an earlier plan
to build it there and pull it in was superseded — see the v3.1 Deviation Notice in the plugin
design spec). This repo's actual purpose is to demonstrate the concept end-to-end, including the
plugin itself, not just consume one built elsewhere.

`plugins/docx-to-content/` uses the same structural conventions as `agent-plugins-skills`
(`.claude-plugin/plugin.json`, `plugin.yaml`, `skills/<skill>/SKILL.md`, hub-and-spoke `scripts/`)
but is authored, tested, and lives only in this repo. No PR/merge/reinstall cycle applies to it
(that protocol, documented in `CLAUDE.md`, governs the *installed* skills in `.agents/skills/`,
sourced from the sibling monorepo — a separate concern from this first-party plugin).

**Three skills, fully implemented** (design: `docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design-v3-ammendments.md`):
- `analyze-document` — real pandoc extraction, structural analysis, defect-signal detection,
  proposed-topic preview, draft `ConversionPlan` — never converts content, never writes canonical
  output.
- `convert-document` — `confirm` (draft → confirmed plan) then `convert` (cleanup pipeline →
  chunking → canonical package build → `validate_canonical.py` → atomic promotion, only if
  validation allows it).
- `render-content` — `CanonicalPackage.load()` (full re-validation) → a registered renderer
  (`renderers/multipage_markdown.py`) → `renderers/validate_rendered.py` → atomic promotion.

**Installed skills remain a separate concern:** `.agents/skills/` (superpowers, agent-scaffolders,
cli-agents, dependency-management, dev-utils) are consumed from `agent-plugins-skills` and
`obra/superpowers` via `plugin-sources.json`/`skills-lock.json`, gitignored, reproducible via the
protocol in `CLAUDE.md`. The Anthropic `docx` skill was removed from this set (2026-07-25) — its
`.docx`→Markdown path was a bare `pandoc -t markdown` call with no cleanup, and its license
prohibits building derivative works on it. See `JOURNAL.md`, 2026-07-25 Session 2.

## 4. Dependencies

Tracked in `DEPENDENCIES.md` — external CLI tools (pandoc, LibreOffice/`soffice`), not Python
packages: do not install/upgrade system tools without checking with the user first, outside the
scope of `.agent/rules/dependency-management.md` (Python `.in`/`.txt` lockfiles only).

## 5. What This Repo Deliberately Does Not Have (Phase 1 scope)

- No running service, no API, no database, no CI/CD pipeline.
- No preview/editing tool for content — SharePoint Online already provides native markdown
  preview/editing at the eventual destination.
- No actual publish step into SharePoint/OneDrive — that and native SharePoint skills,
  publication-map-driven multi-target rendering, and knowledge-access agents are later-phase
  concerns described in `docs/vision/`, not built or authorized here.
- No renderers beyond `multipage_markdown.py` — see
  `plugins/docx-to-content/references/future-output-profiles.md` for the surveyed-but-not-built
  candidates (PDF, Word, PowerPoint, HTML, SharePoint, etc.).

## 6. Roadmap / Open Questions

- **Immediate (Phase 1, in progress):** Task 18 — cut over the real CEIS Manual through the
  finished plugin, replacing `runs/ceis-manual/CEIS-Manual.md` (known-broken pre-plugin output).
  Gated on explicit human confirmation of the proposed topic-grouping plan — see `start-here.md`
  for exact status.
- **Beyond Phase 1:** the phased roadmap (Phase 2 — publication/renderer separation, Phase 3 —
  governed SharePoint knowledge pilot, Phase 4 — native SharePoint skills, Phase 5 — SharePoint
  knowledge agent, Phase 6 — multi-target capability model, Phase 7 — Cowork/Copilot Studio
  evaluation, Phase 8 — scale/operations), proposed plugin boundaries (`sharepoint-knowledge`,
  `knowledge-publication`, `knowledge-evaluation`), and repository rename/restructure options are
  described in `docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md`. That
  document proposes future direction; it does not itself authorize renaming the repository, moving
  files beyond what's already been agreed, or scaffolding new plugins — each requires its own
  reviewed decision.
- Open architecture/governance questions (knowledge-unit boundaries, publication-map reuse,
  metadata authority, security boundaries, stable identity, and more) are tracked in
  `docs/vision/key-unanswered-questions.md`.

## 7. Project Identification

Project Name: manual-conversion-poc

Repository: `github.com/richfrem/manual-conversion-poc`, `main` branch (default, pushed)

Primary Contact: Richard Fremmerlid

Date of Last Update: 2026-07-28
