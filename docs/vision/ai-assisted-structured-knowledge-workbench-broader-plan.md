# Broader Initiative Plan — AI-Assisted Structured Knowledge Workbench

**Current repository:** [richfrem/manual-conversion-poc](https://github.com/richfrem/manual-conversion-poc)  
**Recommended initiative name:** **AI-Assisted Structured Knowledge Workbench**  
**Recommended repository name:** `structured-knowledge-workbench`  
**Recommended Phase 1 name:** **Structured Knowledge Conversion and Canonical Content POC**  
**Existing Phase 1 plugin:** `docx-to-content`  
**Status:** Proposed direction for structured brainstorming and implementation planning. This document does not authorize a repository rename, destructive restructuring, production deployment, or automatic migration of every research idea into backlog scope.

## 1. Executive Decision

The initiative has outgrown the name `manual-conversion-poc`.

The original repository name accurately described the starting experiment, but no longer describes the emerging scope:

```text
Legacy document conversion
→ canonical structured knowledge
→ publication assembly
→ SharePoint knowledge governance
→ native SharePoint skills
→ SharePoint agents
→ Copilot Cowork packages
→ Copilot Studio integrations
→ evaluation, monitoring, and lifecycle management
```

The recommended umbrella is:

```text
AI-Assisted Structured Knowledge Workbench
```

The recommended repository name is:

```text
structured-knowledge-workbench
```

This name is intentionally broader than SharePoint. SharePoint is a major operational and deployment platform, but canonical knowledge, validation, rendering, repository skills, Cowork packaging, and other outputs should not be architecturally defined as SharePoint-only.

Keep these lower-level names:

```text
Phase 1:
Structured Knowledge Conversion and Canonical Content POC

Phase 1 implementation plugin:
docx-to-content

Phase 1 pilot content:
CEIS Manual
```

This preserves the history and bounded purpose of the existing implementation while giving the broader initiative an accurate name.

## 2. Should the Repository Be Renamed?

### Recommendation

**Yes, probably—but only after a repository inventory and compatibility review.**

Rename the existing repository if it is still principally an evolving proof-of-concept workspace and does not yet have external consumers depending on the current URL, package coordinates, release assets, GitHub Pages address, workflows, badges, or hard-coded references.

Do not rename merely for cosmetic alignment. First assess the change surface.

### Why renaming is justified

The current name implies:

- one narrow conversion experiment;
- Word/manual conversion as the enduring product boundary;
- temporary POC status;
- no broader capability or plugin architecture.

The planned repository now encompasses or may encompass:

- canonical-content architecture;
- document-conversion plugins;
- SharePoint knowledge governance;
- native SharePoint skill generation;
- SharePoint agent design and evaluation;
- publication maps and renderers;
- capability routing;
- Cowork packaging;
- Copilot Studio specifications;
- research, standards, evaluations, and evidence.

### Rename gate

Before renaming, inventory:

```text
README links
GitHub Actions workflows
GitHub Pages configuration
badges
marketplace and plugin manifests
package metadata
release automation
issue and PR links
documentation links
clones or submodules
external references
local remotes
hard-coded repository URLs
```

### Rename options considered

#### Recommended: `structured-knowledge-workbench`

Strengths:

- describes the durable product concept;
- remains platform-neutral;
- supports multiple plugins and deployment targets;
- does not imply production readiness;
- includes conversion without being limited to conversion.

#### Alternative: `ai-structured-knowledge-workbench`

Strengths:

- makes AI explicit.

Weakness:

- the durable architecture should continue to make sense even where deterministic tooling performs the work.

#### Alternative: `sharepoint-knowledge-workbench`

Strengths:

- clear operational target.

Weakness:

- too narrow for canonical content, multi-format rendering, GitHub skills, Cowork packaging, and non-SharePoint targets.

#### Not recommended: keep `manual-conversion-poc` indefinitely

Weaknesses:

- materially understates the expanded architecture;
- invites unrelated capabilities to accumulate under a misleading name;
- makes plugin and roadmap boundaries harder to explain.

## 3. One Repository or Several?

### Initial recommendation

Use **one workbench repository with multiple bounded plugins**, not several repositories yet.

The technology is not intrinsically complex. Most near-term work is:

- contracts;
- Markdown skills;
- deterministic Python or PowerShell utilities;
- schemas;
- tests;
- deployment packages;
- documentation;
- evaluation suites.

A single repository supports:

- shared schemas and standards;
- one capability catalogue;
- shared evaluation infrastructure;
- consistent plugin conventions;
- simpler agent routing;
- easier refactoring while boundaries are still being learned.

### Split-repository triggers

Reconsider separate repositories only when one or more of these becomes true:

- a plugin has a distinct release cadence;
- a plugin has materially different security or access requirements;
- a plugin needs independent ownership;
- a plugin has separate consumers and versioning commitments;
- repository size or CI becomes operationally burdensome;
- a deployment target needs an isolated public distribution package;
- credentials, licensing, or compliance require separation.

Do not create separate repositories merely because capabilities have different names.

## 4. Should There Be More Than One Plugin?

### Recommendation

**Yes. Do not turn `docx-to-content` into a catch-all plugin.**

Use multiple plugins grouped by coherent responsibility and runtime. The initial proposed plugin set is:

```text
docx-to-content
sharepoint-knowledge
knowledge-publication
knowledge-evaluation
```

Add Cowork or Copilot Studio packaging plugins later only when implementation is justified by a real pilot.

### Plugin 1 — `docx-to-content`

Purpose:

- ingest DOCX;
- extract temporary Markdown and media;
- analyze structure;
- normalize source artifacts;
- propose and confirm topic boundaries;
- create canonical topics;
- preserve structural anchors and lineage;
- validate fidelity;
- produce canonical package evidence.

This remains the Phase 1 implementation plugin.

It must not absorb:

- SharePoint tenant administration;
- SharePoint agent creation;
- Cowork packaging;
- Copilot Studio deployment;
- generic records-management integration.

### Plugin 2 — `sharepoint-knowledge`

Purpose:

- design SharePoint knowledge-library schemas;
- map canonical metadata to SharePoint fields;
- prepare governed deployment packages;
- generate native SharePoint-compatible `SKILL.md` artifacts;
- generate SharePoint agent definition packages;
- assess content and agent readiness;
- prepare library-health and review workflows;
- validate `AgentAssets` target assumptions;
- preserve package-only mode when no SharePoint write identity is approved.

Suggested skill groups:

```text
library-design/
metadata/
native-skills/
agents/
governance/
health/
deployment/
```

Examples:

```text
design-sharepoint-content-model
generate-sharepoint-metadata-map
prepare-sharepoint-deployment-package
generate-native-sharepoint-skill
validate-native-sharepoint-skill
assess-agent-readiness
design-sharepoint-agent
evaluate-sharepoint-agent
assess-library-health
prepare-content-review
```

### Plugin 3 — `knowledge-publication`

Purpose:

- own publication-map contracts;
- assemble canonical topics;
- render Word, PDF, HTML, PowerPoint, or other products;
- generate navigation;
- apply presentation templates;
- validate publication-level coherence;
- maintain release manifests.

This plugin should remain independent of the source-conversion plugin because canonical content may eventually come from sources other than DOCX.

Suggested skills:

```text
generate-publication-map
validate-publication-map
assemble-publication
render-knowledge-product
validate-rendered-output
prepare-publication-release
```

### Plugin 4 — `knowledge-evaluation`

Purpose:

- define reusable evaluation schemas;
- evaluate canonical-content fidelity;
- evaluate native SharePoint skill behaviour;
- evaluate SharePoint agent grounding and permissions;
- test stale, ambiguous, sensitive, and unsupported cases;
- produce comparable evidence across deployment targets.

This may begin as shared repository infrastructure rather than a separately published plugin. Promote it to a plugin only when consumers need to invoke it independently.

### Later candidate — `copilot-extension-packager`

Do not build yet.

Possible purpose:

- generate Cowork plugin packages;
- create Microsoft 365 app manifests;
- package Agent Skills and references;
- produce Copilot Studio design or import artifacts where supported;
- validate target-specific capability limitations.

Create only after one capability has proven value in a broader distribution pilot.

## 5. Agent Architecture

Use a small number of agents. Do not create one agent per skill.

### Top-level agent — `knowledge-workbench-agent`

Responsibilities:

- understand user intent;
- choose a user journey;
- identify the correct plugin and runtime;
- distinguish Explore, Design, Prepare, Execute, and Monitor;
- invoke bounded domain agents or skills;
- stop at confirmation gates;
- explain why a target was selected.

Suggested routing states:

```text
DOC_CONVERSION_REQUIRED
CANONICAL_CONTENT_REQUIRED
PUBLICATION_REQUIRED
NATIVE_SHAREPOINT_SKILL_CANDIDATE
SHAREPOINT_AGENT_CANDIDATE
SHAREPOINT_DEPLOYMENT_PACKAGE_REQUIRED
COWORK_PACKAGE_CANDIDATE
COPILOT_STUDIO_REQUIRED
HYBRID_MULTI_TARGET_RECOMMENDED
CAPABILITY_NOT_VERIFIED
HUMAN_DECISION_REQUIRED
```

### Domain agent — `structured-knowledge-conversion-agent`

Owns the `docx-to-content` journey.

### Domain agent — `sharepoint-knowledge-agent-designer`

Owns SharePoint library, native skill, and SharePoint agent design journeys.

### Domain agent — `knowledge-publication-agent`

Owns publication maps, assembly, rendering, and release evidence.

### Optional later agent — `knowledge-evaluation-agent`

Owns cross-target evaluation orchestration if evaluation complexity justifies an interactive agent.

### Agent creation rule

Create a domain agent only if it adds:

- meaningful orchestration across several skills;
- interactive decision-making;
- a distinct permission or risk boundary;
- a coherent user journey.

Otherwise, create a skill, not an agent.

## 6. Proposed Repository Structure

```text
structured-knowledge-workbench/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── CHANGELOG.md
│
├── .github/
│   ├── copilot-instructions.md
│   ├── agents/
│   │   ├── knowledge-workbench-agent.md
│   │   ├── structured-knowledge-conversion-agent.md
│   │   ├── sharepoint-knowledge-agent-designer.md
│   │   └── knowledge-publication-agent.md
│   └── workflows/
│
├── plugins/
│   ├── docx-to-content/
│   │   ├── plugin.json
│   │   ├── skills/
│   │   ├── scripts/
│   │   ├── schemas/
│   │   ├── tests/
│   │   └── docs/
│   │
│   ├── sharepoint-knowledge/
│   │   ├── plugin.json
│   │   ├── skills/
│   │   │   ├── library-design/
│   │   │   ├── metadata/
│   │   │   ├── native-skills/
│   │   │   ├── agents/
│   │   │   ├── governance/
│   │   │   ├── health/
│   │   │   └── deployment/
│   │   ├── schemas/
│   │   ├── templates/
│   │   ├── evaluations/
│   │   ├── tests/
│   │   └── docs/
│   │
│   ├── knowledge-publication/
│   │   ├── plugin.json
│   │   ├── skills/
│   │   ├── renderers/
│   │   ├── templates/
│   │   ├── schemas/
│   │   ├── tests/
│   │   └── docs/
│   │
│   └── knowledge-evaluation/
│       ├── plugin.json
│       ├── skills/
│       ├── schemas/
│       ├── fixtures/
│       ├── tests/
│       └── docs/
│
├── capabilities/
│   └── review-manual-topics/
│       ├── capability-spec.md
│       ├── governance-policy.md
│       ├── evaluation-cases/
│       └── targets/
│           ├── github/
│           ├── sharepoint/
│           ├── cowork/
│           └── copilot-studio/
│
├── standards/
│   ├── canonical-content/
│   ├── manual-topic/
│   ├── procedure/
│   ├── policy/
│   ├── training/
│   └── accessibility/
│
├── schemas/
│   ├── canonical-content/
│   ├── publication-map/
│   ├── sharepoint-metadata/
│   ├── native-skill/
│   ├── agent-definition/
│   └── evaluation/
│
├── docs/
│   ├── vision/
│   ├── architecture/
│   ├── phases/
│   ├── plans/
│   ├── decisions/
│   ├── research/
│   └── field-notes/
│
├── examples/
│   ├── ceis/
│   └── native-sharepoint-skills/
│
└── evidence/
    └── .gitkeep
```

### Restructuring caution

Do not perform a big-bang move of every existing file based only on this proposed tree.

First inventory:

- current paths;
- import dependencies;
- CLI assumptions;
- test fixtures;
- documentation links;
- workflow paths;
- plugin and marketplace manifests;
- generated output paths.

Then create a reviewed path-migration map.

## 7. Broader Phased Roadmap

## Phase 0 — Reframe and Plan the Initiative

Goal:

- establish the umbrella name;
- review repository rename impact;
- inventory current implementation and research;
- agree plugin and agent boundaries;
- write the implementation roadmap.

Outputs:

```text
initiative charter
repository inventory
rename decision
plugin boundary decision
agent boundary decision
proposed repository tree
migration map
phase backlog
architecture decision records
```

Exit gate:

- rename and restructure plan approved;
- no destructive move executed without path-impact evidence.

## Phase 1 — Structured Knowledge Conversion and Canonical Content POC

Goal:

- prove that the CEIS Word manual can become maintainable canonical knowledge.

Scope:

```text
DOCX extraction
structural analysis
cleanup
stable anchors
maintainable topic grouping
canonical topic IDs
source lineage
publication map
validation
rendered manual
release evidence
```

Keep the existing `docx-to-content` plugin and complete Task 17/18 work under the bounded approved plan.

Exit gate:

- canonical package is structurally valid;
- source fidelity evidence is accepted;
- approximately maintainable topic boundaries are accepted;
- publication reconstruction succeeds;
- no unexplained content-loss risk remains.

## Phase 2 — Publication and Renderer Separation

Goal:

- establish canonical content as independent of the original DOCX converter.

Scope:

- move or formalize publication-map ownership;
- separate renderer contracts;
- support at least one validated publication assembly path;
- preserve release identity and evidence;
- prove that canonical topics can be reused without rerunning DOCX conversion.

Exit gate:

- publication plugin or module consumes canonical content as an independent contract.

## Phase 3 — Governed SharePoint Knowledge Pilot

Goal:

- prove a bounded SharePoint operational model.

Scope:

- pilot knowledge library;
- minimal metadata schema;
- owner, status, review date, topic ID, publication ID, and validation state;
- versioning;
- permission review;
- topic and publication review;
- package-only versus authorized deployment paths;
- Markdown usability and agent-source format testing.

Exit gate:

- authors, reviewers, and owners can operate the content without undermining canonical identity or governance.

## Phase 4 — Native SharePoint Skills Pilot

Goal:

- prove that the workbench can produce governed native SharePoint skill artifacts.

Initial candidate:

```text
review-manual-topics
```

Additional candidates only after the first is evaluated:

```text
check-required-metadata
apply-content-outline
generate-quiz-from-content
prepare-content-review
identify-stale-content
```

Scope:

- `AgentAssets` governance;
- skill-authoring permissions;
- target-compatible `SKILL.md` generation;
- manual deployment initially;
- normal, negative, ambiguous, permission, and safety evaluations;
- version and evidence tracking.

Exit gate:

- at least one native skill has a repeatable deployment and evaluation process.

## Phase 5 — SharePoint Knowledge Agent Pilot

Goal:

- prove agent readiness, grounding, permissions, and lifecycle controls.

Scope:

- approved source scope;
- supported agent-facing source format;
- behaviour instructions;
- answer boundaries;
- stale and superseded-content handling;
- answerable and unanswerable evaluation cases;
- permission tests;
- agent ownership and review date.

Exit gate:

- agent produces acceptably grounded responses within the approved scope and limitations.

## Phase 6 — Multi-Target Capability Model

Goal:

- define one capability once and generate target-specific implementations.

Pilot capability:

```text
review-manual-topics
```

Targets:

```text
GitHub repository skill
Native SharePoint skill
SharePoint agent support package
```

Cowork and Copilot Studio targets remain optional until a validated need exists.

Exit gate:

- shared specification and evaluation cases prevent behavioural drift across at least two runtimes.

## Phase 7 — Cowork and Copilot Studio Evaluation

Goal:

- determine whether broader distribution or enterprise integration is justified.

Cowork evaluation:

- reusable skill-package value;
- organizational distribution;
- packaging and governance;
- overlap with native SharePoint skills.

Copilot Studio evaluation:

- connector or external-system need;
- richer workflow need;
- environment and capacity implications;
- operational ownership.

Exit gate:

- build only the target that has a concrete use case and accountable owner.

## Phase 8 — Scale, Promotion, and Operations

Potential scope:

- development/test/production promotion;
- centrally governed capability catalogue;
- lifecycle monitoring;
- release automation;
- skill and agent version drift detection;
- support model;
- reusable onboarding patterns;
- records and audit integration.

This phase should not be designed in detail until pilots establish real operational requirements.

## 8. Superpowers Planning Workflow

Use the repository's Superpowers-style workflow to convert this strategy into implementable plans.

### Step 1 — Brainstorming

Run structured brainstorming against this document and the actual repository.

Required questions:

- What is the smallest coherent umbrella product?
- Is `structured-knowledge-workbench` the correct repository name?
- Which existing files belong to Phase 1 versus shared infrastructure?
- Which proposed plugins are true release boundaries versus premature abstraction?
- What should remain one plugin until a second consumer exists?
- Which skills are duplicated or overlap?
- Which proposed agents add orchestration value?
- What must not be migrated blindly from research into backlog scope?
- Which assumptions need tenant experiments?
- Which actions require explicit user approval?

Required outputs:

```text
brainstorming record
open questions
decision candidates
rejected alternatives
risk register
recommended boundaries
```

### Step 2 — Repository Reconnaissance

Inspect the real repository rather than relying on the proposed tree.

Inventory:

```text
files and directories
plugin manifests
marketplace manifests
agents
skills
scripts
schemas
tests
workflows
documentation
research
fixtures
generated outputs
hard-coded paths and URLs
```

Output:

```text
current-state-repository-map.md
```

### Step 3 — Architecture Review

Adversarially review:

- rename value versus disruption;
- one repository versus several;
- plugin boundaries;
- shared-code placement;
- capability-spec model;
- test architecture;
- deployment separation;
- security and permission boundaries;
- premature abstractions;
- missing rollback.

Output:

```text
architecture-decision-report.md
```

Do not approve the proposed structure automatically.

### Step 4 — Write Phase Plans

Produce one implementation plan per approved phase, not one massive plan.

Recommended sequence:

```text
Plan A — Repository rename and non-destructive restructuring
Plan B — Complete Phase 1 canonical-content POC
Plan C — Extract publication boundaries
Plan D — Scaffold sharepoint-knowledge plugin
Plan E — Native SharePoint skill pilot
Plan F — SharePoint agent pilot
Plan G — Multi-target capability specification
```

Each plan should include:

- goal and non-goals;
- files to create or modify;
- contracts and schemas;
- TDD steps;
- migration and compatibility steps;
- documentation updates;
- plugin and marketplace metadata updates;
- validation commands;
- rollback;
- exit evidence;
- explicit user approval gate.

### Step 5 — Implement in Small Batches

Execution rules:

- use one branch or worktree per bounded plan;
- preserve the working Phase 1 implementation;
- avoid simultaneous rename and functional rewrite where possible;
- update references systematically;
- run focused tests after each batch;
- run the full suite before merge;
- produce exit evidence;
- do not declare success from narrative alone.

## 9. Agent Cost Strategy

The project should use the cheapest capable model for each task rather than defaulting to the most expensive model.

### Low-cost agent tasks

A small/cheap agent such as Haiku-class capability may be sufficient for:

- inventorying directories and manifests;
- identifying hard-coded repository URLs;
- moving files according to an approved map;
- updating relative links;
- scaffolding folders;
- applying mechanical naming conventions;
- generating repetitive test fixtures;
- updating indexes and README links;
- checking metadata completeness;
- creating draft issue lists from an approved plan;
- running documented validation commands;
- producing evidence summaries from command output.

### Mid-tier agent tasks

Use a stronger implementation model for:

- non-trivial refactoring;
- plugin-boundary changes;
- schema implementation;
- migration logic;
- test design for edge cases;
- debugging failures;
- target-specific skill generation;
- integration adapters.

### High-reasoning agent tasks

Reserve the strongest model for:

- initial architecture and adversarial review;
- resolving ambiguous plugin boundaries;
- identity and lineage contracts;
- security-sensitive deployment design;
- source-of-truth and metadata-authority decisions;
- reviewing plans before execution;
- diagnosing cross-cutting failures;
- final acceptance review.

### Escalation rule

```text
Start with the cheapest agent expected to succeed.
Escalate only when:
- the task requires architectural judgment;
- the cheaper agent cannot resolve a test failure;
- the change crosses plugin or security boundaries;
- deterministic evidence contradicts the implementation narrative;
- a user decision is required.
```

### Important limitation

Model selection labels and availability differ by environment. The implementation plan should refer to capability tiers rather than hard-coding one vendor model name into repository logic.

## 10. Rename and Restructure Plan

### Stage 1 — Inventory only

- fetch or inspect the current repository;
- record current default branch and status;
- identify open work;
- list current paths;
- search for `manual-conversion-poc` references;
- identify GitHub Pages, workflows, badges, manifests, and release configuration;
- identify external references that cannot be changed automatically.

No rename or move.

### Stage 2 — Approve target name and map

Produce:

```text
rename-impact-report.md
repository-path-migration-map.json
redirect-and-link-update-checklist.md
```

User approves:

- repository name;
- plugin names;
- target tree;
- files to archive;
- files to leave in place temporarily.

### Stage 3 — Rename repository

If approved:

- rename through GitHub;
- verify redirect behaviour;
- update local remote URL;
- update README, badges, workflows, manifests, and documentation;
- retain an explicit historical note:

```text
This repository began as manual-conversion-poc.
```

### Stage 4 — Non-destructive restructuring

- create target directories;
- move only one coherent area at a time;
- update imports and links;
- leave temporary compatibility shims only where needed;
- run tests after every bounded move;
- do not combine moves with large behavioural changes.

### Stage 5 — Plugin extraction

Extract `sharepoint-knowledge` or `knowledge-publication` only after shared contracts and second-consumer needs are clear.

Do not move code into an empty abstraction merely to match the proposed tree.

## 11. Backlog Governance

Do not convert every item in the research documents into an implementation task.

Classify each candidate as:

```text
NOW — necessary to complete the approved current phase
NEXT — evidence-supported candidate for the next phase
LATER — useful only after another capability is proven
RESEARCH — requires product or tenant validation
REJECTED — deliberately out of scope
```

Every backlog item should identify:

- source decision or evidence;
- target phase;
- target plugin;
- runtime;
- owner;
- dependency;
- acceptance evidence;
- whether it changes permissions or production state.

This follows the principle that backlog migration should be reviewed and prioritized, not blindly copied.

## 12. Immediate Recommended Decisions

1. Adopt **AI-Assisted Structured Knowledge Workbench** as the initiative name.
2. Rename Phase 1 to **Structured Knowledge Conversion and Canonical Content POC**.
3. Keep `docx-to-content` as the Phase 1 plugin name.
4. Use `structured-knowledge-workbench` as the preferred repository rename candidate.
5. Plan one repository with multiple bounded plugins initially.
6. Do not build all proposed plugins immediately.
7. Complete repository reconnaissance and Superpowers brainstorming before renaming or restructuring.
8. Preserve Phase 1 delivery; do not let the broader roadmap interrupt the current CEIS evidence run except where current architecture decisions require it.
9. Use low-cost agents for mechanical work and stronger agents only for architecture, ambiguity, debugging, and acceptance review.
10. Require a separate reviewed implementation plan for each phase.

## 13. Definition of Success

The broader initiative succeeds when it can demonstrate—not merely claim—that:

- legacy documents can become maintainable canonical knowledge;
- canonical content is independent of one source document and one renderer;
- publications are assembled through explicit contracts;
- SharePoint can govern approved knowledge without becoming an uncontrolled second source of truth;
- native SharePoint skills can be generated, evaluated, and governed;
- SharePoint agents can be grounded in approved, current, permission-appropriate content;
- one capability can be implemented for more than one runtime without uncontrolled drift;
- every platform-changing action has an approved identity and permission boundary;
- each release has tests, evidence, and rollback;
- the architecture remains understandable to future maintainers.

## 14. Copy-Paste Prompt for the Planning Agent

```markdown
Use the repository's Superpowers brainstorming and plan-writing workflow.

Repository:
https://github.com/richfrem/manual-conversion-poc

Strategic proposal:
Rename the initiative to "AI-Assisted Structured Knowledge Workbench" and consider renaming the repository to `structured-knowledge-workbench`.

Do not rename or move anything yet.

First perform repository reconnaissance and adversarial brainstorming.

Review:
- the actual current repository structure;
- existing plugins, agents, skills, scripts, schemas, tests, workflows, manifests, research, and documentation;
- all hard-coded references to the current repository name;
- the broader plan in this document;
- whether multiple plugins are justified now or are premature abstractions;
- whether `docx-to-content`, `sharepoint-knowledge`, `knowledge-publication`, and `knowledge-evaluation` are coherent boundaries;
- whether one repository remains preferable to multiple repositories;
- which agents add real orchestration value;
- which research items should be NOW, NEXT, LATER, RESEARCH, or REJECTED;
- rename, redirect, import, CI, GitHub Pages, marketplace, plugin-manifest, and documentation impacts.

Challenge the proposal. Do not agree automatically.

Required outputs:
1. current-state-repository-map.md
2. brainstorming-record.md
3. architecture-decision-report.md
4. rename-impact-report.md
5. proposed-repository-tree.md
6. phased-roadmap.md
7. backlog-classification.md
8. one small implementation plan for repository rename and non-destructive restructuring, if and only if the rename is recommended

Planning rules:
- preserve the current Phase 1 implementation;
- avoid a big-bang restructure;
- separate file moves from behavioural changes;
- preserve history and compatibility where practical;
- identify rollback for every migration step;
- update applicable plugin.json and marketplace.json files;
- do not blindly migrate research ideas into the backlog;
- do not implement later phases;
- stop for explicit approval before rename, restructure, or new-plugin scaffolding.

Agent-cost strategy:
- use the cheapest capable agent for inventory, link updates, scaffolding, mechanical moves, repetitive tests, and evidence collection;
- use a mid-tier implementation agent for non-trivial refactors and schema work;
- reserve the strongest reasoning agent for architecture, adversarial plan review, security boundaries, ambiguity, and final acceptance;
- escalate only when evidence or complexity warrants it.
```

## 15. Final Recommendation

Use this naming hierarchy:

```text
Initiative:
AI-Assisted Structured Knowledge Workbench

Repository:
structured-knowledge-workbench

Phase 1:
Structured Knowledge Conversion and Canonical Content POC

Phase 1 plugin:
docx-to-content

Pilot:
CEIS Manual
```

Use one repository and several bounded plugins initially. Keep `docx-to-content` focused. Add `sharepoint-knowledge` as the next likely plugin only after a reviewed plan defines its contracts and pilot. Treat `knowledge-publication` as a separate boundary when canonical content has a second producer or publication has independent consumers. Keep common evaluation support shared until it earns plugin independence.

The expanded vision is legitimate research-driven growth. The control is to expand the roadmap without silently expanding the current phase.
