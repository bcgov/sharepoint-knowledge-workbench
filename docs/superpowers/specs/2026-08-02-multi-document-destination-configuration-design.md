# Multi-Document Destination Configuration Design

**Status:** DESIGN AND INVENTORY ONLY. Does not authorize implementation, tenant modification, or
library/page/agent/skill creation. Written 2026-08-02, prompted directly by a real Phase 5 Task 5
defect: the upload script for the CEIS Manual's rendered-Markdown content duplicated ~319 images
already uploaded to a separate library, because no shared destination-configuration model existed
to route both uploads to the same place. See
[[project_shared_config_parameterized_scripts_proposal]] (superseded in detail by this document,
kept as the earlier informal record) and
[[feedback_design_for_the_end_not_convenient_default]] for why this design exists now rather than
being deferred again.

## 0. Problem this solves

Every tenant-scripting tool in this repo currently hardcodes its own destination decisions
(library names, folder structure, agent names) directly in PowerShell scripts, and duplicates its
own `config.psd1`/`config.psd1.example` per phase folder (`tools/phase-3-sharepoint-discovery/`,
`tools/phase-4-native-sharepoint-skills/` — as `tenant-config.psd1` there, inconsistently named —
`tools/phase-5-sharepoint-knowledge-agent-pilot/`). This works for one document (CEIS Manual) but
breaks down the moment a second manual, policy, or procedure needs converting: there is no shared
model for *where things go*, so every new document risks either duplicating content that should be
shared, or silently colliding with an existing document's files.

