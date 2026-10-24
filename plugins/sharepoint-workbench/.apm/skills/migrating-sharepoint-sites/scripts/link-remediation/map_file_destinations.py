"""Purpose: Build a file destination map from explicit source and target parameters.

Key Input Dependencies: inventory CSV, source web/library/path, target site/library
root/folder, and optionally a normalized ``Destination Mapping`` worksheet for
read-only validation. No SharePoint connection or tenant write is performed.

Usage:
    python map_file_destinations.py --files-csv files.csv \\
        --source-web-url https://source.example/DivisionA \\
        --source-library-title "Administration Documents" \\
        --source-server-relative-prefix "/DivisionA/Administration Documents/" \\
        --target-site-url https://tenant.sharepoint.com/sites/Target \\
        --target-library-title divisiona \\
        --target-library-root-url /sites/Target/divisiona \\
        --target-folder-prefix "administrative documents" --aspx-to-html \\
        --output-csv file-migration-map.csv

Function index: normalize_server_path, _validate_path_segments, _normalize_web_url,
_encode_server_path, _is_under, _ensure_output_is_distinct, _cell_column_index,
_worksheet_path, _read_shared_strings, _worksheet_rows, _worksheet_records,
_read_xlsx_sheet, _truthy, validate_mapping_workbook, transform_filename,
_source_relative_file_path, _select_source_rows, _build_destination_row,
_write_mapping_csv, _normalize_source_scope, _normalize_target_scope,
_validate_inventory_counts, _build_destination_rows, map_destinations, main.
"""

from __future__ import annotations

import argparse
import csv
import json
import posixpath
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote, unquote, urlsplit
from xml.etree import ElementTree

# Ensure script directory is on sys.path for direct invocation
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

SHEET_NAME = "Destination Mapping"
WORKBOOK_COLUMNS = (
    "SourceWebUrl",
    "SourceLibraryTitle",
    "SourceServerRelativePrefix",
    "TargetSiteUrl",
    "TargetLibraryTitle",
    "TargetLibraryRootUrl",
    "TargetFolderPrefix",
    "RenameAspxToHtml",
)
SPREADSHEET_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
DOCUMENT_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
OUTPUT_COLUMNS = [
    "SourceSiteUrl",
    "SourceWebUrl",
    "SourceLibraryTitle",
    "SourceServerRelativeUrl",
    "SourceFileUrl",
    "TargetSiteUrl",
    "TargetLibraryTitle",
    "TargetFolderPath",
    "TargetFileName",
    "TargetServerRelativeUrl",
    "TargetFileUrl",
    "MappingSource",
]


def normalize_server_path(value: str) -> str:
    """Normalize a server-relative path to decoded forward-slash form."""
    path = unquote((value or "").strip().replace("\\", "/"))
    return "/" + "/".join(part for part in path.split("/") if part)


def _validate_path_segments(value: str, label: str) -> None:
    """Reject navigation segments in caller-supplied SharePoint paths."""
    if any(part in {".", ".."} for part in value.replace("\\", "/").split("/")):
        raise ValueError(f"{label} cannot contain '.' or '..' path segments")


def _normalize_web_url(value: str) -> str:
    """Normalize web URLs for exact, case-insensitive source matching."""
    parsed = urlsplit((value or "").strip())
    if not parsed.scheme or not parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError(f"Expected a site/web URL without query or fragment: {value!r}")
    path = normalize_server_path(parsed.path).rstrip("/")
    return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}{path}".rstrip("/")


def _encode_server_path(value: str) -> str:
    """Percent-encode each path segment without encoding its separators."""
    decoded = normalize_server_path(value)
    return "/".join(quote(part, safe="-._~!$&'()*+,;=:@") for part in decoded.split("/"))


def _is_under(path: str, prefix: str) -> bool:
    """Return whether a normalized path is the prefix or a child of it."""
    candidate = normalize_server_path(path).casefold()
    root = normalize_server_path(prefix).rstrip("/").casefold()
    return candidate == root or candidate.startswith(root + "/")


