#!/usr/bin/env python
"""
images.py
=========

Fixes images that pandoc glues directly onto heading lines or list-item
markers (e.g. `## Some Heading ![](media/image1.png)` or
`- item text ![](media/image2.png)`), with no separating blank line. Such
lines can confuse markdown renderers about where the heading/list text ends
and the image begins. This module detects the pattern and moves the image
reference to its own paragraph, preserving both the heading/list text and
the image reference.

Key Input Dependencies: none (pure string transform, no filesystem/network access).

Function Index:
    - fix_glued_images(markdown_text: str) -> str
        Splits an inline image trailing a heading or list-item line onto
        its own paragraph, separated by a blank line on each side.

Usage:
    from pandoc_fixes.images import fix_glued_images
    cleaned = fix_glued_images(raw_markdown_text)
"""

import re

# An image reference, optionally followed by a pandoc attribute block.
_IMAGE = r'!\[[^\]]*\]\([^)]*\)(?:\{[^}]*\})?'

# A heading line (1-6 '#') with trailing text then an image glued to the end.
_HEADING_GLUED = re.compile(
    r'^(#{1,6} .*?)[ \t]+(' + _IMAGE + r')[ \t]*$',
    re.MULTILINE,
)

# A list item line ('-', '*', '+', or numbered) with trailing text then a
# glued image. The separator is restricted to spaces/tabs (not newlines) so
# an image that already sits on its own line/paragraph is left untouched.
_LIST_ITEM_GLUED = re.compile(
    r'^([ \t]*(?:[-*+]|\d+[.)]) .*?)[ \t]+(' + _IMAGE + r')[ \t]*$',
    re.MULTILINE,
)


def fix_glued_images(markdown_text: str) -> str:
    """Move images glued to heading/list-item lines onto their own paragraph.

    Preserves the heading/list-item text and the image reference verbatim;
    only inserts the blank-line separation needed for correct rendering.
    """

    def _split(match: "re.Match[str]") -> str:
        prefix, image = match.group(1), match.group(2)
        return f"{prefix}\n\n{image}\n\n"

    text = _HEADING_GLUED.sub(_split, markdown_text)
    text = _LIST_ITEM_GLUED.sub(_split, text)
    # Collapse any run of 3+ newlines introduced by the split (e.g. when the
    # image was already followed by a blank line) back down to a single
    # blank-line paragraph break, and trim a trailing blank line added when
    # the image was already at end-of-file.
    text = re.sub(r'\n{3,}', '\n\n', text)
    if text.endswith('\n\n') and not markdown_text.endswith('\n\n'):
        text = text[:-1]
    return text
