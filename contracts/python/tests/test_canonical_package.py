import pytest

from knowledge_workbench_contracts.canonical_package import SCHEMA_VERSION, validate


def _valid():
    return {
        "schema_version": SCHEMA_VERSION,
        "package_identity": "sha256:" + "c" * 64,
        "chunks": [],
        "generator": {"plugin": "canonical-knowledge", "plugin_version": "0.1.0-alpha.1"},
    }


def test_validate_accepts_well_formed_package():
    validate(_valid())


def test_validate_rejects_missing_required_field():
    data = _valid()
    del data["chunks"]
    with pytest.raises(ValueError):
        validate(data)


def test_validate_rejects_wrong_schema_version():
    data = _valid()
    data["schema_version"] = "0.0"
    with pytest.raises(ValueError):
        validate(data)
