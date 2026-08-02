"""
chunking.py
===========

Reconciles a CONFIRMED `ConversionPlan`'s `chunk_anchors` (computed during
analysis, against RAW pandoc markdown -- Task 6/`analyze_structure.py`)
against a CLEANED document's actual heading structure (after Task 2's
pandoc cleanup pipeline has run), then slices the cleaned markdown into
per-chunk content strings using the reconciled positions.

Why this exists (spec Non-Negotiable Rule 5, Section 7.2): "Chunk boundaries
are structural anchors recorded from analyzed headings, not raw line numbers
reused after cleanup." Cleanup can shift line numbers (stripping raw TOC
dumps, glued-image lines, footnote artifacts, etc.), but `StructuralAnchor`
identity is heading-path + occurrence based (via `identity.make_chunk_id`),
not line-based -- so anchors recorded against the raw document must still
resolve against the cleaned one.

This module does NOT invoke pandoc or the cleanup pipeline itself -- it
accepts already-cleaned markdown text as a plain string (produced however
the caller obtained it) plus a confirmed plan's `chunk_anchors`. Wiring the
full pandoc -> cleanup -> reconcile -> chunk pipeline end-to-end into
`convert-document` is Task 9's job.

Function Index:
    - parse_headings_with_lines(markdown_text) -> list[dict]
        Like analyze_structure.parse_headings, but also carries each
        heading's 0-based line number and precomputed stable_key.
    - reconcile_anchors(chunk_anchors, cleaned_markdown_text) -> list[ReconciledAnchor]
    - slice_chunks(cleaned_markdown_text, reconciled_anchors) -> SlicedDocument
    - reconcile_and_slice(chunk_anchors, cleaned_markdown_text) -> SlicedDocument

`strategy: "single"` vs `"chunked"` is NOT branched on anywhere in this
module: `analyze_structure.analyze_document` populates `chunk_anchors` from
ALL parsed headings regardless of the strategy recommendation (a
single-strategy plan can still carry more than one anchor; a chunked plan's
anchor list is built the exact same way), so this module treats
`chunk_anchors` uniformly -- "single" is simply whatever anchors happen to
be recorded, including exactly one.
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import identity_core as identity  # noqa: E402
from pandoc_cleanup.heading_emphasis import strip_whole_heading_emphasis  # noqa: E402
from pandoc_cleanup.images import fix_glued_images  # noqa: E402

# Plugin-local heading walk (a copy of source-document-extraction's
# heading_parsing.iter_heading_matches -- cross-plugin dependency
# prohibited, and this module needs to walk the CLEANED document's
# headings, not the raw one, so it isn't just reusing the same call
# anyway). Must normalize heading text identically to how
# `knowledge-analysis` computed the original stable_key, or reconciliation
# never matches. See
# docs/superpowers/plans/phase-4-5-evidence/wave-4-canonical-knowledge-split-decision.md.
_HEADING_LINE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


def _normalize_heading_text(text: str) -> str:
    synthetic_line = f"# {text}\n"
    stripped = strip_whole_heading_emphasis(synthetic_line)
    stripped = fix_glued_images(stripped)
    first_line = stripped.split("\n", 1)[0]
    return first_line[2:].rstrip()


def iter_heading_matches(markdown_text: str):
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


class AnchorReconciliationError(Exception):
    """Base class for reconciliation failures. Reconciliation fails loudly
    (raises) rather than silently truncating or guessing -- per spec
    Non-Negotiable Rule 5's "not raw line numbers reused after cleanup"
    requirement, a chunk boundary that can't be trusted must not be used."""


class MissingAnchorError(AnchorReconciliationError):
    """A confirmed anchor's stable_key has no matching heading anywhere in
    the cleaned document. The chunk is NOT silently dropped or truncated --
    conversion must fail so a human can investigate what cleanup did."""


class AmbiguousAnchorError(AnchorReconciliationError):
    """Two or more headings in the cleaned document recompute to the same
    stable_key as a single confirmed anchor. Reconciliation refuses to
    guess which one is the "real" match -- this is reported as a failure,
    not resolved by picking the first candidate."""


