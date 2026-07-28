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

# An ATX heading line: '#' markers, whitespace, then the rest of the line
# as heading text (trailing whitespace trimmed). Marker-boundary validity
# (whether the text is symmetrically wrapped in a matching emphasis pair)
# is checked separately in `_fully_wrapped`, NOT by this regex alone --
# see that function's docstring for why a pure regex/backreference
# approach is unsafe here.
_HEADING_LINE = re.compile(r'^(#{1,6})[ \t]+(.+?)[ \t]*$', re.MULTILINE)

# (marker_char, allowed run-lengths in order to try) -- longest first so
# `***text***` is checked against a length-3 run before a length-2 run.
# Single-asterisk (`*`) whole-heading wrapping is intentionally out of
# scope (see module docstring); underscore only ever occurs as a
# length-1 italic marker.
_MARKER_OPTIONS = (('*', (3, 2)), ('_', (1,)))


def _fully_wrapped(text: str):
    """Return the inner text if `text` is symmetrically wrapped in exactly
    one matching pair of emphasis markers of the SAME type and length on
    both sides, else return None.

    This exists because a regex using a backreference to only the OPENING
    marker (e.g. `(\\*\\*\\*|\\*\\*)...\\2`) can match a mismatched pair --
    e.g. text opened with `**` and closed with `***` -- because the
    non-greedy inner-text capture will happily absorb the extra marker
    character as if it were heading text, silently corrupting the heading
    (`**Text***` -> `Text*`) instead of leaving it untouched. Checking the
    exact run-length of marker characters at BOTH boundaries explicitly
    (via `text[L]`/`text[-L-1]` not being the marker character) closes
    that gap: a mismatched or overlong marker run is rejected outright and
    the heading is left completely untouched, per this module's contract
    that "not normalized" is always safe and "silently corrupted" never
    is.
    """
    for marker_char, lengths in _MARKER_OPTIONS:
        for length in lengths:
            marker = marker_char * length
            if not (text.startswith(marker) and text.endswith(marker)):
                continue
            if len(text) < 2 * length + 1:
                continue  # no room for non-empty inner content
            # Reject if the marker run at either boundary is actually
            # LONGER than `length` (i.e. the character just inside the
            # boundary is still the marker character) -- this is exactly
            # the mismatched-marker case that corrupted headings before.
            if text[length] == marker_char:
                continue
            if text[-length - 1] == marker_char:
                continue
            inner = text[length:-length]
            if inner.strip() == "":
                continue
            return inner
    return None


def strip_whole_heading_emphasis(markdown_text: str) -> str:
    """Strip whole-heading-wrapping emphasis markers from ATX headings.

    Only applies when a marker pair symmetrically wraps the ENTIRE heading
    text with no leftover/mismatched marker characters at either boundary
    (see `_fully_wrapped`); partial emphasis inside otherwise-plain
    heading text, emphasis outside of headings, and mismatched-marker
    boundaries (e.g. `**Text***`, `***Text**`) are all left completely
    untouched rather than partially/incorrectly stripped.
    """

    def _strip(match: "re.Match[str]") -> str:
        hashes, text = match.group(1), match.group(2)
        inner = _fully_wrapped(text)
        if inner is None:
            return match.group(0)
        return f"{hashes} {inner}"

    return _HEADING_LINE.sub(_strip, markdown_text)
