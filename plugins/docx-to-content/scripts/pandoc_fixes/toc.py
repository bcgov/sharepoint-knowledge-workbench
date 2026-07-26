#!/usr/bin/env python
"""
toc.py
======

Strips a raw Word-generated table-of-contents field dump from pandoc
markdown output. Word's TOC field converts, under pandoc, into a literal
run of bracket links pointing at internal `#_Toc<digits>` bookmarks (e.g.
`[Section Name](#_Toc123456)`), often preceded by an empty bookmark-anchor
span (`[]{#_Toc... }`). This is not usable navigation in plain markdown, so
the block is detected and removed wholesale.

Key Input Dependencies: none (pure string transform, no filesystem/network access).

Function Index:
    - strip_raw_toc(markdown_text: str) -> str
        Removes a leading run of `#_Toc`-anchored bracket links (and any
        preceding bookmark-anchor spans), leaving the rest of the document
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


def strip_raw_toc(markdown_text: str) -> str:
    """Remove a leading raw Word TOC field dump from markdown text.

    Detects a leading run made up only of blank lines, `#_Toc` bookmark
    anchors, and `#_Toc`-targeted bracket links, and removes that entire
    run. Content beyond the TOC dump (including normal headings and normal
    markdown links that do not target `_Toc` bookmarks) is left untouched.
    """
    lines = markdown_text.splitlines(keepends=True)

    end_index = 0
    saw_toc_content = False
    for i, line in enumerate(lines):
        stripped = line.rstrip("\n")
        if stripped.strip() == "":
            continue
        if _BOOKMARK_ANCHOR_LINE.match(stripped) or _TOC_LINK_LINE.match(stripped):
            saw_toc_content = True
            end_index = i + 1
            continue
        # First non-blank, non-TOC line: stop scanning.
        break

    if not saw_toc_content:
        return markdown_text

    remainder = "".join(lines[end_index:])
    # Drop leading blank lines left behind by the removed TOC block.
    remainder = remainder.lstrip("\n")
    return remainder
