<# Exercises the canonical connection reader as a strict-mode consumer. #>
param([string]$Helper, [string]$ConfigPath)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
. $Helper
Get-WorkbenchConnectionConfig -Path $ConfigPath | ConvertTo-Json -Depth 5
