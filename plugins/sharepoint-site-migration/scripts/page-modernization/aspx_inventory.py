"""
aspx_inventory.py
==================

Purpose: Stage 1 of the page-modernization pipeline -- parse a classic
SharePoint page's rendered HTML (plus optional views export and override
hints) into a neutral page inventory of web part zones. Never fabricates a
zone when evidence is absent; reports honestly through the shared outcome
vocabulary (see outcomes.py) rather than collapsing a zero-zone result into
a silent success.

Layer: CLI entry point, invoked as a real subprocess by the pipeline (and by
this plugin's own tests) -- no mocking of parsing or path resolution.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import outcomes

_CONTENT_EDITOR_RE = re.compile(
    r'<div[^>]*class="ms-rtestate-field"[^>]*>(.*?)</div>',
    re.DOTALL | re.IGNORECASE,
)


@dataclass
class Zone:
    zoneId: str
    webPartType: str
    detectionSource: str
    rawHtml: "str | None" = None
    listName: "str | None" = None
    viewQuery: "str | None" = None
    isConnectedConsumer: "bool | None" = None
    relationship: "str | None" = None
    confidence: "str | None" = None

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class Inventory:
    sourcePage: str
    zones: "list[Zone]" = field(default_factory=list)
    warnings: "list[str]" = field(default_factory=list)
    detectionSources: "set[str]" = field(default_factory=set)


def _detect_content_editor_zones(html: str) -> "list[Zone]":
    zones = []
    for i, match in enumerate(_CONTENT_EDITOR_RE.finditer(html), start=1):
        zones.append(Zone(
            zoneId=f"wpz_ce_{i}",
            webPartType="ContentEditor",
            detectionSource="rendered-html",
            rawHtml=match.group(1).strip(),
        ))
    return zones


def _detect_views_zones(views: "list[dict]", source_page: str) -> "list[Zone]":
    zones = []
    for i, view in enumerate(views, start=1):
        if source_page and view.get("ServerRelativeUrl") != source_page:
            continue
        zones.append(Zone(
            zoneId=f"wpz_lv_{i}",
            webPartType="XsltListView",
            detectionSource="views-json",
            listName=view.get("ListTitle"),
            viewQuery=view.get("ViewQuery"),
            isConnectedConsumer=False,
        ))
    return zones


def _detect_override_zones(override: dict) -> "list[Zone]":
    zones = []
    for relation in override.get("knownRelationships", []):
        listName = relation.get("consumerList")
        zones.append(Zone(
            zoneId=f"wpz_lv_child_{listName}",
            webPartType="XsltListView",
            detectionSource="override-file",
            listName=listName,
            isConnectedConsumer=True,
            relationship=relation.get("relationship"),
            confidence=relation.get("confidence"),
        ))
    return zones


def build_inventory(
    html: str,
    source_page: str,
    views: "list[dict] | None",
    views_provided: bool,
    override: "dict | None",
    override_provided: bool,
) -> dict:
    warnings: "list[str]" = []
    zones: "list[Zone]" = []
    detection_sources: "set[str]" = set()

    ce_zones = _detect_content_editor_zones(html)
    zones.extend(ce_zones)
    if ce_zones:
        detection_sources.add("rendered-html")

    partial_reasons: "list[str]" = []

    if views_provided:
        views_zones = _detect_views_zones(views or [], source_page)
        zones.extend(views_zones)
        if views_zones:
            detection_sources.add("views-json")
        else:
            partial_reasons.append("views export was provided but contributed no matching zones")
            warnings.append("views export was provided but contributed no matching zones")

    if override_provided:
        override_zones = _detect_override_zones(override or {})
        zones.extend(override_zones)
        if override_zones:
            detection_sources.add("override-file")
        else:
            partial_reasons.append("override file was provided but contained no known relationships")
            warnings.append("override file was provided but contained no known relationships")

    has_connections = any(z.isConnectedConsumer for z in zones)

    if not detection_sources:
        detection_method = "none"
    elif len(detection_sources) == 1:
        detection_method = next(iter(detection_sources))
    else:
        detection_method = "multi"

    if not zones:
        warnings.append("no web part zones were detected in the source HTML")
        outcome = outcomes.make_outcome(
            "Empty", "No web part zones detected in the source page", counts={"zones": 0}
        )
    elif partial_reasons:
        outcome = outcomes.make_outcome(
            "Partial", "; ".join(partial_reasons), counts={"zones": len(zones)}
        )
    else:
        outcome = outcomes.make_outcome(
            "Observed", f"{len(zones)} zones detected", counts={"zones": len(zones)}
        )

    return {
        "sourcePage": source_page,
        "pageType": "BlankWebPartPage",
        "hasConnections": has_connections,
        "detectionMethod": detection_method,
        "detectionSources": sorted(detection_sources),
        "zones": [z.to_dict() for z in zones],
        "warnings": warnings,
        "outcome": outcome,
    }


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(description="Build a neutral page inventory from a classic SharePoint page.")
    parser.add_argument("--source-html", required=True)
    parser.add_argument("--source-page", default="")
    parser.add_argument("--views-json")
    parser.add_argument("--override")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    source_html_path = Path(args.source_html)
    if not source_html_path.is_file():
        print(f"Unavailable: source HTML file not found: {source_html_path}", file=sys.stderr)
        return 1

    try:
        html = source_html_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Failed: could not read source HTML file: {exc}", file=sys.stderr)
        return 1

    views: "list[dict] | None" = None
    views_provided = args.views_json is not None
    if views_provided:
        views_path = Path(args.views_json)
        if not views_path.is_file():
            print(f"Unavailable: views export file not found: {views_path}", file=sys.stderr)
            return 1
        try:
            views = json.loads(views_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"Failed: could not parse views export file: {exc}", file=sys.stderr)
            return 1

    override: "dict[str, Any] | None" = None
    override_provided = args.override is not None
    if override_provided:
        override_path = Path(args.override)
        if not override_path.is_file():
            print(f"Unavailable: override file not found: {override_path}", file=sys.stderr)
            return 1
        try:
            override = json.loads(override_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"Failed: could not parse override file: {exc}", file=sys.stderr)
            return 1

    inventory = build_inventory(
        html, args.source_page, views, views_provided, override, override_provided
    )

    output_path = Path(args.output)
    output_path.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
