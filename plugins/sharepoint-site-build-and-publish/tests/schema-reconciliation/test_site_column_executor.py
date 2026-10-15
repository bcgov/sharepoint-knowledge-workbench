"""Integration tests for the site-column provisioning executor.

Purpose:
    Verify that typed site-column plans pass their group to Add-PnPField and
    preserve the executor's Custom Columns default.

Key Input Dependencies:
    - scripts/provisioning/spo-provision-site-columns.ps1
    - PowerShell 7 (pwsh)

Function Index:
    _run_executor, test_typed_site_column_group_reaches_add_pnp_field,
    test_typed_site_column_group_defaults_to_custom_columns
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parents[2]
SCRIPT = PACKAGE / "scripts" / "provisioning" / "spo-provision-site-columns.ps1"
CONNECTION_HELPER = (
    PACKAGE.parent
    / "sharepoint-workbench-setup"
    / "scripts"
    / "Get-WorkbenchConnectionConfig.ps1"
)
requires_pwsh = pytest.mark.skipif(shutil.which("pwsh") is None, reason="pwsh not installed")


# Run the executor through a real PowerShell process with tenant cmdlets captured by a harness.
def _run_executor(tmp_path, group=None):
    """Run the executor through a real PowerShell process with captured PnP calls."""
    plan = tmp_path / "plan.json"
    action = {
        "internal_name": "SIZALocationID",
        "action": "create",
        "reason": "declared but not present (type 'Text')",
        "xml": None,
        "type": "Text",
        "display_name": "Location #",
        "required": False,
        "choices": [],
    }
    if group is not None:
        action["group"] = group
    plan.write_text(json.dumps({"confirmation_token": "TEST", "actions": [action]}), encoding="utf-8")

    config = tmp_path / "config.psd1"
    config.write_text(
        "@{ Connection = @{ SiteUrl = 'https://example.invalid/sites/t'; ClientId = 'c'; TenantId = 't' } }",
        encoding="utf-8",
    )
    executor = tmp_path / SCRIPT.name
    executor.write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "Get-WorkbenchConnectionConfig.ps1").write_text(
        CONNECTION_HELPER.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    call_log = tmp_path / "call.json"
    harness = tmp_path / "harness.ps1"
    harness.write_text(
        """
param([string]$Script, [string]$PlanPath, [string]$ConfigPath, [string]$CallLog)
$ErrorActionPreference = 'Stop'
function Connect-PnPOnline { [CmdletBinding()] param($Url, $ClientId, $Tenant, [switch]$Interactive) }
function Add-PnPField {
    [CmdletBinding()]
    param([string]$Type, [string]$InternalName, [string]$DisplayName, [bool]$Required, [string]$Group)
    [ordered]@{
        Type = $Type
        InternalName = $InternalName
        DisplayName = $DisplayName
        Required = $Required
        Group = $Group
    } | ConvertTo-Json | Set-Content -LiteralPath $CallLog
}
function Add-PnPFieldFromXml { [CmdletBinding()] param([string]$FieldXml) }
& $Script -PlanPath $PlanPath -ConfigPath $ConfigPath -Execute -ConfirmToken PROVISION-SPO-SITE-COLUMNS
""",
        encoding="utf-8",
    )
    return subprocess.run(
        [
            "pwsh",
            "-NoProfile",
            "-File",
            str(harness),
            "-Script",
            str(executor),
            "-PlanPath",
            str(plan),
            "-ConfigPath",
            str(config),
            "-CallLog",
            str(call_log),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    ), call_log


# Verify a supplied plan group reaches the typed Add-PnPField call.
@requires_pwsh
def test_typed_site_column_group_reaches_add_pnp_field(tmp_path):
    """Verify a supplied plan group reaches the typed Add-PnPField call."""
    result, call_log = _run_executor(tmp_path, "SIZA Intranet Columns")
    assert result.returncode == 0, result.stderr
    assert json.loads(call_log.read_text(encoding="utf-8"))["Group"] == "SIZA Intranet Columns"


# Verify omitted group values retain the executor's established default.
@requires_pwsh
def test_typed_site_column_group_defaults_to_custom_columns(tmp_path):
    """Verify omitted group values retain the executor's established default."""
    result, call_log = _run_executor(tmp_path)
    assert result.returncode == 0, result.stderr
    assert json.loads(call_log.read_text(encoding="utf-8"))["Group"] == "Custom Columns"
