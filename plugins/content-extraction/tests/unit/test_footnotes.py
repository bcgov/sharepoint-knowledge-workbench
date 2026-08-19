#!/usr/bin/env python
"""
test_footnotes.py
==================

TDD-first: failing tests for pandoc/footnotes.py.
Covers detecting and removing orphaned footnote markers: a `[^1]` reference
in text with no matching `[^1]: definition` anywhere in the document, or a
`[^1]: definition` with no matching `[^1]` reference. Footnotes with a
matching reference AND definition must never be touched.

Usage:
    pytest plugins/source-document-extraction/tests/unit/test_footnotes.py -v
"""

from pandoc.footnotes import clean_orphaned_footnotes


class TestCleanOrphanedFootnotes:
    def test_leaves_matched_footnote_untouched(self):
        text = (
            "Some text with a note.[^1]\n\n"
            "[^1]: This is the footnote definition.\n"
        )
        assert clean_orphaned_footnotes(text) == text

    def test_removes_orphaned_reference_with_no_definition(self):
        text = "Some text with a dangling note.[^1]\n\nNo definition anywhere.\n"
        expected = "Some text with a dangling note.\n\nNo definition anywhere.\n"
        assert clean_orphaned_footnotes(text) == expected

    def test_removes_orphaned_definition_with_no_reference(self):
        text = (
            "Some text with no footnote markers at all.\n\n"
            "[^1]: An orphaned definition nobody points to.\n"
        )
        expected = "Some text with no footnote markers at all.\n\n"
        assert clean_orphaned_footnotes(text) == expected

    def test_handles_mixed_matched_and_orphaned(self):
        text = (
            "First note.[^1] Second dangling note.[^2]\n\n"
            "[^1]: Definition for note one.\n"
            "[^3]: Orphaned definition, no reference.\n"
        )
        expected = (
            "First note.[^1] Second dangling note.\n\n"
            "[^1]: Definition for note one.\n"
        )
        assert clean_orphaned_footnotes(text) == expected