def _ensure_output_is_distinct(output_path: Path, input_paths: List[Path]) -> None:
    """Prevent an output CSV from overwriting any source or validation input."""
    for input_path in input_paths:
        if output_path == input_path or (
            output_path.exists() and output_path.samefile(input_path)
        ):
            raise ValueError(
                f"output path must differ from every input file: {output_path}"
            )


def _cell_column_index(reference: str) -> int:
    """Convert an XLSX A1 column reference to a zero-based index."""
    letters = "".join(character for character in reference if character.isalpha()).upper()
    result = 0
    for letter in letters:
        result = result * 26 + ord(letter) - ord("A") + 1
    return result - 1


def _worksheet_path(archive: zipfile.ZipFile, sheet_name: str) -> str:
    """Resolve a worksheet name to a safe path within an XLSX archive."""
    spreadsheet_tag = f"{{{SPREADSHEET_NS}}}"
    relationship_tag = f"{{{DOCUMENT_REL_NS}}}id"
    workbook_root = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    sheet = next(
        (item for item in workbook_root.findall(f".//{spreadsheet_tag}sheet")
         if item.get("name") == sheet_name),
        None,
    )
    if sheet is None:
        raise ValueError(f"Workbook is missing the {sheet_name!r} worksheet")

    relationship_id = sheet.get(relationship_tag)
    relationships_root = ElementTree.fromstring(
        archive.read("xl/_rels/workbook.xml.rels")
    )
    relationship = next(
        (item for item in relationships_root.findall(f"{{{PACKAGE_REL_NS}}}Relationship")
         if item.get("Id") == relationship_id),
        None,
    )
    if relationship is None:
        raise ValueError(f"Cannot resolve worksheet {sheet_name!r} in workbook")
    target = relationship.get("Target", "")
    sheet_path = posixpath.normpath(
        target.lstrip("/") if target.startswith("/")
        else posixpath.join("xl", target)
    )
    if sheet_path.startswith("../") or sheet_path not in archive.namelist():
        raise ValueError(f"Invalid worksheet path in workbook: {sheet_path}")
    return sheet_path


def _read_shared_strings(archive: zipfile.ZipFile) -> List[str]:
    """Read shared strings from an XLSX archive when present."""
    shared_path = "xl/sharedStrings.xml"
    if shared_path not in archive.namelist():
        return []
    spreadsheet_tag = f"{{{SPREADSHEET_NS}}}"
    shared_root = ElementTree.fromstring(archive.read(shared_path))
    return [
        "".join(node.text or "" for node in item.findall(f".//{spreadsheet_tag}t"))
        for item in shared_root.findall(f"{spreadsheet_tag}si")
    ]


def _worksheet_rows(
    root: ElementTree.Element,
    shared_strings: List[str],
) -> List[List[str]]:
    """Decode worksheet rows from inline and shared-string cell formats."""
    spreadsheet_tag = f"{{{SPREADSHEET_NS}}}"
    rows: List[List[str]] = []
    for row in root.findall(f".//{spreadsheet_tag}sheetData/{spreadsheet_tag}row"):
        values: List[str] = []
        for cell in row.findall(f"{spreadsheet_tag}c"):
            index = _cell_column_index(cell.get("r", "A1"))
            while len(values) <= index:
                values.append("")
            cell_type = cell.get("t")
            if cell_type == "inlineStr":
                value = "".join(
                    node.text or "" for node in cell.findall(f".//{spreadsheet_tag}t")
                )
            else:
                raw_value = cell.find(f"{spreadsheet_tag}v")
                value = raw_value.text if raw_value is not None else ""
                if cell_type == "s" and value:
                    value = shared_strings[int(value)]
            values[index] = value.strip()
        rows.append(values)
    return rows


def _worksheet_records(
    rows: List[List[str]],
    sheet_name: str,
) -> List[Dict[str, str]]:
    """Validate worksheet headers and return non-empty records."""
    header_index = next((index for index, row in enumerate(rows) if any(row)), None)
    if header_index is None:
        raise ValueError(f"Worksheet {sheet_name!r} is empty")
    headers = rows[header_index]
    missing = [column for column in WORKBOOK_COLUMNS if column not in headers]
    if missing:
        raise ValueError(
            f"Worksheet {sheet_name!r} is missing required columns: {', '.join(missing)}"
        )
    if len(set(headers)) != len(headers):
        nonempty_headers = [header for header in headers if header]
        if len(set(nonempty_headers)) != len(nonempty_headers):
            raise ValueError(f"Worksheet {sheet_name!r} contains duplicate column names")

    return [
        {header: row[index] if index < len(row) else "" for index, header in enumerate(headers)}
        for row in rows[header_index + 1:]
        if any(row)
    ]


