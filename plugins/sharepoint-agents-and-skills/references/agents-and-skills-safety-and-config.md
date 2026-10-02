# Agents and native skills: safety gates, config and permissions

## Contents

- [Gate summary](#gate-summary)
- [Script gates](#script-gates)
- [Connection and config](#connection-and-config)
- [SharePoint Copilot permissions](#sharepoint-copilot-permissions)

## Gate summary

The scripts in this plugin do not share one safety model; do not assume a dry run exists.

- **Local only (zero tenant I/O):** `create-sharepoint-agent.ps1`, `update-sharepoint-agent.ps1`, `create-sharepoint-agent-template.ps1`, `apply-sharepoint-agent-template.ps1`, `create-sharepoint-native-skill.ps1`.
- **Read-only against the tenant:** `backup-sharepoint-agents.ps1`, `backup-sharepoint-native-skills.ps1`, `configure-sharepoint-agent-knowledge.ps1`, `get-agent-resource-identifiers.ps1`, `inventory-skills.ps1`,
  `verify-agentassets-ready.ps1`, `diagnose-sharepoint-library.ps1`, `verify-agentassets-artifact.ps1`, `reconcile-deployed-skill.ps1`.
- **Dry run by default, `-Execute` to write:** `deploy-and-verify-skill.ps1` (deploys, then SHA-256 readback).
- **Two-part gate (`-Execute` plus an exact confirmation string):** `restore-sharepoint-agents.ps1` and `restore-sharepoint-native-skills.ps1` need `-ConfirmExactTarget "CONFIRM-RESTORE"`;
  `rollback-skill-deployment.ps1` needs `-ConfirmExactTarget "CONFIRM-REMOVE"`. A single `-Execute` is rejected.
- **No gate, writes immediately:** `provision-agentassets.ps1` creates the `AgentAssets` library and its `Skills/` folder (and uploads a sample skill when `-SkillName` and `-SkillSourcePath` are given) as soon as it runs.

## Script gates

| Script | Effect | Gate |
|---|---|---|
| `restore-sharepoint-agents.ps1` / `restore-sharepoint-native-skills.ps1` | Writes backed-up files back to tenant locations | `-Execute` + `-ConfirmExactTarget "CONFIRM-RESTORE"` |
| `rollback-skill-deployment.ps1` | Recycles (not permanently deletes) one deployed `SKILL.md`, then verifies it is gone | `-Execute` + `-ConfirmExactTarget "CONFIRM-REMOVE"` |
| `deploy-and-verify-skill.ps1` | Uploads a `SKILL.md`, downloads it back, compares SHA-256 | `-Execute` |
| `provision-agentassets.ps1` | Creates `AgentAssets` and `Skills/` | none |

## Connection and config

Most scripts take `-ConfigFile` (connection and authentication context only: `SiteUrl`, `ClientId`, `TenantId`), except `provision-agentassets.ps1`, which takes `-ConfigPath`. The defaults resolve to the repository root
`config.psd1` (`../../../config.psd1`), and `deploy-and-verify-skill.ps1` and `rollback-skill-deployment.ps1` default `-ManifestFile` to a repo-root-relative path. Neither default resolves from an installed skill, so pass
`-ConfigFile` (or `-ConfigPath`) and `-ManifestFile` explicitly. A config with placeholder credentials fails closed with an explicit error; there is no fallback to another config file. Copy `config.psd1.example` to
`config.psd1` and fill in tenant details first. See `deployment-manifest.example.json` at the plugin root for the manifest shape (skill name, repository path, target library, folder and filename).

Targets are always explicit parameters; no tenant, site, library or skill name is hardcoded (with one exception: `inventory-skills.ps1`'s `-ExcludedSitePagesFiles` default lists organisation-specific page names; pass your own).

## SharePoint Copilot permissions

Even when PnP PowerShell writes an `.agent` file successfully with Site Collection Admin credentials, launching it in the SharePoint Copilot UI requires the user to be an explicit member of the **Site Owners** group.
Without it the Copilot panel fails with "Something went wrong with this agent. Please try again later or select a different agent". Being a Site Collection Administrator alone is not sufficient for Microsoft 365 Copilot
grounding at runtime.
