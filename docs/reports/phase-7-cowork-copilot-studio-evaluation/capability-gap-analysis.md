# Phase 7 Capability-Gap Analysis — Copilot Cowork and Copilot Studio

> **Status:** Desk research only, per
> `docs/superpowers/specs/2026-08-03-phase-7-cowork-copilot-studio-desk-research-design.md`. No
> live build, tenant change, or environment creation occurred. Evidence labels
> (`CURRENT_PRIMARY_SOURCE_VERIFIED` / `BUNDLED_PRIMARY_SOURCE` / `EMPIRICALLY_OBSERVED` /
> `SECONDARY_SOURCE_CLAIM` / `HYPOTHESIS_PENDING_HANDS_ON_VALIDATION`) are used exactly as defined
> in the design. Full source provenance is in
> `docs/reports/phase-7-cowork-copilot-studio-evaluation/prior-research-source-ledger.md`.

## 1. Primary workflow and owner

The interactive document-conversion and publication workflow for the SharePoint Knowledge
Workbench: intake → document selection → output formats → destinations → agent grounding →
validation → human approval. **Owner:** Richard Fremmerlid. Success criterion: a "meaningful
advantage" is a specific, documented capability that the existing workbench and native SharePoint
agent do not already provide for this workflow — not general platform capability.

## 2. Existing Phase 1–6 baseline

Four core domain plugins (`source-document-extraction`, `document-structure-analysis`,
`structured-content-assembly`, `structured-content-rendering`) chained into a real
`analyze → confirm → convert → render` pipeline, each independently installable, proven end-to-end
on the CEIS Manual pilot with a byte-identical golden-master reproduction. `workbench-setup`
provides the cross-cutting connection/workflow-profile layer. `sharepoint-content-publication`
produces human-actionable publication plans only — no automated tenant write path exists yet.
(Evidence: `start-here.md`; not re-derived here.)

## 3. SharePoint-agent baseline (the third comparison point)

`plugins/sharepoint-agents-and-skills` (Phase 6, Tasks 0–12; evidence at
`docs/superpowers/plans/phase-6-tasks-1-12-evidence/`), 15 skills. `review-manual-topics` has two
real runtimes:

- `repository-claude` — enforces its "max 2 related topics" contract **deterministically**, via a
  real `TooManyRelatedTopicsError` in `plugins/sharepoint-agents-and-skills/scripts/
  review_manual_topics.py`. `EMPIRICALLY_OBSERVED` (code exists, reviewed).
- `native-sharepoint` — enforces the same contract only through agent instructions, **not
  deterministically**. Live-observed to exceed the cap (`DRIFT-CHECK.md`: `AMB-01` consulted 3 and
  7 related topics against an allowance of 2). `EMPIRICALLY_OBSERVED`, deployed to and evaluated
  against tenant `AG-CSB-INTRANET-DEV`, agent `CEIS-Pilot-Knowledge-Agent`.

**Account/tenant context:** `RESULT-PERM-01.md` shows the evaluation ran under a `gov.bc.ca`
account (`OWNER_EDITOR`, `Richard.Fremmerlid@gov.bc.ca`). This confirms **BC Government
user/account context** only. The tenant's cloud classification, compliance boundary, Protected B
authorization, regional category, and GCC/GCC High equivalence remain **`TENANT_UNKNOWN`** —
not inferred from this one evaluation file.

**Identity decision matrix (native SharePoint agent):**

| Identity role | Value | Evidence label |
|---|---|---|
| User-interaction identity | Delegated end-user (`OWNER_EDITOR`, etc.) | `EMPIRICALLY_OBSERVED` — `RESULT-PERM-01.md` |
| Deployment identity | `UNKNOWN` | not evidenced in the reviewed files |
| Retrieval identity | `UNKNOWN` | not evidenced in the reviewed files |
| Approval identity | `UNKNOWN` | not evidenced in the reviewed files |
| Publication identity | `UNKNOWN` | not evidenced in the reviewed files (publication path is plan-only, per §2) |

## 4. Prior Research Reused and Updated

