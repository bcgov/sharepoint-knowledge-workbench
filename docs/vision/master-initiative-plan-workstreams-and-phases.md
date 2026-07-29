# Master Initiative Plan — AI-Assisted Structured Knowledge Workbench

**Status:** Comprehensive whole-spectrum planning document, distinct from and superordinate to any single
phase's implementation plan. Does not itself authorize implementation of anything beyond what has already
been separately approved (Phase 1, complete; Phase 2, spec approved pending `writing-plans`). Phases 3+
are intentionally left at varying, honest levels of detail — see Section 3.

**Relationship to other documents:**
- `docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md` — the original strategic
  proposal. This document formalizes and completes it into an executable master plan, incorporating the
  narrowing decisions from two rounds of adversarial review (`temp/plan-reviews/`) that the broader plan's
  Phase 2 mechanism (immediate plugin extraction, new agents, rename-first sequencing) did not survive.
- `docs/superpowers/specs/2026-07-28-phase2-canonical-publication-contract-hardening-design.md` — the
  detailed, implementation-ready spec for the one phase currently authorized to move to a plan.
- This document does not replace either. It is the connective layer: every workstream and phase below
  traces to a disposition (NOW/NEXT/LATER/RESEARCH/REJECTED), and phase entry/exit criteria are stated
  even where the phase's internal implementation detail isn't decided yet.

## 1. Correction This Document Makes

An earlier pass in this session conflated **narrowing implementation scope** (correct: only Phase 2 should
become a real implementation plan right now) with **narrowing planning scope** (incorrect: the user asked
for a plan covering the entire vision, broken into subphases — not for the vision itself to be replaced by
one small phase's plan). This document restores full-spectrum planning coverage while keeping the
implementation-readiness gate exactly where the architecture reviews put it: nothing past Phase 2 is
authorized to be built yet.

## 2. Workstreams

Nine workstreams span the full vision. Each maps to one or more phases (Section 4) and carries its own
NOW/NEXT/LATER/RESEARCH/REJECTED disposition per sub-item.

### Workstream A — Canonical Knowledge Foundation
Source-document analysis and conversion; canonical content contracts; stable topic/structural identity;
metadata, lineage, media, and validation; content-type authoring models (manuals, policies, procedures,
training material); source-to-canonical migration and reconciliation.
- **Status:** Substantially built (Phase 1, `docx-to-content`) and being hardened (Phase 2). Content-type
  authoring models beyond "manual" (policy, procedure, training) are **RESEARCH** — no second content type
  has been piloted; do not generalize the schema for hypothetical types.

### Workstream B — Publication and Rendering
Publication-map contract; renderer interfaces; Markdown/Word/PDF/HTML/PowerPoint outputs; templates and
presentation profiles; release identity and publication validation; independent publication from canonical
packages.
- **Status:** Markdown renderer (`multipage-markdown`) built. Publication-map contract being hardened
  (Phase 2). Additional output formats (PDF/Word/HTML/PowerPoint) are **LATER** — explicitly out of Phase
  2's scope per its non-goals; revisit only once Markdown publication is proven independent and a real
  need for another format exists.

### Workstream C — Governed SharePoint Knowledge
SharePoint library architecture; canonical-vs-published source-of-truth rules; metadata mapping; topic
ID/publication ID/owner/status/review-date/validation-state; versioning, permissions, approval, content
review; package-only vs. authorized-write deployment; oversharing/discoverability controls; records,
retention, audit.
- **Status:** **NEXT**, gated behind Phase 3.0 (tenant-capability discovery, Section 4). The minimal
  metadata schema mapping and package-only deployment mode are the two sub-items ready to plan in real
  detail once Phase 3.0 lands (per round-1 architecture review, these have zero tenant-fact dependency and
  could in principle be drafted earlier — but are sequenced after 3.0 so the schema mapping reflects actual
  tenant field constraints rather than guessing). Records/retention/audit integration is **LATER** — no
  pilot exists yet to derive real requirements from.

### Workstream D — Native SharePoint Skills
Tenant capability discovery; `AgentAssets` availability/governance; skill-authoring/deployment permissions;
candidate skill selection; `SKILL.md` generation/validation; manual deployment before automation;
versioning, evidence, promotion, retirement; normal/negative/ambiguous/permission/safety evaluations.
- **Status:** Tenant capability discovery is **NEXT** (Phase 3.0). Everything else in this workstream is
  **RESEARCH** until Phase 3.0's findings exist — the vision doc's own `review-manual-topics` candidate
  skill is a reasonable first pilot target, but its actual feasibility depends entirely on what Phase 3.0
  discovers about `AgentAssets` and skill-authoring permissions in the real tenant.

### Workstream E — SharePoint Knowledge Agents
Approved grounding sources; source scoping/permission behaviour; agent instructions/answer boundaries;
current/stale/superseded content handling; ownership/review dates; answerable/unanswerable evaluation sets;
deployment/lifecycle governance.
- **Status:** **RESEARCH.** Depends on Workstream D's native-skill pilot succeeding first (an agent needs
  something to be grounded in) and Phase 3.0's findings on agent-creation permissions/approval paths in the
  tenant. Do not plan agent behavior details before a skill pilot exists to ground them in.

