"""
test_phase4_exit_gate.py

Unit test for Phase 4 evidence report existence.

Note: this test originally asserted every listed report still contained
"NOT_EXECUTED"/"NOT_RECORDED"/"PENDING" — i.e. it validated the pre-execution baseline, not a
passed/accepted result. That made it impossible to ever pass once Phase 4 was actually executed.
Fixed 2026-08-01 during Phase 4.5 entry-gate reconciliation (see start-here.md) to just check the
required report files exist; per-criterion pass/waive status is asserted in
phase-4-exit-gate-evidence.md itself, reviewed by a human, not re-derived by string-matching here.
"""

from pathlib import Path

def test_phase4_evidence_reports_exist():
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
        "phase-4-exit-gate-evidence.md",
        "EVID-PHASE4-TASK12-ROLLBACK-COMPLETION.md",
    ]

    for report in required_reports:
        file_path = reports_dir / report
        assert file_path.exists(), f"Required report {report} is missing"
        assert file_path.read_text(encoding="utf-8").strip(), f"Required report {report} is empty"
