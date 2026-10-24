#!/usr/bin/env python3
"""Lint and harvest HTML for the SharePoint Online modern Text web part.

Purpose:
    Reports markup the Text web part editor (CKEditor 5) is likely to strip on edit, and
    learns tenant-specific markup from hand-built capture pages.

Key Input Dependencies:
    assets/rte-vocabulary.json (allow-list; override with --vocab). Standard library only.
    Input HTML is the inner HTML of a text part (Get-PnPPageComponent .Text, or what is
    passed to Add-PnPPageTextPart -Text). A full page export works too: content outside
    <div data-sp-rte=""> is ignored when that marker is present.

Usage:
    python scripts/sp_text_webpart_html.py check FILE... [--vocab PATH]   (exit 1 on problems)
    python scripts/sp_text_webpart_html.py harvest FILE... [--vocab PATH] [--write]

Index:
    parse_style, Collector (class), flatten, load_vocab, find_default_vocab,
    tag_problems, style_problems, attribute_problems, element_problems,
    check_html, check_file, harvest, build_parser, main
"""
import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

BLOCK_TAGS = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "div", "blockquote", "pre", "ul", "ol",
              "li", "table", "figure", "section", "article"}
VOID_TAGS = {"br", "col", "img", "hr", "input", "meta", "link"}
RTE_ROOT = "__rte__"

Problem = Tuple[str, str, str]  # (kind, name, message)


def parse_style(value: Optional[str]) -> Dict[str, str]:
    """Parse an inline style string into a lower-cased property dict."""
    props: Dict[str, str] = {}
    for part in (value or "").replace("&#58;", ":").split(";"):
        if ":" in part:
            key, val = part.split(":", 1)
            props[key.strip().lower()] = val.strip()
    return props


class Collector(HTMLParser):
    """Walks HTML and records (tag, attrs, line, enclosing_table_count) for in-scope elements."""

    def __init__(self, text: str) -> None:
        """Parse `text` immediately; results are in `self.elements`."""
        super().__init__(convert_charrefs=True)
        self.scoped = "data-sp-rte" in text
        self.stack: List[str] = []
        self.elements: List[Tuple[str, Dict[str, str], int, int]] = []
        self.feed(text)

    def handle_starttag(self, tag: str, attrs: list) -> None:
        """Record the element and push it onto the open-element stack."""
        attr = {k.lower(): (v or "") for k, v in attrs}
        if self.scoped and RTE_ROOT not in self.stack:
            if tag == "div" and "data-sp-rte" in attr:
                self.stack.append(RTE_ROOT)
            return
        self.elements.append((tag, attr, self.getpos()[0], self.stack.count("table")))
        if tag not in VOID_TAGS:
            self.stack.append(tag)

    def handle_startendtag(self, tag: str, attrs: list) -> None:
        """Handle self-closing syntax as an open immediately followed by a close."""
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        """Pop to the nearest matching open tag; the root closes with its own div."""
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i] == tag or (self.stack[i] == RTE_ROOT and tag == "div" and i == len(self.stack) - 1):
                del self.stack[i:]
                return


def flatten(section: Dict[str, Iterable[str]]) -> set:
    """Union all value lists of a vocabulary section."""
    out: set = set()
    for values in section.values():
        out.update(values)
    return out


def load_vocab(path: Path) -> Tuple[dict, dict]:
    """Load the vocabulary JSON and return (vocab, merged allow-sets including tenant additions)."""
    vocab = json.loads(Path(path).read_text(encoding="utf-8"))
    tenant = vocab.setdefault("tenant", {"tags": [], "classes": [], "styles": [], "attributes": []})
    allow = {
        "tags": flatten(vocab["tags"]) | set(tenant["tags"]),
        "classes": flatten(vocab["classes"]) | set(tenant["classes"]),
        "tenant_styles": set(tenant["styles"]),
        "tenant_attrs": set(tenant["attributes"]),
    }
    return vocab, allow


def find_default_vocab() -> Path:
    """Locate assets/rte-vocabulary.json from the script's own or symlink-resolved location."""
    here = Path(__file__)
    for base in (here, here.resolve()):
        for parent in base.parents:
            candidate = parent / "assets" / "rte-vocabulary.json"
            if candidate.is_file():
                return candidate
    return here.parent.parent / "assets" / "rte-vocabulary.json"


def tag_problems(tag: str, classes: List[str], tables: int, vocab: dict, allow: dict) -> List[Problem]:
    """Check tag, wrapper-div and nesting rules plus classes for one element."""
    out: List[Problem] = []
    if tag == "img":
        return [("img", "img", "raw <img> is dropped on edit; use the CK5 imagePlugin markup (GetInlineImage) or an Image web part")]
    if tag not in allow["tags"]:
        out.append(("tag", tag, "tag not in allow-list"))
    wrappers = vocab["div_requires_class"]
    if tag == "div" and not set(classes) & set(wrappers):
        out.append(("div", "div", "<div> only allowed as table/image wrapper (%s)" % ", ".join(wrappers)))
    if tag == "table" and tables > 0:
        out.append(("nested", "table", "nested table is dropped"))
    for name in classes:
        if name not in allow["classes"]:
            out.append(("class", name, f"class '{name}' not in allow-list"))
    return out


