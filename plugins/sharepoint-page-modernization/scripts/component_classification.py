"""
component_classification.py
============================

Purpose: Stage 2 of the page-modernization pipeline -- assign a Role
(Primary/Secondary/Child/Banner/Unknown), Type, and Variant to each detected
zone from a page inventory (see aspx_inventory.py). The first unconnected
list view is Primary, additional standalone views are Secondary, connected
consumers are Child, ContentEditors are Banner. An unrecognised web part
type is reported through the shared outcome vocabulary (see outcomes.py)
rather than being silently labelled "Unknown" and forgotten.

Layer: CLI entry point, invoked as a real subprocess by the pipeline (and by
this plugin's own tests).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import outcomes

_KNOWN_ZONE_TYPES = {"ContentEditor", "XsltListView"}


def classify_zones(zones: "list[dict]") -> tuple:
    """Returns (components, unsupported_types) where unsupported_types is
    the sorted set of web part types this stage does not know how to
    classify."""
    components = []
    unsupported_types: "set[str]" = set()
    primary_assigned = False

    for zone in zones:
        webPartType = zone.get("webPartType")
        confidence = zone.get("confidence")

        if webPartType == "ContentEditor":
            components.append({
                "role": "Banner",
                "type": webPartType,
                "rawHtml": zone.get("rawHtml"),
                "zone": zone.get("zoneId"),
                "confidence": confidence,
                "evidence": {"detectionSource": zone.get("detectionSource")},
            })
        elif webPartType == "XsltListView":
            if zone.get("isConnectedConsumer"):
                role = "Child"
                variant = "connected-consumer"
            elif not primary_assigned:
                role = "Primary"
                variant = "standalone"
                primary_assigned = True
            else:
                role = "Secondary"
                variant = "standalone"
            components.append({
                "role": role,
                "type": webPartType,
                "variant": variant,
                "listName": zone.get("listName"),
                "viewQuery": zone.get("viewQuery"),
                "relationship": zone.get("relationship"),
                "zone": zone.get("zoneId"),
                "confidence": confidence,
                "evidence": {"detectionSource": zone.get("detectionSource")},
            })
        else:
            unsupported_types.add(webPartType)
            components.append({
                "role": "Unknown",
                "type": webPartType,
                "zone": zone.get("zoneId"),
                "confidence": confidence,
                "evidence": {"detectionSource": zone.get("detectionSource")},
            })

    return components, sorted(t for t in unsupported_types if t)


def build_model(inventory: dict) -> dict:
    zones = inventory.get("zones", [])
    components, unsupported_types = classify_zones(zones)

    if not components:
        outcome = outcomes.make_outcome("Empty", "No zones in the page inventory to classify")
    elif unsupported_types and len(unsupported_types) == len({c["type"] for c in components}):
        outcome = outcomes.make_outcome(
            "NotSupported",
            f"No zone types could be classified: {', '.join(unsupported_types)}",
        )
    elif unsupported_types:
        outcome = outcomes.make_outcome(
            "Partial",
            f"Some zone types could not be classified: {', '.join(unsupported_types)}",
        )
    else:
        outcome = outcomes.make_outcome("Observed", f"{len(components)} components classified")

    return {"components": components, "outcome": outcome}


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(description="Classify page-inventory zones into a component model.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"Unavailable: input inventory file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        inventory = json.loads(input_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Failed: could not parse input inventory file: {exc}", file=sys.stderr)
        return 1

    model = build_model(inventory)

    output_path = Path(args.output)
    output_path.write_text(json.dumps(model, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
