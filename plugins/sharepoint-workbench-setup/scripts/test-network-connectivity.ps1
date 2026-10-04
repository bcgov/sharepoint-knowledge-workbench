<#
.SYNOPSIS
Pre-flight firewall/network + interactive (delegated) authentication check
for the SharePoint connection described in this repository's root
config.psd1 (written by the setup-sharepoint-connection skill).

.DESCRIPTION
Adapted from a real project's network-connectivity script; SharePoint/
Entra/Graph endpoints only -- no project-specific gateway or endpoint was
carried over.

Phase 1 runs Test-NetConnection (TCP reachability) against every endpoint
required for Entra ID auth, SharePoint Online, Microsoft Graph, and
certificate revocation checking (CRL/OCSP):
  - Entra ID token acquisition (Required): login.microsoftonline.com:443/80,
    login.windows.net:443, device.login.microsoftonline.com:443 (required
    here -- this script's interactive/device-code flow depends on it),
    autologon.microsoftazuread-sso.com:443, enterpriseregistration.windows.net:443.
  - SharePoint Online (Required): $tenant.sharepoint.com:443/80,
    spoprod-a.akamaihd.net:443.
  - Microsoft Graph (Required): graph.microsoft.com:443/80.
  - CRL/OCSP revocation checking (Informational only): observed elsewhere to
    soft-fail (auth still succeeds) rather than hard-block when a responder
    is unreachable -- crl.microsoft.com:80, mscrl.microsoft.com:80,
    ocsp.msocsp.com:80, oneocsp.microsoft.com:80, crl3.digicert.com:80,
    ocsp.digicert.com:80, crl.globalsign.com:80, crl.identrust.com:80.

Phase 2 performs a real Connect-PnPOnline delegated auth against SharePoint
Online using the app registration/tenant recorded in config.psd1, prompting
for a browser sign-in (or device code with -DeviceLogin). A pass here
confirms this app registration/user combination can authenticate
interactively.

No environment values are hardcoded -- this reads SiteUrl/TenantId/ClientId
from this repository's root config.psd1 (written by the
setup-sharepoint-connection skill), so running it against a DEV config.psd1
tests DEV and a PROD config.psd1 tests PROD.

.PARAMETER SiteUrl
Full SharePoint site URL, used to derive the tenant subdomain for the
SharePoint checks and as the Connect-PnPOnline target. Defaults to reading
SiteUrl from config.psd1 -- do not hardcode a different environment's URL.

.PARAMETER ConfigPath
Path to config.psd1. Defaults to this repository's root config.psd1 (the
file setup-sharepoint-connection writes).

.PARAMETER DeviceLogin
Use device-code sign-in (prints a code + URL to enter on any device) instead
of the default embedded browser popup. Useful on hosts without an
interactive desktop session.

.PARAMETER SkipAuthTest
Run Phase 1 (network) only. Skips the interactive browser/device-code prompt
entirely -- use this for a firewall-only check when you don't want to sign in.

.EXAMPLE
# Firewall-only check
pwsh -File ./test-network-connectivity.ps1 -SkipAuthTest

.EXAMPLE
# Full network + interactive browser auth check
pwsh -File ./test-network-connectivity.ps1

.EXAMPLE
# Full check using device-code sign-in instead of embedded browser
pwsh -File ./test-network-connectivity.ps1 -DeviceLogin
#>

