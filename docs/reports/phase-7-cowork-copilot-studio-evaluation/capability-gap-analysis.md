# Phase 7 Capability-Gap Analysis — Copilot Cowork and Copilot Studio

> **Status:** Desk research plus a focused live-source verification pass, per
> `docs/superpowers/specs/2026-08-03-phase-7-cowork-copilot-studio-desk-research-design.md`. No
> live build, tenant change, or environment creation occurred. This is a **supporting artifact**
> to the formal decision record, `desk-research-evidence-memo.md`. Evidence-type labels and
> freshness statuses are used exactly as defined in the design (Sections 2 and 4a) — the two
> dimensions are kept in separate fields, never conflated. Full source provenance:
> `prior-research-source-ledger.md`. Full current-source verification detail:
> `current-source-verification-record.md`.

## 1. Primary workflow and owner

The interactive document-conversion and publication workflow for the SharePoint Knowledge
Workbench: intake → document selection → output formats → destinations → agent grounding →
validation → human approval. **Owner:** Richard Fremmerlid. Success criterion: a "meaningful
advantage" is a specific, documented capability that the existing workbench and native SharePoint
agent do not already provide for this workflow — not general platform capability.

## 2. Existing Phase 1–6 baseline

Four core domain plugins chained into a real `analyze → confirm → convert → render` pipeline,
proven end-to-end on the CEIS Manual pilot with a byte-identical golden-master reproduction.
`workbench-setup` provides the cross-cutting connection/workflow-profile layer.
`sharepoint-content-publication` produces human-actionable publication plans only — no automated
tenant write path exists yet. (Evidence: `start-here.md`; not re-derived here.)

## 3. SharePoint-agent baseline (the third comparison point)

`plugins/sharepoint-agents-and-skills` (Phase 6, Tasks 0–12; evidence at
`docs/superpowers/plans/phase-6-tasks-1-12-evidence/`), 15 skills. `review-manual-topics` has two
real runtimes:

- `repository-claude` — enforces its "max 2 related topics" contract programmatically. The
  contract's existence is `REPOSITORY_VERIFIED` (`TooManyRelatedTopicsError` in
  `scripts/review_manual_topics.py`); its actual enforcement is `EMPIRICALLY_OBSERVED` — a real
  passing test, `test_more_than_two_related_topics_is_rejected`
  (`plugins/sharepoint-agents-and-skills/tests/unit/test_review_manual_topics.py`), executes
  `resolve_topic()` against a fixture with three related topics and asserts the exception is
  raised.
- `native-sharepoint` — enforces the same contract only through agent instructions, **not
  programmatically**. `EMPIRICALLY_OBSERVED` to exceed the cap live (`DRIFT-CHECK.md`: `AMB-01`
  consulted 3 and 7 related topics against an allowance of 2), deployed to tenant
  `AG-CSB-INTRANET-DEV`, agent `CEIS-Pilot-Knowledge-Agent`.

**Account/tenant context:** `RESULT-PERM-01.md` shows the evaluation ran under a `gov.bc.ca`
account (`OWNER_EDITOR`, `Richard.Fremmerlid@gov.bc.ca`). This confirms **BC Government
user/account context** only (`EMPIRICALLY_OBSERVED`). The tenant's cloud classification,
compliance boundary, Protected B authorization, regional category, and GCC/GCC High equivalence
remain **`TENANT_UNKNOWN`** — not inferred from this one evaluation file.

**Identity decision matrix (native SharePoint agent):**

| Identity role | Value | Evidence type |
|---|---|---|
| User-interaction identity | Delegated end-user (`OWNER_EDITOR`, etc.) | `EMPIRICALLY_OBSERVED` |
| Deployment identity | `UNKNOWN` | not evidenced in the reviewed files |
| Retrieval identity | `UNKNOWN` | not evidenced in the reviewed files |
| Approval identity | `UNKNOWN` | not evidenced in the reviewed files |
| Publication identity | `UNKNOWN` | not evidenced (publication path is plan-only, per §2) |

## 4. Prior Research Reused and Updated

**AI-Research files inventoried/reviewed:** all 40 substantive files across
`microsoft-copilot-cowork/` (including all **11** `plugin-analysis/*.md` files — corrected from an
earlier miscount of 9), `microsoft-copilot-studio/`, and `microsoft-m365-agents/`. **Not all were
used as findings** — full per-file disposition, including which contributed no reused conclusion,
is in `prior-research-source-ledger.md`.

