# AI-Assisted SharePoint Knowledge Workbench Research

This directory contains research, field notes, and architecture guidance supporting an emerging **AI-Assisted SharePoint Knowledge Workbench**.

The work began with a practical document-conversion problem: how to turn large Word manuals into maintainable, structured knowledge without treating raw Markdown conversion as the final product. It expanded into a broader investigation of how structured Markdown, SharePoint governance, native SharePoint skills, SharePoint agents, Copilot Cowork, Copilot Studio, and GitHub Copilot can work together across the knowledge lifecycle.

## Vision

The broader vision is a governed AI toolbox for organizational knowledge:

```text
Understand
→ Design
→ Convert
→ Structure
→ Enrich
→ Review
→ Approve
→ Publish
→ Curate
→ Find
→ Analyze
→ Generate
→ Create Agents
→ Monitor
```

The workbench is not a single SharePoint agent or a collection of unrelated prompts. It is a versioned design, engineering, evaluation, and packaging environment that can produce several target-specific outputs:

```text
GitHub Copilot / VS Code Knowledge Workbench
    |
    +-- Structured Markdown content
    +-- Publication maps
    +-- Metadata and content-model specifications
    +-- Native SharePoint SKILL.md files
    +-- SharePoint agent definitions
    +-- Copilot Cowork skill packages
    +-- Copilot Studio specifications
    +-- Evaluation suites
    +-- Deployment manifests and evidence
```

## Core Architecture

The research supports a layered capability model.

### SharePoint agents

Use for bounded conversational knowledge experiences:

- find approved guidance;
- answer questions from selected SharePoint sources;
- summarize accessible documents;
- guide users to relevant content.

### Native Copilot in SharePoint skills

Use for repeatable, site-scoped knowledge procedures that can be completed through supported SharePoint capabilities and the current user's permissions:

- review selected manual topics;
- check required metadata;
- apply a content checklist;
- identify missing sections;
- generate a draft quiz;
- organize selected files;
- create review follow-up items.

A field test in the target tenant used a document library named:

```text
AgentAssets
```

The tested name contains no space. Native skill definitions are represented as Markdown `SKILL.md` files beneath the skills area of that library.

Native SharePoint skills do not provide a general-purpose execution environment. They should not be designed to require local file-system access, Python, PowerShell, shell scripts, Git, Pandoc, LibreOffice, arbitrary APIs, or external systems.

### Copilot Cowork skills and plugins

Use when reusable domain workflows should be packaged and distributed more broadly through Microsoft 365 Copilot rather than remaining local to one SharePoint site.

### Copilot Studio

Use when a solution requires broader enterprise-process capabilities such as connectors, external systems, agent flows, richer actions, multi-system orchestration, or deployment across additional channels.

### GitHub Copilot knowledge workbench

Use for engineering-heavy and deterministic work:

- DOCX extraction and cleanup;
- structured-content conversion;
- structural anchors and stable identities;
- schema validation;
- automated tests;
- file-system changes;
- Git workflows;
- publication assembly;
- multi-format rendering;
- deployment adapters;
- reproducible releases and evidence.

## Runtime Decision Rule

```text
Use a native SharePoint skill when the task is interactive,
site-scoped, and can be completed entirely through supported
Copilot in SharePoint actions and the user's current permissions.

Use a GitHub Copilot repository skill when the task requires files,
scripts, custom code, Git, deterministic validation, external systems,
complex testing, or reproducible release artifacts.

Use a hybrid workflow when the repository should prepare, validate,
or package the work and SharePoint should provide the constrained,
business-user-facing interaction.
```

## Research Documents

### Start here

1. [`research-summary-ai-in-sharepoint-content-chaos-to-clarity.md`](research-summary-ai-in-sharepoint-content-chaos-to-clarity.md)  
   Introduces the Microsoft direction around **Setup, Automate, and Insight** and connects it to the complete knowledge-management lifecycle.

2. [`capability-layering-sharepoint-skills-cowork-copilot-studio-github.md`](capability-layering-sharepoint-skills-cowork-copilot-studio-github.md)  
   Provides the broad platform model across SharePoint agents, native SharePoint skills, Copilot Cowork, Copilot Studio, and GitHub Copilot.

