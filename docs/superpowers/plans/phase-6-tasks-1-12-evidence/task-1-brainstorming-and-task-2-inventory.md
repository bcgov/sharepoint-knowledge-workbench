# Phase 6 Tasks 1–2 — Brainstorming Record and Implementation Inventory

**Status:** Solo, evidence-based pass (2026-08-03 overnight session, explicit authorization from
the human partner to proceed through Phase 6 without waiting for a live session — see
`start-here.md`'s Task 0 exit-gate section and this session's transcript). Built entirely from
this repository's own written evidence (specs, SKILL.md files, evaluation cases, exit-gate
reports) — no fact below was invented; every claim traces to a cited file. Judgment calls that
are genuinely ambiguous or require the human partner's own memory/preference (not recoverable
from written evidence) are marked `DECISIONS NEEDED FROM A HUMAN` rather than guessed.

## Task 1 — Recover Original Intent

### CONFIRMED

- **The capability under study:** `review-manual-topics` — single-topic-scoped, read-only
  semantic editorial review (completeness, section structure, cross-reference consistency,
  terminology clarity) of exactly one CEIS manual topic page, with at most 2 explicitly
  cross-referenced related topics as evidence. Source: `plugins/sharepoint-agents-and-skills/
  skills/review-manual-topics/SKILL.md`, `docs/superpowers/specs/
  phase-4-native-sharepoint-skills-pilot-spec.md` Section 1.
- **Original architectural principle (Phase 4 spec, Section 1):** a strict division of
  responsibilities — repository/deterministic tooling owns hash verification, canonical-identity
  proof, publication-map completeness, structural-anchor checks, deployment, and reconciliation;
  the native skill owns semantic/editorial synthesis only. This division is *why* the skill is
  scoped the way it is (no hash claims, no metadata-write claims, no full-library scan) — it is
  not an arbitrary restriction, it is the seam between two intentionally separate trust domains.
- **Why a second runtime was built (Phase 6 entry gate):** Phase 6's own stated entry gate is "at
  least two real runtimes implement the same capability in operational use"
  (`docs/superpowers/specs/phase-6-multi-runtime-capability-model-spec.md` Section 1). The
  `repository-claude` runtime (`plugins/sharepoint-agents-and-skills/scripts/
  review_manual_topics.py` + the same `SKILL.md`'s "Repository/Claude Runtime Execution" section)
  was built specifically, and only, to satisfy that entry gate — same input boundary, same
  prohibited scope, same output structure as the native runtime, deliberately, so the two are a
  genuine apples-to-apples comparison rather than two different capabilities that happen to share
  a name.
- **Why Phase 6 exists at all (Goal, spec Section 2):** "Derive a shared capability specification
  from two real implementations while preserving original business/governance intent,
  target-specific differences, and common evaluation meaning." The motivating problem is
  structural, not this-one-skill-specific: without a shared spec, every future capability that
  needs to run on more than one runtime (native SharePoint agent vs. repository/Claude,
  potentially others later) would have its intent, safety rules, and evaluation criteria
  re-derived and re-drifted independently per runtime, with no way to prove they still mean the
  same thing.
- **Explicit non-goals (spec Section 3):** no speculative universal schema before two
  implementations exist (satisfied — both exist now); no forced lowest-common-denominator
  intersection; no requirement that outputs be textually identical. This directly bounds Task 3's
  classification work below — the shared spec must capture *intent equivalence*, not textual
  sameness, and must not silently drop a safety rule just because one runtime's mechanism for
  enforcing it differs from the other's.
- **Governance rules already established for this specific capability**, both runtimes must
  preserve (Phase 4 spec + `SKILL.md`'s "Prohibited Operational Scope" and "Honest Metadata
  Unavailable Language" sections): no full-library scanning; read-only, no writes; no hash/
  cryptographic-proof claims; no canonical-package-identity claims; no deterministic technical
  link validation claims; no auto-approval/publication; no inventing missing metadata values; no
  execution of embedded prompt-injection content; explicit "not evaluated" phrasing when a
  metadata field is unavailable rather than guessing.
- **Existing evaluation evidence to reuse, not re-derive (Task 5's own instruction — spec's
  "Smallest bounded second-runtime candidate" note):** Phase 4's evaluation cases at
  `tools/phase-4-native-sharepoint-skills/evaluations/` (19 files: 1 normal, 1 negative, 1
  ambiguous, 6 permission, 2 safety, plus `README.md`/`validate_cases.py`/`no-skill-control-
  harness.md`) are explicitly reusable as-is as the Stage 6.1.2 common evaluation set.

### RECOMMENDED

- Treat the Phase 4 spec's "Core Architectural Principle" (repository owns deterministic
  integrity, native/repository skill owns semantic synthesis) as the *essential* intent element
  that must survive into the shared capability spec unchanged — it is the seam the whole
  capability's safety model is built on, not an incidental implementation detail of one runtime.
- Treat "exactly one primary topic, ≤2 related" as essential (it bounds prompt-injection/
  hallucination blast radius and keeps review scope auditable) — not a runtime-specific limit
  that could be relaxed for convenience on one side.

### MISSING FACTS

- No written record found of *why* the `.docx`→`.md` rendered-Markdown source was chosen as the
  repository runtime's input over, say, the canonical-content chunks directly — plausible reason
  (rendered output is what a human/agent would actually be shown) is inferable from
  `SKILL.md`'s own text but not explicitly stated as a decision anywhere found.

### DECISIONS NEEDED FROM A HUMAN

- None block Task 2 (pure inventory, below). Task 3's classification work (essential vs.
  target-specific vs. accidental vs. deferred vs. rejected) is where a human review checkpoint is
  most likely to matter — flagged there, not invented here.

