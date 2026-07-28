# Research Summary — Get Started with Copilot in SharePoint (Preview)

**Primary source:** [Get started with Copilot in SharePoint (preview)](https://learn.microsoft.com/en-us/SharePoint/copilot-in-sharepoint-get-started)  
**Publisher:** Microsoft Learn  
**Source last updated:** June 25, 2026  
**Purpose:** Summarize the documented Copilot in SharePoint preview, its controls and limitations, and explain how it affects the proposed AI-Assisted SharePoint Knowledge Workbench for a government environment.  
**Status:** Research and architecture input; not implementation authorization.

## 1. Executive Summary

Microsoft documents Copilot in SharePoint as a natural-language interface for working with SharePoint content and structures. During the preview, licensed users can use it to:

- ask questions;
- run workflows;
- create SharePoint sites;
- create pages;
- create lists;
- create libraries;
- create interactive reports;
- create Office files.

The documentation also identifies skills as a supported extension mechanism for repeatable, multi-step workflows. Related Microsoft documentation says skills can encode organization-specific rules, document standards, or review checklists; can be created from natural language and reviewed before saving; and are stored as Markdown files in a site's Agent Assets library.

For the proposed workbench, this is significant because Microsoft is providing a native SharePoint execution surface for several ideas already identified in the architecture:

```text
Natural-language intent
→ SharePoint structure or workflow
→ reusable skill
→ governed site content
→ Copilot and agent experience
```

However, the preview has explicit prerequisites, administrative controls, usage limits, unsupported government-cloud environments, scope limitations, and permission boundaries. The native SharePoint skill model also cannot connect to external systems or run custom code. Therefore, it complements—but does not replace—the repository-based GitHub Copilot workbench, deterministic conversion pipeline, tests, release evidence, and separately authorized platform automation.

## 2. Product Status and Availability

The source applies to the **preview** version of Copilot in SharePoint, previously referred to as AI in SharePoint.

Microsoft states that starting in mid-June 2026, the capabilities roll out as an opt-out preview and become available automatically to users with a Microsoft 365 Copilot license. Previously configured tenant or site opt-outs are honored.

The documentation states that the preview requires:

- an active Microsoft 365 Copilot license;
- availability of the preview in the tenant;
- no separate user opt-in after the opt-out preview reaches the tenant.

Microsoft states that Copilot in SharePoint is included with the Microsoft 365 Copilot license during preview and at general availability, at no extra cost beyond that license.

## 3. Government-Cloud Limitation

The source explicitly states that Copilot in SharePoint is not currently supported in:

- Microsoft 365 Government Community Cloud (GCC);
- GCC High;
- Department of Defense environments;
- Office 365 air-gapped cloud environments;
- Microsoft 365 operated by 21Vianet.

This limitation must not be generalized to all public-sector organizations. The relevant question for this project is the actual Microsoft 365 cloud environment used by the target organization.

Before planning a pilot, verify:

```text
tenant cloud
Microsoft 365 Copilot licensing
preview availability
tenant and site exclusions
organizational approval
security, privacy, records, and accessibility requirements
```

## 4. Documented Capability Scope

The Microsoft Learn page says Copilot in SharePoint helps users work with content through natural language.

Documented top-level capabilities include:

```text
Ask questions
Run workflows
Create sites
Create pages
Create lists
Create libraries
Create interactive reports
Create Office files
```

The page links to related documentation for capabilities such as:

- extending Copilot in SharePoint with skills;
- creating sites with AI;
- creating document libraries with AI;
- automating workflows with Copilot in SharePoint.

The source establishes product direction and capability categories. Each workflow requires separate review of its own current documentation before relying on detailed behaviour.

## 5. Administrative Availability Controls

During preview, Microsoft documents PowerShell-based controls using the existing `KnowledgeAgent` parameters in `Set-SPOTenant`.

The main scope values are:

```text
AllSites
IncludeSelectedSites
ExcludeSelectedSites
NoSites
```

Microsoft documents these meanings:

- `AllSites` — available on all sites;
- `IncludeSelectedSites` — available only on identified sites;
- `ExcludeSelectedSites` — available on all sites except identified sites;
- `NoSites` — unavailable on all sites.

Microsoft also documents:

- `KnowledgeAgentSelectedSitesList` for the included or excluded site URLs;
- `KnowledgeAgentSelectedSitesListOperation` values of `Overwrite`, `Append`, and `Remove`;
- a maximum of 100 URLs in the selected-sites list;
- per-geo execution for multigeo tenants;
- SharePoint Online Management Shell version 16.0.26615.12013 or later during preview.

The source notes that the underlying parameter names retain the earlier Knowledge Agent terminology for compatibility even though the feature is now called Copilot in SharePoint.

## 6. Site-Level Controls

Microsoft documents a Site AI settings panel that allows site owners to control aspects of the site experience.

Documented options include:

- choosing which agent opens from the Agent icon—Copilot in SharePoint or a custom agent;
- hiding the Copilot button on site pages for site visitors.

The source also states that Restricted Content Discovery is respected. If Restricted Content Discovery is enabled on a site, Copilot in SharePoint and AI actions do not appear on that site, regardless of the broader Copilot in SharePoint availability setting.

This is directly relevant to the workbench's proposed permission- and oversharing-aware operating model.

## 7. Language, Usage, and Model Constraints

### Language Support

Microsoft says Copilot in SharePoint supports only languages that appear in both:

- the SharePoint Online supported-language list;
- the Microsoft 365 Copilot supported-language list.

Microsoft recommends using a supported language for prompts and says results may vary for languages outside the supported list because those languages are not tested or validated for this experience.

### Usage Limits

During preview, Microsoft applies daily and weekly per-user usage limits. The limits are individual, not pooled across the organization. When a user reaches a limit, Copilot features remain unavailable until the limit resets automatically, and SharePoint notifies the user.

Microsoft states that it may adjust the limits during preview as usage patterns are monitored.

### Model Management

Microsoft states that Copilot in SharePoint currently uses a Microsoft-managed reasoning model from OpenAI. Microsoft chooses and manages the model, and the specific model may change as the service adopts newer models. Customers do not configure the model for this experience.

These constraints mean that preview behaviour and capacity should not be treated as a fixed production contract.

## 8. Skills in Copilot in SharePoint

Related Microsoft Learn documentation defines a skill as a reusable representation of a repeatable, multi-step workflow.

Skills can capture organization-specific rules such as:

- document standards;
- review checklists;
- repeatable content-management procedures.

Microsoft documents that a user can:

```text
describe a workflow in natural language
→ review the draft skill
→ adjust its steps, inputs, or outputs
→ confirm that it should be saved
→ reuse it in later prompts
```

Copilot in SharePoint can automatically load a relevant skill based on a request, or the user can invoke a skill explicitly by name.

### Skill Storage

Microsoft documents that SharePoint skills are stored as Markdown files under:

```text
/Agent Assets/Skills/<skill-name>/SKILL.md
```

The files are stored in the site's Agent Assets library. Microsoft says the library is product-managed and cannot be deleted, but standard SharePoint file governance can be applied to skill files, including permissions, retention, sensitivity labels, and auditing.

### Skill Permissions

Microsoft documents these defaults:

- Edit permission is required to create a skill;
- View permission is sufficient to run a skill.

Microsoft says permission inheritance on the Agent Assets library can be broken if a more restrictive model is required.

### Skill Limits

Microsoft explicitly states that Copilot in SharePoint skills:

- cannot connect to external systems;
- cannot execute custom code;
- can only perform actions already supported by Copilot in SharePoint;
- operate only within the user's existing permissions;
- do not expand access or introduce capabilities beyond what Copilot in SharePoint provides.

This is a central architecture constraint.

## 9. Two Complementary Skill Environments

The research supports a two-layer workbench model rather than choosing between GitHub Copilot and Copilot in SharePoint.

### Repository and GitHub Copilot Skills

Best suited to capabilities requiring:

- custom code;
- DOCX parsing and cleanup;
- deterministic transformations;
- hashing and structural identity;
- canonical package generation;
- schema and contract testing;
- Git branches and pull requests;
- reproducible releases;
- external tools or approved APIs;
- deployment packages;
- complex validation and evidence.

### Native Copilot in SharePoint Skills

Best suited to capabilities that:

- run in the SharePoint user context;
- use native SharePoint actions;
- organize files and folders;
- interact with SharePoint content and lists;
- encode site-specific review checklists or document standards;
- benefit from storage and governance in the Agent Assets library;
- need to be usable by site viewers or editors without a development environment.

### Combined Model

```text
GitHub Copilot workbench
→ design, code, test, package, validate, and prepare

Copilot in SharePoint
→ guide users, apply native site workflows, organize content,
  ask questions, and run site-scoped skills

SharePoint governance
→ permissions, retention, sensitivity, auditing, metadata,
  approval, and site-level controls
```

The two skill systems should share specifications and evidence where practical, but they should not be assumed to have identical syntax, capabilities, permissions, or deployment paths.

## 10. Implications for the Proposed Knowledge Workbench

The product documentation strengthens several parts of the proposed vision.

### 10.1 Native Routing and Skill Reuse

The documented ability to automatically load relevant SharePoint skills supports the workbench's routing concept.

The workbench could expose a small number of user journeys while internal routing selects an applicable skill.

### 10.2 Natural-Language Setup

The documented ability to create sites, lists, libraries, pages, reports, and files through natural language supports the Setup pillar.

The government workbench should still separate:

```text
request
design proposal
human and governance review
authorized action
validation and evidence
```

### 10.3 Native Site Workflows

The documented ability to run workflows and extend Copilot with repeatable skills supports the Automate pillar.

Site-scoped workflow ideas include:

- review checklists;
- document-standard checks;
- content organization;
- metadata review;
- list updates;
- user-guided cleanup processes.

Each proposed workflow must be validated against the actual actions supported by Copilot in SharePoint. Native skills cannot be assumed to run repository code or call external systems.

### 10.4 Governed Skill Files

Because SharePoint skills are Markdown files in the Agent Assets library, the broader workbench can treat the skills themselves as governed content.

Potential controls include:

- owner;
- purpose;
- status;
- review date;
- sensitivity;
- approved site scope;
- version history;
- audit history;
- evaluation evidence.

The Microsoft documentation confirms that ordinary SharePoint permissions, retention, sensitivity labels, and auditing can apply to these files.

## 11. Implications for Government Governance

### Tenant and Site Rollout

The documented `IncludeSelectedSites` mode supports a bounded pilot instead of immediate tenant-wide rollout.

A government pilot should identify:

- approved tenant environment;
- selected pilot sites;
- licensed participants;
- site owners;
- permitted skills;
- approval and auditing expectations;
- Restricted Content Discovery requirements;
- rollback or opt-out procedure.

### Skill Authoring Rights

The default rule that site editors can create skills may be too broad for some government sites.

A governance decision is required on whether to:

- accept the default;
- restrict the Agent Assets library;
- separate skill authors from ordinary site editors;
- require review before a skill is used broadly;
- maintain approved skill templates;
- track skill tests and evaluation evidence.

### Human Validation

Microsoft's Copilot documentation says AI-generated content may be incomplete, inaccurate, or out of date and requires user review and validation before action.

The workbench should therefore record distinctions such as:

```text
AI proposal
human-reviewed proposal
approved skill
skill execution result
validated platform change
```

### Security and Permissions

Native SharePoint skills do not grant additional access. That is useful, but it does not eliminate oversharing risk. If a user already has access to content that should not have been broadly shared, AI can make that content easier to find and use.

The pilot should therefore include:

- permission review;
- site-scope review;
- sensitivity review;
- Restricted Content Discovery assessment;
- validation that skill outputs do not disclose restricted information through titles, summaries, metadata, or generated indexes.

## 12. Proposed Native SharePoint Skill Backlog

The following are candidate native skills, subject to verification against supported SharePoint actions.

### Content Preparation

```text
review-document-standard
check-required-metadata
summarize-selected-content
classify-selected-content
prepare-content-review
```

### Organization

```text
organize-selected-files
apply-approved-folder-rules
identify-missing-metadata
add-items-to-review-list
prepare-publication-inventory
```

### Governance

```text
run-review-checklist
identify-overdue-content
prepare-owner-review
record-review-outcome
identify-content-requiring-escalation
```

### Agent Readiness

```text
check-source-approval-state
identify-stale-agent-sources
prepare-agent-source-inventory
run-agent-readiness-checklist
```

These names are design candidates, not claims that each workflow is currently executable through native skills.

## 13. Proposed Repository Skill Backlog

Capabilities requiring custom code or external interfaces remain in the GitHub Copilot workbench.

```text
analyze-document
convert-document
recommend-topic-boundaries
generate-content-metadata
validate-canonical-content
generate-publication-map
render-content
design-sharepoint-content-model
generate-sharepoint-deployment-package
design-approval-workflow
evaluate-sharepoint-agent
produce-release-evidence
```

If later platform tools are approved, separate action skills could deploy the reviewed artifacts.

## 14. Workbench Architecture Update

The documentation supports this layered architecture:

```text
Government Knowledge Standards and Policies
        ↓
GitHub Copilot Knowledge Workbench
Design → Convert → Validate → Test → Package → Produce Evidence
        ↓
Reviewed Configuration and Content Artifacts
        ↓
Copilot in SharePoint
Ask → Create → Organize → Run Native Skills → Guide Site Users
        ↓
SharePoint Governance
Permissions → Metadata → Retention → Sensitivity → Auditing → Approval
        ↓
Copilot and Agent Experiences
Find → Answer → Act Within Permission → Evaluate → Monitor
```

## 15. Suggested Pilot

A bounded pilot could test both workbench layers.

### Phase A — Repository Preparation

1. Complete the CEIS canonical-content conversion and evidence review.
2. Produce a manageable topic package and explicit publication map.
3. Define a minimal SharePoint metadata schema.
4. Prepare skill specifications and evaluation cases.

### Phase B — SharePoint Deployment

1. Select an approved pilot site.
2. Verify Copilot in SharePoint availability and licensing.
3. Confirm the site's inclusion or exclusion status.
4. Review Restricted Content Discovery and permissions.
5. Upload or publish approved content through the authorized process.
6. Apply approved metadata and governance controls.

### Phase C — Native Skill Trial

1. Create one low-risk, site-scoped review or metadata skill from natural language.
2. Review the draft before saving.
3. Confirm the generated `SKILL.md` location and contents.
4. Apply appropriate permissions to Agent Assets.
5. Run the skill on a controlled content set.
6. Record input, output, user permissions, reviewer result, and audit evidence.

### Phase D — Evaluation

Assess:

- skill-routing accuracy;
- user understanding;
- false positives and false negatives;
- permission behaviour;
- review effort;
- content quality;
- metadata quality;
- auditability;
- distinction between recommendation and execution;
- overlap and gaps between native SharePoint skills and repository skills.

## 16. Questions Requiring Verification

Before implementation, verify:

- whether the target tenant is in a supported cloud;
- whether the preview is available;
- who has Microsoft 365 Copilot licenses;
- whether the organization has opted out tenant-wide or for the target sites;
- whether the approved SharePoint Online Management Shell version is available;
- who may create skills;
- whether Agent Assets permissions should be restricted;
- which native actions the proposed skills can actually perform;
- audit and retention requirements for generated skill files;
- records treatment of skill definitions and execution outputs;
- how native skill changes are promoted across development, test, and production sites;
- how skill versions and evaluations are recorded;
- how Copilot in SharePoint interacts with the canonical-content source-of-truth model.

## 17. Research-Informed Vision Statement

> The AI-Assisted SharePoint Knowledge Workbench should use two complementary skill environments. Repository-based GitHub Copilot skills provide custom code, deterministic conversion, validation, testing, packaging, and release evidence. Native Copilot in SharePoint skills provide reusable, site-scoped, permission-aware workflows that guide users and interact with SharePoint content through supported capabilities. Government controls determine where Copilot is available, who can create and run skills, how skill definitions are governed, and when a recommendation may become an authorized action.

## 18. Key Takeaway

This Microsoft Learn page moves the workbench vision from general product direction toward a concrete native SharePoint skill model.

The most important findings are:

```text
Copilot in SharePoint is a preview capability.
It uses natural language to ask, create, and run supported workflows.
Availability can be controlled tenant-wide or by selected sites.
Restricted Content Discovery is respected.
Skills encode repeatable multi-step workflows.
Skills are stored as governed Markdown files in SharePoint.
Skills run only within supported capabilities and existing permissions.
Skills cannot call external systems or execute custom code.
```

Therefore, native SharePoint skills should be treated as one execution layer inside the broader workbench—not as a replacement for the GitHub-based conversion and engineering layer.

## 19. Source and Research Limitations

This summary is based primarily on the linked Microsoft Learn page and related Microsoft product-help material retrieved for Copilot in SharePoint, SharePoint skills, agents, and responsible AI.

The feature is documented as preview, and Microsoft notes that:

- enablement changes at general availability;
- usage limits may change;
- the managed model may change;
- unsupported environments remain excluded until Microsoft documents otherwise.

The Microsoft documentation does not define this project's canonical-content architecture, government operating model, GitHub workbench, publication-map contract, or approval design. Those sections are project recommendations and must be reviewed separately.
