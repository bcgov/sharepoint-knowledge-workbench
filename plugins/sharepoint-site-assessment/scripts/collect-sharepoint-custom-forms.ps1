<#
.SYNOPSIS
Discovers and downloads non-standard (customized) list-form .aspx files from
a legacy on-premises SharePoint 2016 site, via REST + Windows-credential
auth.

.DESCRIPTION
On-prem SharePoint (unlike modern SPO) has no Entra app-registration path in
general use here, so this script authenticates via NTLM/Kerberos --
Invoke-RestMethod/Invoke-WebRequest with -UseDefaultCredentials or an
explicit -Credential -- not Connect-PnPOnline. This is a deliberate
divergence from this repo's standard PnP.PowerShell auth convention,
required because the target is on-prem SP2016.

For every list/library across the site (and every sub-web), checks whether
its NewForm.aspx / EditForm.aspx / DispForm.aspx are the out-of-box files or
have been customized (a list is treated as customized if any non-standard
.aspx file sits alongside the standard forms in its root folder -- e.g.
NewForm_Original.aspx, ForPrinting.aspx -- the same signal the standard
forms being replaced/renamed leaves behind). Every non-standard form found
is downloaded locally and classified:
  - InfoPath: contains an InfoPath/XsnLocation marker, no inline <script>
  - Custom (script): contains an inline <script> block
  - Custom (layout-only): customized but no script and no InfoPath marker

Writes forms.json in the exact JSON-array shape consumed by this plugin's
forms_analysis.py (analyze-custom-forms skill):
  [{ listName, isCustomized, hasScript, formType }]
one entry per list (not per file) -- out-of-box lists are included with
isCustomized=false so the consumer can compute out-of-box vs. custom ratios.

.PARAMETER SiteUrl
The on-prem SP2016 site to inspect. Required (no hardcoded default).

.PARAMETER OutputDir
Directory to write forms.json and downloaded .aspx files to. Defaults to
.\sharepoint-custom-forms-export relative to the current working directory.

.PARAMETER UseDefaultCredentials
Use the current Windows session (Kerberos/NTLM pass-through). Requires VPN /
domain-joined. Without this switch, a credential prompt is shown.

.EXAMPLE
.\collect-sharepoint-custom-forms.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -UseDefaultCredentials

.EXAMPLE
.\collect-sharepoint-custom-forms.ps1 -SiteUrl "https://sp2016.example.org/sites/Legacy" -OutputDir .\forms-export -Credential (Get-Credential)
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$SiteUrl,

    [string]$OutputDir = ".\sharepoint-custom-forms-export",

    [switch]$UseDefaultCredentials,

    [System.Management.Automation.PSCredential]$Credential
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not [System.IO.Path]::IsPathRooted($OutputDir)) {
    $OutputDir = Join-Path (Get-Location) $OutputDir
}
if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null }

if (-not $UseDefaultCredentials -and -not $Credential) {
    $Credential = Get-Credential -Message "Credentials for $SiteUrl"
    if (-not $Credential) { throw "No credentials provided." }
}

Write-Host "Site   : $SiteUrl" -ForegroundColor White
Write-Host "Output : $OutputDir" -ForegroundColor White

function Invoke-SP {
    param([string]$Url)
    $headers = @{ Accept = 'application/json;odata=verbose' }
    try {
        if ($UseDefaultCredentials) {
            return Invoke-RestMethod -Uri $Url -Headers $headers -UseDefaultCredentials -ErrorAction Stop
        }
        return Invoke-RestMethod -Uri $Url -Headers $headers -Credential $Credential -ErrorAction Stop
    } catch {
        Write-Verbose "REST error on $Url : $($_.Exception.Message)"
        return $null
    }
}

function Get-All {
    param([string]$Url)
    $all = [System.Collections.Generic.List[object]]::new()
    $nextUrl = $Url
    while ($nextUrl) {
        $r = Invoke-SP -Url $nextUrl
        if (-not $r) { break }
        if ($r.d.results) { $r.d.results | ForEach-Object { $all.Add($_) } }
        $nextProp = $r.d.PSObject.Properties['__next']
        $nextUrl = if ($nextProp) { $nextProp.Value } else { $null }
    }
    return $all
}

function Get-SPSubWebs {
    param([string]$WebUrl)
    $subwebs = @()
    $res = Get-All -Url "$WebUrl/_api/web/webs?`$select=Title,Url,ServerRelativeUrl"
    foreach ($w in $res) {
        $subwebs += $w
        $subwebs += Get-SPSubWebs -WebUrl $w.Url
    }
    return $subwebs
}

