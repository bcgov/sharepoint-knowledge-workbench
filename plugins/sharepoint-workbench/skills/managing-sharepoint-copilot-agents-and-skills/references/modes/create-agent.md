# Legacy mode: sharepoint-create-agent-package

---
name: sharepoint-create-agent-package
plugin: sharepoint-copilot-agents-and-skills
description: Authors a validated SharePoint Copilot agent (.agent JSON) source file locally, from explicit name, description, instructions and knowledge-source parameters, or from a Markdown template. Use to produce an agent package. Does not deploy it.
allowed-tools: Bash, Read, Write
---

# Create SharePoint Agent

Produce a locally validated `.agent` JSON source file (`schemaVersion 0.2.0`). Zero tenant I/O.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Zero tenant I/O: no `Connect-PnPOnline` anywhere in the script. Do not deploy the package here.
- At least one knowledge source is required, and exactly one instruction source (`-AgentInstructionsPath` or `-AgentInstructions`). `-Overwrite` is required to replace an existing file.
- It always sets `discourage_model_knowledge = true` to force grounding on the knowledge sources.
- Custom agents are read-only RAG: they cannot create files. `items_by_url` must match the live resource (use `get-agent-resource-identifiers.ps1`).

## Quick start

```powershell
pwsh -File scripts/create-sharepoint-agent.ps1 -AgentName "Policy Helper" -AgentDescription "Answers policy questions" -AgentInstructionsPath instructions.md -KnowledgeSourcePaths @('https://tenant.sharepoint.com/sites/x/Policies') -OutputPath policy-helper.agent
```

## Workflow

1. Choose the format: Markdown (`-AgentMarkdownTemplatePath`) or parameters/JSON (`-AgentName`, `-AgentDescription`, instructions, `-KnowledgeSourcePaths`, `-AgentTemplatePath`).
2. Resolve identifiers for each knowledge folder with `get-agent-resource-identifiers.ps1`.
3. Run the script with `-OutputPath`.
4. To bind native skills, follow the binding rules in the details reference.

## Verification

The output is valid `.agent` JSON with the expected sources (a single source stays an array). Deployment is a separate step.

## References

- [Safety, config and permissions](../agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Agent package authoring](../agent-package-authoring-details.md): read for both formats, native-skill binding, the grounding table, identifier rules and the single-element array fix.


# Legacy mode: sharepoint-create-agent-template

---
name: sharepoint-create-agent-template
plugin: sharepoint-copilot-agents-and-skills
description: Authors a reusable SharePoint agent template (purpose, instruction structure, boundaries, refusal behavior, citation expectations, knowledge-source placeholders, governance metadata), distinct from a concrete .agent package. Use to capture a reusable agent shape. Zero tenant I/O.
allowed-tools: Bash, Read, Write
---

# Create SharePoint Agent Template

Capture the reusable shape of an agent separately from any deployment target. `create-agent-package-from-template` later fills it in.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Zero tenant I/O. This does not produce a deployable `.agent` file; use `sharepoint-create-agent-package-from-template` for that.
- Required: `-TemplateName`, `-Purpose`, `-TemplateVersion`, `-KnowledgeSourcePlaceholderCount` (>= 1), `-OutputPath`, and exactly one of `-InstructionsTemplatePath` or `-InstructionsTemplate`.
- `-AnswerBoundary`, `-RefusalBehavior` and `-CitationExpectations` are optional and appended as their own sections. `-Overwrite` replaces an existing file.

## Quick start

```powershell
pwsh -File scripts/create-sharepoint-agent-template.ps1 -TemplateName policy-helper -Purpose "Answer policy questions" -TemplateVersion 1.0 -KnowledgeSourcePlaceholderCount 2 -InstructionsTemplatePath instructions.md -OutputPath policy-helper.template.json
```

## Workflow

1. Decide the purpose, boundaries and how many knowledge sources a concrete agent will need.
2. Run the script.
3. Apply the template with `sharepoint-create-agent-package-from-template`.

## Verification

The template file exists with the intended placeholder count and the optional sections you supplied.

## References

- [Safety, config and permissions](../agents-and-skills-safety-and-config.md): read for the gate model of every script, the `-ConfigFile` default caveat and the Copilot permission note.
- [Agent package authoring](../agent-package-authoring-details.md): read for templates versus agents and the tests.
