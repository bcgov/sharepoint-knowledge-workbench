"""Tests that download-sharepoint-inventory-files.ps1 signs in once per web for Online downloads.

Runs the real bulk script in pwsh with stubbed PnP cmdlets (no tenant access) and
counts Connect-PnPOnline calls. Before the fix, spo-download-file.ps1 connected and
disconnected for every file, prompting the user once per file.

Key Input Dependencies: managing-sharepoint-lists-and-libraries/scripts/download-sharepoint-inventory-files.ps1,
spo-download-file.ps1, Get-WorkbenchConnectionConfig.ps1.
"""
import csv
import shutil
import subprocess
from pathlib import Path

import pytest

PLUGIN = Path(__file__).resolve().parents[1]
SKILLS_DIR = PLUGIN / ".apm" / "skills" if (PLUGIN / ".apm" / "skills").exists() else PLUGIN / "skills"
SCRIPT = SKILLS_DIR / "managing-sharepoint-lists-and-libraries" / "scripts" / "download-sharepoint-inventory-files.ps1"
PWSH = shutil.which("pwsh")
TENANT = "https://contoso.sharepoint.com"

STUBS = r"""
$global:ConnectCount = 0
$global:DisconnectCount = 0
function global:Connect-PnPOnline { param([string]$Url, [string]$ClientId, [string]$Tenant, [switch]$Interactive, [string]$TenantAdminUrl, [switch]$ReturnConnection)
    $global:ConnectCount++; [pscustomobject]@{ Url = $Url } }
function global:Disconnect-PnPOnline { param([object]$Connection) $global:DisconnectCount++ }
function global:Get-PnPFile { param([string]$Url, [string]$Path, [string]$FileName, [switch]$AsFile, [switch]$Force, [object]$Connection)
    if (-not $Connection) { throw 'Get-PnPFile called without the shared -Connection.' }
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $Path $FileName) -Value $Url }
"""


def _write_inputs(tmp_path, webs):
    config = tmp_path / "config.psd1"
    config.write_text(
        "@{ Connection = @{ SiteUrl = '%s/sites/A'; ClientId = '00000000-0000-0000-0000-000000000001'; "
        "TenantId = '00000000-0000-0000-0000-000000000002' } }" % TENANT,
        encoding="utf-8",
    )
    inventory = tmp_path / "files.csv"
    with inventory.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["FileUrl", "WebUrl", "LibraryTitle", "FileName", "FileExtension", "RelativePath"])
        writer.writeheader()
        for web, count in webs:
            for index in range(count):
                name = f"doc{index}.pdf"
                writer.writerow({"FileUrl": f"{TENANT}{web}/Docs/{name}", "WebUrl": f"{TENANT}{web}",
                                 "LibraryTitle": "Docs", "FileName": name, "FileExtension": "pdf",
                                 "RelativePath": f"Docs/{name}"})
    return config, inventory


def _run(tmp_path, webs, stubs=STUBS):
    config, inventory = _write_inputs(tmp_path, webs)
    out = tmp_path / "out"
    command = (
        stubs
        + f"try {{ & '{SCRIPT}' -InventoryCsv '{inventory}' -ConfigPath '{config}' -OutputDir '{out}' "
        "-Extensions pdf -Platform Online -Execute -ConfirmToken DOWNLOAD-SHAREPOINT-INVENTORY-FILES | Out-Null } "
        "catch { Write-Output \"ERROR=$($_.Exception.Message)\" }; "
        "Write-Output \"CONNECTS=$global:ConnectCount DISCONNECTS=$global:DisconnectCount\""
    )
    result = subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-Command", command],
                            capture_output=True, text=True, timeout=120)
    rows = list(csv.DictReader((out / "downloads.csv").open(encoding="utf-8"))) if (out / "downloads.csv").exists() else []
    return result, rows


@pytest.mark.skipif(PWSH is None, reason="pwsh is required")
def test_online_bulk_download_connects_once_for_one_web(tmp_path):
    result, rows = _run(tmp_path, [("/sites/A", 3)])
    assert "CONNECTS=1 DISCONNECTS=1" in result.stdout, result.stdout + result.stderr
    assert [r["Status"] for r in rows] == ["DOWNLOADED"] * 3
    assert all(Path(r["LocalPath"]).exists() for r in rows)


@pytest.mark.skipif(PWSH is None, reason="pwsh is required")
def test_online_bulk_download_connects_once_per_distinct_web(tmp_path):
    result, rows = _run(tmp_path, [("/sites/A", 2), ("/sites/A/sub", 2)])
    assert "CONNECTS=2 DISCONNECTS=2" in result.stdout, result.stdout + result.stderr
    assert [r["Status"] for r in rows] == ["DOWNLOADED"] * 4


@pytest.mark.skipif(PWSH is None, reason="pwsh is required")
def test_failed_sign_in_stops_without_prompting_per_file(tmp_path):
    failing = STUBS + "function global:Connect-PnPOnline { $global:ConnectCount++; throw 'AADSTS50126: sign-in cancelled' }\n"
    result, rows = _run(tmp_path, [("/sites/A", 3)], failing)
    assert "CONNECTS=1 " in result.stdout, result.stdout + result.stderr
    assert [r["Status"] for r in rows] == ["FAILED", "NOT_ATTEMPTED", "NOT_ATTEMPTED"]
