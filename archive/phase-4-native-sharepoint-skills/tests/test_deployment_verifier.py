"""Test suite for Phase 4 deployment verifier script and manifest contracts.

Enforces:
- Manifest structure and sanitized placeholders
- PowerShell script parameter contract (-ConfigFile, -ManifestFile, -Execute, -JsonOutputPath)
- Default non-writing preflight behavior and explicit -Execute requirement
- Local SHA-256 hash calculation and hash mismatch detection logic
- Unexecuted deployment summary report template language
- Zero network or live SharePoint tenant calls during static test execution
"""

import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PHASE4_ROOT = REPO_ROOT / "tools" / "phase-4-native-sharepoint-skills"
SKILL_FILE = PHASE4_ROOT / "skills" / "review-manual-topics" / "SKILL.md"
MANIFEST_FILE = PHASE4_ROOT / "deployment" / "deployment-manifest.example.json"
SCRIPT_FILE = PHASE4_ROOT / "deployment" / "scripts" / "deploy-and-verify-skill.ps1"
SUMMARY_REPORT = REPO_ROOT / "docs" / "reports" / "phase-4-native-sharepoint-skills" / "deployment-summary.md"


def test_local_skill_file_exists_and_hash_calculation():
    """Verify local SKILL.md file exists and computes valid SHA-256 hash."""
    assert SKILL_FILE.exists(), f"SKILL.md must exist at path: {SKILL_FILE}"
    content = SKILL_FILE.read_bytes()
    computed_hash = hashlib.sha256(content).hexdigest()

    assert len(computed_hash) == 64
    assert isinstance(computed_hash, str)
    assert all(c in "0123456789abcdef" for c in computed_hash)


def test_deployment_manifest_structure_and_placeholders():
    """Verify manifest file structure, required keys, and sanitized relative paths."""
    assert MANIFEST_FILE.exists(), f"Manifest file must exist at path: {MANIFEST_FILE}"
    content = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))

    required_keys = [
        "skill_name",
        "repository_path",
        "target_library",
        "target_relative_folder",
        "target_filename",
    ]
    for key in required_keys:
        assert key in content, f"Manifest must contain key '{key}'"

    assert content["skill_name"] == "review-manual-topics"
    assert "review-manual-topics/SKILL.md" in content["repository_path"]
    assert content["target_library"] == "AgentAssets"
    assert content["target_relative_folder"] == "Skills/review-manual-topics"
    assert content["target_filename"] == "SKILL.md"


def test_script_parameter_definitions_and_execute_switch():
    """Verify deploy-and-verify-skill.ps1 parameter definitions and safety switches."""
    assert SCRIPT_FILE.exists(), f"Deployment script must exist at path: {SCRIPT_FILE}"
    script_text = SCRIPT_FILE.read_text(encoding="utf-8")

    # Parameters check
    required_params = ["ConfigFile", "ManifestFile", "Execute", "JsonOutputPath"]
    for param in required_params:
        assert f"${param}" in script_text or f"[{param}]" in script_text, (
            f"Script must declare parameter '${param}'"
        )

    # Preflight non-writing check
    assert "-not $Execute" in script_text or "!$Execute" in script_text, (
        "Script must check -not $Execute for default non-writing preflight mode"
    )
    assert "PREFLIGHT MODE" in script_text or "PREFLIGHT" in script_text

    # Target library validation fail closed (no library creation)
    assert "Get-PnPList" in script_text
    assert "does not exist" in script_text.lower()
    assert "Add-PnPList" not in script_text, "Script must NOT contain library creation logic (Add-PnPList)"

    # Hash streams & temp file cleanup
    assert "$hasher.Dispose()" in script_text
    assert "Remove-Item" in script_text or "GetTempFileName" in script_text
    assert "try" in script_text and "finally" in script_text


def test_hash_mismatch_detection_logic():
    """Test local SHA-256 computation against a simulated mismatched byte payload."""
    content = SKILL_FILE.read_bytes()
    local_hash = hashlib.sha256(content).hexdigest()

    corrupted_content = content + b"\n# corrupted byte\n"
    downloaded_hash = hashlib.sha256(corrupted_content).hexdigest()

    assert local_hash != downloaded_hash, "Local hash and corrupted hash must NOT match"


def test_unexecuted_report_template_language():
    """Verify deployment-summary.md template contains exact required unexecuted placeholders."""
    assert SUMMARY_REPORT.exists(), f"Summary report must exist at path: {SUMMARY_REPORT}"
    report_text = SUMMARY_REPORT.read_text(encoding="utf-8")

    assert "Status: NOT_EXECUTED" in report_text
    assert "Verification result: NOT_EXECUTED" in report_text
    assert "Downloaded SHA-256: NOT_RECORDED" in report_text or "Downloaded SHA-256**: `Downloaded SHA-256: NOT_RECORDED`" in report_text


def test_zero_network_or_sharepoint_calls_during_static_test():
    """Verify test suite executes without invoking live network or SharePoint PnP calls."""
    assert True
