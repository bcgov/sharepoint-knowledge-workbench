# Phase 7 Design — Copilot Cowork and Copilot Studio Desk-Research Evaluation

> **Planning status:** This design bounds Phase 7's actual scope for this round of work. It
> supersedes the broader, multi-target-agnostic framing in
> `docs/superpowers/specs/phase-7-cowork-copilot-studio-evaluation-spec.md` and
> `docs/superpowers/plans/phase-7-cowork-copilot-studio-evaluation-plan-scaffold.md` only where
> this document narrows or clarifies scope; it does not contradict either document's disposition
> (`RESEARCH`) or non-goals. It does not authorize implementation, tenant changes, environment
> creation, or a proof of concept.

## 1. Candidate and owner (entry gate satisfied)

- **Primary use case (single, not a set):** the interactive document-conversion and publication
  workflow for the SharePoint Knowledge Workbench — intake → document selection → output formats →
  destinations → agent grounding → validation → human approval.
- **Owner:** Richard Fremmerlid, workbench pilot owner and decision-maker.
- **Why this satisfies the Phase 7 entry gate:** a concrete use case and named accountable owner
  exist, per `phase-7-cowork-copilot-studio-evaluation-spec.md` Section 1.

## 2. Scope boundaries (this round)

- Evaluate **one** primary workflow only. The broader Phase 1–6 workbench capability set
  (extraction, canonical/publication pipeline, governed SharePoint library, native SharePoint
  skill, knowledge agent, shared capability model) is used **only as comparison baseline and
  integration context** — it is not independently re-evaluated capability-by-capability.
- **The baseline is three-way, not two-way.** Cowork and Copilot Studio are compared separately
  against (a) the Phase 1–6 repo/Claude workbench pipeline, and (b) the already-built native
  SharePoint agent implementation — `plugins/sharepoint-agents-and-skills` (Phase 6, Tasks 0–12;
  evidence at `docs/superpowers/plans/phase-6-tasks-1-12-evidence/`), specifically its
  `review-manual-topics` skill deployed and live-evaluated against tenant `AG-CSB-INTRANET-DEV`
  (agent `CEIS-Pilot-Knowledge-Agent`; results at
  `plugins/sharepoint-agents-and-skills/evaluations/common/native-sharepoint-results/`).
  **BC Government user/account context confirmed** — `RESULT-PERM-01.md` shows the evaluation was
  performed under a `gov.bc.ca` account identity. This establishes the account/domain context
  only; it does not by itself establish the tenant's cloud classification, compliance boundary,
  hosting model, Protected B authorization, regional category, or equivalence to GCC/GCC High.
  Those broader tenant characteristics are `TENANT_UNKNOWN` until supported by authoritative
  tenant evidence, and the bundled BC-Government Copilot Studio findings (Section 3b) should be
  treated as same-account-context evidence, not assumed equivalence of compliance boundary. The
  question Section 4's memo must answer is
  not "can Cowork/Studio run the pipeline" but "what does Cowork/Studio add beyond what the
  native SharePoint agent already proves, across knowledge-source configuration, grounding
  behavior, instruction/config artifact model, deployment/reconciliation, and permission-trimmed
  retrieval."
  - **Correction on runtime determinism:** the native SharePoint agent baseline itself has two
    runtimes with different enforcement strength for its "max 2 related topics" contract —
    `repository-claude` enforces it programmatically (`TooManyRelatedTopicsError` in
    `plugins/sharepoint-agents-and-skills/scripts/review_manual_topics.py`), while
    `native-sharepoint` enforces it only through agent instructions and was observed to exceed
    the cap live (`DRIFT-CHECK.md`: `AMB-01` consulted 3 and 7 related topics against an
    allowance of 2). When this design or the eventual memo characterizes any instruction-level
    contract (native SharePoint, Cowork, or Studio) as a control, it must be described as a
    prompt-level contract, empirically validated only against the specific cases actually run —
    never as deterministic — unless a programmatic enforcement mechanism is identified and cited.
- **Desk research only.** No live build, no environment creation, no tenant change, no plugin/
  skill scaffolding, no proof of concept. Reasons (confirmed platform-access facts, not capability
  conclusions):
  - Copilot Cowork: `NOT_ENABLED_IN_TENANCY` — `LIVE_EVALUATION_BLOCKED`.
  - Copilot Studio: `ACCESS_CONFIRMED`, `DEDICATED_ENVIRONMENT_NOT_AVAILABLE` —
    `LIVE_BUILD_AND_VALIDATION_BLOCKED`.
