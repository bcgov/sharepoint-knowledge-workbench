"""Export an offline CSV link inventory from downloaded pages/documents/page fields.

Purpose:
    Extract supported URL-bearing content into CSV inventory rows for offline
    review and later link remediation.

Usage: python export_link_inventory.py --source-dir downloads --output-dir links
       python export_link_inventory.py --manifest-csv downloads.csv --output-dir links

No network or source mutations. Static markup, OOXML external relationships and
modern-page .page.json field exports are supported. PDFs are explicitly unsupported.

Key Input Dependencies:
    - Downloaded files under --source-dir, or a CSV manifest passed with --manifest-csv.
    - Optional path/base URL and format filters supplied by the caller.

Function Index:
    normalize_sharepoint_url, MarkupLinks.__init__, MarkupLinks.handle_starttag,
    markup_urls, _mapping_field_urls, _embedded_field_urls, field_urls,
    read_webpart_xml, _read_page_json,
    _read_webpart_json, _read_office_relationships, read_links, write_csv,
    _manifest_inputs, _directory_inputs, _process_source, run, main
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import zipfile
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from xml.etree import ElementTree

# Ensure script directory is on sys.path for direct invocation
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from link_extraction import classify


LINK_COLUMNS = [
    "SourceUrl",
    "WebUrl",
    "LibraryTitle",
    "RelativePath",
    "ServerRelativeUrl",
    "LocalPath",
    "SourcePart",
    "RawUrl",
    "ResolvedUrl",
    "LinkKind",
    "OccurrenceCount",
]
SOURCE_COLUMNS = ["SourceUrl", "LocalPath", "Format", "Status", "LinkCount", "Message"]
SUPPORTED = {".html", ".htm", ".aspx", ".docx", ".xlsx", ".pptx", ".pdf", ".webpart", ".dwp", ".xml", ".json", ".txt"}


def normalize_sharepoint_url(raw_url: str) -> str:
    """Normalize and unescape SharePoint URL encodings (HTML entities, Unicode escapes, and URI percent encodings)."""
    if not raw_url:
        return ""
    val = raw_url.strip()
    # Unescape HTML entities (e.g. &amp;, &#58;, &#47;)
    val = html.unescape(val)
    # Unescape literal JSON/Unicode sequences like \u002f or \u003a
    if "\\u00" in val:
        val = re.sub(r'\\u00([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1), 16)), val)
    return val.strip()


class MarkupLinks(HTMLParser):
    """Read explicit HTML link attributes, including unquoted values and entities."""

    def __init__(self):
        """Initialize the HTML parser and its extracted URL collection."""
        super().__init__(convert_charrefs=True)
        self.urls = []

    def handle_starttag(self, tag, attrs):
        """Collect navigational attributes and CSS url() values from one tag."""
        for name, value in attrs:
            if name.lower() in {"href", "src", "action", "url"} and value:
                norm = normalize_sharepoint_url(value)
                if norm:
                    self.urls.append(norm)
            elif name.lower() == "style" and value and "url(" in value.lower():
                # Extract CSS background-image url(...)
                for match in re.finditer(r'url\s*\(\s*[\'"]?([^\'")]+)[\'"]?\s*\)', value, re.IGNORECASE):
                    norm = normalize_sharepoint_url(match.group(1))
                    if norm:
                        self.urls.append(norm)

    handle_startendtag = handle_starttag


def markup_urls(text):
    """Extract normalized URLs from markup link attributes."""
    if not text:
        return []
    parser = MarkupLinks()
    parser.feed(text)
    return parser.urls


def _mapping_field_urls(value: dict):
    """Extract links from JSON properties and recurse through other values."""
    for key, child in value.items():
        if isinstance(child, str) and key.lower().endswith(
            ("url", "href", "src", "imagesource", "serverrelativeurl", "contentlink")
        ):
            normalized = normalize_sharepoint_url(child)
            if normalized:
                yield normalized
        else:
            yield from field_urls(child)


def _embedded_field_urls(value: str):
    """Extract markup links and recursively inspect serialized JSON strings."""
    yield from markup_urls(value)
    if not value.lstrip().startswith(("[", "{")):
        return
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return
    yield from field_urls(parsed)


def field_urls(value):
    """Read HTML plus URL-bearing properties in exported page/web-part/list-item JSON."""
    if isinstance(value, dict):
        yield from _mapping_field_urls(value)
    elif isinstance(value, list):
        for child in value:
            yield from field_urls(child)
    elif isinstance(value, str):
        yield from _embedded_field_urls(value)


def read_webpart_xml(content: str) -> list[tuple[str, str]]:
    """Extract links and ContentLink references from classic SP2016 .webpart / .dwp XML."""
    found = []
    # Search for ContentLink / Content XML tags and properties
    for tag_match in re.finditer(r'<(?:\w+:)?(?:ContentLink|property\b[^>]*name=["\']ContentLink["\'])[^>]*>(.*?)</(?:\w+:)?(?:ContentLink|property)>', content, re.IGNORECASE | re.DOTALL):
        link_val = normalize_sharepoint_url(tag_match.group(1))
        if link_val:
            found.append(("ContentLink", link_val))
    for content_match in re.finditer(r'<(?:\w+:)?(?:Content|property\b[^>]*name=["\']Content["\'])[^>]*>(.*?)</(?:\w+:)?(?:Content|property)>', content, re.IGNORECASE | re.DOTALL):
        inner_html = content_match.group(1)
        # Unwrap CDATA
        cdata_match = re.search(r'<!\[CDATA\[(.*?)\]\]>', inner_html, re.DOTALL)
        if cdata_match:
            inner_html = cdata_match.group(1)
        for url in markup_urls(inner_html):
            found.append(("Content", url))
    return found


def _read_page_json(path: Path) -> tuple[list[tuple[str, str]], dict]:
    """Read URL-bearing fields and source metadata from a modern page export."""
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    fields = payload.get("Fields", {})
    return [(name, url) for name, value in fields.items() for url in field_urls(value)], payload


def _read_webpart_json(path: Path) -> tuple[list[tuple[str, str]], dict]:
    """Extract links from a web-part behavior JSON export."""
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    found = []
    if isinstance(payload, list):
        for webpart in payload:
            webpart_id = webpart.get("WebPartId", webpart.get("Id", "webpart"))
            content = webpart.get("Content", webpart.get("sampleContent", ""))
            if content:
                found.extend((f"WebPart:{webpart_id}", url) for url in markup_urls(content))
            if webpart.get("ContentLink"):
                found.append((
                    f"WebPart:{webpart_id}:ContentLink",
                    normalize_sharepoint_url(webpart["ContentLink"]),
                ))
    return found, {}


def _read_office_relationships(path: Path) -> tuple[list[tuple[str, str]], dict]:
    """Extract external relationship targets from an Office Open XML archive."""
    found = []
    with zipfile.ZipFile(path) as archive:
        for part in archive.namelist():
            if not part.endswith(".rels"):
                continue
            for relation in ElementTree.fromstring(archive.read(part)):
                if relation.attrib.get("TargetMode") != "External" or not relation.attrib.get("Target"):
                    continue
                normalized = normalize_sharepoint_url(relation.attrib["Target"])
                if normalized:
                    found.append((part, normalized))
    return found, {}


def read_links(path):
    """Return (source-part, URL) pairs and optional modern-page source metadata."""
    if path.name.endswith(".page.json"):
        return _read_page_json(path)
    
    # Check for webpart-content.json (from sharepoint-analyze-webpart-behavior)
    if path.name == "webpart-content.json" or path.name.endswith(".webparts.json"):
        return _read_webpart_json(path)

    suffix = path.suffix.lower()
    if suffix in {".html", ".htm", ".aspx", ".txt"}:
        return [("markup", url) for url in markup_urls(path.read_text(encoding="utf-8-sig"))], {}

    if suffix in {".webpart", ".dwp"} or (suffix == ".xml" and "webpart" in path.name.lower()):
        return read_webpart_xml(path.read_text(encoding="utf-8-sig")), {}

    if suffix in {".docx", ".xlsx", ".pptx"}:
        return _read_office_relationships(path)

    if suffix == ".json":
        # Generic list-item or schema JSON export
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        return [("json-field", url) for url in field_urls(payload)], {}

    raise NotImplementedError(f"Link parsing for {suffix or 'extensionless files'} is not supported")


def write_csv(path, rows, columns):
    """Write inventory rows with a UTF-8 BOM for spreadsheet compatibility."""
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _manifest_inputs(
    manifest_csv: Path,
    local_root_path: Path | None,
    path_column: str | None,
    allowed_formats: set[str] | None,
) -> list[dict]:
    """Resolve local files and apply format filters to manifest rows."""
    with manifest_csv.open(encoding="utf-8-sig", newline="") as handle:
        raw_inputs = list(csv.DictReader(handle))
    inputs = []
    for row in raw_inputs:
        local = ""
        if path_column and row.get(path_column):
            candidate = row[path_column]
            local = str(local_root_path / candidate.lstrip("/\\")) if local_root_path else candidate
        elif row.get("LocalPath"):
            candidate = row["LocalPath"]
            local = str(local_root_path / candidate.lstrip("/\\")) if local_root_path and not Path(candidate).is_absolute() else candidate
        elif local_root_path:
            for column in ("RelativePath", "LibraryRelativePath", "ServerRelativeUrl"):
                if row.get(column):
                    local = str(local_root_path / row[column].lstrip("/\\"))
                    break
        if local and not Path(local).is_absolute() and not local_root_path:
            local = str(manifest_csv.parent / local)
        row["LocalPath"] = local
        extension = Path(local).suffix.lower() if local else (
            f".{row['FileExtension'].lower().lstrip('.')}" if row.get("FileExtension") else ""
        )
        if allowed_formats and extension not in allowed_formats:
            continue
        inputs.append(row)
    return inputs


def _directory_inputs(
    source_dir: Path,
    output_dir: Path,
    base_url: str | None,
    allowed_formats: set[str] | None,
) -> list[dict]:
    """Enumerate supported downloaded files while excluding the output tree."""
    inputs = []
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file() or path.is_relative_to(output_dir):
            continue
        suffix = path.suffix.lower()
        if allowed_formats and suffix not in allowed_formats:
            continue
        if not allowed_formats and suffix not in SUPPORTED and not path.name.endswith(".page.json"):
            continue
        relative = path.relative_to(source_dir).as_posix()
        file_url = urljoin(base_url.rstrip("/") + "/", relative) if base_url else ""
        inputs.append({"LocalPath": str(path), "FileUrl": file_url, "Status": "DOWNLOADED"})
    return inputs


def _process_source(row: dict, skip_unsupported: bool) -> tuple[list[dict], dict, int]:
    """Extract one source file's links and return its status record."""
    local = row.get("LocalPath", "")
    source_url = row.get("FileUrl", row.get("SourceUrl", ""))
    extension = Path(local).suffix.lower() if local else ""
    record = {
        "SourceUrl": source_url, "LocalPath": local, "Format": extension,
        "Status": "EMPTY", "LinkCount": 0, "Message": "",
    }
    links = []
    failed = 0
    try:
        if row.get("Status", "DOWNLOADED") != "DOWNLOADED":
            raise OSError(f"Source download status: {row.get('Status')}")
        if not local:
            raise OSError("LocalPath is missing")
        found, metadata = read_links(Path(local))
        source_url = metadata.get("SourceUrl", source_url)
        record["SourceUrl"] = source_url
        occurrences = Counter(found)
        for (part, raw_url), count in occurrences.items():
            parsed = urlsplit(raw_url)
            resolved = urljoin(source_url, raw_url) if source_url else (raw_url if parsed.scheme else "")
            kind = (
                "non-navigational"
                if raw_url.startswith("#") or parsed.scheme.lower() in {"mailto", "tel", "javascript"}
                else classify(raw_url)
            )
            links.append({
                "SourceUrl": source_url,
                "WebUrl": metadata.get("WebUrl", row.get("WebUrl", "")),
                "LibraryTitle": metadata.get("LibraryTitle", row.get("LibraryTitle", "")),
                "RelativePath": metadata.get("RelativePath", row.get("RelativePath", "")),
                "ServerRelativeUrl": metadata.get("ServerRelativeUrl", row.get("ServerRelativeUrl", "")),
                "LocalPath": local,
                "SourcePart": part,
                "RawUrl": raw_url,
                "ResolvedUrl": resolved,
                "LinkKind": kind,
                "OccurrenceCount": count,
            })
        record["LinkCount"] = len(occurrences)
        if occurrences:
            record["Status"] = "OBSERVED"
    except NotImplementedError as exc:
        if not skip_unsupported:
            failed += 1
        record.update(Status="NOT_SUPPORTED", Message=str(exc))
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        failed += 1
        record.update(Status="FAILED", Message=str(exc))
    return links, record, failed


