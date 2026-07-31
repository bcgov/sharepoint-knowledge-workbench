# Skill Lifecycle Policy & Rollback Procedure

## 1. Accountable Ownership & Governance
- **Accountable owner**: `PENDING_HUMAN_DECISION`
- **Technical maintainer**: `PENDING_HUMAN_DECISION`
- **Review cadence**: `PENDING_HUMAN_DECISION`
- **Emergency removal authority**: `PENDING_HUMAN_DECISION`

## 2. Versioning & Promotion
- Repository `tools/phase-4-native-sharepoint-skills/skills/review-manual-topics/SKILL.md` is the sole authoring source of truth.
- Updates require git commit and PnP script re-deployment with SHA-256 readback verification.

## 3. Human-Authorized Removal & Rollback Procedure
If a skill defect occurs or rollback is required:
1. Obtain explicit human authorization for removal.
2. Execute `rollback-skill-deployment.ps1` (or `rollback-skill.ps1`) with interactive confirmation (or `-Force` switch in automated harnesses).
3. Recycles file to SharePoint Recycle Bin (`Move-PnPFileToRecycleBin`) rather than permanent deletion.
4. Performs post-action verification checking that target item no longer exists in active site assets.
5. Verify custom agent fallback to native grounded synthesis.
