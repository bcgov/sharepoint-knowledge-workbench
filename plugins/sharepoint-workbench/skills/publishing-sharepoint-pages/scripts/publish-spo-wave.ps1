<#
.SYNOPSIS
Publishes a validated set of modern SharePoint page packages in one PnP session.

.DESCRIPTION
Validates every package before connecting, authenticates once, then publishes
each independent page through the existing page publisher. A failed page is
recorded and does not trigger a second login or an automatic retry.

.KEY INPUT DEPENDENCIES
- Corrected wave publication packages
- -WaveManifestPath: authoritative page membership, environment, and target site
- -ConfigPath: config-spo-<env>.psd1 supplying Connection.SiteUrl/ClientId/TenantId
- PnP.PowerShell
- Exact confirmation token for tenant writes
- Explicit duplicate-page decision before target pages are written
- Output path for the mandatory publication receipt when executing
- Interactive console for streamed authentication and page progress messages

.OUTPUTS
- Consolidated JSON publication receipt
- Per-page status and verification results

.FUNCTION INDEX
Read-SpoConfiguration, Get-SpoWaveFileSha256, Write-SpoWaveReceipt,
Publish-SpoWave.

.EXAMPLE
pwsh -File .\plugins\sp-migration\scripts\publication\publish-spo-wave.ps1 `
  -ConfigPath .\config-spo-dev.psd1 `
  -WaveManifestPath .\wave-manifest.json `
  -PackageDirectory .\packages `
  -WaveId wave-1-20260929-1000 -OutputPath .\receipt.json
#>

[CmdletBinding()]
param(
    [string[]]$PackagePath,
    [string]$PackageDirectory,
    [string]$WaveManifestPath,
    [string]$WaveId,
    [string]$ConfigPath,
    [string]$OutputPath,
    [switch]$Execute,
    [string]$ConfirmToken,
    [ValidateSet("Reject", "Approve", "Skip")]
    [string]$DuplicatePageAction,
    [ValidateSet("Backup", "NoBackup")]
    [string]$ExistingPageBackupAction,
    [switch]$NonInteractive,
    [switch]$LibraryMode
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Reads the environment configuration file named by -ConfigPath (config-spo-<env>.psd1).
# Identical in every sp-migration script so each installed skill stays self-contained.
function Read-SpoConfiguration {
    <#
    Returns Path, Environment, SiteUrl, ClientId, TenantId (from Connection.*) and
    Source (the SP2016 Source block, or $null). Throws when -ConfigPath is missing,
    the file does not exist, or a name listed in -Require is empty in Connection.
    #>
    [CmdletBinding()]
    param(
        [AllowEmptyString()][string]$Path,
        [string[]]$Require = @()
    )

    if ([string]::IsNullOrWhiteSpace($Path)) {
        throw "-ConfigPath is required: pass the config-spo-<env>.psd1 file for the environment."
    }
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "-ConfigPath file not found: $Path"
    }

    $raw = Import-PowerShellDataFile -LiteralPath $Path
    $connection = if ($raw.ContainsKey("Connection")) { $raw.Connection } else { @{} }
    foreach ($name in $Require) {
        if (-not $connection.ContainsKey($name) -or [string]::IsNullOrWhiteSpace([string]$connection[$name])) {
            throw "Configuration is missing Connection.${name}: $Path"
        }
    }
    $environment = [string]$connection["Environment"]
    if (-not [string]::IsNullOrWhiteSpace($environment) -and $environment -notin @("dev", "test", "prod")) {
        throw "Connection.Environment must be dev, test, or prod: $Path"
    }

    return [pscustomobject]@{
        Path        = $Path
        Environment = $environment
        SiteUrl     = [string]$connection["SiteUrl"]
        ClientId    = [string]$connection["ClientId"]
        TenantId    = [string]$connection["TenantId"]
        Source      = if ($raw.ContainsKey("Source")) { $raw.Source } else { $null }
    }
}

$batchPackagePath = $PackagePath
$batchPackageDirectory = $PackageDirectory
$batchWaveManifestPath = $WaveManifestPath
$batchConfigPath = $ConfigPath
$batchOutputPath = $OutputPath
$batchExecute = $Execute
$batchConfirmToken = $ConfirmToken
$batchDuplicatePageAction = $DuplicatePageAction
$batchExistingPageBackupAction = $ExistingPageBackupAction
$batchNonInteractive = $NonInteractive
$waveInvocationName = $MyInvocation.InvocationName

