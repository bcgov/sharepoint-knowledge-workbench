"""Integration tests for Lookup support in the list-column executor.

Purpose:
    Verify spo-add-list-column.ps1 builds Lookup field XML from a plan (resolving the
    lookup list GUID by title), keeps typed columns on Add-PnPField, and records a
    failure when the lookup list is missing.

Key Input Dependencies:
    - scripts/provisioning/spo-add-list-column.ps1
    - PowerShell 7 (pwsh)

Function Index:
    _run_executor, test_lookup_column_is_created_from_xml_with_resolved_list_guid,
    test_typed_column_still_uses_add_pnp_field,
    test_lookup_column_without_lookup_list_is_reported_as_failed
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parents[2]
SCRIPT = PACKAGE / "scripts" / "provisioning" / "spo-add-list-column.ps1"
CONNECTION_HELPER = (
    PACKAGE.parent
    / "sharepoint-workbench-setup"
    / "scripts"
    / "Get-WorkbenchConnectionConfig.ps1"
)
LOOKUP_LIST_GUID = "11111111-2222-3333-4444-555555555555"
requires_pwsh = pytest.mark.skipif(shutil.which("pwsh") is None, reason="pwsh not installed")

HARNESS = """
param([string]$Script, [string]$PlanPath, [string]$ConfigPath, [string]$CallLog)
$ErrorActionPreference = 'Stop'
$global:calls = @()
function Connect-PnPOnline { [CmdletBinding()] param($Url, $ClientId, $Tenant, [switch]$Interactive) }
function Get-PnPList {
    [CmdletBinding()] param($Identity)
    if ($Identity -eq 'Form Types') { [pscustomobject]@{ Id = [guid]'%s'; Title = 'Form Types' } }
    else { throw "List '$Identity' not found" }
}
function Add-PnPField {
    [CmdletBinding()]
    param([string]$List, [string]$Type, [string]$InternalName, [string]$DisplayName, [bool]$AddToDefaultView)
    $global:calls += [ordered]@{ Cmdlet = 'Add-PnPField'; List = $List; Type = $Type; InternalName = $InternalName }
}
function Add-PnPFieldFromXml {
    [CmdletBinding()] param([string]$List, [string]$FieldXml)
    $global:calls += [ordered]@{ Cmdlet = 'Add-PnPFieldFromXml'; List = $List; FieldXml = $FieldXml }
}
$out = & $Script -PlanPath $PlanPath -ConfigPath $ConfigPath -Execute -ConfirmToken ADD-SPO-LIST-COLUMN
[ordered]@{ calls = $global:calls; result = ($out | ConvertFrom-Json) } | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $CallLog
""" % LOOKUP_LIST_GUID


# Run the executor through a real PowerShell process with tenant cmdlets replaced by a harness.
def _run_executor(tmp_path, action):
    """Run the executor against one plan action and return (process, parsed call log)."""
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"confirmation_token": "TEST", "actions": [action]}), encoding="utf-8")
    config = tmp_path / "config.psd1"
    config.write_text(
        "@{ Connection = @{ SiteUrl = 'https://example.invalid/sites/t'; ClientId = 'c'; TenantId = 't' } }",
        encoding="utf-8",
    )
    executor = tmp_path / SCRIPT.name
    executor.write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "Get-WorkbenchConnectionConfig.ps1").write_text(
        CONNECTION_HELPER.read_text(encoding="utf-8"), encoding="utf-8"
    )
    call_log = tmp_path / "call.json"
    harness = tmp_path / "harness.ps1"
    harness.write_text(HARNESS, encoding="utf-8")
    proc = subprocess.run(
        ["pwsh", "-NoProfile", "-File", str(harness), "-Script", str(executor),
         "-PlanPath", str(plan), "-ConfigPath", str(config), "-CallLog", str(call_log)],
        capture_output=True, text=True, timeout=120,
    )
    log = json.loads(call_log.read_text(encoding="utf-8")) if call_log.exists() else None
    return proc, log


# A Lookup action resolves the lookup list GUID by title and submits field XML to the target list.
@requires_pwsh
def test_lookup_column_is_created_from_xml_with_resolved_list_guid(tmp_path):
    """A Lookup action resolves the lookup list GUID by title and submits field XML to the target list."""
    proc, log = _run_executor(tmp_path, {
        "list_title": "Forms", "internal_name": "SIZAFormType", "display_name": "Form Type",
        "type": "Lookup", "lookup_list": "Form Types", "lookup_field": "Title",
    })
    assert proc.returncode == 0, proc.stderr
    assert log["result"]["outcome"] == "OBSERVED"
    (call,) = log["calls"]
    assert call["Cmdlet"] == "Add-PnPFieldFromXml"
    assert call["List"] == "Forms"
    xml = call["FieldXml"]
    assert 'Type="Lookup"' in xml
    assert 'Name="SIZAFormType"' in xml
    assert 'DisplayName="Form Type"' in xml
    assert f'List="{{{LOOKUP_LIST_GUID}}}"' in xml
    assert 'ShowField="Title"' in xml


# Typed columns keep the existing Add-PnPField path.
@requires_pwsh
def test_typed_column_still_uses_add_pnp_field(tmp_path):
    """Typed columns keep the existing Add-PnPField path."""
    proc, log = _run_executor(tmp_path, {
        "list_title": "Forms", "internal_name": "SIZAFormNumber", "display_name": "Form Number",
        "type": "Text", "add_to_default_view": True,
    })
    assert proc.returncode == 0, proc.stderr
    (call,) = log["calls"]
    assert call["Cmdlet"] == "Add-PnPField"
    assert call["Type"] == "Text"


# A Lookup action naming a list that does not exist is reported as failed, never silently skipped.
@requires_pwsh
def test_lookup_column_without_lookup_list_is_reported_as_failed(tmp_path):
    """A Lookup action naming a missing list is reported as failed."""
    proc, log = _run_executor(tmp_path, {
        "list_title": "Forms", "internal_name": "SIZAFormType", "display_name": "Form Type",
        "type": "Lookup", "lookup_list": "No Such List",
    })
    assert proc.returncode == 0, proc.stderr
    assert log["result"]["outcome"] == "FAILED"
    assert log["calls"] == []
    assert "No Such List" in log["result"]["failed"][0]["error"]
