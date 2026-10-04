# SharePoint Agents and Native SharePoint Skills as Outputs of the AI-Assisted Knowledge Workbench

**Purpose:** Define how SharePoint agents and native Copilot in SharePoint skills differ from repository-based GitHub Copilot agents and skills, where they are created and stored, what licensing and permissions they require, how they become accessible in SharePoint, and how the proposed knowledge workbench can generate them as governed deployment outputs.  
**Status:** Architecture and research note; not implementation or deployment authorization.  
**Primary Microsoft sources:**

- [Get started with Copilot in SharePoint (preview)](https://learn.microsoft.com/en-us/SharePoint/copilot-in-sharepoint-get-started)
- [Extend Copilot in SharePoint with skills](https://learn.microsoft.com/en-us/sharepoint/ai-in-sharepoint-skills)
- [Frequently asked questions about agents in SharePoint](https://support.microsoft.com/en-us/office/frequently-asked-questions-about-agents-in-sharepoint-bdcf4a1a-3e5a-4f95-93f6-6e3d1a3e5a4f)

> Verify current Microsoft documentation, tenant availability, licensing, and organizational policy before implementation. Copilot in SharePoint is documented as a preview capability, and product behaviour, names, limits, and enablement may change.

## 1. Executive Summary

The AI-Assisted SharePoint Knowledge Workbench can produce more than structured content and publication packages. Two important deployment targets are:

1. **Native Copilot in SharePoint skills** — constrained, reusable, site-scoped workflows stored as Markdown in SharePoint.
2. **SharePoint agents** — purpose-specific conversational knowledge experiences grounded in selected SharePoint content.

These outputs are not equivalent to the agents and skills implemented in a GitHub repository.

```text
GitHub Copilot / VS Code Knowledge Workbench
    |
    | designs, generates, tests, reviews, versions, and packages
    v
Governed deployment artifacts
    |
    +-- Structured Markdown topics
    +-- Publication maps
    +-- SharePoint schema specifications
    +-- Native SharePoint SKILL.md definitions
    +-- SharePoint agent definition packages
    +-- Evaluation sets
    +-- Deployment manifests and evidence
    |
    v
SharePoint Online
    |
    +-- Governed knowledge libraries
    +-- Native Copilot in SharePoint skills
    +-- SharePoint agents
    +-- Metadata, permissions, versioning, approvals, and audit history
```

The workbench is the engineering and design environment. Native SharePoint skills and SharePoint agents are deliberately narrower runtime outputs.

## 2. Four Different Artifact Types

Use the following terms consistently.

### 2.1 Repository Agent

A repository agent is an interactive GitHub Copilot or development-environment agent that can orchestrate repository tools, scripts, tests, and approved integrations.

Examples:

```text
knowledge-workbench-agent
structured-knowledge-conversion-agent
sharepoint-knowledge-governance-agent
knowledge-insight-agent
sharepoint-agent-designer
```

A repository agent may coordinate:

- Python or PowerShell;
- Pandoc and LibreOffice;
- Git branches, commits, and pull requests;
- schemas and contracts;
- unit, integration, and regression tests;
- deterministic validation;
- package generation;
- deployment preparation;
- approved external APIs or tools.

### 2.2 Repository Skill

A repository skill is a bounded capability stored and versioned in the Git repository for use by GitHub Copilot or another repository agent environment.

Examples:

```text
analyze-document
convert-document
generate-content-metadata
generate-publication-map
design-sharepoint-agent
evaluate-sharepoint-agent
```

A repository skill may invoke custom code and command-line tools when the repository environment and policy permit it.

### 2.3 Native SharePoint Skill

A native SharePoint skill is a reusable, multi-step workflow interpreted by Copilot in SharePoint.

Microsoft documents that native skills can encode organization-specific rules such as document standards and review checklists. A user can describe the workflow in natural language, review and revise the draft, explicitly confirm that it should be saved, and reuse it in later prompts.

Native SharePoint skills:

- use capabilities already supported by Copilot in SharePoint;
- operate within the current user's permissions;
- do not provide additional access;
- cannot connect to external systems;
- cannot execute arbitrary custom code.

### 2.4 SharePoint Agent

A SharePoint agent is a purpose-specific conversational experience grounded in selected SharePoint sources.

Conceptually:

```text
Purpose
+ behaviour instructions
+ selected SharePoint knowledge sources
+ user access to those sources
= SharePoint agent
```

A SharePoint agent is primarily a consumption, discovery, and guidance experience. It is not equivalent to a repository development agent with arbitrary tools, code execution, source control, tests, or external-system orchestration.

## 3. Where Native SharePoint Skills Are Created

Microsoft documents creation through the **Copilot in SharePoint chat panel** on a SharePoint site page or document library.

The documented pattern is:

```text
Open Copilot in SharePoint
→ describe the repeatable workflow in natural language
→ review the generated skill draft
→ revise steps, inputs, or outputs if needed
→ explicitly confirm that the skill should be saved
```

After saving, Copilot in SharePoint may automatically load a relevant skill based on the request, or the user may invoke the skill explicitly by name.

This resembles the workbench's human-confirmation pattern:

```text
Describe
→ Draft
→ Review
→ Confirm
→ Save
→ Use
```

## 4. Where Native SharePoint Skills Are Stored

Microsoft documents the location as:

```text
SharePoint site
└── Agent Assets
    └── Skills
        └── <skill-name>
            └── SKILL.md
```

The exact documented path is:

```text
/Agent Assets/Skills/<skill-name>/SKILL.md
```

The **Agent Assets** library is created and managed by the product. Microsoft states that the library cannot be deleted.

The underlying skill definition is Markdown and may be reviewed directly. If edited directly, its expected structure must remain intact so Copilot in SharePoint can continue to interpret it.

Standard SharePoint governance can apply to skill files, including:

- permissions;
- retention;
- sensitivity labels;
- auditing;
- version history.

## 5. Who Can Create and Run Native SharePoint Skills

Microsoft documents the following default permissions:

```text
Edit permission
→ create skills

View permission
→ run skills
```

Microsoft also documents that permission inheritance can be broken on the Agent Assets library when a more restrictive model is required.

For regulated use, the default may be too broad for some sites. A proposed operating model is:

```text
Site viewer
→ run approved skills

Content editor
→ edit operational content, but not automatically author skills

Skill author
→ draft native skills

Skill reviewer or owner
→ review purpose, steps, risks, permissions, and evaluation evidence

Site owner
→ manage availability, Agent Assets permissions, and approved deployment
```

This role model is a project recommendation, not a Microsoft-prescribed requirement.

## 6. Licensing and Availability for Native SharePoint Skills

Native skills require a SharePoint site where **Copilot in SharePoint is available**.

Microsoft documents Copilot in SharePoint as part of the Microsoft 365 Copilot preview experience. During the documented preview:

- users require an active Microsoft 365 Copilot license;
- Copilot in SharePoint is included with that license;
- the feature rolls out as an opt-out preview for licensed users;
- tenant and site availability can be controlled administratively.

Microsoft documents availability scopes using `KnowledgeAgentScope`:

```text
AllSites
IncludeSelectedSites
ExcludeSelectedSites
NoSites
```

The selected-sites list supports up to 100 site URLs during the documented preview.

Microsoft also states that Restricted Content Discovery is respected. If Restricted Content Discovery is enabled for a site, Copilot in SharePoint and AI actions do not appear on that site.

### Government-cloud limitation

Microsoft's documentation states that Copilot in SharePoint is not currently supported in:

- GCC;
- GCC High;
- Department of Defense environments;
- Office 365 air-gapped environments;
- Microsoft 365 operated by 21Vianet.

Do not assume this excludes every public-sector tenant. Verify the actual target tenant cloud and current Microsoft availability.

## 7. Native SharePoint Skill Capability Boundary

Native SharePoint skills are intentionally constrained.

Microsoft states that a native skill:

- can chain built-in Copilot in SharePoint capabilities into a repeatable process;
- can understand and summarize content where supported;
- can organize files and folders where supported;
- can interact with SharePoint content such as lists where supported;
- can only perform actions the user is already permitted to perform;
- cannot connect to external systems;
- cannot execute custom code;
- cannot introduce a capability not already available in Copilot in SharePoint.

Therefore, a native skill cannot directly replace repository capabilities such as:

```text
python -m scripts.cli convert
pytest
pandoc
LibreOffice
Git branch or pull request creation
custom database access
arbitrary Microsoft Graph calls
external workflow engines
custom deterministic validators
```

## 8. Where SharePoint Agents Are Created

SharePoint agents are created through the native SharePoint agent creation experience available on modern SharePoint sites to users with the necessary permissions and licensing or configured billing.

A creator configures a tailored agent for a specific purpose and selects SharePoint knowledge sources.

The resulting agent is a configured platform artifact rather than a custom-code agent runtime.

## 9. What SharePoint Agent Knowledge Sources Can Include

Microsoft documents that a SharePoint agent can use selected source items such as:

- SharePoint sites;
- document libraries;
- folders;
- files.

Microsoft currently documents a limit of up to **20 source items** for an agent. A higher-level source, such as a site, library, or folder, may include underlying content without selecting every file separately.

Agent responses remain permission-trimmed. A user receives information only from selected sources that the user is already authorized to access.

### Important source-format caution

The current Microsoft agent FAQ lists supported document and web formats but does not list Markdown among the supported formats in the retrieved documentation. Separate community testing has reported inconsistent Markdown retrieval when `.md` files are stored in SharePoint libraries and used through SharePoint knowledge sources.

Therefore:

```text
Native Markdown browser support
≠ confirmed SharePoint agent grounding support
```

Validate Markdown retrieval and citation in the target tenant before relying on `.md` files as direct agent knowledge sources.

Possible interim patterns include:

- approved rendered HTML or SharePoint pages;
- approved Word, PDF, text, or other documented supported formats;
- a governed index or summary page linking to structured Markdown;
- a dual-output model where Markdown remains structured and an approved agent-facing representation is generated.

## 10. Licensing for SharePoint Agents

Microsoft documents that SharePoint agents can be used when either:

- the user has a Microsoft 365 Copilot license; or
- the organization has configured Pay-As-You-Go billing for SharePoint agents.

Licensing, availability, supported files, and limits should be verified against current Microsoft documentation and the target tenant before a pilot.

Copilot in SharePoint itself has separate preview availability and licensing requirements. Do not assume that access to one Microsoft agent experience automatically enables every Copilot in SharePoint capability.

## 11. Where SharePoint Agents Are Accessible

Microsoft documents that SharePoint agents can be accessed from SharePoint locations such as:

- a SharePoint site;
- a SharePoint page;
- a document library.

Agents may also be used in Teams when added there. Microsoft documentation also describes agents used in SharePoint becoming accessible from the Microsoft 365 Copilot Chat left rail after the user has interacted with the agent.

The agent's availability does not override content permissions.

For a useful agent experience, the agent must be:

- created in an approved SharePoint environment;
- scoped to approved knowledge sources;
- shared with the intended users;
- supported by user access to the underlying sources;
- evaluated for purpose, grounding, current content, and permissions.

## 12. SharePoint Agents and Native Skills Are Separate Artifacts

A SharePoint agent and a native SharePoint skill are not the same artifact.

### SharePoint Agent

```text
Purpose
+ instructions
+ knowledge sources
+ behaviour
+ source permissions
= conversational knowledge experience
```

### Native SharePoint Skill

```text
Repeatable workflow
+ organization-specific rules
+ supported Copilot in SharePoint actions
+ user permissions
= reusable site-scoped process
```

An agent may use supported native skills, but the agent definition and skill definition have different purposes and lifecycle concerns.

## 13. The Studio as the Design and Compilation Environment

The workbench can be treated as a compiler, test environment, and release-management system for SharePoint-native artifacts.

```text
Organizational standards and business intent
        +
Structured content and metadata
        +
Workflow requirements
        +
SharePoint platform constraints
        ↓
AI-Assisted Knowledge Workbench
        ↓
Validated SharePoint-native deployment artifacts
```

Potential output targets include:

```text
Target: Structured Markdown package
Target: SharePoint content-model specification
Target: SharePoint deployment package
Target: Native SharePoint SKILL.md
Target: SharePoint agent definition package
Target: Approval-workflow specification
Target: Agent evaluation set
Target: Publication output
Target: Evidence package
```

## 14. Native SharePoint Skills as Workbench Outputs

A workbench-generated native skill package could contain:

```text
sharepoint-native-skills/
  review-manual-topic/
    SKILL.md
    deployment-manifest.json
    governance-metadata.json
    evaluation-cases.md
    permission-assumptions.md
    source-specification.md
```

The package should record:

- skill name and purpose;
- intended site;
- supported inputs;
- expected outputs;
- workflow steps;
- prohibited actions;
- expected user permissions;
- owner;
- review date;
- sensitivity or classification decision, if applicable;
- version;
- evaluation cases;
- deployment method;
- evidence requirements.

The workbench should validate that a native skill contains no repository-only assumptions such as Python, PowerShell, Git, external APIs, or custom executables.

## 15. SharePoint Agents as Workbench Outputs

A workbench-generated SharePoint agent package could contain:

```text
sharepoint-agents/
  sample-knowledge-agent/
    agent-purpose.md
    behaviour-instructions.md
    knowledge-sources.json
    permission-assumptions.md
    prohibited-behaviours.md
    escalation-rules.md
    evaluation-set.json
    readiness-report.md
    deployment-manifest.json
```

The package should define:

- agent purpose;
- intended users;
- approved source scope;
- expected source permissions;
- response boundaries;
- treatment of insufficient evidence;
- treatment of stale, unapproved, or conflicting content;
- escalation behaviour;
- questions the agent should answer;
- questions the agent should decline or escalate;
- owner and review date;
- evaluation suite;
- deployment and sharing instructions;
- monitoring requirements.

The workbench may generate and validate this package without automatically creating the agent in SharePoint.

## 16. Shared Specification, Different Implementations

A repository skill and native SharePoint skill may implement the same business intent using different capabilities.

Example shared intent:

```text
Review a manual topic against an approved content standard.
```

### Repository implementation

```text
Run schema validation
→ test links and media
→ inspect publication map
→ compare content hash and lineage
→ produce machine-readable evidence
```

### Native SharePoint implementation

```text
Review selected content
→ apply a supported checklist
→ identify missing visible metadata
→ summarize findings
→ record unresolved items in a SharePoint list
→ ask the reviewer for disposition
```

The business workflow is shared. The implementations are target-specific.

A direct copy of a repository `SKILL.md` into Agent Assets should not be assumed to work.

## 17. Deployment Patterns

The workbench should support multiple deployment paths.

### 17.1 Manual Native Skill Creation

```text
Workbench creates reviewed skill specification
→ authorized user opens Copilot in SharePoint
→ user asks Copilot to create the skill
→ user compares the draft with the specification
→ user confirms save
→ SharePoint stores SKILL.md in Agent Assets
→ evaluation is run
```

### 17.2 Manual SharePoint Agent Creation

```text
Workbench creates agent definition package
→ authorized user opens SharePoint agent builder
→ user configures purpose, instructions, and approved sources
→ user saves and shares the agent
→ evaluation suite is run
→ result and evidence are recorded
```

### 17.3 Authorized Automated Deployment

```text
Workbench creates validated deployment package
→ approved platform adapter uses approved identity and permissions
→ artifact is deployed through a supported interface
→ deployment is verified
→ evidence and rollback information are recorded
```

This mode requires separately verified Microsoft interfaces, Microsoft Entra authorization, target-site access, change control, and operational ownership.

### 17.4 Package-Only Mode

```text
Workbench produces artifacts and instructions
→ no platform write occurs
```

Package-only mode must remain available when direct SharePoint automation is not approved.

## 18. Direct Modern-Page and Web-Part Publishing

Native Copilot in SharePoint may create supported SharePoint content through Microsoft's product experience and the user's existing permissions.

External workbench code that creates or modifies SharePoint pages, `.aspx` artifacts, layouts, or web parts is a separate publishing capability. It may require:

- an approved Microsoft Entra application or delegated identity;
- administrator consent;
- least-privilege Microsoft Graph or SharePoint permissions;
- explicit target-site authorization;
- certificate or workload-identity management;
- conditional-access compliance;
- audit evidence;
- rollback.

Architecture rule:

> Prefer native Copilot in SharePoint capabilities for supported interactive content operations. Treat external page or web-part publishing as a separately authorized adapter. Never manipulate raw `.aspx` markup as though it were structured content.

## 19. Validation Requirements for Native SharePoint Skills

Before a native skill is accepted, verify:

- the workflow is within documented native capabilities;
- no external systems or custom code are assumed;
- inputs and outputs are clear;
- user permissions are identified;
- recommendation and action are separated;
- approval is never inferred;
- destructive actions require explicit confirmation;
- owner, purpose, status, and review date are recorded;
- evaluation cases cover normal, negative, and ambiguous scenarios;
- the skill does not expose restricted information;
- the deployed `SKILL.md` matches the approved definition.

## 20. Validation Requirements for SharePoint Agents

Before a SharePoint agent is accepted, verify:

- the purpose is bounded and understandable;
- sources are approved and current;
- intended users have access to the selected sources;
- oversharing and sensitivity risks were reviewed;
- obsolete or superseded content is excluded or clearly handled;
- contradictory content is resolved or documented;
- agent instructions address insufficient evidence;
- escalation behaviour is defined;
- the evaluation set includes:
  - answerable questions;
  - unanswerable questions;
  - ambiguous questions;
  - sensitive-content questions;
  - stale-content questions;
  - cross-topic questions;
  - procedure questions;
  - exception questions;
- responses are checked for grounding and permission behaviour;
- the owner, review date, source scope, and deployment evidence are recorded.

## 21. Governance Requirements

### 21.1 Skill Authoring Rights

Decide whether ordinary site editors may create skills or whether Agent Assets permissions should be restricted.

### 21.2 Human Approval

AI-generated skill drafts, agent instructions, and proposed knowledge scopes require human review before deployment.

### 21.3 Oversharing

Permission trimming does not correct an already overshared site. AI can make permitted content easier to discover. Source-scope and permission review remain mandatory.

### 21.4 Records and Retention

Determine the records treatment of:

- skill definitions;
- agent definitions;
- evaluation results;
- deployment manifests;
- chat or execution evidence;
- approval records;
- superseded versions.

### 21.5 Security and Privacy

Review:

- tenant cloud and availability;
- site permissions;
- Restricted Content Discovery;
- sensitivity labels;
- protected-information handling;
- sharing controls;
- auditability;
- incident response.

### 21.6 Accessibility

Agent and skill outputs should support accessible content and must not replace accessibility validation.

### 21.7 Separation of Duties

Where risk warrants it, separate:

```text
artifact author
artifact reviewer
site deployer
content approver
evaluator
operational owner
```

## 22. Recommended Operating Modes

The workbench should expose explicit modes.

### Explore

- inspect product or site state;
- analyze sources;
- make no changes.

### Design

- create skill and agent specifications;
- propose source scopes and workflows;
- make no platform changes.

### Prepare

- generate deployment packages and evaluation sets;
- prepare manual deployment instructions;
- make no platform changes.

### Execute

- create, save, share, or deploy native skills or agents;
- require approved authorization and evidence.

### Monitor

- assess source freshness, permissions, skill usage, evaluation drift, and agent readiness;
- make no destructive action without approval.

## 23. Suggested Pilot

### Phase A — Workbench Preparation

1. Complete the structured-content pilot.
2. Define a manageable topic package and publication map.
3. Select one low-risk native SharePoint workflow.
4. Create a native skill specification and evaluation cases.
5. Create one bounded SharePoint agent definition and readiness report.

### Phase B — Site Preparation

1. Verify target tenant support and licensing.
2. Confirm Copilot in SharePoint site availability.
3. Review Restricted Content Discovery, permissions, and sensitivity.
4. Decide who can create and run native skills.
5. Decide how Agent Assets is governed.

### Phase C — Native Skill Trial

1. Create one native skill through the documented SharePoint experience.
2. Review the generated draft before saving.
3. Confirm the stored `SKILL.md` location and content.
4. Run the evaluation set against controlled content.
5. Record results, permissions, and evidence.

### Phase D — SharePoint Agent Trial

1. Create a purpose-specific agent with approved sources.
2. Share it with a controlled participant group.
3. Run the approved evaluation suite.
4. Check grounding, permissions, stale-content handling, and escalation.
5. Record limitations and required remediations.

### Phase E — Architecture Decision

Determine:

- which artifacts remain repository-only;
- which workflows are suitable for native skills;
- which content representations work reliably as agent sources;
- whether manual deployment is sufficient;
- whether an external deployment adapter is justified;
- which licensing and governance model is sustainable.

## 24. Key Architecture Principles

```text
The workbench is the design, engineering, testing, and evidence environment.

Repository skills may use custom code and tools.

Native SharePoint skills are constrained, site-scoped workflows stored in Agent Assets.

SharePoint agents are constrained, permission-aware knowledge experiences.

The studio may generate both, but generation does not equal deployment or approval.

Every deployment target requires its own contract, validator, evaluation, owner, and lifecycle.

Package-only mode remains valid when platform automation is not authorized.
```

## 25. Research and Verification Notes

Verify the following against current Microsoft documentation and the target tenant before implementation:

- Copilot in SharePoint preview or general-availability status;
- tenant-cloud support;
- Microsoft 365 Copilot licensing;
- Pay-As-You-Go availability for SharePoint agents;
- current source-item limits;
- supported agent knowledge-source formats;
- native skill actions;
- Agent Assets behaviour and permissions;
- administrative availability controls;
- audit, retention, and sensitivity capabilities;
- supported automated deployment interfaces;
- Markdown retrieval and citation behaviour for agents.

Product documentation and preview behaviour may change.
