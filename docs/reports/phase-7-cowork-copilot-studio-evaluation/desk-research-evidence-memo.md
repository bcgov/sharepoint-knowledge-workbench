# Phase 7 Desk-Research Evidence Memo — Copilot Cowork and Copilot Studio

> **This is the formal Phase 7 decision record**, per
> `docs/superpowers/specs/2026-08-03-phase-7-cowork-copilot-studio-desk-research-design.md`
> Section 4. It consolidates and cites three supporting artifacts rather than repeating their
> content:
> - `prior-research-source-ledger.md` — per-source provenance, evidence type, freshness status
> - `capability-gap-analysis.md` — full working analysis, capability classification, both dispositions with rationale
> - `current-source-verification-record.md` — this phase's focused live-documentation verification
>
> No live build, tenant change, or environment creation occurred.

## 1. Primary use case, owner, success criteria

Interactive document-conversion and publication workflow: intake → document selection → output
formats → destinations → agent grounding → validation → human approval. **Owner:** Richard
Fremmerlid. "Meaningful advantage" means a specific, documented capability the existing workbench
and native SharePoint agent do not already provide for this workflow.

## 2. Baseline

Three-way, not two-way: (a) the Phase 1–6 repo/Claude workbench pipeline; (b) the native
SharePoint agent implementation, `plugins/sharepoint-agents-and-skills` (Phase 6, Tasks 0–12); (c)
each candidate platform. Full detail: `capability-gap-analysis.md` Sections 2–3.

## 3. Cowork — summary

No packaging/versioning/reconciliation model exists; execution relevant to this workflow's
operations (extraction/rendering/validation) is not supported. Tenant status:
`NOT_ENABLED_IN_TENANCY` / `LIVE_EVALUATION_BLOCKED` (access status, kept separate from the
capability finding above). This phase's live-source verification corrected the tenant-enablement
framing: Anthropic is default-on for most regions since 2026-01-07, not admin opt-in as the prior
research stated — see `current-source-verification-record.md` item 7. Full detail:
`capability-gap-analysis.md` Section 5.

## 4. Copilot Studio — summary

Connected Agents provide a real typed Input/Output artifact primitive
(`CURRENT_PRIMARY_SOURCE_VERIFIED`); three lifecycle-interception triggers exist and are
confirmed current, but remain candidate control points for this specific workflow, not
established semantics. Tenant status: `ACCESS_CONFIRMED` / `DEDICATED_ENVIRONMENT_NOT_AVAILABLE` /
`LIVE_BUILD_AND_VALIDATION_BLOCKED`. This phase's verification found the single most consequential
update in the whole research effort: Studio agents now receive a dedicated Entra Agent ID by
default (July 2026 rollout) — the prior research's "delegated-identity-only" framing is outdated
for Studio. Full detail: `capability-gap-analysis.md` Section 6–8.

## 5. Agent/skill-as-artifact comparison (Section 3 of the design)

Studio's artifact model remains structurally different from `sharepoint-agents-and-skills`' plain
markdown-in-git model — Dataverse-solution-package-centric, though Git-based CI/CD is a supported
ALM path (a correction to the prior research's "no git integration" framing). No native reconcile-
against-deployed-state or drift-detection equivalent was identified in either platform. Full
detail: `capability-gap-analysis.md` Section 7–8.

## 6. Capability classification

Per-platform `DIRECT_FIT` / `ADAPTATION_REQUIRED` / `INCOMPATIBLE` table for this workflow's own
steps: `capability-gap-analysis.md` Section 10.

## 7. What would justify a future pilot

- **Cowork:** a bounded pilot scoped to intake-conversation only, as a Split-Runtime front-end,
  contingent on tenant enablement.
- **Copilot Studio:** a bounded pilot testing whether a Dedicated Environment resolves the
  observed Default-Environment DLP blocking, scoped to read-only grounding, contingent on
  environment access.
- Neither is authorized here. Full detail: `capability-gap-analysis.md` Section 12.

## 8. Future hands-on-validation backlog

Every `HYPOTHESIS_PENDING_HANDS_ON_VALIDATION`-tagged finding: whether a Dedicated Environment
changes Studio's DLP behavior; whether Cowork's tenant prerequisites, once enabled, surface the
documented capabilities in this specific tenant; all `UNKNOWN` identity-matrix cells (approval and
publication identity for both platforms; Cowork's deployment/retrieval identity; whether Cowork
itself has adopted an Entra-Agent-ID-equivalent model); whether Message-node non-verbatim behavior
can be disabled at the topic level. Full list: `capability-gap-analysis.md` Section 11.

## 9. Dispositions

- **Copilot Cowork: `REMAIN_RESEARCH`.**
- **Copilot Studio: `REMAIN_RESEARCH`** (revised from an earlier draft's
  `BLOCKED_PENDING_PLATFORM_ACCESS` — that disposition's strict definition, per the design's
  Section 5 correction, does not fit here because documentation-only conclusions were in fact
  reachable, including via this phase's live-source verification).

Full rationale for both: `capability-gap-analysis.md` Sections 13–14.

## 10. Exit criteria check

- [x] Evidence memo written and committed at this path.
- [x] Both targets have a disposition, each traceable to specific documented findings and the
  three-way baseline.
- [x] Every substantive finding in the supporting artifacts tagged with an evidence-type label
  from the corrected seven-value scheme, kept separate from freshness status.
- [x] Platform-access status and capability conclusions are not conflated.
- [x] No implementation, environment, or tenant action taken.
- [x] No instruction-level contract described as deterministic without a cited programmatic
  enforcement mechanism (repository-claude's cap is `REPOSITORY_VERIFIED`/`EMPIRICALLY_OBSERVED`
  via a real passing test; native-sharepoint's is explicitly not).
- [x] No single observed Studio identity pattern generalized into a platform-wide identity model
  (the identity matrix, Section 8 of `capability-gap-analysis.md`, carries deployment/retrieval/
  user-interaction/approval/publication as separate fields, several still `UNKNOWN`).
- [x] Focused current-primary-source verification performed against the claims material to the
  two dispositions (`current-source-verification-record.md`), per the design's Section 7 method
  requirement.