### Workstream F — Multi-Runtime Capability Model
Shared capability specification; GitHub/Claude skill implementation; native SharePoint skill implementation;
SharePoint-agent support package; common evaluation cases; target-specific adapters; behavioural-drift
detection; reuse-vs-target-specific-behavior rules.
- **Status:** **LATER.** The vision doc's own exit gate for this ("shared spec+evaluation cases prevent
  behavioural drift across at least two runtimes") cannot be evaluated until at least two runtimes actually
  exist with a shared capability implemented on both. Currently zero SharePoint-side runtimes exist. Do not
  design the shared capability specification format speculatively before there is a second runtime to
  specify against.

### Workstream G — Cowork and Copilot Studio
Capability-gap analysis; candidate use cases; packaging/organizational distribution; connector/external-
system requirements; workflow/orchestration requirements; licensing/capacity/environment/ownership;
explicit build/no-build gates.
- **Status:** **REJECTED for now, revisit as RESEARCH only if a concrete use case with an accountable owner
  emerges** (per the vision doc's own Phase 7 exit gate: "build only the target that has a concrete use
  case and accountable owner"). No such use case currently exists. Do not scaffold packaging plugins or
  manifests speculatively.

### Workstream H — Evaluation and Assurance
Canonical fidelity; validator mutation coverage; publication correctness; SharePoint content readiness;
skill behaviour; agent grounding; permission/oversharing tests; staleness/ambiguity tests; cross-runtime
behavioural comparison; release evidence/auditability.
- **Status:** Canonical fidelity and validator mutation coverage are **NOW** — this is the substance of
  Phase 2 (Section 5.1 of the Phase 2 spec). Everything else in this workstream is **LATER/RESEARCH**,
  gated behind the workstreams it evaluates (C/D/E/F) actually existing. Per the round-1 architecture
  review, `knowledge-evaluation` stays shared test infrastructure, not a plugin, until a consumer needs to
  invoke it independently — that threshold is not met yet for any sub-item here beyond Phase 2's own
  mutation suite.

### Workstream I — Operations and Lifecycle
Dev/test/production promotion; release management; version compatibility; monitoring/drift detection;
ownership/support; review cycles; incident handling; deprecation/retirement; onboarding/adoption patterns.
- **Status:** **LATER**, explicitly per the vision doc's own Phase 8 framing ("should not be designed in
  detail until pilots establish real operational requirements"). Nothing here should be designed before
  Phase 3-5 produce real operational experience to design from.

## 3. Full Phased Roadmap With Honest Detail Levels

| Phase | Name | Detail level now | Status |
|---|---|---|---|
| 1 | Structured Knowledge Conversion and Canonical Content POC | Implemented | **DONE** (engineering-complete; formal closure pending human spot-check, see `runs/ceis-manual-v2/evidence-report.md`) |
| 2 | Canonical/Publication Contract Hardening | Implementation-ready | **Spec approved, plan pending** (`docs/superpowers/specs/2026-07-28-phase2-canonical-publication-contract-hardening-design.md`) |
| 3.0 | SharePoint Tenant-Capability Discovery | Research-spike-ready, concrete questions defined below | **NEXT** |
| 3 | Governed SharePoint Knowledge Pilot | Bounded pilot scope, provisional architecture | **NEXT, gated behind 3.0** |
| 4 | Native SharePoint Skills Pilot | Capability/governance requirements only | **RESEARCH, gated behind 3.0/3** |
| 5 | SharePoint Knowledge Agent Pilot | Capability/governance requirements only | **RESEARCH, gated behind 4** |
| 6 | Multi-Runtime Capability Model | Decision framework only, no committed implementation | **LATER, gated behind ≥2 real runtimes** |
| 7 | Cowork and Copilot Studio Evaluation | Decision framework, candidate pilots only | **REJECTED pending concrete use case** |
| 8 | Scale, Promotion, and Operations | Operational capability categories and entry criteria only | **LATER, gated behind Phase 3-5 experience** |

This intentionally avoids two failure modes: reducing the entire vision to Phase 2's implementation detail,
and fabricating implementation-level detail for phases whose real requirements (tenant facts, pilot
outcomes, a second runtime) don't exist yet.

### Phase 3.0 — concrete questions and evidence requirements (research-spike-ready)

Per both architecture reviews: having tenant access is not the same as knowing what the tenant permits.
Phase 3.0's sole deliverable is `tenant-capability-report.md`, answering, with observed evidence (not
assumption):
- Does `AgentAssets` exist in this tenant? Where, and who can write to it?
- Is native `SKILL.md` authoring available on this tenant's licence/rollout ring? What schema does it
  actually accept?
