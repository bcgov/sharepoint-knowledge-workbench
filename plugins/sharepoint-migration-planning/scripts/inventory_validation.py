"""
inventory_validation.py
=========================

Purpose:
    Stage 2 (`discover-sharepoint-site-inventory`) logic, scoped to its
    "buildable now" half: accept a path to an export directory a human (or
    an out-of-workbench script) already produced, validate/normalize its
    shape against `assets/site-inventory-export-schema.json`, and translate
    it into the raw object list `dependency_graph.load_matrix_objects`
    needs -- critically preserving lookup-column targets (which list a
    Lookup field points at), the relationship stage 3a's dependsOn edges
    are built from. Never performs live-tenant discovery itself (that is
    the not-yet-built, design-only `sharepoint-collection` connector);
    never invents lookup-target data that is not present in the export;
    never silently proceeds on an incomplete or malformed export.

Layer: sharepoint-migration-planning / stage 2 (site inventory intake)

Key Input Dependencies:
    - provisioning_outcomes.Outcome (symlinked from sharepoint-provisioning)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from provisioning_outcomes import Outcome

INVENTORY_FILENAME = "site-inventory.json"


@dataclass(frozen=True)
class InventoryValidationResult:
    """Result of validating an export directory. ``issues`` names exactly
    what is missing/malformed (never a bare boolean) so an operator can fix
    the export directly. ``matrix_objects`` is only populated when
    ``outcome`` is ``OBSERVED`` or ``EMPTY`` -- callers must not use it
    otherwise."""

    outcome: str
    issues: tuple[str, ...] = ()
    matrix_objects: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict:
        return {
            "outcome": self.outcome,
            "issues": list(self.issues),
            "matrix_objects": list(self.matrix_objects),
        }


def validate_export_directory(export_dir: "Path | str") -> InventoryValidationResult:
    """Validate `export_dir` against the expected shape (a
    `site-inventory.json` file with a `lists` array; each list has `name`
    and a `fields` array; each `Lookup`-type field has a `lookupList`).
    Reads only the one file this shape names -- no other I/O. Never raises
    for a malformed export; always reports honestly via `Outcome` and
    `issues`."""
    export_dir = Path(export_dir)
    inventory_path = export_dir / INVENTORY_FILENAME

    if not inventory_path.is_file():
        return InventoryValidationResult(
            outcome=Outcome.UNAVAILABLE,
            issues=(f"{inventory_path} not found -- expected a site-inventory.json export file",),
        )

    try:
        raw_text = inventory_path.read_text(encoding="utf-8")
        data = json.loads(raw_text)
    except (OSError, json.JSONDecodeError) as exc:
        return InventoryValidationResult(
            outcome=Outcome.FAILED,
            issues=(f"{inventory_path} could not be read/parsed as JSON: {exc}",),
        )

    if not isinstance(data, dict) or "lists" not in data:
        return InventoryValidationResult(
            outcome=Outcome.FAILED,
            issues=(f"{inventory_path} is missing the required top-level 'lists' array",),
        )

    lists = data["lists"]
    if not isinstance(lists, list):
        return InventoryValidationResult(
            outcome=Outcome.FAILED,
            issues=("'lists' must be an array",),
        )

    if not lists:
        return InventoryValidationResult(outcome=Outcome.EMPTY, issues=(), matrix_objects=())

    issues: list[str] = []
    matrix_objects: list[dict[str, Any]] = []
    seen_names: set[str] = set()

    for index, raw_list in enumerate(lists):
        if not isinstance(raw_list, dict):
            issues.append(f"lists[{index}] is not an object")
            continue

        name = raw_list.get("name")
        if not name:
            issues.append(f"lists[{index}] is missing required field 'name'")
            continue
        if name in seen_names:
            issues.append(f"duplicate list name '{name}' in export")
            continue
        seen_names.add(name)

        fields = raw_list.get("fields")
        if not isinstance(fields, list):
            issues.append(f"'{name}' is missing required field 'fields' (array)")
            continue

        depends_on: list[str] = []
        for field_index, raw_field in enumerate(fields):
            if not isinstance(raw_field, dict):
                issues.append(f"'{name}'.fields[{field_index}] is not an object")
                continue
            field_name = raw_field.get("name")
            field_type = raw_field.get("type")
            if not field_name or not field_type:
                issues.append(f"'{name}'.fields[{field_index}] is missing required 'name'/'type'")
                continue
            if field_type == "Lookup":
                lookup_list = raw_field.get("lookupList")
                if not lookup_list:
                    issues.append(
                        f"'{name}'.{field_name} is a Lookup field with no 'lookupList' target -- "
                        "cannot derive its dependency edge"
                    )
                    continue
                if lookup_list not in depends_on:
                    depends_on.append(lookup_list)

        matrix_objects.append({"name": name, "objectType": "List", "dependsOn": depends_on})

    if issues:
        return InventoryValidationResult(outcome=Outcome.FAILED, issues=tuple(issues), matrix_objects=())

    return InventoryValidationResult(
        outcome=Outcome.OBSERVED, issues=(), matrix_objects=tuple(matrix_objects)
    )