**Findings still current or newly current-verified:** the general architectural structure of
Cowork's portability model (format- vs. runtime-compatible), Studio's lifecycle-interception
trigger *names* (now `CURRENT_PRIMARY_SOURCE_VERIFIED` — see Section 6), and Connected Agents I/O
contracts (now `CURRENT_PRIMARY_SOURCE_VERIFIED`).

**Findings updated by this phase's live verification pass** (full detail in
`current-source-verification-record.md`):
1. Copilot Studio agents now receive an automatic, dedicated Microsoft Entra Agent ID by default
   (July 2026 rollout) — the bundle's "delegated-identity-only" framing for Studio is outdated.
2. Copilot Studio ALM supports Git-based CI/CD tooling (Azure DevOps, GitHub Actions) — the
   bundle's "no git integration at all" framing is too strong.
3. Anthropic is enabled as a Cowork subprocessor **by default** for most tenants since 2026-01-07
   (EU/EFTA/UK excepted) — the bundle's "explicit opt-in required" framing is outdated for most
   regions; this tenant's own regional category remains `TENANT_UNKNOWN`.
4. Cowork's "no local execution" claim has a scoped exception: Excel-context skills execute real
   JavaScript against Office.js — not applicable to this workflow's own operations, but the
   absolute framing was too strong.

**Findings updated or superseded (prior-research-internal):** the AGAT Software regional-
disablement claim is superseded by `viable-skills-summary.md` v6's retraction. The "4–6hr Dataverse
refresh window" claim is superseded by its removal in `opus-v2.md`.

**Questions still unresolved (carried into the future-validation backlog, Section 12):** the
Purview/Power-Platform-DLP governance-engine mismatch; whether a Custom/Dedicated Environment
actually changes the observed DLP-blocking behavior; whether this project's own tenant shares the
BC Government Shared Environment's compliance characteristics; whether the Cowork product surface
(distinct from Studio) has adopted Entra Agent ID.

## 5. Copilot Cowork — opportunities and limitations

**Opportunities:** intake conversation and workflow guidance — `BUNDLED_RESEARCH_SYNTHESIS`
(`research/elicitation.md`), corroborated by `agent-build-walkthrough.md`'s topic-routing
observation; the Agent Builder's Describe→Configure flow structurally resembles this repo's own
`create-sub-agent` interview pattern (`BUNDLED_RESEARCH_SYNTHESIS`, `research/overview.md`).

**Limitations:** no execution of scripts/agents/hooks/bin for this workflow's kind of operations
(`BUNDLED_RESEARCH_SYNTHESIS`, `research/limitations.md`, `research/criticisms.md`; the Excel-JS
exception noted in Section 4 does not apply here); no packaging, versioning, or reconciliation
model — a skill is a single live-edited OneDrive file (`BUNDLED_RESEARCH_SYNTHESIS`,
`research/schema-notes.md`); cannot edit files in place or delete files
(`BUNDLED_RESEARCH_SYNTHESIS`, `research/cowork-limitations.md`); hard caps (50 skills/user, 1MB
SKILL.md, 20-file/10MB companion limit — the companion-file cap is now `CURRENT_PRIMARY_SOURCE_
VERIFIED`, others `REQUIRES_FRESHNESS_CHECK`); tenant enablement requires usage-based billing and,
for most regions, a default-on (not default-off) Anthropic-subprocessor setting
(`CURRENT_PRIMARY_SOURCE_VERIFIED`, Section 4 item 3).

**Tier classification:** the primary workflow is a shared, deterministic, team-owned tool, not
personal productivity — it reads as a Tier 2 ("Missing Middle") workload under
`viable-skills-summary.md`'s framework (`BUNDLED_RESEARCH_SYNTHESIS`), which the source states is
architecturally absent in Cowork today; **not identified in the reviewed corpus** does not
establish that no such channel exists at all, only that this review did not find one.

## 6. Copilot Studio — opportunities and limitations

**Opportunities:** Connected Agents provide typed Input/Output schema contracts for sub-agent
invocation — the closest native primitive to a callable, typed artifact
(`CURRENT_PRIMARY_SOURCE_VERIFIED`: [Add other agents overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-add-other-agents)).
Three lifecycle-interception points are `CURRENT_PRIMARY_SOURCE_VERIFIED` to exist, but remain
**candidate** control points for this specific workflow, not established execution semantics:

