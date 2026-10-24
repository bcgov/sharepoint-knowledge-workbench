# Agent package authoring: create, update, templates

## Contents

- [create-agent-package](#create-agent-package)
- [Native skill binding in agents](#native-skill-binding-in-agents)
- [Grounding and architecture boundaries](#grounding-and-architecture-boundaries)
- [Agent runtime limits and resource identifiers](#agent-runtime-limits-and-resource-identifiers)
- [update-agent-package](#update-agent-package)
- [Templates: create and apply](#templates-create-and-apply)
- [Tests (source repository only)](#tests-source-repository-only)

## create-agent-package

Produces a locally validated `.agent` JSON source file per the reverse-engineered schema (`schemaVersion 0.2.0`, `customCopilotConfig.gptDefinition`). It is a new build, parameterized per the design document's script parameter
matrix, not extracted from the experimental `create-*-agent.ps1` scripts (those stay in `tools/` as evidence of the schema pattern). Zero tenant I/O; it does not deploy the package. It always sets
`behavior_overrides.special_instructions.discourage_model_knowledge = true` to force grounding on knowledge sources, matching the confirmed-working reference agent.

Two authoring formats:

1. **Markdown (`.agent.md`):** `-AgentMarkdownTemplatePath` reads a human-friendly Markdown template (for example `qa-test-list-agent.agent.md` or `sharepoint-agent.template.md`), parsing `# Name`, `## Purpose` and grounding URLs.
2. **Declarative parameters / JSON:** `-AgentName`, `-AgentDescription`, `-AgentInstructionsPath` or `-AgentInstructions`, `-KnowledgeSourcePaths` (array of URLs), and `-AgentTemplatePath` (JSON structure template
   `sharepoint-agent.template.json`).

Output: `-OutputPath` (required); `-Overwrite` to replace an existing file. Template files ship with the create-agent-package skill, in its assets folder.

## Native skill binding in agents

The SharePoint `.agent` schema has no documented property (such as `skills` or `skillIds`) for hard-binding a native skill. The runtime matches skills dynamically from:

1. the skill's YAML `description` in `/AgentAssets/Skills/<skill-name>/SKILL.md`, which must state its purpose and trigger phrases;
2. explicit invocation in conversation starters: each should state "Use the <skill-name> skill to...";
3. unambiguous agent instructions: "For every request to [action], you must invoke and follow the native SharePoint skill named <skill-name>. Do not independently reproduce or substitute your own procedure.";
4. exact folder matching: the referenced name must match `/AgentAssets/Skills/<skill-name>/SKILL.md` exactly.

## Grounding and architecture boundaries

| Layer | Artifact | Role | Grounding enforcement | Write capabilities |
|---|---|---|---|---|
| Enforced scope | `.agent` (`capabilities.items_by_url`) | What to know | Hard structural boundary: retrieval is restricted to the curated list of up to 20 sources | Read-only / RAG: cited responses; cannot create or write files |
| Site context | `SHAREPOINT.md` (in `AgentAssets`) | Site knowledge | Site-level bias: loaded into all chat sessions on that site | None: informational |
| Workflow | `SKILL.md` (in `AgentAssets/Skills`) | How to act | Soft procedural bias: steers behavior, cannot enforce a retrieval boundary | Read and synthesis; native file creation only in first-party Copilot in SharePoint |
| Write extensions | Copilot Studio / SPFx | Actions | Connector/API controlled (Power Platform or Graph permissions) | Active writes, needed if agents must write to libraries |

## Agent runtime limits and resource identifiers

- Custom `.agent` definitions run in read-only, retrieval-augmented mode and have no write or create-file capability. Instructions that generate documents, code or diagrams must format output as copy-paste-ready blocks
  (Mermaid markdown, structured JSON) for human or pipeline upload.
- `items_by_url` must match the live SharePoint resource exactly. For a custom list: `type: "List"`, `unique_id: "00000000-0000-0000-0000-000000000000"`, `list_id: "<real-list-guid>"`. For a document library or folder:
  `type: "Folder"`, `unique_id: "<real-folder-guid>"` (or the zero GUID if top-level), and the library's `list_id`. Never assign another folder's GUID to an arbitrary subfolder. Resolve identifiers with
  `get-agent-resource-identifiers.ps1 -ConfigFile ...` (see `agent-knowledge-binding-details.md`).

## update-agent-package

Previously there was no way to change an agent's instructions or grounding sources without running create again from scratch. This operates on the same local `.agent` JSON package `create-agent-package` produces.
`-AgentPath` must already exist (it updates, never creates). `-AgentDescription`, `-AgentInstructionsPath` / `-AgentInstructions` and `-KnowledgeSourcePaths` are optional, but at least one is required (a no-op call is
rejected). An empty `-KnowledgeSourcePaths` needs `-AllowEmptyKnowledgeSources`, so it never silently clears all grounding. Zero tenant I/O; it does not deploy.

## Templates: create and apply

Template creation is distinct from agent creation. `create-agent-package` produces a concrete `.agent` for one target; `create-agent-template` captures the reusable shape (governance metadata, boundary rules,
knowledge-source placeholder count); `create-agent-package-from-template` later fills it in.

- **create-agent-template:** `-TemplateName`, `-Purpose`, `-TemplateVersion`, `-KnowledgeSourcePlaceholderCount` (`>= 1`) required; exactly one of `-InstructionsTemplatePath` or `-InstructionsTemplate`;
  optional `-AnswerBoundary`, `-RefusalBehavior`, `-CitationExpectations` (appended as their own sections); `-OutputPath` required, `-Overwrite` to replace. Does not produce a deployable `.agent`.
- **create-agent-package-from-template:** `-TemplatePath` (must exist), `-AgentName`, `-AgentDescription` (the template has no identity), `-KnowledgeSourcePaths` (must contain exactly the template's
  `KnowledgeSourcePlaceholderCount`; a mismatch is rejected, never truncated or padded), `-OutputPath`; `-Overwrite` is passed through to `create-sharepoint-agent.ps1`, to which it delegates. It does not deploy.
  Invoking a script with a multi-value array parameter (two or more `-KnowledgeSourcePaths`) followed by more named parameters is unreliable under `pwsh -File`; use `-Command` with an explicit `@(...)` array literal.
  Single-value arrays work under `-File`.

## Tests (source repository only)

`tests/unit/test_agent_templates.py` (templates, including exact-source-count enforcement), `test_create_sharepoint_agent.py` (valid JSON, at-least-one source, overwrite protection, mutually exclusive instruction
sources) and `test_update_sharepoint_agent.py` (description update leaves instructions unchanged, source replacement, missing-path rejection, no-parameters rejection, empty-sources-without-allow rejection).

A real bug was found and fixed writing the create tests: `ConvertTo-Json` unwraps a single-element PowerShell array into a bare object, so `items_by_url` with exactly one knowledge source serialized as `{...}` instead of
`[{...}]` (schema-invalid for the most common case). Fixed with an explicit `[System.Object[]]` cast.
