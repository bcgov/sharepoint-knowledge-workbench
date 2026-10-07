"""The bulk downloader and the Markdown uploader report start time, end time and total runtime.
Purpose:
    Verify both scripts print Started/Finished/Elapsed on the console without changing the uploader's
    JSON stdout contract, in default dry-run mode (no tenant I/O).

Key Input Dependencies:
    - download-sharepoint-inventory-files.ps1, spo-upload-file.ps1, and pwsh when available.

Function Index:
    test_downloader_reports_start_end_and_elapsed, test_uploader_reports_runtime_on_stderr_and_keeps_json_stdout,
    test_uploader_reports_runtime_even_when_the_plan_is_invalid
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts/content-publication"
DOWNLOADER = SCRIPTS / "download-sharepoint-inventory-files.ps1"
UPLOADER = SCRIPTS / "spo-upload-file.ps1"
requires_pwsh = pytest.mark.skipif(shutil.which("pwsh") is None, reason="pwsh is not installed")
STAMP = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"


# Write the minimal flat config the dry-run scripts accept.
def _config(tmp_path):
    """Write a minimal config.psd1 for dry-run invocations."""
    config = tmp_path / "config.psd1"
    config.write_text(
        "@{ Connection = @{ SiteUrl = 'https://example.invalid/sites/t'; ClientId = 'c'; TenantId = 't' }; "
        "Authentication = @{ TenantAdminUrl = 'https://example-admin.invalid' } }", encoding="utf-8")
    return config


# Assert the three runtime lines appear with timestamps and an elapsed value.
def _assert_runtime_lines(text):
    """Assert Started, Finished and Elapsed lines are present in text."""
    assert re.search(rf"Started:\s+{STAMP}", text), text
    assert re.search(rf"Finished:\s+{STAMP}", text), text
    assert re.search(r"Elapsed:\s+\d{2}:\d{2}:\d{2}", text), text


# Verify the downloader prints its runtime in dry-run mode.
@requires_pwsh
def test_downloader_reports_start_end_and_elapsed(tmp_path):
    """Verify the downloader prints Started/Finished/Elapsed."""
    inventory = tmp_path / "files.csv"
    inventory.write_text(
        "FileUrl,FileName,FileExtension,WebUrl,LibraryTitle,RelativePath\n"
        "https://example.test/sub/docs/page.aspx,page.aspx,aspx,https://example.test/sub,Docs,sub/docs/page.aspx\n",
        encoding="utf-8")
    result = subprocess.run(
        ["pwsh", "-NoProfile", "-File", str(DOWNLOADER), "-InventoryCsv", str(inventory),
         "-ConfigPath", str(_config(tmp_path)), "-OutputDir", str(tmp_path / "dl")],
        capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    _assert_runtime_lines(result.stdout + result.stderr)


# Verify the uploader prints runtime on stderr and leaves stdout as pure JSON.
@requires_pwsh
def test_uploader_reports_runtime_on_stderr_and_keeps_json_stdout(tmp_path):
    """Verify stderr carries Started/Finished/Elapsed and stdout is still valid JSON."""
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"document_id": "d", "actions": [{
        "source_path": str(tmp_path / "a.pdf"), "target_library": "Lib",
        "target_folder": "f", "target_filename": "a.pdf"}]}), encoding="utf-8")
    result = subprocess.run(
        ["pwsh", "-NoProfile", "-File", str(UPLOADER), "-PlanPath", str(plan), "-ConfigPath", str(_config(tmp_path))],
        capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["document_id"] == "d"
    _assert_runtime_lines(result.stderr)


# Verify the uploader still reports runtime when it fails before doing any work.
@requires_pwsh
def test_uploader_reports_runtime_even_when_the_plan_is_invalid(tmp_path):
    """Verify Finished/Elapsed are printed when the script throws."""
    result = subprocess.run(
        ["pwsh", "-NoProfile", "-File", str(UPLOADER), "-PlanPath", str(tmp_path / "missing.json"),
         "-ConfigPath", str(_config(tmp_path))],
        capture_output=True, text=True, timeout=60)
    assert result.returncode != 0
    _assert_runtime_lines(result.stderr)
