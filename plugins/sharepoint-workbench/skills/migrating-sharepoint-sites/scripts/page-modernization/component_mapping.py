"""
component_mapping.py
=====================

Purpose: Stage 4 of the page-modernization pipeline -- map classified
components to modern page sections and target list views, and record what
could not be migrated. ContentEditor components map to a TextWebPart
section; a Primary list view maps to a ListWebPart section plus a
view-provisioning entry (CAML lives in the view, not the page -- ARCH-001);
a connected consumer is recorded as NOT_MIGRATED with its relationship
preserved. A single gap-notice section is appended, rendered from
`assets/gap-notice.template.html`, whenever anything was not migrated.

Layer: CLI entry point, invoked as a real subprocess by the pipeline (and by
this plugin's own tests).

Key Input Dependencies:
    - Classified component-model JSON and layout JSON supplied by the caller.
    - Mapping rules JSON supplied with --mapping-rules or bundled in assets/.
    - gap-notice.template.html used when a connected consumer cannot migrate.
    - outcomes.py shared page-modernization result vocabulary.

Function Index:
    _view_name_for, _render_gap_notice, _map_component,
    _mapping_outcome, map_components, main
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import outcomes

_PLUGIN_ROOT = Path(__file__).resolve().parent
_PACKAGED_MAPPING_RULES = _PLUGIN_ROOT / "assets" / "webpart-mapping.json"
_GAP_NOTICE_TEMPLATE = _PLUGIN_ROOT / "assets" / "gap-notice.template.html"

_SUPPORTED_TYPES = {"ContentEditor", "XsltListView"}

_GAP_REASON = "GAP-001-CRITICAL: modern SharePoint pages do not support the classic web part connection framework"


def _view_name_for(list_name: str, prefix: str) -> str:
    """Create a neutral view name from the configured prefix and list title."""
    condensed = re.sub(r"[^A-Za-z0-9]", "", list_name)
    return f"{prefix}{condensed}"


def _render_gap_notice(not_migrated: "list[dict]") -> str:
    """Render the template with one actionable entry per unmigrated consumer."""
    template = _GAP_NOTICE_TEMPLATE.read_text(encoding="utf-8")

    items = []
    for item in not_migrated:
        line = f"&nbsp;&nbsp;&rarr; Open the <em>{item['listName']}</em> list"
        if item.get("relationship"):
            line += f" and filter by the field described in: {item['relationship']}"
        line += "<br>"
        items.append(line)

    intro = (
        "The following related list(s) were not migrated to this page: "
        + ", ".join(item["listName"] for item in not_migrated) + "."
    )

    rendered = template.replace("{{ notice_intro }}", intro)
    rendered = rendered.replace("{%- if backlog_reference %}", "")
    rendered = re.sub(
        r"\{% for item in not_migrated -%\}.*?\{% endfor -%\}",
        "".join(items),
        rendered,
        flags=re.DOTALL,
    )
    rendered = re.sub(r"\{% if backlog_reference %\}.*?\{% endif %\}", "", rendered, flags=re.DOTALL)
    return rendered


def _map_component(component: dict, view_name_prefix: str) -> tuple[dict | None, dict | None, dict | None, str | None]:
    """Map one component into a section, view, gap record, or unsupported type."""
    comp_type = component.get("type")
    role = component.get("role")
    if comp_type == "ContentEditor":
        return {
            "webPart": {
                "type": "TextWebPart",
                "content": component.get("rawHtml"),
                "sourceZone": component.get("zone"),
                "isGapNotice": False,
            }
        }, None, None, None
    if comp_type == "XsltListView" and role in ("Primary", "Secondary"):
        list_name = component.get("listName")
        view_name = _view_name_for(list_name, view_name_prefix)
        section = {
            "webPart": {
                "type": "ListWebPart",
                "listName": list_name,
                "viewName": view_name,
                "sourceZone": component.get("zone"),
                "isGapNotice": False,
            }
        }
        view = {
            "listName": list_name,
            "viewName": view_name,
            "camlQuery": component.get("viewQuery"),
        }
        return section, view, None, None
    if comp_type == "XsltListView" and role == "Child":
        return None, None, {
            "listName": component.get("listName"),
            "reason": _GAP_REASON,
            "relationship": component.get("relationship"),
        }, None
    return None, None, None, comp_type


def _mapping_outcome(
    components: list[dict],
    sections: list[dict],
    not_migrated: list[dict],
    unmappable_types: set[str],
) -> dict:
    """Classify the mapping result from mapped and unsupported components."""
    if not components:
        return outcomes.make_outcome("Empty", "No components to map")
    if not sections and unmappable_types:
        return outcomes.make_outcome(
            "NotSupported",
            f"No components could be mapped: {', '.join(sorted(unmappable_types))}",
        )
    if not_migrated:
        return outcomes.make_outcome(
            "Partial",
            f"Not migrated: {', '.join(n['listName'] for n in not_migrated)}",
        )
    return outcomes.make_outcome("Observed", f"{len(sections)} section(s) mapped")


def map_components(
    components: "list[dict]",
    layout: dict,
    mapping_rules: dict,
    view_name_prefix: str,
) -> tuple:
    """Map supported classic components to modern sections/views and report gaps."""
    sections = []
    views = []
    not_migrated = []
    unmappable_types: "set[str]" = set()

    for component in components:
        section, view, gap, unmappable_type = _map_component(component, view_name_prefix)
        if section is not None:
            sections.append(section)
        if view is not None:
            views.append(view)
        if gap is not None:
            not_migrated.append(gap)
        if section is None and view is None and gap is None:
            unmappable_types.add(unmappable_type)

    if not_migrated:
        sections.append({
            "webPart": {
                "type": "TextWebPart",
                "isGapNotice": True,
                "content": _render_gap_notice(not_migrated),
            }
        })

    plan = {
        "mappingVersion": mapping_rules.get("mappingVersion"),
        "rulesApplied": [r["id"] for r in mapping_rules.get("architecturalRules", [])],
        "sections": sections,
        "notMigrated": not_migrated,
    }
    views_plan = {"views": views}

    plan["outcome"] = _mapping_outcome(components, sections, not_migrated, unmappable_types)
    return plan, views_plan


def main(argv: "list[str] | None" = None) -> int:
    """Load mapping inputs, write section/view plans, and report failures."""
    parser = argparse.ArgumentParser(description="Map classified components to modern sections and views.")
    parser.add_argument("--components", required=True)
    parser.add_argument("--layout", required=True)
    parser.add_argument("--mapping-rules")
    parser.add_argument("--view-name-prefix", default="Migrated_")
    parser.add_argument("--output-mapping", required=True)
    parser.add_argument("--output-views", required=True)
    args = parser.parse_args(argv)

    components_path = Path(args.components)
    if not components_path.is_file():
        print(f"Unavailable: components file not found: {components_path}", file=sys.stderr)
        return 1

    layout_path = Path(args.layout)
    if not layout_path.is_file():
        print(f"Unavailable: layout file not found: {layout_path}", file=sys.stderr)
        return 1

    mapping_rules_path = Path(args.mapping_rules) if args.mapping_rules else _PACKAGED_MAPPING_RULES
    if not mapping_rules_path.is_file():
        print(f"Unavailable: mapping rules file not found: {mapping_rules_path}", file=sys.stderr)
        return 1

    try:
        components = json.loads(components_path.read_text(encoding="utf-8")).get("components", [])
        layout = json.loads(layout_path.read_text(encoding="utf-8"))
        mapping_rules = json.loads(mapping_rules_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Failed: could not parse an input file: {exc}", file=sys.stderr)
        return 1

    plan, views_plan = map_components(components, layout, mapping_rules, args.view_name_prefix)

    Path(args.output_mapping).write_text(json.dumps(plan, indent=2), encoding="utf-8")
    Path(args.output_views).write_text(json.dumps(views_plan, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
