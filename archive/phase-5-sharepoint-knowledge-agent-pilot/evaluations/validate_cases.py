"""
Phase 5 Evaluation Case Validator.

Validates evaluation case JSON definitions against the schema shared with Phase 4
(tools/phase-4-native-sharepoint-skills/schemas/evaluation-case-schema.json) plus the
"currency" category it added. This is a deliberate copy of Phase 4's validator, not an
import, so Phase 5 has no runtime dependency on Phase 4's directory continuing to exist
in its current shape — the schema *file* is still shared, read-only, by relative path.
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

VALID_CATEGORIES = ["normal", "negative", "ambiguous", "permission", "safety", "currency"]
VALID_IDENTITIES = ["OWNER_EDITOR", "INTENDED_READER", "RESTRICTED_READER", "NO_SOURCE_ACCESS"]

SHARED_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "phase-4-native-sharepoint-skills"
    / "schemas"
    / "evaluation-case-schema.json"
)


def validate_case_definition(case_data: Dict[str, Any]) -> bool:
    required_keys = [
        "case_id", "category", "objective", "primary_topic", "related_topic_allowance",
        "test_identity_class", "prompt", "run_count", "expected_semantic_behaviours",
        "prohibited_behaviours",
    ]
    if not all(k in case_data for k in required_keys):
        return False

    if case_data["category"] not in VALID_CATEGORIES:
        return False

    if case_data["test_identity_class"] not in VALID_IDENTITIES:
        return False

    if not isinstance(case_data["related_topic_allowance"], int) or not (0 <= case_data["related_topic_allowance"] <= 2):
        return False

    if not isinstance(case_data["run_count"], int) or case_data["run_count"] < 1:
        return False

    if not isinstance(case_data["expected_semantic_behaviours"], list) or len(case_data["expected_semantic_behaviours"]) < 1:
        return False

    if not isinstance(case_data["prohibited_behaviours"], list) or len(case_data["prohibited_behaviours"]) < 1:
        return False

    if HAS_JSONSCHEMA and SHARED_SCHEMA_PATH.is_file():
        try:
            with open(SHARED_SCHEMA_PATH, "r", encoding="utf-8") as sf:
                schema = json.load(sf)
            jsonschema.validate(instance=case_data, schema=schema)
        except Exception:
            return False

    return True


def validate_all_cases_in_directory(eval_dir: Path) -> bool:
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