- Can agents be created, by whom, with what approval path? What identity would a write path use?
- Is native Markdown rendering enabled in this tenant?
- What are the actual available metadata field types/constraints for a pilot knowledge library?

### Phase 3 — provisional architecture (bounded pilot scope)

Ready to describe now, pending Phase 3.0 confirmation, not full implementation: a pilot knowledge library
with the minimal metadata schema (owner, status, review date, topic ID, publication ID, validation state)
mapped from Phase 2's hardened canonical/publication contracts; versioning; permission review; package-only
deployment mode (produces artifacts, writes nothing) as the default until an authorized write identity is
approved; topic/publication review workflow. Native-skill and agent work (Phases 4-5) are out of Phase 3's
scope even if Phase 3.0 shows they're technically available — sequence them after Phase 3's pilot library
proves out, not concurrently.

### Phases 4-8 — requirements-only, no committed architecture

Each of these phases' scope is already stated at the requirements level in the original vision doc
(Sections 7's Phase 4-8 descriptions) and is not repeated here in more detail than that, per the "honest
detail levels" table above — inventing implementation specifics for these now would be exactly the
premature-commitment cost both reviews warned against for Phase 2's plugin-extraction question.

## 4. Backlog Classification Summary

| Disposition | Items |
|---|---|
| **NOW** | Phase 2 (all of Workstream A/B hardening + Workstream H's mutation-testing substance) |
| **NEXT** | Phase 3.0 tenant discovery; Phase 3's metadata-schema mapping and package-only deployment mode |
| **LATER** | Additional renderer output formats (B); records/retention/audit (C); Workstream F (multi-runtime model); Workstream I (operations/lifecycle) |
| **RESEARCH** | Workstream D beyond tenant discovery; Workstream E entirely; Phase 4-5 architecture specifics |
| **REJECTED (for now)** | Workstream G (Cowork/Copilot Studio) — revisit only if a concrete use case with an accountable owner appears |

Also carried over from the round-1 architecture review, unchanged: repository rename deferred (not
rejected — revisit anytime, low urgency); no new plugins beyond `docx-to-content` until Phase 3 justifies
`sharepoint-knowledge`; no new agents until ≥2 plugins with ≥2 distinct user journeys exist.

## 5. Traceability

Every subject raised across this session's discussion and the original vision doc is accounted for above,
either as an active NOW/NEXT item, a stated gating dependency, or an explicit LATER/RESEARCH/REJECTED
disposition with its reason — nothing is silently dropped, and nothing beyond Phase 2 is silently promoted
to "planned in detail" without its prerequisite evidence existing first.
