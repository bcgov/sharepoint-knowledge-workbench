<#
.SYNOPSIS
    Idempotently provisions sample lists, lookup relationships, Picture columns,
    and a modern test page with HeaderType None for validating Master-Detail SPFx web parts.

.DESCRIPTION
    Creates or updates:
    - Primary List (e.g. Books or Persons)
    - Lookup List (e.g. Authors or PersonDetails) with Picture URL field
    - Child Event Lists (e.g. Appearances, Narratives) with lookup references
    - Sample records with image links
    - Modern test page with HeaderType None

.PARAMETER SiteUrl
    The target site collection URL (e.g. https://<tenant>.sharepoint.com/sites/<SiteName>).

.PARAMETER ClientId
    Optional Azure AD App Registration Client ID for interactive authentication.

.PARAMETER PageName
    Name of the modern test page to create or update (default: master-detail-dossier-poc).

.EXAMPLE
    pwsh -File ./provision-sample-dossier-schema.ps1 -SiteUrl "https://bcgovernmenttrial400.sharepoint.com/sites/AppRegistrationTests"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$SiteUrl,

    [Parameter(Mandatory = $false)]
    [string]$ClientId,

    [Parameter(Mandatory = $false)]
    [string]$TenantId,

    [Parameter(Mandatory = $false)]
    [string]$TenantAdminUrl,

    [Parameter(Mandatory = $false)]
    [string]$ConfigPath = (Join-Path $PSScriptRoot "..\..\..\config.psd1"),

    [Parameter(Mandatory = $false)]
    [string]$PageName = "master-detail-dossier-poc"
)

$ErrorActionPreference = "Stop"

$connectionHelper = Join-Path $PSScriptRoot "Get-WorkbenchConnectionConfig.ps1"
if (Test-Path $connectionHelper) {
    . $connectionHelper
    $connectionConfig = Get-WorkbenchConnectionConfig -Path $ConfigPath
    if (-not $SiteUrl) { $SiteUrl = $connectionConfig.SiteUrl }
    if (-not $ClientId) { $ClientId = $connectionConfig.ClientId }
    if (-not $TenantId) { $TenantId = $connectionConfig.TenantId }
    if (-not $TenantAdminUrl) { $TenantAdminUrl = $connectionConfig.TenantAdminUrl }
}

if (-not $SiteUrl) {
    throw "SiteUrl is required. Provide -SiteUrl or a valid -ConfigPath."
}

$AuthorsListName = "Authors"
$BooksListName   = "Books"
$ApprListName    = "Author_Appearances"
$NarrListName    = "Author_Narratives"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Provisioning Sample Dossier Schema: $SiteUrl" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

