#!/usr/bin/env python
"""
images.py
=========

Fixes images that pandoc glues directly onto heading lines or list-item
markers, in EITHER order:
    - text-then-image: `## Some Heading ![](media/image1.png)` or
      `- item text ![](media/image2.png)`
    - image-then-text: `### ![](media/image12.png){...}**Bold Heading**`
      or `- ![](media/image3.png) item text`
with no separating blank line. Such lines can confuse markdown renderers
about where the heading/list text ends and the image begins. This module
detects both orderings and moves the image reference to its own
paragraph, preserving both the heading/list text and the image reference.

Key Input Dependencies: none (pure string transform, no filesystem/network access).

Function Index:
    - fix_glued_images(markdown_text: str) -> str
        Splits an inline image glued to a heading or list-item line (image
        before OR after the text) onto its own paragraph, separated by a
        blank line on each side; heading/list-item text is always left as
        the text-only line, with the image moved to a following paragraph.

Usage:
    from pandoc.images import fix_glued_images
    cleaned = fix_glued_images(raw_markdown_text)
"""

import re

# An image reference, optionally followed by a pandoc attribute block.
# Alt text uses `(?:[^\]\\]|\\.)*` rather than a naive `[^\]]*` -- see
# scripts/package.py's _IMAGE_REF docstring: a markdown-escaped `]` in alt
# text otherwise terminates the character class early and the whole
# reference is silently missed.
_IMAGE = r'!\[(?:[^\]\\]|\\.)*\]\([^)]*\)(?:\{[^}]*\})?'

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

# A heading line with an image glued to the START of the heading text
# (image first, then text on the same line, no separating space handled --
# e.g. `### ![](img.png){...}**Bold Heading**`).
_HEADING_GLUED_LEADING_IMAGE = re.compile(
    r'^(#{1,6})[ \t]+(' + _IMAGE + r')[ \t]*(\S.*)$',
    re.MULTILINE,
)

# A list-item line with an image glued to the START of the item text
# (image first, then text, e.g. `- ![](img.png) item text`).
_LIST_ITEM_GLUED_LEADING_IMAGE = re.compile(
    r'^([ \t]*(?:[-*+]|\d+[.)]))[ \t]+(' + _IMAGE + r')[ \t]*(\S.*)$',
    re.MULTILINE,
)


def fix_glued_images(markdown_text: str) -> str:
    """Move images glued to heading/list-item lines onto their own paragraph.

    Handles both orderings -- text-then-image and image-then-text -- on
    heading and list-item lines. Preserves the heading/list-item text and
    the image reference verbatim; only inserts the blank-line separation
    needed for correct rendering, and (for the image-then-text case)
    reorders so the heading/list-item's own text stays on its native line
    and the image follows on its own paragraph, matching the same
    separation style as the text-then-image case.
    """

    def _split(match: "re.Match[str]") -> str:
        prefix, image = match.group(1), match.group(2)
        return f"{prefix}\n\n{image}\n\n"

    def _split_leading_image(match: "re.Match[str]") -> str:
        marker, image, text = match.group(1), match.group(2), match.group(3)
        return f"{marker} {text}\n\n{image}\n\n"

    text = _HEADING_GLUED.sub(_split, markdown_text)
    text = _LIST_ITEM_GLUED.sub(_split, text)
    text = _HEADING_GLUED_LEADING_IMAGE.sub(_split_leading_image, text)
    text = _LIST_ITEM_GLUED_LEADING_IMAGE.sub(_split_leading_image, text)
    # Collapse any run of 3+ newlines introduced by the split (e.g. when the
    # image was already followed by a blank line) back down to a single
    # blank-line paragraph break, and trim a trailing blank line added when
    # the image was already at end-of-file.
    text = re.sub(r'\n{3,}', '\n\n', text)
    if text.endswith('\n\n') and not markdown_text.endswith('\n\n'):
        text = text[:-1]
    return text
