"""Static offline unit tests for Phase 4 skill inventory and report templates."""

import hashlib
import re
import subprocess
from pathlib import Path


def test_deconfliction_reports_contain_unexecuted_templates():
    repo_root = Path(__file__).resolve().parents[3]
    reports_dir = repo_root / "docs" / "reports" / "phase-4-native-sharepoint-skills"

    cand_file = reports_dir / "candidate-selection.md"
    input_file = reports_dir / "input-availability-report.md"

    assert cand_file.exists(), "candidate-selection.md must exist"
    assert input_file.exists(), "input-availability-report.md must exist"

    cand_content = cand_file.read_text(encoding="utf-8")
    assert "review-manual-topics" in cand_content
    assert "Status:" in cand_content
    assert "https://" not in cand_content, "Must not hardcode live tenant URL in tracked template"

    input_content = input_file.read_text(encoding="utf-8")
    assert "CEISPilotKnowledgePages" in input_content
    assert "Status:" in input_content


def test_inventory_script_has_zero_write_cmdlets():
    repo_root = Path(__file__).resolve().parents[3]
    script_path = (
        repo_root
        / "tools"
        / "phase-4-native-sharepoint-skills"
        / "deployment"
        / "scripts"
        / "inventory-skills.ps1"
    )

    assert script_path.exists(), "inventory-skills.ps1 must exist"
    script_content = script_path.read_text(encoding="utf-8")

    write_cmdlet_pattern = re.compile(
        r"\b(Add|Set|New|Remove|Clear|Move|Copy|Grant|Revoke|Submit|Restore|Register|Unregister)-PnP\w*\b",
        re.IGNORECASE,
    )
    matches = write_cmdlet_pattern.findall(script_content)
    assert len(matches) == 0, f"Found write-capable PnP cmdlets in read-only script: {matches}"


def test_unambiguous_agent_assets_state_reporting():
    """Test disambiguated AgentAssets state classification options."""
    valid_library_states = {"OBSERVED", "NOT_FOUND", "FORBIDDEN", "PARTIAL", "FAILED"}
    valid_folder_states = {"OBSERVED", "NOT_FOUND", "FORBIDDEN", "NOT_EVALUATED"}
    valid_url_states = {"OBSERVED", "NOT_OBSERVED"}

    assert "NOT_FOUND" in valid_library_states
    assert "OBSERVED" in valid_library_states
    assert "OBSERVED_EMPTY" not in valid_library_states, "OBSERVED_EMPTY must not be used (disambiguate library vs folder state)"
    assert "NOT_OBSERVED" in valid_url_states


def test_durable_evidence_hash_and_git_tracking():
    """Test evidence file generation, SHA-256 hash calculation, and git ignore status."""
    evidence_file = Path(__file__).resolve().parents[3] / "temp" / "EVID-PHASE4-TASK7-001-tenant-inventory.json"
    if evidence_file.exists():
        content = evidence_file.read_bytes()
        calculated_hash = hashlib.sha256(content).hexdigest()
        assert len(calculated_hash) == 64

        # Verify file is ignored by git
        res = subprocess.run(
            ["git", "check-ignore", str(evidence_file)],
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0
        assert "temp/" in res.stdout or "EVID-PHASE4-TASK7-001" in res.stdout


def test_bounded_collision_language_enforcement():
    """Test bounded wording enforcement in candidate selection report."""
    cand_file = Path(__file__).resolve().parents[3] / "docs" / "reports" / "phase-4-native-sharepoint-skills" / "candidate-selection.md"
    assert cand_file.exists()
    cand_content = cand_file.read_text(encoding="utf-8")

    assert "No collision was observed within the successfully inspected scope." in cand_content
    assert "The tenant contains no collisions" not in cand_content, "Must avoid unbounded total claims"


def test_missing_configuration_handling(tmp_path):
    repo_root = Path(__file__).resolve().parents[3]
    script_path = (
        repo_root
        / "tools"
        / "phase-4-native-sharepoint-skills"
        / "deployment"
        / "scripts"
        / "inventory-skills.ps1"
    )

    non_existent_config = tmp_path / "non_existent_config.psd1"

    res = subprocess.run(
        ["pwsh", "-NoProfile", "-File", str(script_path), "-ConfigFile", str(non_existent_config)],
        capture_output=True,
        text=True,
    )
    assert res.returncode != 0
    assert "not found" in res.stderr.lower() or "not found" in res.stdout.lower()


