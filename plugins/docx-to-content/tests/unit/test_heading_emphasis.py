#!/usr/bin/env python
"""
test_heading_emphasis.py
=========================

TDD-first: failing tests for pandoc_fixes/heading_emphasis.py.
Covers normalizing a heading whose ENTIRE text content is wrapped in a
single matching pair of emphasis markers (bold `**...**`, or the combined
bold+italic `***...***`) -- extraction noise, not intended canonical
heading text. Partial emphasis inside a heading (only part of the text
wrapped) must be left untouched.

Usage:
    pytest plugins/docx-to-content/tests/unit/test_heading_emphasis.py -v
"""

from pandoc_fixes.heading_emphasis import strip_whole_heading_emphasis


class TestStripWholeHeadingEmphasis:
    def test_strips_whole_heading_bold(self):
        text = "# **PROTECTION ORDERS**\n\nBody text.\n"
        expected = "# PROTECTION ORDERS\n\nBody text.\n"
        assert strip_whole_heading_emphasis(text) == expected

    def test_strips_whole_heading_bold_italic(self):
        text = "### ***Extended Access***\n\nBody text.\n"
        expected = "### Extended Access\n\nBody text.\n"
        assert strip_whole_heading_emphasis(text) == expected

    def test_leaves_partial_emphasis_untouched(self):
        text = "# Getting **Started** Quickly\n\nBody text.\n"
        assert strip_whole_heading_emphasis(text) == text

    def test_leaves_non_heading_emphasis_untouched(self):
        text = "# Section\n\nThis is **bold** text in a paragraph.\n"
        assert strip_whole_heading_emphasis(text) == text

    def test_leaves_plain_heading_untouched(self):
        text = "## Plain Heading\n\nBody text.\n"
        assert strip_whole_heading_emphasis(text) == text

    def test_preserves_heading_level(self):
        text = "#### **Deep Heading**\n"
        expected = "#### Deep Heading\n"
        assert strip_whole_heading_emphasis(text) == expected

    def test_handles_multiple_headings(self):
        text = (
            "# **Title One**\n\n"
            "Body.\n\n"
            "## Normal Heading\n\n"
            "More body.\n\n"
            "### ***Title Three***\n"
        )
        expected = (
            "# Title One\n\n"
            "Body.\n\n"
            "## Normal Heading\n\n"
            "More body.\n\n"
            "### Title Three\n"
        )
        assert strip_whole_heading_emphasis(text) == expected

    def test_strips_whole_heading_underscore_italic(self):
        # Underscore-delimited italic (`_..._`) is unambiguous (unlike
        # `*...*`, which collides with list-item marker syntax at the start
        # of a line), so it's handled the same as bold/bold-italic.
        text = "# _Just Italic_\n\nBody text.\n"
        expected = "# Just Italic\n\nBody text.\n"
        assert strip_whole_heading_emphasis(text) == expected

    def test_leaves_single_asterisk_italic_whole_heading_untouched_if_ambiguous(self):
        # Single-asterisk italic wrapping a whole heading is scoped out
        # (see module docstring): `*` is also used for list-item markers
        # and cannot be reliably distinguished from stray formatting at the
        # heading-text level without much higher risk of false positives.
        # This test documents that this case is intentionally NOT handled.
        text = "# *Just Italic*\n\nBody text.\n"
        assert strip_whole_heading_emphasis(text) == text