param(
    [string]$SiteUrl    = "",
    [string]$ConfigPath = "",
    [switch]$DeviceLogin,
    [switch]$SkipAuthTest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ============================================================
# Resolve config (SiteUrl, and -- for Phase 2 -- ClientId/TenantId)
# No environment values are ever hardcoded here -- this repository's root
# config.psd1 is the single source of truth for which tenant/site this run
# targets.
# ============================================================
$cfg = $null
if (-not $ConfigPath -or -not (Test-Path $ConfigPath)) {
    $candidates = @(
        "$PWD\config.psd1",
        "$PSScriptRoot\config.psd1",
        "$PSScriptRoot\..\config.psd1",
        "$PSScriptRoot\..\..\config.psd1",
        "$PSScriptRoot\..\..\..\config.psd1",
        "$PSScriptRoot\..\..\..\..\config.psd1"
    )
    foreach ($cand in $candidates) {
        if (Test-Path $cand) {
            $ConfigPath = (Resolve-Path $cand).Path
            break
        }
    }
}

if (Test-Path $ConfigPath) {
    $raw = Import-PowerShellDataFile $ConfigPath
    # Support both this plugin's nested `Connection = @{...}` schema
    # (setup-sharepoint-connection's output) and a flat top-level
    # ClientId/TenantId/SiteUrl schema (seen in some existing config.psd1
    # files carried over from other tooling).
    $cfg = if ($raw.ContainsKey('Connection')) { $raw.Connection } else { $raw }
    if (-not $SiteUrl -and $cfg.SiteUrl) { $SiteUrl = $cfg.SiteUrl }
}

if (-not $SiteUrl) { Write-Error "Could not resolve SiteUrl. Pass -SiteUrl or set Connection.SiteUrl in config.psd1." }

$tenant = ([Uri]$SiteUrl).Host -replace '\.sharepoint\.com$', ''

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  test-network-connectivity — Delegated Auth                ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Tenant   : $tenant" -ForegroundColor White
Write-Host ""

# ============================================================
# Endpoint list -- Entra ID, SharePoint Online, Microsoft Graph, CRL/OCSP
# only. No project-specific gateway or endpoint is included here.
# ============================================================
$checks = @(
    # Entra ID token acquisition
    @{ Group = "Entra ID token acquisition"; Host = "login.microsoftonline.com";           Port = 443; Required = $true }
    @{ Group = "Entra ID token acquisition"; Host = "login.microsoftonline.com";           Port = 80;  Required = $true }
    @{ Group = "Entra ID token acquisition"; Host = "login.windows.net";                   Port = 443; Required = $true }
    @{ Group = "Entra ID token acquisition"; Host = "device.login.microsoftonline.com";    Port = 443; Required = $true }
    @{ Group = "Entra ID token acquisition"; Host = "autologon.microsoftazuread-sso.com";  Port = 443; Required = $true }
    @{ Group = "Entra ID token acquisition"; Host = "enterpriseregistration.windows.net";  Port = 443; Required = $true }

    # SharePoint Online
    @{ Group = "SharePoint Online"; Host = "$tenant.sharepoint.com"; Port = 443; Required = $true }
    @{ Group = "SharePoint Online"; Host = "$tenant.sharepoint.com"; Port = 80;  Required = $true }
    @{ Group = "SharePoint Online"; Host = "spoprod-a.akamaihd.net"; Port = 443; Required = $true }

    # Microsoft Graph
    @{ Group = "Microsoft Graph"; Host = "graph.microsoft.com"; Port = 443; Required = $true }
    @{ Group = "Microsoft Graph"; Host = "graph.microsoft.com"; Port = 80;  Required = $true }

    # Certificate revocation checking -- informational only; observed
    # elsewhere to soft-fail (auth still succeeds) when a responder is
    # unreachable, so a blocked CRL/OCSP host doesn't falsely gate
    # "safe to proceed" -- still worth opening for defense in depth.
    @{ Group = "CRL/OCSP revocation checking (informational — soft-fail tolerated by observed auth behavior)"; Host = "crl.microsoft.com";     Port = 80; Required = $false }
    @{ Group = "CRL/OCSP revocation checking (informational — soft-fail tolerated by observed auth behavior)"; Host = "mscrl.microsoft.com";   Port = 80; Required = $false }
    @{ Group = "CRL/OCSP revocation checking (informational — soft-fail tolerated by observed auth behavior)"; Host = "ocsp.msocsp.com";       Port = 80; Required = $false }
    @{ Group = "CRL/OCSP revocation checking (informational — soft-fail tolerated by observed auth behavior)"; Host = "oneocsp.microsoft.com"; Port = 80; Required = $false }
    @{ Group = "CRL/OCSP revocation checking (informational — soft-fail tolerated by observed auth behavior)"; Host = "crl3.digicert.com";     Port = 80; Required = $false }
    @{ Group = "CRL/OCSP revocation checking (informational — soft-fail tolerated by observed auth behavior)"; Host = "ocsp.digicert.com";     Port = 80; Required = $false }
    @{ Group = "CRL/OCSP revocation checking (informational — soft-fail tolerated by observed auth behavior)"; Host = "crl.globalsign.com";    Port = 80; Required = $false }
    @{ Group = "CRL/OCSP revocation checking (informational — soft-fail tolerated by observed auth behavior)"; Host = "crl.identrust.com";     Port = 80; Required = $false }
)

# ============================================================
# Run checks
# ============================================================
# Test-NetConnection is Windows-only (NetTCPIP module). Use a raw
# .NET TcpClient connect-with-timeout instead so this script runs
# cross-platform (macOS/Linux pwsh included).
function Test-TcpPort {
    param([string]$ComputerName, [int]$Port, [int]$TimeoutMs = 5000)
    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $connectTask = $client.ConnectAsync($ComputerName, $Port)
        if ($connectTask.Wait($TimeoutMs) -and $client.Connected) { return $true }
        return $false
    } catch {
        return $false
    } finally {
        $client.Close()
    }
}