def run(
    *,
    output_dir,
    source_dir=None,
    manifest_csv=None,
    base_url=None,
    local_root=None,
    path_column=None,
    formats=None,
    skip_unsupported=False,
):
    """Analyze local inputs and preserve per-source read/format coverage in sources.csv."""
    if bool(source_dir) == bool(manifest_csv):
        raise ValueError("Supply exactly one of source_dir or manifest_csv")
    output_dir = Path(output_dir).resolve()
    local_root_path = Path(local_root).resolve() if local_root else None
    allowed_formats = {f.lower() if f.startswith(".") else f".{f.lower()}" for f in formats} if formats else None

    if manifest_csv:
        manifest_csv = Path(manifest_csv).resolve()
        inputs = _manifest_inputs(manifest_csv, local_root_path, path_column, allowed_formats)
    else:
        source_dir = Path(source_dir).resolve(strict=True)
        inputs = _directory_inputs(source_dir, output_dir, base_url, allowed_formats)
    links, sources = [], []
    failed = 0
    for row in inputs:
        source_links, record, source_failures = _process_source(row, skip_unsupported)
        links.extend(source_links)
        sources.append(record)
        failed += source_failures
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "links.csv", links, LINK_COLUMNS)
    write_csv(output_dir / "sources.csv", sources, SOURCE_COLUMNS)
    status = "FAILED" if inputs and failed == len(inputs) else "PARTIAL" if failed else "OBSERVED" if links else "EMPTY"
    report = {"Status": status, "SourceCount": len(sources), "LinkCount": len(links), "ProblemCount": failed,
              "Scope": "Explicit href/src/action/url attributes, Office external relationships, exported page HTML and URL-bearing JSON properties",
              "Exclusions": ["PDF and legacy binary Office formats", "CSS url(), srcset and script-generated URLs", "Live page collection", "Link resolution/validation and rewriting"]}
    (output_dir / "manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main():
    """Parse CLI options, run the local inventory export, and return its status."""
    parser = argparse.ArgumentParser(description=__doc__)
    sources = parser.add_mutually_exclusive_group(required=True)
    sources.add_argument("--source-dir", type=Path)
    sources.add_argument("--manifest-csv", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--base-url", help="Original remote directory URL when no source manifest is available")
    parser.add_argument("--local-root", type=Path, help="Base directory for resolving relative file paths in manifest CSV")
    parser.add_argument("--path-column", help="CSV column name containing the local or relative file path")
    parser.add_argument("--formats", help="Comma-separated file extensions to include (e.g. aspx,html,docx)")
    parser.add_argument("--skip-unsupported", action="store_true", help="Do not count unsupported file types as execution problems")
    args = parser.parse_args()
    formats_list = [f.strip() for f in args.formats.split(",")] if args.formats else None
    report = run(
        output_dir=args.output_dir,
        source_dir=args.source_dir,
        manifest_csv=args.manifest_csv,
        base_url=args.base_url,
        local_root=args.local_root,
        path_column=args.path_column,
        formats=formats_list,
        skip_unsupported=args.skip_unsupported,
    )
    print(json.dumps(report, indent=2))
    return 1 if report["Status"] in {"PARTIAL", "FAILED"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
