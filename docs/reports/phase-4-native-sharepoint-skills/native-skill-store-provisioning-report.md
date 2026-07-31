# Native Skill Store Provisioning Discovery Report

## 1. Executive Summary
This discovery report documents Task 7.5 reconnaissance on the current Phase 4 sandbox target (`https://bcgov.sharepoint.com/sites/AG-CSB-INTRANET-DEV`). As historical reference, it includes site comparison data from an earlier Phase 3 execution environment (`https://bcgov.sharepoint.com/sites/AG-CSB-ITAU-CMAT-DEV`). The earlier site is **retired from Phase 4 execution** and is documented here only to show prior evidence of native skill store provisioning on a different site.

Per Task 7.5 governance, custom creation of `AgentAssets` via `New-PnPList` or substitute locations (`SkillAssets`, `SiteAssets`) is strictly `FORBIDDEN`. Provisioning of the native skill store must occur strictly through approved tenant/site native mechanisms. Phase 4 execution is blocked until the provisioning mechanism is confirmed on the current target.

## 2. Site & Tenant Comparison Matrix

| Property / Metric | Pilot Site (`AG-CSB-intranet-dev`) | Dev Site (`AG-CSB-ITAU-CMAT-DEV`) | Status Vocabulary |
|---|---|---|---|
| **Site Template** | Team Site (`GROUP#0`) | Communication / Team Site | `OBSERVED` |
| **Copilot Availability** | Active / Available | Active / Available | `OBSERVED` |
| **Restricted Content Discovery (RCD)** | Disabled / Standard | Disabled / Standard | `OBSERVED` |
| **Copilot Limited-Mode Status** | Normal / Enabled | Normal / Enabled | `OBSERVED` |
| **Licensing / Feature Availability** | Microsoft 365 Copilot Tenant License | Microsoft 365 Copilot Tenant License | `OBSERVED` |
| **Existing Agent Experience** | Default Site Agent | Default Site Agent + Custom Agent | `OBSERVED` |
| **AgentAssets Existence** | `NOT_FOUND` | `OBSERVED` | `OBSERVED` vs `NOT_FOUND` |
| **AgentAssets Library Identity** | `NOT_OBSERVED` | Document Library (`BaseTemplate 101`) | `DOCUMENTED` |
| **AgentAssets Content Types** | `NOT_EVALUATED` | Document (`0x0101...`), Skill (`SKILL.md`) | `DOCUMENTED` |
| **AgentAssets Root URL** | `NOT_OBSERVED` | `/sites/AG-CSB-ITAU-CMAT-DEV/AgentAssets` | `OBSERVED` |
| **Skills Folder Structure** | `NOT_EVALUATED` | `AgentAssets/Skills/<skill-name>/SKILL.md` | `DOCUMENTED` |
| **Current User Permissions** | Full Control / Site Owner | Full Control / Site Owner | `ADMIN_CONFIRMED` |
| **Provisioning Trigger Method** | Pending Approved UI Action | Copilot Studio / Agent Creation UI Interaction | `DOCUMENTED` |

## 3. Provenance & Provisioning Trigger Mechanism
Phase 3 discovery log (`docs/research/research-summary-phase3-sharepoint-write-capability-discovery.md`) documents that on `AG-CSB-ITAU-CMAT-DEV`, the `AgentAssets` library was created automatically as a side effect of Copilot agent provisioning / Copilot UI interaction when an agent or skill was created via Microsoft Copilot UI. Manual scripting via `New-PnPList` was NOT used to create `AgentAssets`.

## 4. Outcome Classification

**Evidence-Based Finding:**

- `AGENTASSETS_NOT_FOUND` — `AgentAssets` library does not exist on `AG-CSB-INTRANET-DEV`.
- `PROVISIONING_METHOD_INCONCLUSIVE` — No supported native-skill-store provisioning mechanism has been established for this site.
- `NATIVE_SKILL_AUTHORING_NOT_CONFIRMED` — Native SharePoint skill authoring availability remains unconfirmed.
- `PHASE_4_ENTRY_GATE_NOT_MET`
- `TASK_8_BLOCKED`

**Required Administrative/Product Decision:**

A site owner, tenant administrator, or Microsoft product owner must confirm:

1. Is native SharePoint skill authoring enabled and supported on `AG-CSB-INTRANET-DEV`?
2. If yes, what supported Microsoft product experience provisions the native skill store for this site?

Acceptable evidence: `ADMIN_CONFIRMED`, `PRODUCT_UI_OBSERVED`, or `MICROSOFT_DOCUMENTED`.

**Non-Approved Actions:**

- Do NOT create an ordinary document library named `AgentAssets` as a substitute.
- Do NOT infer support from an ordinary library name.
- Do NOT re-gate Phase 4 to an alternate site.
- Phase 4 execution remains blocked until provisioning method is confirmed on the current target.

## 5. Evaluation Reference Reconciliation
All positive and permission evaluation references expected to exist were observed. NEG-01 intentionally references a missing/invalid topic as its negative control.

---

## 6. Evidence Durability & Storage Status

**Temporary Storage (Current):**
- Evidence ID: `EVID-PHASE4-TASK7-001`
- Current Location: `temp/EVID-PHASE4-TASK7-001-tenant-inventory.json` (transient, not Git-tracked)
- SHA-256 Hash: `0555cd51b79a30ae54ef0faf8e4a52083789804bf77f02c8fac56fd70e41b19a`

**Durable Storage (Before Phase 4 Closure):**
- Status: `PENDING_RELOCATION` — Evidence must be moved to an approved durable non-Git location before Phase 4 closure.
- Action: Copy the exact file to durable storage; verify SHA-256 remains unchanged.
- Do NOT invent a durable destination. Coordinate with project governance on approved evidence storage path.
- Tracked report will record: evidence ID, SHA-256, sanitized storage label, collection date, collector/reviewer role, access classification.

---

## 7. Operational Paths & Worktree Registration

**Registered Phase 4 Worktree:**
```
/Users/richardfremmerlid/Projects/copilot-worktrees/phase-4
Branch: phase-4-native-sharepoint-skills
Status: Clean, synchronized with remote
```

**Repository Root:**
```
/Users/richardfremmerlid/Projects/sharepoint-knowledge-workbench
```

**Orphaned Path (Do Not Use):**
```
/Users/richardfremmerlid/Projects/sharepoint-knowledge-workbench/.worktrees/phase-4-native-sharepoint-skills
Status: Broken worktree reference (not registered, created by repository folder rename)
Action: Handle via separate housekeeping step after Phase 4 closure. Do NOT remove during Phase 4.
```
