# Architecture Overview

This is a proof-of-concept repo, not a running application — there is no frontend, backend,
database, or deployed service. It is **Phase 1** ("Structured Knowledge Conversion and Canonical
Content POC") of a broader initiative, the **AI-Assisted Structured Knowledge Workbench**: pulling
content out of Word documents (where content and formatting are baked together) into structured
content that can be rendered into many outputs and eventually ground knowledge-access agents. The
**CEIS Manual** is the Phase 1 pilot document. Phase 1's scope is deliberately narrow — the full
initiative's direction (repository/plugin boundaries beyond Phase 1, SharePoint delivery, native
skills, agents, publication, evaluation) is described in `docs/vision/`, not here. Update this file
as the repo's actual shape changes — don't let it drift into describing a system that isn't here.

**Phase 4.5 is complete** (2026-08-02): the original combined `docx-to-content` plugin has been
decomposed into four independently-installable domain plugins (§3 below), each installing and
running standalone with zero editable-source duplication between them. See `start-here.md` for
current branch/merge status.

## 1. Project Structure

```
sharepoint-knowledge-workbench/
├── intake/                  # Source .docx files awaiting/pending conversion (read-only inputs)
│   └── CEIS MANUAL - working version.docx   # Phase 1 pilot document
├── runs/                    # Per-document-run conversion output
│   ├── ceis-manual/          # pre-plugin, known-broken first-pass conversion — retained as
│   │                          #   historical evidence only, not authoritative — see §3
│   └── ceis-manual-v2/       # the real, plugin-produced, validated PASS output — canonical-content/,
│                              #   render/rendered-output/, evidence-report.md — current & authoritative
├── plugins/                  # four independently-installable domain plugins (Phase 4.5) — see §3
│   ├── source-document-extraction/
│   ├── document-structure-analysis/
│   ├── structured-content-assembly/
│   └── structured-content-rendering/
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

This repo **is** a git repository, pushed to `github.com/richfrem/sharepoint-knowledge-workbench`
(`main` is the default branch).

There is no `src/`, `backend/`, `frontend/`, or `Dockerfile` — none of that applies.

## 2. High-Level Flow (Phase 1, now running through the four Phase 4.5 domain plugins)

Still no live system, no request/response cycle, no database. The flow is a multi-stage,
CLI-driven pipeline, gated by explicit human plan confirmation between analysis and conversion,
chained across the four domain plugins' real public interfaces (see §3):

```
intake/<doc>.docx
        |
        v  source-document-extraction: extract_and_normalize()
        |     real pandoc extraction, structural analysis, defect-signal detection
        |     -> normalized-source-document
        |
        v  document-structure-analysis: recommend_from_normalized()
        |     topic-boundary reasoning, chunking-strategy recommendation
        |     -> DRAFT ConversionPlan (analysis-plan)
        |
Draft ConversionPlan  ── requires explicit human confirmation before proceeding
        |
        v  structured-content-assembly: build_canonical_package()
        |     cleanup pipeline -> structural-anchor reconciliation/chunking
        |     -> package build -> validate_canonical.py -> atomic promotion
        |
Structured Content Package (manifest.json, validated chunks + sidecars, media/,
publication-map.json for the "grouped" strategy)
        |
        v  structured-content-rendering: render()
        |     CanonicalPackage.load() (full re-validation) -> a registered renderer
        |     (currently multipage-markdown) -> renderers/validate_rendered.py -> atomic promotion
        |
