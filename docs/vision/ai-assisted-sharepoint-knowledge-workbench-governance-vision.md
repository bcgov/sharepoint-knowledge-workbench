# AI-Assisted SharePoint Knowledge Workbench — Structured Knowledge, Governance, and Insight Vision

**Status:** Future-state architecture and capability backlog  
**Relationship to Phase 1:** This document extends the `docx-to-content` proof of concept (historically accurate description of Phase 1 as it ran — see the naming-reconciliation note below for what exists now). It does not authorize expansion of the current Phase 1 implementation or bypass its acceptance gates.

> **Naming reconciliation note (added 2026-08-02):** `docx-to-content` was decommissioned
> 2026-08-01 (Phase 4.5 Wave 8), decomposed into `source-document-extraction`,
> `document-structure-analysis`, `structured-content-assembly`, `structured-content-rendering`.
> This document's proposed `sharepoint-knowledge-governance-agent` has no plugin home yet — see
> `docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md`'s own naming-
> reconciliation note (near its top) for the full current-vs-proposed plugin mapping before citing
> any plugin/agent name from this document as settled.
>
> **Generalization note (added 2026-08-09):** this document was originally titled and framed as a
> "Government" vision, written against a real government pilot tenant. Renamed to
> `ai-assisted-sharepoint-knowledge-workbench-governance-vision.md` and reworded to describe a
> general regulated-enterprise structured knowledge management workbench — the governance/records/
> security/accessibility rigor throughout is substantive and kept as-is (it applies to any
> regulated enterprise, not government specifically), only the government-specific framing and
> site examples were generalized. Old filename retained here for anyone searching by memory.

## 1. Purpose

The `docx-to-content` proof of concept tests whether a large Word-authored manual can be converted into validated, maintainable canonical content and rendered independently of its original document format.

The broader opportunity is larger than document conversion. In a regulated enterprise environment, the same pipeline could support a governed knowledge-management model in which:

- AI assists with content authoring, restructuring, classification, metadata proposals, review preparation, impact analysis, and maintenance;
- deterministic automation validates content, creates derived elements, renders outputs, and records lineage;
- SharePoint Online provides familiar operational capabilities such as document libraries, metadata, version history, permissions, content approval, and workflow integration;
- accountable people retain responsibility for business meaning, approval, exception handling, records obligations, security decisions, and risk acceptance.

The intended result is not an ungoverned AI publishing system. It is a governed knowledge-management pipeline in which AI and automation reduce repetitive effort while existing or improved organizational controls remain visible and enforceable.

## 2. Three Capability Pillars: Setup, Automate, and Insight

The content-management vision can be communicated through three high-level capability pillars.

```text
SETUP
Create and configure governed content libraries

AUTOMATE
Organize, enrich, validate, clean up, and maintain content at scale

INSIGHT
Find, understand, analyze, visualize, and reuse governed knowledge
```

These pillars simplify the message without collapsing the underlying controls. Each pillar combines AI-assisted recommendations, deterministic validation, SharePoint capabilities, and human accountability.

### 2.1 Setup

Setup establishes a governed destination for structured content.

#### Create Library: Natural Language to Governed Schema

A user should be able to describe a content-management need in ordinary language, for example:

```text
Create a library for operations manuals and procedures.
Require a content owner, knowledge type, approval status, audience,
review date, publication membership, stable topic ID, and validation status.
```

An AI-assisted design skill could translate that request into a proposed, reviewable schema containing:

- SharePoint library purpose and scope;
- proposed content types;
- site columns and field types;
- required and optional metadata;
- controlled vocabularies;
- default values;
- document-library views;
- versioning settings;
- approval requirements;
- retention, sensitivity, and access questions requiring organizational decisions;
- mappings between canonical metadata and SharePoint columns.

Natural language must produce a **proposal**, not an automatically trusted production schema. The proposed schema must identify:

- which values are deterministic;
- which values are inferred;
- which values require an accountable human decision;
- which values must come from an approved organizational authority or controlled vocabulary;
- which platform permissions are required before deployment.

#### Configure Library: Metadata, Views, Enrichment, and Governance

After the schema is approved, authorized automation may configure:

- content types;
- metadata columns;
- controlled choices or term sets;
- views such as `My Draft Content`, `Awaiting Review`, `Awaiting My Approval`, `Approved Topics`, and `Overdue for Review`;
- versioning and approval settings;
- default metadata;
- validation-status fields;
- publication and topic identifiers;
- workflow integration points;
- metadata-enrichment rules.

Design and deployment remain separate:

