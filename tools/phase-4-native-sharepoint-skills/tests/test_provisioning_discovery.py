"""Static offline unit tests for Phase 4 native skill store provisioning discovery."""

import pytest
from pathlib import Path


def test_site_comparison_parameters_and_vocabularies():
    """Test required vocabularies and site comparison parameters in provisioning report."""
    repo_root = Path(__file__).resolve().parents[3]
    report_file = (
        repo_root
        / "docs"
        / "reports"
        / "phase-4-native-sharepoint-skills"
        / "native-skill-store-provisioning-report.md"
    )

    assert report_file.exists(), "native-skill-store-provisioning-report.md must exist"
    content = report_file.read_text(encoding="utf-8")

    # Verify site comparison URLs
    assert "AG-CSB-intranet-dev" in content
    assert "AG-CSB-ITAU-CMAT-DEV" in content

    # Verify required vocabularies
    vocabularies = [
        "OBSERVED",
        "ADMIN_CONFIRMED",
        "DOCUMENTED",
        "NOT_OBSERVED",
        "FORBIDDEN",
    ]
    for vocab in vocabularies:
        assert vocab in content, f"Vocabulary {vocab} missing from report"

    # Verify outcome classification language
    assert "Outcome C" in content or "PHASE_4_ENTRY_GATE_NOT_MET" in content


def test_corrected_evaluation_reference_statement():
    """Test corrected evaluation reference statement in report files."""
    repo_root = Path(__file__).resolve().parents[3]
    reports_dir = repo_root / "docs" / "reports" / "phase-4-native-sharepoint-skills"

    expected_statement = (
        "All positive and permission evaluation references expected to exist were observed. "
        "NEG-01 intentionally references a missing/invalid topic as its negative control."
    )

    input_file = reports_dir / "input-availability-report.md"
    cand_file = reports_dir / "candidate-selection.md"
    prov_file = reports_dir / "native-skill-store-provisioning-report.md"

    assert expected_statement in input_file.read_text(encoding="utf-8")
    assert expected_statement in cand_file.read_text(encoding="utf-8")
    assert expected_statement in prov_file.read_text(encoding="utf-8")