**AI-Research files used:** all 40 substantive files across `microsoft-copilot-cowork/`,
`microsoft-copilot-studio/`, and `microsoft-m365-agents/` (full inventory and per-file disposition
in `prior-research-source-ledger.md`). External bundle for reviewer reference:
`temp/bundles/phase-7-prior-copilot-research/payload.md` (~108,647 tokens, 46 files including
this repo's own Phase 7 context — not committed, a temp/ working artifact).

**Findings still current (`BUNDLED_PRIMARY_SOURCE`, unresolved by this pass, not yet
`CURRENT_PRIMARY_SOURCE_VERIFIED`):** the architectural structure of Cowork's portability model
(format- vs. runtime-compatible, `viable-skills-summary.md` Claim 6); Copilot Studio's Dataverse-
solution-export-only versioning (`generative-orchestration.md` §9); the three lifecycle-
interception trigger names (`OnKnowledgeRequested`/`AI Response Generated`/`On Plan Complete`).

**Findings updated or superseded:** the AGAT Software regional-disablement claim
(`research/reviews/agat-sovereignty-identity.md`, 2026-03-18) is superseded by
`viable-skills-summary.md` v6's explicit retraction. The "4–6hr Dataverse refresh window" claim
(`research/reviews/gpt55-v1.md`) is superseded by its removal in `opus-v2.md`.

**Questions still unresolved (carried forward, not answered by this pass):** the Purview/Power-
Platform-DLP governance-engine mismatch (`learnings.md` L19–L20); whether a Custom/Dedicated
Environment actually changes the observed DLP-blocking behavior (`learnings.md` L23); whether this
project's own tenant shares the BC Government Shared Environment's compliance characteristics
observed in the hands-on Studio testing.

**What Phase 7 added rather than repeated:** the three-way baseline framing; the portability
classification applied to this repo's own workflow steps (Section 6 below); the decomposed
identity-field matrix (Section 3 above, Section 8 below); the corrected deterministic-vs-
instruction-level distinction using this repo's own Phase 6 code evidence (none of this existed in
the AI-Research corpus, which never analyzed this repo's own SharePoint-agent implementation).

## 5. Copilot Cowork — opportunities and limitations

**Opportunities:** intake conversation and workflow guidance are plausible `DIRECT_FIT`
(Elicitation Forms, `research/elicitation.md`, `BUNDLED_PRIMARY_SOURCE`); the Agent Builder's
Describe→Configure flow structurally resembles this repo's own `create-sub-agent` interview
pattern (`research/overview.md`, `BUNDLED_PRIMARY_SOURCE`).

**Limitations:** no local code execution — the extraction/rendering/validation pipeline cannot run
inside Cowork (`research/limitations.md`, `research/criticisms.md`, `BUNDLED_PRIMARY_SOURCE`); no
packaging, versioning, or reconciliation model — a skill is a single live-edited OneDrive file
(`research/schema-notes.md`, `research/how-to-build-custom-skills.md`); cannot edit files in place
or delete files (`research/cowork-limitations.md`); hard caps (50 skills/user, 1MB SKILL.md,
20-file/10MB companion limit — `REQUIRES_FRESHNESS_CHECK`); tenant enablement requires both
admin-enabled usage-based billing and explicit Anthropic-subprocessor opt-in
(`research/overview.md`).

**Tier classification:** the primary workflow is a shared, deterministic, team-owned tool, not
personal productivity — it reads as a Tier 2 ("Missing Middle") workload under
`viable-skills-summary.md`'s framework, which the source itself states is architecturally absent
in Cowork today (no native channel). `BUNDLED_PRIMARY_SOURCE`.

## 6. Copilot Studio — opportunities and limitations

**Opportunities:** Connected Agents provide typed Input/Output schema contracts for sub-agent
invocation — the closest native primitive to a callable, typed artifact
(`generative-orchestration.md` §8, `BUNDLED_PRIMARY_SOURCE`). Three lifecycle-interception points
exist as **candidate** control points, not established execution semantics for this workflow:

| Candidate trigger | Candidate use | Evidence label |
|---|---|---|
| `OnKnowledgeRequested` | Grounding-query shaping/filtering | `BUNDLED_PRIMARY_SOURCE` |
| `AI Response Generated` | Inspecting/modifying/redacting a generated response — **not** part of this workbench's own compile/render pipeline | `BUNDLED_PRIMARY_SOURCE` |
| `On Plan Complete` | Post-plan control point; suitability for publication handoff unverified | `BUNDLED_PRIMARY_SOURCE` |

**Limitations, empirically observed** (`agent-build-walkthrough.md`, 2026-06-20, BC Government
Shared Environment — `EMPIRICALLY_OBSERVED`, environment-scoped per `learnings.md` L23):
Message-node output is **not delivered verbatim** — the LLM reformats/enriches static text,
a direct risk for any validation/approval step needing exact text (Step 4); all knowledge-source
connector types were blanket-blocked by default DLP in this Default/Shared environment (Step 5);
channel/auth restricted to Teams/M365/SharePoint unless an Entra App Registration is manually
provisioned (Step 6). **Critical scoping caveat:** `learnings.md` L23 states this severe blocking
is characteristic of Power Platform **Default Environments** specifically and does not necessarily
apply to Custom/Dedicated Environments — untested here, `HYPOTHESIS_PENDING_HANDS_ON_VALIDATION`.

**Governance mismatch:** the same file/model/channel/user is Purview-governed and allowed in M365
Copilot Chat but Power-Platform-DLP-governed and blocked in Copilot Studio — the two policy
engines are not unified as of the source's own June 2026 dating (`learnings.md` L19–L20,
explicitly unresolved by the original researcher).

