"""heading_parsing.py
===================

Purpose:
    Source-level observation functions: this plugin owns every function that produces a source-level *observation* (heading structure, statistics, defect signals) from already-extracted pandoc markdown text, regardless of whether it touches `pandoc` directly.

Key Input Dependencies:
    - re
    - pandoc.attrs
    - pandoc.heading_emphasis
    - pandoc.images
    - pandoc.toc

Source-level observation functions: this plugin owns every function that
produces a source-level *observation* (heading structure, statistics,
defect signals) from already-extracted pandoc markdown text, regardless of
whether it touches `pandoc` directly. Semantic interpretation of these
observations (topic boundaries, strategy recommendation) is
`document-structure-analysis`'s responsibility, not this module's.

Function Index:
    - parse_headings(markdown_text) -> list[dict]
    - iter_heading_matches(markdown_text) -> generator
    - detect_raw_toc(markdown_text) -> bool
    - detect_defect_signals(markdown_text) -> dict
    - compute_statistics(markdown_text) -> dict

Key Functions Index:
    - _normalize_heading_text()
    - iter_heading_matches()
    - parse_headings()
    - _counts_by_level()
    - _repeated_heading_texts()
    - _repeated_paths()
    - _image_stats()
    - detect_raw_toc()
    - detect_defect_signals()
    - compute_statistics()"""

import re

from pandoc.attrs import strip_pandoc_attrs
from pandoc.heading_emphasis import strip_whole_heading_emphasis
from pandoc.images import fix_glued_images
from pandoc.toc import _TOC_SLUG_LINE, _TOC_LINK_LINE, strip_raw_toc

_HEADING_RE_TEMPLATE = r"^(#{{1,6}})\s+(.+?)\s*$"
_HEADING_LINE = re.compile(_HEADING_RE_TEMPLATE.format(), re.MULTILINE)

# See scripts/package.py's _IMAGE_REF docstring for why alt text uses
# `(?:[^\]\\]|\\.)*` rather than a naive `[^\]]*` -- a markdown-escaped
# `]` in alt text otherwise terminates the character class early and the
# reference is silently missed.
_IMAGE_REF = re.compile(r"!\[(?:[^\]\\]|\\.)*\]\(([^)\s]+)")


def _normalize_heading_text(text: str) -> str:
    """Apply the same convert-time cleanup normalizations that would alter
    a single heading's text, to that heading's text alone.

    Structural anchor identity is computed from heading path text both at
    analysis time (this module, against RAW pandoc extraction) and at
    reconciliation time (structured-content-assembly's chunking, against the
    CLEANED document, after the cleanup pipeline has already run). If
    analysis computed identity from raw, un-normalized text while
    reconciliation recomputed it from normalized text, the two would never
    match. Normalizing here, in the single function `parse_headings` calls,
    guarantees both sides always compute identity from the same normalized
    text.
    """
    synthetic_line = f"# {text}\n"
    stripped = strip_whole_heading_emphasis(synthetic_line)
    stripped = fix_glued_images(stripped)
    first_line = stripped.split("\n", 1)[0]
    return first_line[2:].rstrip()


def iter_heading_matches(markdown_text: str):
    """Low-level ATX heading walk shared by `parse_headings` and any
    cleaned-document heading index a downstream plugin needs, so the
    path/occurrence computation exists in exactly one place.

    Yields `(match, level, text, path, occurrence)` in document order, where
    `path` is the full heading path (ancestor chain + this heading's text,
    reconstructed with a level-based stack so skipped levels -- e.g. an H1
    followed directly by an H3 -- are handled gracefully) and `occurrence`
    disambiguates two headings that share an identical full path.
    """
    stack = []  # list of (level, text)
    occurrence_counts = {}  # tuple(path) -> count seen so far

    for match in _HEADING_LINE.finditer(markdown_text):
        level = len(match.group(1))
        text = _normalize_heading_text(match.group(2).strip())
        if not text:
            continue

        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, text))

        path = [t for _, t in stack]
        path_key = tuple(path)
        occurrence_counts[path_key] = occurrence_counts.get(path_key, 0) + 1
        occurrence = occurrence_counts[path_key]

        yield match, level, text, path, occurrence


def parse_headings(markdown_text: str) -> list:
    """Parse ATX headings from pandoc markdown output into an ordered list
    of dicts: {"level": int, "text": str, "path": list[str], "occurrence": int}.

    Thin wrapper over `iter_heading_matches` that drops the regex match
    object (callers needing source position should use `iter_heading_matches`
    directly instead of re-parsing).
    """
    return [
        {"level": level, "text": text, "path": path, "occurrence": occurrence}
        for _match, level, text, path, occurrence in iter_heading_matches(markdown_text)
    ]


# Count parsed source headings by heading level for extraction diagnostics.
def _counts_by_level(headings: list) -> dict:
    """Count parsed source headings by heading level for extraction diagnostics."""
    counts = {}
    for h in headings:
        counts[h["level"]] = counts.get(h["level"], 0) + 1
    return counts


# Identify normalized heading titles that occur more than once in the source document.
def _repeated_heading_texts(headings: list) -> dict:
    """Identify normalized heading titles that occur more than once in the source document."""
    text_counts = {}
    for h in headings:
        text_counts[h["text"]] = text_counts.get(h["text"], 0) + 1
    return {text: count for text, count in text_counts.items() if count > 1}


