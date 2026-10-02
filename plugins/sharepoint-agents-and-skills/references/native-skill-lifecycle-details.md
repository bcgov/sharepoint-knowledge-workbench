# Native skill lifecycle: create, provision, deploy, verify, roll back

## Contents

- [create-sharepoint-native-skill](#create-sharepoint-native-skill)
- [AgentAssets: provision, readiness, diagnostic](#agentassets-provision-readiness-diagnostic)
- [deploy-sharepoint-native-skill](#deploy-sharepoint-native-skill)
- [verify-sharepoint-native-skill](#verify-sharepoint-native-skill)
- [rollback-sharepoint-native-skill](#rollback-sharepoint-native-skill)
- [Tests (source repository only)](#tests-source-repository-only)

## create-sharepoint-native-skill

Produces a locally validated `SKILL.md` source package from explicit parameters. It writes only to a local output path and never connects to a tenant.

- `-SkillName` (required): must match the `AgentAssets/Skills/<name>/` folder convention (lowercase, alphanumeric and hyphens).
- `-SkillDescription` (required).
- `-InstructionsPath` or `-Instructions` (exactly one): no default instruction content is invented; the caller supplies real content.
- `-InputBoundary`, `-ProhibitedScope` (optional): appended as their own sections.
- `-OutputPath` (required): local file path; `-Overwrite` to replace an existing file.

It does not deploy (use `sharepoint-deploy-sharepoint-native-skill` separately) and does not use `create-test-skill.ps1` as a runtime dependency.

**Chat runtime boundary.** Native skills executed by SharePoint Copilot chat agents in the web interface cannot create files in document libraries. When designing skill instructions (diagram generators, report builders),
make the skill produce copy-paste-ready structured content (Markdown, Mermaid, JSON). If a skill has a saving step, instruct the agent to give the full content and a suggested filename in chat and to say that file upload
needs external execution (for example workbench publish scripts) when automated creation tools are unavailable.

## AgentAssets: provision, readiness, diagnostic

Inspection of a site's `AgentAssets` document library (the library Copilot in SharePoint reads native `SKILL.md` files from), confirming it and its `Skills/` subfolder exist before any deployment.

- **Provision** (`provision-agentassets.ps1`, `-ConfigPath`): creates `AgentAssets` as a document library and its `Skills/` subfolder if missing. Optionally uploads one named sample skill when both `-SkillName` and
  `-SkillSourcePath` are supplied. It has no dry-run gate; it is the only write-capable capability here.
- **Readiness check** (`verify-agentassets-ready.ps1`): confirms `AgentAssets` and `Skills/` exist and are accessible, inventories existing `SKILL.md` files, and reports `READY` or `BLOCKED`.
- **Library diagnostic** (`diagnose-sharepoint-library.ps1`): read-only inspection of any library (not only `AgentAssets`); with no `-LibraryName` it lists every library, otherwise it shows items and fields.
  Use it to troubleshoot library names and IDs.

The readiness check and diagnostic must never create the library as a side effect. Output: provisioning confirms what was created or already existed, with an optional JSON inventory (`-JsonOutputPath`); readiness gives
`READY` or `BLOCKED` plus the `SKILL.md` list; the diagnostic gives library metadata (title, URL, ID, item count, fields).

## deploy-sharepoint-native-skill

Deploys a repository-authored native skill's `SKILL.md` to `AgentAssets/Skills/<skill-name>/SKILL.md` with byte-for-byte SHA-256 readback verification. It deploys an already-built package; it does not author one.

- **Deploy and verify** (`deploy-and-verify-skill.ps1`): dry-run by default. Reads a deployment manifest (skill name, repository source path, target library, folder, filename), computes the local file's SHA-256, uploads it, downloads
  it back and confirms a 100% hash match, failing loudly on mismatch. Zero writes unless `-Execute`; without it, it displays the exact resolved target (preflight only).
- **Native-skill inventory** (`inventory-skills.ps1`): read-only inventory of deployed `SKILL.md` assets and Site Pages-hosted knowledge content, to confirm what is deployed before or after a deployment. Its
  `-ExcludedSitePagesFiles` default holds organisation-specific page names; pass your own.

It does not create the `AgentAssets` library or `Skills/` folder; it fails closed if the target is missing (that is the provisioning script's job). The manifest shape is in `deployment-manifest.example.json` at the plugin root.

## verify-sharepoint-native-skill

Read-only verification that a deployed `SKILL.md` matches its repository source exactly, by SHA-256. It never uploads, overwrites or deletes.

- **Artifact verification** (`verify-agentassets-artifact.ps1`): lists everything in `AgentAssets/Skills/`, downloads and hashes any `SKILL.md`, compares each against a named repository source (`-TargetSkillName`,
  `-RepoSkillPath`), and reports `ARTIFACT_ALREADY_PRESENT` (hash match), `DEPLOYED_ARTIFACT_DRIFT_DETECTED` (mismatch) or `DEPLOYMENT_CANDIDATE_NOT_YET_PRESENT` (nothing deployed under that name).
- **Deployment reconciliation** (`reconcile-deployed-skill.ps1`, generalized from a historical script): the same read-only reconciliation, computing the expected SHA-256 from the live local file (`-RepoSkillPath`)
  instead of a hardcoded hash, and reporting frontmatter (`name`, `description`) next to the hash comparison.

No claims beyond SHA-256 comparison of the exact bytes retrieved (nothing about canonical package identity or structural-anchor completeness). `-TargetSkillName` has no hardcoded default.

## rollback-sharepoint-native-skill

Removes a deployed native skill's `SKILL.md` from `AgentAssets/Skills/<skill-name>/` by moving it to the SharePoint Recycle Bin (recoverable), never permanent deletion (`Move-PnPFileToRecycleBin`, not `Remove-PnPFile`).
Dry run by default: it displays the resolved target with zero writes unless `-Execute` is passed, and `-Execute` additionally needs `-ConfirmExactTarget "CONFIRM-REMOVE"` (exact match); a single `-Execute` is rejected. It
verifies afterwards that the item is no longer in active site content. The manifest names the exact target (same shape as the deploy skill's). It rolls back only the exact named target; no bulk or pattern removal.

## Tests (source repository only)

`tests/unit/test_create_sharepoint_native_skill.py` (valid-package generation, invalid-name rejection, missing-instructions rejection, overwrite protection, `-Overwrite` allowing replace; no tenant connection) and
`tests/unit/test_restore_sharepoint_native_skills.py`. A real bug fixed while writing the restore tests: the original wrote its `-JsonOutputPath` evidence after `Write-Error`, which is terminating under
`$ErrorActionPreference = "Stop"`, so the evidence write was dead code. Fixed in the restore script and the same copied defect in `rollback-skill-deployment.ps1`.
