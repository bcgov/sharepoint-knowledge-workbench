import pytest
from pathlib import Path
from schema_scaffold import create_empty_schema_definition, scaffold_schema
from schema_export import SectionStatus

def test_create_empty_schema_definition():
    schema = create_empty_schema_definition("pilot-site")
    assert schema.label == "pilot-site"
    assert schema.status == SectionStatus.OBSERVED
    assert len(schema.site_columns) == 0
    assert len(schema.content_types) == 0
    assert len(schema.lists) == 0

def test_scaffold_schema(tmp_path):
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
