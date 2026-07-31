"""Static offline unit tests for Phase 4 skill inventory and report templates."""

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