This design separates three concerns that are currently conflated in ad hoc script defaults:
**connection** (how do I reach the tenant), **publication intent** (where should this specific
document's outputs normally go), and **operation** (what exactly is this script doing right now).

## 1. Three configuration layers

### Layer 1 — Root connection configuration

Tracked template: `config.psd1.example` (already exists per-phase-folder; this design
consolidates to one root-level file: `config.psd1.example` at the repo root). User-owned,
git-ignored file: `config.psd1` at the repo root.

```powershell
@{
    SiteUrl                = "https://tenant.sharepoint.com/sites/site"
    TenantId                = ""
    ClientId                = ""
    AuthenticationMode      = "Interactive"

    # Optional, depending on authentication mode
    CertificateThumbprint   = ""
    TenantAdminUrl          = ""

    # Optional defaults, not mandatory operational targets
    DefaultPublicationRoot  = "KnowledgePublications"
    DefaultAgentAssetsRoot  = "AgentAssets"
}
```

Must never contain: client secrets, access tokens, certificate passwords, user passwords, or any
document-specific value (library names, folder names, agent names, page names, skill names,
overwrite decisions, rollback targets). Connection configuration answers "where and how do I
connect?" — never "what exact artifact should this script create or modify?"

### Layer 2 — Per-document publication profile

Every converted source document or structured content package gets its own profile at
`publication-profiles/<DocumentId>.publication.psd1` (e.g.
`publication-profiles/ceis-manual.publication.psd1`). Tracked in git (no secrets, no PII, no
environment-sensitive identifiers) — this is project content, analogous in spirit to
`tools/phase-4-native-sharepoint-skills/deployment/deployment-manifest.example.json`'s existing
pattern (skill → target library/folder mapping), generalized to a full document's publication
intent.

```powershell
@{
    SchemaVersion = "1.0"

    Document = @{
        DocumentId        = "ceis-manual"
        Title             = "CEIS Manual"
        ContentType       = "Manual"
        ContentOwner      = ""
        SourcePackagePath = "runs/ceis-manual-v2"
    }

    HumanPublication = @{
        Enabled            = $true
        TargetType         = "DocumentLibrary"
        LibraryName        = "KnowledgePublications"
        RootFolder         = "ceis-manual"
        TopicFolder        = "topics"
        MediaFolder        = "media"
        NavigationFolder   = "navigation"
        PublicationProfile = "multipage-markdown"
    }

    PagePublication = @{
        Enabled            = $false
        TargetType         = "SitePages"
        LibraryName        = "Site Pages"
        RootFolder         = "ceis-manual"
        PageTemplate       = ""
        PageNamePattern    = "{TopicId}.aspx"
    }

    AgentGrounding = @{
        Enabled            = $true
        LibraryName        = "AgentGrounding"
        RootFolder         = "ceis-manual"
        GroundingProfile   = "manual-grounding"
    }

    Agents = @(
        @{
            Enabled             = $true
            AgentId             = "ceis-knowledge-agent"
            AgentName           = "CEIS Knowledge Agent"
            AgentTemplate       = ""
            KnowledgeTargets    = @("HumanPublication")
            IncludeNativeSkills = $false
            Skills              = @()
        }
    )

    NativeSkills = @()   # Add only approved deployed skills

    Evidence = @{
        OutputPath = "docs/reports/publications/ceis-manual"
    }
}
```

This answers: what content package is this? Where should its outputs normally go? Which
representations should be produced? Which agents/skills should use those representations?

### Layer 3 — Explicit script parameters

Every operational script exposes named parameters that override profile values, which override
root-config defaults. Precedence, strictly:

```text
explicit script parameter
  → publication profile
  → explicitly supplied root config
  → approved environment variable
  → repository-root config.psd1
  → fail closed
```

Scripts must never silently infer a write target from filenames or the current working directory.

## 2. Common parameter contract

Every SharePoint-connected script supports, as applicable: `-ConfigPath`, `-SiteUrl`, `-ClientId`,
`-TenantId`, `-AuthenticationMode`, `-PublicationProfilePath`, `-DocumentId`. Every write-capable
script additionally supports `-DryRun`, `-Execute`, `-EvidencePath`. Destructive scripts
additionally support `-ConfirmExactTarget` (matches the existing pattern already used in
`tools/phase-4-native-sharepoint-skills/deployment/scripts/rollback-skill.ps1`'s
`-ConfirmExactTarget` gate). Add only parameters relevant to the script — no universal parameter
block forced onto every script regardless of what it does.

## 3. Operation-specific parameters

| Script type | Parameters |
|---|---|
| Content upload | `-LibraryName`, `-RootFolder`, `-SourcePath`, `-ArtifactType`, `-PublicationProfile`, `-PackageIdentity`, `-Overwrite` |
| Image/media upload | `-LibraryName`, `-RootFolder`, `-MediaFolder`, `-SourceMediaPath`, `-PreserveRelativePaths`, `-Overwrite` |
| ASPX page | `-SitePagesLibrary`, `-RootFolder`, `-PageName`, `-PageTitle`, `-PageTemplate`, `-SourceManifestPath`, `-PromoteAsNews`, `-Overwrite` |
| Agent creation | `-AgentName`, `-AgentDescription`, `-AgentTemplatePath`, `-KnowledgeSourcePaths`, `-KnowledgeLibraryNames`, `-KnowledgeFolderPaths`, `-AgentOutputPath`, `-Overwrite` |
| Agent template | `-TemplateName`, `-TemplateSourcePath`, `-TargetFolder`, `-Overwrite` |
| Native-skill deployment | `-SkillName`, `-SkillSourcePath`, `-AgentAssetsLibrary`, `-SkillsFolder`, `-ExpectedSHA256`, `-Overwrite` |
| Reconciliation | `-DocumentId`, `-PackageIdentity`, `-ExpectedManifestPath`, `-TargetLibrary`, `-TargetRootFolder`, `-ComparisonMode`, `-EvidencePath` |
| Rollback | `-ExactTargetUrl`, `-ExpectedSHA256`, `-Execute`, `-ConfirmExactTarget`, `-EvidencePath` |

None of these operation-specific values belong in root `config.psd1`.

## 4. Multi-manual destination model

Do not assume one manual = one library. Default:

```text
KnowledgePublications/
├── ceis-manual/
│   ├── topics/
│   ├── media/
│   ├── navigation/
│   └── package-manifest.json
├── civil-court-procedures/
│   └── ...
└── small-claims-manual/
    └── ...
```

Multiple manuals may share one library when they share permissions, sensitivity, business
ownership, approval process, retention rules, publication lifecycle, metadata model, and
agent-consumption model. Use a separate library when any of those materially differs. Classify
every destination decision as one of: `SHARED_LIBRARY_WITH_DOCUMENT_FOLDER`,
`SEPARATE_LIBRARY_REQUIRED`, `DOCUMENT_SET_REQUIRED`, `SITE_PAGES_REQUIRED`,
`AGENT_ASSET_LOCATION`, `REQUIRES_HUMAN_DECISION`.

## 5. Artifact destination questions (for the setup skill's interview)

**Document identity:** stable `DocumentId`? Human-readable title? Content type (manual, policy,
procedure, guide, reference, training, other)? Content owner?

**Human-facing publication:** publish human-readable output at all? Share the default knowledge
library, or use its own root folder? Separate topics/media/navigation subfolders? Markdown, ASPX,
or another implemented profile?

**Images and media:** stay inside the document's root folder (default:
`<HumanLibrary>/<DocumentId>/media/` — never one global flat image folder)? Shared across
manuals? Filenames globally unique? Relative paths preserved? Retention/permission separation
required?

