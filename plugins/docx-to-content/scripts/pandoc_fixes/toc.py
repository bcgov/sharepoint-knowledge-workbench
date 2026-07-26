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

Key Input Dependencies: none (pure string transform, no filesystem/network access).

Function Index:
    - strip_raw_toc(markdown_text: str) -> str
        Removes every contiguous run of `#_Toc`-anchored bracket links
        (and any interleaved bookmark-anchor spans/blank lines) found
        anywhere in the document, leaving the rest of the document
        untouched. Normal markdown links (to real headings, not `_Toc`
        bookmarks) are never touched.

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


def _is_toc_line(stripped_line: str) -> bool:
    return bool(_BOOKMARK_ANCHOR_LINE.match(stripped_line) or _TOC_LINK_LINE.match(stripped_line))


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
        while j < n:
            s = lines[j].rstrip("\n")
            if s.strip() == "":
                j += 1
                continue
            if _is_toc_line(s):
                last_toc_index = j
                j += 1
                continue
            break

        for k in range(i, last_toc_index + 1):
            keep[k] = False
        i = last_toc_index + 1

    result = "".join(lines[k] for k in range(n) if keep[k])
    # Collapse blank-line runs left behind by removed TOC blocks, and trim
    # a leading blank line if the removed block was at the very start.
    result = re.sub(r'\n{3,}', '\n\n', result)
    result = result.lstrip("\n")
    return result
