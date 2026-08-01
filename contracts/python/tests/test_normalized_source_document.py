import pytest

from knowledge_workbench_contracts.normalized_source_document import (
    SCHEMA_VERSION,
    validate,
)


def _valid():
    return {
        "schema_version": SCHEMA_VERSION,
        "source_content_sha256": "a" * 64,
        "markdown_text": "# Title\n",
        "media_files": [],
    }


def test_validate_accepts_well_formed_document():
    validate(_valid())  # must not raise


def test_validate_rejects_missing_required_field():
    data = _valid()
    del data["markdown_text"]
    with pytest.raises(ValueError):
        validate(data)


def test_validate_rejects_wrong_schema_version():
    data = _valid()
    data["schema_version"] = "0.0"
    with pytest.raises(ValueError):
        validate(data)