Published Output (navigable human-facing pages/ASPX + token-dense agent-optimized digests)
```

Three chunking strategies are supported end to end: `"single"`, `"chunked"` (one chunk per
heading), and `"grouped"` (headings folded into ~topic-sized files, with per-heading identity
preserved as sidecar metadata and ordering driven by `publication-map.json`) — see
`docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design-v3-ammendments.md` and
`docs/superpowers/plans/2026-07-28-docx-to-content-topic-grouping.md`.

## 3. Plugins — self-contained in this repo, not the sibling monorepo

Word-conversion work is authored directly in this repo, built from scratch under TDD, not
relocated from the sibling monorepo `agent-plugins-skills` (an earlier plan to build it there and
pull it in was superseded — see the v3.1 Deviation Notice in the plugin design spec). This repo's
actual purpose is to demonstrate the concept end-to-end, including the plugins themselves, not
just consume ones built elsewhere.

Originally built as one combined plugin (`docx-to-content`), Phase 4.5 decomposed it into four
independently-installable domain plugins, each installing and running standalone (`pip install -e
plugins/<name>`, zero dependency on any other workbench distribution) — see
`docs/architecture/phase-4-5-target-architecture.md` for the full distribution graph and
`docs/superpowers/plans/phase-4-5-evidence/phase-4-5-exit-statement.md` for the exit record. Each
uses the same structural conventions as `agent-plugins-skills` (`.claude-plugin/plugin.json`,
`plugin.yaml`, `skills/<skill>/SKILL.md`, hub-and-spoke `scripts/`) but is authored, tested, and
lives only in this repo. No PR/merge/reinstall cycle applies to them (that protocol, documented in
`CLAUDE.md`, governs the *installed* skills in `.agents/skills/`, sourced from the sibling
monorepo — a separate concern from these first-party plugins).

**Four plugins, chained via their real public interfaces:**
- `source-document-extraction` — real pandoc extraction, structural analysis, defect-signal
  detection, produces `normalized-source-document`.
- `document-structure-analysis` — topic-boundary reasoning, chunking-strategy recommendation, produces a
  draft `ConversionPlan` (`analysis-plan`) — requires explicit human confirmation before
  proceeding.
- `structured-content-assembly` — cleanup pipeline → chunking → canonical package build →
  `validate_canonical.py` → atomic promotion, only if validation allows it; produces
  `canonical-package`/`publication-map`.
- `structured-content-rendering` — `CanonicalPackage.load()` (full re-validation) → a registered renderer
  (`renderers/multipage_markdown.py`) → `renderers/validate_rendered.py` → atomic promotion;
  produces `rendered-output-profile`.

**Ten SharePoint-domain plugins (Phase 9, `2026-08-08` update):** extracted/generalized from a
separate SharePoint migration repository per an exhaustive 505-file source audit
(`temp/phase9-source-audit/file-tracking.json`), same standalone-install convention as the four
content-pipeline plugins above — `sharepoint-discovery`, `sharepoint-schema`,
`sharepoint-provisioning`, `sharepoint-page-modernization`, `sharepoint-link-remediation`,
`sharepoint-content-migration`, `sharepoint-migration-planning` (Stage 3a implemented; setup/
discovery/generated-wave-script stages remain design scaffolds), `sharepoint-content-publication`,
`workbench-setup`, and `sharepoint-agents-and-skills` (agent/native-skill lifecycle plus 9 Claude
Code routing/analysis agents in `agents/`). Every write-capable module across these plugins shares
one three-gate safety contract: planning is pure, apply is dry-run by default, and a real apply
requires both an explicitly injected executor/writer and a plan-derived confirmation token. See
each plugin's own README for scope, non-responsibilities, and provenance.

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

## 5. What This Repo Deliberately Does Not Have (Phase 1 scope, plus later corrections)

- No running service, no API, no database, no CI/CD pipeline.
- No preview/editing tool for content — SharePoint Online already provides native markdown
  preview/editing at the eventual destination.
- **Corrected 2026-08-08:** an actual publish step into SharePoint and native SharePoint skills
  now exist (`sharepoint-content-publication`, `sharepoint-agents-and-skills`) — this line
  originally said neither was built or authorized; that was true for Phase 1 scope only, and is
  superseded by Phase 6/9 work merged since. Live-tenant I/O beyond opt-in connection testing
  still does not exist anywhere in this workbench — every write-capable module (publication,
  provisioning, content migration, link/field-image remediation) ships zero transport of its own
  and requires an explicitly injected executor/writer plus a plan-derived confirmation token; nothing
  writes to a real tenant autonomously.
- No renderers beyond `multipage_markdown.py` — see
  `docs/research/structured-content-engineering/legacy/future-output-profiles.md` for candidate
  profiles (including dual-target rendering for human visual consumption vs. agent-optimized RAG
  digests).

## 6. Roadmap / Open Questions

- **Phase 1 status:** engineering-complete (real CEIS Manual cut over through the finished plugin,
  `convert`/`render` both validated PASS, a real defect found and fixed with regression tests, full
  suite 449 passed/1 skipped). Formal closure is pending one human step — see `start-here.md` for
  the exact remaining checklist.
- **Phase 2 status:** planned, not yet executed. Spec and an 18-task TDD implementation plan exist
  (`docs/superpowers/specs/2026-07-28-phase2-canonical-publication-contract-hardening-design.md`
  and its companion plan), reviewed across multiple rounds of external adversarial review.
  Execution is gated on Phase 1's formal closure and explicit user approval — see `start-here.md`.
- **The authoritative full roadmap** — Phase 2 through Phase 8, plus 3.0 and 5.5A/5.5B, each with
  subphases, implementation stages, entry/exit gates, and a full traceability matrix — is
  `docs/vision/master-initiative-plan-workstreams-and-phases.md`. This supersedes the original
  high-level proposal in `docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md`
  (kept for historical comparison) with a structure that survived several rounds of external
  review: proposed plugin boundaries (`sharepoint-knowledge`, `structured-content-rendering`,
  `knowledge-evaluation`) and a repository rename are explicitly deferred, not authorized by either
  document alone — each requires its own reviewed decision when its trigger condition is met (see
  the master plan's traceability matrix and extraction-triggers reference).
- Open architecture/governance questions (knowledge-unit boundaries, publication-map reuse,
  metadata authority, security boundaries, stable identity, and more) are tracked in
  `docs/vision/key-unanswered-questions.md`.

## 7. Project Identification

Project Name: sharepoint-knowledge-workbench

Repository: `github.com/richfrem/sharepoint-knowledge-workbench`, `main` branch (default, pushed)

Primary Contact: Richard Fremmerlid

Date of Last Update: 2026-08-02
