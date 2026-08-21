# START-HERE.md - Workbench Next Session Roadmap & Status

Welcome back! This document is the primary quick-start guide and tracker for resuming work on the **SharePoint Knowledge Workbench**.

---

## 1. Where We Left Off (Current Status)

### CrownNet My Favourite Apps (`My Applications` SPFx Web Part):
- **Full 32 Application Master Catalog**: Verified in trial tenancy with exact URLs, display orders (100–131), subtitles, and real 350×350 PNG icon graphics (`Images1/icons/`).
- **Canonical Schema & Relational Integrity**: Master `Applications` list and `My Favourite Apps` user preference list provisioned with genuine `ApplicationId` Lookup (`Applications:ID`) and `Restrict Delete` enabled.
- **Dynamic SPFx Web Part (v1.0.11.0)**: Built, packaged, and deployed. Auto-binds lists, displays organization default pins, and supports user heart toggling.
- **Repeatable Playbook**: Documented in [`temp/trialtenancy/crownnet-my-fav-apps/REPEATABLE_SITE_DEPLOYMENT_PLAYBOOK.md`](./temp/trialtenancy/crownnet-my-fav-apps/REPEATABLE_SITE_DEPLOYMENT_PLAYBOOK.md).

---

## 2. Immediate Next Session Tasks

### Phase A: Target Tenancy Validation (`AG-CSB-INTRANET-DEV`)
When ready to replicate and test the **My Favourite Apps** solution on the CSB Intranet DEV site:
1. Swap `config.psd1` to `config-csb-intranet-dev.psd1`.
2. Run the 7-step repeatable playbook:
   ```powershell
   # 1. Provision Lists
   pwsh -File temp/trialtenancy/crownnet-my-fav-apps/scripts/01-provision-prereq-lists.ps1
   pwsh -File temp/trialtenancy/crownnet-my-fav-apps/scripts/01c-configure-applications-view.ps1
   pwsh -File temp/trialtenancy/crownnet-my-fav-apps/scripts/01d-provision-my-favourite-apps-list.ps1

   # 2. Upload Icons & Seed Catalog
   pwsh -File temp/trialtenancy/crownnet-my-fav-apps/scripts/04-upload-icons.ps1
   pwsh -File temp/trialtenancy/crownnet-my-fav-apps/scripts/02-seed-sample-data.ps1

   # 3. Deploy SPFx Package
   pwsh -File plugins/sharepoint-spfx-authoring/skills/sharepoint-deploy-spfx-solution/scripts/deploy-spfx-package.ps1 `
       -PackagePath "temp/bcps-webparts/Technical Documentation/crownnet-my-fav-apps/crownnet-my-fav-apps/sharepoint/solution/crownnet-my-fav-apps-dev.sppkg"
   ```

---

### Phase B: Repository Script & Skill Standardization (64 Scripts)
Continue standardizing all repository `.ps1` automation scripts and their corresponding `SKILL.md` definitions across the 16 plugins:

📖 **Master Reference & Tracker**:  
[`docs/research/architecture-design-patterns/standardizing-rollouts-via-canonical-skills.md`](./docs/research/architecture-design-patterns/standardizing-rollouts-via-canonical-skills.md)

**Standardization Checklist per Script:**
1. [ ] **Connection Discovery**: Implement `Get-ResolvedConnection` with `-SiteUrl` / `-ConfigPath` parameter overrides.
2. [ ] **Multi-Tenancy Support**: Support both Trial Tenancy and CSB Intranet DEV profiles seamlessly.
3. [ ] **Error Handling**: Use `-ErrorAction Stop` with fail-loud logging.
4. [ ] **Skill Sync**: Update `SKILL.md` and `.agents/skills` mirrors with parameter syntax.

---

## 3. Key Reference Documents

- **Repeatable Deployment Playbook**: [`temp/trialtenancy/crownnet-my-fav-apps/REPEATABLE_SITE_DEPLOYMENT_PLAYBOOK.md`](./temp/trialtenancy/crownnet-my-fav-apps/REPEATABLE_SITE_DEPLOYMENT_PLAYBOOK.md)
- **Deployment Guide Alignment**: [`temp/trialtenancy/crownnet-my-fav-apps/DEPLOYMENT_GUIDE_ALIGNMENT.md`](./temp/trialtenancy/crownnet-my-fav-apps/DEPLOYMENT_GUIDE_ALIGNMENT.md)
- **Toolchain & Dependencies**: [`temp/trialtenancy/crownnet-my-fav-apps/DEPENDENCIES.md`](./temp/trialtenancy/crownnet-my-fav-apps/DEPENDENCIES.md)
- **Architecture Design Patterns**: [`docs/research/architecture-design-patterns/standardizing-rollouts-via-canonical-skills.md`](./docs/research/architecture-design-patterns/standardizing-rollouts-via-canonical-skills.md)