| Candidate trigger | Candidate use | Evidence type |
|---|---|---|
| `OnKnowledgeRequested` | Grounding-query shaping/filtering | `CURRENT_PRIMARY_SOURCE_VERIFIED` (trigger exists); candidate use for this workflow unverified |
| `AI Response Generated` | Inspecting/modifying/redacting a generated response — **not** part of this workbench's own compile/render pipeline | `CURRENT_PRIMARY_SOURCE_VERIFIED` (trigger exists); candidate use unverified |
| `Plan Complete` (design's earlier "On Plan Complete" is a naming variant, same trigger) | Post-plan control point; suitability for publication handoff unverified | `CURRENT_PRIMARY_SOURCE_VERIFIED` (trigger exists); candidate use unverified |

**Limitations, empirically observed** (`agent-build-walkthrough.md`, 2026-06-20, BC Government
Shared Environment — `EMPIRICALLY_OBSERVED`, environment-scoped per `learnings.md` L23): Message-
node output is **not delivered verbatim** — a direct risk for any validation/approval step needing
exact text; all knowledge-source connector types were blanket-blocked by default DLP in this
Default/Shared environment (corroborated as a real mechanism by
`CURRENT_PRIMARY_SOURCE_VERIFIED` Power Platform DLP documentation, though the specific
Default-vs-Dedicated distinction remains `HYPOTHESIS_PENDING_HANDS_ON_VALIDATION`); channel/auth
restricted to Teams/M365/SharePoint unless an Entra App Registration is manually provisioned.

**Governance mismatch:** the same file/model/channel/user is Purview-governed and allowed in M365
Copilot Chat but Power-Platform-DLP-governed and blocked in Copilot Studio — the two policy
engines are not unified as of the source's own June 2026 dating (`EMPIRICALLY_OBSERVED`,
`learnings.md` L19–L20, explicitly unresolved by the original researcher).

**Identity — corrected by this phase's verification:** Copilot Studio agents now receive an
automatic, dedicated Entra Agent ID by default (`CURRENT_PRIMARY_SOURCE_VERIFIED`, July 2026
rollout) — see Section 8's identity matrix.

## 7. Copilot Studio agent/action/template-as-artifact model