**ASPX pages:** required at all (do not assume every document needs one)? Which library? Own
folder? Template? Name-generation pattern?

**Agent grounding:** use the human-facing files directly, or a separate agent-optimized
representation? Scoped to one document, several, or the whole approved library? Folder-scoped or
explicit source list? Uniform permissions across selected sources?

**Agent creation:** new or reuse existing? Name/purpose? Which publications ground it? Create now
or only produce a deployment package? Native skills included? Template?

**Native skills:** required at all? Already approved/deployed, or does the profile only reference
them pending separate deployment authorization? (Never silently deploy a skill because a profile
references it.)

## 6. Target-resolution algorithm

One reusable component resolves: root config + publication profile + script parameters + artifact
type → exact resolved SharePoint target, with the configuration source of every resolved value
recorded. Conceptually: `SiteUrl + artifact type + (explicit LibraryName or profile default) +
DocumentId + artifact-specific folder → exact target URL`. Examples:

```text
Human topic:    KnowledgePublications/ceis-manual/topics/topic-001.md
Media:          KnowledgePublications/ceis-manual/media/image-001.png
Agent grounding: AgentGrounding/ceis-manual/grounding.md
ASPX page:      Site Pages/ceis-manual/topic-001.aspx
Native skill:   AgentAssets/Skills/review-manual-topics/SKILL.md
```

Every write script prints: resolved `SiteUrl`, resolved library, resolved `DocumentId`, resolved
folder, resolved exact target, the configuration source of each value, and dry-run/write mode.

## 7. Collision prevention (validated before any write)

`DocumentId` non-empty and normalized; target folder belongs to the intended document; same
filename under a different `DocumentId` is safe (different folder); same filename within the same
`DocumentId` is detected as a real collision; package identity matches the publication profile;
overwrite behavior is explicit, never implicit; one manual's write can never overwrite another
manual's content; rollback is bounded to exactly one document package. A script must not default
to a flat library root for multi-document publication unless the profile explicitly approves it.

## 8. Setup plugin

New plugin: `workbench-setup`. Per this repo's own Skill Development Protocol (`CLAUDE.md`), any
new *skill* is authored in the sibling `agent-plugins-skills` monorepo, PR'd, and merged by the
human partner — not written directly in this repo. This section specifies what the skill(s) must
do; it does not authorize writing skill code here.

**`setup-sharepoint-connection`** — creates the root, git-ignored `config.psd1`. Asks: `SiteUrl`,
`ClientId`, `TenantId`, `AuthenticationMode`, optional certificate thumbprint, optional default
publication roots.

**`initialize-publication-profile`** (later) — creates
`publication-profiles/<DocumentId>.publication.psd1` by asking the Section 5 questions. Must:
propose defaults; show every resolved destination before writing; allow overrides; validate
collisions; write only after explicit confirmation; never connect to or modify SharePoint during
profile generation unless the user separately requests read-only target validation.

## 9. Agent-assisted setup behavior

