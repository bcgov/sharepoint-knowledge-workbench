<#
.SYNOPSIS
    Task 9: Retrieve actual metadata field values from a Phase 3 pilot topic

.DESCRIPTION
    Read-only inspection of actual SharePoint field values for selected topic.
    Tests these fields:
    - TopicID
    - PublicationOrder
    - TopicContentSHA256
    - Status
    - ReviewDate
    - TransitionAction
    - TransitionTarget

.EXAMPLE
    .\task-9-retrieve-topic-metadata.ps1
#>

[CmdletBinding()]
param(
    [string]$ConfigFile = "tools/phase-4-native-sharepoint-skills/config.psd1"
)

$ErrorActionPreference = "Stop"

Write-Host "=== TASK 9: RETRIEVE ACTUAL METADATA FOR SELECTED TOPIC ===" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $ConfigFile)) {
    Write-Error "Config file $ConfigFile not found."
    exit 1
}

$config = Import-PowerShellDataFile $ConfigFile
Import-Module PnP.PowerShell -ErrorAction Stop

Write-Host "Connecting to tenant..." -ForegroundColor Cyan
$hasValidAppReg = ($config.ClientId -and $config.TenantId -and `
    $config.ClientId -notlike "*test*" -and $config.ClientId -notlike "*example*" -and `
    $config.TenantId -notlike "*test*" -and $config.TenantId -notlike "*example*")

if ($hasValidAppReg) {
    Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId -Interactive -ErrorAction Stop
} else {
    $phase3ConfigPath = "../../tools/phase-3-sharepoint-discovery/config.psd1"
    if (Test-Path $phase3ConfigPath) {
        Write-Host "Using Phase 3 credentials..." -ForegroundColor Yellow
        $phase3Config = Import-PowerShellDataFile $phase3ConfigPath
        Connect-PnPOnline -Url $config.SiteUrl -ClientId $phase3Config.ClientId -Tenant $phase3Config.TenantId -Interactive -ErrorAction Stop
    } else {
        Write-Error "No valid authentication available."
        exit 1
    }
}

Write-Host "✓ Connected to: $($config.SiteUrl)" -ForegroundColor Green
Write-Host ""

# Load Phase 4 configuration (already has verified Phase 3 library names)
$phase4Config = Import-PowerShellDataFile $ConfigFile
$pageLibraryName = $phase4Config.PilotKnowledgeLibrary

# Find the CEISPilotKnowledgePages library (Phase 3 output)
Write-Host "Locating Page Library '$pageLibraryName'..." -ForegroundColor Cyan
try {
    $ceisList = Get-PnPList -Identity $pageLibraryName -ErrorAction SilentlyContinue

    if (-not $ceisList) {
        Write-Error "Phase 3 Page Library '$pageLibraryName' not found. Verify Phase 3 pilot was run on this site."
        exit 1
    }

    Write-Host "✓ Library found: $($ceisList.Title)" -ForegroundColor Green
    Write-Host "  ID: $($ceisList.Id)" -ForegroundColor Gray
    Write-Host ""

    # Get first 5 items to select from
    Write-Host "Retrieving items to select from..." -ForegroundColor Cyan
    $items = Get-PnPListItem -List $ceisList -PageSize 5

    Write-Host "Found $($items.Count) items:" -ForegroundColor Green
    $items | ForEach-Object {
        Write-Host "  - $($_.FieldValues.Title)" -ForegroundColor Gray
    }

    Write-Host ""
    Write-Host "Selecting first item for metadata visibility testing..." -ForegroundColor Yellow
    $selectedItem = $items[0]

    if (-not $selectedItem) {
        Write-Error "No items available for testing"
        exit 1
    }

    Write-Host "✓ Selected: $($selectedItem.FieldValues.Title)" -ForegroundColor Green
    Write-Host ""

    # Retrieve all fields and their values
    Write-Host "=== ACTUAL SHAREPOINT FIELD VALUES ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Item Title: $($selectedItem.FieldValues.Title)" -ForegroundColor White
    Write-Host "Item ID: $($selectedItem.Id)" -ForegroundColor Gray
    Write-Host ""

    # Check each metadata field
    $fieldsToTest = @("TopicID", "PublicationOrder", "TopicContentSHA256", "Status", "ReviewDate", "TransitionAction", "TransitionTarget")

    foreach ($fieldName in $fieldsToTest) {
        $fieldValue = $selectedItem.FieldValues[$fieldName]

        if ($null -eq $fieldValue) {
            Write-Host "$fieldName : [NULL / NOT PRESENT]" -ForegroundColor Yellow
        } elseif ([string]::IsNullOrWhiteSpace($fieldValue)) {
            Write-Host "$fieldName : [EMPTY]" -ForegroundColor Yellow
        } else {
            Write-Host "$fieldName : $fieldValue" -ForegroundColor Green
        }
    }

    Write-Host ""
    Write-Host "=== SUMMARY ===" -ForegroundColor Cyan
    Write-Host "Topic: $($selectedItem.FieldValues.Title)" -ForegroundColor White
    Write-Host "Ready for metadata visibility testing via agent/skill" -ForegroundColor Green

} catch {
    Write-Error "Error during retrieval: $_"
    exit 1
}

Disconnect-PnPOnline
