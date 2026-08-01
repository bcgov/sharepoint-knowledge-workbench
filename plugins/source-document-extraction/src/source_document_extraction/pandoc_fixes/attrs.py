#!/usr/bin/env python
"""
attrs.py
========

Strips leftover pandoc attribute syntax from markdown text produced by
`pandoc -t markdown`. Pandoc emits attribute blocks such as
`{width="624" height="325"}` (after images) and bracketed spans such as
`[text]{.underline}` / `[text]{.mark}` (for underlined/highlighted runs).
These are pandoc-specific extensions, not standard markdown, and render as
literal visible text in GitHub/VS Code/standard markdown viewers.

Key Input Dependencies: none (pure string transform, no filesystem/network access).

Function Index:
    - strip_pandoc_attrs(markdown_text: str) -> str
        Removes bracketed-span attribute wrappers (preserving their inner
        text) and bare trailing attribute blocks (e.g. image dimensions),
        while leaving normal markdown links/brackets untouched.

Usage:
    from pandoc_fixes.attrs import strip_pandoc_attrs
    cleaned = strip_pandoc_attrs(raw_markdown_text)
"""

import re

# A pandoc attribute block: {.class #id key="value" key=value ...}
# Requires at least one attribute-like token so we don't match arbitrary
# curly-brace text that isn't pandoc attribute syntax.
_ATTR_TOKEN = r'(?:\.[\w-]+|#[\w-]+|[\w-]+="[^"]*"|[\w-]+=\S+)'
_ATTR_BLOCK = re.compile(r'\{\s*' + _ATTR_TOKEN + r'(?:\s+' + _ATTR_TOKEN + r')*\s*\}')

# A bracketed span immediately followed by an attribute block: [text]{...}
# Only matches when the bracket is NOT preceded by '!' (which would make it
# an image alt-text bracket, not a span) and not followed by '(' (which
# would make it a markdown link, e.g. [Section One](#section-one)).
_SPAN = re.compile(
    r'(?<!\!)\[([^\[\]]*)\]' + _ATTR_BLOCK.pattern
)


def strip_pandoc_attrs(markdown_text: str) -> str:
    """Strip pandoc-specific attribute syntax while preserving the content
    it annotates.

    - `[some text]{.underline}` / `[some text]{.mark}` -> `some text`
    - `![](media/image1.png){width="624" height="325"}` -> `![](media/image1.png)`

    Real markdown links (`[text](url)`) and plain bracketed text with no
    trailing attribute block are left untouched.
    """
    # Unwrap bracketed spans first (preserves the enclosed text).
    text = _SPAN.sub(r'\1', markdown_text)
    # Remove any remaining bare attribute blocks (e.g. trailing image attrs).
    text = _ATTR_BLOCK.sub('', text)
    return text
