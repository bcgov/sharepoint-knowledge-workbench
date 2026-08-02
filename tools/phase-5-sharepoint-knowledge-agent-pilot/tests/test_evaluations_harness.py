"""
Unit tests for Phase 5 Evaluation Cases and Harness.
"""
import json
from pathlib import Path
import importlib.util

spec_path = Path(__file__).resolve().parents[1] / "evaluations" / "validate_cases.py"
spec = importlib.util.spec_from_file_location("validate_cases", spec_path)
validate_cases = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_cases)


def test_shared_schema_path_resolves_to_phase4_schema_file():
    assert validate_cases.SHARED_SCHEMA_PATH.name == "evaluation-case-schema.json"
    assert validate_cases.SHARED_SCHEMA_PATH.is_file(), (
        f"Expected shared schema at {validate_cases.SHARED_SCHEMA_PATH}"
    )


def test_at_least_one_case_per_in_scope_category():
    repo_root = Path(__file__).resolve().parents[3]
    eval_dir = repo_root / "tools" / "phase-5-sharepoint-knowledge-agent-pilot" / "evaluations"

    in_scope_categories = ["normal", "negative", "ambiguous", "currency"]
    for cat in in_scope_categories:
        cat_files = list((eval_dir / cat).glob("*.json"))
        assert len(cat_files) >= 1, f"Category {cat} must have at least 1 case file"


def test_all_cases_match_schema():
    repo_root = Path(__file__).resolve().parents[3]
    eval_dir = repo_root / "tools" / "phase-5-sharepoint-knowledge-agent-pilot" / "evaluations"

    case_files = list(eval_dir.glob("*/*.json"))
    assert len(case_files) >= 1, "No evaluation case files found yet"

    for case_file in case_files:
        with open(case_file, "r", encoding="utf-8") as f:
            case_data = json.load(f)
        assert validate_cases.validate_case_definition(case_data), f"Case {case_file} failed validation"
