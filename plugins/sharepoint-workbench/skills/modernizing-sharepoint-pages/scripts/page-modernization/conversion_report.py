"""
conversion_report.py
=====================

Purpose: render a human-readable Markdown disposition report from a
PageConversionManifest-shaped dict (conforming to
`assets/manifest-schema.json`) -- a header (source page, converted-at,
outcome), a web-part classification table (from `webParts`), a gaps/
dependency section (from `gaps` -- every gap named, never silently dropped),
and a layout/confidence summary section (from `layout`/`confidence`). Pure
function: no I/O, no tenant contact, matching this plugin's zero-tenant-I/O
design.

Layer: CLI entry point, invoked as a real subprocess by the pipeline (and by
this plugin's own tests).

Key Input Dependencies:
    - Page-conversion manifest JSON supplied with --manifest.
    - outcomes.py shared page-modernization result vocabulary.

Function Index:
    _render_webpart_table, _render_gaps, _render_confidence,
    render_conversion_report, main
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import outcomes

_REQUIRED_FIELDS = (
    "sourcePage", "convertedAt", "manifestHash", "mapping",
    "environmentProfile", "source", "target", "webParts",
    "layout", "gaps", "confidence", "outcome",
)


def _render_webpart_table(web_parts: "list[dict]") -> str:
    """Render the source web-part classifications as a Markdown table."""
    header = "| Type | Source Zone | List | Gap Notice |\n|---|---|---|---|"
    rows = []
    for wp in web_parts:
        wp_type = wp.get("type") or "Unknown"
        zone = wp.get("sourceZone") or "-"
        list_name = wp.get("listName") or "-"
        is_gap = "Yes" if wp.get("isGapNotice") else "No"
        rows.append(f"| {wp_type} | {zone} | {list_name} | {is_gap} |")
    return "\n".join([header, *rows]) if rows else header + "\n| _(none)_ | | | |"


def _render_gaps(gaps: "list[str]") -> str:
    """Render every migration gap or an explicit no-gaps message."""
    if not gaps:
        return "No gaps recorded."
    return "\n".join(f"- {gap}" for gap in gaps)


def _render_confidence(confidence: dict) -> str:
    """Render confidence details or an explicit empty-state message."""
    if not confidence:
        return "_(no confidence data recorded)_"
    return "\n".join(f"- **{key}**: {value}" for key, value in confidence.items())


def render_conversion_report(manifest: dict) -> "tuple[str | None, dict]":
    """Render a Markdown disposition report from `manifest`. Returns
    (markdown_or_None, outcome). Never silently renders a blank/partial
    report for malformed input -- a missing required field or an invalid
    outcome vocabulary entry is reported honestly and no report is written."""
    missing = [field for field in _REQUIRED_FIELDS if field not in manifest]
    if missing:
        return None, outcomes.make_outcome(
            "Unavailable", f"Missing required manifest field(s): {', '.join(missing)}"
        )

    try:
        outcomes.validate_outcome(manifest["outcome"])
    except outcomes.OutcomeError as exc:
        return None, outcomes.make_outcome("Failed", f"Manifest outcome is malformed: {exc}")

    layout = manifest["layout"]

    sections = [
        f"# Conversion Report: {manifest['sourcePage']}",
        "",
        f"- **Converted at**: {manifest['convertedAt']}",
        f"- **Outcome**: {manifest['outcome']['status']} -- {manifest['outcome']['detail']}",
        "",
        "## Web Part Classification",
        "",
        _render_webpart_table(manifest["webParts"]),
        "",
        "## Gaps",
        "",
        _render_gaps(manifest["gaps"]),
        "",
        "## Layout",
        "",
        f"- **Template**: {layout.get('template', '-')}",
        f"- **Mapped to**: {layout.get('mappedTo', '-')}",
        f"- **Column count**: {layout.get('columnCount', '-')}",
        "",
        "## Confidence",
        "",
        _render_confidence(manifest["confidence"]),
        "",
    ]
    report = "\n".join(sections)

    gaps = manifest["gaps"]
    if gaps:
        render_outcome = outcomes.make_outcome(
            "Partial", f"Conversion report rendered; {len(gaps)} gap(s) recorded"
        )
    else:
        render_outcome = outcomes.make_outcome("Observed", "Conversion report rendered")

    return report, render_outcome


def main(argv: "list[str] | None" = None) -> int:
    """Load a conversion manifest and write its validated Markdown report."""
    parser = argparse.ArgumentParser(
        description="Render a Markdown disposition report from a PageConversionManifest."
    )
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    manifest_path = Path(args.manifest)
    if not manifest_path.is_file():
        print(f"Unavailable: manifest file not found: {manifest_path}", file=sys.stderr)
        return 1

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Failed: could not parse manifest file: {exc}", file=sys.stderr)
        return 1

    report, outcome = render_conversion_report(manifest)

    if report is None:
        print(f"{outcome['status']}: {outcome['detail']}", file=sys.stderr)
        return 1

    Path(args.output).write_text(report, encoding="utf-8")
    print(f"{outcome['status']}: {outcome['detail']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
