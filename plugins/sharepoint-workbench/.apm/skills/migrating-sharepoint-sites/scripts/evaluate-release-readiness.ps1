<#
.SYNOPSIS
Evaluates whether a release manifest's in-scope objects are ready for a
human go/no-go decision: READY_FOR_DECISION, BLOCKED, or INCOMPLETE_EVIDENCE.

.DESCRIPTION
Never executes, deploys, or decides anything itself -- it only evaluates
locally-supplied evidence against the release gates below and returns one
of exactly three states. A human still makes the actual go/no-go call.

Gates evaluated:
- objectScope must be non-empty; an empty/missing scope is an invalid
  input and the function throws rather than silently evaluating nothing.
- Every dependency must be in state COMPLETE, unless an approvedExceptions
  entry explicitly names that dependency's id with an attributed
  approvedBy/approvedAt.
- Every in-scope object must have a testAcceptance entry whose environment
  is exactly "test" (a "dev" entry for the same object never satisfies
  this -- DEV and TEST are different environment sets per the register's
  own fieldAuthority rule), with accepted=$true AND a non-blank
  approvedBy. An outcome of "SKIPPED_EXISTING" alone, without an
  explicit accepted=$true/approvedBy, does not count as acceptance.
- Every CRITICAL verifierFindings entry for an in-scope object must have
  passed=$true, unless covered by an approvedExceptions entry for that
  specific checkId/objectId.
- recoveryRehearsal must be present, performed=$true, and validUntil must
  be in the future; missing or expired blocks the release outright.
- Every sensitiveAccessChecks entry must have passed=$true; a failure
  here is never waived by an unrelated passing check elsewhere in the
  manifest (each sensitive-access failure is evaluated independently).
- If the manifest supplies entirely empty verifierFindings AND entirely
  empty testAcceptance (no evidence at all to evaluate, as opposed to
  evidence that explicitly fails a gate), the result is
  INCOMPLETE_EVIDENCE rather than BLOCKED or READY -- there is not enough
  information yet to make either call.

A result carries a Fingerprint (hash of releaseId + packageDigest +
objectScope); Test-ReleaseReadinessStillValid recomputes that fingerprint
against a (possibly changed) manifest and returns $false the moment the
package digest, release id, or scope has changed since the result was
produced -- a stale readiness result must never be treated as still valid.

.KEY INPUT DEPENDENCIES
- A release manifest object/JSON with: releaseId, packageDigest,
  objectScope[], dependencies[], testAcceptance[], verifierFindings[],
  approvedExceptions[], sensitiveAccessChecks[], recoveryRehearsal

.OUTPUTS
- Invoke-ReleaseReadinessEvaluation: an object with State
  (READY_FOR_DECISION|BLOCKED|INCOMPLETE_EVIDENCE), Blockers (string[]),
  Details (per-object evaluation notes), and Fingerprint.
- Test-ReleaseReadinessStillValid: $true/$false.

.FUNCTION INDEX
Get-ReleaseReadinessFingerprint, Invoke-ReleaseReadinessEvaluation,
Test-ReleaseReadinessStillValid.

.EXAMPLE
pwsh -File .\evaluate-release-readiness.ps1 -ManifestPath .\release-manifest.json
#>

[CmdletBinding()]
param(
    [string]$ManifestPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-ReleaseReadinessFingerprint {
    <# Fingerprints the release identity + package + scope that, if any
    change, must invalidate a prior readiness result. #>
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][object]$Manifest)

    $scopeJoined = (@($Manifest.objectScope) | Sort-Object) -join ","
    $combined = "$($Manifest.releaseId)|$($Manifest.packageDigest)|$scopeJoined"
    $hashBytes = [System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes($combined))
    return [System.BitConverter]::ToString($hashBytes).Replace("-", "").ToLowerInvariant()
}

function ConvertTo-SafeArray {
    <# @($null) returns a 1-element array containing $null, not an empty
    array -- this normalizes a possibly-$null collection (e.g. an empty
    JSON array round-tripped through ConvertFrom-Json) into a genuine
    empty array so downstream .Count/Where-Object logic is accurate. #>
    [CmdletBinding()]
    param([Parameter()]$InputObject)

    if ($null -eq $InputObject) { return ,@() }
    return ,@($InputObject)
}

