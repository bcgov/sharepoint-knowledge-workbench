"""Integration tests for item metadata (values) on upload.

Purpose:
    Verify spo-upload-file.ps1 passes plan `values` to Add-PnPFile, resolves lookup values
    by title to the lookup item ID, keeps value-less uploads unchanged, and shows values in
    the dry-run summary.

Key Input Dependencies:
    - scripts/content-publication/spo-upload-file.ps1
    - PowerShell 7 (pwsh)

Function Index:
    _run, test_values_reach_add_pnp_file, test_lookup_value_is_resolved_to_item_id,
    test_upload_without_values_passes_no_values, test_unresolved_lookup_value_fails_before_upload,
    test_dry_run_summary_lists_values
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parents[2]
SCRIPT = PACKAGE / "scripts" / "content-publication" / "spo-upload-file.ps1"
CONNECTION_HELPER = (
    PACKAGE.parent
    / "sharepoint-workbench-setup"
    / "scripts"
    / "Get-WorkbenchConnectionConfig.ps1"
)
requires_pwsh = pytest.mark.skipif(shutil.which("pwsh") is None, reason="pwsh not installed")

HARNESS = """
param([string]$Script, [string]$PlanPath, [string]$ConfigPath, [string]$CallLog, [switch]$Execute)
$ErrorActionPreference = 'Stop'
$global:calls = @()
function Connect-PnPOnline { [CmdletBinding()] param($Url, $ClientId, $Tenant, [switch]$Interactive) }
function Get-PnPList { [CmdletBinding()] param($Identity) [pscustomobject]@{ Title = $Identity } }
function Resolve-PnPFolder { [CmdletBinding()] param($SiteRelativePath) }
function Get-PnPFolder { [CmdletBinding()] param($Url) [pscustomobject]@{ Name = $Url } }
function Get-PnPFile { [CmdletBinding()] param($Url) $null }
function Get-PnPListItem {
    [CmdletBinding()] param($List, $Fields, $PageSize)
    $global:calls += [ordered]@{ Cmdlet = 'Get-PnPListItem'; List = $List }
    [pscustomobject]@{ Id = 7; FieldValues = @{ Title = 'Adult Criminal Forms' } }
    [pscustomobject]@{ Id = 8; FieldValues = @{ Title = 'Youth Court Forms' } }
}
function Add-PnPFile {
    [CmdletBinding()] param($Path, $Folder, $NewFileName, [hashtable]$Values)
    $global:calls += [ordered]@{
        Cmdlet = 'Add-PnPFile'; NewFileName = $NewFileName
        HasValues = $PSBoundParameters.ContainsKey('Values'); Values = $Values
    }
}
$params = @{ PlanPath = $PlanPath; ConfigPath = $ConfigPath }
if ($Execute) { $params['Execute'] = $true; $params['ConfirmToken'] = 'PUBLISH-SPO-MARKDOWN' }
$err = $null
try { $out = & $Script @params } catch { $err = $_.Exception.Message }
[ordered]@{ calls = $global:calls; error = $err; stdout = ($out | Out-String) } | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $CallLog
"""


# Run the uploader through a real PowerShell process with tenant cmdlets replaced by a harness.
def _run(tmp_path, values, execute=True):
    """Run the uploader for one action and return the parsed harness log."""
    source = tmp_path / "adm011.pdf"
    source.write_bytes(b"%PDF-1.4 test")
    action = {
        "source_path": str(source), "target_library": "Forms", "target_folder": "",
        "target_filename": "adm011.pdf",
    }
    if values is not None:
        action["values"] = values
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"document_id": "forms", "actions": [action]}), encoding="utf-8")
    config = tmp_path / "config.psd1"
    config.write_text(
        "@{ Connection = @{ SiteUrl = 'https://example.invalid/sites/t'; ClientId = 'c'; TenantId = 't' } }",
        encoding="utf-8",
    )
    (tmp_path / SCRIPT.name).write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "Get-WorkbenchConnectionConfig.ps1").write_text(
        CONNECTION_HELPER.read_text(encoding="utf-8"), encoding="utf-8"
    )
    harness = tmp_path / "harness.ps1"
    harness.write_text(HARNESS, encoding="utf-8")
    call_log = tmp_path / "call.json"
    cmd = ["pwsh", "-NoProfile", "-File", str(harness), "-Script", str(tmp_path / SCRIPT.name),
           "-PlanPath", str(plan), "-ConfigPath", str(config), "-CallLog", str(call_log)]
    if execute:
        cmd.append("-Execute")
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr
    return json.loads(call_log.read_text(encoding="utf-8"))


def _calls(log, cmdlet):
    return [c for c in log["calls"] if c["Cmdlet"] == cmdlet]


# Plain values in the plan action reach Add-PnPFile -Values.
@requires_pwsh
def test_values_reach_add_pnp_file(tmp_path):
    """Plain values in the plan action reach Add-PnPFile -Values."""
    log = _run(tmp_path, {"Title": "Record of Fees", "SIZAFormNumber": "adm011"})
    assert log["error"] is None
    (upload,) = _calls(log, "Add-PnPFile")
    assert upload["HasValues"] is True
    assert upload["Values"] == {"Title": "Record of Fees", "SIZAFormNumber": "adm011"}


# A lookup value given by title is resolved to the lookup item ID.
@requires_pwsh
def test_lookup_value_is_resolved_to_item_id(tmp_path):
    """A lookup value given by title is resolved to the lookup item ID."""
    log = _run(tmp_path, {
        "Title": "Record of Fees",
        "SIZAFormType": {"lookup_list": "Form Types", "lookup_value": "Adult Criminal Forms"},
    })
    assert log["error"] is None
    (upload,) = _calls(log, "Add-PnPFile")
    assert upload["Values"]["SIZAFormType"] == 7
    assert upload["Values"]["Title"] == "Record of Fees"


# An action without values keeps the original upload call (no -Values).
@requires_pwsh
def test_upload_without_values_passes_no_values(tmp_path):
    """An action without values keeps the original upload call."""
    log = _run(tmp_path, None)
    assert log["error"] is None
    (upload,) = _calls(log, "Add-PnPFile")
    assert upload["HasValues"] is False


# A lookup title with no match stops the run before the file is uploaded.
@requires_pwsh
def test_unresolved_lookup_value_fails_before_upload(tmp_path):
    """A lookup title with no match stops the run before the file is uploaded."""
    log = _run(tmp_path, {
        "SIZAFormType": {"lookup_list": "Form Types", "lookup_value": "No Such Type"},
    })
    assert log["error"] and "No Such Type" in log["error"]
    assert _calls(log, "Add-PnPFile") == []


# The dry-run summary lists the values and makes no tenant call.
@requires_pwsh
def test_dry_run_summary_lists_values(tmp_path):
    """The dry-run summary lists the values and makes no tenant call."""
    log = _run(tmp_path, {"Title": "Record of Fees"}, execute=False)
    assert log["calls"] == []
    assert "Record of Fees" in log["stdout"]