3. [`skill-runtime-decision-guide-sharepoint-vs-github-copilot.md`](skill-runtime-decision-guide-sharepoint-vs-github-copilot.md)  
   Provides the practical decision tree for choosing where a skill should be created, stored, executed, tested, and governed.

### SharePoint agents and native skills

4. [`sharepoint-agents-and-native-skills-as-workbench-outputs.md`](sharepoint-agents-and-native-skills-as-workbench-outputs.md)  
   Explains how native skills and SharePoint agents can be generated as constrained outputs of the broader studio, including storage, licensing, permissions, deployment, and evaluation considerations.

5. [`research-summary-copilot-in-sharepoint-get-started.md`](research-summary-copilot-in-sharepoint-get-started.md)  
   Summarizes the documented Copilot in SharePoint preview, administrative controls, availability, skill storage, permission boundaries, and capability limitations.

6. [`field-note-sharepoint-agentassets-review-manual-topics-skill.md`](field-note-sharepoint-agentassets-review-manual-topics-skill.md)  
   Records the successful tenant experiment using the `AgentAssets` library and the generated `review-manual-topics` native skill. It also identifies hardening and evaluation requirements.

7. [`field-note-ready-made-copilot-agent-launch-by-name.md`](field-note-ready-made-copilot-agent-launch-by-name.md)  
   Records an unverified observation from Phase 5 Task 4: the ready-made/default Copilot appears to "launch" a named custom `.agent` when asked in natural language, but its cited sources suggest it may be self-answering rather than truly handing off to that agent's distinct instructions. Do not treat as confirmed until verified per that note's method.

8. [`field-note-aspx-vs-markdown-grounding-comparison.md`](field-note-aspx-vs-markdown-grounding-comparison.md)  
   Records tenant-tested findings from Phase 5's Task 7/8 live comparison of two grounding formats. Two reproducible failure modes appeared on **both** agents regardless of format — inferring "currency" from file-upload timestamps instead of real review metadata, and giving mutually contradictory confident answers across repeated runs of a cross-topic-relationship question — suggesting model-level rather than format-specific behavior. One single-case finding suggests a possible Markdown-side ambiguity-handling advantage, not yet confirmed at scale.

### Content creation, curation, and Markdown

7. [`research-summary-native-markdown-sharepoint-onedrive.md`](research-summary-native-markdown-sharepoint-onedrive.md)  
   Examines native Markdown viewing, editing, versioning, and governance in SharePoint and OneDrive, along with source-of-truth and agent-grounding implications.

8. [`research-summary-sharepoint-ai-forward-content-creation-curation.md`](research-summary-sharepoint-ai-forward-content-creation-curation.md)  
   Extends the lifecycle beyond conversion into AI-assisted creation, review, publication, continuous curation, knowledge health, and agent readiness.

9. [`concept-dual-target-rendering-agent-vs-human.md`](concept-dual-target-rendering-agent-vs-human.md)  
   Defines the dual-target rendering model separating rich, styled human-facing output from token-dense, instruction-embedded agent-optimized publication digests.

## Suggested Reading Paths

### For the overall vision

```text
AI in SharePoint research summary
→ capability layering
→ SharePoint agents and native skills as outputs
```

### For implementation decisions

```text
Copilot in SharePoint research summary
→ AgentAssets field note
→ skill runtime decision guide
```

### For structured-content architecture

```text
Native Markdown research summary
→ content creation and curation research
→ SharePoint agents and native skills as outputs
```

### For platform selection

```text
Capability layering
→ skill runtime decision guide
```

## Key Research Findings

### Markdown is transitional during conversion but can be structured afterward

Raw DOCX-to-Markdown output is an intermediate extraction. It still requires analysis, restructuring, cleanup, validation, and packaging. Approved Markdown topics may then become maintainable structured content if identity, lineage, metadata, review, and publication controls are preserved.

### Content creation and curation are one lifecycle

Creating more content without maintaining, governing, superseding, and retiring it recreates content chaos. The future model must support continuous content health, not only initial migration.

