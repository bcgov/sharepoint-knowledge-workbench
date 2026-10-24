# Legacy mode: sharepoint-inspect-agent-knowledge

---
name: sharepoint-inspect-agent-knowledge
plugin: sharepoint-copilot-agents-and-skills
description: Read-only report of a deployed SharePoint agent's current knowledge-source bindings, plus resolution of the exact site_id, web_id, list_id and unique_id a new binding needs. Use to inspect what an agent is grounded on or to get correct identifiers for site isolation.
allowed-tools: Bash, Read
---

# Configure SharePoint Agent Knowledge

Two read-only capabilities: inspect a deployed agent's bindings, and resolve the resource identifiers a new binding needs.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Read-only: neither script performs a tenant write.
- Targets are explicit (`-AgentPath`, `-FolderSiteRelativePath`); there is no default.
- This inspects a deployed agent; editing a local package is `sharepoint-update-agent-package`.
- When running an installed copy, pass `-ConfigFile` explicitly.

## Quick start

```powershell
pwsh -File scripts/get-agent-resource-identifiers.ps1 -ConfigFile config.psd1 -FolderSiteRelativePath "<site-relative folder>"
```

## Workflow

1. To inspect an agent: `configure-sharepoint-agent-knowledge.ps1 -ConfigFile ... -AgentPath ...`.
2. To bind a new source: `get-agent-resource-identifiers.ps1` for the folder, then use its `site_id`, `web_id`, `list_id` and `unique_id` in the agent's `items_by_url`.
3. Report the bindings or identifiers with the exact values returned.

## Verification

Identifiers are non-empty and match the live resource; a folder gets its real `unique_id`, never another folder's GUID or the zero GUID (zeros only for a top-level library). There are no executable tests (a pure read has no dry-run mode).

## References

- [Safety, config and permissions](../agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Knowledge binding details](../agent-knowledge-binding-details.md): read for the two capabilities and the Phase 6 plan correction.
- [Agent package authoring](../agent-package-authoring-details.md): read for `items_by_url` identifier rules.


# Legacy mode: sharepoint-update-agent-package

---
name: sharepoint-update-agent-package
plugin: sharepoint-copilot-agents-and-skills
description: Updates an existing local .agent source package's description, instructions or knowledge sources in place, without recreating the whole package. Use to change an agent you already authored. Zero tenant I/O.
allowed-tools: Bash, Read, Write
---

# Update SharePoint Agent

Change an agent's instructions or grounding sources without running create again from scratch. It operates on the local `.agent` JSON that `create-agent-package` produces.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Zero tenant I/O. Do not deploy the updated package.
- `-AgentPath` must already exist: this updates, never creates.
- Pass at least one of `-AgentDescription`, `-AgentInstructionsPath`/`-AgentInstructions`, `-KnowledgeSourcePaths`; a no-op call is rejected.
- Never silently clear all grounding: an empty `-KnowledgeSourcePaths` needs `-AllowEmptyKnowledgeSources`.

## Quick start

```powershell
pwsh -File scripts/update-sharepoint-agent.ps1 -AgentPath policy-helper.agent -AgentDescription "Updated description"
```

## Workflow

1. Confirm the `.agent` file and what changes.
2. Run the script with only the parameters to change.
3. Redeploy through a separate step.

## Verification

The changed field is updated and the others (for example instructions) are unchanged.

## References

- [Safety, config and permissions](../agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Agent package authoring](../agent-package-authoring-details.md): read for update behavior and the tests.