def _read_xlsx_sheet(workbook_path: Path, sheet_name: str) -> List[Dict[str, str]]:
    """Read and validate a named worksheet using only the Python standard library."""
    try:
        with zipfile.ZipFile(workbook_path) as archive:
            sheet_path = _worksheet_path(archive, sheet_name)
            shared_strings = _read_shared_strings(archive)
            root = ElementTree.fromstring(archive.read(sheet_path))
    except (OSError, zipfile.BadZipFile, KeyError, ElementTree.ParseError) as exc:
        raise ValueError(f"Unable to read mapping workbook {workbook_path}: {exc}") from exc
    return _worksheet_records(_worksheet_rows(root, shared_strings), sheet_name)


def _truthy(value: str) -> bool:
    """Parse the explicit true/false values accepted in the workbook mapping."""
    normalized = (value or "").strip().casefold()
    if normalized in {"true", "yes", "y", "1"}:
        return True
    if normalized in {"false", "no", "n", "0"}:
        return False
    raise ValueError(f"RenameAspxToHtml must be true or false, got {value!r}")


def validate_mapping_workbook(
    workbook_path: Path,
    mapping: Dict[str, Any],
) -> str:
    """Require exactly one workbook row to match the explicit CLI mapping."""
    rows = _read_xlsx_sheet(Path(workbook_path).resolve(strict=True), SHEET_NAME)
    expected = {
        "SourceWebUrl": _normalize_web_url(mapping["source_web_url"]).casefold(),
        "SourceLibraryTitle": str(mapping["source_library_title"]).strip().casefold(),
        "SourceServerRelativePrefix": normalize_server_path(
            mapping["source_server_relative_prefix"]
        ).casefold(),
        "TargetSiteUrl": _normalize_web_url(mapping["target_site_url"]).casefold(),
        "TargetLibraryTitle": str(mapping["target_library_title"]).strip().casefold(),
        "TargetLibraryRootUrl": normalize_server_path(
            mapping["target_library_root_url"]
        ).casefold(),
        "TargetFolderPrefix": normalize_server_path(
            mapping["target_folder_prefix"]
        ).strip("/").casefold(),
        "RenameAspxToHtml": bool(mapping["aspx_to_html"]),
    }
    matches = []
    for row in rows:
        actual = {
            "SourceWebUrl": _normalize_web_url(row["SourceWebUrl"]).casefold(),
            "SourceLibraryTitle": row["SourceLibraryTitle"].strip().casefold(),
            "SourceServerRelativePrefix": normalize_server_path(
                row["SourceServerRelativePrefix"]
            ).casefold(),
            "TargetSiteUrl": _normalize_web_url(row["TargetSiteUrl"]).casefold(),
            "TargetLibraryTitle": row["TargetLibraryTitle"].strip().casefold(),
            "TargetLibraryRootUrl": normalize_server_path(
                row["TargetLibraryRootUrl"]
            ).casefold(),
            "TargetFolderPrefix": normalize_server_path(
                row["TargetFolderPrefix"]
            ).strip("/").casefold(),
            "RenameAspxToHtml": _truthy(row["RenameAspxToHtml"]),
        }
        if actual == expected:
            matches.append(row)
    if len(matches) != 1:
        raise ValueError(
            f"Explicit mapping does not match exactly one row in {SHEET_NAME!r}; "
            f"found {len(matches)} matches"
        )
    return str(matches[0].get("MappingId", "matched workbook row"))


def transform_filename(filename: str, rename_aspx_to_html: bool = False) -> str:
    """Apply the explicit .aspx-to-.html transformation when requested."""
    if rename_aspx_to_html and filename.casefold().endswith(".aspx"):
        return filename[:-5] + ".html"
    return filename