```text
Natural-language request
→ proposed schema
→ human and governance review
→ approved configuration package
→ authorized deployment
→ configuration validation
```

This separation is essential in a regulated enterprise environment, where SharePoint, Power Automate, Microsoft Entra, records management, security, privacy, and accessibility requirements may involve different decision authorities.

### 2.2 Automate

Automation applies approved rules consistently across libraries and content while preserving human accountability.

#### Organize

AI-assisted skills may help:

- classify content by approved knowledge type;
- propose topic boundaries;
- associate topics with publication maps;
- apply approved metadata mappings;
- identify related content;
- detect duplicate or conflicting topics;
- recommend folder-independent views and navigation;
- identify content that does not fit the approved schema;
- prepare changes for human confirmation.

An approved configuration should be reusable across multiple libraries, but reuse must not mean blind deployment. Each target library should be assessed for:

- purpose;
- audience;
- security classification;
- records requirements;
- existing metadata;
- existing workflows;
- local exceptions;
- migration and rollback needs.

#### Clean Up and Maintain

A cleanup skill family may help return an existing library to an approved state by identifying:

- missing or inconsistent metadata;
- stale or overdue content;
- ownerless content;
- broken links and missing media;
- obsolete or superseded files;
- duplicate content;
- invalid knowledge types;
- unapproved content in published views;
- publications containing stale topic versions;
- orphan topics not included in any publication;
- content that violates naming, schema, or path rules.

Cleanup actions must be separated into:

```text
report only
recommend changes
prepare an approved change package
perform authorized changes
verify and record results
```

No cleanup skill should delete, retire, reclassify, approve, or overwrite organizational content solely because an AI model recommends it.

#### Governed Automation Pattern

```text
Observe
→ Analyze
→ Recommend
→ Human approve or override
→ Execute through approved identity
→ Validate
→ Record evidence
→ Support rollback
```

### 2.3 Insight

Insight capabilities help staff find, understand, assess, and reuse governed knowledge.

#### Find Information

Potential capabilities include:

- improved search across canonical topics and published outputs;
- question and answer experiences grounded in approved content;
- navigation through publication maps and related topics;
- filters using owner, audience, knowledge type, status, review date, and publication;
- clear indication of source, approval state, version, and effective date;
- permission-aware retrieval that does not expose restricted content.

Search and Q&A should prefer approved content and should identify when the available evidence is incomplete, stale, unapproved, or outside the user's access.

#### Analyze and Visualize

Potential analysis and visualization capabilities include:

- content inventory by knowledge type, owner, audience, and status;
- review-date and stale-content dashboards;
- approval-flow bottlenecks;
- broken-link and validation trends;
- topic reuse and publication dependencies;
- content duplication and conflict candidates;
- orphan topics and unused media;
- knowledge coverage by system, business process, policy, or training need;
- change-impact views showing which publications are affected by a topic update.

Dashboards are derived views. They do not replace the canonical content, publication map, approval record, or validation evidence.

#### Generate Documents and Other Knowledge Products

Approved canonical content may be used to generate:

- multipage Markdown;
- Word or PDF publications;
- briefing or training presentations;
- HTML packages;
- audio scripts and transcripts;
- review packages;
- release notes;
- quick-reference guides;
- future SharePoint modern-page or Copilot grounding packages.

Generation must remain traceable to:

- canonical topic IDs and versions;
- publication map and audience profile;
- approved metadata;
- presentation template version;
- renderer version;
- validation evidence;
- approval and release identity.

Generated outputs are not automatically new canonical sources.

### 2.4 Relationship Among the Pillars

```text
SETUP
Natural language → proposed schema → approved library configuration
        ↓
AUTOMATE
Organize → enrich → validate → clean up → maintain
        ↓
INSIGHT
Find → answer → analyze → visualize → generate knowledge products
        ↓
CONTINUOUS GOVERNANCE
Review → approve → publish → monitor → revise → retire
```

The pillars are mutually reinforcing:

- Setup creates the governed structure required for safe automation.
- Automation keeps content and libraries aligned with the approved structure.
- Insight makes governed content useful to staff and reveals quality or coverage gaps.
- Continuous governance feeds lessons and changes back into schemas, templates, workflows, and content standards.

## 3. Vision Expansion: An AI-Assisted SharePoint Knowledge Workbench

The broader vision is not simply a document-conversion pipeline or a collection of disconnected SharePoint utilities. It is an **AI-assisted SharePoint Knowledge Workbench**, delivered through GitHub Copilot skills and interactive agents, that helps content teams manage the full knowledge lifecycle.

