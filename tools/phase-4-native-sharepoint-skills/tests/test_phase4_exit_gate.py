"""
test_phase4_exit_gate.py

Unit test for Phase 4 evidence template existence and unexecuted baseline validation.
"""

from pathlib import Path
import pytest

def test_phase4_evidence_templates_exist_before_execution():
    repo_root = Path(__file__).resolve().parents[3]
    reports_dir = repo_root / "docs" / "reports" / "phase-4-native-sharepoint-skills"
    
    required_reports = [
        "candidate-selection.md",
        "input-availability-report.md",
        "metadata-visibility-report.md",
        "deployment-summary.md",
        "evaluation-summary.md",
        "permission-and-safety-summary.md",
        "skill-lifecycle-summary.md",
        "phase-4-exit-gate-evidence.md"
    ]
    
    for report in required_reports:
        file_path = reports_dir / report
        assert file_path.exists(), f"Required report {report} is missing"
        content = file_path.read_text(encoding="utf-8")
        assert "Status: NOT_EXECUTED" in content or "Actual result: NOT_RECORDED" in content or "PENDING" in content