class AnchorOrderingError(AnchorReconciliationError):
    """Reconciled anchor line numbers came back out of the original
    chunk_anchors order (e.g. cleanup somehow reordered headings). Chunk
    slicing assumes anchors are monotonically increasing in the cleaned
    document; if that invariant breaks, slicing math would silently
    produce corrupt/overlapping chunks, so this fails loudly instead."""


@dataclass
class ReconciledAnchor:
    anchor: "object"  # contracts.StructuralAnchor
    line: int  # 0-based line number of this heading in the cleaned document


@dataclass
class ChunkSlice:
    anchor: "object"  # contracts.StructuralAnchor
    start_line: int  # inclusive, 0-based
    end_line: int  # exclusive, 0-based
    content: str


@dataclass
class SlicedDocument:
    preamble: str  # content before the first reconciled anchor's heading line
    chunks: list  # list[ChunkSlice]


# ---------------------------------------------------------------------------
# Cleaned-document heading index
# ---------------------------------------------------------------------------

def parse_headings_with_lines(markdown_text: str) -> list:
    """Parse ATX headings from the CLEANED document, reusing
    `analyze_structure.iter_heading_matches` (same path/occurrence walk used
    to build the original draft plan's chunk_anchors) rather than
    re-implementing the heading regex/parsing logic a second time.

    Returns an ordered list of dicts: {"level", "text", "path", "occurrence",
    "line", "stable_key"}, where "line" is the heading's 0-based line number
    in `markdown_text` and "stable_key" is
    `identity.make_chunk_id(path, occurrence)` -- the same function used to
    compute the confirmed plan's anchor stable_keys during analysis, so
    equality comparison between an anchor's stored stable_key and a cleaned
    heading's recomputed stable_key is a direct, valid identity check.
    """
    headings = []
    for match, level, text, path, occurrence in iter_heading_matches(
        markdown_text
    ):
        line_no = markdown_text.count("\n", 0, match.start())
        headings.append({
            "level": level,
            "text": text,
            "path": list(path),
            "occurrence": occurrence,
            "line": line_no,
            "stable_key": identity.make_chunk_id(path, occurrence),
        })
    return headings


# ---------------------------------------------------------------------------
# Reconciliation
# ---------------------------------------------------------------------------

def reconcile_anchors(chunk_anchors: list, cleaned_markdown_text: str) -> list:
    """For each StructuralAnchor in `chunk_anchors` (in recorded order),
    find the line in `cleaned_markdown_text` where that same logical
    heading now lives.

    Algorithm:
      1. Walk the cleaned document's headings via `parse_headings_with_lines`
         and recompute each one's own stable_key the exact same way the
         original draft-plan anchors were computed
         (`identity.make_chunk_id(path, occurrence)`).
      2. Group cleaned headings by stable_key.
      3. For each confirmed anchor, look up its stored stable_key in that
         grouping:
           - zero matches -> MissingAnchorError (fail, do not truncate).
           - 2+ matches -> AmbiguousAnchorError (fail, do not guess).
           - exactly 1 match -> reconciled to that heading's line number.
      4. Heading LEVEL is deliberately not part of the match: identity.
         make_chunk_id takes only (heading_path, occurrence), never a level
         argument, so a heading whose markdown level shifted (e.g. "##" ->
         "###") still resolves by path+occurrence. Level is informational
         on StructuralAnchor, not part of its identity -- this matches the
         spirit of Rule 5 (anchors are structural, not formatting-based),
         and Task 2's cleanup modules are documented as fixing formatting
         artifacts only, never intentionally altering heading levels, so
         tolerating a level change here does not mask real damage; it just
         means level-shift detection is not this module's job.
      5. Matched lines must come back in non-decreasing order matching the
         original chunk_anchors order (cleanup does not reorder headings);
         if that invariant is violated, raise AnchorOrderingError rather
         than silently producing corrupt chunk slices.
    """
    cleaned_headings = parse_headings_with_lines(cleaned_markdown_text)
    by_key = {}
    for h in cleaned_headings:
        by_key.setdefault(h["stable_key"], []).append(h)

    reconciled = []
    previous_line = -1
    for anchor in chunk_anchors:
        matches = by_key.get(anchor.stable_key, [])
        if not matches:
            raise MissingAnchorError(
                f"anchor {anchor.stable_key!r} (heading path "
                f"{anchor.source_heading_path!r}, occurrence {anchor.occurrence}) "
                "has no matching heading in the cleaned document; refusing "
                "to silently truncate the chunk -- investigate what the "
                "cleanup pipeline did to this heading"
            )
        if len(matches) > 1:
            raise AmbiguousAnchorError(
                f"anchor {anchor.stable_key!r} (heading path "
                f"{anchor.source_heading_path!r}, occurrence {anchor.occurrence}) "
                f"matches {len(matches)} headings in the cleaned document "
                f"(lines {[m['line'] for m in matches]}); ambiguous "
                "reconciliation, refusing to guess which one is correct"
            )
        line = matches[0]["line"]
        if line <= previous_line:
            raise AnchorOrderingError(
                f"anchor {anchor.stable_key!r} reconciled to line {line}, "
                f"which is not after the previous anchor's line "
                f"{previous_line}; cleaned document heading order does not "
                "match the confirmed plan's chunk_anchors order"
            )
        reconciled.append(ReconciledAnchor(anchor=anchor, line=line))
        previous_line = line

    return reconciled


