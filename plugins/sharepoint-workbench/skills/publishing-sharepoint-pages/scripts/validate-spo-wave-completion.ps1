<#
.SYNOPSIS
Validates a wave after every expected page is successfully published.

.DESCRIPTION
Compares the complete wave scope with the successful PnP publication receipt.
When duplicate handling is `Skip`, existing pages listed in the receipt are
accepted as already present, while only newly published pages remain eligible
for an optional Edit -> Publish cycle.

.KEY INPUT DEPENDENCIES
- Wave manifest produced by new-spo-wave-manifest.ps1
- PnP publication receipt

.OUTPUTS
- JSON completion report; exits non-zero when the wave is incomplete

.FUNCTION INDEX
Resolve-SpoWavePackagePath, Get-SpoWaveFileSha256, Test-SpoWaveCompletion.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$WaveManifestPath,
    [Parameter(Mandatory = $true)][string]$PublicationReceiptPath,
    [Parameter(Mandatory = $true)][string]$OutputPath,
    [Alias("ExpectedPackageDirectory")]
    [string]$PackageDirectory,
    [switch]$NoFail
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-SpoWavePackagePath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$PackagePath,
        [Parameter(Mandatory = $true)][string]$ReceiptDirectory,
        [string]$PackageDirectory
    )

    if ([System.IO.Path]::IsPathRooted($PackagePath)) { return $PackagePath }
    $baseDirectory = if ([string]::IsNullOrWhiteSpace($PackageDirectory)) {
        $ReceiptDirectory
    } else {
        $PackageDirectory
    }
    return Join-Path $baseDirectory $PackagePath
}

