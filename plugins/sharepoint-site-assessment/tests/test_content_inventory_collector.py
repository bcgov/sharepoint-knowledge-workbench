"""Exercise the collector with mocked PnP and paginated on-prem REST responses."""

import csv
import json
import shutil
import subprocess
from pathlib import Path

import pytest


PLUGIN = Path(__file__).resolve().parents[1]
COLLECTOR = PLUGIN / "scripts" / "collect-sharepoint-content-inventory.ps1"
HARNESS = Path(__file__).parent / "fixtures" / "content-inventory-mocks.ps1"


def collect(tmp_path, platform, scenario="complete"):
    assert COLLECTOR.is_file(), "recursive content collector is missing"
    pwsh = shutil.which("pwsh")
    if not pwsh:
        pytest.skip("PowerShell is required for collector integration tests")
    output = tmp_path / "inventory"
    result = subprocess.run(
        [pwsh, "-NoProfile", "-File", str(HARNESS), "-Collector", str(COLLECTOR),
         "-OutputDir", str(output), "-Platform", platform, "-Scenario", scenario],
        capture_output=True, text=True, timeout=60,
    )
    assert (output / "manifest.json").exists(), result.stdout + result.stderr
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8-sig"))
    with (output / "files.csv").open(encoding="utf-8-sig", newline="") as handle:
        files = list(csv.DictReader(handle))
    with (output / "libraries.csv").open(encoding="utf-8-sig", newline="") as handle:
        libraries = list(csv.DictReader(handle))
    return result, manifest, files, libraries, output


@pytest.mark.parametrize("platform", ["Online", "OnPrem"])
def test_all_webs_files_and_empty_hidden_libraries(tmp_path, platform):
    result, manifest, files, libraries, _ = collect(tmp_path, platform)
    assert result.returncode == 0, result.stdout + result.stderr
    assert manifest["Status"] == "COMPLETE"
    assert manifest["WebCount"] == 3
    assert len(libraries) == 5  # document, hidden asset, empty and descendant libraries
    assert any(row["FileCount"] == "0" for row in libraries)
    assert {row["FileName"] for row in files} == {
        "manual.docx", "photo.PNG", "logo.svg", "news.aspx", "default.aspx"
    }
    photo = next(row for row in files if row["FileName"] == "photo.PNG")
    assert photo["SourceSiteUrl"] == "https://example.test/sites/root"
    assert photo["SourceSiteName"] == "Root"
    assert photo["WebTitle"] == "Child"
    assert photo["RelativePath"] == "child/Documents/deep/photo.PNG"
    assert photo["FileExtension"] == "png"
    assert photo["SizeBytes"] == "20"
    assert photo["LibraryTitle"] == "Documents"
    assert photo["ContainerType"] == "DocumentLibrary"
    assert photo["LibraryRelativePath"] == "deep/photo.PNG"
    assert next(row for row in files if row["FileName"] == "logo.svg")["ContainerType"] == "AssetLibrary"
    assert all(row["FileName"] != "folder" for row in files)


@pytest.mark.parametrize("platform", ["Online", "OnPrem"])
@pytest.mark.parametrize("scenario", ["library-denied", "subsites-denied"])
def test_failures_are_reported_as_partial(tmp_path, platform, scenario):
    result, manifest, files, _, output = collect(tmp_path, platform, scenario)
    assert result.returncode != 0
    assert manifest["Status"] == "PARTIAL"
    assert manifest["ErrorCount"] >= 1
    assert files  # successful locations are preserved
    assert "denied" in (output / "errors.csv").read_text(encoding="utf-8-sig")


def test_late_rest_page_failure_preserves_earlier_files(tmp_path):
    result, manifest, files, _, _ = collect(tmp_path, "OnPrem", "page-denied")
    assert result.returncode != 0
    assert manifest["Status"] == "PARTIAL"
    assert "manual.docx" in {row["FileName"] for row in files}


def test_auth_denial_is_actionable_and_failed(tmp_path):
    result, manifest, files, libraries, output = collect(tmp_path, "OnPrem", "unauthorized")
    assert result.returncode != 0
    assert manifest["Status"] == "FAILED"
    assert files == libraries == []
    error = (output / "errors.csv").read_text(encoding="utf-8-sig")
    assert "401" in error
    assert "prompt" in error


@pytest.mark.parametrize("platform", ["Online", "OnPrem"])
def test_empty_inventory_keeps_csv_headers(tmp_path, platform):
    result, manifest, files, libraries, output = collect(tmp_path, platform, "empty")
    assert result.returncode == 0, result.stdout + result.stderr
    assert manifest["Status"] == "EMPTY"
    assert files == libraries == []
    assert "FileName" in (output / "files.csv").read_text(encoding="utf-8-sig")


def test_skill_routes_content_inventory_and_link_is_registered():
    skill = PLUGIN / "skills" / "sharepoint-collect-site-inventory"
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    description = text.split("description:", 1)[1].split("allowed-tools:", 1)[0]
    for term in ("documents", "images", "subsites"):
        assert term in description
    link = skill / "scripts" / COLLECTOR.name
    assert link.is_symlink()
    assert link.resolve() == COLLECTOR.resolve()
    manifest = json.loads((PLUGIN.parents[1] / "symlinks.json").read_text(encoding="utf-8"))
    assert any(entry["dst"].endswith("sharepoint-collect-site-inventory/scripts/" + COLLECTOR.name)
               for entry in manifest["links"])


@pytest.mark.parametrize("target,expected", [
    ("https://tenant.sharepoint.com/sites/root", "Online"),
    ("https://example.test/sites/root", "OnPrem"),
    ("https://sharepoint.com.example.test/sites/root", "OnPrem"),
])
@pytest.mark.parametrize("override", [False, True])
def test_auto_detection_config_and_target_override(tmp_path, target, expected, override):
    config = tmp_path / "profile.psd1"
    configured_url = "https://unused.test/sites/root" if override else target
    config.write_text(
        "@{ SiteUrl = '" + configured_url + "'; ClientId = 'mock-client'; TenantId = 'mock-tenant' }",
        encoding="utf-8",
    )
    pwsh = shutil.which("pwsh")
    if not pwsh:
        pytest.skip("PowerShell is required")
    output = tmp_path / "auto"
    command = [pwsh, "-NoProfile", "-File", str(HARNESS), "-Collector", str(COLLECTOR),
               "-OutputDir", str(output), "-Platform", "Auto", "-Scenario", "complete",
               "-ConfigPath", str(config), "-TargetUrl", target]
    if not override:
        command.append("-ConfigOnly")
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8-sig"))
    assert manifest["Platform"] == expected
    assert manifest["SourceSiteUrl"] == target
    assert manifest["WebCount"] == 3
