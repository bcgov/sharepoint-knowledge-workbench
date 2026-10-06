"""Export an offline CSV link inventory from downloaded pages/documents/page fields.

Usage: python export_link_inventory.py --source-dir downloads --output-dir links
       python export_link_inventory.py --manifest-csv downloads.csv --output-dir links

No network or source mutations. Static markup, OOXML external relationships and
modern-page .page.json field exports are supported. PDFs are explicitly unsupported.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
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


LINK_COLUMNS = ["SourceUrl", "WebUrl", "LibraryTitle", "LocalPath", "SourcePart", "RawUrl", "ResolvedUrl", "LinkKind", "OccurrenceCount"]
SOURCE_COLUMNS = ["SourceUrl", "LocalPath", "Format", "Status", "LinkCount", "Message"]
SUPPORTED = {".html", ".htm", ".aspx", ".docx", ".xlsx", ".pptx", ".pdf"}


class MarkupLinks(HTMLParser):
    """Read explicit HTML link attributes, including unquoted values and entities."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name.lower() in {"href", "src", "action", "url"} and value:
                self.urls.append(value.strip())

    handle_startendtag = handle_starttag


def markup_urls(text):
    parser = MarkupLinks()
    parser.feed(text)
    return parser.urls


def field_urls(value):
    """Read HTML plus URL-bearing properties in exported page/web-part JSON."""
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(child, str) and key.lower().endswith(("url", "href", "src", "imagesource")):
                if child.strip():
                    yield html.unescape(child.strip())
            else:
                yield from field_urls(child)
    elif isinstance(value, list):
        for child in value:
            yield from field_urls(child)
    elif isinstance(value, str):
        yield from markup_urls(value)
        if value.lstrip().startswith(("[", "{")):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                return
            yield from field_urls(parsed)


def read_links(path):
    """Return (source-part, URL) pairs and optional modern-page source metadata."""
    if path.name.endswith(".page.json"):
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        fields = payload["Fields"]
        return [(name, url) for name, value in fields.items() for url in field_urls(value)], payload
    suffix = path.suffix.lower()
    if suffix in {".html", ".htm", ".aspx"}:
        return [("markup", url) for url in markup_urls(path.read_text(encoding="utf-8-sig"))], {}
    if suffix in {".docx", ".xlsx", ".pptx"}:
        found = []
        with zipfile.ZipFile(path) as archive:
            for part in archive.namelist():
                if not part.endswith(".rels"):
                    continue
                for relation in ElementTree.fromstring(archive.read(part)):
                    if relation.attrib.get("TargetMode") == "External" and relation.attrib.get("Target"):
                        found.append((part, relation.attrib["Target"]))
        return found, {}
    raise NotImplementedError(f"Link parsing for {suffix or 'extensionless files'} is not supported")


def write_csv(path, rows, columns):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


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
        with manifest_csv.open(encoding="utf-8-sig", newline="") as handle:
            raw_inputs = list(csv.DictReader(handle))
        inputs = []
        for row in raw_inputs:
            # Auto-discover local file path if path_column not specified
            local = ""
            if path_column and row.get(path_column):
                candidate = row[path_column]
                local = str(local_root_path / candidate.lstrip("/\\")) if local_root_path else candidate
            elif row.get("LocalPath"):
                candidate = row["LocalPath"]
                local = str(local_root_path / candidate.lstrip("/\\")) if local_root_path and not Path(candidate).is_absolute() else candidate
            elif local_root_path:
                for col in ("RelativePath", "LibraryRelativePath", "ServerRelativeUrl"):
                    if row.get(col):
                        local = str(local_root_path / row[col].lstrip("/\\"))
                        break

            if local and not Path(local).is_absolute() and not local_root_path:
                local = str(manifest_csv.parent / local)

            row["LocalPath"] = local

            ext = Path(local).suffix.lower() if local else (f".{row['FileExtension'].lower().lstrip('.')}" if row.get("FileExtension") else "")
            if allowed_formats and ext not in allowed_formats:
                continue
            inputs.append(row)
    else:
        source_dir = Path(source_dir).resolve(strict=True)
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
            inputs.append({"LocalPath": str(path), "FileUrl": urljoin(base_url.rstrip("/") + "/", relative) if base_url else "", "Status": "DOWNLOADED"})
    links, sources = [], []
    failed = 0
    for row in inputs:
        local = row.get("LocalPath", "")
        source_url = row.get("FileUrl", row.get("SourceUrl", ""))
        ext = Path(local).suffix.lower() if local else ""
        record = {"SourceUrl": source_url, "LocalPath": local, "Format": ext, "Status": "EMPTY", "LinkCount": 0, "Message": ""}
        try:
            if row.get("Status", "DOWNLOADED") != "DOWNLOADED":
                raise OSError(f"Source download status: {row.get('Status')}")
            if not local:
                raise OSError("LocalPath is missing")
            found, metadata = read_links(Path(local))
            source_url = metadata.get("SourceUrl", source_url)
            record["SourceUrl"] = source_url
            occurrences = Counter(found)
            for (part, raw), count in occurrences.items():
                parsed = urlsplit(raw)
                resolved = urljoin(source_url, raw) if source_url else (raw if parsed.scheme else "")
                kind = "non-navigational" if raw.startswith("#") or parsed.scheme.lower() in {"mailto", "tel", "javascript"} else classify(raw)
                links.append({"SourceUrl": source_url, "WebUrl": metadata.get("WebUrl", row.get("WebUrl", "")), "LibraryTitle": metadata.get("LibraryTitle", row.get("LibraryTitle", "")), "LocalPath": local, "SourcePart": part, "RawUrl": raw, "ResolvedUrl": resolved, "LinkKind": kind, "OccurrenceCount": count})
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
        sources.append(record)
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
