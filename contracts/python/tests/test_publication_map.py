import pytest

from knowledge_workbench_contracts.publication_map import SCHEMA_VERSION, validate


def _valid():
    return {
        "schema_version": SCHEMA_VERSION,
        "entries": [{"topic_id": "t1", "order": 0}],
    }


def test_validate_accepts_well_formed_map():
    validate(_valid())


def test_validate_rejects_missing_required_field():
    data = _valid()
    del data["entries"]
    with pytest.raises(ValueError):
        validate(data)


def test_validate_rejects_wrong_schema_version():
    data = _valid()
    data["schema_version"] = "0.0"
    with pytest.raises(ValueError):
        validate(data)
