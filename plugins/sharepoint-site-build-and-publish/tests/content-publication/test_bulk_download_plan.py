"""The bulk downloader plans from inventory CSV without any tenant I/O.
Purpose:
    Verify inventory-driven bulk download planning and mocked retrieval behavior without tenant writes.

Key Input Dependencies:
    - The bulk-download PowerShell script, its fixture harness, CSV inventory shape, and pwsh when available.

Function Index:
    test_plan_preserves_duplicate_filenames_and_selects_page_formats, test_live_adapter_is_mocked_and_preserves_bytes_and_identity
"""
import csv
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/content-publication/download-sharepoint-inventory-files.ps1"


# Verify the contract that plan preserves duplicate filenames and selects page formats.
def test_plan_preserves_duplicate_filenames_and_selects_page_formats(tmp_path):
    """Verify the contract that plan preserves duplicate filenames and selects page formats."""
    assert SCRIPT.exists(), "bulk download script is missing"
    config = tmp_path / "profile.psd1"
    config.write_text("@{ SiteUrl='https://example.test'; ClientId='client'; TenantId='tenant' }", encoding="utf-8")
    inventory = tmp_path / "files.csv"
    with inventory.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["FileUrl", "FileName", "FileExtension", "WebUrl", "LibraryTitle", "RelativePath"])
        writer.writeheader()
        for name, folder in [("same.aspx", "one"), ("same.aspx", "two"), ("image.png", "one")]:
            writer.writerow({"FileUrl": f"https://example.test/{folder}/{name}", "FileName": name, "FileExtension": name.split('.')[-1], "WebUrl": f"https://example.test/{folder}", "LibraryTitle": "Docs", "RelativePath": f"{folder}/{name}"})
    output = tmp_path / "downloads"
    result = subprocess.run([shutil.which("pwsh"), "-NoProfile", "-File", str(SCRIPT), "-InventoryCsv", str(inventory), "-ConfigPath", str(config), "-OutputDir", str(output)], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    with (output / "downloads.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert {row["Status"] for row in rows} == {"PLANNED"}
    assert len({row["LocalPath"] for row in rows}) == 2
    assert not any(output.rglob("*.aspx"))


# Verify the contract that live adapter is mocked and preserves bytes and identity.
@pytest.mark.parametrize("platform", ["OnPrem", "Online"])
def test_live_adapter_is_mocked_and_preserves_bytes_and_identity(tmp_path, platform):
    """Verify the contract that live adapter is mocked and preserves bytes and identity."""
    config = tmp_path / "profile.psd1"
    config.write_text("@{ SiteUrl='https://example.test'; ClientId='client'; TenantId='tenant' }", encoding="utf-8")
    inventory = tmp_path / "files.csv"
    inventory.write_text('FileUrl,FileName,FileExtension,WebUrl,LibraryTitle,RelativePath\nhttps://example.test/sub/docs/page.aspx,page.aspx,aspx,https://example.test/sub,Docs,sub/docs/page.aspx\n', encoding="utf-8")
    output = tmp_path / "downloads"
    harness = Path(__file__).parent / "fixtures/bulk-download-mocks.ps1"
    result = subprocess.run([shutil.which("pwsh"), "-NoProfile", "-File", str(harness), "-Script", str(SCRIPT),
                             "-InventoryCsv", str(inventory), "-ConfigPath", str(config), "-OutputDir", str(output),
                             "-Platform", platform], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "DOWNLOADED" in (output / "downloads.csv").read_text(encoding="utf-8-sig")
    assert len(list(output.rglob("*.aspx"))) == 1
