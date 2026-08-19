import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wave1_test_ownership import owner_domain_for, fill_ledger, DOMAINS, FILE_OWNER_DOMAIN


def test_split_file_strategy_test_goes_to_knowledge_analysis():
    assert (
        owner_domain_for("tests/unit/test_analyze_structure.py", "test_small_single_recommends_single_strategy")
        == "KNOWLEDGE_ANALYSIS"
    )


def test_split_file_extraction_test_goes_to_source_document_extraction():
    assert (
        owner_domain_for("tests/unit/test_analyze_structure.py", "test_heading_counts_by_level_small_single")
        == "SOURCE_DOCUMENT_EXTRACTION"
    )


def test_non_split_file_uses_file_level_mapping():
    assert owner_domain_for("tests/unit/test_chunking.py", "test_anything") == "CANONICAL_KNOWLEDGE"


def test_unmapped_file_raises():
    import pytest

    with pytest.raises(KeyError):
        owner_domain_for("tests/unit/test_does_not_exist.py", "test_x")


def test_every_file_owner_domain_value_is_a_real_or_none_domain():
    for file_name, domain in FILE_OWNER_DOMAIN.items():
        assert domain is None or domain in DOMAINS, f"{file_name}: invalid domain {domain!r}"


def test_fill_ledger_assigns_every_entry_a_real_domain():
    evidence_dir = Path(__file__).resolve().parents[3] / "docs" / "superpowers" / "plans" / "phase-4-5-evidence"
    ledger = json.loads((evidence_dir / "wave-0-test-ledger.json").read_text())
    filled = fill_ledger(ledger)
    assert len(filled["entries"]) == len(ledger["entries"])
    for entry in filled["entries"]:
        assert entry["proposed_owner_domain"] in DOMAINS, entry


def test_fill_ledger_covers_every_test_file_present_in_the_real_ledger():
    evidence_dir = Path(__file__).resolve().parents[3] / "docs" / "superpowers" / "plans" / "phase-4-5-evidence"
    ledger = json.loads((evidence_dir / "wave-0-test-ledger.json").read_text())
    files_in_ledger = {e["file"] for e in ledger["entries"]}
    mapped_files = set(FILE_OWNER_DOMAIN) | {"tests/unit/test_analyze_structure.py"}
    assert files_in_ledger <= mapped_files, files_in_ledger - mapped_files
