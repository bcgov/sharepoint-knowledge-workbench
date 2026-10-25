#!/usr/bin/env python3
"""Deterministic BC Design System alignment check for a converted static HTML page.

Purpose:
    Partial, repeatable validation of a converted page before publication. It checks
    the page chrome required by references/bc-design-system-page-chrome.md and, when
    a source ASPX is supplied, content-structure parity. It cannot adjudicator visual
    quality or contrast; a human still reviews the rendered page.

Key Input Dependencies:
    - Converted HTML file (required).
    - Original source ASPX/HTML (optional, enables structure-parity checks).
    - colors_and_type.css (optional, enables the hard-coded colour check).

Usage:
    python validate_design_system_page.py page.html --source page.aspx \
        --tokens-css .agents/skills/design-system-design-system/assets/colors_and_type.css
    Exit codes: 0 all checks pass, 1 one or more failures, 2 usage or read error.
    Prints a JSON report (checks, status, detail) to stdout.

Index:
    read_text, collect, extract_hex, check_chrome, check_accessibility,
    check_assets, check_colors, check_parity, validate, main
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

CSS_FILE = "colors_and_type.css"
CSS_FILE_ALIASES = ("colors_and_type.css", "bc-gov-design-system", "design-system-design-system")
ACK_TEXT = "acknowledges the territories of First Nations"
ACTIVE_TAGS = {"script", "iframe", "object", "embed", "form"}
PARITY_KEYS = ("table", "tr", "cell", "li", "a_href")
# Present when the design-system tokens are inlined in a <style> block instead of linked.
INLINE_TOKEN_MARKER = "--color-brand-primary"
HEX_RE = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b")


def read_text(path: Path) -> str:
    """Read a file as UTF-8, falling back to cp1252 for legacy sources."""
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("cp1252")


class Page(HTMLParser):
    """Collects the facts the checks need in a single pass."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict]] = []
        self.doctype = False
        self.title = ""
        self.style = ""
        self.inline_styles: list[str] = []
        self.headings: list[int] = []
        self.counts = {k: 0 for k in PARITY_KEYS}
        self.th_without_scope = 0
        self.imgs_without_alt = 0
        self.text = ""
        self._stack: list[str] = []
        self._breadcrumb_depth = 0

    def handle_decl(self, decl: str) -> None:
        self.doctype = self.doctype or decl.lower().startswith("doctype html")

    def handle_starttag(self, tag: str, attrs: list) -> None:
        a = {k: (v or "") for k, v in attrs}
        self.tags.append((tag, a))
        if tag not in {"br", "img", "meta", "link", "hr", "input"}:
            self._stack.append(tag)
        if (tag == "nav" and a.get("aria-label") == "Breadcrumb") or tag == "footer":
            self._breadcrumb_depth = self._breadcrumb_depth or len(self._stack)
        if "style" in a:
            self.inline_styles.append(a["style"])
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        if tag == "img" and not a.get("alt", "").strip():
            self.imgs_without_alt += 1
        if tag == "th" and "scope" not in a:
            self.th_without_scope += 1
        self._count(tag, a)

    def _count(self, tag: str, a: dict) -> None:
        if self._breadcrumb_depth:
            return
        key = {"td": "cell", "th": "cell"}.get(tag, tag)
        if key in ("table", "tr", "cell", "li"):
            self.counts[key] += 1
        elif tag == "a" and a.get("href"):
            self.counts["a_href"] += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self._stack:
            while self._stack and self._stack.pop() != tag:
                pass
        if self._breadcrumb_depth and len(self._stack) < self._breadcrumb_depth:
            self._breadcrumb_depth = 0

    def handle_data(self, data: str) -> None:
        if self._stack and self._stack[-1] == "title":
            self.title += data
        elif self._stack and self._stack[-1] == "style":
            self.style += data
        self.text += data

    def has(self, tag: str, **attrs: str) -> bool:
        return any(t == tag and all(a.get(k) == v for k, v in attrs.items()) for t, a in self.tags)

    def has_class(self, tag: str, cls: str) -> bool:
        return any(t == tag and cls in a.get("class", "").split() for t, a in self.tags)


def collect(html: str) -> Page:
    page = Page()
    page.feed(html)
    return page


