"""Executable tests for restore-sharepoint-agents.ps1's safety gates (zero tenant I/O paths only)."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "restore-sharepoint-agents.ps1"

pwsh = shutil.which("pwsh")
pytestmark = pytest.mark.skipif(pwsh is None, reason="pwsh not installed")


@pytest.fixture()
def config_file(tmp_path):
    cfg = tmp_path / "config.psd1"
    cfg.write_text('@{ SiteUrl = "https://example.sharepoint.com/sites/test"; ClientId = "x"; TenantId = "y" }')
    (tmp_path / "backup.agent").write_text("backed up agent content")
    return cfg


def run_script(config_file: Path, extra: str) -> subprocess.CompletedProcess:
    items_ps1 = "@(@{LocalPath='" + str(config_file.parent / "backup.agent") + "'; Url='SitePages/Example/agent.agent'})"
    return subprocess.run(
        [pwsh, "-NoProfile", "-NonInteractive", "-Command",
         f"& '{SCRIPT}' -ConfigFile '{config_file}' -Items {items_ps1} {extra}"],
        capture_output=True, text=True,
    )


def test_dry_run_performs_no_write(config_file, tmp_path):
    json_out = tmp_path / "result.json"
    result = run_script(config_file, f"-JsonOutputPath '{json_out}'")
    assert result.returncode == 0, result.stderr
    data = json.loads(json_out.read_text())
    assert data["status"] == "NOT_EXECUTED"


def test_execute_without_confirm_is_rejected_with_evidence(config_file, tmp_path):
    json_out = tmp_path / "result.json"
    result = run_script(config_file, f"-Execute -JsonOutputPath '{json_out}'")
    assert result.returncode != 0
    data = json.loads(json_out.read_text())
    assert data["status"] == "CANCELLED"


def test_missing_backup_file_fails_before_connection(tmp_path):
    cfg = tmp_path / "config.psd1"
    cfg.write_text('@{ SiteUrl = "https://example.sharepoint.com/sites/test"; ClientId = "x"; TenantId = "y" }')
    items_ps1 = "@(@{LocalPath='" + str(tmp_path / "missing.agent") + "'; Url='SitePages/Example/agent.agent'})"
    result = subprocess.run(
        [pwsh, "-NoProfile", "-NonInteractive", "-Command", f"& '{SCRIPT}' -ConfigFile '{cfg}' -Items {items_ps1}"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
