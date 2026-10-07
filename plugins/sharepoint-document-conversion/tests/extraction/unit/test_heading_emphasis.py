#!/usr/bin/env python
"""test_heading_emphasis.py
=========================

Purpose:
    TDD-first: failing tests for pandoc/heading_emphasis.py.

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - pandoc.heading_emphasis

TDD-first: failing tests for pandoc/heading_emphasis.py.
Covers normalizing a heading whose ENTIRE text content is wrapped in a
single matching pair of emphasis markers (bold `**...**`, or the combined
bold+italic `***...***`) -- extraction noise, not intended canonical
heading text. Partial emphasis inside a heading (only part of the text
wrapped) must be left untouched.

Usage:
    pytest plugins/sharepoint-document-conversion/tests/extraction/unit/test_heading_emphasis.py -v

Key Functions Index:
    - TestStripWholeHeadingEmphasis.test_strips_whole_heading_bold()
    - TestStripWholeHeadingEmphasis.test_strips_whole_heading_bold_italic()
    - TestStripWholeHeadingEmphasis.test_leaves_partial_emphasis_untouched()
    - TestStripWholeHeadingEmphasis.test_leaves_non_heading_emphasis_untouched()
    - TestStripWholeHeadingEmphasis.test_leaves_plain_heading_untouched()
    - TestStripWholeHeadingEmphasis.test_preserves_heading_level()
    - TestStripWholeHeadingEmphasis.test_handles_multiple_headings()
    - TestStripWholeHeadingEmphasis.test_strips_whole_heading_underscore_italic()
    - TestStripWholeHeadingEmphasis.test_leaves_mismatched_marker_boundary_untouched_open_two_close_three()
    - TestStripWholeHeadingEmphasis.test_leaves_mismatched_marker_boundary_untouched_open_three_close_two()
    - TestStripWholeHeadingEmphasis.test_leaves_single_asterisk_italic_whole_heading_untouched_if_ambiguous()"""

from pandoc.heading_emphasis import strip_whole_heading_emphasis


class TestStripWholeHeadingEmphasis:
    # Verify strips whole heading bold.
    def test_strips_whole_heading_bold(self):
        """Verify strips whole heading bold."""
        text = "# **SAMPLE TOPIC**\n\nBody text.\n"
        expected = "# SAMPLE TOPIC\n\nBody text.\n"
        assert strip_whole_heading_emphasis(text) == expected

    # Verify strips whole heading bold italic.
    def test_strips_whole_heading_bold_italic(self):
        """Verify strips whole heading bold italic."""
        text = "### ***Extended Access***\n\nBody text.\n"
        expected = "### Extended Access\n\nBody text.\n"
        assert strip_whole_heading_emphasis(text) == expected

    # Verify leaves partial emphasis untouched.
    def test_leaves_partial_emphasis_untouched(self):
        """Verify leaves partial emphasis untouched."""
        text = "# Getting **Started** Quickly\n\nBody text.\n"
        assert strip_whole_heading_emphasis(text) == text

    # Verify leaves non heading emphasis untouched.
    def test_leaves_non_heading_emphasis_untouched(self):
        """Verify leaves non heading emphasis untouched."""
        text = "# Section\n\nThis is **bold** text in a paragraph.\n"
        assert strip_whole_heading_emphasis(text) == text

    # Verify leaves plain heading untouched.
    def test_leaves_plain_heading_untouched(self):
        """Verify leaves plain heading untouched."""
        text = "## Plain Heading\n\nBody text.\n"
        assert strip_whole_heading_emphasis(text) == text

    # Verify preserves heading level.
    def test_preserves_heading_level(self):
        """Verify preserves heading level."""
        text = "#### **Deep Heading**\n"
        expected = "#### Deep Heading\n"
        assert strip_whole_heading_emphasis(text) == expected

    # Verify handles multiple headings.
    def test_handles_multiple_headings(self):
        """Verify handles multiple headings."""
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

    # Verify strips whole heading underscore italic.
    def test_strips_whole_heading_underscore_italic(self):
        # Underscore-delimited italic (`_..._`) is unambiguous (unlike
        # `*...*`, which collides with list-item marker syntax at the start
        # of a line), so it's handled the same as bold/bold-italic.
        """Verify strips whole heading underscore italic."""
        text = "# _Just Italic_\n\nBody text.\n"
        expected = "# Just Italic\n\nBody text.\n"
        assert strip_whole_heading_emphasis(text) == expected

    # Verify leaves mismatched marker boundary untouched open two close three.
    def test_leaves_mismatched_marker_boundary_untouched_open_two_close_three(self):
        # Opened with `**`, closed with `***` -- a marker-type mismatch.
        # Must be left completely untouched, not partially stripped into a
        # heading with a stray trailing asterisk.
        """Verify leaves mismatched marker boundary untouched open two close three."""
        text = "# **Text***\n\nBody.\n"
        assert strip_whole_heading_emphasis(text) == text

    # Verify leaves mismatched marker boundary untouched open three close two.
    def test_leaves_mismatched_marker_boundary_untouched_open_three_close_two(self):
        """Verify leaves mismatched marker boundary untouched open three close two."""
        text = "# ***Text**\n\nBody.\n"
        assert strip_whole_heading_emphasis(text) == text

    # Verify leaves single asterisk italic whole heading untouched if ambiguous.
    def test_leaves_single_asterisk_italic_whole_heading_untouched_if_ambiguous(self):
        # Single-asterisk italic wrapping a whole heading is scoped out
        # (see module docstring): `*` is also used for list-item markers
        # and cannot be reliably distinguished from stray formatting at the
        # heading-text level without much higher risk of false positives.
        # This test documents that this case is intentionally NOT handled.
        """Verify leaves single asterisk italic whole heading untouched if ambiguous."""
        text = "# *Just Italic*\n\nBody text.\n"
        assert strip_whole_heading_emphasis(text) == text