def extract_hex(css: str) -> set[str]:
    return {h.lower() for h in HEX_RE.findall(css)}


def result(name: str, ok: bool, detail: str = "") -> dict:
    return {"check": name, "status": "PASS" if ok else "FAIL", "detail": detail}


def check_chrome(p: Page) -> list[dict]:
    css_link = any(t == "link" and any(cf in a.get("href", "") for cf in CSS_FILE_ALIASES) for t, a in p.tags)
    css_link = css_link or INLINE_TOKEN_MARKER in p.style
    logo = any(t == "img" and "bc-logo" in a.get("src", "") for t, a in p.tags)
    return [
        result("doctype", p.doctype),
        result("html-lang", any(t == "html" and a.get("lang") for t, a in p.tags)),
        result("charset-utf8", any(t == "meta" and a.get("charset", "").lower() == "utf-8" for t, a in p.tags)),
        result("viewport", p.has("meta", name="viewport")),
        result("title", bool(p.title.strip())),
        result("design-system-css-link", css_link, f"{CSS_FILE} linked, or tokens inlined"),
        result("site-header", p.has_class("header", "site-header")),
        result("header-logo", logo),
        result("subheader", p.has_class("div", "subheader")),
        result("breadcrumb", p.has("nav", **{"aria-label": "Breadcrumb"})),
        result("main-landmark", p.has("main")),
        result("single-h1", p.headings.count(1) == 1, f"h1 count={p.headings.count(1)}"),
        result("indigenous-acknowledgment", ACK_TEXT in " ".join(p.text.split())),
        result("footer", p.has("footer")),
    ]


def check_accessibility(p: Page) -> list[dict]:
    skipped = any(b - a > 1 for a, b in zip(p.headings, p.headings[1:]))
    return [
        result("focus-visible-rule", ":focus-visible" in p.style),
        result("images-have-alt", p.imgs_without_alt == 0, f"missing={p.imgs_without_alt}"),
        result("th-have-scope", p.th_without_scope == 0, f"missing={p.th_without_scope}"),
        result("no-skipped-heading-levels", not skipped, f"levels={p.headings}"),
    ]


def check_assets(p: Page) -> list[dict]:
    active = sorted({t for t, _ in p.tags if t in ACTIVE_TAGS})
    external = [
        a.get("src") or a.get("href") for t, a in p.tags
        if t in {"img", "link", "source"} and re.match(r"https?:", a.get("src") or a.get("href") or "")
    ]
    imports = re.findall(r"@import[^;]*;", p.style)
    return [
        result("no-active-markup", not active, ",".join(active)),
        result("no-external-assets", not external and not imports, "; ".join(external + imports)),
    ]


def check_colors(p: Page, tokens_css: str | None) -> list[dict]:
    if tokens_css is None:
        return [result("no-unknown-hex-colors", True, "skipped: no --tokens-css")]
    allowed = extract_hex(tokens_css)
    used = extract_hex(p.style + " ".join(p.inline_styles))
    unknown = sorted(used - allowed)
    return [result("no-unknown-hex-colors", not unknown, ",".join(unknown))]


def check_parity(p: Page, source: Page) -> list[dict]:
    return [
        result(f"parity-{k}", p.counts[k] == source.counts[k], f"page={p.counts[k]} source={source.counts[k]}")
        for k in PARITY_KEYS
    ]


def validate(html: str, source_html: str | None = None, tokens_css: str | None = None) -> dict:
    page = collect(html)
    checks = check_chrome(page) + check_accessibility(page) + check_assets(page) + check_colors(page, tokens_css)
    if source_html is not None:
        checks += check_parity(page, collect(source_html))
    failed = [c["check"] for c in checks if c["status"] == "FAIL"]
    return {"status": "FAIL" if failed else "PASS", "failed": failed, "checks": checks}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate a converted page against the BC Design System chrome.")
    ap.add_argument("html", type=Path, help="Converted HTML file")
    ap.add_argument("--source", type=Path, help="Original ASPX/HTML for structure parity")
    ap.add_argument("--tokens-css", type=Path, help="colors_and_type.css for the hex-colour check")
    args = ap.parse_args(argv)
    try:
        report = validate(
            read_text(args.html),
            read_text(args.source) if args.source else None,
            read_text(args.tokens_css) if args.tokens_css else None,
        )
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
