# Agent knowledge binding: inspect and resolve identifiers

## Contents

- [The two read-only capabilities](#the-two-read-only-capabilities)
- [Correction from the Phase 6 plan](#correction-from-the-phase-6-plan)
- [Tests](#tests)

## The two read-only capabilities

1. **Inspect a deployed agent's bindings** (`configure-sharepoint-agent-knowledge.ps1`, `-ConfigFile`, `-AgentPath`, `-JsonOutputPath`): downloads a deployed `.agent` file and reports what it is grounded on right now. Distinct
   from `sharepoint-update-sharepoint-agent`, which edits a local package.
2. **Resolve resource identifiers** (`get-agent-resource-identifiers.ps1`, `-ConfigFile`, `-FolderSiteRelativePath`, `-JsonOutputPath`): extracts `site_id`, `web_id`, `list_id` and `unique_id` for a site-relative folder, per the
   confirmed working method in the source repository's Phase 4 agent-format learning journal and critical-learnings document. Previously these IDs were extracted from a working reference agent by hand each time a new agent
   needed correct site isolation; this script automates that.

Both are read-only: neither performs a tenant write. Targets are explicit (no defaults).

## Correction from the Phase 6 plan

The plan named `task-9-retrieve-topic-metadata.ps1` as this capability's source. Direct reading showed that script inspects topic item metadata values (`TopicID`, `PublicationOrder`, `TopicContentSHA256`, `Status`,
`ReviewDate`, `TransitionAction`, `TransitionTarget`), which is unrelated to agent knowledge-source configuration. It was not extracted from and remains research-only in `tools/`. Both scripts here are new builds for the real
capability gap (corrected 2026-08-03).

## Tests

No executable tests: both scripts need a live tenant connection and a pure read query has no dry-run mode (consistent with the plugin's other tenant-diagnostic scripts such as `diagnose-sharepoint-library.ps1`).
