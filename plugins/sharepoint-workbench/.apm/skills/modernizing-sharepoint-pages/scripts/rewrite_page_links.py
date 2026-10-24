#!/usr/bin/env python3
"""Rewrite SP2016 links in a converted page to relative links on the target site.

Purpose:
    A migrated page keeps its content, but links to files that were already migrated must
    open the SharePoint Online copy. Each href/src that resolves (against the page's SP2016
    URL) to a ledger row whose status is UPLOADED or VERIFIED becomes a path relative to
    the page's target folder. Anything else is left untouched and reported for a human
    disposition; nothing is guessed. External hosts, mailto/tel/javascript and bare
    #anchors are ignored.

Key Input Dependencies:
    - Converted HTML file.
    - Ledger CSV from library_migration_ledger.py (FileUrl, TargetLibrary, TargetFolder,
      TargetFilename, Status).
    - The page's own SP2016 FileUrl (its ledger row supplies the target folder).

Usage:
    python rewrite_page_links.py page.html --ledger ledger.csv --page-url <SP2016 page URL> \
        --source-host https://source-tenant.example.com --output page.rewritten.html --report links.json
    Exit codes: 0 no unresolved links, 1 unresolved links remain (see report), 2 usage error.

Index:
    rewrite_links, load_ledger, main (helpers: _key, _target_path, _relative, _rewrite_value)
"""
from __future__ import annotations

import argparse
import csv
import html as htmllib
import json
import posixpath
import re
import sys
from pathlib import Path
from urllib.parse import quote, unquote, urljoin, urlsplit

AVAILABLE = {"UPLOADED", "VERIFIED"}
IGNORED_SCHEMES = ("mailto:", "tel:", "javascript:", "data:")
# Page chrome already points at the target site (/sites/<site>/...), never at the source.
TARGET_SITE_PREFIXES = ("/sites/",)
ATTR_RE = re.compile(r"""(?P<attr>\b(?:href|src))(?P<eq>\s*=\s*)(?P<q>["'])(?P<val>.*?)(?P=q)""", re.I | re.S)


def _key(url: str) -> str:
    """Case-insensitive, decoded identity of a source file URL (no query or fragment)."""
    parts = urlsplit(url)
    return f"{parts.netloc}{unquote(parts.path)}".lower()


def _target_path(row: dict[str, str]) -> str:
    return posixpath.join(row["TargetLibrary"], row["TargetFolder"], row["TargetFilename"])


def _relative(page_row: dict[str, str], row: dict[str, str]) -> str:
    start = posixpath.join(page_row["TargetLibrary"], page_row["TargetFolder"])
    return quote(posixpath.relpath(_target_path(row), start), safe="/")


def load_ledger(path: Path) -> list[dict[str, str]]:
    """Read a ledger CSV into rows."""
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _rewrite_value(value: str, page_url: str, page_row: dict, index: dict, source_host: str) -> tuple[str, dict | None]:
    """Return the (possibly new) attribute value and a report entry, or None when ignored."""
    raw = htmllib.unescape(value).strip()
    if not raw or raw.startswith("#") or raw.lower().startswith(IGNORED_SCHEMES + TARGET_SITE_PREFIXES):
        return value, None
    absolute = urljoin(page_url, raw)
    if urlsplit(absolute).netloc.lower() != source_host.lower():
        return value, None
    row = index.get(_key(absolute))
    if row is None or row["Status"] not in AVAILABLE:
        reason = "not in ledger" if row is None else f"ledger status {row['Status']}"
        return value, {"original": raw, "new": None, "status": "unresolved", "reason": reason}
    parts = urlsplit(raw)
    suffix = (f"?{parts.query}" if parts.query else "") + (f"#{parts.fragment}" if parts.fragment else "")
    new = _relative(page_row, row) + suffix
    status = "unchanged" if new == raw else "rewritten"
    return htmllib.escape(new, quote=False) if status == "rewritten" else value, \
        {"original": raw, "new": new, "status": status, "reason": _target_path(row)}


def rewrite_links(html: str, page_url: str, ledger_rows: list[dict[str, str]],
                  source_host: str) -> tuple[str, list[dict]]:
    """Rewrite resolvable source links to relative target links; return (html, report)."""
    source_host = urlsplit(source_host).netloc or source_host
    index = {_key(r["FileUrl"]): r for r in ledger_rows}
    page_row = index.get(_key(page_url))
    if page_row is None:
        raise ValueError(f"Page URL not in ledger: {page_url}")
    report: list[dict] = []

    def sub(m: re.Match) -> str:
        new_val, entry = _rewrite_value(m["val"], page_url, page_row, index, source_host)
        if entry is not None:
            report.append(entry)
        return f'{m["attr"]}{m["eq"]}{m["q"]}{new_val}{m["q"]}'

    return ATTR_RE.sub(sub, html), report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("html", type=Path)
    ap.add_argument("--ledger", type=Path, required=True)
    ap.add_argument("--page-url", required=True)
    ap.add_argument("--source-host", required=True, help="e.g. https://source-tenant.example.com")
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--report", type=Path)
    a = ap.parse_args(argv)
    try:
        text = a.html.read_text(encoding="utf-8")
        out, report = rewrite_links(text, a.page_url, load_ledger(a.ledger), urlsplit(a.source_host).netloc)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    a.output.write_text(out, encoding="utf-8")
    if a.report:
        a.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    counts = {s: sum(e["status"] == s for e in report) for s in ("rewritten", "unchanged", "unresolved")}
    print(json.dumps(counts))
    return 1 if counts["unresolved"] else 0


if __name__ == "__main__":
    sys.exit(main())