function Invoke-ReleaseReadinessEvaluation {
    <#
    Evaluates one release manifest against the documented gates and returns
    State/Blockers/Details/Fingerprint. Throws on an invalid manifest
    (empty objectScope). Never returns a state outside the three-value
    contract and never emits any acceptance/closure label of its own.
    #>
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][object]$Manifest)

    $objectScope = ConvertTo-SafeArray $Manifest.objectScope
    if ($objectScope.Count -eq 0) {
        throw "Release manifest has an empty objectScope; nothing is selected to evaluate."
    }

    $blockers = [System.Collections.Generic.List[string]]::new()
    $details = [System.Collections.Generic.List[object]]::new()

    $dependencies = ConvertTo-SafeArray $Manifest.dependencies
    $approvedExceptions = ConvertTo-SafeArray $Manifest.approvedExceptions
    $testAcceptance = ConvertTo-SafeArray $Manifest.testAcceptance
    $verifierFindings = ConvertTo-SafeArray $Manifest.verifierFindings
    $sensitiveAccessChecks = ConvertTo-SafeArray $Manifest.sensitiveAccessChecks

    $hasAnyAcceptanceEvidence = $testAcceptance.Count -gt 0
    $hasAnyVerifierEvidence = $verifierFindings.Count -gt 0
    $incompleteEvidence = (-not $hasAnyAcceptanceEvidence) -and (-not $hasAnyVerifierEvidence)

    # --- Dependencies ---
    foreach ($dependency in $dependencies) {
        if ([string]$dependency.state -eq "COMPLETE") { continue }
        $exception = $approvedExceptions | Where-Object {
            [string]$_.checkId -eq [string]$dependency.id -and -not [string]::IsNullOrWhiteSpace([string]$_.approvedBy)
        } | Select-Object -First 1
        if ($exception) {
            $details.Add([pscustomobject]@{ Gate = "dependency"; Id = $dependency.id; Status = "WAIVED_BY_EXCEPTION" })
            continue
        }
        $blockers.Add("Dependency '$($dependency.id)' is not COMPLETE (state: $($dependency.state)) and has no approved exception.")
    }

    # --- TEST acceptance per in-scope object ---
    foreach ($objectId in $objectScope) {
        $acceptanceEntries = @($testAcceptance | Where-Object { [string]$_.objectId -eq [string]$objectId })
        $testEntry = $acceptanceEntries | Where-Object { [string]$_.environment -eq "test" } | Select-Object -First 1

        if (-not $testEntry) {
            if ($acceptanceEntries.Count -gt 0) {
                $blockers.Add("Object '$objectId' has acceptance evidence only for a non-test environment; DEV evidence cannot satisfy a TEST acceptance requirement.")
            } elseif ($hasAnyAcceptanceEvidence) {
                $blockers.Add("Object '$objectId' has no TEST acceptance entry.")
            }
            continue
        }

        $accepted = [bool]$testEntry.accepted
        $approvedBy = if ($testEntry.PSObject.Properties["approvedBy"]) { [string]$testEntry.approvedBy } else { $null }
        if (-not $accepted -or [string]::IsNullOrWhiteSpace($approvedBy)) {
            $outcome = if ($testEntry.PSObject.Properties["outcome"]) { [string]$testEntry.outcome } else { "UNKNOWN" }
            $blockers.Add("Object '$objectId' TEST acceptance is not confirmed (outcome: $outcome); an outcome alone does not satisfy acceptance without accepted=true and an attributed approvedBy.")
            continue
        }
        $details.Add([pscustomobject]@{ Gate = "testAcceptance"; Id = $objectId; Status = "ACCEPTED" })
    }

    # --- CRITICAL verifier findings per in-scope object ---
    foreach ($objectId in $objectScope) {
        $criticalFindings = $verifierFindings | Where-Object { [string]$_.objectId -eq [string]$objectId -and [string]$_.severity -eq "CRITICAL" }
        foreach ($finding in $criticalFindings) {
            if ([bool]$finding.passed) { continue }
            $exception = $approvedExceptions | Where-Object {
                [string]$_.checkId -eq [string]$objectId -and -not [string]::IsNullOrWhiteSpace([string]$_.approvedBy)
            } | Select-Object -First 1
            if ($exception) {
                $details.Add([pscustomobject]@{ Gate = "verifierFinding"; Id = $objectId; Status = "WAIVED_BY_EXCEPTION" })
                continue
            }
            $blockers.Add("Object '$objectId' has a failing CRITICAL verifier finding with no approved exception.")
        }
    }

    # --- Sensitive-access checks: never waived by an unrelated pass ---
    foreach ($check in $sensitiveAccessChecks) {
        if ([bool]$check.passed) { continue }
        $blockers.Add("Sensitive-access check failed for object '$($check.objectId)'; this cannot be waived by any other passing check.")
    }

    # --- Recovery rehearsal ---
    $rehearsal = $Manifest.recoveryRehearsal
    if (-not $rehearsal -or -not [bool]$rehearsal.performed) {
        $blockers.Add("Recovery rehearsal has not been performed.")
    } else {
        [datetime]$validUntil = [datetime]::MinValue
        $parsedValidUntil = $false
        if ($rehearsal.PSObject.Properties["validUntil"] -and -not [string]::IsNullOrWhiteSpace([string]$rehearsal.validUntil)) {
            $parsedValidUntil = [datetime]::TryParse([string]$rehearsal.validUntil, [ref]$validUntil)
        }
        if (-not $parsedValidUntil -or $validUntil -lt (Get-Date).ToUniversalTime()) {
            $blockers.Add("Recovery rehearsal is expired or has no valid expiry.")
        }
    }

    $state = if ($blockers.Count -gt 0) {
        "BLOCKED"
    } elseif ($incompleteEvidence) {
        "INCOMPLETE_EVIDENCE"
    } else {
        "READY_FOR_DECISION"
    }

    return [pscustomobject]@{
        State = $state
        Blockers = $blockers.ToArray()
        Details = $details.ToArray()
        Fingerprint = Get-ReleaseReadinessFingerprint -Manifest $Manifest
    }
}

function Test-ReleaseReadinessStillValid {
    <#
    Returns $true only if Manifest's fingerprint still matches Result's
    Fingerprint. A changed releaseId, packageDigest, or objectScope
    invalidates a prior readiness result; it must be re-evaluated, not
    reused.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][object]$Result,
        [Parameter(Mandatory = $true)][object]$Manifest
    )

    return ([string]$Result.Fingerprint -eq (Get-ReleaseReadinessFingerprint -Manifest $Manifest))
}

if ($MyInvocation.InvocationName -ne "." -and $PSBoundParameters.ContainsKey("ManifestPath")) {
    if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
        throw "Manifest file was not found: $ManifestPath"
    }
    $manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
    $evaluation = Invoke-ReleaseReadinessEvaluation -Manifest $manifest
    $evaluation | ConvertTo-Json -Depth 10
}