$results = @()
$lastGroup = ""

foreach ($check in $checks) {
    if ($check.Group -ne $lastGroup) {
        Write-Host ""
        Write-Host "  $($check.Group)" -ForegroundColor Cyan
        Write-Host "  $('─' * $check.Group.Length)" -ForegroundColor DarkGray
        $lastGroup = $check.Group
    }

    $ok = Test-TcpPort -ComputerName $check.Host -Port $check.Port

    $results += [PSCustomObject]@{
        Group    = $check.Group
        Host     = $check.Host
        Port     = $check.Port
        Required = $check.Required
        Passed   = $ok
    }

    $label = "$($check.Host):$($check.Port)"
    if ($ok) {
        Write-Host "    [PASS] $label" -ForegroundColor Green
    } elseif ($check.Required) {
        Write-Host "    [FAIL] $label  (Required)" -ForegroundColor Red
    } else {
        Write-Host "    [WARN] $label  (Optional/conditional — see script comments)" -ForegroundColor Yellow
    }
}

# ============================================================
# Phase 2 — Authentication test (interactive/delegated)
# Prompts for browser sign-in (or device code with -DeviceLogin).
# ============================================================
$authTestRun    = $false
$authTestPassed = $false
$authTestError  = $null

if ($SkipAuthTest) {
    Write-Host ""
    Write-Host "  Authentication test — skipped (-SkipAuthTest)" -ForegroundColor DarkGray
} elseif (-not $cfg -or -not $cfg.ClientId -or -not $cfg.TenantId) {
    Write-Host ""
    Write-Host "  Authentication test — skipped (ClientId/TenantId not set in config.psd1)" -ForegroundColor DarkGray
} else {
    Write-Host ""
    Write-Host "  Authentication test (interactive/delegated)" -ForegroundColor Cyan
    Write-Host "  ────────────────────────────────────────────" -ForegroundColor DarkGray
    Write-Host "    Site      : $SiteUrl" -ForegroundColor DarkGray
    Write-Host "    ClientId  : $($cfg.ClientId)" -ForegroundColor DarkGray
    Write-Host "    Mode      : $(if ($DeviceLogin) { 'Device code' } else { 'Interactive browser popup' })" -ForegroundColor DarkGray
    Write-Host ""
    if ($DeviceLogin) {
        Write-Host "    A device code and URL will be printed below — open the URL in any" -ForegroundColor Yellow
        Write-Host "    browser and enter the code to complete sign-in." -ForegroundColor Yellow
    } else {
        Write-Host "    A browser sign-in window will open — complete the sign-in there." -ForegroundColor Yellow
    }
    Write-Host ""

    $authTestRun = $true
    try {
        Import-Module PnP.PowerShell -ErrorAction Stop
        if ($DeviceLogin) {
            Connect-PnPOnline -Url $SiteUrl -ClientId $cfg.ClientId -Tenant $cfg.TenantId -DeviceLogin -ErrorAction Stop
        } else {
            Connect-PnPOnline -Url $SiteUrl -ClientId $cfg.ClientId -Tenant $cfg.TenantId -Interactive -ErrorAction Stop
        }
        $web = Get-PnPWeb -ErrorAction Stop

        Write-Host "    [PASS] Connected — site title: '$($web.Title)'" -ForegroundColor Green

        # CurrentUser is not loaded by Get-PnPWeb/Get-PnPContext by default — must be
        # explicitly requested via Get-PnPProperty, otherwise LoginName reads back empty.
        $currentUser = Get-PnPProperty -ClientObject $web -Property CurrentUser -ErrorAction Stop
        $loginName   = $currentUser.LoginName

        Write-Host "    [PASS] Signed in as: $loginName" -ForegroundColor Green
        $authTestPassed = $true

        Disconnect-PnPOnline -ErrorAction SilentlyContinue
    } catch {
        $authTestError = $_.Exception.Message
        Write-Host "    [FAIL] $authTestError" -ForegroundColor Red
        Write-Host "           Most common causes: sign-in was cancelled/timed out, the signed-in" -ForegroundColor Yellow
        Write-Host "           account lacks access to this site, or site permissions have not" -ForegroundColor Yellow
        Write-Host "           been granted for this app registration yet." -ForegroundColor Yellow
    }
}

