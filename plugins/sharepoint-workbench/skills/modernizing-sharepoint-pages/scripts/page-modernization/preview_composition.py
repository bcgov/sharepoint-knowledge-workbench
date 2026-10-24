"""
preview_composition.py
=======================

Purpose: compose a self-contained offline preview HTML file by merging a
site's structural chrome (navigation, header, logo, ancestors) with an
already-extracted page's content (modern-preview.html + metadata.json).
Shows a converted page as it would look with full site chrome in place, for
reviewer sign-off before any upload. Disk-only -- reads the two caller-named
input folders and writes the one caller-named output file; no tenant I/O.

Layer: CLI entry point, invoked as a real subprocess by the pipeline (and by
this plugin's own tests).

Key Input Dependencies:
    - Page folder containing metadata.json and modern-preview.html.
    - Chrome folder containing site-chrome.json and optional local assets.
    - outcomes.py shared page-modernization result vocabulary.

Function Index:
    _extract_page_content, _render_top_nav, _render_breadcrumb,
    _resolve_logo, _preview_chrome_gaps, _preview_page_title,
    _preview_outcome, compose_preview, main
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

import outcomes

_MAX_VISIBLE_TOP_NAV = 5


def _extract_page_content(page_html: str) -> str:
    """Select the page-content region, body, or complete HTML as a fallback."""
    match = re.search(
        r'(?si)<(?:main|div) class="page-content">(?P<content>.*?)</(?:main|div)>', page_html
    )
    if match:
        return match.group("content")
    body_match = re.search(r"(?si)<body[^>]*>(?P<body>.*?)</body>", page_html)
    if body_match:
        return body_match.group("body")
    return page_html


def _render_top_nav(top_nav: "list[dict]") -> str:
    """Render navigation entries and group overflow under the More menu."""
    visible = list(top_nav[:_MAX_VISIBLE_TOP_NAV])
    overflow = top_nav[_MAX_VISIBLE_TOP_NAV:]
    if overflow:
        visible.append({"Title": "More", "Url": "#", "Children": overflow})

    parts = []
    for item in visible:
        url = item.get("Url") or "#"
        title = item.get("Title") or ""
        children = item.get("Children") or []
        if children:
            child_html = "".join(
                f"<li><a href='{c.get('Url') or '#'}'>{c.get('Title') or ''}</a></li>"
                for c in children
            )
            parts.append(
                f"<li class='has-children'><a href='{url}'>{title} &#9660;</a><ul>{child_html}</ul></li>"
            )
        else:
            parts.append(f"<li><a href='{url}'>{title}</a></li>")
    return "".join(parts)


def _render_breadcrumb(ancestors: "list[dict]") -> str:
    """Render ancestor links for the page breadcrumb."""
    return " <span class='bc-sep'>›</span> ".join(
        f"<span class='bc-item'><a href='{a.get('Url') or '#'}'>{a.get('Title') or ''}</a></span>"
        for a in ancestors
    )


def _resolve_logo(web: dict, chrome_folder: Path, page_folder: Path) -> str:
    """Return the logo src to embed in the preview, copying a local logo file
    into the page folder's assets/ subfolder for portability. Returns '' if
    no logo is available -- never fabricates a substitute."""
    local_file = web.get("SiteLogoLocalFile")
    if local_file:
        src_path = chrome_folder / local_file
        if src_path.is_file():
            assets_dir = page_folder / "assets"
            assets_dir.mkdir(exist_ok=True)
            dest_path = assets_dir / local_file
            if not dest_path.exists():
                shutil.copy(src_path, dest_path)
            return f"assets/{local_file}"
    return web.get("SiteLogoUrl") or ""


def _preview_chrome_gaps(
    logo_src: str, ancestors: list[dict], top_nav: list[dict]
) -> list[str]:
    """List required site-chrome components absent from the supplied export."""
    missing = []
    if not logo_src:
        missing.append("logo")
    if not ancestors:
        missing.append("ancestors")
    if not top_nav:
        missing.append("navigation")
    return missing


def _preview_page_title(meta: dict) -> str:
    """Choose the exported title or derive a neutral title from the page name."""
    title = meta.get("Title")
    if title:
        return title
    page_name = meta.get("PageName")
    return re.sub(r"\.aspx$", "", page_name) if page_name else "Page Preview"


def _preview_outcome(missing_chrome_parts: list[str]) -> dict:
    """Build the observed/partial result for the available preview chrome."""
    if missing_chrome_parts:
        return outcomes.make_outcome(
            "Partial", f"Missing chrome element(s): {', '.join(missing_chrome_parts)}"
        )
    return outcomes.make_outcome("Observed", "Preview composed with full chrome")


_PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{page_title} — {web_title}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: "Segoe UI", Arial, sans-serif; font-size: 14px; background: #f4f4f4; padding: 20px; color: #323130; }}
    .chrome-shell {{ max-width: 1200px; width: 100%; margin: 0 auto; border: 1px solid #ddd; background: #fff; box-shadow: 0 4px 15px rgba(0,0,0,0.05); overflow: hidden; }}
    .site-header {{ display: flex; align-items: center; justify-content: space-between; padding: 16px 24px; border-bottom: 1px solid #e0e0e0; background: #fff; }}
    .site-logo {{ display: flex; align-items: center; gap: 16px; }}
    .site-logo img {{ height: 50px; }}
    .site-title {{ font-size: 24px; font-weight: 300; color: #333; }}
    .top-nav {{ background: #fff; border-bottom: 3px solid #003366; padding: 0 16px; position: relative; }}
    .top-nav ul {{ list-style: none; display: flex; flex-wrap: wrap; gap: 4px; }}
    .top-nav li {{ position: relative; }}
    .top-nav li a {{ display: block; padding: 10px 16px; color: #003366; font-size: 14px; font-weight: 600; text-decoration: none; white-space: nowrap; }}
    .top-nav li ul {{ display: none; position: absolute; top: 100%; left: 0; background: #113254; border: 1px solid #0d2743; min-width: 260px; z-index: 100; }}
    .top-nav li:hover ul {{ display: block; }}
    .top-nav li ul li a {{ color: #fff; font-weight: normal; }}
    .breadcrumb {{ background: #fff; border-bottom: 1px solid #e0e0e0; padding: 12px 24px; font-size: 13px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
    .bc-item a, .bc-current {{ background: #f3f3f3; border: 1px solid #dcdcdc; border-radius: 16px; padding: 4px 14px; color: #444; text-decoration: none; display: inline-block; font-size: 12px; }}
    .bc-current {{ background: #e6e6e6; font-weight: 600; }}
    .page-content {{ padding: 32px 40px 48px 40px; overflow: hidden; word-wrap: break-word; overflow-wrap: break-word; }}
    .page-content img {{ max-width: 100%; height: auto; }}
    .chrome-meta {{ background: #fffbe6; border-top: 1px solid #ffe58f; padding: 12px 24px; font-size: 11px; color: #666; display: flex; justify-content: space-between; }}
  </style>
</head>
<body>
<div class="chrome-shell">
  <div class="site-header">
    <div class="site-logo">
      {logo_img}
      <div class="site-title">{web_title}</div>
    </div>
  </div>
  <nav class="top-nav">
    <ul>{top_nav_html}</ul>
  </nav>
  <div class="breadcrumb">
    {breadcrumb_html}{breadcrumb_sep}
    <span class="bc-current">{page_title}</span>
  </div>
  <main class="page-content">
    {page_content}
  </main>
  <div class="chrome-meta">
    <span>Original Page: {original_url}</span>
    <span>Extracted: {extracted_at}</span>
  </div>
</div>
</body>
</html>
"""