Versioning is primarily via exporting Dataverse solutions as compressed packages, **and** Git-based
CI/CD tooling (Azure DevOps, GitHub Actions for Power Platform) is a supported ALM path
(`CURRENT_PRIMARY_SOURCE_VERIFIED`, corrects the bundle's "no git integration at all" framing).
This remains a structurally different artifact model from `sharepoint-agents-and-skills`' plain
markdown-in-git author → package → deploy → reconcile/drift-detect workflow — the Studio path
wraps Dataverse-solution packages rather than tracking human-readable source files directly — not
a superset or subset of the repo's own model.

## 8. Overlap with `sharepoint-agents-and-skills`

**No comparable mechanism was identified during this review** for a native reconcile-against-
deployed-state or drift-detection capability matching
`plugins/sharepoint-agents-and-skills/scripts/reconcile-deployed-skill.ps1` and
`drift_detection.py`, in either platform. Identity comparison, per architecture, corrected per
Section 4/6's verification findings:

| Identity role | Native SharePoint agent | Cowork | Copilot Studio |
|---|---|---|---|
| Agent/service identity | not evidenced as a distinct concept in the sources reviewed | Delegated end-user Entra identity per `viable-skills-summary.md` Claim 7 (`BUNDLED_RESEARCH_SYNTHESIS`, unresolved by this pass) | Dedicated Entra Agent ID, automatic for new agents since the July 2026 rollout (`CURRENT_PRIMARY_SOURCE_VERIFIED`) — this is the agent's own service-principal identity, distinct from who deploys it |
| Deployment/publisher identity | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` — current sources establish the agent *has* a dedicated identity, not *who/what* performs the publish/deploy action; not conflated with the agent/service identity row above |
| Connector/action identity | `UNKNOWN` | `UNKNOWN` | On-Behalf-Of (delegated to the invoking user) by default for most connectors; Client Credentials Flow available for the documented autonomous-agent pattern, using the agent's own identity (`CURRENT_PRIMARY_SOURCE_VERIFIED`) |
| Retrieval identity | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` for this workflow's specific knowledge-source mechanism — the maker-credential OAuth consent observed in `agent-build-walkthrough.md` Step 5 is one connector-authentication instance, not generalized to a platform-wide retrieval-identity rule |
| User-interaction identity | Delegated end-user (`EMPIRICALLY_OBSERVED` — `RESULT-PERM-01.md`) | Delegated end-user, per `viable-skills-summary.md` Claim 7 (`BUNDLED_RESEARCH_SYNTHESIS`) | Delegated end-user, consistent with the On-Behalf-Of connector-identity finding above (`CURRENT_PRIMARY_SOURCE_VERIFIED`) |
| Approval identity | `UNKNOWN` | `UNKNOWN` | `UNKNOWN` — not addressed by the sources reviewed |
| Publication identity | `UNKNOWN` (plan-only path) | `UNKNOWN` | `UNKNOWN` — not addressed by the sources reviewed |

The most consequential correction in this pass is scoped precisely: Copilot Studio now has a
genuine dedicated **agent/service identity** primitive wired in by default (closing part of the
"Primitive Gap" the bundle described), confirmed by current sources. This does **not** by itself
establish who deploys the agent, which identity performs a given connector's retrieval action
beyond the one On-Behalf-Of/Client-Credentials distinction actually documented, or who approves or
publishes — those remain independently `UNKNOWN` rather than inferred from the agent-identity
finding. This has not been confirmed for Cowork specifically.

## 9. Potential integration patterns

Split-Runtime is **the principal integration pattern identified by this research**, not
established as the *only* architecturally possible one — platform as conversational front-end/
orchestrator, this repo's existing pipeline as execution backend, SharePoint as content/grounding
destination. Named trade-off dimensions requiring workload-specific evidence before any pilot:
identity/execution boundary (Section 8, now partially resolved for Studio), state/idempotency and
OneDrive/Graph `etag` concurrency, approval placement, auditability, DLP visibility, latency
(`BUNDLED_RESEARCH_SYNTHESIS`, `viable-skills-summary.md` cites 8–15s split-runtime vs. 2–3s
native but flags this as needing workload-specific benchmarking), duplicate metering/hosting cost,
and Protected B/ITSG-33 applicability (named controls AC-4/SC-7/SI-7/AU-12,
`BUNDLED_RESEARCH_SYNTHESIS`; tenant-applicability itself
`HYPOTHESIS_PENDING_HANDS_ON_VALIDATION` given `TENANT_UNKNOWN`).

## 10. Capability-gap classification (this repo's own workflow steps, per platform)

| Workflow capability | Existing baseline | Cowork classification | Cowork evidence/basis | Copilot Studio classification | Studio evidence/basis | Unresolved validation |
|---|---|---|---|---|---|---|
| Intake conversation / elicitation | Not present today | `DIRECT_FIT` | `BUNDLED_RESEARCH_SYNTHESIS`, `research/elicitation.md` | `DIRECT_FIT` | `EMPIRICALLY_OBSERVED`, `agent-build-walkthrough.md` Step 3e | Neither hands-on tested for this workflow's specific prompts |
| Workflow guidance / stepwise instruction | Present (CLI/agent session) | `DIRECT_FIT` | `SECONDARY_SOURCE_CLAIM`, `research/how-to-build-custom-skills.md` | `DIRECT_FIT` | `EMPIRICALLY_OBSERVED`, Instructions-field finding | Neither hands-on tested |
| Knowledge-grounded review | Present (native SharePoint agent) | `ADAPTATION_REQUIRED` | tenant enablement gate, Section 5 | `ADAPTATION_REQUIRED` | `EMPIRICALLY_OBSERVED` DLP-block finding, environment-scoped | Whether a Dedicated Environment resolves the block — untested |
| Structured state management across steps | Present (pipeline state) | `ADAPTATION_REQUIRED` | no comparable mechanism identified during this review | `ADAPTATION_REQUIRED` | no comparable mechanism identified during this review | Neither platform's state model reviewed in depth |
| DOCX/PDF extraction, deterministic rendering | Present (Phase 1–6 pipeline) | `INCOMPATIBLE` | `BUNDLED_RESEARCH_SYNTHESIS`, `research/limitations.md`/`criticisms.md` | `INCOMPATIBLE` | no native execution path identified in the sources reviewed | Not applicable — external execution is the design's own assumption |
| SharePoint deployment/reconciliation | Present (`sharepoint-agents-and-skills`) | `INCOMPATIBLE` natively; `ADAPTATION_REQUIRED` via external service | `BUNDLED_RESEARCH_SYNTHESIS`, `research/schema-notes.md` | `INCOMPATIBLE` natively; `ADAPTATION_REQUIRED` via external service | `CURRENT_PRIMARY_SOURCE_VERIFIED`, Section 7 ALM finding | Neither has a native reconcile/drift-detect equivalent |
| Regression/validation evidence generation | Present (`native-sharepoint-results/`) | `INCOMPATIBLE` | no comparable mechanism identified during this review | `INCOMPATIBLE` | no comparable mechanism identified during this review | Neither platform's evaluation tooling reviewed |

(Classification method reused from `knowledge-plugins-analysis/README.md`'s 🟢/🟡/🔴 scheme and
the `plugin-analysis/*.md` verdict pattern — method only; those files' own third-party subjects
are not cited as findings here. Only `DIRECT_FIT` / `ADAPTATION_REQUIRED` / `INCOMPATIBLE` are
used — no other classification value.)

## 11. Capability gaps requiring future platform access

- Whether Studio's DLP-blocking behavior actually differs in a Custom/Dedicated Environment
  (`learnings.md` L23) — untestable without that environment.
- Whether Cowork's tenant enablement (now understood to be default-on for most regions per Section
  4) actually surfaces the documented capabilities in this specific tenant — untestable while
  `NOT_ENABLED_IN_TENANCY`.
