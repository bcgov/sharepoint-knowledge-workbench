"""Contract tests for the standalone SharePoint document-library folder creator.

Purpose:
    Verify spo-create-folder.ps1 is dry-run by default, plans library verification and parent-first folder creation,
    and refuses a real write without its confirmation token before any tenant I/O.

Key Input Dependencies:
    - scripts/content-publication/spo-create-folder.ps1 and pwsh.

Function Index:
    _run, test_dry_run_plans_library_check_and_parent_first_folders, test_execute_requires_confirm_token,
    test_rejects_traversal_in_folder_path, test_skill_scripts_folder_exposes_the_script
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parents[3]
SCRIPT = PACKAGE / "scripts" / "content-publication" / "spo-create-folder.ps1"
SKILL_LINK = PACKAGE / "skills" / "sharepoint-create-document-library" / "scripts" / "spo-create-folder.ps1"
requires_pwsh = pytest.mark.skipif(shutil.which("pwsh") is None, reason="pwsh not installed")


# Run the folder creator with a throwaway config and return the completed process.
def _run(tmp_path, *extra):
    """Run the folder creator with a throwaway config and return the completed process."""
    config = tmp_path / "config.psd1"
    config.write_text(
        "@{ Connection = @{ SiteUrl = 'https://example.invalid/sites/t'; ClientId = 'c'; TenantId = 't' } }",
        encoding="utf-8")
    return subprocess.run(
        ["pwsh", "-NoProfile", "-File", str(SCRIPT), "-ConfigPath", str(config), *extra],
        capture_output=True, text=True, timeout=120,
    )


# Verify the dry run lists library verification and each folder segment, parent first, without writing.
@requires_pwsh
def test_dry_run_plans_library_check_and_parent_first_folders(tmp_path):
    """Verify the dry run lists library verification and each folder segment, parent first, without writing."""
    result = _run(tmp_path, "-LibraryName", "sheriff", "-FolderPath", "administrative documents/awards")
    assert result.returncode == 0, result.stderr
    summary = json.loads(result.stdout)
    assert summary["dry_run"] is True
    assert summary["library"] == "sheriff"
    assert summary["verify_library"].startswith("Get-PnPList")
    assert [f["folder"] for f in summary["folders"]] == [
        "sheriff/administrative documents",
        "sheriff/administrative documents/awards",
    ]


# Verify a real write without the exact token is refused.
@requires_pwsh
def test_execute_requires_confirm_token(tmp_path):
    """Verify a real write without the exact token is refused."""
    result = _run(tmp_path, "-LibraryName", "sheriff", "-FolderPath", "a", "-Execute", "-ConfirmToken", "WRONG")
    assert result.returncode != 0
    assert "CREATE-SPO-FOLDER" in result.stderr


# Verify path traversal and empty segments are refused before any planning.
@requires_pwsh
def test_rejects_traversal_in_folder_path(tmp_path):
    """Verify path traversal and empty segments are refused before any planning."""
    result = _run(tmp_path, "-LibraryName", "sheriff", "-FolderPath", "a/../b")
    assert result.returncode != 0
    assert "Invalid folder path" in result.stderr


# Verify the skill-facing script is a file-level symlink to the canonical script.
def test_skill_scripts_folder_exposes_the_script():
    """Verify the skill-facing script is a file-level symlink to the canonical script."""
    assert SKILL_LINK.exists()
    assert SKILL_LINK.resolve() == SCRIPT.resolve()