# ---------------------------------------------------------------------------
# Chunk slicing
# ---------------------------------------------------------------------------

def slice_chunks(cleaned_markdown_text: str, reconciled_anchors: list) -> "SlicedDocument":
    """Slice `cleaned_markdown_text` into per-chunk content strings using
    reconciled (freshly-recomputed) line positions -- never any line number
    that might have been stored on the original plan (StructuralAnchor never
    carries one; per Task 6's design anchors are purely structural).

    Each chunk runs from its own reconciled heading line to the line before
    the next reconciled anchor's heading line, or end-of-document for the
    last chunk. Content before the first reconciled anchor's heading line
    (front matter / preamble) is returned separately as `SlicedDocument.
    preamble` rather than being attached to the first chunk -- this is the
    explicit, documented front-matter handling choice: a preamble is not
    covered by any StructuralAnchor, so it must not be silently folded into
    a chunk whose identity belongs to a specific heading. Callers that want
    to treat preamble as "part of chunk one" can concatenate it themselves;
    this module keeps the two conceptually distinct.
    """
    lines = cleaned_markdown_text.splitlines(keepends=True)

    if not reconciled_anchors:
        return SlicedDocument(preamble=cleaned_markdown_text, chunks=[])

    first_line = reconciled_anchors[0].line
    preamble = "".join(lines[:first_line])

    chunks = []
    for idx, reconciled in enumerate(reconciled_anchors):
        start = reconciled.line
        end = (
            reconciled_anchors[idx + 1].line
            if idx + 1 < len(reconciled_anchors)
            else len(lines)
        )
        content = "".join(lines[start:end])
        chunks.append(
            ChunkSlice(
                anchor=reconciled.anchor,
                start_line=start,
                end_line=end,
                content=content,
            )
        )

    return SlicedDocument(preamble=preamble, chunks=chunks)


# ---------------------------------------------------------------------------
# Convenience entry point
# ---------------------------------------------------------------------------

def reconcile_and_slice(chunk_anchors: list, cleaned_markdown_text: str) -> "SlicedDocument":
    """Reconcile `chunk_anchors` against `cleaned_markdown_text` and slice
    the cleaned document into chunk content strings in one call. Uniform
    across `strategy: "single"` and `strategy: "chunked"` plans -- there is
    no branch on strategy anywhere in this module; a single-strategy plan's
    (possibly single-entry) `chunk_anchors` list is processed identically to
    a chunked plan's."""
    reconciled = reconcile_anchors(chunk_anchors, cleaned_markdown_text)
    return slice_chunks(cleaned_markdown_text, reconciled)