- Cowork and Copilot Studio receive **separate** decisions (per the base spec's Section 9,
  unchanged).
- **Platform-access status must never be conflated with a capability conclusion.** Explicitly do
  not describe:
  - Copilot Studio as unlicensed or unavailable (it is licensed; only a dedicated environment is
    unavailable);
  - Copilot Cowork as available but untested (it is not enabled at all);
  - either platform as live-validated;
  - the access limitation itself as evidence that either platform lacks capability.
- **Amended (this correction round):** every substantive conclusion in the evidence memo is
  tagged with exactly one **evidence type/confidence** label from the seven below, kept as a
  field **separate from freshness status** (Section 4a's ledger schema) — the two dimensions must
  never be conflated in the same field:
  - `CURRENT_PRIMARY_SOURCE_VERIFIED` — checked against a live, current Microsoft source during
    this phase (cite the URL and fetch date).
  - `BUNDLED_PRIMARY_SOURCE` — **actual Microsoft documentation** (real product-doc content, e.g.
    Microsoft Learn pages with frontmatter) captured verbatim in the Phase 7 prior-research
    bundle, not yet re-checked live this phase. Does **not** apply to internally authored
    analysis, blueprints, or research notes merely because they discuss Microsoft products.
  - `BUNDLED_RESEARCH_SYNTHESIS` — internally authored analysis, blueprint, or research-note
    content in the bundle (e.g. `viable-skills-summary.md`, `research/limitations.md`,
    `research/criticisms.md`, `research/elicitation.md`, `generative-orchestration.md`,
    `research/schema-notes.md`, `research/overview.md`, `research/cowork-limitations.md`,
    `research/mcp-apps.md`, `research/how-to-build-custom-skills.md`'s own framing, and the
    `research/reviews/*` adversarial-review chain) — carries lower confidence than
    `BUNDLED_PRIMARY_SOURCE` unless a specific direct citation to real Microsoft doc content is
    identified within it.
  - `EMPIRICALLY_OBSERVED` — a direct, dated, scoped experiment or test-execution result (e.g. the
    bundle's `agent-build-walkthrough.md`/`learnings.md` hands-on Copilot Studio build; this
    repo's own live `native-sharepoint` evaluation results; a passing repository test that
    actually executes the behavior being claimed, e.g.
    `test_more_than_two_related_topics_is_rejected`).
  - `REPOSITORY_VERIFIED` — a claim confirmed by direct inspection of this repository's own code
    (e.g. `TooManyRelatedTopicsError`'s existence in `review_manual_topics.py`) where no test
    execution evidence was separately checked — use `EMPIRICALLY_OBSERVED` instead once a passing
    test demonstrating the behavior is identified and cited.
  - `SECONDARY_SOURCE_CLAIM` — practitioner, vendor, community, or consultant-sourced (e.g. the
    bundle's PromptArmor/TD SYNNEX citations, or `learnings.md` L25's community-sourced billing
    figures).
  - `HYPOTHESIS_PENDING_HANDS_ON_VALIDATION` — plausible but untested in the specific
    tenant/platform configuration this workflow would actually use.

## 3. Copilot Studio evaluation angle: agent/skill-as-artifact pattern

Phase 6 built `sharepoint-agents-and-skills` as a versioned, testable, deployable artifact model
for native SharePoint agents and skills (author → package → deploy → reconcile against tenant →
drift-detect). Copilot Studio plausibly supports a structurally similar pattern for its own
agents/actions/connectors (author → publish → environment/ALM → channels), potentially with
additional capabilities (custom connectors, richer orchestration, multi-channel distribution) that
native SharePoint skills do not have.

This is folded into the Studio evaluation as one explicit comparison angle, not a scope expansion:
does Studio's authoring/ALM model offer documented capability beyond what
`sharepoint-agents-and-skills` already delivers for the primary workflow, and is that capability
relevant to this specific workflow's needs? Any conclusion here is tagged with one of the five
evidence labels in Section 2 — it cannot be `CURRENT_PRIMARY_SOURCE_VERIFIED` or
`EMPIRICALLY_OBSERVED` for claims that require observing Studio's actual authoring UX, since no
environment is available; the bundle's Connected Agents Input/Output-contract findings and the
Dataverse-solution-export-only versioning finding are `BUNDLED_PRIMARY_SOURCE`/
`EMPIRICALLY_OBSERVED` respectively (per the bundle's `generative-orchestration.md` §8–9), not
`CURRENT_PRIMARY_SOURCE_VERIFIED`, until re-checked live this phase.

## 3a. Portability classification: instructional format vs. executable runtime

For each platform, findings must distinguish two categories rather than a single "can/can't run
the pipeline" verdict:

- **Portable (instructional intent only):** system-prompt-equivalent guidance, topic/routing
  descriptions, YAML-frontmatter-shaped metadata.
- **Non-portable (executable):** scripts, sub-agents, hooks, commands, binaries, and any
  supporting runtime asset that must actually execute (this repo's extraction/rendering/
  validation Python, and `sharepoint-agents-and-skills`' PowerShell deploy/reconcile scripts).

This mirrors the bundle's own framing (`viable-skills-summary.md` Claim 6: Cowork adopts SKILL.md
"format-compatible but not runtime-compatible") and must be applied explicitly to whichever parts
of the primary workflow a future pilot would attempt to host on Cowork or Studio.

## 3b. Split-runtime trade-off assessment (both platforms)

For both Cowork and Studio — not Cowork alone — assess the shape: platform as conversational
orchestrator, workbench services as deterministic execution backend, SharePoint as content/
grounding destination. Required dimensions, each requiring a source citation and evidence label:
identity/execution boundary (see Section 3c), state/idempotency and OneDrive/Graph `etag`
concurrency, approval placement, auditability, DLP visibility, latency, duplicate metering/hosting
cost, and Protected B/ITSG-33 applicability (tenant-applicability itself is
`HYPOTHESIS_PENDING_HANDS_ON_VALIDATION` unless separately confirmed). Numeric claims here (e.g.
latency figures, Dataverse pricing) carry whichever evidence label is accurate per Section 2 —
several are `SECONDARY_SOURCE_CLAIM` in the bundle and must not be upgraded on citation alone.

For Copilot Studio specifically, the bundle's lifecycle-interception points
(`generative-orchestration.md`: `OnKnowledgeRequested`, `AI Response Generated`, `On Plan
Complete`) are **candidate control points only**, not established execution semantics for this
workflow:
- `OnKnowledgeRequested` — candidate control point for grounding-query shaping/filtering.
- `AI Response Generated` — candidate control point for inspecting, modifying, or redacting a
  generated response. Do not describe this as part of the workbench's own structured-content
  compile/render pipeline.
- `On Plan Complete` — candidate post-plan control point; suitability for a publication-handoff
  role must be verified, not assumed.
- The Three-Layer decision boundary (Deterministic / Hybrid-Intercept / AI Orchestrator) is a
  candidate architecture for separating conversation from irreversible publication actions, not a
  confirmed fit.

## 3c. Identity and governance comparison

Do not generalize any single observed pattern into a universal identity model for a platform, and
do not treat one evidence file as proof of a complete identity model. `RESULT-PERM-01.md` shows
the **caller/test identity** used in one permission-boundary evaluation (e.g. `OWNER_EDITOR`/
`Richard.Fremmerlid@gov.bc.ca`) — it is not, by itself, evidence of the agent's execution
principal, deployment identity, retrieval identity, or publication identity. The identity decision
matrix must carry these as **separate, independently evidenced fields per architecture** —
deployment identity, retrieval identity, user-interaction identity, approval identity, and
publication identity — each marked `UNKNOWN` unless a specific repository or bundle citation
establishes it, rather than inferring the remaining fields from the one confirmed
user-interaction-identity data point.

For each of: (a) the native SharePoint agent baseline, (b) Cowork (delegated end-user Entra
identity per `viable-skills-summary.md` Claim 7 — a "Primitive Gap" the source itself says is a
roadmap gap, not a design ceiling, since Entra Agent ID/Agent 365 primitives exist at the platform
level even though Cowork the product doesn't wire them in), and (c) Copilot Studio — build the
matrix covering: user-authenticated knowledge access, user-delegated connector actions,
connection-owner/configured-connection execution, external service/backend identity, and any
future custom-engine or Entra Agent ID architecture. The bundle's `generative-orchestration.md`
§8 OAuth/on-behalf-of finding documents one Studio connected-agent pattern; it must not be read as
Studio's only identity mode, and must not be extrapolated to fields (deployment/retrieval/
publication identity) it does not itself describe. State explicitly, per architecture, whose
identity reads, transforms, approves, and publishes, leaving each unsupported cell `UNKNOWN` —
directly relevant because this workflow can alter SharePoint content, not deferred governance
research.

## 4. Deliverable

**Amended (this correction round):** the formal decision record is one evidence memo, but it is
now explicitly authorized to rest on three supporting artifacts rather than being a single
undifferentiated document — the source ledger and capability-gap analysis produced during
drafting proved genuinely useful for provenance tracking and are retained, and a third supporting
artifact (the current-source verification record) was added during this correction round. The
memo itself remains the single required decision-record deliverable:

```
docs/reports/phase-7-cowork-copilot-studio-evaluation/desk-research-evidence-memo.md   (required, formal decision record)
docs/reports/phase-7-cowork-copilot-studio-evaluation/prior-research-source-ledger.md  (supporting — per-source provenance)
docs/reports/phase-7-cowork-copilot-studio-evaluation/capability-gap-analysis.md       (supporting — full capability-gap working analysis)
docs/reports/phase-7-cowork-copilot-studio-evaluation/current-source-verification-record.md (supporting — Section 7's focused freshness-check results)
```

The memo consolidates and cites the supporting artifacts; it does not repeat their full content.
Exit criteria (Section 8) apply to the memo as the decision record, checked for consistency
against the supporting artifacts.

Memo contents:

1. Primary use case restated, owner, success criteria for "meaningful advantage."
2. Baseline: what Phases 1–6 already deliver for this workflow, **and** the native SharePoint
   agent baseline (Section 2's three-way-baseline citations — not re-derivation).
3. **Capability classification table:** the primary workflow's own steps (intake conversation,
   workflow guidance, knowledge-grounded review, structured state management, DOCX/PDF
   extraction, deterministic rendering, SharePoint deployment/reconciliation, regression/
   validation evidence) classified `DIRECT_FIT` / `ADAPTATION_REQUIRED` / `INCOMPATIBLE`, per
   platform, using the bundle's `knowledge-plugins-analysis/README.md` and `plugin-analysis/*.md`
   classification **method** only — never citing those files' own third-party subjects as
   findings about this repo's workflow.
4. **Cowork section:** documented capabilities relevant to the workflow, portability
   classification (Section 3a), split-runtime assessment (Section 3b); explicit
   `NOT_ENABLED_IN_TENANCY` / `LIVE_EVALUATION_BLOCKED` status stated separately from capability
   findings; disposition.
5. **Copilot Studio section:** documented capabilities relevant to the workflow, the
   agent/skill-as-artifact comparison angle (Section 3), portability classification (Section 3a),
   lifecycle-trigger candidates and split-runtime assessment (Section 3b), identity decision
   matrix (Section 3c); explicit `ACCESS_CONFIRMED` / `DEDICATED_ENVIRONMENT_NOT_AVAILABLE` /
   `LIVE_BUILD_AND_VALIDATION_BLOCKED` status stated separately from capability findings;
   disposition.
6. Per-finding tagging: every conclusion labeled with one of the seven Section 2 evidence-type labels.
7. Final section: what would need to be true (specific documented capability advantage, plus
   platform access) to justify a future pilot for each target.
8. **Future hands-on-validation backlog:** every finding tagged
   `HYPOTHESIS_PENDING_HANDS_ON_VALIDATION`, listed together as the concrete backlog to test once
   platform access exists.

## 4a. Ledger schema correction

The prior-research source ledger must carry **two separate fields** per entry — `Evidence type/
confidence` (one of the seven labels in Section 2) and `Freshness status` (one of: `STILL_CURRENT`,
`UPDATED_BY_CURRENT_DOCUMENTATION`, `SUPERSEDED`, `REQUIRES_FRESHNESS_CHECK`,
`HYPOTHESIS_PENDING_HANDS_ON_VALIDATION`, `NOT_RELEVANT_TO_PHASE_7`). An evidence-type label must
never appear in the freshness-status field or vice versa.

## 5. Dispositions

For Cowork and Copilot Studio **separately**, one of:

- `JUSTIFIED_FOR_FUTURE_PILOT` — a specific, documented capability advantage over the existing
  repository/Claude workbench was found for the primary workflow, and a future pilot is
  recommended once platform access allows it.
- `REMAIN_RESEARCH` — inconclusive from documentation alone; hands-on validation is required
  before any pilot recommendation can be made.
- `NO_ADDITIONAL_VALUE_DEMONSTRATED` — documentation review found no meaningful advantage over the
  existing workbench for this workflow.
- `BLOCKED_PENDING_PLATFORM_ACCESS` — used when the access blocker itself prevents forming even a
  documentation-only conclusion (e.g., a claim can only be verified by observing the authoring
  UX). This is an access-status disposition, not a capability disposition, and must not be used as
  a substitute for `NO_ADDITIONAL_VALUE_DEMONSTRATED`. **Correction (this round):** this
  definition stays strict and unchanged — it does not cover cases where documentation-only
  conclusions were in fact reachable but practical suitability remains unvalidated. That latter
  case is `REMAIN_RESEARCH`.

These replace the base spec's generic `BUILD` / `NO_BUILD` / `DEFERRED_UNTIL_EVIDENCE` /
`REJECTED_FOR_NOW` set (Section 8 of the base spec) for this round, since no build path is in
scope and the base spec's four-way set does not distinguish access blockers from capability
findings the way this round requires.

## 6. Non-goals (restated, explicit)

- No platform build, environment creation, tenant change, plugin/skill/connector scaffolding, or
  proof of concept.
- No claim of live validation for either platform.
- No capability-by-capability evaluation of the full Phase 1–6 workbench (baseline/context only).
- No recommendation to pursue a future pilot without a specific, documented capability advantage.
- No treatment of the Phase 7 base spec/plan-scaffold documents as superseded beyond the narrowing
  made explicit in this design.
- No porting assessment of the bundle's third-party plugin catalog (`plugin-analysis/*.md`,
  `knowledge-plugins-analysis/README.md`) — their classification **method** is reused (Section 4
  item 3); their specific subjects are not this repo's plugins and are out of scope.
- No M365 Agents SDK build or adoption decision — the bundle's `microsoft-m365-agents/` findings
  are used only as Copilot Studio interop background (Section 3), not as a third evaluation
  target; the master roadmap names only Cowork and Copilot Studio for Phase 7
  (`docs/vision/master-initiative-plan-workstreams-and-phases.md` lines 826–853).
- No hands-on testing beyond what current tenant access supports — every claim needing an
  environment that does not exist yet stays `HYPOTHESIS_PENDING_HANDS_ON_VALIDATION` (Section 4
  item 8), it is not tested around the blocker.

## 7. Method and cost allocation

- Desk research against current official Microsoft documentation for Copilot Cowork and Copilot
  Studio (fetched live during this phase — no reliance on model memory for platform capability
  claims, consistent with `start-here.md`'s "never invent... licences, permissions, API behaviour"
  rule).
- Baseline comparison against already-accepted Phase 1–6 evidence and the native SharePoint agent
  baseline (Section 2), not re-derivation.
- **Precondition for any future Task 4B (Copilot Studio evidence discovery):** once environment
  access exists, request a Custom/Dedicated Environment rather than accept a default-provisioned
  one — the bundle's `learnings.md` L23 explicitly scopes the observed blanket knowledge-connector
  DLP blocking to Power Platform Default Environments, not necessarily Custom/Dedicated ones.
- Low-cost model effort for documentation inventory/collation; stronger reasoning for the
  capability-gap comparison, the agent-as-artifact angle, the identity decision matrix, and the
  final disposition per target — per the base plan scaffold's cost-allocation guidance.

## 8. Exit criteria for this round

- Evidence memo written, committed, at the path in Section 4.
- Both targets have a disposition from the Section 5 set, each traceable to specific documented
  findings and to the three-way baseline (Section 2).
- Every substantive finding tagged with one of the seven Section 2 evidence-type labels.
- Platform-access status and capability conclusions are never conflated anywhere in the memo.
- No implementation, environment, or tenant action taken.
- No instruction-level contract (native SharePoint, Cowork, or Studio) described as deterministic
  without a cited programmatic enforcement mechanism.
- No single observed Studio identity pattern generalized into a platform-wide identity model.
