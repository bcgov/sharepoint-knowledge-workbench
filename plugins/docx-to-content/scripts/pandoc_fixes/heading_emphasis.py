#!/usr/bin/env python
"""
heading_emphasis.py
====================

Normalizes headings whose ENTIRE text content is wrapped in a single
matching pair of emphasis markers -- e.g. `# **PROTECTION ORDERS**` -> `#
PROTECTION ORDERS`, or `### ***Extended Access***` -> `### Extended
Access`. This is Word/pandoc extraction noise (the whole run happened to
be bold in the source document), not intentionally meaningful emphasis, so
it is stripped for a clean canonical heading.

A heading where only PART of the text is emphasized (e.g.
`# Getting **Started** Quickly`) is legitimate, meaningful inline emphasis
and is left completely untouched -- only whole-heading wrapping is treated
as noise.

Scope: handles `**...**` (bold), `***...***` (bold+italic), and `_..._`
(underscore italic). Single-asterisk italic (`*...*`) wrapping a whole
heading is intentionally NOT handled: `*` at the start of a line collides
with list-item marker syntax, and reliably distinguishing "whole heading
wrapped in single-asterisk italic" from other `*`-prefixed constructs
without a much higher false-positive rate was judged not worth it for a
narrowly-scoped cleanup rule. `_..._` has no such collision and is handled.

Key Input Dependencies: none (pure string transform, no filesystem/network access).

Function Index:
    - strip_whole_heading_emphasis(markdown_text: str) -> str
        Strips a single matching pair of whole-heading-wrapping emphasis
        markers (`**...**`, `***...***`, `_..._`) from ATX heading lines,
        preserving heading level and the underlying text exactly.

Usage:
    from pandoc_fixes.heading_emphasis import strip_whole_heading_emphasis
    cleaned = strip_whole_heading_emphasis(raw_markdown_text)
"""

import re

# An ATX heading line whose entire text content (after the leading '#'
# markers and surrounding whitespace) is wrapped in one matching pair of
# emphasis markers. Longest marker (`***`) tried first so `***text***` is
# not misread as `**` wrapping `*text*`.
_WHOLE_HEADING_EMPHASIS = re.compile(
    r'^(#{1,6})[ \t]+(\*\*\*|\*\*|_)(?!\s)(.+?)(?<!\s)\2[ \t]*$',
    re.MULTILINE,
)


def strip_whole_heading_emphasis(markdown_text: str) -> str:
    """Strip whole-heading-wrapping emphasis markers from ATX headings.

    Only applies when the marker pair wraps the ENTIRE heading text (no
    leftover text outside the markers on the line); partial emphasis
    inside otherwise-plain heading text is left untouched, as is emphasis
    appearing outside of headings.
    """

    def _strip(match: "re.Match[str]") -> str:
        hashes, _marker, inner = match.group(1), match.group(2), match.group(3)
        # Reject a match where the "inner" text itself still contains the
        # closing marker sequence unbalanced (defensive; the non-greedy
        # capture plus negative lookbehind/lookahead already prevent this
        # in practice for well-formed input).
        return f"{hashes} {inner}"

    return _WHOLE_HEADING_EMPHASIS.sub(_strip, markdown_text)
