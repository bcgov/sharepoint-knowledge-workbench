#!/usr/bin/env python
"""test_footnotes.py
==================

Purpose:
    TDD-first: failing tests for pandoc/footnotes.py.

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - pandoc.footnotes

TDD-first: failing tests for pandoc/footnotes.py.
Covers detecting and removing orphaned footnote markers: a `[^1]` reference
in text with no matching `[^1]: definition` anywhere in the document, or a
`[^1]: definition` with no matching `[^1]` reference. Footnotes with a
matching reference AND definition must never be touched.

Usage:
    pytest plugins/sharepoint-document-conversion/tests/extraction/unit/test_footnotes.py -v

Key Functions Index:
    - TestCleanOrphanedFootnotes.test_leaves_matched_footnote_untouched()
    - TestCleanOrphanedFootnotes.test_removes_orphaned_reference_with_no_definition()
    - TestCleanOrphanedFootnotes.test_removes_orphaned_definition_with_no_reference()
    - TestCleanOrphanedFootnotes.test_handles_mixed_matched_and_orphaned()"""

from pandoc.footnotes import clean_orphaned_footnotes


class TestCleanOrphanedFootnotes:
    # Verify leaves matched footnote untouched.
    def test_leaves_matched_footnote_untouched(self):
        """Verify leaves matched footnote untouched."""
        text = (
            "Some text with a note.[^1]\n\n"
            "[^1]: This is the footnote definition.\n"
        )
        assert clean_orphaned_footnotes(text) == text

    # Verify removes orphaned reference with no definition.
    def test_removes_orphaned_reference_with_no_definition(self):
        """Verify removes orphaned reference with no definition."""
        text = "Some text with a dangling note.[^1]\n\nNo definition anywhere.\n"
        expected = "Some text with a dangling note.\n\nNo definition anywhere.\n"
        assert clean_orphaned_footnotes(text) == expected

    # Verify removes orphaned definition with no reference.
    def test_removes_orphaned_definition_with_no_reference(self):
        """Verify removes orphaned definition with no reference."""
        text = (
            "Some text with no footnote markers at all.\n\n"
            "[^1]: An orphaned definition nobody points to.\n"
        )
        expected = "Some text with no footnote markers at all.\n\n"
        assert clean_orphaned_footnotes(text) == expected

    # Verify handles mixed matched and orphaned.
    def test_handles_mixed_matched_and_orphaned(self):
        """Verify handles mixed matched and orphaned."""
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