def _source_relative_file_path(
    row: Dict[str, str],
    container_root: str,
    source_prefix: str,
) -> str:
    """Return a selected file path relative to the source prefix or library root."""
    server_path = normalize_server_path(row.get("ServerRelativeUrl", ""))
    base = source_prefix or container_root
    if not _is_under(server_path, base):
        raise ValueError(f"Inventory path is outside the selected source scope: {server_path}")
    return server_path[len(normalize_server_path(base).rstrip("/")):].lstrip("/")


def _select_source_rows(
    inventory_rows: List[Dict[str, str]],
    source_web: str,
    source_library: str,
    container_root: str,
    source_prefix: str,
) -> List[Dict[str, str]]:
    """Select inventory rows matching one exact source web/library scope."""
    selected = []
    for row in inventory_rows:
        row_web = row.get("WebUrl", "").strip()
        if not row_web or _normalize_web_url(row_web) != source_web:
            continue
        if row.get("LibraryTitle", "").strip().casefold() != source_library.casefold():
            continue
        server_path = normalize_server_path(row.get("ServerRelativeUrl", ""))
        if source_prefix and not _is_under(server_path, source_prefix):
            continue
        if not _is_under(server_path, container_root):
            raise ValueError(f"Inventory path is outside its declared source library: {server_path}")
        selected.append(row)
    return selected


def _build_destination_row(
    row: Dict[str, str],
    source_library: str,
    target_site: str,
    target_library: str,
    target_library_root: str,
    target_folder: str,
    container_root: str,
    source_prefix: str,
    aspx_to_html: bool,
    mapping_source: str,
) -> tuple[Dict[str, str], bool]:
    """Build one source-to-target inventory row and report extension conversion."""
    source_server_rel = normalize_server_path(row.get("ServerRelativeUrl", ""))
    relative_file = _source_relative_file_path(row, container_root, source_prefix)
    relative_parts = relative_file.split("/")
    source_filename = row.get("FileName", "").strip() or relative_parts[-1]
    if "/" in source_filename or "\\" in source_filename or source_filename in {".", ".."}:
        raise ValueError(f"Invalid file name in inventory: {source_filename!r}")
    target_filename = transform_filename(source_filename, aspx_to_html)
    relative_folder = "/".join(relative_parts[:-1])
    target_folder_path = "/".join(
        part for part in (target_folder, relative_folder) if part
    )
    _validate_path_segments(target_folder_path, "Target folder prefix")
    encoded_root = _encode_server_path(target_library_root)
    encoded_folder = _encode_server_path(target_folder_path).lstrip("/")
    encoded_filename = quote(target_filename, safe="-._~!$&'()*+,;=:@")
    target_path = "/".join(
        part for part in (encoded_root, encoded_folder, encoded_filename) if part
    )
    target_site_parts = urlsplit(target_site)
    target_full_url = f"{target_site_parts.scheme}://{target_site_parts.netloc}{target_path}"
    return {
        "SourceSiteUrl": row.get("SourceSiteUrl", ""),
        "SourceWebUrl": row.get("WebUrl", ""),
        "SourceLibraryTitle": source_library,
        "SourceServerRelativeUrl": source_server_rel,
        "SourceFileUrl": row.get("FileUrl", "").strip(),
        "TargetSiteUrl": target_site,
        "TargetLibraryTitle": target_library,
        "TargetFolderPath": target_folder_path,
        "TargetFileName": target_filename,
        "TargetServerRelativeUrl": target_path,
        "TargetFileUrl": target_full_url,
        "MappingSource": mapping_source,
    }, target_filename != source_filename


def _write_mapping_csv(output_csv: Path, rows: List[Dict[str, str]]) -> None:
    """Write the validated destination map as UTF-8 with a BOM for Excel."""
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _normalize_source_scope(
    source_web_url: str,
    source_library_title: str,
    source_server_relative_prefix: str,
) -> tuple[str, str, str, str]:
    """Normalize the selected source web, library, and optional folder prefix."""
    source_web = _normalize_web_url(source_web_url)
    source_library = source_library_title.strip()
    if not source_library:
        raise ValueError("Source library title is required")
    source_prefix = (
        normalize_server_path(source_server_relative_prefix).rstrip("/")
        if source_server_relative_prefix.strip()
        else ""
    )
    _validate_path_segments(source_prefix, "Source path prefix")
    container_root = normalize_server_path(
        urlsplit(source_web).path + "/" + source_library
    )
    return source_web, source_library, container_root, source_prefix


