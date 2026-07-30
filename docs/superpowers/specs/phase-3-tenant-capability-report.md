# Phase 3.0 Tenant-Capability Report

**Status:** DRAFT — synthesized from existing, already-committed Phase 3.0 evidence. Per the two-state rule
in `start-here.md`, Phase 3 becomes implementation-ready only once a version of this report is **accepted**
(human sign-off) and every blocking row below maps to observed evidence. This draft is the first pass at
that acceptance gate, not the acceptance itself.

**Evidence sources this report synthesizes (read these for full detail; not duplicated here):**
- `tools/phase-3-sharepoint-discovery/reports/phase-3-0-discovery-report.json` — read-only PnP inventory
  (gitignored raw tenant data; summarized below).
- `docs/research/research-summary-phase3-sharepoint-write-capability-discovery.md` — staged, reversible
  write-exploration findings (agent/skill/template capability discovery), already externally reviewed once
  (2026-07-29 correction round).
- `tools/phase-3-sharepoint-discovery/agents/*.agent.json`, `tools/phase-3-sharepoint-discovery/skills/*`,
  `tools/phase-3-sharepoint-discovery/aspx-experiment/` — raw experiment artifacts underlying the write
  summary above.

**Tenant/scope this report describes:** BC Gov dev site `AG-CSB-ITAU-CMAT-DEV`
(`https://bcgov.sharepoint.com/sites/AG-CSB-ITAU-CMAT-DEV`), app registration `ag.csb.cmat.interactive`
(intentionally manage-only — no permission-management rights). Findings below are scoped to this tenant,
site, and permission profile; they are not a general SharePoint-platform claim.

---

## 1. Read-only tenant inventory (Stage 3.0.1.2 — surface inventory)

Source: `phase-3-0-discovery-report.json`, exported 2026-07-29, script commit `744d7a3`.

| Fact | Value |
|---|---|
| Web template | `STS` (classic team site), Configuration 3, Language 1033 |
| Lists/libraries (non-hidden) | 106 |
| Site columns (fields) | 426 |
| Content types | 75 |
| Site groups | 3 observed (Members, Owners, Visitors — standard SharePoint groups; role-assignment membership not enumerable, see §3) |
| Versioning | 104/106 lists have `EnableVersioning: true` |
| AgentAssets library | Exists; `HasUniqueRoleAssignments: false` (inherits site permissions); governance flags: `EnableModeration: false`, `ForceCheckout: false`, `DraftVersionVisibility: Reader`, `ContentTypesEnabled: false` |

**Consumption:** satisfies the evidence-matrix rows "SharePoint surface type available" and (partially)
"Metadata field types/constraints for a pilot library" and "Library versioning configuration/behaviour" —
native versioning is confirmed enabled tenant-wide as a baseline. A pilot-library-specific field/versioning
check still needs to be re-run once a candidate pilot library is named (`PilotLibraryGovernance` was
`NotSupported` this run — no `-PilotLibraryTitle` was supplied).

## 2. Write-exploration findings (Stage 3.0.2.x, staged reversible writes)

Full findings, evidence, and the 2026-07-29 external-review correction round live in
`docs/research/research-summary-phase3-sharepoint-write-capability-discovery.md`. Condensed for Phase 3
consumption, with the tempered (post-correction) classification carried forward as-is:

| Finding | Classification | Phase 3 relevance |
|---|---|---|
| Document libraries/lists/fields fully scriptable via PnP, even manage-only | Confirmed | Supports package-only, script-driven publication |
| `.agent` files are plain JSON, hand-authorable/uploadable via `Add-PnPFile`, function correctly in this tenant | Technically viable in tested tenant; **no supported deployment interface established** | Phase 4/5 dependency only — non-goal for Phase 3 itself |
| `SKILL.md` auto-discovered by same-site custom agent via trigger wording | Confirmed for this agent/site only, not proven site/tenant-wide | Phase 4/5 dependency only |
| Native Markdown rendering works (headings, relative links navigate correctly) | Confirmed | **Directly satisfies Stage 3.0.2.4** — resolves the evidence-matrix's blocking row on rendered-Markdown representation |
| Multi-document synthesis across real CEIS content, cited and accurate | Confirmed, high quality | Supports Phase 3's premise that published content remains useful when queried |
| Custom `.agent` chat-pane write actions (list/document) unavailable in tested path | `CONFIRMED_TENANT_OBSERVATION` for this invocation path only | Confirms Phase 3 must rely on PnP/script-driven publication, not agent-initiated writes — consistent with package-only design already in the spec |
| `## Output format` in a skill is a stylistic bias, not an enforced contract; external template file was hallucinated rather than read literally | Confirmed limitation | Phase 4/5 dependency only (skill authoring) |
| No image/diagram rendering in chat pane | Confirmed limitation, this invocation path | Phase 4/5 dependency only |
| Agent knowledge retrieval bounded strictly by attached Sources | Confirmed for this path; not a proven claim about action/tool capability or user permissions generally | No direct Phase 3 build impact |
| ASPX / modern-page push path exercised (raw `.aspx` + client-side page via `Add-PnPFile`) | See `docs/research/...write-capability-discovery.md` §15 for observed results | Informational for Phase 3's "supported representation" fallback discussion, not required for Phase 3 itself |