## 7. Copilot Studio agent/action/template-as-artifact model

Versioning exists only via exporting Dataverse solutions as compressed XML/JSON packages — no
native git-diff or PR-review workflow (`generative-orchestration.md` §9,
`BUNDLED_PRIMARY_SOURCE`). This is a structurally different artifact model from
`sharepoint-agents-and-skills`' git-tracked author → package → deploy → reconcile/drift-detect
workflow, not a superset or subset of it.

## 8. Overlap with `sharepoint-agents-and-skills`

No overlap in artifact lifecycle: neither Cowork nor Studio has a native reconcile-against-
deployed-state or drift-detection mechanism comparable to
`plugins/sharepoint-agents-and-skills/scripts/reconcile-deployed-skill.ps1` and
`drift_detection.py`. Identity comparison, per architecture (not generalized to a single Studio
identity mode — `generative-orchestration.md` §8 documents one OAuth/on-behalf-of connected-agent
pattern only):

| Identity role | Native SharePoint agent | Cowork | Copilot Studio |
|---|---|---|---|
| User-interaction identity | Delegated end-user (`EMPIRICALLY_OBSERVED`) | Delegated end-user Entra identity (`viable-skills-summary.md` Claim 7, `BUNDLED_PRIMARY_SOURCE`) | Delegated, via OAuth on-behalf-of for the one observed connected-agent pattern (`BUNDLED_PRIMARY_SOURCE`) — not established as Studio's only mode |
| Deployment identity | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` |
| Retrieval identity | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` — connector execution observed to require maker's own OAuth consent in one test (`agent-build-walkthrough.md` Step 5), not generalized further |
| Approval identity | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` |
| Publication identity | `UNKNOWN` (plan-only path) | `UNKNOWN` | `UNKNOWN` |

## 9. Potential integration patterns

Both platforms' only architecturally plausible role, if built, is Split-Runtime: platform as
conversational front-end/orchestrator, this repo's existing pipeline as deterministic execution
backend, SharePoint as content/grounding destination. Named trade-off dimensions requiring
workload-specific evidence before any pilot: identity/execution boundary (Section 8), state/
idempotency and OneDrive/Graph `etag` concurrency, approval placement, auditability, DLP
visibility, latency (`viable-skills-summary.md` cites 8–15s split-runtime vs. 2–3s native, but
flags this as needing workload-specific benchmarking — `SECONDARY_SOURCE_CLAIM`-adjacent, not a
verified figure), duplicate metering/hosting cost, and Protected B/ITSG-33 applicability (named
controls AC-4/SC-7/SI-7/AU-12 in `opus-v3.md`; tenant-applicability itself
`HYPOTHESIS_PENDING_HANDS_ON_VALIDATION` given `TENANT_UNKNOWN` per Section 3).

## 10. Capability-gap classification (this repo's own workflow steps)

| Workflow capability | Classification | Basis |
|---|---|---|
| Intake conversation / elicitation | `DIRECT_FIT` (Cowork), plausible (Studio) | `research/elicitation.md`; `agent-build-walkthrough.md` Step 3e |
| Workflow guidance / stepwise instruction | `DIRECT_FIT` both | `research/how-to-build-custom-skills.md` |
| Knowledge-grounded review | `ADAPTATION_REQUIRED`, contingent on connector/DLP posture | `agent-build-walkthrough.md` Step 5; `learnings.md` L21–L23 |
| Structured state management across steps | `ADAPTATION_REQUIRED` | no native state-carry mechanism described for either platform |
| DOCX/PDF extraction, deterministic rendering | `INCOMPATIBLE` (native) | `research/limitations.md`, `research/criticisms.md` |
| SharePoint deployment/reconciliation | `INCOMPATIBLE` (native); `ADAPTATION_REQUIRED` via external service | `generative-orchestration.md` §9 |
| Regression/validation evidence generation | `INCOMPATIBLE` (native) | no native equivalent found in either corpus |

(Classification method reused from `knowledge-plugins-analysis/README.md`'s 🟢/🟡/🔴 scheme and
the `plugin-analysis/*.md` verdict pattern — method only; those files' own third-party subjects
are not this repo's plugins and are not cited as findings here.)

## 11. Capability gaps requiring future platform access

- Whether Studio's DLP-blocking behavior actually differs in a Custom/Dedicated Environment
  (`learnings.md` L23) — untestable without that environment.
- Whether Cowork's stated tenant prerequisites (subprocessor opt-in, usage-based billing) would,
  once enabled, actually surface the capabilities documented — untestable while
  `NOT_ENABLED_IN_TENANCY`.
- All `UNKNOWN` identity-matrix cells in Sections 3 and 8 — require either live testing or
  additional repository/tenant evidence not currently available.
- Whether Message-node non-verbatim behavior can be disabled at the topic level
  (`agent-build-walkthrough.md` Step 4 notes this as unconfirmed).

## 12. Future pilot hypotheses (not authorized, not scoped as work)

- **Studio, contingent on Dedicated Environment access:** a bounded pilot testing whether a
  Dedicated Environment resolves the Default-Environment DLP blocking, scoped to read-only
  knowledge-source grounding only — would directly resolve the largest open
  `HYPOTHESIS_PENDING_HANDS_ON_VALIDATION` item in this memo.
- **Cowork, contingent on tenant enablement:** a bounded pilot testing only the intake-conversation
  step as a Split-Runtime front-end, with all pipeline execution remaining external — would test
  the Tier 2 "Missing Middle" gap directly rather than assuming it.
- Neither hypothesis is authorized by this memo; both require separate approval per the base
  spec's Section 8/11 exit criteria before any implementation.

## 13. Disposition — Copilot Cowork

**`REMAIN_RESEARCH`.**

Rationale: a specific architectural limitation (no packaging/versioning/reconciliation model, no
local execution) is well-documented and consistent across independent sources
(`research/limitations.md`, `research/criticisms.md`, `research/schema-notes.md`,
`viable-skills-summary.md`), which argues against `JUSTIFIED_FOR_FUTURE_PILOT` for anything beyond
the narrow intake-conversation front-end role. However, `NOT_ENABLED_IN_TENANCY` means no finding
in this memo has been hands-on validated, and several quantitative limits are themselves
`REQUIRES_FRESHNESS_CHECK`. This is not `NO_ADDITIONAL_VALUE_DEMONSTRATED` (that would overstate
confidence given zero hands-on access) and not `BLOCKED_PENDING_PLATFORM_ACCESS` (a documentation-
only conclusion about the pipeline-execution gap was in fact reachable). `REMAIN_RESEARCH` is the
accurate label: the one plausible narrow role (intake front-end) is a real but unconfirmed
hypothesis (Section 12), not yet a documented advantage over the existing workbench.

## 14. Disposition — Copilot Studio

**`BLOCKED_PENDING_PLATFORM_ACCESS`.**

Rationale: the single largest open question — whether the observed Default-Environment DLP
blocking (`agent-build-walkthrough.md` Step 5, `learnings.md` L21–L23) is specific to that
environment type or would also affect whatever environment this project could actually provision —
cannot be answered from documentation alone; `learnings.md` L23 itself says so. The Connected
Agents artifact/identity findings (Sections 7–8) are real and documented, but their practical value
for this workflow is contingent on first resolving the environment-type question, which requires
the currently-unavailable Dedicated Environment. This is not `NO_ADDITIONAL_VALUE_DEMONSTRATED`
(real candidate capabilities exist — Section 6) and not yet `JUSTIFIED_FOR_FUTURE_PILOT` (no
capability advantage has been confirmed usable given the access blocker). Once environment access
exists, this disposition should be revisited using the bounded pilot in Section 12.