def _normalize_target_scope(
    target_site_url: str,
    target_library_title: str,
    target_library_root_url: str,
    target_folder_prefix: str,
) -> tuple[str, str, str, str]:
    """Normalize and validate the selected target site, library, and folder."""
    target_site = _normalize_web_url(target_site_url)
    target_library = target_library_title.strip()
    if not target_library:
        raise ValueError("Target library title is required")
    site_path = normalize_server_path(urlsplit(target_site).path).rstrip("/")
    target_library_root = normalize_server_path(target_library_root_url)
    _validate_path_segments(target_library_root, "Target library root")
    if (
        not target_library_root.startswith("/")
        or not _is_under(target_library_root, site_path)
        or target_library_root.rstrip("/").casefold() == site_path.casefold()
    ):
        raise ValueError(
            "Target library root must be a server-relative path below the target site URL"
        )
    target_folder = normalize_server_path(target_folder_prefix).strip("/")
    _validate_path_segments(target_folder, "Target folder prefix")
    return target_site, target_library, target_library_root, target_folder


def _validate_inventory_counts(
    selected: List[Dict[str, str]],
    expected_source_files: Optional[int],
    expected_aspx_count: Optional[int],
) -> int:
    """Validate selected inventory size and return its ASPX file count."""
    if not selected:
        raise ValueError("No inventory files matched the explicit source container parameters")
    aspx_count = sum(
        row.get("FileName", "").casefold().endswith(".aspx")
        or row.get("FileExtension", "").strip().casefold().lstrip(".") == "aspx"
        for row in selected
    )
    if expected_source_files is not None and len(selected) != expected_source_files:
        raise ValueError(
            f"Expected {expected_source_files} source files, found {len(selected)}"
        )
    if expected_aspx_count is not None and aspx_count != expected_aspx_count:
        raise ValueError(f"Expected {expected_aspx_count} ASPX files, found {aspx_count}")
    return aspx_count


def _build_destination_rows(
    selected: List[Dict[str, str]],
    source_library: str,
    target_site: str,
    target_library: str,
    target_library_root: str,
    target_folder: str,
    container_root: str,
    source_prefix: str,
    aspx_to_html: bool,
    mapping_source: str,
) -> tuple[List[Dict[str, str]], int]:
    """Build destination rows and reject duplicate source or target paths."""
    mapped_rows: List[Dict[str, str]] = []
    source_paths: set[str] = set()
    target_paths: set[str] = set()
    renamed_count = 0
    for row in selected:
        source_server_rel = normalize_server_path(row.get("ServerRelativeUrl", ""))
        source_key = source_server_rel.casefold()
        if source_key in source_paths:
            raise ValueError(f"Duplicate source path in inventory: {source_server_rel}")
        source_paths.add(source_key)
        mapped_row, renamed = _build_destination_row(
            row,
            source_library,
            target_site,
            target_library,
            target_library_root,
            target_folder,
            container_root,
            source_prefix,
            aspx_to_html,
            mapping_source,
        )
        target_key = unquote(mapped_row["TargetServerRelativeUrl"]).casefold()
        if target_key in target_paths:
            raise ValueError(
                "Multiple source files map to the same target path: "
                f"{mapped_row['TargetServerRelativeUrl']}"
            )
        target_paths.add(target_key)
        renamed_count += renamed
        mapped_rows.append(mapped_row)
    return mapped_rows, renamed_count