try {
    Write-Host "Connecting to SharePoint Online..." -ForegroundColor Cyan
    $connectParams = @{ Url = $SiteUrl; Interactive = $true }
    if ($ClientId) { $connectParams["ClientId"] = $ClientId }
    if ($TenantId) { $connectParams["Tenant"] = $TenantId }
    if ($TenantAdminUrl) { $connectParams["TenantAdminUrl"] = $TenantAdminUrl }
    Connect-PnPOnline @connectParams

    # 1. Ensure Authors list + Picture column
    Write-Host "Ensuring '$AuthorsListName' list and Picture column exist..." -ForegroundColor Cyan
    $authorsList = Get-PnPList -Identity $AuthorsListName -ErrorAction SilentlyContinue
    if (-not $authorsList) {
        New-PnPList -Title $AuthorsListName -Template GenericList -ErrorAction Stop | Out-Null
        $authorsList = Get-PnPList -Identity $AuthorsListName -ErrorAction Stop
    }
    $pictureField = Get-PnPField -List $AuthorsListName -Identity "Picture" -ErrorAction SilentlyContinue
    if (-not $pictureField) {
        Add-PnPField -List $AuthorsListName -Type URL -DisplayName "Picture" -InternalName "Picture" -ErrorAction Stop | Out-Null
    }

    # 2. Ensure Books list + BookAuthor lookup field
    Write-Host "Ensuring '$BooksListName' list and BookAuthor lookup exist..." -ForegroundColor Cyan
    $booksList = Get-PnPList -Identity $BooksListName -ErrorAction SilentlyContinue
    if (-not $booksList) {
        New-PnPList -Title $BooksListName -Template GenericList -ErrorAction Stop | Out-Null
        $booksList = Get-PnPList -Identity $BooksListName -ErrorAction Stop
    }
    $authorLookupField = Get-PnPField -List $BooksListName -Identity "BookAuthor" -ErrorAction SilentlyContinue
    if (-not $authorLookupField) {
        Add-PnPField -List $BooksListName -Type Lookup -DisplayName "BookAuthor" -InternalName "BookAuthor" `
            -LookupList $authorsList.Id.ToString() -LookupField "Title" -ErrorAction Stop | Out-Null
    }

    # 3. Ensure Author_Appearances list
    Write-Host "Ensuring '$ApprListName' list exists..." -ForegroundColor Cyan
    $apprList = Get-PnPList -Identity $ApprListName -ErrorAction SilentlyContinue
    if (-not $apprList) {
        New-PnPList -Title $ApprListName -Template GenericList -ErrorAction Stop | Out-Null
        $apprList = Get-PnPList -Identity $ApprListName -ErrorAction Stop
    }
    if (-not (Get-PnPField -List $ApprListName -Identity "EventDate" -ErrorAction SilentlyContinue)) {
        Add-PnPField -List $ApprListName -Type DateTime -DisplayName "EventDate" -InternalName "EventDate" -ErrorAction Stop | Out-Null
    }
    if (-not (Get-PnPField -List $ApprListName -Identity "Location" -ErrorAction SilentlyContinue)) {
        Add-PnPField -List $ApprListName -Type Text -DisplayName "Location" -InternalName "Location" -ErrorAction Stop | Out-Null
    }
    if (-not (Get-PnPField -List $ApprListName -Identity "RelatedAuthor" -ErrorAction SilentlyContinue)) {
        Add-PnPField -List $ApprListName -Type Lookup -DisplayName "RelatedAuthor" -InternalName "RelatedAuthor" `
            -LookupList $authorsList.Id.ToString() -LookupField "Title" -ErrorAction Stop | Out-Null
    }

    # 4. Ensure Author_Narratives list
    Write-Host "Ensuring '$NarrListName' list exists..." -ForegroundColor Cyan
    $narrList = Get-PnPList -Identity $NarrListName -ErrorAction SilentlyContinue
    if (-not $narrList) {
        New-PnPList -Title $NarrListName -Template GenericList -ErrorAction Stop | Out-Null
        $narrList = Get-PnPList -Identity $NarrListName -ErrorAction Stop
    }
    if (-not (Get-PnPField -List $NarrListName -Identity "Narrative" -ErrorAction SilentlyContinue)) {
        Add-PnPField -List $NarrListName -Type Note -DisplayName "Narrative" -InternalName "Narrative" -ErrorAction Stop | Out-Null
    }
    if (-not (Get-PnPField -List $NarrListName -Identity "RelatedAuthor" -ErrorAction SilentlyContinue)) {
        Add-PnPField -List $NarrListName -Type Lookup -DisplayName "RelatedAuthor" -InternalName "RelatedAuthor" `
            -LookupList $authorsList.Id.ToString() -LookupField "Title" -ErrorAction Stop | Out-Null
    }

    # 5. Populate Sample Authors with Picture URLs
    Write-Host "Populating sample records..." -ForegroundColor Cyan
    $sampleAuthors = @(
        @{ Name = "George Orwell"; Picture = "/sites/AppRegistrationTests/Images1/orwell.jpg, George Orwell" },
        @{ Name = "Jane Austen";   Picture = "/sites/AppRegistrationTests/Images1/jane-austin.jpg, Jane Austen" },
        @{ Name = "Isaac Asimov";  Picture = "/sites/AppRegistrationTests/Images1/isaac-asimov.jpeg, Isaac Asimov" }
    )
    $existingAuthors = Get-PnPListItem -List $AuthorsListName -Fields "Id", "Title", "Picture" -ErrorAction SilentlyContinue

    foreach ($author in $sampleAuthors) {
        $existing = $existingAuthors | Where-Object { $_["Title"] -eq $author.Name }
        if ($existing) {
            Set-PnPListItem -List $AuthorsListName -Identity $existing.Id -Values @{ "Picture" = $author.Picture } -ErrorAction SilentlyContinue | Out-Null
        } else {
            Add-PnPListItem -List $AuthorsListName -Values @{ Title = $author.Name; Picture = $author.Picture } -ErrorAction SilentlyContinue | Out-Null
        }
    }

    # 6. Ensure Modern Test Page with HeaderType None
    Write-Host "Configuring modern test page '$PageName' with HeaderType None..." -ForegroundColor Cyan
    $page = Get-PnPPage -Identity $PageName -ErrorAction SilentlyContinue
    if (-not $page) {
        $page = Add-PnPPage -Name $PageName -LayoutType Article -HeaderType None -ErrorAction Stop
        Add-PnPPageSection -Page $page -SectionTemplate OneColumn -Order 1 | Out-Null
    } else {
        Set-PnPPage -Identity $PageName -HeaderType None | Out-Null
    }
    Set-PnPPage -Identity $PageName -Publish | Out-Null

    Write-Host "==================================================================" -ForegroundColor Green
    Write-Host " Schema & Page Provisioning COMPLETE!" -ForegroundColor Green
    Write-Host " Target Page: $($SiteUrl.TrimEnd('/'))/SitePages/$PageName.aspx" -ForegroundColor Yellow
    Write-Host "==================================================================" -ForegroundColor Green

} catch {
    Write-Host " FAIL: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
