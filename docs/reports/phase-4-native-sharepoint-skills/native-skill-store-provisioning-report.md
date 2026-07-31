# Native Skill Store Provisioning Discovery Report

## 1. Executive Summary
This discovery report documents the site and tenant comparison between the pilot site (`https://bcgov.sharepoint.com/sites/AG-CSB-intranet-dev`) and the dev site (`https://bcgov.sharepoint.com/sites/AG-CSB-ITAU-CMAT-DEV`) where `AgentAssets` was previously observed during Phase 3 capability discovery.

Per Task 7.5 governance, custom creation of `AgentAssets` via `New-PnPList` or substitute locations (`SkillAssets`, `SiteAssets`) is strictly `FORBIDDEN`. Provisioning of the native skill store must occur strictly through approved tenant/site native mechanisms.

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

- **Justification**: On the pilot site (`AG-CSB-intranet-dev`), `AgentAssets` does not yet exist (`NOT_FOUND`), and native skill store provisioning through UI action has not been triggered on this site instance.
- **Recommendations**:
  1. Re-gate Phase 4 to execute on the proven dev site (`AG-CSB-ITAU-CMAT-DEV`) where `AgentAssets` is already natively provisioned and verified.
  2. Alternatively, perform the approved tenant/UI provisioning action on `AG-CSB-intranet-dev` to trigger native `AgentAssets` creation prior to Task 8 authorization.
  3. Obtain explicit tenant enablement or select another approved site with active `AgentAssets`.

## 5. Evaluation Reference Reconciliation
All positive and permission evaluation references expected to exist were observed. NEG-01 intentionally references a missing/invalid topic as its negative control.
