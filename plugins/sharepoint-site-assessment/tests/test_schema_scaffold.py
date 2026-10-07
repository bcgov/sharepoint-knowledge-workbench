"""
Purpose: Verify schema-definition scaffolding from neutral local inputs.

Key Input Dependencies:
    - pytest, the plugin module under test, and temporary JSON fixtures created by the test cases.

Function index:
    - test_create_empty_schema_definition
    - test_scaffold_schema
"""

import pytest
from pathlib import Path
from schema_scaffold import create_empty_schema_definition, scaffold_schema
from schema_export import SectionStatus

# Verify that the empty-schema factory returns a valid observed definition.
def test_create_empty_schema_definition():
    """Check the label, observed status, and empty object collections."""
    schema = create_empty_schema_definition("pilot-site")
    assert schema.label == "pilot-site"
    assert schema.status == SectionStatus.OBSERVED
    assert len(schema.site_columns) == 0
    assert len(schema.content_types) == 0
    assert len(schema.lists) == 0

# Verify that caller-supplied fields and lists are written as a schema file.
def test_scaffold_schema(tmp_path):
    """Check schema content, normalized list identity, and output-file creation."""
    out = tmp_path / "schema.json"
    schema = scaffold_schema(
        label="pilot-site",
        output_path=out,
        site_columns=[{"internal_name": "ProjectStatus", "display_name": "Project Status", "type_as_string": "Choice"}],
        lists=[{"title": "Projects", "base_template": 100, "fields": []}],
    )
    assert len(schema.site_columns) == 1
    assert schema.site_columns[0].internal_name == "ProjectStatus"
    assert len(schema.lists) == 1
    assert schema.lists[0].key == "projects"
    assert out.exists()
