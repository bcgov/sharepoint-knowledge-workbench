# sharepoint-copilot-agents-and-skills

This is one of the seven installable SharePoint Knowledge Workbench plugins. Its current skill inventory and previous-name mapping are listed in the [seven-domain catalog](../../docs/architecture/seven-domain-plugin-skill-catalog.md).

## Purpose

Owns the authoring and lifecycle of SharePoint Online Copilot agents (`.agent` packages) and native Copilot Studio skills: local authoring and templates, deployed knowledge inspection, AgentAssets readiness, deployment, verification, backup, restore and rollback.

## Runtime effects

Skills author local files, inspect tenant state, or perform live operations according to each skill's documented controls. Check the individual skill and script before running it; package-level descriptions do not replace command-level safety requirements.

## Functional group

### Agent and native skill lifecycle

- `sharepoint-backup-agents` and `sharepoint-backup-native-skills` — read deployed artifacts into a local backup.
- `sharepoint-create-agent-package`, `sharepoint-create-agent-package-from-template`, and `sharepoint-create-agent-template` — author agent packages and reusable templates locally.
- `sharepoint-create-native-skill` — author a native SharePoint skill locally.
- `sharepoint-deploy-native-skill`, `sharepoint-verify-native-skill`, and `sharepoint-undeploy-native-skill` — deploy, verify, and roll back native skills.
- `sharepoint-inspect-agent-knowledge` — inspect deployed knowledge bindings without changing them.
- `sharepoint-prepare-agentassets-library` — inspect AgentAssets readiness and provision when explicitly requested.
- `sharepoint-restore-agents` and `sharepoint-restore-native-skills` — restore backed-up artifacts under their documented controls.
- `sharepoint-update-agent-package` — update a local agent package without tenant I/O.

## Previous identities

Skill and plugin names changed in the seven-domain migration for issue #6. The old names are migration provenance, not installable aliases.

| Previous skill | Current skill | Previous plugin |
|---|---|---|
| `sharepoint-backup-sharepoint-agents` | `sharepoint-backup-agents` | `sharepoint-agents-and-skills` |
| `sharepoint-backup-sharepoint-native-skills` | `sharepoint-backup-native-skills` | `sharepoint-agents-and-skills` |
| `sharepoint-create-sharepoint-agent` | `sharepoint-create-agent-package` | `sharepoint-agents-and-skills` |
| `sharepoint-apply-sharepoint-agent-template` | `sharepoint-create-agent-package-from-template` | `sharepoint-agents-and-skills` |
| `sharepoint-create-sharepoint-agent-template` | `sharepoint-create-agent-template` | `sharepoint-agents-and-skills` |
| `sharepoint-create-sharepoint-native-skill` | `sharepoint-create-native-skill` | `sharepoint-agents-and-skills` |
| `sharepoint-deploy-sharepoint-native-skill` | `sharepoint-deploy-native-skill` | `sharepoint-agents-and-skills` |
| `sharepoint-configure-sharepoint-agent-knowledge` | `sharepoint-inspect-agent-knowledge` | `sharepoint-agents-and-skills` |
| `sharepoint-inventory-and-validate-agentassets` | `sharepoint-prepare-agentassets-library` | `sharepoint-agents-and-skills` |
| `sharepoint-restore-sharepoint-agents` | `sharepoint-restore-agents` | `sharepoint-agents-and-skills` |
| `sharepoint-restore-sharepoint-native-skills` | `sharepoint-restore-native-skills` | `sharepoint-agents-and-skills` |
| `sharepoint-rollback-sharepoint-native-skill` | `sharepoint-undeploy-native-skill` | `sharepoint-agents-and-skills` |
| `sharepoint-update-sharepoint-agent` | `sharepoint-update-agent-package` | `sharepoint-agents-and-skills` |
| `sharepoint-verify-sharepoint-native-skill` | `sharepoint-verify-native-skill` | `sharepoint-agents-and-skills` |

## Installing

See the repository [INSTALL.md](../../INSTALL.md). Example:

```text
/plugin install sharepoint-copilot-agents-and-skills@sharepoint-knowledge-workbench
```
