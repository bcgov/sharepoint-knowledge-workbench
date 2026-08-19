# ==============================================================================
# Script Name: phase-3-0-tenant-discovery.ps1
# Description: Phase 3.0 (SharePoint Tenant-Capability Discovery) read-only probe
#              script for the manual-conversion-poc initiative's Phase 3 pilot
#              (Governed SharePoint Knowledge Pilot). Answers, with observed
#              evidence rather than assumption, the specific questions Phase 3's
#              provisional metadata schema (spec Section 7) needs answered before
#              it stops being provisional.
#
#              Every probe below returns an explicit result ENVELOPE
#              (Status/ObservedAt/RequiredPermission/ErrorType/ErrorMessage/
#              EvidenceSource/DecisionImpact/Data) rather than a bare value or
#              empty array. This matters because a script whose entire purpose
#              is replacing assumptions with observed facts must never let
#              "legitimately empty" and "query failed/forbidden" collapse into
#              the same JSON shape — see New-ProbeResult below.
#
#              Report sections:
#                1. Meta                — script/environment/connection context
#                                          (PnP/PS version, site/web IDs,
#                                          connected account, git commit).
#                2. Web                 — site/web template, configuration,
#                                          language (master plan Stage 3.0.1.2).
#                3. Lists               — all lists/libraries + versioning
#                                          config (Stage 3.0.1.2 + evidence
#                                          matrix's proposed addition #1).
#                4. SiteFields          — column/field types actually in use
#                                          on this tenant (Stage 3.0.2.5), as a
#                                          concrete basis for confirming
#                                          Section 7's proposed column types.
#                5. ContentTypes        — site content type inventory.
#                6. SiteGroups          — candidate distinct identities for the
#                                          future Stage 3.4.2 oversharing test
#                                          (evidence matrix's proposed addition #2).
#                7. AgentAssetsLibrary  — existence + governance settings
#                                          (moderation/checkout/draft-visibility/
#                                          crawl/content-types) + unique-permission
#                                          signal for the "AgentAssets" library,
#                                          per docs/research/field-note-sharepoint-
#                                          agentassets-review-manual-topics-skill.md's
#                                          observed naming.
#                8. CustomAgents        — existing Copilot Agent (*.agent) files,
#                                          via the real cmdlet Get-PnPCopilotAgent.
#                9. ReadyMadeAgent      — ALWAYS ManualRequired: Microsoft states
#                                          the ready-made site agent has no
#                                          associated .agent file, so an empty
#                                          CustomAgents list does NOT mean there
#                                          is no agent experience on this site.
#               10. NativeSkills        — SKILL.md files discovered under
#                                          AgentAssets/Skills/*, kept as a
#                                          SEPARATE artifact type from
#                                          CustomAgents (a native skill is a
#                                          repeatable workflow; a SharePoint
#                                          agent is a conversational experience —
#                                          they are not the same thing).
#               11. CopilotAdmin        — tenant-level Copilot in SharePoint
#                                          limited-mode setting
#                                          (Get-PnPCopilotAdminLimitedMode).
#               12. RestrictedContentDiscovery — best-effort read of the site's
#                                          Restricted Content Discovery status
#                                          via Get-PnPTenantSite; expected to
#                                          require SharePoint Administrator
#                                          rights this app registration does
#                                          not have (by design — see below).
#               13. ManualStepsNeeded   — everything this script fundamentally
#                                          cannot observe read-only (rendering
#                                          fidelity, authoring entitlement,
#                                          agent-to-skill invocation, licensing).
#
#              This script is strictly READ-ONLY — it creates, modifies, and
#              deletes nothing in the tenant, per the master plan's Subphase
#              3.0.2 staged protocol ("read-only first"). The app registration
#              used to connect is INTENTIONALLY scoped without permission-
#              management rights (no Manage Permissions / Full Control) — so
#              probes that need that (e.g. full role-assignment enumeration)
#              are EXPECTED to report Forbidden, by design, not a bug in this
#              script or a tenant misconfiguration.
#
#              Modeled on the login/config pattern from the sibling
#              check-appearance-city-to-be-verified.ps1 example script (CMAT SPO
#              Replatform Team), adapted for this initiative's own tenant/site
#              and discovery questions. Config is loaded from a sibling
#              config.psd1 in the SAME directory.
#
# Output:      A single JSON report at $OutputPath. This file is tenant evidence
#              — do NOT commit it to the manual-conversion-poc Git repository.
#              Per Phase 3 spec Section 16's evidence-storage split, only a
#              hand-written SANITIZED SUMMARY (no raw URLs/identities/site
#              structure) belongs in docs/reports/; this raw JSON is a
#              controlled-original and stays out of Git (already gitignored
#              at this tools/ path — see repo .gitignore).
#
# Usage:       pwsh ./phase-3-0-tenant-discovery.ps1
#              (Requires the PnP.PowerShell module and interactive login via the
#              delegated app registration in config.psd1 — a browser window will
#              open for you to authenticate. No credentials are stored by this
#              script or passed on the command line.)
# ==============================================================================

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$ConfigPath = (Join-Path $PSScriptRoot "config.psd1"),

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = (Join-Path $PSScriptRoot "phase-3-0-discovery-report.json"),

    # Hidden/system lists (e.g. "Web Part Gallery", "Master Page Gallery") are
    # excluded by default — they add noise and aren't candidate pilot libraries.
    # Pass -IncludeHiddenLists to include them if you need the full picture.
    [Parameter(Mandatory = $false)]
    [switch]$IncludeHiddenLists,

    # Optional: name of a candidate pilot library (if one already exists) to run
    # the same governance/permission-signal probe against as AgentAssets gets.
    # Leave unset if no candidate library exists yet.
    [Parameter(Mandatory = $false)]
    [string]$PilotLibraryTitle
)

