# Phase 3–5 Dependency-Status Map — Phase 3.0 Stage 3.0.3.2

**Deliverable for:** `docs/vision/master-initiative-plan-workstreams-and-phases.md`, Stage 3.0.3.2.
**Companion to:** `docs/research/tenant-capability-report.md` (Stage 3.0.3.1).
**Decision owner:** initiative technical lead, with tenant-admin sign-off required on every row
marked `CONFIRMED_BLOCKED` below (per the plan's Stage 3.0.3.2 decision-owner assignment — none
are marked that way in this map; see the "no hard blocks" note at the end).

Each row traces a Phase 3, 4, or 5 entry-gate dependency to the specific probe result it rests on.
Status values: `CONFIRMED_AVAILABLE`, `CONFIRMED_BLOCKED`, `NEEDS_ESCALATION` (a specific person/role
must resolve it), `DEFERRED_UNTIL_EVIDENCE` (a specific future probe would resolve it).

## Phase 3 — Governed SharePoint Knowledge Pilot

| Dependency | Traced to | Status | Evidence |
|---|---|---|---|
| `AgentAssets`/document-library existence as a publication target | Probe 1 (Stage 3.0.2.1) | `CONFIRMED_AVAILABLE` | `AgentAssetsLibrary.Exists: Observed`; any document library (not only `AgentAssets`) can host a `.agent` file, per the write-based §2 finding |
| Write-principal / permission model for the pilot library | Probe 1 (Stage 3.0.2.1) | `NEEDS_ESCALATION` | `AgentAssetsLibrary.RoleAssignments: Forbidden` — requires Manage Permissions/Full Control or tenant-admin confirmation; owner: tenant SharePoint admin |
| Metadata schema for the pilot library (Subphase 3.1's schema-mapping work) | Probe 5 (Stage 3.0.2.5) | `DEFERRED_UNTIL_EVIDENCE` | Only one field type (`Note`) exercised; `SiteFields`/`ContentTypes` captured but not synthesized against a real planned schema — needs a dedicated probe once Subphase 3.1 defines required columns |
| Package-only deployment (file/library write mechanics) | Probes 1, 3 (Stages 3.0.2.1, 3.0.2.3) | `CONFIRMED_AVAILABLE` | `Add-PnPFile`/`Resolve-PnPFolder` confirmed scriptable for recursive multi-file upload (348-file real CEIS output uploaded successfully) even under a manage-only app registration |
| Publication reconciliation/rollback (Subphase 3.3) | not directly probed | `DEFERRED_UNTIL_EVIDENCE` | No probe in this session tested update-in-place, versioning-based rollback, or drift detection against a previously-published library; Subphase 3.3 needs its own dry-run before this can be marked available |
| Native Markdown rendering as the pilot's display mechanism | Probe 4 (Stage 3.0.2.4) | `CONFIRMED_AVAILABLE` | Real rendered CEIS output (25/26 topic pages + 111 images) confirmed rendering correctly in SharePoint's built-in Markdown viewer, including working relative-link navigation |
| Modern-page (`.aspx`) publishing as an alternative Renderer target | Phase 3.0 §15 (ASPX experiment, adjacent to the five formal probes) | `CONFIRMED_BLOCKED` (raw upload) / `CONFIRMED_AVAILABLE` (supported API) | Raw `.aspx` upload to Site Pages via `Add-PnPFile`: `Access denied` (confirmed platform boundary, not a permissions gap — same account succeeded at every other write probe). Supported alternative `Add-PnPPage` + `Add-PnPPageTextPart`: confirmed working, user-screenshot-verified rendering of heading/list/first image. **Not currently on Phase 3's critical path** — Phase 3 targets library-file publishing, not page-based publishing (see Full Traceability Matrix row "Multi-format rendering / non-SharePoint targets") |
| Oversharing/discoverability risk (Stage 3.4.2) | Probe 1's `RoleAssignments` gap + `RestrictedContentDiscovery` | `NEEDS_ESCALATION` | Both role-assignment enumeration and Restricted Content Discovery status returned `Forbidden`, requiring SharePoint Administrator role — Stage 3.4.2's discoverability test cannot be fully evidenced without tenant-admin participation |
| Governed write identity for authorized-write deployment (vs. package-only) | Probe 3 (Stage 3.0.2.3) | `DEFERRED_UNTIL_EVIDENCE` | Both tested creation/write paths used a single delegated user account; no service-principal/automation-account write path has been tested or approved |

## Phase 4 — Native SharePoint Skills Pilot

| Dependency | Traced to | Status | Evidence |
|---|---|---|---|
| `SKILL.md` authoring availability on this ring | Probe 2 (Stage 3.0.2.2) | `CONFIRMED_AVAILABLE` | Eight custom `SKILL.md` variants authored and uploaded successfully via `Add-PnPFile`; no dedicated PnP cmdlet needed |
| Skill schema (frontmatter + body sections) | Probe 2 (Stage 3.0.2.2) | `CONFIRMED_AVAILABLE` | Reverse-engineered schema documented in `research-summary...md` §5 and Technical Mechanics §4, cross-checked against one real pre-existing skill (`review-manual-topics/SKILL.md`) |
| Skill discovery by an agent without explicit reference | Probe 2 (Stage 3.0.2.2) | `PROVISIONAL` | Confirmed for one tested custom agent, one site, one trigger phrase — NOT confirmed across agents, sites, or competing-trigger scenarios (external-review correction #2); Priority 3 in the follow-up backlog targets this gap |
| Output-format enforcement (a skill's `## Output format` section) | Probe 2 (Stage 3.0.2.2), §6-7 | `CONFIRMED_BLOCKED` (as a hard contract) | JSON-schema requests honored most reliably; custom delimiter templates frequently ignored; externally-referenced template files not read literally (hallucination risk). Candidate skills for Phase 4 should assume best-effort formatting, not enforced contracts, unless Priority 4's follow-up isolates a working pattern |
| Write-action skills (e.g. list-item creation via a skill) | `research-summary...md` §8 | `CONFIRMED_BLOCKED` (tested invocation path only) | Agent consistently and correctly self-reported inability to create/modify list items or documents; independently verified via PnP that no item was silently created. Per external-review correction #1, this is a `CONFIRMED_TENANT_OBSERVATION` for the tested chat-pane invocation path only, not a universal platform boundary — Priority 2 in the follow-up backlog targets other invocation surfaces |

## Phase 5 — SharePoint Knowledge Agent Pilot

| Dependency | Traced to | Status | Evidence |
|---|---|---|---|
| Agent creation possible at all | Probe 3 (Stage 3.0.2.3) | `CONFIRMED_AVAILABLE` | Two working creation paths (UI wizard, hand-authored JSON via `Add-PnPFile`) confirmed functional end-to-end, including grounded citation of real content |
| Formal agent-creation approval path / write identity | Probe 3 (Stage 3.0.2.3) | `NEEDS_ESCALATION` | `CopilotAdmin` probe returned `Forbidden` (403), requiring the SharePoint Administrator role; the plan requires this be confirmed by tenant admin directly, not inferred — not yet obtained |
| Grounding/citation quality against real manual content | Probe 3 + `research-summary...md` §14 | `CONFIRMED_AVAILABLE` | Multi-document synthesis across two real CEIS topics (warrants, protection orders) produced a correctly cited, domain-accurate answer with no overclaiming |
| Source-scope behavior (what the agent can/cannot see) | `research-summary...md`, Executive Summary limitation #4 + correction #4 | `PROVISIONAL` | Confirmed the tested agent cannot derive content outside its attached source scope — but this conflates knowledge-retrieval scope, platform action capability, and user permissions, per external-review correction #4; hub-scoped source expansion (Priority 8) is untested |
| Permission-aware / stale-content behavior (Subphase 5.2) | not directly probed | `DEFERRED_UNTIL_EVIDENCE` | No probe in this session tested content-currency or permission-boundary behavior at the agent layer; Stage 5.2.1/5.2.2 need their own dedicated test transcripts |
| List data as an agent grounding source | `research-summary...md` §16 (official Microsoft doc summary) | `CONFIRMED_BLOCKED` | Microsoft documentation states agents cannot use List data as a grounding source, and the Site Pages library can never be added as an agent source at all — this reframes any future plan that assumed list-based grounding |
| Cross-surface parity (Teams app store discoverability) | `research-summary...md` §18 | `DEFERRED_UNTIL_EVIDENCE` | Microsoft documentation confirms SharePoint custom agents are independently discoverable from Microsoft Teams — a materially different host surface than the SharePoint chat pane tested throughout this session; nothing has been re-verified there (new backlog Priority 10) |

## No hard `CONFIRMED_BLOCKED` findings against Phase 3's core scope

No dependency required for Phase 3's minimum pilot scope (package-only deployment of rendered
Markdown content to a document library, native Markdown rendering as the display mechanism) is
`CONFIRMED_BLOCKED`. The two `CONFIRMED_BLOCKED` rows above (raw `.aspx` upload; write-action
skills in the tested invocation path; List-data grounding) affect Phase 3's optional page-based
extension, Phase 4's write-action skill candidates, and Phase 5's grounding-source design
respectively — none are on Phase 3's critical path as currently scoped in the master plan.

## Rows requiring tenant-admin sign-off before Phase 3 is treated as fully implementation-ready

1. `AgentAssets`/pilot-library write-principal enumeration (Phase 3).
2. Restricted Content Discovery / oversharing risk confirmation (Phase 3, Stage 3.4.2).
3. Formal agent-creation approval path and licensing/entitlement confirmation (Phase 3.0.2.3 gates
   Phase 5's agent work, and Phase 3's own write-identity decision).

These three are the rows a decision owner must either resolve with tenant admin or explicitly
accept as residual risk before authorizing full Phase 3 implementation, per the plan's Stage
3.0.3.2 decision-owner assignment.
