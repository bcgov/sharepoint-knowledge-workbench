"""Purpose:
    Exercise strict-mode parsing of flat, nested, and minimal PowerShell configuration profiles.

Key Input Dependencies:
    - scripts/Get-WorkbenchConnectionConfig.ps1
    - tests/fixtures/read-config-strict.ps1
    - PowerShell (pwsh) when available.

Verify flat, nested and minimal profiles in strict-mode PowerShell callers.

Function Index:
    - test_optional_config_sections_under_strict_mode
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest


PLUGIN = Path(__file__).resolve().parents[1]


# Verify that optional config sections under strict mode.
@pytest.mark.parametrize("content,mode,client", [
    ("@{ SiteUrl='https://example.test'; ClientId='client'; TenantId='tenant' }", "Interactive", "client"),
    ("@{ SiteUrl='https://example.test' }", "Interactive", None),
    ("@{ Connection=@{ SiteUrl='https://example.test'; ClientId='client'; TenantId='tenant'; AuthenticationMode='DeviceCode' } }", "DeviceCode", "client"),
    ("@{ Connection=@{ SiteUrl='https://example.test' }; Authentication=@{ TenantAdminUrl='https://admin.example.test'; CertificateThumbprint='test-thumbprint' }; AuthenticationMode='Certificate' }", "Certificate", None),
])
def test_optional_config_sections_under_strict_mode(tmp_path, content, mode, client):
    """Verify that optional config sections under strict mode."""
    pwsh = shutil.which("pwsh")
    if not pwsh:
        pytest.skip("PowerShell is required")
    config = tmp_path / "profile.psd1"
    config.write_text(content, encoding="utf-8")
    result = subprocess.run(
        [pwsh, "-NoProfile", "-File", str(PLUGIN / "tests/fixtures/read-config-strict.ps1"),
         "-Helper", str(PLUGIN / "scripts/Get-WorkbenchConnectionConfig.ps1"),
         "-ConfigPath", str(config)], capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr
    resolved = json.loads(result.stdout)
    assert resolved["SiteUrl"] == "https://example.test"
    assert resolved["ClientId"] == client
    assert resolved["AuthenticationMode"] == mode
    if mode == "Certificate":
        assert resolved["CertificateThumbprint"] == "test-thumbprint"
        assert resolved["TenantAdminUrl"] == "https://admin.example.test"