# ============================================================
# Summary
# ============================================================
$requiredFails = @($results | Where-Object { $_.Required -and -not $_.Passed })
$optionalFails = @($results | Where-Object { -not $_.Required -and -not $_.Passed })
$passed        = @($results | Where-Object { $_.Passed })

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Summary                                                 ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Site tested     : $SiteUrl" -ForegroundColor White
Write-Host "  Network passed  : $($passed.Count) / $($results.Count)" -ForegroundColor White
Write-Host "  Required FAILED : $($requiredFails.Count)" -ForegroundColor $(if ($requiredFails.Count -gt 0) { "Red" } else { "Green" })
Write-Host "  Optional FAILED : $($optionalFails.Count)" -ForegroundColor $(if ($optionalFails.Count -gt 0) { "Yellow" } else { "Green" })
if ($authTestRun) {
    Write-Host "  Auth test       : $(if ($authTestPassed) { 'PASS' } else { 'FAIL' })" -ForegroundColor $(if ($authTestPassed) { "Green" } else { "Red" })
} else {
    Write-Host "  Auth test       : skipped" -ForegroundColor DarkGray
}
Write-Host ""

if ($requiredFails.Count -gt 0) {
    Write-Host "  Blocked endpoints (Required) — file/escalate the firewall change before proceeding:" -ForegroundColor Red
    foreach ($f in $requiredFails) {
        Write-Host "    - $($f.Host):$($f.Port)  [$($f.Group)]" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "  Do not attempt authentication troubleshooting until these pass." -ForegroundColor Yellow
    Write-Host ""
    exit 1
} elseif ($authTestRun -and -not $authTestPassed) {
    Write-Host "  All required network endpoints reachable, but the authentication test failed." -ForegroundColor Red
    Write-Host ""
    exit 1
} else {
    Write-Host "  All required endpoints reachable$(if ($authTestPassed) { ' and interactive authentication succeeded' }). Safe to proceed." -ForegroundColor Green
    Write-Host ""
    exit 0
}
