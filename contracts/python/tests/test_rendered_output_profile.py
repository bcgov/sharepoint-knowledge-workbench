import pytest

from knowledge_workbench_contracts.rendered_output_profile import SCHEMA_VERSION, validate


def _valid():
    return {
        "schema_version": SCHEMA_VERSION,
        "renderer": "multipage-markdown",
        "page_count": 25,
        "source_content_sha256": "d" * 64,
    }


def test_validate_accepts_well_formed_profile():
    validate(_valid())


def test_validate_rejects_missing_required_field():
    data = _valid()
    del data["renderer"]
    with pytest.raises(ValueError):
        validate(data)


def test_validate_rejects_wrong_schema_version():
    data = _valid()
    data["schema_version"] = "0.0"
    with pytest.raises(ValueError):
        validate(data)