# ------------------------------------------------------------------------------
# Result-envelope helper (Priority 0 fix). Every probe below returns one of
# these instead of a bare value, so "Empty"/"Observed"/"Forbidden"/"Failed" can
# never be silently confused with each other downstream.
# ------------------------------------------------------------------------------
function New-ProbeResult {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("Observed", "Empty", "Forbidden", "Unavailable", "NotSupported", "Failed", "ManualRequired")]
        [string]$Status,

        [Parameter(Mandatory = $false)]
        $Data = $null,

        [Parameter(Mandatory = $false)]
        [string]$RequiredPermission = $null,

        [Parameter(Mandatory = $false)]
        [string]$ErrorType = $null,

        [Parameter(Mandatory = $false)]
        [string]$ErrorMessage = $null,

        [Parameter(Mandatory = $false)]
        [string]$EvidenceSource = $null,

        [Parameter(Mandatory = $false)]
        [string]$DecisionImpact = $null
    )
    return [PSCustomObject]@{
        Status             = $Status
        ObservedAt         = (Get-Date).ToString("o")
        RequiredPermission = $RequiredPermission
        ErrorType          = $ErrorType
        ErrorMessage       = $ErrorMessage
        EvidenceSource     = $EvidenceSource
        DecisionImpact     = $DecisionImpact
        Data               = $Data
    }
}

