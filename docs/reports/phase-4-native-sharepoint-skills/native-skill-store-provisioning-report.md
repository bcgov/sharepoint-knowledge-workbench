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

**Outcome C: Native skill authoring unavailable on this site (`PHASE_4_ENTRY_GATE_NOT_MET`)**

- **Justification**: On the current target site (`AG-CSB-INTRANET-DEV`), `AgentAssets` does not yet exist (`NOT_FOUND`). No supported native-skill-store provisioning mechanism has yet been established for this sandbox target.
- **Required Action**:
  A site owner, tenant administrator, or Microsoft product owner must confirm whether native SharePoint skill authoring is enabled on `AG-CSB-INTRANET-DEV` and identify the supported product experience, if any, that provisions the native skill store.
- **Non-Approved Actions**:
  - Do NOT create an ordinary document library named `AgentAssets` as a substitute.
  - Do NOT re-gate Phase 4 to an alternate site.
  - Phase 4 execution remains blocked until provisioning method is established on the current target.

## 5. Evaluation Reference Reconciliation
All positive and permission evaluation references expected to exist were observed. NEG-01 intentionally references a missing/invalid topic as its negative control.