- All `UNKNOWN` identity-matrix cells in Sections 3 and 8 (approval identity, publication identity
  for both platforms; Cowork's deployment/retrieval identity) — require either live testing or
  additional evidence not currently available.
- Whether Message-node non-verbatim behavior can be disabled at the topic level — unconfirmed by
  either the bundle or this pass's live-source check.
- Whether the Cowork product surface has adopted an Entra-Agent-ID-equivalent identity model —
  not found in this pass.

## 12. Future pilot hypotheses (not authorized, not scoped as work)

- **Studio, contingent on Dedicated Environment access:** a bounded pilot testing whether a
  Dedicated Environment resolves the Default-Environment DLP blocking, scoped to read-only
  knowledge-source grounding only.
- **Cowork, contingent on tenant enablement:** a bounded pilot testing only the intake-conversation
  step as a Split-Runtime front-end, with all pipeline execution remaining external.
- Neither hypothesis is authorized by this memo; both require separate approval per the base
  spec's Section 8/11 exit criteria before any implementation.

## 13. Disposition — Copilot Cowork

**`REMAIN_RESEARCH`.**

Rationale: a specific limitation (no packaging/versioning/reconciliation model, no execution
capability relevant to this workflow's operations) is consistently found across independent
internal-synthesis sources, which argues against `JUSTIFIED_FOR_FUTURE_PILOT` for anything beyond
a narrow intake-conversation front-end role. However, `NOT_ENABLED_IN_TENANCY` means no finding
has been hands-on validated, several quantitative limits remain `REQUIRES_FRESHNESS_CHECK`, and
this phase's verification pass corrected the tenant-enablement framing (Section 4 item 3) in a way
that makes future access more plausible than the original bundle suggested. This is not
`NO_ADDITIONAL_VALUE_DEMONSTRATED` (would overstate confidence given zero hands-on access) and not
`BLOCKED_PENDING_PLATFORM_ACCESS` (documentation-only conclusions about the execution gap were in
fact reachable, including via live-source verification this phase). `REMAIN_RESEARCH` is the
accurate label — the narrow intake-front-end role is a real but unconfirmed hypothesis (Section
12), not yet a documented advantage.

## 14. Disposition — Copilot Studio

**`REMAIN_RESEARCH`** (revised from a prior draft's `BLOCKED_PENDING_PLATFORM_ACCESS`).

Rationale: per the design's Section 5 correction, `BLOCKED_PENDING_PLATFORM_ACCESS` is reserved
for cases where the access blocker prevents forming even a documentation-only conclusion. This
phase's live-source verification pass shows that was not the case here — several substantive,
current-source-verified conclusions were reached (Section 8's identity-matrix update; Section 7's
ALM/versioning correction; Section 6's confirmed lifecycle-trigger existence). What remains
genuinely blocked is not the documentation-level analysis but the **practical suitability
question**: whether the observed Default-Environment DLP blocking would also affect whatever
environment this project could actually provision, which `learnings.md` L23 itself says cannot be
answered without a Dedicated Environment. That is squarely a "documentation identifies plausible
value, hands-on evidence is needed" situation — `REMAIN_RESEARCH`, not
`BLOCKED_PENDING_PLATFORM_ACCESS`. Once environment access exists, revisit using the bounded pilot
in Section 12.
