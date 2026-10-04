<#
.SYNOPSIS
    Shared helpers for the list-content audit scripts (dot-source with: . "$PSScriptRoot/audit-helpers.ps1").
#>

function ConvertTo-ODataListTitle {
    <#
    .SYNOPSIS
        Makes a list title safe to place inside getbytitle('...') of a SharePoint REST URL.
    .DESCRIPTION
        A single quote is doubled (OData string literal rule) and the result is URL-encoded, so titles containing an apostrophe,
        ampersand, hash, percent sign, plus sign or a space cannot break or redirect the request.
    #>
    param([Parameter(Mandatory)][string]$Title)
    return [System.Uri]::EscapeDataString($Title.Replace("'", "''"))
}