# Wraps a scriptblock probe: on success, Status is Empty/Observed depending on
# whether $Data is an empty collection; on failure, Status is Forbidden (if the
# error looks permission-related) or Failed, with the exception message kept.
function Invoke-Probe {
    param(
        [Parameter(Mandatory = $true)] [scriptblock]$Script,
        [Parameter(Mandatory = $true)] [string]$EvidenceSource,
        [Parameter(Mandatory = $true)] [string]$DecisionImpact,
        [Parameter(Mandatory = $false)] [string]$RequiredPermission = $null
    )
    try {
        $data = & $Script
        $isEmpty = ($null -eq $data) -or (($data -is [array]) -and $data.Count -eq 0)
        return New-ProbeResult -Status $(if ($isEmpty) { "Empty" } else { "Observed" }) -Data $data `
            -EvidenceSource $EvidenceSource -DecisionImpact $DecisionImpact -RequiredPermission $RequiredPermission
    }
    catch {
        $msg = $_.Exception.Message
        $looksForbidden = $msg -match "Unauthorized|Forbidden|Access is denied|403|unauthorized operation"
        return New-ProbeResult -Status $(if ($looksForbidden) { "Forbidden" } else { "Failed" }) `
            -ErrorType $_.Exception.GetType().Name -ErrorMessage $msg `
            -EvidenceSource $EvidenceSource -DecisionImpact $DecisionImpact -RequiredPermission $RequiredPermission
    }
}

# Runs a governance/permission-signal probe against a single named list/library —
# used for both AgentAssets and (optionally) a candidate pilot library, so both
# get the identical evidence shape.
function Get-LibraryGovernanceProbe {
    param([Parameter(Mandatory = $true)] [string]$ListTitle)

    $result = [PSCustomObject]@{
        ListTitle                = $ListTitle
        Exists                   = New-ProbeResult -Status "Unavailable"
        HasUniqueRoleAssignments = New-ProbeResult -Status "Unavailable"
        RoleAssignments          = New-ProbeResult -Status "Unavailable"
        Governance               = New-ProbeResult -Status "Unavailable"
    }

    $result.Exists = Invoke-Probe -EvidenceSource "Get-PnPList -Identity '$ListTitle'" `
        -DecisionImpact "Confirms the library exists before any other probe against it is meaningful." `
        -Script { $l = Get-PnPList -Identity $ListTitle -ErrorAction Stop; if ($l) { @($l.Title) } else { @() } }

    if ($result.Exists.Status -ne "Observed") {
        return $result
    }

    $result.HasUniqueRoleAssignments = Invoke-Probe -EvidenceSource "Get-PnPList -Includes HasUniqueRoleAssignments" `
        -DecisionImpact "Whether this library breaks permission inheritance — a prerequisite signal for oversharing risk." `
        -Script { , (Get-PnPList -Identity $ListTitle -Includes HasUniqueRoleAssignments -ErrorAction Stop).HasUniqueRoleAssignments }

    # Full role-assignment enumeration needs Manage Permissions/Full Control on the
    # list. This app registration is INTENTIONALLY scoped without that (manage-only,
    # no permission changes) — so Forbidden here is expected-by-design, not a bug.
    $result.RoleAssignments = Invoke-Probe -EvidenceSource "Get-PnPList -Includes RoleAssignments (Member/RoleDefinitionBindings)" `
        -DecisionImpact "Which principals/roles are actually assigned — needed to confirm no broad principal (Members/Visitors/Everyone) is overshared on a governed library. NOT determinable with a manage-only app registration; requires an account with Manage Permissions/Full Control." `
        -RequiredPermission "Manage Permissions / Full Control on the list" `
        -Script {
            $l = Get-PnPList -Identity $ListTitle -Includes RoleAssignments -ErrorAction Stop
            $rows = @()
            foreach ($ra in $l.RoleAssignments) {
                $member = Get-PnPProperty -ClientObject $ra -Property Member
                $roleDefs = Get-PnPProperty -ClientObject $ra -Property RoleDefinitionBindings
                $rows += [PSCustomObject]@{
                    PrincipalTitle = $member.Title
                    PrincipalType  = $member.PrincipalType.ToString()
                    Roles          = @($roleDefs | ForEach-Object { $_.Name })
                }
            }
            $rows
        }

    $result.Governance = Invoke-Probe -EvidenceSource "Get-PnPList -Includes EnableModeration,ForceCheckout,DraftVersionVisibility,NoCrawl,OnQuickLaunch,ContentTypesEnabled" `
        -DecisionImpact "Confirms whether draft/approval/checkout controls this library depends on for governed publication are actually enabled, rather than assumed." `
        -Script {
            $l = Get-PnPList -Identity $ListTitle -Includes EnableModeration, ForceCheckout, DraftVersionVisibility, NoCrawl, OnQuickLaunch, ContentTypesEnabled -ErrorAction Stop
            , ([PSCustomObject]@{
                EnableModeration       = $l.EnableModeration
                ForceCheckout          = $l.ForceCheckout
                DraftVersionVisibility = $l.DraftVersionVisibility.ToString()
                NoCrawl                = $l.NoCrawl
                OnQuickLaunch          = $l.OnQuickLaunch
                ContentTypesEnabled    = $l.ContentTypesEnabled
            })
        }

    return $result
}

if (-not (Test-Path $ConfigPath)) {
    Write-Error "Config file not found: $ConfigPath. Copy config.psd1.example (in this same folder) to config.psd1 and fill in ClientId/TenantId/SiteUrl before running this script."
    exit 1
}

Write-Host "Loading configuration from $ConfigPath..." -ForegroundColor Cyan
$config = Import-PowerShellDataFile -Path $ConfigPath

foreach ($required in @("ClientId", "TenantId", "SiteUrl")) {
    if (-not $config.ContainsKey($required) -or [string]::IsNullOrWhiteSpace($config[$required])) {
        Write-Error "config.psd1 is missing a value for '$required'. This script cannot connect without it."
        exit 1
    }
}

Write-Host "Connecting to SPO at $($config.SiteUrl) (interactive delegated login — a browser window will open)..." -ForegroundColor Cyan
Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ForceAuthentication -ErrorAction Stop

Write-Host "Connected successfully!" -ForegroundColor Green

# --- 1. Meta: environment/connection context (Priority 0) ---
Write-Host "Recording script/environment/connection metadata..." -ForegroundColor Yellow
$gitCommit = $null
try { $gitCommit = (git -C $PSScriptRoot rev-parse --short HEAD 2>$null) } catch { $gitCommit = $null }
$currentUserLoginName = $null
try { $currentUserLoginName = (Get-PnPProperty -ClientObject (Get-PnPWeb) -Property CurrentUser -ErrorAction Stop).LoginName } catch { $currentUserLoginName = $null }

$meta = [PSCustomObject]@{
    ScriptGitCommit       = $gitCommit
    ExportDate            = (Get-Date).ToString("o")
    PnPPowerShellVersion  = (Get-Module PnP.PowerShell).Version.ToString()
    PowerShellVersion     = $PSVersionTable.PSVersion.ToString()
    SiteUrl               = $config.SiteUrl
    ConnectedAccount      = $currentUserLoginName
    AuthenticationType    = "Interactive delegated (Connect-PnPOnline -Interactive -ForceAuthentication)"
    AppRegistrationScope  = "Intentionally manage-only: no permission-management (Manage Permissions/Full Control) rights. Forbidden results on permission-enumeration probes below are expected-by-design, not tenant misconfiguration or a script bug."
    WebId                 = $null
    SiteId                = $null
    IncludeHiddenLists    = [bool]$IncludeHiddenLists
    PilotLibraryRequested = $PilotLibraryTitle
}
try { $meta.WebId = (Get-PnPWeb -Includes Id -ErrorAction Stop).Id.ToString() } catch { }
try { $meta.SiteId = (Get-PnPSite -Includes Id -ErrorAction Stop).Id.ToString() } catch { }

$report = [PSCustomObject]@{
    Meta                       = $meta
    Purpose                    = "Phase 3.0 tenant-capability discovery (read-only) for manual-conversion-poc Phase 3 pilot"
    Web                        = $null
    Lists                      = @()
    SiteFields                 = @()
    ContentTypes               = @()
    SiteGroups                 = $null
    AgentAssetsLibrary         = $null
    CustomAgents               = $null
    ReadyMadeAgent             = New-ProbeResult -Status "ManualRequired" `
        -DecisionImpact "Microsoft states the ready-made site agent has no associated .agent file, so CustomAgents.Data.Count == 0 does NOT mean there is no agent experience on this site." `
        -EvidenceSource "docs/research (Microsoft support docs on ready-made SharePoint agents)"
    NativeSkills               = $null
    CopilotAdmin               = $null
    RestrictedContentDiscovery = $null
    PilotLibraryGovernance     = $null
    ManualStepsNeeded          = @(
        ("Stage 3.0.2.4 (native Markdown rendering): this script cannot observe rendered output. " +
         "Manually upload one sample rendered CEIS topic (from runs/ceis-manual-v2/render/) to a " +
         "designated non-production test library, view it in the browser, and record whether it " +
         "renders usably (headings/lists/tables/images) or requires a different representation " +
         "(e.g. a Site Page). Remove the test upload afterward per the staged-write protocol."),
        ("Stage 3.0.2.2 (native SKILL.md authoring): confirm interactively in the Copilot in " +
         "SharePoint UI whether a skill can actually be authored and saved on this site/library. " +
         "NativeSkills below only shows what already exists, not whether the current user/tenant " +
         "can create new skills."),
        ("Stage 3.0.2.1/3.0.2.3 (Copilot in SharePoint licensing/entitlement, agent-creation " +
         "approval, tenant-wide inclusion/KnowledgeAgentScope settings): these require tenant-" +
         "admin-level confirmation beyond what a site-level PnP probe can determine."),
        ("Ready-made agent behavior: whether one exists, is enabled, and how it differs from an " +
         "approved custom agent or a default agent — not observable via Get-PnPCopilotAgent " +
         "(see ReadyMadeAgent field). Confirm manually in the Copilot in SharePoint UI."),
        ("Agent-to-skill invocation: whether a custom SharePoint agent can actually invoke a " +
         "NativeSkills entry, and whether skill availability changes by site/library/folder " +
         "context — not provable from file existence alone."),
        ("Full role-assignment enumeration (who exactly has access to AgentAssets/pilot library): " +
         "this app registration is intentionally manage-only. Confirm via a SharePoint admin or " +
         "an account with Manage Permissions/Full Control, or the SharePoint Advanced Management " +
         "permission-state reports."),
        ("Restricted Content Discovery + KnowledgeAgentScope: RestrictedContentDiscovery below is " +
         "expected to report Forbidden for a non-tenant-admin account. Confirm via a SharePoint " +
         "Administrator (Get-PnPTenantSite or the SharePoint admin center)."),
        ("Agent source-format support: whether Markdown is actually retrievable/citable by a " +
         "SharePoint agent (browser rendering, search indexing, agent grounding, and citation are " +
         "four separate capabilities — do not assume one implies another). Requires a manual " +
         "agent-query test against uploaded Markdown content."),
        ("Hub-site association and potential agent source-scope expansion: if this site is " +
         "associated with a hub, an agent configured against the hub could ground on content " +
         "beyond this site. Confirm hub membership and any hub-scoped agent configuration " +
         "manually or via a tenant admin.")
    )
}

# --- 2. Site/web inventory (Stage 3.0.1.2) ---
Write-Host "Inspecting web/site properties..." -ForegroundColor Yellow
$web = Get-PnPWeb -Includes WebTemplate, Configuration, Language, RegionalSettings
$report.Web = [PSCustomObject]@{
    Title         = $web.Title
    Url           = $web.Url
    WebTemplate   = $web.WebTemplate
    Configuration = $web.Configuration
    Language      = $web.Language
}
Write-Host "  Web template: $($web.WebTemplate) (configuration $($web.Configuration))" -ForegroundColor Green

# --- 3. Lists/libraries inventory, including versioning config (Stage 3.0.1.2 + proposed addition #1) ---
Write-Host "Inspecting lists/libraries (incl. versioning settings)..." -ForegroundColor Yellow
$listParams = @{ Includes = @("EnableVersioning", "EnableMinorVersions", "MajorVersionLimit", "MajorWithMinorVersionsLimit", "BaseTemplate", "ItemCount", "Hidden") }
$lists = Get-PnPList @listParams
foreach ($list in $lists) {
    if (-not $IncludeHiddenLists -and $list.Hidden) { continue }
    $report.Lists += [PSCustomObject]@{
        Title                       = $list.Title
        BaseTemplate                = $list.BaseTemplate.ToString()
        ItemCount                   = $list.ItemCount
        Hidden                      = $list.Hidden
        EnableVersioning            = $list.EnableVersioning
        EnableMinorVersions         = $list.EnableMinorVersions
        MajorVersionLimit           = $list.MajorVersionLimit
        MajorWithMinorVersionsLimit = $list.MajorWithMinorVersionsLimit
    }
}
Write-Host "  Found $($report.Lists.Count) list(s)/librar(ies) (hidden $(if ($IncludeHiddenLists) {'included'} else {'excluded'}))" -ForegroundColor Green

# --- 4. Site (web-scoped) field/column type inventory (Stage 3.0.2.5) ---
Write-Host "Inspecting site columns (field types actually in use on this tenant)..." -ForegroundColor Yellow
$fields = Get-PnPField -InSiteHierarchy
foreach ($f in $fields) {
    if ($f.Hidden -and -not $IncludeHiddenLists) { continue }
    $choices = $null
    if ($f.TypeAsString -eq "Choice" -or $f.TypeAsString -eq "MultiChoice") {
        try { $choices = (Get-PnPProperty -ClientObject $f -Property "Choices").Choices } catch { $choices = $null }
    }
    $report.SiteFields += [PSCustomObject]@{
        InternalName = $f.InternalName
        Title        = $f.Title
        TypeAsString = $f.TypeAsString
        Required     = $f.Required
        Group        = $f.Group
        Choices      = $choices
    }
}
Write-Host "  Found $($report.SiteFields.Count) site column(s)" -ForegroundColor Green

# --- 5. Content type inventory ---
Write-Host "Inspecting site content types..." -ForegroundColor Yellow
$contentTypes = Get-PnPContentType
foreach ($ct in $contentTypes) {
    $report.ContentTypes += [PSCustomObject]@{
        Name        = $ct.Name
        Id          = $ct.Id.ToString()
        Group       = $ct.Group
        Description = $ct.Description
    }
}
Write-Host "  Found $($report.ContentTypes.Count) content type(s)" -ForegroundColor Green

# --- 6. Site groups (candidate identities for Stage 3.4.2, evidence matrix's proposed addition #2) ---
Write-Host "Inspecting site groups (candidate identities for the future oversharing/permission test)..." -ForegroundColor Yellow
$report.SiteGroups = Invoke-Probe -EvidenceSource "Get-PnPGroup" `
    -DecisionImpact "Candidate distinct identities for the Stage 3.4.2 oversharing/permission test. Does not itself perform that test." `
    -Script {
        $groups = Get-PnPGroup -ErrorAction Stop
        $groups | ForEach-Object {
            [PSCustomObject]@{
                Title                          = $_.Title
                Id                             = $_.Id
                OwnerTitle                     = $_.OwnerTitle
                OnlyAllowMembersViewMembership = $_.OnlyAllowMembersViewMembership
            }
        }
    }
Write-Host "  Site groups: $($report.SiteGroups.Status)" -ForegroundColor Green

# --- 7. AgentAssets library governance/permission-signal probe (Stages 3.0.2.1-3.0.2.3) ---
# Per docs/research/field-note-sharepoint-agentassets-review-manual-topics-skill.md, the observed
# library name is "AgentAssets" (no space). Kept as its own report section, separate from
# CustomAgents/NativeSkills below, per the research's explicit recommendation not to conflate
# library existence with agent/skill artifacts.
Write-Host "Inspecting AgentAssets library governance/permissions..." -ForegroundColor Yellow
$report.AgentAssetsLibrary = Get-LibraryGovernanceProbe -ListTitle "AgentAssets"
Write-Host "  AgentAssets exists: $($report.AgentAssetsLibrary.Exists.Status); governance: $($report.AgentAssetsLibrary.Governance.Status); role assignments: $($report.AgentAssetsLibrary.RoleAssignments.Status)" -ForegroundColor Green

# --- 7b. Optional: same governance/permission-signal probe for a named candidate pilot library ---
if (-not [string]::IsNullOrWhiteSpace($PilotLibraryTitle)) {
    Write-Host "Inspecting candidate pilot library '$PilotLibraryTitle' governance/permissions..." -ForegroundColor Yellow
    $report.PilotLibraryGovernance = Get-LibraryGovernanceProbe -ListTitle $PilotLibraryTitle
    Write-Host "  '$PilotLibraryTitle' exists: $($report.PilotLibraryGovernance.Exists.Status)" -ForegroundColor Green
}
else {
    $report.PilotLibraryGovernance = New-ProbeResult -Status "NotSupported" `
        -DecisionImpact "No candidate pilot library named yet (-PilotLibraryTitle not supplied). Re-run with that parameter once a candidate library exists." `
        -EvidenceSource "N/A - not requested this run"
}

# --- 8. Custom Copilot Agents (*.agent files) — kept separate from ReadyMadeAgent/NativeSkills ---
Write-Host "Inventorying existing Copilot Agent (.agent) files..." -ForegroundColor Yellow
$report.CustomAgents = Invoke-Probe -EvidenceSource "Get-PnPCopilotAgent" `
    -DecisionImpact "Existing custom .agent files site-wide. An empty result does NOT mean no agent experience exists — see ReadyMadeAgent." `
    -Script {
        $agents = Get-PnPCopilotAgent -ErrorAction Stop
        $agents | ForEach-Object { [PSCustomObject]@{ Name = $_.Name; ServerRelativeUrl = $_.ServerRelativeUrl } }
    }
Write-Host "  Custom agents: $($report.CustomAgents.Status)" -ForegroundColor Green

# --- 9. Native SKILL.md files under AgentAssets/Skills — a SEPARATE artifact type from agents ---
# A native SharePoint skill (repeatable workflow, SKILL.md) is not the same artifact as a
# SharePoint agent (conversational experience). This only proves the file exists; it does not
# prove runtime discovery/invocation by any given agent (see ManualStepsNeeded).
Write-Host "Inventorying native SKILL.md files under AgentAssets..." -ForegroundColor Yellow
if ($report.AgentAssetsLibrary.Exists.Status -eq "Observed") {
    $report.NativeSkills = Invoke-Probe -EvidenceSource "Get-PnPFolderItem -FolderSiteRelativeUrl 'AgentAssets' -Recursive" `
        -DecisionImpact "Confirms whether SKILL.md files have actually been authored/saved in AgentAssets on this site; does not confirm agent discovery or invocation of them." `
        -Script {
            $items = Get-PnPFolderItem -FolderSiteRelativeUrl "AgentAssets" -Recursive -ErrorAction Stop
            $skillFiles = $items | Where-Object { $_.Name -eq "SKILL.md" }
            $skillFiles | ForEach-Object {
                [PSCustomObject]@{
                    Name                      = $_.Name
                    ServerRelativeUrl         = $_.ServerRelativeUrl
                    DefinitionDiscovered      = $true
                    RuntimeInvocationVerified = $false
                    AgentInvocationVerified   = $false
                }
            }
        }
}
else {
    $report.NativeSkills = New-ProbeResult -Status "NotSupported" `
        -DecisionImpact "AgentAssets library does not exist on this site, so no Skills subfolder can be inspected." `
        -EvidenceSource "Derived from AgentAssetsLibrary.Exists"
}
Write-Host "  Native skills: $($report.NativeSkills.Status)" -ForegroundColor Green

# --- 10. Copilot admin limited-mode setting (tenant-level Copilot in SharePoint governance signal) ---
Write-Host "Checking Copilot admin limited-mode setting..." -ForegroundColor Yellow
$report.CopilotAdmin = Invoke-Probe -EvidenceSource "Get-PnPCopilotAdminLimitedMode" `
    -DecisionImpact "Tenant-level Copilot in SharePoint governance signal. Expected Forbidden for a non-tenant-admin account." `
    -RequiredPermission "Tenant administrator (SharePoint Administrator role)" `
    -Script { , (Get-PnPCopilotAdminLimitedMode -ErrorAction Stop) }
Write-Host "  Copilot admin limited mode: $($report.CopilotAdmin.Status)" -ForegroundColor Green

# --- 11. Restricted Content Discovery (best-effort; expected Forbidden for a site-level account) ---
# Restricted Content Discovery suppresses org-wide discoverability and removes AI entry points
# (Copilot button, AI actions, agent creation, AI page creation) without changing permissions or
# removing content from the index. This is a distinct question from "who has site access" — see
# the ManualStepsNeeded entry on KnowledgeAgentScope/licensing for the related tenant-wide facts
# this script cannot observe at all.
Write-Host "Attempting Restricted Content Discovery status read (expected to require tenant-admin rights)..." -ForegroundColor Yellow
$report.RestrictedContentDiscovery = Invoke-Probe -EvidenceSource "Get-PnPTenantSite -Identity <SiteUrl> -Detailed" `
    -DecisionImpact "Whether this site is excluded from org-wide AI/Copilot discovery entry points — a distinct fact from site-level permissions." `
    -RequiredPermission "SharePoint Administrator role (tenant admin center access)" `
    -Script { , (Get-PnPTenantSite -Identity $config.SiteUrl -Detailed -ErrorAction Stop) }
Write-Host "  Restricted Content Discovery: $($report.RestrictedContentDiscovery.Status)" -ForegroundColor Green

# --- Save JSON output ---
$jsonContent = $report | ConvertTo-Json -Depth 8
[System.IO.File]::WriteAllText($OutputPath, $jsonContent)

Write-Host "========================================================================" -ForegroundColor Green
Write-Host "Phase 3.0 discovery report exported to: $OutputPath" -ForegroundColor Green
Write-Host "This file contains tenant-specific evidence (site URLs, structure, field" -ForegroundColor Yellow
Write-Host "names, connected account). Do NOT commit it to the manual-conversion-poc" -ForegroundColor Yellow
Write-Host "Git repository. Write a sanitized summary into" -ForegroundColor Yellow
Write-Host "docs/reports/phase-3-sharepoint-pilot/ referencing this file's controlled" -ForegroundColor Yellow
Write-Host "(non-Git) location instead, per spec Section 16's evidence-storage split." -ForegroundColor Yellow
Write-Host "========================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Manual verification still needed (not automatable read-only):" -ForegroundColor Cyan
foreach ($step in $report.ManualStepsNeeded) {
    Write-Host "  - $step" -ForegroundColor Cyan
}