def style_problems(tag: str, classes: List[str], style: Optional[str], vocab: dict, allow: dict) -> List[Problem]:
    """Report inline style properties the editor strips for this element."""
    styles = vocab["styles"]
    permitted = set(styles["block"] if tag in BLOCK_TAGS else styles["inline"])
    permitted |= set(styles["by_tag"].get(tag, []))
    for name in classes:
        permitted |= set(styles["by_class"].get(name, []))
    return [("style", prop, f"style '{prop}' is stripped by the editor")
            for prop in parse_style(style)
            if prop not in permitted and f"{tag}:{prop}" not in allow["tenant_styles"]]


def attribute_problems(tag: str, classes: List[str], attrs: Dict[str, str], vocab: dict, allow: dict) -> List[Problem]:
    """Report attributes outside the allow-list, plus colspan/rowspan."""
    cfg = vocab["attributes"]
    permitted = set(cfg["any"]) | set(cfg.get(tag, []))
    for name in classes:
        permitted |= set(cfg.get(name, []))
    out: List[Problem] = []
    for name in attrs:
        if name in ("colspan", "rowspan"):
            out.append(("span", name, f"{name} is not supported; expand into empty cells"))
        elif name not in permitted and f"{tag}:{name}" not in allow["tenant_attrs"]:
            out.append(("attr", name, f"attribute '{name}' not in allow-list"))
    return out


def element_problems(tag: str, attrs: Dict[str, str], tables: int, vocab: dict, allow: dict) -> List[Problem]:
    """Return all problems for one element. kind: tag|div|nested|class|style|attr|span|img."""
    classes = attrs.get("class", "").split()
    found = tag_problems(tag, classes, tables, vocab, allow)
    if tag == "img":
        return found
    return found + style_problems(tag, classes, attrs.get("style"), vocab, allow) \
        + attribute_problems(tag, classes, attrs, vocab, allow)


def check_html(text: str, vocab: dict, allow: dict) -> List[Tuple[int, str]]:
    """Lint an HTML string and return [(line, message)]; messages are prefixed with the tag."""
    problems = []
    for tag, attrs, line, tables in Collector(text).elements:
        for _, _, message in element_problems(tag, attrs, tables, vocab, allow):
            problems.append((line, f"<{tag}>: {message}"))
    return problems


def check_file(path: Path, vocab: dict, allow: dict) -> List[str]:
    """Lint one file and return report lines of the form path:line message."""
    text = Path(path).read_text(encoding="utf-8")
    return [f"{path}:{line} {message}" for line, message in check_html(text, vocab, allow)]


def harvest(paths: Iterable[Path], vocab_path: Path, write: bool) -> dict:
    """Add markup seen in tenant captures to vocab['tenant'] (per-tag keys such as 'span:font-size').

    Structural rules (div wrapper, nested table, colspan, raw img) are reported as notes,
    never harvested. Returns {'added_to_tenant': {...}, 'structural_notes': [...]}.
    """
    vocab, allow = load_vocab(vocab_path)
    tenant = vocab["tenant"]
    found: Dict[str, set] = {"tags": set(), "classes": set(), "styles": set(), "attributes": set()}
    keyed = {"tag": ("tags", False), "class": ("classes", False), "style": ("styles", True), "attr": ("attributes", True)}
    notes: set = set()
    for path in paths:
        for tag, attrs, _, tables in Collector(Path(path).read_text(encoding="utf-8")).elements:
            for kind, name, message in element_problems(tag, attrs, tables, vocab, allow):
                if kind in keyed:
                    bucket, per_tag = keyed[kind]
                    found[bucket].add(f"{tag}:{name}" if per_tag else name)
                else:
                    notes.add(f"<{tag}>: {message} (seen in capture - review manually)")
    added = {}
    for bucket, values in found.items():
        new = sorted(values - set(tenant[bucket]))
        if new:
            added[bucket] = new
            tenant[bucket] = sorted(set(tenant[bucket]) | values)
    if write:
        Path(vocab_path).write_text(json.dumps(vocab, indent=2) + "\n", encoding="utf-8")
    return {"added_to_tenant": added, "structural_notes": sorted(notes)}


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["check", "harvest"])
    parser.add_argument("files", nargs="+")
    parser.add_argument("--vocab", default=None, help="vocabulary JSON (default: assets/rte-vocabulary.json)")
    parser.add_argument("--write", action="store_true", help="harvest only: save changes to the vocabulary")
    return parser


def main() -> int:
    """Run the CLI. Exit 0 clean, 1 problems found, 2 input error."""
    args = build_parser().parse_args()
    vocab_path = Path(args.vocab) if args.vocab else find_default_vocab()
    missing = [f for f in [*args.files, str(vocab_path)] if not Path(f).is_file()]
    if missing:
        print(f"error: file not found: {', '.join(missing)}", file=sys.stderr)
        return 2
    if args.command == "harvest":
        print(json.dumps(harvest([Path(f) for f in args.files], vocab_path, args.write), indent=2))
        print(f"wrote {vocab_path}" if args.write else "(dry run; pass --write to save)")
        return 0
    vocab, allow = load_vocab(vocab_path)
    report = [line for f in args.files for line in check_file(Path(f), vocab, allow)]
    print("\n".join(report))
    print(f"{len(report)} problem(s)")
    return 1 if report else 0


if __name__ == "__main__":
    sys.exit(main())