. "$PSScriptRoot\publish-spo-page.ps1" -LibraryMode

function Get-SpoWaveFileSha256 {
    <# Returns a lowercase SHA-256 digest for a file's exact bytes. #>
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$Path)

    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Write-SpoWaveReceipt {
    <# Atomically persists a wave receipt/checkpoint after each outcome. #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][object]$Receipt,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $temporary = "$Path.$([guid]::NewGuid().ToString('N')).tmp"
    try {
        $Receipt | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $temporary -Encoding UTF8
        Move-Item -LiteralPath $temporary -Destination $Path -Force
    }
    finally {
        if (Test-Path -LiteralPath $temporary -PathType Leaf) {
            Remove-Item -LiteralPath $temporary -Force
        }
    }
}

function Publish-SpoWave {
    [CmdletBinding()]
    param(
        [string[]]$PackagePath,
        [string]$PackageDirectory,
        [Parameter(Mandatory = $true)][string]$WaveManifestPath,
        [string]$WaveId,
        [Parameter(Mandatory = $true)][string]$SiteUrl,
        [Parameter(Mandatory = $true)][string]$TargetEnvironment,
        [string]$ClientId,
        [string]$TenantId,
        [string]$OutputPath,
        [switch]$Execute,
        [string]$ConfirmToken,
        [ValidateSet("Reject", "Approve", "Skip")]
        [string]$DuplicatePageAction,
        [ValidateSet("Backup", "NoBackup")]
        [string]$ExistingPageBackupAction,
        [switch]$NonInteractive
    )

    $candidatePaths = @($PackagePath)
    if (-not [string]::IsNullOrWhiteSpace($PackageDirectory)) {
        if (-not (Test-Path -LiteralPath $PackageDirectory -PathType Container)) {
            throw "Package directory was not found: $PackageDirectory"
        }
        $candidatePaths = @(
            @(
                Get-ChildItem -LiteralPath $PackageDirectory -Recurse -Filter "*-publication-package.json" |
                    ForEach-Object FullName
                Get-ChildItem -LiteralPath $PackageDirectory -Recurse -Filter "publication-package.json" |
                    ForEach-Object FullName
            ) |
                Sort-Object -Unique
        )
    }
    $resolvedPackages = @(
        foreach ($path in $candidatePaths) {
            if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
                throw "Publication package was not found: $path"
            }
            (Resolve-Path -LiteralPath $path).Path
        }
    )
    if ($resolvedPackages.Count -eq 0) {
        throw "At least one publication package or package directory is required."
    }
    if ($Execute -and [string]::IsNullOrWhiteSpace($OutputPath)) {
        throw "Executable publication requires -OutputPath so completion validation has a durable receipt."
    }
    if (-not (Test-Path -LiteralPath $WaveManifestPath -PathType Leaf)) {
        throw "Authoritative wave manifest was not found: $WaveManifestPath"
    }
    $waveManifest = Get-Content -LiteralPath $WaveManifestPath -Raw | ConvertFrom-Json
    if ([string]::IsNullOrWhiteSpace([string]$waveManifest.WaveId) -or
        [string]::IsNullOrWhiteSpace([string]$waveManifest.TargetEnvironment) -or
        [string]::IsNullOrWhiteSpace([string]$waveManifest.TargetSiteUrl)) {
        throw "Wave manifest must define WaveId, TargetEnvironment, and TargetSiteUrl."
    }
    if (-not [string]::IsNullOrWhiteSpace($WaveId) -and $WaveId -ne [string]$waveManifest.WaveId) {
        throw "Requested WaveId does not match the authoritative wave manifest."
    }
    $WaveId = [string]$waveManifest.WaveId
    if ($TargetEnvironment -ne [string]$waveManifest.TargetEnvironment) {
        throw "Selected configuration environment '$TargetEnvironment' does not match wave manifest '$($waveManifest.TargetEnvironment)'."
    }
    if ($SiteUrl.TrimEnd("/") -ne ([string]$waveManifest.TargetSiteUrl).TrimEnd("/")) {
        throw "Selected configuration SiteUrl does not match the target site bound to the wave manifest."
    }
    $expectedByPageId = @{}
    foreach ($page in @($waveManifest.Pages)) {
        if ([string]::IsNullOrWhiteSpace([string]$page.PageId) -or
            [string]$page.WaveId -ne $WaveId -or
            [string]$page.TargetEnvironment -ne $TargetEnvironment -or
            [string]$page.TargetSiteUrl.TrimEnd("/") -ne $SiteUrl.TrimEnd("/") -or
            [string]::IsNullOrWhiteSpace([string]$page.TargetPageServerRelativeUrl)) {
            throw "Wave manifest contains an incomplete or inconsistent page identity."
        }
        if ($expectedByPageId.ContainsKey([string]$page.PageId)) {
            throw "Wave manifest contains duplicate PageId '$($page.PageId)'."
        }
        $expectedByPageId[[string]$page.PageId] = $page
    }
    if ($expectedByPageId.Count -eq 0 -or [int]$waveManifest.PageCount -ne $expectedByPageId.Count) {
        throw "Wave manifest PageCount must match its non-empty unique Pages list."
    }

    $packages = @(
        foreach ($path in $resolvedPackages) {
            $package = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
            if ($package.WouldPublish -ne $false -or [string]$package.Mode -ne "DryRun") {
                throw "Only non-publishing preparation packages may be executed: $path"
            }
            if ([string]$package.Target.PageMode -notin @("CreateOnly", "OverwriteExisting")) {
                throw "Unsupported publication page mode in package: $path"
            }
            $pageId = [string]$package.Target.PageId
            if (-not $expectedByPageId.ContainsKey($pageId)) {
                throw "Publication package PageId '$pageId' is not a member of the authoritative wave manifest."
            }
            $expectedPage = $expectedByPageId[$pageId]
            if ([string]$package.Target.WaveId -ne $WaveId -or
                [string]$package.Target.Wave -ne [string]$waveManifest.Wave -or
                [string]$package.Target.Environment -ne $TargetEnvironment -or
                [string]$package.Target.TargetSiteUrl.TrimEnd("/") -ne $SiteUrl.TrimEnd("/") -or
                [string]$package.Target.PageServerRelativeUrl -ne [string]$expectedPage.TargetPageServerRelativeUrl -or
                [string]$package.Source.SiteName -ne [string]$expectedPage.SiteName -or
                [string]$package.Source.ServerRelativeUrl -ne [string]$expectedPage.ServerRelativeUrl) {
                throw "Publication package identity does not match wave-manifest PageId '$pageId'."
            }
            [pscustomobject]@{ Path = $path; Package = $package }
        }
    )
    $packageIds = @($packages | ForEach-Object { [string]$_.Package.Target.PageId })
    if ($packageIds.Count -ne $expectedByPageId.Count -or
        @($packageIds | Sort-Object -Unique).Count -ne $expectedByPageId.Count) {
        throw "Publication package set must contain exactly one package for every authoritative wave page."
    }
    $packageEvidence = @(
        foreach ($item in $packages) {
            [ordered]@{
                PackagePath = $item.Path
                PackageSha256 = Get-SpoWaveFileSha256 -Path $item.Path
                PageId = [string]$item.Package.Target.PageId
                Page = [string]$item.Package.Target.PageServerRelativeUrl
                Environment = [string]$item.Package.Target.Environment
                WaveId = [string]$item.Package.Target.WaveId
            }
        }
    )

    $receipt = [ordered]@{
        Operation = "publish-spo-wave"
        WaveId = $WaveId
        RunId = [guid]::NewGuid().ToString()
        Status = if ($Execute) { "PREPARED" } else { "DRY_RUN" }
        TargetEnvironment = $TargetEnvironment
        SiteUrl = $SiteUrl
        DryRun = -not $Execute
        Authentication = if ($Execute) { "one-session" } else { "none" }
        PackageCount = $packages.Count
        ExpectedPageCount = $expectedByPageId.Count
        WaveManifestPath = (Resolve-Path -LiteralPath $WaveManifestPath).Path
        WaveManifestSha256 = Get-SpoWaveFileSha256 -Path $WaveManifestPath
        PackageEvidence = $packageEvidence
        CheckpointCount = 0
        AttemptedPages = [System.Collections.Generic.List[string]]::new()
        PostPublication = [ordered]@{
            EditPublishCycle = "NOT_REQUIRED"
            Status = "NOT_REQUIRED"
            ExpectedResult = "PUBLISHED"
        }
        ExistingPageCheck = [ordered]@{
            Status = if ($Execute) { "NOT_RUN" } else { "NOT_APPLICABLE" }
            ExistingPages = [System.Collections.Generic.List[string]]::new()
            Action = if ($DuplicatePageAction) { $DuplicatePageAction } else { "NOT_SELECTED" }
            ExistingPageBackup = if ($ExistingPageBackupAction) { $ExistingPageBackupAction } else { "NOT_SELECTED" }
            SkippedPages = [System.Collections.Generic.List[string]]::new()
        }
        Results = [System.Collections.Generic.List[object]]::new()
    }
    if (-not $Execute) {
        foreach ($item in $packages) {
            $receipt.Results.Add([ordered]@{
                PackagePath = $item.Path
                PackageSha256 = (Get-SpoWaveFileSha256 -Path $item.Path)
                PageId = [string]$item.Package.Target.PageId
                Status = "READY"
                Page = [string]$item.Package.Target.PageServerRelativeUrl
            })
        }
    } else {
        if ($ConfirmToken -ne "PUBLISH-SPO-PAGE") {
            throw "-Execute requires -ConfirmToken PUBLISH-SPO-PAGE."
        }
        if ([string]::IsNullOrWhiteSpace($ClientId) -or [string]::IsNullOrWhiteSpace($TenantId)) {
            throw "-Execute requires ClientId and TenantId."
        }
        foreach ($commandName in @(
            "Connect-PnPOnline", "Add-PnPFile", "Add-PnPPage",
            "Add-PnPPageSection", "Add-PnPPageTextPart", "Add-PnPPageImageWebPart",
            "Remove-PnPPage", "Set-PnPPage",
            "Get-PnPFile", "Get-PnPPage", "Get-PnPWeb", "Get-PnPSite",
            "Get-PnPList"
        )) {
            if (-not (Get-Command $commandName -ErrorAction SilentlyContinue)) {
                throw "PnP.PowerShell command is required: $commandName"
            }
        }

        Write-Host "[WAVE] Authenticating to $SiteUrl ..."
        Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Tenant $TenantId -Interactive
        Write-Host "[WAVE] Authentication succeeded. Checking $($packages.Count) target page(s) before publishing ..."
        $receipt.ExistingPageCheck.Status = "COMPLETED"
        foreach ($item in $packages) {
            $page = [string]$item.Package.Target.PageServerRelativeUrl
            $identity = Get-SpoPageIdentity -PageServerRelativeUrl $page
            try {
                $existing = Get-PnPPage -Identity $identity.CreateName -ErrorAction Stop
                if ($existing) {
                    $receipt.ExistingPageCheck.ExistingPages.Add($page)
                    Write-Host "[WAVE] EXISTING: $page"
                }
            } catch {
                if ($_.Exception.Message -notmatch "404|not found|does not exist") {
                    throw "Unable to determine whether the target page exists: $page -- $($_.Exception.Message)"
                }
            }
        }
        $existingCount = $receipt.ExistingPageCheck.ExistingPages.Count
        Write-Host "[WAVE] Existing page check finished: $existingCount found."
        if ($existingCount -gt 0 -and [string]::IsNullOrWhiteSpace($DuplicatePageAction)) {
            if ($NonInteractive) {
                $receipt.ExistingPageCheck.Status = "DUPLICATE_ACTION_REQUIRED"
                if (-not [string]::IsNullOrWhiteSpace($OutputPath)) { Write-SpoWaveReceipt -Receipt $receipt -Path $OutputPath }
                Write-Host "[WAVE] BLOCKED: choose Reject, Approve, or Skip before publication."
                throw "Publication blocked: $existingCount duplicate page(s) found. Review ExistingPageCheck.ExistingPages and rerun with -DuplicatePageAction Reject, Approve, or Skip."
            }
            Write-Host "[WAVE] $existingCount existing page(s) were found at the target site:"
            foreach ($existingPage in @($receipt.ExistingPageCheck.ExistingPages)) {
                Write-Host "  - $existingPage"
            }
            do {
                $answer = Read-Host "Overwrite existing page(s)? Reject (do not publish) / Approve (overwrite) / Skip (publish only new pages) [Reject/Approve/Skip]"
                if ($null -eq $answer) {
                    # A non-terminal shell returns no input; block like -NonInteractive instead of crashing.
                    $receipt.ExistingPageCheck.Status = "DUPLICATE_ACTION_REQUIRED"
                    if (-not [string]::IsNullOrWhiteSpace($OutputPath)) { Write-SpoWaveReceipt -Receipt $receipt -Path $OutputPath }
                    Write-Host "[WAVE] BLOCKED: no interactive input is available; choose Reject, Approve, or Skip."
                    throw "Publication blocked: $existingCount duplicate page(s) found and no interactive input was available. Rerun with -NonInteractive or -DuplicatePageAction Reject, Approve, or Skip."
                }
                $DuplicatePageAction = switch -Regex ($answer.Trim()) {
                    "^(?i)r(eject)?$" { "Reject"; break }
                    "^(?i)a(pprove)?$" { "Approve"; break }
                    "^(?i)s(kip)?$" { "Skip"; break }
                    default { $null }
                }
            } while ([string]::IsNullOrWhiteSpace($DuplicatePageAction))
            Write-Host "[WAVE] Duplicate-page decision: $DuplicatePageAction"
        }
        if ($existingCount -gt 0 -and $DuplicatePageAction -eq "Approve" -and [string]::IsNullOrWhiteSpace($ExistingPageBackupAction)) {
            if ($NonInteractive) {
                $ExistingPageBackupAction = "Backup"
            } else {
                $backupAnswer = Read-Host "Create a full-recovery backup of each existing page before overwrite? [Y/n] (default: Y)"
                $ExistingPageBackupAction = if ([string]$backupAnswer -match "^\s*(?i)n(o)?\s*$") { "NoBackup" } else { "Backup" }
            }
            Write-Host "[WAVE] Existing-page backup decision: $ExistingPageBackupAction"
        }
        if ([string]::IsNullOrWhiteSpace($ExistingPageBackupAction)) {
            $ExistingPageBackupAction = "Backup"
        }
        $receipt.ExistingPageCheck.Action = $DuplicatePageAction
        $receipt.ExistingPageCheck.ExistingPageBackup = $ExistingPageBackupAction
        if ($existingCount -gt 0 -and $DuplicatePageAction -eq "Reject") {
            $receipt.ExistingPageCheck.Status = "REJECTED"
            $receipt.Status = "REJECTED"
            if (-not [string]::IsNullOrWhiteSpace($OutputPath)) { Write-SpoWaveReceipt -Receipt $receipt -Path $OutputPath }
            Write-Host "[WAVE] REJECTED: no pages will be published."
            if (Get-Command Disconnect-PnPOnline -ErrorAction SilentlyContinue) {
                Disconnect-PnPOnline
            }
            return [pscustomobject]$receipt
        }
        $packagesToPublish = @($packages)
        if ($existingCount -gt 0 -and $DuplicatePageAction -eq "Skip") {
            $existingLookup = @{}
            foreach ($existingPage in @($receipt.ExistingPageCheck.ExistingPages)) {
                $existingLookup[$existingPage] = $true
            }
            $packagesToPublish = @(
                foreach ($item in $packages) {
                    $page = [string]$item.Package.Target.PageServerRelativeUrl
                    if ($existingLookup.ContainsKey($page)) {
                        $receipt.ExistingPageCheck.SkippedPages.Add($page)
                        $receipt.Results.Add([ordered]@{
                            PackagePath = $item.Path
                            PackageSha256 = Get-SpoWaveFileSha256 -Path $item.Path
                            PageId = [string]$item.Package.Target.PageId
                            Status = "SKIPPED_EXISTING"
                            Page = $page
                        })
                        $receipt.AttemptedPages.Add($page)
                        $receipt.CheckpointCount++
                        if (-not [string]::IsNullOrWhiteSpace($OutputPath)) { Write-SpoWaveReceipt -Receipt $receipt -Path $OutputPath }
                    } else {
                        $item
                    }
                }
            )
            $receipt.ExistingPageCheck.Status = "SKIPPED_DUPLICATES"
            Write-Host "[WAVE] SKIP: $($receipt.ExistingPageCheck.SkippedPages.Count) duplicate page(s); publishing $($packagesToPublish.Count) non-duplicate page(s)."
        } elseif ($existingCount -gt 0 -and $DuplicatePageAction -eq "Approve") {
            $receipt.ExistingPageCheck.Status = "APPROVED"
            Write-Host "[WAVE] APPROVE: publishing all $($packagesToPublish.Count) page(s), including $existingCount duplicate page(s)."
        } else {
            $receipt.ExistingPageCheck.Status = "NO_DUPLICATES"
        }
        $receipt.Status = "RUNNING"
        if (-not [string]::IsNullOrWhiteSpace($OutputPath)) { Write-SpoWaveReceipt -Receipt $receipt -Path $OutputPath }
        Write-Host "[WAVE] Publishing $($packagesToPublish.Count) page(s)."
        $publishedCount = 0
        $failedCount = 0
        $pageNumber = 0
        try {
            foreach ($item in $packagesToPublish) {
                $pageNumber++
                $page = [string]$item.Package.Target.PageServerRelativeUrl
                Write-Host "[WAVE] Publishing $pageNumber/$($packagesToPublish.Count): $page ..."
                try {
                    $result = Publish-SpoPage `
                        -PackagePath $item.Path `
                        -SiteUrl $SiteUrl `
                        -Execute `
                        -UseExistingConnection `
                        -ConfirmToken $ConfirmToken `
                        -ExistingPageBackupAction $ExistingPageBackupAction
                    $publishedCount++
                    $receipt.AttemptedPages.Add($page)
                    $receipt.Results.Add([ordered]@{
                        PackagePath = $item.Path
                        PackageSha256 = Get-SpoWaveFileSha256 -Path $item.Path
                        PageId = [string]$item.Package.Target.PageId
                        Status = "PUBLISHED"
                        Page = $page
                        Result = $result
                    })
                    $receipt.CheckpointCount++
                    if (-not [string]::IsNullOrWhiteSpace($OutputPath)) { Write-SpoWaveReceipt -Receipt $receipt -Path $OutputPath }
                    Write-Host "[WAVE] PUBLISHED $pageNumber/$($packagesToPublish.Count): $page"
                } catch {
                    $failedCount++
                    $receipt.AttemptedPages.Add($page)
                    $errorMessage = $_.Exception.Message
                    $receipt.Results.Add([ordered]@{
                        PackagePath = $item.Path
                        PackageSha256 = Get-SpoWaveFileSha256 -Path $item.Path
                        PageId = [string]$item.Package.Target.PageId
                        Status = "FAILED"
                        Page = $page
                        Error = $errorMessage
                    })
                    $receipt.CheckpointCount++
                    if (-not [string]::IsNullOrWhiteSpace($OutputPath)) { Write-SpoWaveReceipt -Receipt $receipt -Path $OutputPath }
                    Write-Host "[WAVE] FAILED $pageNumber/$($packagesToPublish.Count): $page -- $errorMessage"
                }
            }
        } finally {
            $receipt.PublishedCount = $publishedCount
            $receipt.FailureCount = $failedCount
            $receipt.Status = if ($failedCount -gt 0 -and $publishedCount -gt 0) {
                "PARTIAL"
            } elseif ($failedCount -gt 0) {
                "FAILED"
            } else {
                "COMPLETE"
            }
            if (-not [string]::IsNullOrWhiteSpace($OutputPath)) { Write-SpoWaveReceipt -Receipt $receipt -Path $OutputPath }
            Write-Host "[WAVE] Publication pass finished: $publishedCount published, $failedCount failed."
            if (Get-Command Disconnect-PnPOnline -ErrorAction SilentlyContinue) {
                Disconnect-PnPOnline
            }
        }
        if ($failedCount -gt 0) {
            throw "Wave publication $($receipt.Status): $failedCount page(s) failed; inspect durable receipt/checkpoints at '$OutputPath'."
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($OutputPath)) {
        Write-SpoWaveReceipt -Receipt $receipt -Path $OutputPath
    }
    return [pscustomobject]$receipt
}

if ($waveInvocationName -ne ".") {
    $spoConfig = Read-SpoConfiguration -Path $batchConfigPath -Require @("SiteUrl", "ClientId", "TenantId", "Environment")
    $waveParameters = @{
        PackagePath      = $batchPackagePath
        PackageDirectory = $batchPackageDirectory
        WaveManifestPath = $batchWaveManifestPath
        WaveId           = $WaveId
        SiteUrl          = $spoConfig.SiteUrl
        TargetEnvironment = $spoConfig.Environment
        ClientId         = $spoConfig.ClientId
        TenantId         = $spoConfig.TenantId
        OutputPath       = $batchOutputPath
        Execute          = $batchExecute
        ConfirmToken     = $batchConfirmToken
        NonInteractive   = $batchNonInteractive
    }
    if (-not [string]::IsNullOrWhiteSpace($batchDuplicatePageAction)) {
        $waveParameters.DuplicatePageAction = $batchDuplicatePageAction
    }
    if (-not [string]::IsNullOrWhiteSpace($batchExistingPageBackupAction)) {
        $waveParameters.ExistingPageBackupAction = $batchExistingPageBackupAction
    }
    Publish-SpoWave @waveParameters
}
