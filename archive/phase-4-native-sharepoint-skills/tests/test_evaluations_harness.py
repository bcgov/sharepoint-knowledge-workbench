"""
Unit tests for Phase 4 Evaluation Cases and Harness.
"""
import json
from pathlib import Path
import importlib.util

spec_path = Path(__file__).resolve().parents[1] / "evaluations" / "validate_cases.py"
spec = importlib.util.spec_from_file_location("validate_cases", spec_path)
validate_cases = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_cases)


def test_all_11_evaluation_cases_match_schema():
    repo_root = Path(__file__).resolve().parents[3]
    eval_dir = repo_root / "tools" / "phase-4-native-sharepoint-skills" / "evaluations"

    case_files = list(eval_dir.glob("*/*.json"))
    assert len(case_files) >= 11, f"Must have at least 11 evaluation cases, found {len(case_files)}"

    for case_file in case_files:
        with open(case_file, "r", encoding="utf-8") as f:
            case_data = json.load(f)
        assert validate_cases.validate_case_definition(case_data), f"Case {case_file} failed validation"


def test_evaluation_case_categories_and_counts():
    repo_root = Path(__file__).resolve().parents[3]
    eval_dir = repo_root / "tools" / "phase-4-native-sharepoint-skills" / "evaluations"

    categories = ["normal", "negative", "ambiguous", "permission", "safety"]
    for cat in categories:
        cat_files = list((eval_dir / cat).glob("*.json"))
        assert len(cat_files) >= 1, f"Category {cat} must have at least 1 case file"


def test_synthetic_injection_fixture_exists():
    repo_root = Path(__file__).resolve().parents[3]
    fixture_path = (
        repo_root
        / "tools"
        / "phase-4-native-sharepoint-skills"
        / "fixtures"
        / "sanitized"
        / "synthetic-injection-topic.html"
    )
    assert fixture_path.is_file(), f"Synthetic injection fixture missing at {fixture_path}"
    content = fixture_path.read_text(encoding="utf-8")
    assert "Ignore the review skill" in content or "ATTENTION ASSISTANT" in content


def test_unexecuted_report_templates_exist():
    repo_root = Path(__file__).resolve().parents[3]
    reports_dir = repo_root / "docs" / "reports" / "phase-4-native-sharepoint-skills"

    summary_file = reports_dir / "evaluation-summary.md"
    perm_file = reports_dir / "permission-and-safety-summary.md"

    assert summary_file.is_file(), "evaluation-summary.md missing"
    assert perm_file.is_file(), "permission-and-safety-summary.md missing"

    assert "Status: NOT_EXECUTED" in summary_file.read_text(encoding="utf-8")
    assert "Status: NOT_EXECUTED" in perm_file.read_text(encoding="utf-8")


def test_currency_category_is_accepted_by_schema():
    case = {
        "case_id": "CUR-00-SCHEMA-CHECK",
        "category": "currency",
        "objective": "Schema smoke test only.",
        "primary_topic": "initiate-a-file",
        "related_topic_allowance": 0,
        "test_identity_class": "INTENDED_READER",
        "prompt": "Schema smoke test prompt.",
        "run_count": 1,
        "expected_semantic_behaviours": ["Placeholder behaviour for schema smoke test."],
        "prohibited_behaviours": ["Placeholder prohibition for schema smoke test."],
    }
    assert validate_cases.validate_case_definition(case)
