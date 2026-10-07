"""Purpose: Create a dry-run link rewrite plan using an explicit destination map.

Key Input Dependencies: extracted links.csv and file-migration-map.csv.
This planner performs no content or SharePoint writes. Unmapped internal targets
remain distinct from external URLs.

Usage:
    python generate_link_rewrite_plan.py --links-csv links.csv \\
        --migration-map file-migration-map.csv --output-csv link-rewrite-plan.csv

Function index: _normalized_path, _normalized_url, load_migration_map,
_unique_match, _ensure_output_is_distinct, _pre_map_status,
_target_url_with_suffix, _plan_link,
plan_rewrites, main.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import SplitResult, unquote, urlsplit

PLAN_COLUMNS = [
    "SourceHostUrl",
    "SourceHostServerRelativeUrl",
    "SourcePart",
    "RawUrl",
    "ResolvedUrl",
    "LinkKind",
    "TargetStatus",
    "TargetSPOUrl",
    "TargetSPOServerRelativeUrl",
    "OccurrenceCount",
]


def _normalized_path(value: str) -> str:
    """Normalize a URL or server-relative path for case-insensitive matching."""
    path = urlsplit((value or "").strip()).path or (value or "").strip()
    return unquote(path).replace("\\", "/").casefold()


def _normalized_url(value: str) -> str:
    """Normalize a URL's origin and path while discarding query and fragment."""
    parsed = urlsplit((value or "").strip())
    if not parsed.scheme or not parsed.netloc:
        return ""
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}{_normalized_path(parsed.path)}"


def load_migration_map(
    map_path: Path,
) -> Tuple[
    Dict[str, List[Dict[str, str]]],
    Dict[str, List[Dict[str, str]]],
    Set[Tuple[str, str]],
]:
    """Load URL/path indexes and source origins from the destination map."""
    url_lookup: Dict[str, List[Dict[str, str]]] = {}
    path_lookup: Dict[str, List[Dict[str, str]]] = {}
    source_origins: Set[Tuple[str, str]] = set()
    with map_path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            source_path = _normalized_path(row.get("SourceServerRelativeUrl", ""))
            source_url = _normalized_url(row.get("SourceFileUrl", ""))
            if source_path:
                path_lookup.setdefault(source_path, []).append(row)
            if source_url:
                url_lookup.setdefault(source_url, []).append(row)
                parsed = urlsplit(source_url)
                source_origins.add((parsed.scheme.lower(), parsed.netloc.lower()))
    return url_lookup, path_lookup, source_origins


def _unique_match(
    url_lookup: Dict[str, List[Dict[str, str]]],
    path_lookup: Dict[str, List[Dict[str, str]]],
    url: str,
) -> Tuple[Optional[Dict[str, str]], bool]:
    """Return one destination match, or mark a duplicate path as ambiguous."""
    normalized_url = _normalized_url(url)
    if normalized_url and normalized_url in url_lookup:
        matches = url_lookup[normalized_url]
    else:
        normalized_path = _normalized_path(url)
        matches = path_lookup.get(normalized_path, [])
    if len(matches) == 1:
        return matches[0], False
    return None, len(matches) > 1


def _ensure_output_is_distinct(output_path: Path, input_paths: List[Path]) -> None:
    """Prevent a plan output from overwriting either source input file."""
    for input_path in input_paths:
        if output_path == input_path or (
            output_path.exists() and output_path.samefile(input_path)
        ):
            raise ValueError(
                f"output path must differ from every input file: {output_path}"
            )


def _pre_map_status(
    raw_url: str,
    resolved_url: str,
    parsed_raw: SplitResult,
    parsed_resolution: SplitResult,
    source_origins: Set[Tuple[str, str]],
) -> Optional[str]:
    """Classify external, anchor-like, and unresolved links before map lookup."""
    if raw_url.startswith("#") or parsed_raw.scheme.lower() in {
        "mailto", "tel", "javascript", "data"
    }:
        return "ANCHOR"

    if parsed_resolution.scheme.lower() in {"http", "https"} and parsed_resolution.netloc:
        origin = (parsed_resolution.scheme.lower(), parsed_resolution.netloc.lower())
        if origin not in source_origins:
            return "EXTERNAL"
    elif parsed_raw.scheme or parsed_raw.netloc:
        return "EXTERNAL"
    elif not resolved_url and not raw_url.startswith("/"):
        return "UNRESOLVED_RELATIVE"
    return None


