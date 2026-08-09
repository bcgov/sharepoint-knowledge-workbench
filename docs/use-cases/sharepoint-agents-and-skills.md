# Use Case: Agent & Native-Skill Lifecycle

Owns SharePoint Copilot agent and native-skill lifecycle capability: `AgentAssets` inventory and
validation, agent lifecycle (create/update/knowledge-configuration/backup/restore/templates), and
native-skill lifecycle (create/deploy/verify/rollback/backup/restore).

## When to use this

You need to create, update, deploy, verify, back up, restore, or roll back a SharePoint Copilot
agent or a native (SharePoint-deployed, not repository-Claude) skill.

## Workflow at a glance

15 skills covering the full agent/native-skill lifecycle — see the plugin README for the complete
list. This plugin does **not** own domain-routing agents (those were decentralized to their owning
domain plugins in 2026-08 — e.g. the link-remediation routing agent lives in
`sharepoint-link-remediation`, not here); it owns only the lifecycle tooling that creates, deploys,
and manages agents/skills across all domains.

**Non-responsibilities:** content rendering (`structured-content-rendering`), SharePoint content
publication (`sharepoint-content-publication`), workbench connection/config setup
(`workbench-setup`).

## Full detail

[`plugins/sharepoint-agents-and-skills/README.md`](../../plugins/sharepoint-agents-and-skills/README.md)