# Identify structural heading paths repeated in the parsed document outline.
def _repeated_paths(headings: list) -> dict:
    """Identify structural heading paths repeated in the parsed document outline."""
    path_counts = {}
    for h in headings:
        key = tuple(h["path"])
        path_counts[key] = path_counts.get(key, 0) + 1
    return {path: count for path, count in path_counts.items() if count > 1}


# Summarize extracted image references and their file types for the normalized document report.
def _image_stats(media_dir) -> dict:
    """Summarize extracted image references and their file types for the normalized document report."""
    if not media_dir.exists():
        return {"count": 0, "formats": []}
    files = [p for p in media_dir.rglob("*") if p.is_file()]
    formats = sorted({p.suffix.lstrip(".").lower() for p in files if p.suffix})
    return {"count": len(files), "formats": formats}


def detect_raw_toc(markdown_text: str) -> bool:
    """Reuses pandoc.toc.strip_raw_toc's detection logic: if stripping
    raw-TOC field dumps changes the text, raw TOC evidence was present."""
    return strip_raw_toc(markdown_text) != markdown_text


def detect_defect_signals(markdown_text: str) -> dict:
    """Reuses pandoc.images.fix_glued_images,
    pandoc.attrs.strip_pandoc_attrs, and
    pandoc.heading_emphasis.strip_whole_heading_emphasis detection
    logic rather than re-implementing pattern matching from scratch."""
    return {
        "raw_toc_detected": detect_raw_toc(markdown_text),
        "glued_images": fix_glued_images(markdown_text) != markdown_text,
        "pandoc_attrs": strip_pandoc_attrs(markdown_text) != markdown_text,
        "bold_wrapped_headings": strip_whole_heading_emphasis(markdown_text) != markdown_text,
    }


# ---------------------------------------------------------------------------
# Extended analysis statistics -- measured directly from the already-
# extracted markdown text; "not measured" is reported (never a fabricated
# number) if a statistic cannot be computed with reasonable effort using
# pure string/regex analysis (no re-invoking pandoc).
# ---------------------------------------------------------------------------

_TABLE_SEPARATOR_ROW = re.compile(
    r'^\s*\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)+\|?\s*$', re.MULTILINE
)
# Note: the pattern above requires at least one `|` between two dash-runs,
# so a bare horizontal-rule-shaped line of dashes with no pipe characters
# at all (e.g. a divider pandoc emits for a Word horizontal rule) is never
# mistaken for a table separator row.
_GRID_TABLE_HEADER_SEPARATOR = re.compile(
    r'^\s*(?:\+[-:]*=[-=:]*)+\+\s*$', re.MULTILINE
)
# Each `+`-delimited segment must contain at least one `=`; the pattern anchors on the segment's first `=` (preceded only by `-`/`:`)
# so it has exactly one way to match any line and cannot backtrack exponentially.
# Pandoc emits grid tables (bounded by `+---+`/`+===+` lines) for complex/
# merged-cell Word tables. `_TABLE_SEPARATOR_ROW` only recognizes GFM-style
# `| --- | --- |` pipe-table separators, so a document containing only grid
# tables would otherwise be reported as having zero tables. A grid table's
# `+===+` header separator (distinct from the plain `+---+` row boundaries
# between data rows, which use only `-`) occurs exactly once per grid
# table, so counting it gives one count per grid table.
_FOOTNOTE_REFERENCE = re.compile(r'\[\^([\w-]+)\](?!:)')
_FOOTNOTE_DEFINITION_LINE = re.compile(r'^\[\^([\w-]+)\]:', re.MULTILINE)
# Both use `(?:[^\]\\]|\\.)*` rather than a naive `[^\]]*` -- see
# scripts/package.py's _IMAGE_REF docstring: a markdown-escaped `]` in
# link/alt text otherwise terminates the character class early and the
# reference is silently missed.
_LOCAL_LINK = re.compile(r'(?<!\!)\[(?:[^\]\\]|\\.)*\]\(#[^)]*\)')
_IMAGE_REFERENCE = re.compile(r'!\[(?:[^\]\\]|\\.)*\]\([^)]*\)')


def compute_statistics(markdown_text: str) -> dict:
    """Measure extended statistics directly from already-extracted
    markdown text: table count (by counting separator rows), footnote
    reference/definition counts, local document link count, total image
    reference count, and generated-TOC-entries-detected."""
    table_count = len(_TABLE_SEPARATOR_ROW.findall(markdown_text)) + len(
        _GRID_TABLE_HEADER_SEPARATOR.findall(markdown_text)
    )
    footnote_reference_count = len(
        [m for m in _FOOTNOTE_REFERENCE.finditer(markdown_text)]
    )
    footnote_definition_count = len(_FOOTNOTE_DEFINITION_LINE.findall(markdown_text))
    local_link_count = len(_LOCAL_LINK.findall(markdown_text))
    image_reference_count = len(_IMAGE_REFERENCE.findall(markdown_text))

    toc_bookmark_entries = len(_TOC_LINK_LINE.findall(markdown_text))
    toc_slug_entries = len(_TOC_SLUG_LINE.findall(markdown_text))
    generated_toc_entries_detected = toc_bookmark_entries + toc_slug_entries

    return {
        "table_count": table_count,
        "footnote_reference_count": footnote_reference_count,
        "footnote_definition_count": footnote_definition_count,
        "local_link_count": local_link_count,
        "image_reference_count": image_reference_count,
        "generated_toc_entries_detected": generated_toc_entries_detected,
    }