$standardFormNames = @("NewForm.aspx", "EditForm.aspx", "DispForm.aspx", "AllItems.aspx", "view.aspx", "Upload.aspx")

Write-Host "`nDiscovering webs..." -ForegroundColor Cyan
$webInfo = Invoke-SP -Url "$SiteUrl/_api/web?`$select=ServerRelativeUrl,Title,Url"
if (-not $webInfo) { throw "Could not connect to $SiteUrl" }
$allWebs = @($webInfo.d)
$allWebs += Get-SPSubWebs -WebUrl $SiteUrl
Write-Host "  Discovered $($allWebs.Count) web(s)." -ForegroundColor Green

$formsInventory = [System.Collections.Generic.List[object]]::new()
$downloadedCount = 0

foreach ($w in $allWebs) {
    $lists = Get-All -Url "$($w.Url)/_api/web/Lists?`$select=Title,RootFolder/ServerRelativeUrl&`$expand=RootFolder&`$filter=Hidden eq false"
    foreach ($list in $lists) {
        $rootUrl = $list.RootFolder.ServerRelativeUrl
        $formsFolderUrl = "$rootUrl/Forms"
        $encodedFormsFolder = [Uri]::EscapeDataString($formsFolderUrl)
        $files = Get-All -Url "$($w.Url)/_api/web/GetFolderByServerRelativeUrl('$encodedFormsFolder')/Files?`$select=Name,ServerRelativeUrl"

        $customFiles = @($files | Where-Object { $_.Name -match '\.aspx$' -and $_.Name -notin $standardFormNames })

        if ($customFiles.Count -eq 0) {
            $formsInventory.Add([PSCustomObject]@{
                listName     = $list.Title
                isCustomized = $false
                hasScript    = $false
                formType     = "Standard"
            })
            continue
        }

        $listHasScript = $false
        $listFormType = "Custom"
        foreach ($f in $customFiles) {
            $localFile = Join-Path $OutputDir ("{0}_{1}" -f ($list.Title -replace '[\\/:*?"<>|]', '_'), $f.Name)
            $encodedFileUrl = [Uri]::EscapeDataString($f.ServerRelativeUrl)
            $fileUrl = "$($w.Url)/_api/web/GetFileByServerRelativeUrl('$encodedFileUrl')/`$value"
            $fileText = $null
            try {
                if ($UseDefaultCredentials) {
                    Invoke-WebRequest -Uri $fileUrl -UseDefaultCredentials -OutFile $localFile -ErrorAction Stop | Out-Null
                } else {
                    Invoke-WebRequest -Uri $fileUrl -Credential $Credential -OutFile $localFile -ErrorAction Stop | Out-Null
                }
                $downloadedCount++
                $fileText = Get-Content -LiteralPath $localFile -Raw -ErrorAction SilentlyContinue
                Write-Host "  [OK] $($list.Title) -> $($f.Name)" -ForegroundColor DarkGray
            } catch {
                Write-Warning "  Failed to download $($f.ServerRelativeUrl): $($_.Exception.Message)"
            }

            if ($fileText) {
                if ($fileText -match '<script\b') { $listHasScript = $true }
                if ($fileText -match 'XsnLocation|InfoPathSolution|urn:schemas-microsoft-com:office:infopath') {
                    $listFormType = "InfoPath"
                }
            }
        }

        $formsInventory.Add([PSCustomObject]@{
            listName     = $list.Title
            isCustomized = $true
            hasScript    = $listHasScript
            formType     = $listFormType
        })
    }
}

# forms.json -- consumed directly by forms_analysis.py (analyze-custom-forms)
$jsonPath = Join-Path $OutputDir "forms.json"
$formsInventory | ConvertTo-Json -Depth 5 | Set-Content -Path $jsonPath -Encoding UTF8

$customCount = @($formsInventory | Where-Object { $_.isCustomized }).Count

Write-Host "`nComplete." -ForegroundColor Green
Write-Host "  Lists inspected   : $($formsInventory.Count)" -ForegroundColor Green
Write-Host "  Customized lists  : $customCount" -ForegroundColor Green
Write-Host "  Files downloaded  : $downloadedCount" -ForegroundColor Green
Write-Host "  forms.json        : $jsonPath (feeds analyze-custom-forms)" -ForegroundColor Green