A setup agent may *recommend* defaults from content type, topic count, media presence, required
output formats, permissions, ownership, agent scope, and existing approved libraries — but every
recommendation is a proposal, tagged `PROPOSED_DEFAULT`, `USER_CONFIRMED`, `USER_OVERRIDDEN`, or
`REQUIRES_GOVERNANCE_DECISION`. The agent must never silently choose: library creation, permission
boundaries, agent scope, overwrite behavior, native-skill deployment, or retention model.

## 10. Script inventory and parameter matrix (to build before refactoring)

Before any script is touched, inventory every script that publishes files, uploads images,
creates/updates pages, creates agents, creates agent templates, deploys native skills, creates
libraries/folders, reconciles state, or rolls back artifacts. Real candidates already in this
repo: `tools/phase-3-sharepoint-discovery/{push-aspx-experiment.ps1, provision-agentassets.ps1,
phase-3-0-tenant-discovery.ps1, run-phase3-tenant-pilot.ps1}`; `tools/
phase-4-native-sharepoint-skills/deployment/scripts/{task-8-deploy-review-manual-topics.ps1,
task-8a-reconcile-deployed-skill.ps1, task-9-retrieve-topic-metadata.ps1, task-12-rollback.ps1,
rollback-skill.ps1, rollback-skill-deployment.ps1, provision-agentassets.ps1,
create-test-agent.ps1, create-corrected-agent.ps1, create-aspx-only-agent-test.ps1,
create-updated-agent-sitepages.ps1, deploy-and-verify-skill.ps1}`; `tools/
phase-5-sharepoint-knowledge-agent-pilot/upload-rendered-markdown.ps1`. For each, record: script
path, plugin/phase owner, current hardcoded values, current config dependencies, required
connection parameters, required operation parameters, write-safety gate, publication-profile
support, standalone-install support, tests required. Do not refactor blindly before this matrix
exists.

## 11. Tests required (once implementation is authorized)

Root config resolution; publication-profile resolution; explicit parameter override; missing-value
failure (fail closed, not silent default); two manuals in one library; two manuals with the same
topic filename (collision detection); manual-specific media folders; separate-library governance
decision; ASPX enabled vs. disabled; agent-grounding enabled vs. disabled; one-document vs.
multi-document agent scope; profile-generated targets; collision rejection; republishing one
manual without affecting another; rollback of one manual without affecting another; a standalone-
installed script using `-ConfigPath` correctly; no hardcoded sandbox URL anywhere; no secrets ever
written to `config.psd1`.

## 12. Future authoring/republication compatibility

The publication profile is designed to remain the stable destination contract beyond first-time
upload: `DocumentId → approved structured-content update → identify affected outputs → rerender
affected publication profiles → republish only that document → reconcile without changing other
documents`. This is deliberately the same shape as the Phase 6.5 loop already recorded in
`docs/vision/master-initiative-plan-workstreams-and-phases.md` ("Ongoing Structured Content
Authoring and Republishing") — this design's publication profile is what that phase's
republication step would resolve destinations against, once triggered. Not authorized to build
now; noted for consistency.

## 13. Implementation-phase recommendation

This design is infrastructure, not a phase deliverable in its own right — it has no user-facing
content or agent to show for an exit gate the way Phases 1-6.5 do. Recommended placement: a new
**prerequisite subphase under Phase 3** (Subphase 3.1, which already owns library-schema mapping)
rather than a standalone numbered phase, since its entry gate is naturally satisfied by Phase
5.5A's own entry gate ("a concrete second content type is identified with a real document/need
behind it") — the two should trigger together, since a second real document is exactly when this
design's value (avoiding duplication/collision across manuals) becomes real rather than
speculative. **Not authorized to implement now** — recorded here so it exists as a named,
detailed design the moment a real second document shows up, rather than being re-derived from
scratch or (as almost happened this session) skipped in favor of a convenient one-off script.

## Recommended default (summary)

```text
one human-publication library
  → one folder per DocumentId
      → topics/media/navigation beneath it

one agent-grounding library
  → one folder per DocumentId

agents
  → scope to one or more DocumentId folders
```

Use a separate library only when permissions, lifecycle, ownership, retention, or artifact purpose
requires a real boundary. Core rule: **root config** = connection/environment defaults;
**publication profile** = one document's intended destinations; **script parameters** = this
operation's exact behavior and overrides.
