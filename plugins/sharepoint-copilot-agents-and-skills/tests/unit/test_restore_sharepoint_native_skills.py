"""
Executable tests for restore-sharepoint-native-skills.ps1's safety gates. Only
exercises the dry-run and confirmation-rejection paths, which perform zero
tenant I/O -- no PnP connection is attempted in either case.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "restore-sharepoint-native-skills.ps1"

pwsh = shutil.which("pwsh")
pytestmark = pytest.mark.skipif(pwsh is None, reason="pwsh not installed")


def run_script(config_file: Path, args: list[str]) -> subprocess.CompletedProcess:
    items_ps1 = "@(@{LocalPath='" + str(config_file.parent / "backup.md") + "'; Url='AgentAssets/Skills/example/SKILL.md'})"
    return subprocess.run(
        [
            pwsh, "-NoProfile", "-NonInteractive", "-Command",
            f"& '{SCRIPT}' -ConfigFile '{config_file}' -Items {items_ps1} " + " ".join(args),
        ],
        capture_output=True,
        text=True,
    )


@pytest.fixture()
def config_file(tmp_path):
    cfg = tmp_path / "config.psd1"
    cfg.write_text('@{ SiteUrl = "https://example.sharepoint.com/sites/test"; ClientId = "x"; TenantId = "y" }')
    (tmp_path / "backup.md").write_text("backed up content")
    return cfg


def test_dry_run_performs_no_write_and_exits_zero(config_file, tmp_path):
    json_out = tmp_path / "result.json"
    result = run_script(config_file, [f"-JsonOutputPath '{json_out}'"])
    assert result.returncode == 0, result.stderr
    data = json.loads(json_out.read_text())
    assert data["status"] == "NOT_EXECUTED"
    assert data["mode"] == "DRY_RUN_PREFLIGHT"


def test_execute_without_confirm_string_is_rejected(config_file, tmp_path):
    json_out = tmp_path / "result.json"
    result = run_script(config_file, ["-Execute", f"-JsonOutputPath '{json_out}'"])
    assert result.returncode != 0
    data = json.loads(json_out.read_text())
    assert data["status"] == "CANCELLED"


def test_execute_with_wrong_confirm_string_is_rejected(config_file, tmp_path):
    result = run_script(config_file, ["-Execute", "-ConfirmExactTarget", "'wrong-string'"])
    assert result.returncode != 0


def test_missing_backup_file_fails_before_any_connection_attempt(tmp_path):
    cfg = tmp_path / "config.psd1"
    cfg.write_text('@{ SiteUrl = "https://example.sharepoint.com/sites/test"; ClientId = "x"; TenantId = "y" }')
    items_ps1 = "@(@{LocalPath='" + str(tmp_path / "does-not-exist.md") + "'; Url='AgentAssets/Skills/example/SKILL.md'})"
    result = subprocess.run(
        [pwsh, "-NoProfile", "-NonInteractive", "-Command", f"& '{SCRIPT}' -ConfigFile '{cfg}' -Items {items_ps1}"],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "not found" in (result.stderr + result.stdout).lower()
