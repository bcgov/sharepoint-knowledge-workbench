#!/usr/bin/env pwsh
$ConfigFile = "tools/phase-4-native-sharepoint-skills/config.psd1"
$config = Import-PowerShellDataFile -Path $ConfigFile

Connect-PnPOnline -Url $config.SiteUrl -ClientId $config.ClientId -Tenant $config.TenantId

$items = Get-PnPListItem -List "AgentAssets" -PageSize 1000

$targetFile = $items | Where-Object {
    $_.FieldValues.FileLeafRef -eq "SKILL.md" -and
    $_.FieldValues.FileRef -like "*review-manual-topics*"
}

if ($targetFile) {
    Write-Host "Found: $($targetFile.FieldValues.FileRef)" -ForegroundColor Yellow
    Remove-PnPListItem -List "AgentAssets" -Identity $targetFile.Id -Force
    Write-Host "SUCCESS: File deleted" -ForegroundColor Green
} else {
    Write-Error "File not found"
    exit 1
}

Disconnect-PnPOnline
