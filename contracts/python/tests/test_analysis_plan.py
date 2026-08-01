import pytest

from knowledge_workbench_contracts.analysis_plan import SCHEMA_VERSION, validate


def _valid():
    return {
        "schema_version": SCHEMA_VERSION,
        "plan_id": "b" * 64,
        "strategy": "grouped",
        "structural_anchors": [],
        "confirmation": {"confirmed": False},
    }


def test_validate_accepts_well_formed_plan():
    validate(_valid())


def test_validate_rejects_missing_required_field():
    data = _valid()
    del data["strategy"]
    with pytest.raises(ValueError):
        validate(data)


def test_validate_rejects_wrong_schema_version():
    data = _valid()
    data["schema_version"] = "9.9"
    with pytest.raises(ValueError):
        validate(data)
