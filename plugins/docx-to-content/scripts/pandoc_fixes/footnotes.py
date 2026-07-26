#!/usr/bin/env python
"""
footnotes.py
============

Detects and removes orphaned footnote markers left over from pandoc
conversion: a `[^label]` reference in the body text with no matching
`[^label]: definition` line anywhere in the document, or vice versa (a
definition with no matching reference). Footnotes with both a reference and
a matching definition are never touched — content is only dropped when it
is provably orphaned on one side of the pair.

Key Input Dependencies: none (pure string transform, no filesystem/network access).

Function Index:
    - clean_orphaned_footnotes(markdown_text: str) -> str
        Removes footnote reference markers with no matching definition, and
        footnote definition lines with no matching reference.

Usage:
    from pandoc_fixes.footnotes import clean_orphaned_footnotes
    cleaned = clean_orphaned_footnotes(raw_markdown_text)
"""

import re

_REFERENCE = re.compile(r'\[\^([\w-]+)\]')
_DEFINITION_LINE = re.compile(r'^\[\^([\w-]+)\]:.*$', re.MULTILINE)


def clean_orphaned_footnotes(markdown_text: str) -> str:
    """Remove orphaned footnote references and definitions.

    A reference `[^label]` is removed if no `[^label]: ...` definition line
    exists anywhere in the document. A definition line `[^label]: ...` is
    removed if no `[^label]` reference exists anywhere in the body text.
    Matched pairs (reference + definition for the same label) are preserved
    verbatim.
    """
    definition_labels = {m.group(1) for m in _DEFINITION_LINE.finditer(markdown_text)}

    lines = markdown_text.splitlines(keepends=True)

    # Reference labels: any `[^label]` occurrence on a line that is NOT
    # itself a definition line.
    reference_labels = set()
    for line in lines:
        stripped = line.rstrip("\n")
        if _DEFINITION_LINE.match(stripped):
            continue
        reference_labels.update(m.group(1) for m in _REFERENCE.finditer(stripped))

    matched_labels = definition_labels & reference_labels

    def _strip_unmatched_reference(match: "re.Match[str]") -> str:
        label = match.group(1)
        if label in matched_labels:
            return match.group(0)
        return ""

    output_lines = []
    for line in lines:
        stripped = line.rstrip("\n")
        def_match = _DEFINITION_LINE.match(stripped)
        if def_match:
            if def_match.group(1) in matched_labels:
                output_lines.append(line)
            # else: orphaned definition line, drop entirely.
            continue
        output_lines.append(_REFERENCE.sub(_strip_unmatched_reference, line))

    return "".join(output_lines)
