param([string]$Script, [string]$InventoryCsv, [string]$ConfigPath, [string]$OutputDir, [string]$Platform)
$ErrorActionPreference = 'Stop'
function Invoke-WebRequest {
    [CmdletBinding()] param($Uri, $OutFile, [switch]$UseBasicParsing, $Credential)
    if (-not $Credential) { throw 'Interactive/explicit credentials are required' }
    if ($Uri -notmatch '/_api/web/GetFileByServerRelativeUrl.+/\$value$') { throw 'Stored file bytes must use REST value endpoint' }
    'mock page' | Set-Content -LiteralPath $OutFile
}
function Connect-PnPOnline { [CmdletBinding()] param($Url, $ClientId, $Tenant, [switch]$Interactive) }
function Disconnect-PnPOnline { [CmdletBinding()] param() }
function Get-PnPFile {
    [CmdletBinding()] param($Url, $Path, $FileName, [switch]$AsFile, [switch]$Force)
    if ($Url -notlike '/*') { throw 'PnP needs server-relative file URL' }
    'mock page' | Set-Content -LiteralPath (Join-Path $Path $FileName)
}
$credential = [pscredential]::new('mock', (ConvertTo-SecureString 'mock' -AsPlainText -Force))
& $Script -InventoryCsv $InventoryCsv -ConfigPath $ConfigPath -OutputDir $OutputDir -Platform $Platform -Credential $credential -Execute -ConfirmToken DOWNLOAD-SHAREPOINT-INVENTORY-FILES
