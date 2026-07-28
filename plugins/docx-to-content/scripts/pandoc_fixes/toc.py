#!/usr/bin/env python
"""
toc.py
======

Strips a raw Word-generated table-of-contents field dump from pandoc
markdown output. Word's TOC field converts, under pandoc, into a literal
run of bracket links pointing at internal `#_Toc<digits>` bookmarks (e.g.
`[Section Name](#_Toc123456)`), often preceded by an empty bookmark-anchor
span (`[]{#_Toc... }`). This is not usable navigation in plain markdown, so
the block is detected and removed wherever it occurs in the document — not
only at the very start (a title/cover-page heading commonly precedes the
Word-generated TOC).

A SECOND, unrelated Word TOC representation also occurs: instead of
`_Toc`-bookmark anchors, pandoc sometimes converts the TOC field into
nested markdown links that target ordinary slugified-heading anchors --
an OUTER bracket-link wrapping an INNER bracket-link (the page number),
both resolving to the SAME `#slugified-heading` anchor, e.g.:
`[Section Name [6](#section-name)](#section-name)`. This shape is only
treated as a TOC block when at least two such lines appear consecutively
(allowing blank lines between them) -- a single link of this shape, or
scattered unrelated links elsewhere in a document, are never mistaken for
a generated TOC.

Key Input Dependencies: none (pure string transform, no filesystem/network access).

Function Index:
    - strip_raw_toc(markdown_text: str) -> str
        Removes every contiguous run of `#_Toc`-anchored bracket links
        (and any interleaved bookmark-anchor spans/blank lines), and every
        contiguous run (2+ lines) of same-anchor nested slug-link TOC
        entries, found anywhere in the document, leaving the rest of the
        document untouched. Normal markdown links (to real headings, not
        `_Toc` bookmarks, and not the double-nested same-anchor shape) are
        never touched.

Usage:
    from pandoc_fixes.toc import strip_raw_toc
    cleaned = strip_raw_toc(raw_markdown_text)
"""

import re

# An empty bookmark-anchor span pandoc emits for a Word bookmark, e.g.
# `[]{#_Toc1 .anchor}`.
_BOOKMARK_ANCHOR_LINE = re.compile(r'^\[\]\{#_Toc[^}]*\}\s*$', re.MULTILINE)

# A single TOC entry line: a bracket link whose target is a `_Toc` bookmark.
_TOC_LINK_LINE = re.compile(r'^\[[^\]]*\]\(#_Toc\d+\)\s*$', re.MULTILINE)

# A single slug-anchor TOC entry line: an outer bracket-link wrapping an
# inner bracket-link (the page number), both targeting the SAME
# `#slugified-heading` anchor, e.g.
# `[Section Name [6](#section-name)](#section-name)`. Matched individually
# here; `strip_raw_toc` requires a RUN of 2+ such lines before treating
# them as a generated TOC block (see module docstring) -- a single line of
# this shape is not, by itself, evidence of a generated TOC.
_TOC_SLUG_LINE = re.compile(
    r'^\[.*\[[^\]]*\]\(#([\w-]+)\)\]\(#\1\)\s*$', re.MULTILINE
)

# A "Table of Contents" marker line (optionally bold), commonly immediately
# preceding a generated TOC block. Only used to extend removal backward once
# a TOC run has already been positively identified -- never used on its own
# to trigger stripping.
_TOC_MARKER_LINE = re.compile(r'^\*{0,2}\s*table of contents\s*\*{0,2}\s*$', re.IGNORECASE)


def _is_bookmark_toc_line(stripped_line: str) -> bool:
    return bool(_BOOKMARK_ANCHOR_LINE.match(stripped_line) or _TOC_LINK_LINE.match(stripped_line))


def _is_slug_toc_line(stripped_line: str) -> bool:
    return bool(_TOC_SLUG_LINE.match(stripped_line))


def _is_toc_line(stripped_line: str) -> bool:
    return _is_bookmark_toc_line(stripped_line) or _is_slug_toc_line(stripped_line)


def strip_raw_toc(markdown_text: str) -> str:
    """Remove every raw Word TOC field dump found anywhere in the document.

    Scans the whole document (not just its start) for contiguous runs of
    `#_Toc` bookmark anchors and `#_Toc`-targeted bracket links — blank
    lines between TOC entries are treated as part of the same run — and
    drops those lines. A block preceded by ordinary content (e.g. a title
    heading) is detected just as reliably as one at the very top of the
    file. Content that is not part of a detected TOC run, including normal
    headings and normal markdown links that do not target `_Toc`
    bookmarks, is left untouched.
    """
    lines = markdown_text.splitlines(keepends=True)
    n = len(lines)
    keep = [True] * n

    i = 0
    while i < n:
        stripped = lines[i].rstrip("\n")
        if stripped.strip() == "" or not _is_toc_line(stripped):
            i += 1
            continue

        # Found the start of a candidate TOC run: scan forward, allowing
        # blank lines between TOC entries, until a non-blank line that is
        # not TOC-shaped ends the run.
        j = i
        last_toc_index = i
        toc_line_count = 0
        has_bookmark_toc_line = False
        while j < n:
            s = lines[j].rstrip("\n")
            if s.strip() == "":
                j += 1
                continue
            if _is_toc_line(s):
                last_toc_index = j
                toc_line_count += 1
                if _is_bookmark_toc_line(s):
                    has_bookmark_toc_line = True
                j += 1
                continue
            break

        # A `_Toc`-bookmark shape is unambiguous evidence on its own (a
        # single line suffices, matching prior behavior). The slug-anchor
        # shape is only treated as a generated TOC block once 2+ entries
        # appear consecutively -- a lone double-nested same-anchor link is
        # left alone (see module docstring).
        if has_bookmark_toc_line or toc_line_count >= 2:
            run_start = i
            # Extend backward over a "Table of Contents" marker line (and
            # any blank lines between it and the run) if present.
            m = run_start - 1
            while m >= 0 and lines[m].rstrip("\n").strip() == "":
                m -= 1
            if m >= 0 and _TOC_MARKER_LINE.match(lines[m].rstrip("\n").strip()) and keep[m]:
                run_start = m

            for k in range(run_start, last_toc_index + 1):
                keep[k] = False
            i = last_toc_index + 1
        else:
            i += 1

    result = "".join(lines[k] for k in range(n) if keep[k])
    # Collapse blank-line runs left behind by removed TOC blocks, and trim
    # a leading blank line if the removed block was at the very start.
    result = re.sub(r'\n{3,}', '\n\n', result)
    result = result.lstrip("\n")
    return result