function Get-SpoWaveFileSha256 {
    <# Returns a lowercase SHA-256 digest for a file's exact bytes. #>
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$Path)

    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Test-SpoWaveCompletion {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$WaveManifestPath,
        [Parameter(Mandatory = $true)][string]$PublicationReceiptPath
    )

    foreach ($path in @($WaveManifestPath, $PublicationReceiptPath)) {
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "Wave completion input was not found: $path"
        }
    }
    $wave = Get-Content -LiteralPath $WaveManifestPath -Raw | ConvertFrom-Json
    $publication = Get-Content -LiteralPath $PublicationReceiptPath -Raw | ConvertFrom-Json
    $missingReceiptFields = @(
        foreach ($field in @("RunId", "Status", "TargetEnvironment", "SiteUrl",
                "WaveId", "WaveManifestSha256", "PackageEvidence", "PackageCount",
                "ExpectedPageCount", "DryRun", "Results")) {
            $property = $publication.PSObject.Properties[$field]
            if (-not $property -or $null -eq $property.Value) { $field }
        }
    )
    $missingManifestFields = @(
        foreach ($field in @("WaveId", "Wave", "TargetEnvironment", "TargetSiteUrl", "PageCount", "Pages")) {
            $property = $wave.PSObject.Properties[$field]
            if (-not $property -or $null -eq $property.Value) { $field }
        }
    )
    if ($missingReceiptFields.Count -gt 0 -or $missingManifestFields.Count -gt 0) {
        return [pscustomobject][ordered]@{
            Complete = $false
            WaveId = if ($wave.PSObject.Properties["WaveId"]) { [string]$wave.WaveId } else { "" }
            AcceptanceGate = "PUBLISHED"
            MissingBindingFields = $missingReceiptFields
            MissingManifestFields = $missingManifestFields
        }
    }
    $manifestHash = Get-SpoWaveFileSha256 -Path $WaveManifestPath
    $manifestMatches = $manifestHash -eq [string]$publication.WaveManifestSha256
    $identityMatches = [string]$publication.WaveId -eq [string]$wave.WaveId -and
        [string]$publication.TargetEnvironment -eq [string]$wave.TargetEnvironment -and
        [string]$publication.SiteUrl.TrimEnd("/") -eq [string]$wave.TargetSiteUrl.TrimEnd("/")
    $identityMatches = $identityMatches -and
        [int]$publication.ExpectedPageCount -eq [int]$wave.PageCount -and
        [int]$publication.PackageCount -eq @($publication.PackageEvidence).Count
    $expectedById = @{}
    foreach ($page in @($wave.Pages)) { $expectedById[[string]$page.PageId] = $page }
    $packageDrift = [System.Collections.Generic.List[string]]::new()
    $packageById = @{}
    $packageMetadataById = @{}
    foreach ($evidence in @($publication.PackageEvidence)) {
        $packagePath = Resolve-SpoWavePackagePath -PackagePath ([string]$evidence.PackagePath) `
            -ReceiptDirectory (Split-Path -Parent $PublicationReceiptPath) -PackageDirectory $PackageDirectory
        if (-not (Test-Path -LiteralPath $packagePath -PathType Leaf)) {
            $packageDrift.Add("MissingPackage:$($evidence.PageId)")
            continue
        }
        if ((Get-SpoWaveFileSha256 -Path $packagePath) -ne [string]$evidence.PackageSha256) {
            $packageDrift.Add("PackageHashMismatch:$($evidence.PageId)")
            continue
        }
        $package = Get-Content -LiteralPath $packagePath -Raw | ConvertFrom-Json
        $pageId = [string]$evidence.PageId
        if (-not $expectedById.ContainsKey($pageId) -or $packageById.ContainsKey($pageId)) {
            $packageDrift.Add("UnexpectedOrDuplicatePackage:$pageId")
            continue
        }
        $expectedPage = $expectedById[$pageId]
        if ([string]$package.Target.PageId -ne $pageId -or
            [string]$package.Target.PageServerRelativeUrl -ne [string]$expectedPage.TargetPageServerRelativeUrl -or
            [string]$package.Target.WaveId -ne [string]$wave.WaveId -or
            [string]$package.Target.Environment -ne [string]$wave.TargetEnvironment -or
            [string]$package.Target.TargetSiteUrl.TrimEnd("/") -ne [string]$wave.TargetSiteUrl.TrimEnd("/") -or
            [string]$package.Source.SiteName -ne [string]$expectedPage.SiteName -or
            [string]$package.Source.ServerRelativeUrl -ne [string]$expectedPage.ServerRelativeUrl -or
            [string]$evidence.Page -ne [string]$expectedPage.TargetPageServerRelativeUrl -or
            [string]$evidence.Environment -ne [string]$wave.TargetEnvironment -or
            [string]$evidence.WaveId -ne [string]$wave.WaveId) {
            $packageDrift.Add("PackageManifestMismatch:$pageId")
            continue
        }
        $packageById[$pageId] = $packagePath
        $packageMetadataById[$pageId] = $evidence
    }
    $missingPackageIds = @($expectedById.Keys | Where-Object { -not $packageById.ContainsKey($_) })
    $unexpectedPackageIds = @($packageById.Keys | Where-Object { -not $expectedById.ContainsKey($_) })

    $resultById = @{}
    $duplicateResults = [System.Collections.Generic.List[string]]::new()
    $outcomeDrift = [System.Collections.Generic.List[string]]::new()
    foreach ($result in @($publication.Results)) {
        $pageId = [string]$result.PageId
        if (-not $expectedById.ContainsKey($pageId) -or $resultById.ContainsKey($pageId)) {
            $duplicateResults.Add($pageId)
            continue
        }
        if (-not $packageMetadataById.ContainsKey($pageId) -or
            [string]$result.Page -ne [string]$expectedById[$pageId].TargetPageServerRelativeUrl -or
            [string]$result.PackageSha256 -ne [string]$packageMetadataById[$pageId].PackageSha256) {
            $outcomeDrift.Add($pageId)
        } else {
            $resultPackagePath = Resolve-SpoWavePackagePath -PackagePath ([string]$result.PackagePath) `
                -ReceiptDirectory (Split-Path -Parent $PublicationReceiptPath) -PackageDirectory $PackageDirectory
            if ([System.IO.Path]::GetFullPath($resultPackagePath) -ne
                [System.IO.Path]::GetFullPath($packageById[$pageId])) {
                $outcomeDrift.Add($pageId)
            }
        }
        $resultById[$pageId] = $result
    }
    $missingOutcomes = @($expectedById.Keys | Where-Object { -not $resultById.ContainsKey($_) })
    $failedOutcomes = @($resultById.Values | Where-Object { [string]$_.Status -notin @("PUBLISHED", "SKIPPED_EXISTING") })
    $skippedExisting = @($resultById.Values | Where-Object { [string]$_.Status -eq "SKIPPED_EXISTING" } | ForEach-Object Page)
    $published = @($resultById.Values | Where-Object { [string]$_.Status -eq "PUBLISHED" } | ForEach-Object Page)
    $existingAction = if ($publication.PSObject.Properties["ExistingPageCheck"]) {
        [string]$publication.ExistingPageCheck.Action
    } else { "" }
    $skipActionValid = $skippedExisting.Count -eq 0 -or $existingAction -eq "Skip"
    $expectedPaths = @($wave.Pages | ForEach-Object TargetPageServerRelativeUrl)
    $missingPublication = @($expectedPaths | Where-Object { $_ -notin @($published + $skippedExisting) })
    $unexpectedPublication = @(@($published + $skippedExisting) | Where-Object { $_ -notin $expectedPaths })
    $complete = $expectedPaths.Count -gt 0 -and $manifestMatches -and $identityMatches -and
        [string]$publication.Status -eq "COMPLETE" -and -not [bool]$publication.DryRun -and
        $packageDrift.Count -eq 0 -and $missingPackageIds.Count -eq 0 -and $unexpectedPackageIds.Count -eq 0 -and
        $missingOutcomes.Count -eq 0 -and $duplicateResults.Count -eq 0 -and $failedOutcomes.Count -eq 0 -and
        $outcomeDrift.Count -eq 0 -and $skipActionValid -and
        $missingPublication.Count -eq 0 -and $unexpectedPublication.Count -eq 0

    return [pscustomobject][ordered]@{
        Complete = $complete
        WaveId = [string]$wave.WaveId
        Wave = [string]$wave.Wave
        RunId = [string]$publication.RunId
        AcceptanceGate = "PUBLISHED"
        Expected = $expectedPaths.Count
        Published = @($published | Select-Object -Unique).Count
        SkippedExisting = @($skippedExisting | Select-Object -Unique)
        Accepted = @($published + $skippedExisting | Select-Object -Unique).Count
        ManifestMatchesReceipt = $manifestMatches
        IdentityMatches = $identityMatches
        PackageDrift = $packageDrift.ToArray()
        MissingPackages = $missingPackageIds
        UnexpectedPackages = $unexpectedPackageIds
        MissingOutcomes = $missingOutcomes
        DuplicateOutcomes = $duplicateResults.ToArray()
        OutcomeDrift = $outcomeDrift.ToArray()
        FailedOutcomes = @($failedOutcomes | ForEach-Object { [string]$_.Page })
        MissingPublication = $missingPublication
        UnexpectedPublication = $unexpectedPublication
    }
}

$report = Test-SpoWaveCompletion `
    -WaveManifestPath $WaveManifestPath `
    -PublicationReceiptPath $PublicationReceiptPath
$parent = Split-Path -Parent $OutputPath
if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
}
$report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
$report
if (-not $report.Complete -and -not $NoFail) {
    exit 1
}