def compose_preview(page_folder: Path, chrome_folder: Path) -> "tuple[str | None, dict]":
    """Compose the offline preview HTML. Returns (html_or_None, outcome)."""
    meta_file = page_folder / "metadata.json"
    preview_file = page_folder / "modern-preview.html"
    chrome_file = chrome_folder / "site-chrome.json"

    missing = [str(p) for p in (meta_file, preview_file, chrome_file) if not p.is_file()]
    if missing:
        return None, outcomes.make_outcome(
            "Unavailable", f"Missing required input file(s): {', '.join(missing)}"
        )

    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    page_html = preview_file.read_text(encoding="utf-8")
    chrome = json.loads(chrome_file.read_text(encoding="utf-8"))

    page_content = _extract_page_content(page_html)
    if not page_content.strip():
        return None, outcomes.make_outcome("Empty", "Page content is empty")

    web = chrome.get("Web") or {}
    top_nav = chrome.get("TopNav") or []
    ancestors = chrome.get("Ancestors") or []

    logo_src = _resolve_logo(web, chrome_folder, page_folder)
    missing_chrome_parts = _preview_chrome_gaps(logo_src, ancestors, top_nav)
    page_title = _preview_page_title(meta)

    web_title = web.get("Title") or "SharePoint Site"
    breadcrumb_html = _render_breadcrumb(ancestors)

    html = _PAGE_TEMPLATE.format(
        page_title=page_title,
        web_title=web_title,
        logo_img=f"<img src='{logo_src}' alt='Site Logo'>" if logo_src else "",
        top_nav_html=_render_top_nav(top_nav),
        breadcrumb_html=breadcrumb_html,
        breadcrumb_sep="<span class='bc-sep'>›</span>" if breadcrumb_html else "",
        page_content=page_content,
        original_url=meta.get("PageServerRelativeUrl") or "",
        extracted_at=meta.get("ExtractedAt") or "",
    )

    return html, _preview_outcome(missing_chrome_parts)


def main(argv: "list[str] | None" = None) -> int:
    """Compose a preview from local page and chrome folders and write it."""
    parser = argparse.ArgumentParser(
        description="Compose an offline preview by merging site chrome with extracted page content."
    )
    parser.add_argument("--page-folder", required=True)
    parser.add_argument("--chrome-folder", required=True)
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    page_folder = Path(args.page_folder)
    chrome_folder = Path(args.chrome_folder)

    if not page_folder.is_dir():
        print(f"Unavailable: page folder not found: {page_folder}", file=sys.stderr)
        return 1
    if not chrome_folder.is_dir():
        print(f"Unavailable: chrome folder not found: {chrome_folder}", file=sys.stderr)
        return 1

    try:
        html, outcome = compose_preview(page_folder, chrome_folder)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Failed: could not parse an input file: {exc}", file=sys.stderr)
        return 1

    if html is None:
        print(f"{outcome['status']}: {outcome['detail']}", file=sys.stderr)
        return 1

    output_path = Path(args.output) if args.output else page_folder / "full-preview.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"{outcome['status']}: {outcome['detail']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
