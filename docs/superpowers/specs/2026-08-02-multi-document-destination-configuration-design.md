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

**Corrected structure (2026-08-02 external review):** the original single flat hashtable mixed
authentication with destination defaults, and used one ambiguous `DefaultPublicationRoot` value
that the resolver treated as a library name — `Root` can mean a library, a folder, a
server-relative path, or a publication root within a library, so it was never actually
unambiguous. Split into three named sub-sections, and rename the defaults to be artifact-specific
(each one maps 1:1 to an `ArtifactType` in Section 6's resolver, never a generic fallback):

```powershell
@{
    Connection = @{
        SiteUrl            = "https://tenant.sharepoint.com/sites/site"
        TenantId           = ""
        ClientId           = ""
        AuthenticationMode = "Interactive"
    }

    Authentication = @{
        # Optional, depending on AuthenticationMode
        CertificateThumbprint = ""
        TenantAdminUrl        = ""
    }

    Defaults = @{
        # Optional artifact-specific defaults, not mandatory operational targets. Each key maps
        # to exactly one ArtifactType in Section 6 — there is no generic "publication root"
        # fallback that every artifact type shares, because a human-topic default and a
        # native-skill default are never interchangeable.
        DefaultHumanPublicationLibrary  = "KnowledgePublications"
        DefaultAgentGroundingLibrary    = "AgentGrounding"
        DefaultAgentAssetsLibrary       = "AgentAssets"
        DefaultSitePagesLibrary         = "Site Pages"
    }
}
```

**Mandatory vs. optional vs. conditional keys:** `Connection.SiteUrl`, `Connection.TenantId`,
`Connection.ClientId`, and `Connection.AuthenticationMode` are mandatory — a script cannot connect
without them. `Authentication.*` are conditional — required only when `AuthenticationMode` is a
mode that needs them (e.g. certificate-based auth needs `CertificateThumbprint`; interactive mode
needs neither). `Defaults.*` are optional — a script always accepts an explicit override parameter
that takes precedence, per Section 1 Layer 3's precedence order.

Must never contain: client secrets, access tokens, certificate passwords, user passwords, or any
document-specific value (library names *for a specific document*, folder names, agent names, page
names, skill names, overwrite decisions, rollback targets — the `Defaults.*` keys above are
tenant-wide fallbacks, not per-document values, which is the distinction that matters). Connection
configuration answers "where and how do I connect, and what are this tenant's general-purpose
library defaults?" — never "what exact artifact should this specific document's script create or
modify?"

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
        # PackageIdentity is the canonical package's own identity (Phase 2's package_identity —
        # see docs/architecture/docx-to-content-legacy-references/canonical-contract.md), not a
        # value invented here. Combined with DocumentId and each section's own
        # PublicationProfile/TargetType, it forms the stable composite publication identity —
        # DocumentId + PublicationProfile + PackageIdentity — used wherever a single DocumentId is
        # not specific enough (one document has a Markdown publication, an ASPX publication, AND
        # an agent-grounding publication simultaneously; each needs its own identity, not one
        # shared DocumentId). Section 6's resolver and Section 7's collision check both derive
        # a PublicationId from this triple; it is never set by hand.
        PackageIdentity   = ""
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

    # NativeSkills lists which approved, already-deployed skills this document's agents may
    # reference — it is a reference list, NOT a resolvable target section. Resolving a
    # NativeSkill target (Section 6) never reads this array's shape directly; it takes an exact
    # -SkillName, looks that name up in this list to confirm it's approved for this document, and
    # resolves the skill's OWN deployment target from Defaults.DefaultAgentAssetsLibrary /
    # explicit -SkillsFolder — a document does not own a skill's deployment location.
    NativeSkills = @(
        # @{ SkillName = "review-manual-topics"; Approved = $true }
    )

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

### Layer 1b — Document-workflow profile (added 2026-08-02, architecture decision)

A fourth artifact, upstream of the publication profile: `document-workflows/
<DocumentId>.workflow.psd1`, produced by the future `initialize-document-workflow` skill (Section
8). Where the publication profile (Layer 2) records **where** artifacts go, the workflow profile
records **what processing should occur**:

```powershell
@{
    SchemaVersion = "1.0"

    Document = @{
        DocumentId  = "ceis-manual"
        SourcePath  = "intake/CEIS MANUAL - working version.docx"
        SourceFormat = "docx"
        IsRevision  = $false   # vs. new conversion
    }

    RequestedStages = @("extract", "analyze", "assemble", "render")

    RequestedRendererProfiles = @("multipage-markdown")   # only implemented profiles may appear
    UnsupportedRequests = @()   # e.g. "PDF" if requested but no renderer exists yet — recorded,
                                 # never silently treated as executable

    HumanConfirmationGates = @{
        TopicBoundaries = $true
        PublicationTargets = $true
    }

    PublicationProfilePath = "publication-profiles/ceis-manual.publication.psd1"

    AgentActionsRequested = @()   # e.g. "create-agent", "update-existing-agent" — requests only,
                                   # never auto-executed by this profile's existence

    OutstandingDecisions = @()   # explicit list of unresolved human decisions surfaced during intake
}
```

This profile is planning data only — its existence never triggers execution. A future
`run-document-workflow` orchestration skill (not authorized or designed here) would be the only
thing that reads it to actually invoke domain-plugin capabilities in sequence.

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

**Corrected (2026-08-02 external review):** the original algorithm let every unresolved artifact
type fall back to one generic `DefaultPublicationRoot` — wrong, since a human topic, an agent
grounding file, an ASPX page, and a native skill each have their own default library and must
never silently borrow another artifact type's default. Fallback is now artifact-specific and fails
closed (raises, does not guess) when the specific default is absent:

```text
ArtifactType    -> Default source (Section 1 Layer 1's Defaults.*)
HumanTopic      -> Defaults.DefaultHumanPublicationLibrary
Media           -> Defaults.DefaultHumanPublicationLibrary   (media lives alongside topics)
AgentGrounding  -> Defaults.DefaultAgentGroundingLibrary
AspxPage        -> Defaults.DefaultSitePagesLibrary
NativeSkill     -> Defaults.DefaultAgentAssetsLibrary          (resolves the SKILL's own
                                                                  deployment target, never a
                                                                  per-document target — see
                                                                  Section 1 Layer 2's NativeSkills
                                                                  note)
```

One reusable component resolves: root config `Connection`/`Defaults` + publication profile +
script parameters + `ArtifactType` → exact resolved SharePoint target, with the configuration
source of every resolved value recorded (`OverrideParameter` | `PublicationProfile` | `RootConfig`
| `Default` — `Default` only applies where no root config, profile, or parameter value exists at
all, e.g. `RootFolder` falling back to `DocumentId` itself). Resolution also emits a
`PublicationId` — the composite `DocumentId + PublicationProfile-or-TargetType + PackageIdentity`
identity from Section 1 Layer 2's note — used by Section 7's collision check instead of the raw
resolved path string alone. Examples:

```text
Human topic:     KnowledgePublications/ceis-manual/topics/topic-001.md
Media:           KnowledgePublications/ceis-manual/media/image-001.png
Agent grounding: AgentGrounding/ceis-manual/grounding.md
ASPX page:       Site Pages/ceis-manual/topic-001.aspx
Native skill:    AgentAssets/Skills/review-manual-topics/SKILL.md
```

Every write script prints: resolved `SiteUrl`, resolved library, resolved `DocumentId`, resolved
`PublicationId`, resolved folder, resolved exact target, the configuration source of each value,
and dry-run/write mode.

**Path safety (added 2026-08-02 external review):** the resolver rejects, rather than silently
normalizing away, any of: `..` path-traversal segments; an absolute item path where a relative one
is expected; empty required path segments; duplicate slashes; filename characters invalid for
SharePoint; and any resolved path that would place the item outside its own `DocumentId`'s folder
boundary (e.g. an override that tries to write to `<other-document-id>/...`). A rejected input is
a hard failure, not a best-effort correction — a script must never silently rewrite an unsafe path
into a safe-looking one and proceed.

## 7. Collision prevention (validated before any write)

**Corrected collision identity (2026-08-02 external review):** comparing only the resolved path
string is insufficient — it ignores the site, so identical paths on two different sites (or two
different `PublicationId`s that happen to resolve to visually similar strings before
normalization) could be falsely flagged as colliding, or a real cross-site collision could be
missed. Collision identity is the tuple: **normalized `SiteUrl` + `LibraryName` + normalized
folder/item path** (equivalently, the resolved `PublicationId` plus the exact resolved path within
it). Two targets collide only when all three match.

Validated before any write: `DocumentId` non-empty and normalized; target folder belongs to the
intended document (path-safety check from Section 6); same filename under a different `DocumentId`
is safe (different folder, different `PublicationId`); same filename within the same `DocumentId`
+ same `PublicationId` is detected as a real collision; `PackageIdentity` matches the publication
profile's recorded value; overwrite behavior is explicit, never implicit; one manual's write can
never overwrite another manual's content; rollback is bounded to exactly one document's
`PublicationId`. A script must not default to a flat library root for multi-document publication
unless the profile explicitly approves it.

## 8. Setup plugin

New plugin: `workbench-setup`, owned and authored directly in this repo at
`plugins/workbench-setup/` (same as `sharepoint-agents-and-skills`/`sharepoint-content-
publication` — this repo's own `plugins/` convention, per CLAUDE.md's "Plugin-Local Resource
Sharing"). **Correction (2026-08-03):** an earlier version of this paragraph wrongly stated these
skills belong in the sibling `agent-plugins-skills` monorepo per the Skill Development Protocol's
Category 1 (marketplace-style) rule — that was a mistake, conflating "use the `marketplace-
manager` skill installed *from* `agent-plugins-skills` as the procedure for `marketplace.json`
updates" with "author this plugin's code *in* `agent-plugins-skills`." This section specifies
what the skill(s) must do; it did not, and does not, authorize implementation ahead of Phase 6
Task 0.17's own approval.

**Canonical template ownership (corrected 2026-08-02 external review):** there must be exactly one
hand-maintained source of truth for `config.psd1.example`'s content, not two. The
`workbench-setup` plugin owns the canonical copy at its own `assets/config.psd1.example`. Any
consuming repo's root `config.psd1.example` (this repo's included) is a materialized hard copy
produced by the plugin's installer, not an independently hand-maintained duplicate — the same
hub-and-spoke, installer-materializes-a-real-copy pattern this repo's own `CLAUDE.md` already
requires for plugin-local resource sharing (`symlink_manager.py` for in-repo sharing; here, the
installer's copy step is the cross-repo equivalent, since a real filesystem symlink cannot cross
repository/plugin package boundaries the way it can within one repo's `plugins/*` tree).

**`setup-sharepoint-connection`** — creates the root, git-ignored `config.psd1` from the canonical
template above. **Corrected behavior (2026-08-02 external review):** the original spec said the
skill "never connects to SharePoint," which directly contradicted this same section's own mention
of an optional read-only validation — those two statements cannot both be true as written. The
corrected, non-contradictory behavior: **generating the config file is the default action and
never connects to anything; an explicit, separate `-TestConnection` flag performs a read-only
validation only after the user deliberately opts in.** Mandatory questions: `SiteUrl`, `TenantId`,
`ClientId`, `AuthenticationMode` (these four are the only unconditionally mandatory keys, matching
Section 1 Layer 1's `Connection.*` block exactly). Conditional: `CertificateThumbprint`/
`TenantAdminUrl`, asked only when `AuthenticationMode` needs them. Optional: the four
`Defaults.*` library names, offered with sensible defaults the user can accept or override.

**`initialize-publication-profile`** (later) — creates
`publication-profiles/<DocumentId>.publication.psd1` by asking the Section 5 questions. Must:
propose defaults; show every resolved destination (via Section 6's resolver) before writing; allow
overrides; validate collisions (via Section 7's check); write only after explicit confirmation;
never connect to or modify SharePoint during profile generation unless the user separately
requests the same kind of explicit, opt-in read-only target validation as
`setup-sharepoint-connection`'s `-TestConnection`.

**`initialize-document-workflow`** (added 2026-08-02, architecture decision — the broader
interactive intake wizard). **Ownership:** `workbench-setup`, not `source-document-extraction`.
`source-document-extraction` answers "given this source document and output directory, extract and
normalize its contents" — it begins only after source identity and workflow intent are already
established. The intake wizard answers the upstream questions (what is this document, what should
happen to it, where do outputs go, which agents use them, what's still undecided) that would
otherwise force `source-document-extraction` to become a cross-domain orchestrator (owning
SharePoint destinations, output formats, publication profiles, agent configuration, native-skill
selection — none of which are its domain).

Covers, across all domains without performing any of their work: source-document identity; new
conversion vs. revision; content type and ownership; requested processing stages; topic-analysis
requirements; requested output formats (**only implemented renderer profiles are offered as
executable choices** — unimplemented formats may be recorded as requested-but-unsupported, never
silently accepted as if executable); human-facing publication locations (via Section 5's
questions); media locations; ASPX publication; agent-grounding representations; existing-vs-new
agent decision; native-skill requirements; governance/evidence settings (owner, status, effective/
review dates, evidence-output location, prototype/dev/test/production intent); and an explicit
list of unresolved human decisions.

**Two distinct output artifacts, not one:**
- `document-workflows/<DocumentId>.workflow.psd1` — records **what processing should occur**
  (pipeline stages requested, renderer profiles requested, human-confirmation gates, agent actions
  requested, unsupported requests, outstanding decisions). New schema, specified in the addendum to
  Section 1 below.
- `publication-profiles/<DocumentId>.publication.psd1` — records **where each resulting artifact
  should be published and which agents may consume it** (unchanged from Section 1 Layer 2 above).
  `initialize-document-workflow` produces this too (superseding `initialize-publication-profile` as
  a standalone entry point — the narrower skill's question set is absorbed into the broader
  wizard's flow, not duplicated as a separate skill).

**Execution boundary — initialization only, first version:**
```text
ask -> propose defaults -> validate -> display resolved configuration -> write profile files -> stop
```
Must **not**, in this first version: extract documents; confirm topic boundaries; render content;
connect to or modify SharePoint; upload files; create pages; create agents; deploy native skills.
Every one of those stays a separate, explicitly invoked domain-plugin capability — a conversational
answer must never silently trigger tenant writes or pipeline execution. A later, separate
`run-document-workflow` orchestration skill may execute an already-approved workflow profile — not
authorized or designed here, and not to be combined with `initialize-document-workflow` in one
skill (combining them would let a planning conversation accidentally start real execution).

**Plugin structure** (`workbench-setup`, only create a `skills/` subfolder once its implementation,
schema, and tests actually exist — no empty taxonomy folders, per this design's own Section 8
canonical-template precedent and the sibling `sharepoint-agents-and-skills` design's Wave 0
correction):
```text
plugins/workbench-setup/
├── scripts/
│   ├── initialize_sharepoint_config.ps1
│   ├── initialize_document_workflow.py
│   ├── initialize_publication_profile.ps1
│   └── validate_workflow_configuration.py
├── assets/
│   ├── config.psd1.example
│   ├── document-workflow.psd1.example
│   └── publication-profile.psd1.example
├── references/
│   ├── destination-decision-guide.md
│   ├── output-profile-catalog.md
│   └── workflow-stage-catalog.md
├── skills/
│   ├── setup-sharepoint-connection/
│   └── initialize-document-workflow/
└── tests/
```

**Not authorized by this section:** creating `workbench-setup`, writing any of the scripts above,
or building `initialize-document-workflow`. This is architecture recording only.

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