def map_destinations(
    files_csv: Path,
    output_csv: Path,
    source_web_url: str,
    source_library_title: str,
    target_site_url: str,
    target_library_title: str,
    target_library_root_url: str,
    target_folder_prefix: str = "",
    source_server_relative_prefix: str = "",
    aspx_to_html: bool = False,
    expected_source_files: Optional[int] = None,
    expected_aspx_count: Optional[int] = None,
    mapping_workbook: Optional[Path] = None,
) -> Dict[str, Any]:
    """Map exactly the selected source container to the supplied target location."""
    files_csv = Path(files_csv).resolve(strict=True)
    output_csv = Path(output_csv).resolve()
    input_paths = [files_csv]
    workbook_path = (
        Path(mapping_workbook).resolve(strict=True)
        if mapping_workbook is not None
        else None
    )
    if workbook_path is not None:
        input_paths.append(workbook_path)
    _ensure_output_is_distinct(output_csv, input_paths)
    source_web, source_library, container_root, source_prefix = _normalize_source_scope(
        source_web_url, source_library_title, source_server_relative_prefix
    )
    target_site, target_library, target_library_root, target_folder = (
        _normalize_target_scope(
            target_site_url,
            target_library_title,
            target_library_root_url,
            target_folder_prefix,
        )
    )
    mapping_values = {
        "source_web_url": source_web_url,
        "source_library_title": source_library,
        "source_server_relative_prefix": source_prefix or container_root,
        "target_site_url": target_site,
        "target_library_title": target_library,
        "target_library_root_url": target_library_root,
        "target_folder_prefix": target_folder,
        "aspx_to_html": aspx_to_html,
    }
    workbook_validation = "NOT_REQUESTED"
    mapping_source = "explicit CLI parameters"
    if workbook_path is not None:
        mapping_source = validate_mapping_workbook(workbook_path, mapping_values)
        workbook_validation = "MATCHED"

    with files_csv.open(encoding="utf-8-sig", newline="") as handle:
        inventory_rows = list(csv.DictReader(handle))
    selected = _select_source_rows(
        inventory_rows, source_web, source_library, container_root, source_prefix
    )
    aspx_count = _validate_inventory_counts(
        selected, expected_source_files, expected_aspx_count
    )
    mapped_rows, renamed_count = _build_destination_rows(
        selected,
        source_library,
        target_site,
        target_library,
        target_library_root,
        target_folder,
        container_root,
        source_prefix,
        aspx_to_html,
        mapping_source,
    )
    _write_mapping_csv(output_csv, mapped_rows)

    return {
        "Status": "COMPLETED",
        "MappedFiles": len(mapped_rows),
        "AspxFiles": aspx_count,
        "AspxRenamed": renamed_count,
        "WorkbookValidation": workbook_validation,
        "OutputCsv": str(output_csv),
    }


def main() -> int:
    """Parse CLI arguments, map the selected inventory container, and print its summary."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--files-csv", type=Path, required=True, help="Input source inventory files.csv")
    parser.add_argument("--output-csv", type=Path, required=True, help="Output file-migration-map.csv")
    parser.add_argument("--source-web-url", required=True, help="Exact source SharePoint web URL")
    parser.add_argument("--source-library-title", required=True, help="Exact source library title")
    parser.add_argument("--source-server-relative-prefix", default="", help="Optional source folder prefix")
    parser.add_argument("--target-site-url", required=True, help="Target SPO site collection URL")
    parser.add_argument("--target-library-title", required=True, help="Target library display title")
    parser.add_argument("--target-library-root-url", required=True, help="Target library server-relative root URL")
    parser.add_argument("--target-folder-prefix", default="", help="Optional folder below the target library")
    parser.add_argument("--aspx-to-html", action="store_true", help="Rename selected .aspx files to .html")
    parser.add_argument("--expected-source-files", type=int, help="Fail unless this many source files match")
    parser.add_argument("--expected-aspx-count", type=int, help="Fail unless this many selected files are .aspx")
    parser.add_argument("--mapping-workbook", type=Path, help="Optional workbook for read-only mapping validation")
    args = parser.parse_args()

    summary = map_destinations(
        files_csv=args.files_csv,
        output_csv=args.output_csv,
        source_web_url=args.source_web_url,
        source_library_title=args.source_library_title,
        target_site_url=args.target_site_url,
        target_library_title=args.target_library_title,
        target_library_root_url=args.target_library_root_url,
        target_folder_prefix=args.target_folder_prefix,
        source_server_relative_prefix=args.source_server_relative_prefix,
        aspx_to_html=args.aspx_to_html,
        expected_source_files=args.expected_source_files,
        expected_aspx_count=args.expected_aspx_count,
        mapping_workbook=args.mapping_workbook,
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