### SharePoint skills fill a genuine middle-layer gap

Native skills are more procedural than simple agent conversations but less complex than a full Copilot Studio solution. They are an appropriate target for lightweight, site-local knowledge operations.

### Similar `SKILL.md` files do not imply equivalent runtimes

Repository, SharePoint, and Cowork skill definitions may look structurally similar while supporting different tools, permissions, deployment methods, and guarantees. Each target requires its own capability contract and evaluation suite.

### Dual-target rendering resolves human visual vs. agent indexing conflicts

Human readers need rich layout, CSS, breadcrumbs, and visual formatting, whereas AI indexing agents need high semantic density, token-efficient chunking, and clear citation instructions. Rendering the single structured source of truth into distinct human-facing and agent-optimized publication targets resolves context window and index crawler limitations while providing rich display links to users.

### The studio should define capabilities once and compile for targets

A target-neutral capability specification can prevent drift across runtime implementations.

```text
capabilities/
  review-manual-topics/
    capability-spec.md
    governance-policy.md
    evaluation-cases/
    targets/
      github/
      sharepoint/
      cowork/
      copilot-studio/
```

### Recommendation must remain separate from action

Every capability should make its operating mode explicit:

```text
Explore
Design
Prepare
Execute
Monitor
```

AI-generated proposals must not silently become content changes, metadata updates, approvals, publications, retirements, or deletions.

## Government-Specific Controls

The workbench vision adds controls beyond the product demonstrations reviewed in this research:

- accountable ownership;
- human confirmation of authoritative metadata;
- content, publication, and release approval;
- least privilege and separation of duties;
- security, privacy, and sensitivity review;
- oversharing prevention;
- records classification, retention, legal hold, and disposition;
- accessibility;
- audit evidence;
- deployment authorization;
- rollback and recovery;
- source-of-truth and metadata-authority decisions;
- evaluation before agents or skills are treated as operationally ready.

## Current Evidence

The research bundle contains both product research and tenant-tested evidence.

Tenant-tested evidence currently includes:

- creation of a native SharePoint skill after establishing the `AgentAssets` document library;
- generation of a structured `review-manual-topics` `SKILL.md`;
- a skill definition containing YAML front matter, trigger phrases, inputs, ordered steps, SharePoint list operations, failure guidance, and a defined output format.

This evidence does not yet prove every custom-agent-to-skill invocation scenario. Agent discovery, sharing, permissions, Markdown grounding, cross-site portability, deployment automation, and lifecycle promotion still require controlled testing.

## Near-Term Research and Pilot Priorities

1. Complete and evaluate the structured-content pilot.
2. Confirm maintainable topic boundaries and publication-map behaviour.
3. Test a bounded SharePoint Markdown authoring and approval model.
4. Harden and evaluate the `review-manual-topics` native skill.
5. Verify how custom SharePoint agents discover or invoke native skills.
6. Test supported knowledge-source formats, including Markdown retrieval and citation.
7. Define governance for `AgentAssets`, including authoring rights and approval.
8. Define a target-neutral capability specification.
9. Pilot one hybrid capability with repository and SharePoint implementations.
10. Evaluate whether broader distribution belongs in Cowork or integrated processing belongs in Copilot Studio.

## Repository Conventions Recommended by This Research

- Keep product research separate from approved architecture decisions.
- Label tenant observations as empirical evidence.
- Label proposed capabilities as design candidates until tested.
- Preserve source URLs and retrieval limitations in research notes.
- Maintain target-specific implementations beneath a shared capability specification.
- Add evaluation cases before deployment.
- Keep package-only and design-only modes available when platform write permissions are unavailable.
- Do not store unrestricted production credentials in the repository.
- Update applicable plugin and marketplace metadata when implementation changes introduce repository-distributed capabilities.

## Status

This directory is a research and architecture foundation. It does not authorize production deployment, tenant-wide enablement, external connectors, Entra permissions, or automated SharePoint modification.

Product names, preview status, supported actions, licensing, billing, packaging formats, and tenant availability may change. Verify each proposed target against current Microsoft documentation, the intended tenant, and organizational policy before implementation.