def _target_url_with_suffix(target_url: str, raw_url: str, resolved_url: str) -> str:
    """Carry original query and fragment data onto a mapped destination URL."""
    target_parts = urlsplit(target_url)
    raw_parts = urlsplit(raw_url)
    resolved_parts = urlsplit(resolved_url)
    return target_parts._replace(
        query=raw_parts.query or resolved_parts.query,
        fragment=raw_parts.fragment or resolved_parts.fragment,
    ).geturl()


def _plan_link(
    row: Dict[str, str],
    url_lookup: Dict[str, List[Dict[str, str]]],
    path_lookup: Dict[str, List[Dict[str, str]]],
    source_origins: Set[Tuple[str, str]],
) -> Dict[str, str]:
    """Produce one rewrite-plan row and classify its destination status."""
    raw_url = row.get("RawUrl", "").strip()
    resolved_url = row.get("ResolvedUrl", "").strip()
    resolution = resolved_url or raw_url
    parsed_raw = urlsplit(raw_url)
    parsed_resolution = urlsplit(resolution)
    status = _pre_map_status(
        raw_url, resolved_url, parsed_raw, parsed_resolution, source_origins
    )
    target_spo_url = raw_url if status in {"ANCHOR", "EXTERNAL"} else ""
    target_spo_rel = ""

    if status is None:
        matched, ambiguous = _unique_match(url_lookup, path_lookup, resolution)
        if ambiguous:
            status = "AMBIGUOUS"
        elif matched:
            status = "RESOLVED_INTERNAL"
            target_spo_url = _target_url_with_suffix(
                matched.get("TargetFileUrl", ""), raw_url, resolution
            )
            target_spo_rel = matched.get("TargetServerRelativeUrl", "")
        else:
            status = "UNMAPPED_NOT_IN_MAP"

    return {
        "SourceHostUrl": row.get("SourceUrl", ""),
        "SourceHostServerRelativeUrl": row.get("ServerRelativeUrl", ""),
        "SourcePart": row.get("SourcePart", ""),
        "RawUrl": raw_url,
        "ResolvedUrl": resolved_url,
        "LinkKind": row.get("LinkKind", "hyperlink"),
        "TargetStatus": status,
        "TargetSPOUrl": target_spo_url,
        "TargetSPOServerRelativeUrl": target_spo_rel,
        "OccurrenceCount": row.get("OccurrenceCount", "1"),
    }


def plan_rewrites(
    links_csv: Path,
    migration_map_csv: Path,
    output_csv: Path,
) -> Dict[str, Any]:
    """Match extracted links to migration targets and write a reviewable plan."""
    links_csv = Path(links_csv).resolve(strict=True)
    migration_map_csv = Path(migration_map_csv).resolve(strict=True)
    output_csv = Path(output_csv).resolve()
    _ensure_output_is_distinct(output_csv, [links_csv, migration_map_csv])

    url_lookup, path_lookup, source_origins = load_migration_map(migration_map_csv)

    with links_csv.open(encoding="utf-8-sig", newline="") as handle:
        link_rows = list(csv.DictReader(handle))

    plan_rows = []
    status_counts = {
        "RESOLVED_INTERNAL": 0,
        "EXTERNAL": 0,
        "ANCHOR": 0,
        "UNMAPPED_NOT_IN_MAP": 0,
        "UNRESOLVED_RELATIVE": 0,
        "AMBIGUOUS": 0,
    }

    for row in link_rows:
        plan_row = _plan_link(row, url_lookup, path_lookup, source_origins)
        status_counts[plan_row["TargetStatus"]] += 1
        plan_rows.append(plan_row)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PLAN_COLUMNS)
        writer.writeheader()
        writer.writerows(plan_rows)

    summary = {
        "Status": "COMPLETED",
        "TotalLinks": len(plan_rows),
        "ResolvedInternal": status_counts["RESOLVED_INTERNAL"],
        "External": status_counts["EXTERNAL"],
        "Anchors": status_counts["ANCHOR"],
        "UnmappedNotInMap": status_counts["UNMAPPED_NOT_IN_MAP"],
        "UnresolvedRelative": status_counts["UNRESOLVED_RELATIVE"],
        "Ambiguous": status_counts["AMBIGUOUS"],
        "OutputCsv": str(output_csv),
    }
    return summary


def main() -> int:
    """Parse CLI arguments, generate a plan, and print its summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--links-csv", type=Path, required=True, help="Input extracted links.csv")
    parser.add_argument("--migration-map", type=Path, required=True, help="Input file-migration-map.csv")
    parser.add_argument("--output-csv", type=Path, required=True, help="Output link-rewrite-plan.csv")
    args = parser.parse_args()

    summary = plan_rewrites(
        links_csv=args.links_csv,
        migration_map_csv=args.migration_map,
        output_csv=args.output_csv,
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