The workbench should help teams:

- understand existing content and repositories;
- design governed knowledge libraries;
- create SharePoint schemas from reviewed natural-language requirements;
- migrate and restructure existing documents;
- classify and enrich content with proposed metadata;
- organize canonical topics into coherent publications;
- prepare and support review and approval;
- publish validated knowledge products;
- create and evaluate SharePoint knowledge agents;
- search, analyze, visualize, and improve knowledge health;
- monitor content for staleness, duplication, broken links, missing ownership, and governance gaps.

This vision aligns with Microsoft's description of AI in SharePoint as a way to build and organize SharePoint content from natural-language intent, create sites, libraries, pages, and lists, organize and clean up content, enrich content with metadata, keep content updated for Copilot and agents, and codify repeatable site-specific processes.

Source inspiration:

- [AI in SharePoint — From Content Chaos to Clarity and Impact: Get Copilot Ready](https://adoption.microsoft.com/files/microsoft-365-community-conference/2026/pdf/MS29%20-%20AI%20in%20SharePoint%20-%20From%20Content%20Chaos%20to%20Clarity%20and%20Impact.%20Get%20Copilot%20Ready.pdf)

The governance-oriented workbench extends that direction with explicit controls for:

- accountable content ownership;
- human confirmation and approval;
- least-privilege execution;
- security, privacy, and sensitivity decisions;
- records classification, retention, and disposition;
- accessibility;
- audit evidence;
- deployment authorization;
- rollback and recovery;
- separation between recommendation and action;
- protection against overshared or unapproved content becoming easier to discover through AI.

### 3.1 Seven User-Facing Journeys

The workbench should be presented through a small number of understandable journeys rather than exposing every internal skill directly.

#### Journey 1 — Create a Knowledge Library

```text
Describe need
→ propose schema
→ review metadata and governance
→ approve configuration
→ deploy through an authorized identity
→ validate the library
```

#### Journey 2 — Migrate Existing Knowledge

```text
Ingest source
→ create temporary extraction
→ analyze
→ recommend topic boundaries and knowledge type
→ confirm
→ canonicalize
→ validate
→ prepare publication
```

#### Journey 3 — Organize and Enrich Content

```text
Assess content
→ propose metadata
→ associate topics with publications
→ identify relationships and duplicates
→ confirm changes
→ apply approved enrichment
```

#### Journey 4 — Review and Approve Changes

```text
Compare versions
→ summarize substantive changes
→ show publication context and impact
→ validate
→ request review and approval
→ record the decision
```

#### Journey 5 — Publish Knowledge Products

```text
Select approved topics and publication map
→ select audience and presentation profile
→ render
→ validate
→ approve release
→ publish or package
```

#### Journey 6 — Create and Evaluate Knowledge Agents

```text
Assess source readiness
→ define purpose and audience
→ select approved knowledge scope
→ propose behaviour and boundaries
→ create through an authorized platform path
→ evaluate answers and permissions
→ monitor readiness and drift
```

#### Journey 7 — Monitor and Improve Knowledge Health

```text
Inventory
→ detect stale, broken, duplicated, ownerless, or unapproved content
→ analyze trends and dependencies
→ prepare remediation
→ approve actions
→ execute and verify
```

### 3.2 Workbench Operating Modes

Every user journey should make its operating mode explicit.

#### Explore

- search;
- inspect;
- analyze;
- explain;
- visualize;
- produce no platform changes.

#### Design

- propose schemas;
- recommend metadata;
- design workflows;
- prepare publication maps;
- draft agent instructions;
- produce reviewable artifacts only.

#### Prepare

- generate deployment packages;
- create scripts or configuration artifacts;
- prepare cleanup plans;
- assemble review or publication packages;
- make no production change.

#### Execute

- create or configure libraries;
- apply metadata;
- deploy workflows;
- upload or publish content;
- create agents;
- require explicit authorization, approved identity, validation, and rollback planning.

#### Monitor

- detect drift;
- identify stale or invalid content;
- assess agent and publication readiness;
- report governance exceptions;
- initiate no destructive action without approval.

A broad request such as `clean up this library` must not silently switch from Explore or Design into Execute.

### 3.3 Layered Orchestration

The workbench should use layered orchestration so users do not need to know every skill name.

```text
User intent
→ interactive routing agent
→ user journey and workflow
→ specialized domain skills
→ deterministic tools or authorized platform actions
→ evidence and approval gate
```

#### Layer 1 — User-Facing Journeys

The seven journeys above are the primary entry points.

#### Layer 2 — Interactive Routing and Domain Agents

Candidate agents:

```text
knowledge-workbench-agent
structured-knowledge-conversion-agent
sharepoint-knowledge-governance-agent
knowledge-insight-agent
sharepoint-agent-designer
```

The routing agent should ask targeted questions, identify risk and permissions, choose the applicable journey, and invoke the correct domain agent or skills.

#### Layer 3 — Reusable Domain Skills

Domain skills perform bounded capabilities such as:

```text
recommend-topic-boundaries
generate-content-metadata
design-metadata-schema
design-publication-map
design-approval-workflow
assess-library-health
prepare-content-review
evaluate-agent-grounding
```

#### Layer 4 — Deterministic Tools and Authorized Actions

Examples:

```text
parse DOCX
validate canonical package
compute identities and hashes
create SharePoint columns
apply approved metadata
deploy approved workflow
upload validated content
run agent evaluation set
```

Agents and skills must orchestrate these tools rather than duplicate their implementation.

### 3.4 SharePoint Knowledge Agents as Governed Knowledge Products

A SharePoint knowledge agent should be treated as another derived knowledge experience, not as an ungoverned chatbot layered over arbitrary content.

```text
Approved Canonical Topics
+
Publication or Knowledge Scope
+
SharePoint Permissions
+
Agent Instructions
+
Approved Behaviour Boundaries
+
Evaluation Set
=
Governed SharePoint Knowledge Agent
```

Potential capabilities include:

#### `assess-agent-readiness`

Check:

- source approval state;
- content ownership and review dates;
- metadata completeness;
- duplicate or contradictory content;
- permissions and oversharing risks;
- source-format suitability;
- topic and publication coverage;
- stale or superseded content;
- unresolved validation warnings.

#### `design-sharepoint-agent`

Prepare a reviewable agent design containing:

- purpose;
- audience;
- approved knowledge scope;
- behaviour instructions;
- answer boundaries;
- escalation and insufficient-evidence behaviour;
- source and permission assumptions;
- evaluation questions;
- known limitations.

#### `create-sharepoint-agent`

Create the approved platform artifact only when an authorized creation mechanism, target environment, identity, permissions, and deployment process are available.

#### `evaluate-sharepoint-agent`

Run a governed evaluation set covering:

```text
answerable question
unanswerable question
ambiguous question
sensitive-content question
outdated-content question
cross-topic question
procedure question
exception question
```

Evaluation should examine:

- whether the answer is grounded in approved sources;
- whether permissions are respected;
- whether source, version, and approval context are available;
- whether warnings and exceptions survive summarization;
- whether the agent declines when evidence is insufficient;
- whether stale or superseded content is avoided.

#### `monitor-agent-content-readiness`

Monitor whether changes to source content, approval status, permissions, metadata, or publication scope should trigger agent reevaluation.

### 3.5 The Repository as a Declarative Workbench Definition

A future repository may evolve from one conversion plugin into a structured workbench definition.

```text
knowledge-workbench/
  agents/
    knowledge-workbench-agent/
    structured-knowledge-conversion-agent/
    sharepoint-knowledge-governance-agent/
    knowledge-insight-agent/
    sharepoint-agent-designer/

  skills/
    setup/
    migration/
    authoring/
    metadata/
    organization/
    governance/
    publishing/
    insight/
    agents/
    monitoring/

  standards/
    manual-topic/
    procedure/
    policy/
    training/

  schemas/
    canonical-content/
    publication-map/
    sharepoint-metadata/
    workflow-definition/
    agent-definition/
    evaluation/

  templates/
    content/
    presentation/
    workflow/
    agent/

  evaluations/
    content/
    publication/
    workflow/
    agent/

  evidence/
```

The repository becomes a versioned definition of:

- knowledge standards;
- schemas;
- skills;
- agent behaviour;
- templates;
- evaluations;
- deployment packages;
- evidence requirements.

It must not become a repository of unrestricted credentials or an automatic path to production.

### 3.6 Refined Vision Statement

> The future solution is an AI-assisted SharePoint Knowledge Workbench delivered through GitHub Copilot skills and interactive agents. The workbench helps content teams create and configure governed knowledge libraries, convert and organize content, enrich metadata, design review and approval processes, prepare SharePoint knowledge agents, analyze knowledge health, and generate reusable knowledge products. The workbench separates exploration, design, preparation, execution, and monitoring so AI assistance can scale without bypassing organizational accountability, security, privacy, records, accessibility, approval, or deployment controls.

## 4. Guiding Principle

```text
AI proposes, compares, checks, assembles, and prepares.

Deterministic automation validates, renders, packages, and records.

Accountable people decide, approve, publish, and accept risk.
```

AI may recommend values or changes, but it must not silently invent authoritative ownership, approval, security classification, records classification, retention, or legal/policy decisions.

## 5. Proposed End-to-End Model

```text
Source Document or Existing Content
        ↓
Temporary Extraction
        ↓
Analysis and Knowledge-Type Recommendation
        ↓
Human Confirmation of Structure and Boundaries
        ↓
Canonical Topic Library
        ↓
AI-Assisted Metadata Enrichment
        ↓
Publication Map
        ↓
SharePoint Content Types and Metadata
        ↓
Review and Approval Workflow
        ↓
Approved Publication Release
        ↓
Rendered Outputs and Knowledge Experiences
        ↓
Continuous Knowledge-Health Monitoring
```

The following distinctions remain mandatory:

```text
Source document
≠ temporary extraction
≠ canonical topic
≠ publication map
≠ rendered output
≠ approved release
```

And:

```text
heading
≠ topic
≠ physical file
≠ retrieval chunk
≠ publication section
```

## 6. Responsibilities by Layer

### 4.1 Canonical Content and Repository Controls

The canonical package and repository should remain authoritative for machine-integrity concerns such as:

- stable content identity;
- source lineage and fingerprints;
- machine-owned metadata;
- content and media hashes;
- schema validation;
- structural-anchor reconciliation;
- link and media validation;
- publication-map definitions;
- renderer and template versions;
- deterministic generated elements;
- automated tests and evidence;
- reproducible releases and rollback.

### 4.2 SharePoint Operational Governance

SharePoint Online may provide business-facing operational controls such as:

- content owner and accountable business area;
- reviewer and approver;
- approval status;
- review and expiry dates;
- audience;
- knowledge type;
- sensitivity and classification fields, where approved;
- version history;
- permissions;
- document-library views;
- publication status;
- workflow notifications;
- retention and records controls, where organizationally configured.

### 4.3 Human Accountability

People remain accountable for:

- accuracy of business content;
- policy meaning and legal effect;
- authoritative ownership;
- security and privacy decisions;
- records-management decisions;
- acceptance of exceptions and warnings;
- substantive approval;
- publication and retirement decisions.

## 7. Metadata Authority Model

Every metadata field must have one defined authority. The pipeline must not allow Git, Markdown front matter, SharePoint columns, workflows, and manifests to independently overwrite the same field without reconciliation.

A candidate authority model is:

| Metadata | Proposed authority |
|---|---|
| Topic ID | Deterministic canonical pipeline |
| Content hash | Deterministic canonical pipeline |
| Source lineage | Deterministic canonical pipeline |
| Publication membership/order | Publication map |
| Validation status | Validation pipeline |
| Renderer/template version | Release manifest |
| Title | Canonical content, unless another authority is explicitly chosen |
| Knowledge type | Controlled vocabulary, human-confirmed |
| Business owner | SharePoint/governance process |
| Reviewer/approver | SharePoint/governance process |
| Approval status | Approval workflow |
| Review date | Business owner/workflow |
| Audience | Controlled vocabulary, human-confirmed |
| Sensitivity | Approved organizational classification process |
| Records classification/retention | Approved records-management process |

AI-generated metadata proposals should record their provenance and authority class.

Example:

```json
{
  "field": "audience",
  "proposed_value": "Frontline staff",
  "source": "inferred from canonical content",
  "confidence": "medium",
  "authority": "requires business confirmation"
}
```

Deterministic metadata is different:

```json
{
  "field": "topic_id",
  "value": "file-access--7d91c4a2",
  "source": "deterministic structural identity",
  "authority": "system generated"
}
```

Recommended provenance classes:

```text
deterministic
extracted
inferred
human-confirmed
workflow-controlled
externally-governed
```

## 8. Topic, Publication, and Release Governance

Distributed content requires more than one approval scope.

### 6.1 Topic Approval

Used for contained changes to one or more canonical topics.

Review material should include:

- previous and proposed content;
- substantive change summary;
- source evidence;
- validation findings;
- related content potentially affected;
- publication context.

### 6.2 Publication Approval

Used when:

- topics are added or removed;
- ordering or hierarchy changes;
- multiple topics change in one release;
- a topic is reused in another publication;
- navigation or publication metadata changes.

Review material should include:

- assembled publication preview;
- changed-topic list;
- publication-context diffs;
- navigation changes;
- warnings and dispositions;
- release manifest.

### 6.3 Standard and Template Approval

Used when changing:

- required knowledge-type sections;
- metadata requirements;
- semantic-component definitions;
- validation rules;
- presentation templates;
- renderer behaviour.

A template or standard change may affect many outputs and should not be treated as an ordinary topic edit.

### 6.4 Separate Status Models

Topic, publication, and release statuses should not be collapsed into one field.

Candidate states:

```text
Topic:
draft → in review → approved → superseded → retired

Publication:
draft assembly → review candidate → approved release → superseded

Release:
generated → validated → approved → published → withdrawn
```

A publication release must identify the exact approved topic versions it contains.

## 9. Publication Assembly

Canonical topics should be stored independently of one publication's layout.

```text
Canonical Topic Library
+
Publication Map
+
Approved Topic Versions
+
Audience or Variant Profile
+
Presentation Template
+
Renderer
=
Governed Published Knowledge Product
```

A publication map should eventually define:

- publication identity and title;
- included topic IDs;
- approved topic versions;
- order and hierarchy;
- parent-child relationships;
- audience or variant;
- generated navigation;
- inclusions and exclusions;
- references to shared topics.

Physical folder structure must not become the authoritative publication model.

For an initial pilot, a versioned manifest may serve as the single-publication map if this is documented explicitly and does not rely on filename or directory order.

## 10. SharePoint Delivery Models

### 8.1 Markdown in a Document Library

A SharePoint document library is a practical early destination because Markdown files can be governed as ordinary files with metadata, versioning, permissions, and approval workflows.

Possible pilot design:

```text
Knowledge Content Library
  Canonical Topics
  Publication Maps
  Published Markdown
  Validation Evidence
  Release Records
```

Candidate views:

```text
My Draft Content
Awaiting Review
Awaiting My Approval
Approved Topics
Overdue for Review
Topics by Publication
Topics by Owner
Topics with Validation Warnings
Superseded Content
```

### 8.2 SharePoint Modern Pages

Modern pages may later provide a richer intranet experience, but raw `.aspx` is never an authoring or canonical format.

Programmatic creation may require approved Microsoft Entra permissions, Microsoft Graph or PnP access, and an organizational deployment model. Therefore, modern-page publishing remains a separately authorized adapter.

### 8.3 Source-of-Truth Options

A future implementation must choose explicitly among:

#### Model A — SharePoint as Canonical Authoring Repository

Users edit Markdown in SharePoint. The pipeline retrieves approved versions and creates validated packages and releases.

#### Model B — Git as Canonical; SharePoint as Governed Publication

Canonical edits occur in Git. SharePoint contains review and publication copies plus operational metadata and approvals.

#### Model C — Controlled Synchronization

SharePoint edits become proposed Git changes:

```text
SharePoint edit
→ validation
→ branch or pull request
→ AI change summary
→ approval and merge
→ regenerate SharePoint publication
```

#### Model D — Hybrid Ownership

Canonical text and machine metadata are pipeline-owned. SharePoint columns and workflows own operational governance data. Designated SharePoint-local regions may be editable only if drift detection and ownership rules are explicit.

No model should permit silent two-way editing that creates competing sources of truth.

## 11. Proposed Skill Family

The following are proposed post-Phase-1 skills. They are not authorized Phase 1 deliverables unless separately approved.

### 9.1 `generate-content-metadata`

Purpose:

- analyze canonical Markdown;
- extract deterministic metadata;
- propose inferred metadata;
- validate metadata against the selected knowledge standard;
- identify fields requiring human confirmation.

Must not invent authoritative owner, approver, sensitivity, retention, records classification, or effective date.

### 9.2 `design-metadata-schema`

Purpose:

- recommend a metadata dictionary;
- define controlled vocabularies;
- identify the authority for every field;
- map canonical metadata to SharePoint columns;
- detect duplicated or conflicting metadata ownership.

### 9.3 `create-sharepoint-content-model`

Purpose:

- propose SharePoint libraries, content types, site columns, choices, views, versioning, and approval requirements;
- generate deployment artifacts only when an approved platform mechanism and permissions are supplied.

Candidate content types:

```text
Manual Topic
Procedure
Policy
Training Topic
Publication Map
Published Release
Validation Evidence
```

### 9.4 `design-approval-workflow`

Purpose:

- recommend topic, publication, and release approval processes;
- identify states, transitions, approvers, notifications, rejection handling, and escalation;
- produce a human-reviewable workflow specification.

This is a design skill. It must not deploy a workflow.

### 9.5 `create-sharepoint-approval-workflow`

Purpose:

- take an approved workflow specification;
- create or update an actual SharePoint/Power Automate approval flow using an approved environment and identity;
- validate workflow triggers, decisions, status updates, and notifications.

This is an action skill and must require explicit authorization.

### 9.6 `publish-canonical-content-to-sharepoint`

Purpose:

- publish validated Markdown and media;
- apply approved metadata;
- associate topics with publications;
- verify uploaded identity and hashes;
- report publication results.

Required operating modes should include:

```text
package-only
manual-upload package
delegated-user publication
approved application publication
```

The skill must never mark content approved or overwrite an approved release silently.

### 9.7 `prepare-content-review`

Purpose:

- compare proposed and approved topic versions;
- prepare before-and-after diffs;
- show changed topics in publication context;
- identify related and reused content;
- summarize validation findings;
- prepare reviewer questions;
- assemble a review package without making the approval decision.

### 9.8 `assess-content-impact`

Purpose:

- accept a system, business-process, policy, or legislative change;
- identify potentially affected topics and publications;
- identify possible training and communication impacts;
- produce an impact-assessment report for human review.

### 9.9 `monitor-knowledge-health`

Purpose:

- identify overdue review dates;
- missing owners;
- broken links;
- validation failures;
- duplicate or conflicting content;
- stale publication assemblies;
- orphan topics;
- retired topics still referenced;
- publications containing topic versions newer than the last publication approval.

### 9.10 `generate-publication-map`

Purpose:

- assemble approved topics into a coherent publication;
- define order and hierarchy;
- generate navigation;
- preserve separation between canonical storage and publication organization.

## 12. Proposed Agent Boundaries

### `structured-knowledge-conversion-agent`

Orchestrates:

```text
analyze-document
recommend-topic-boundaries
convert-document
generate-content-metadata
prepare-content-review
generate-publication-map
render-content
produce-evidence
```

This agent primarily operates on local/repository artifacts and must preserve the explicit human confirmation gate.

### `sharepoint-knowledge-governance-agent`

Orchestrates:

```text
design-metadata-schema
create-sharepoint-content-model
design-approval-workflow
create-sharepoint-approval-workflow
publish-canonical-content-to-sharepoint
monitor-knowledge-health
```

This agent may require elevated platform permissions and must separate design from action. It must not assume Microsoft Graph, PnP PowerShell, Power Automate deployment, or Microsoft Entra permissions are available.

## 13. Regulated Enterprise Environment Constraints

Any future implementation must account for:

- least-privilege access;
- approved identities and application registrations;
- administrator consent and connector policies;
- security classification and sensitivity;
- privacy and protected information;
- records classification, retention, legal holds, and disposition;
- accessibility requirements;
- auditability and approval evidence;
- separation of duties;
- environment promotion and change control;
- malware scanning and safe handling of uploaded documents;
- business-continuity and rollback requirements;
- support ownership and operational sustainability.

The pipeline must continue to function in a `package-only` mode when platform provisioning or publication permissions are unavailable.

## 14. AI Trust and Review Rules

Every AI-produced proposal should distinguish:

```text
measured fact
extracted value
deterministic result
heuristic recommendation
AI inference
human-confirmed decision
workflow-controlled decision
not measured
unknown
requires review
```

AI-generated changes should retain:

- source provenance;
- affected topic IDs;
- affected publication IDs;
- reason for the proposal;
- supporting evidence;
- validation result;
- reviewer decision.

AI must not:

- infer approval;
- infer security or records classification as authoritative;
- silently weaken policy language;
- silently omit unmatched content;
- silently accept warnings;
- claim that a human review occurred;
- publish rejected or unapproved content.

## 15. Pilot Recommendation

After the `docx-to-content` Phase 1 evidence run is complete, test a lightweight governed SharePoint pilot:

1. Produce a manageable set of coherent canonical topic files.
2. Preserve deeper structural anchors for lineage and internal addressability.
3. Assemble the complete manual through an explicit publication map or documented manifest hierarchy.
4. Upload the Markdown topics and required media to a dedicated SharePoint document library.
5. Define a minimal `Manual Topic` content type or equivalent metadata model.
6. Apply owner, status, audience, review date, publication ID, stable topic ID, and validation status.
7. Enable versioning and a lightweight approval workflow.
8. Make one representative business-content change.
9. Use AI to prepare:
   - the proposed edit;
   - topic diff;
   - publication-context diff;
   - impact summary;
   - validation report;
   - reviewer questions.
10. Review the change at both topic and assembled-publication levels.
11. Record a simple approval artifact.
12. Regenerate and validate the publication output.
13. Evaluate author, reviewer, approver, and reader experience.

The pilot should answer:

> Can content teams safely author, review, approve, publish, and maintain distributed canonical content without losing the coherence and controls of the complete knowledge product?

## 16. Capability-to-Skill Map

The Setup, Automate, and Insight pillars suggest a coordinated skill portfolio.

### Setup Skills

```text
design-metadata-schema
create-sharepoint-content-model
design-approval-workflow
create-sharepoint-approval-workflow
```

Setup skills should follow a design-before-action pattern. Natural-language requests first create reviewable specifications; deployment skills act only after explicit approval and permission checks.

### Automation Skills

```text
generate-content-metadata
recommend-topic-boundaries
generate-publication-map
organize-sharepoint-library
assess-library-health
prepare-library-cleanup
apply-approved-library-cleanup
assess-content-impact
monitor-knowledge-health
```

Reporting and recommendation skills should be usable without write access. Action skills should be separately authorized, idempotent where practical, evidence-producing, and rollback-aware.

### Insight Skills

```text
find-governed-knowledge
answer-from-approved-content
analyze-knowledge-portfolio
visualize-knowledge-health
prepare-content-review
generate-knowledge-product
produce-release-evidence
```

Insight skills must preserve permissions, approval state, source citations, version context, and uncertainty. Generated documents must remain traceable to approved canonical content and publication definitions.

### Agent Boundaries

```text
structured-knowledge-conversion-agent
    → converts, structures, validates, and renders content

sharepoint-knowledge-governance-agent
    → designs and provisions metadata, libraries, and workflows

knowledge-insight-agent
    → finds, analyzes, visualizes, and generates from approved knowledge
```

These agents should share contracts and evidence but should not share unrestricted permissions. Conversion, governance provisioning, and knowledge consumption are separate trust boundaries.

## 17. Decisions Required Before Implementation

Before building SharePoint governance automation, decide:

- canonical source-of-truth model;
- authoritative owner for each metadata field;
- topic and publication approval scopes;
- minimum content types and controlled vocabularies;
- target SharePoint site and library;
- approved authentication and deployment model;
- records and retention requirements;
- sensitivity and access model;
- accessibility requirements;
- rollback and release model;
- edit and synchronization policy;
- responsible operational support team.

## 18. Sequencing

```text
1. Complete Phase 1 conversion and evidence.
2. Review the actual pilot authoring and review experience.
3. Confirm the canonical topic and publication-map model.
4. Define metadata authority and dictionary.
5. Design SharePoint content types and approval workflows.
6. Validate records, security, privacy, and accessibility requirements.
7. Build design-only skills first.
8. Obtain authorization for platform-action skills.
9. Run a bounded SharePoint governance pilot.
10. Evaluate evidence before scaling to additional content sets.
```

Do not add the proposed SharePoint governance skills to the current Phase 1 implementation plan merely because they are listed here.

## 19. Success Measures

Evaluate:

- conversion and metadata accuracy;
- author effort for a representative change;
- reviewer effort and comprehension;
- approval-cycle clarity;
- preservation of publication context;
- validation defect rate;
- stale-content detection;
- broken-link and media rates;
- owner and review-date completeness;
- ability to regenerate outputs without duplicate editing;
- rollback and release reproducibility;
- user acceptance;
- quality of AI-assisted impact and review summaries.
- effectiveness of routing agents in selecting the correct journey and skills;
- proportion of work completed in Explore/Design/Prepare modes without unnecessary write access;
- agent-readiness defects detected before agent creation;
- knowledge-agent evaluation pass/fail evidence and regression trends;
- ability to trace generated answers and knowledge products to approved content;
- reduction in manual effort for library setup, metadata design, cleanup assessment, and review preparation;
- user understanding of when the workbench is recommending versus executing changes.

## 20. Final Principle

```text
Knowledge governance does not disappear when content becomes Markdown.

Setup creates governed libraries and schemas.

Automation organizes, enriches, validates, cleans up, and maintains content.

Insight helps staff find, understand, analyze, visualize, and reuse approved knowledge.

Structured content makes governance more explicit, testable, reusable, and automatable.

SharePoint can provide familiar operational workflow and metadata controls.

AI can reduce the authoring, classification, review-preparation, maintenance,
and publishing burden.

Accountable people remain responsible for meaning, approval, publication, and risk.

The workbench hides skill complexity behind understandable user journeys,
while preserving explicit operating modes, permission boundaries, evidence,
and human decision gates.

SharePoint knowledge agents are governed outputs of approved content,
permissions, instructions, and evaluations—not substitutes for content quality.
```