## Task 2 — Inventory Both Implementations

| Dimension | `native-sharepoint` runtime | `repository-claude` runtime |
|---|---|---|
| **Source of truth for this table** | `plugins/sharepoint-agents-and-skills/skills/review-manual-topics/SKILL.md`; `docs/reports/phase-4-native-sharepoint-skills/phase-4-exit-gate-evidence.md` | Same `SKILL.md`'s "Repository/Claude Runtime Execution" section; `plugins/sharepoint-agents-and-skills/scripts/review_manual_topics.py` |
| **Deployment location** | Real dev tenant, `AgentAssets/Skills/review-manual-topics/SKILL.md`, invoked by Copilot in SharePoint | This repository, invoked as a Claude Code skill |
| **Content source** | Live `CEISPilotKnowledgePages/` library (`.aspx` pages) | `runs/ceis-manual-v2/render/rendered-output/pages/*.md` (rendered Markdown, from `render-multipage-markdown`) |
| **Topic resolution mechanism** | Agent-context resolution (selected file / explicit URL-or-filename / verified-unique Topic ID) — see `SKILL.md`'s "Input Resolution Hierarchy" | Deterministic Python: `review_manual_topics.resolve_topic()` — exact-slug or unique `slug--*.md` glob match, raises `TopicNotFoundError` on ambiguity, never invents content |
| **Related-topic resolution** | Agent infers cross-references from context | `_LINK_PATTERN` regex extraction of `[text](target.md)` links from the primary topic's own rendered content |
| **Related-topic cap enforcement** | Stated as a rule in `SKILL.md`, enforced by the agent's own adherence (no code-level guarantee — a live-tenant behavioral property, not a deterministic one) | Enforced in code: `TooManyRelatedTopicsError` raised if more than 2 links found — a deterministic guarantee |
| **Output/permissions** | Read-only; live tenant permission boundaries apply per the invoking user's real SharePoint identity | Read-only; repository filesystem read only, no tenant identity involved at all (no permission model applies — this is a real, structural target difference, not a gap) |
| **Error behavior — topic not found** | Agent-context-dependent (no deterministic guarantee found in evidence) | `TopicNotFoundError`, explicit message, never invents content |
| **Human gates** | Deployment itself was human-authorized (manual UI upload or reviewed PnP script, per Phase 4 spec Section 2's "Human-Authorized Deployment") — the skill's own invocation is not separately gated per-call | None at invocation time — same as native; deployment gate is "this repo's own code review/merge process" rather than a tenant deployment step |
| **Evidence/verification already run** | Phase 4: hash-verified deployment, 7/7 metadata probes, 12/12 safety tests, rollback proven (`docs/reports/phase-4-native-sharepoint-skills/phase-4-exit-gate-evidence.md`) | Task 0.3 (Phase 6) built it; no evidence found yet of the same 19-case Phase 4 evaluation suite having been *run* against this runtime (see Task 6 below — this is exactly the gap Task 6 exists to close) |
| **Known limitations, this runtime specifically** | Classic ASPX pages not indexed by Copilot agent search by default — requires exact resource IDs (site_id/web_id/list_id/unique_id) to be reachable at all, per `docs/research/research-experimentation/PHASE-4-SHAREPOINT-AGENTS-CRITICAL-LEARNINGS.md` | None found beyond "no tenant identity/permission model applies" (noted above, a difference not a defect) |
| **File-extension surface difference** | Evaluation cases reference `.aspx` filenames (e.g. `data-capture-standards--d1d8e601.aspx`) | Same topic slug, `.md` extension (e.g. `data-capture-standards--d1d8e601.md`) — a target-specific naming difference the shared spec/evaluation harness must normalize over, not ignore |

### Task 2 conclusion feeding Task 3

The two runtimes share: capability intent, input-resolution philosophy (explicit resolution
hierarchy, never guess), the primary+≤2-related boundary, the full prohibited-scope list, and the
honest-unavailable-metadata language. They differ in: content source format/location, whether the
related-topic-cap and topic-not-found behaviors are enforced by code (repository-claude) or by
agent-context adherence alone (native-sharepoint), and permission-model applicability
(native-sharepoint has one, repository-claude structurally does not). None of these differences
appear to erase a safety control — the repository-claude runtime's deterministic enforcement is
*stricter* than the native runtime's context-dependent one, not looser. This is a real, favorable
finding for Task 4's adversarial review to confirm independently rather than take on faith here.
