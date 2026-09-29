<#
.SYNOPSIS
    Quick diagnostic to verify REST connectivity and find the correct server-relative URL for a page.
    Run this before convert-wiki-page.ps1 to confirm the path is correct.

.EXAMPLE
    .\diagnose-page.ps1 -SourceSiteUrl "https://csb.test.jag.gov.bc.ca/CourtAdmin" -PageName "Court-Admin-Training-Homepage.aspx" -UseDefaultCredentials
#>
param(
    [Parameter(Mandatory = $true)] [string]$SourceSiteUrl,
    [Parameter(Mandatory = $true)] [string]$PageName,
    [Parameter(Mandatory = $false)] [switch]$UseDefaultCredentials
)

$spHeaders = @{ "Accept" = "application/json;odata=verbose" }

function Call-Rest {
    param([string]$Url)
    Write-Host "`nGET: $Url" -ForegroundColor DarkGray
    try {
        if ($UseDefaultCredentials) {
            $r = Invoke-RestMethod -Uri $Url -Headers $spHeaders -UseDefaultCredentials -ErrorAction Stop
        } else {
            $cred = Get-Credential
            $r = Invoke-RestMethod -Uri $Url -Headers $spHeaders -Credential $cred -ErrorAction Stop
        }
        return $r
    } catch {
        Write-Host "HTTP ERROR: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            try {
                $s = $_.Exception.Response.GetResponseStream()
                $reader = [System.IO.StreamReader]::new($s)
                Write-Host "Response body: $($reader.ReadToEnd())" -ForegroundColor Yellow
            } catch {}
        }
        return $null
    }
}

Write-Host "=== Step 1: Get Web ServerRelativeUrl ===" -ForegroundColor Cyan
$web = Call-Rest "$SourceSiteUrl/_api/web?`$select=ServerRelativeUrl,Url"
if ($web) {
    Write-Host "  ServerRelativeUrl = $($web.d.ServerRelativeUrl)" -ForegroundColor Green
    Write-Host "  Url               = $($web.d.Url)" -ForegroundColor Green
    $webRelUrl = $web.d.ServerRelativeUrl
} else {
    Write-Host "FAILED - cannot continue" -ForegroundColor Red; exit 1
}

Write-Host "`n=== Step 2: List all Pages libraries on this web ===" -ForegroundColor Cyan
$lists = Call-Rest "$SourceSiteUrl/_api/web/lists?`$select=Title,BaseTemplate,RootFolder/ServerRelativeUrl&`$expand=RootFolder&`$filter=Hidden eq false"
if ($lists -and $lists.d.results) {
    foreach ($l in $lists.d.results) {
        Write-Host "  Library: '$($l.Title)'  BaseTemplate=$($l.BaseTemplate)  Path=$($l.RootFolder.ServerRelativeUrl)"
    }
}

Write-Host "`n=== Step 3: Probe direct file URL ===" -ForegroundColor Cyan
$encodedPage = [Uri]::EscapeDataString($PageName).Replace("'","''")
$pageRelUrl = ("$webRelUrl/Pages/$PageName").Replace("//","/")
Write-Host "  Trying: $pageRelUrl" -ForegroundColor DarkGray
$fileInfo = Call-Rest "$SourceSiteUrl/_api/web/GetFileByServerRelativeUrl('$([Uri]::EscapeDataString($pageRelUrl))')?`$select=Name,ServerRelativeUrl,Exists"
if ($fileInfo -and $fileInfo.d) {
    Write-Host "  EXISTS: $($fileInfo.d.ServerRelativeUrl)  Exists=$($fileInfo.d.Exists)" -ForegroundColor Green
} else {
    Write-Host "  File not found at $pageRelUrl" -ForegroundColor Red
}

Write-Host "`n=== Step 4: List first 10 items in Pages library ===" -ForegroundColor Cyan
$encodedLib = [Uri]::EscapeDataString("Pages").Replace("'","''")
$items = Call-Rest "$SourceSiteUrl/_api/web/lists/getbytitle('$encodedLib')/items?`$select=Id,Title,FileLeafRef,FileRef&`$top=10"
if ($items -and $items.d.results) {
    foreach ($i in $items.d.results) {
        Write-Host "  [$($i.Id)] $($i.FileLeafRef) -> $($i.FileRef)"
    }
} else {
    Write-Host "  Could not list items in 'Pages' library" -ForegroundColor Red
}
