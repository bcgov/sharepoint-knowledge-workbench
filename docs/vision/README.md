# Vision and implementation roadmap

This directory separates the workbench's current implementation from its broader future-state
vision. The live repository has **7 installable plugins, 104 skills, and 11 of the 12 documented
use cases implemented**. The remaining use case is the integrated AI-assisted knowledge-management
pipeline; it remains a vision, not a shipped end-to-end capability. The 11/12 count is a count of
use-case documents, not a measure of completion across every strategic goal.

The current package and skill inventory is maintained in the
[seven-plugin catalog](../architecture/seven-domain-plugin-skill-catalog.md). The [architecture
overview](../../architecture.md), [installation guide](../../INSTALL.md), and [use-case index](../use-cases/README.md)
describe the implemented toolkit.

The built workbench covers setup, document conversion, site assessment, SharePoint object
creation and publishing, site migration, Copilot agent/native-skill lifecycle, and SPFx development.
The broader vision goes further: a governed lifecycle for creating and maintaining knowledge,
integrated human approval and source-of-truth controls, knowledge-health monitoring, records and
retention governance, and a validated cross-runtime authoring and republishing loop. Those remain
future design or research topics unless an implementation is present in the plugins and verified
by their tests.

## Current planning documents

- [Broader initiative plan](ai-assisted-structured-knowledge-workbench-broader-plan.md) — strategy
  and roadmap, with a current-state notice before its original proposal material.
- [SharePoint knowledge-workbench governance vision](ai-assisted-sharepoint-knowledge-workbench-governance-vision.md)
  — the future capability and governance model.
- [Master initiative plan](master-initiative-plan-workstreams-and-phases.md) — phase and stage
  roadmap. Its current implementation snapshot distinguishes shipped repository capabilities from
  the larger, still-gated vision.
- [Key unanswered questions](key-unanswered-questions.md) — unresolved operating-model and
  architecture questions.
- [Content-authoring workflow options](content-authoring-workflow-options.md) — unresolved design
  alternatives for ongoing business-author editing; not an implemented workflow.

Temporary review notes, one-off audits, generated evidence, and scratch scripts belong in the
git-ignored `temp/` directory. Stable vision, open questions, and the roadmap remain versioned here.
