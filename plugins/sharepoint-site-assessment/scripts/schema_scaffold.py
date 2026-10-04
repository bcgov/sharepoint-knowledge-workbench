"""
schema_scaffold.py
==================

Purpose:
    Programmatically scaffold a declarative SiteSchemaDefinition JSON structure
    from scratch without requiring an existing live tenant export. Supports
    authoring site columns, content types, lists, and libraries according to
    the workbench schema specification.

Layer: sharepoint-site-assessment / scripts (pure local transform).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from schema_definition import (
    ContentTypeDefinition,
    FieldDefinition,
    ListDefinition,
    SiteSchemaDefinition,
)
from schema_export import SectionStatus


def create_empty_schema_definition(label: str = "custom-template") -> SiteSchemaDefinition:
    """Create a minimal empty SiteSchemaDefinition with OBSERVED status."""
    return SiteSchemaDefinition(
        label=label,
        site_columns=(),
        content_types=(),
        lists=(),
        status=SectionStatus.OBSERVED,
    )


def scaffold_schema(
    label: str,
    output_path: Optional[Path] = None,
    site_columns: Optional[List[dict]] = None,
    content_types: Optional[List[dict]] = None,
    lists: Optional[List[dict]] = None,
) -> SiteSchemaDefinition:
    """Scaffold a full schema definition from provided dictionaries."""
    sc_objs = tuple(FieldDefinition.from_dict(c) for c in (site_columns or []))
    ct_objs = tuple(ContentTypeDefinition.from_dict(ct) for ct in (content_types or []))
    
    list_objs = []
    for l in (lists or []):
        if "key" not in l:
            l = dict(l)
            l["key"] = l.get("title", "custom-list").lower().replace(" ", "-")
        list_objs.append(ListDefinition.from_dict(l))

    schema = SiteSchemaDefinition(
        label=label,
        site_columns=sc_objs,
        content_types=ct_objs,
        lists=tuple(list_objs),
        status=SectionStatus.OBSERVED,
    )

    if output_path:
        schema.save(Path(output_path))

    return schema


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a declarative SharePoint SiteSchemaDefinition JSON template."
    )
    parser.add_argument(
        "--label",
        default="custom-template",
        help="Schema label/identifier for this template",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        required=True,
        help="Destination JSON file path for the scaffolded schema",
    )

    args = parser.parse_args(argv)
    schema = create_empty_schema_definition(label=args.label)
    schema.save(args.output)
    print(f"Scaffolded schema definition written to: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