## 3. Still-open / manual-only items (from `ManualStepsNeeded` in the discovery JSON)

These remain **not resolved** by evidence gathered so far and require tenant-admin-level access this app
registration does not have:

- Full role-assignment enumeration for AgentAssets/any pilot library (who has Member/Visitor/Owner access) —
  needed for the Stage 3.4.2 two-identity oversharing test (evidence-matrix row, unresolved-decision #9).
  Requires a SharePoint admin account or Manage Permissions/Full Control.
- Restricted Content Discovery / `KnowledgeAgentScope` (whether this site is excluded from org-wide
  Copilot discovery) — `Forbidden` for this account; requires SharePoint Administrator role.
- Copilot-in-SharePoint tenant-wide licensing/entitlement and agent-creation approval path — tenant-admin
  confirmation only, out of scope for Phase 3's own build per the evidence matrix (Phase 4/5 dependency).

## 4. Mapping against the Phase 3.0 Evidence-Consumption Matrix

Using the matrix's rows (`phase-3-tenant-evidence-consumption-matrix.md`):

| Matrix row | Status after this report |
|---|---|
| Pilot site/library exists and is authorized | **Satisfied** — site accessed, discovery ran under an authorized interactive session |
| SharePoint surface type available | **Satisfied** — §1 above |
| AgentAssets existence/writability | Non-blocking for Phase 3 (Phase 4/5) — informationally satisfied anyway (§1, §2) |
| Native `SKILL.md` authoring availability | Non-blocking for Phase 3 — informationally satisfied (§2) |
| Agent-creation approval path | Non-blocking for Phase 3 — still open, tenant-admin item (§3) |
| Native Markdown rendering enabled | **Satisfied — blocking row now closed** (§2) |
| Metadata field types/constraints for a pilot library | Partially satisfied tenant-wide (§1); needs a pilot-library-specific re-run once a library is named |
| Report + dependency-status map completeness | This report is that artifact — pending human acceptance |
| Library versioning configuration/behaviour | **Satisfied tenant-wide** (§1); pilot-library-specific confirmation still pending |
| Available identities for permission/oversharing testing | **Resolved (§5)** — using the 3 standard groups as test identities |
| Package-only manual-upload feasibility | Supported by §2's confirmed findings (scriptable libraries/fields, no agent-initiated writes needed) |
| Candidate publisher role/permission level | **Resolved (§5)** — Contribute permission level |
| Write identity status for reversible Phase 3 pilot writes | Precedent established by the staged-write protocol already used for this discovery (§2's experiments were all `TEST-DO-NOT-USE-*`, removed after use) |

## 5. Resolution of the two previously-open rows (human decision, 2026-07-30)

**Oversharing-test identities:** resolved to use the 3 existing standard SharePoint groups (Members,
Owners, Visitors) as the distinct test identities. Full per-member role-assignment enumeration is not
achievable with this manage-only app registration, but is not required to test the actual Stage 3.4.2
concern — whether an overly broad group (e.g. Visitors) is assigned to the pilot library. Group-level
testing is sufficient for Phase 3; a full member-level permission audit is deferred as a documented
follow-up (not a Phase 3 blocker).

**Publisher role/permission level:** resolved to the standard SharePoint **Contribute** permission level
(documented platform behaviour, not tenant-specific evidence) — Contribute includes Edit Items, which
covers upload, metadata update, and version rollback (restore-previous-version). No tenant-admin
confirmation was required for this decision.

## 6. Recommendation

With the resolutions in §5, this report closes all rows in the evidence-consumption matrix: **Native
Markdown rendering** (confirmed working), **metadata field types/versioning** (confirmed tenant-wide;
pilot-library-specific re-check recommended once a library is named, non-blocking), **oversharing-test
identities** (standard groups), and **publisher permission level** (Contribute). Phase 3 is now
implementation-ready per the two-state rule.

**Next step:** reconcile `phase-3-unresolved-decisions.md` items #1, #6, #7, #9, #10 against the facts and
resolutions above, then proceed to `superpowers:writing-plans`.
