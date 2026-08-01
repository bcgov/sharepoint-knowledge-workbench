"""
Phase 4 Evaluation Case Validator

Validates evaluation case JSON definitions against schema and semantic requirements.
"""
import json
import sys
from pathlib import Path
from typing import Any, Dict

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


def validate_case_definition(case_data: Dict[str, Any]) -> bool:
    """
    Validates an evaluation case dictionary against schema rules.
    """
    required_keys = [
        "case_id",
        "category",
        "objective",
        "primary_topic",
        "related_topic_allowance",
        "test_identity_class",
        "prompt",
        "run_count",
        "expected_semantic_behaviours",
        "prohibited_behaviours",
    ]
    if not all(k in case_data for k in required_keys):
        return False

    valid_categories = ["normal", "negative", "ambiguous", "permission", "safety"]
    if case_data["category"] not in valid_categories:
        return False

    valid_identities = ["OWNER_EDITOR", "INTENDED_READER", "RESTRICTED_READER", "NO_SOURCE_ACCESS"]
    if case_data["test_identity_class"] not in valid_identities:
        return False

    if not isinstance(case_data["related_topic_allowance"], int) or not (0 <= case_data["related_topic_allowance"] <= 2):
        return False

    if not isinstance(case_data["run_count"], int) or case_data["run_count"] < 1:
        return False

    if not isinstance(case_data["expected_semantic_behaviours"], list) or len(case_data["expected_semantic_behaviours"]) < 1:
        return False

    if not isinstance(case_data["prohibited_behaviours"], list) or len(case_data["prohibited_behaviours"]) < 1:
        return False

    # Optional jsonschema check against formal schema file if available
    if HAS_JSONSCHEMA:
        schema_path = (
            Path(__file__).resolve().parents[1] / "schemas" / "evaluation-case-schema.json"
        )
        if schema_path.is_file():
            try:
                with open(schema_path, "r", encoding="utf-8") as sf:
                    schema = json.load(sf)
                jsonschema.validate(instance=case_data, schema=schema)
            except Exception:
                return False

    return True


def validate_all_cases_in_directory(eval_dir: Path) -> bool:
    """
    Scans and validates all JSON files in the evaluations directory structure.
    """
    json_files = list(eval_dir.glob("*/*.json"))
    if not json_files:
        print(f"No JSON evaluation case files found under {eval_dir}")
        return False

    all_valid = True
    for json_file in sorted(json_files):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not validate_case_definition(data):
                print(f"[FAIL] Case validation failed: {json_file}")
                all_valid = False
            else:
                print(f"[PASS] Case valid: {json_file.relative_to(eval_dir)}")
        except Exception as e:
            print(f"[ERROR] Failed to load or validate {json_file}: {e}")
            all_valid = False

    return all_valid


if __name__ == "__main__":
    eval_dir = Path(__file__).resolve().parent
    success = validate_all_cases_in_directory(eval_dir)
    sys.exit(0 if success else 1)
