"""
test_schema_definition.py -- contract tests for generating a schema
definition from an already-loaded SchemaExport.

Purpose:
    Prove that `generate_schema_definition` produces an honest, JSON-
    round-trippable schema definition: full coverage from a healthy export,
    an explicit degraded status (never a silent empty-but-successful
    definition) from a partial/unavailable export, and no project literals
    baked into the module itself.

Layer: sharepoint-schema / plugin-local tests

Key Input Dependencies:
    - schema_export (fixture loading)
    - schema_definition (module under test)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from schema_export import SectionStatus, load_schema_export  # noqa: E402
from schema_definition import (  # noqa: E402
    FieldDefinition,
    ContentTypeDefinition,
    ListDefinition,
    SiteSchemaDefinition,
    generate_schema_definition,
)

FIXTURES = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "exports"


def test_generates_full_definition_from_a_healthy_export():
    export = load_schema_export(FIXTURES / "baseline", label="baseline")
    definition = generate_schema_definition(export, label="baseline")

    assert isinstance(definition, SiteSchemaDefinition)
    assert definition.label == "baseline"
    assert definition.status is SectionStatus.OBSERVED

    site_column_names = {f.internal_name for f in definition.site_columns}
    assert site_column_names == {"summary", "retired_code"}
    assert all(isinstance(f, FieldDefinition) for f in definition.site_columns)

    ct_names = {ct.name for ct in definition.content_types}
    assert ct_names == {"Reference Item"}
    assert all(isinstance(ct, ContentTypeDefinition) for ct in definition.content_types)

    assert len(definition.lists) == 1
    records = definition.lists[0]
    assert isinstance(records, ListDefinition)
    assert records.title == "Records"
    assert records.key == "lists/Records"
    field_names = {f.internal_name for f in records.fields}
    assert field_names == {"alpha", "legacy_ref"}


def test_degraded_export_produces_honest_non_observed_definition(tmp_path):
    export = load_schema_export(tmp_path / "does-not-exist", label="ghost")
    definition = generate_schema_definition(export, label="ghost")

    assert definition.status is SectionStatus.UNAVAILABLE
    assert definition.site_columns == ()
    assert definition.content_types == ()
    assert definition.lists == ()


def test_partial_export_is_reported_as_partial_not_observed(tmp_path):
    root = tmp_path / "partial"
    (root / "summary").mkdir(parents=True)
    (root / "summary" / "site_columns.json").write_text(
        json.dumps([{"InternalName": "alpha", "TypeAsString": "Text"}]), encoding="utf-8"
    )
    # content_types.json and lists.json are missing -> UNAVAILABLE sections
    export = load_schema_export(root, label="partial")
    definition = generate_schema_definition(export, label="partial")

    assert export.status is SectionStatus.PARTIAL
    assert definition.status is SectionStatus.PARTIAL
    # the section that *was* observed is still honestly reflected
    assert len(definition.site_columns) == 1
    assert definition.content_types == ()
    assert definition.lists == ()


def test_list_with_unreadable_fields_section_is_still_recorded_honestly(tmp_path):
    root = tmp_path / "q"
    (root / "summary").mkdir(parents=True)
    (root / "summary" / "site_columns.json").write_text("[]", encoding="utf-8")
    (root / "summary" / "content_types.json").write_text("[]", encoding="utf-8")
    (root / "summary" / "lists.json").write_text(
        json.dumps([{"Title": "Other", "BaseTemplate": 100}]), encoding="utf-8"
    )
    (root / "lists" / "Other").mkdir(parents=True)
    (root / "lists" / "Other" / "fields.json").write_text("[[[", encoding="utf-8")

    export = load_schema_export(root, label="q")
    definition = generate_schema_definition(export, label="q")

    other = definition.lists[0]
    assert other.title == "Other"
    assert other.fields_status is SectionStatus.FAILED
    assert other.fields == ()


def test_json_round_trip_preserves_shape():
    export = load_schema_export(FIXTURES / "baseline", label="baseline")
    definition = generate_schema_definition(export, label="baseline")

    payload = definition.to_dict()
    json_text = json.dumps(payload)
    restored = SiteSchemaDefinition.from_dict(json.loads(json_text))

    assert restored == definition


def test_field_definition_round_trip():
    field = FieldDefinition(
        internal_name="alpha",
        display_name="Alpha",
        type_as_string="Text",
        required=False,
        hidden=False,
        read_only=False,
        group="Custom Columns",
    )
    assert FieldDefinition.from_dict(field.to_dict()) == field


def test_module_has_no_project_literals_or_tenant_urls():
    import re

    source = Path(__file__).resolve().parents[1] / "scripts" / "schema_definition.py"
    text = source.read_text(encoding="utf-8").lower()
    for literal in [__import__("base64").b64decode(x).decode() for x in ['Y2Vpcw==', 'Y21hdA==', 'amFnLmdvdi5iYy5jYQ==', 'YmNnb3Y=', 'Z292LmJjLmNh', 'aXRhdQ==', 'cGlv', 'aWNt']]:
        pattern = re.compile(r"(?<![a-z0-9])" + re.escape(literal) + r"(?![a-z0-9])")
        assert not pattern.search(text), f"found project literal {literal!r} in schema_definition.py"
    assert "sharepoint.com" not in text
