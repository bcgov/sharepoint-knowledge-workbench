#!/usr/bin/env python
"""test_toc.py
===========

Purpose:
    TDD-first: failing tests for pandoc/toc.py.

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - pandoc.toc

TDD-first: failing tests for pandoc/toc.py.
Covers detecting and stripping a raw Word-generated table-of-contents field
dump: a nested bracket-link tree (e.g. `[Section Name](#_Toc123456)`
repeated many times), often preceded by a bookmark anchor, that pandoc
converts literally instead of as real document structure.

Usage:
    pytest plugins/sharepoint-document-conversion/tests/extraction/unit/test_toc.py -v

Key Functions Index:
    - TestStripRawToc.test_strips_raw_toc_block()
    - TestStripRawToc.test_leaves_normal_links_untouched()
    - TestStripRawToc.test_leaves_document_with_no_toc_untouched()
    - TestStripRawToc.test_strips_toc_without_bookmark_anchor()
    - TestStripRawToc.test_strips_slug_anchor_toc_block()
    - TestStripRawToc.test_leaves_legitimate_internal_link_list_untouched()
    - TestStripRawToc.test_leaves_single_legitimate_link_adjacent_to_stripped_toc()
    - TestStripRawToc.test_strips_toc_preceded_by_title_heading()"""

from pandoc.toc import strip_raw_toc


class TestStripRawToc:
    # Verify strips raw TOC block.
    def test_strips_raw_toc_block(self):
        """Verify strips raw TOC block."""
        text = (
            "[]{#_Toc1 .anchor}\n\n"
            "[Section One](#_Toc111111)\n\n"
            "[Section Two](#_Toc222222)\n\n"
            "[Section Three](#_Toc333333)\n\n"
            "# Section One\n\n"
            "Body text.\n"
        )
        expected = (
            "# Section One\n\n"
            "Body text.\n"
        )
        assert strip_raw_toc(text) == expected

    # Verify leaves normal links untouched.
    def test_leaves_normal_links_untouched(self):
        """Verify leaves normal links untouched."""
        text = (
            "# Introduction\n\n"
            "See [Section One](#section-one) for details.\n\n"
            "[Section Two](#section-two) has more.\n"
        )
        assert strip_raw_toc(text) == text

    # Verify leaves document with no TOC untouched.
    def test_leaves_document_with_no_toc_untouched(self):
        """Verify leaves document with no TOC untouched."""
        text = "# Section One\n\nJust a normal document body.\n"
        assert strip_raw_toc(text) == text

    # Verify strips TOC without bookmark anchor.
    def test_strips_toc_without_bookmark_anchor(self):
        """Verify strips TOC without bookmark anchor."""
        text = (
            "[Section One](#_Toc111111)\n\n"
            "[Section Two](#_Toc222222)\n\n"
            "# Section One\n\n"
            "Body text.\n"
        )
        expected = "# Section One\n\nBody text.\n"
        assert strip_raw_toc(text) == expected

    # Verify strips slug anchor TOC block.
    def test_strips_slug_anchor_toc_block(self):
        # Real-world shape: pandoc converts a Word-generated
        # TOC field into nested markdown links -- an outer bracket-link
        # wrapping an inner bracket-link (the page number), both targeting
        # the same slugified-heading `#anchor`, repeated per TOC entry,
        # preceded by a "Table of Contents" marker line.
        """Verify strips slug anchor TOC block."""
        text = (
            "**Table of Contents**\n\n"
            "[Section Alpha [1](#section-alpha)](#section-alpha)\n\n"
            "[Section Beta [2](#section-beta)](#section-beta)\n\n"
            "[Section Gamma [3](#section-gamma)](#section-gamma)\n\n"
            "[Section Delta [4](#section-delta)](#section-delta)\n\n"
            "[Section Epsilon [5](#section-epsilon)](#section-epsilon)\n\n"
            "# Section Alpha\n\n"
            "Body text.\n"
        )
        expected = (
            "# Section Alpha\n\n"
            "Body text.\n"
        )
        assert strip_raw_toc(text) == expected

    # Verify leaves legitimate internal link list untouched.
    def test_leaves_legitimate_internal_link_list_untouched(self):
        # A legitimate list of internal cross-reference links -- NOT the
        # double-nested-link-to-same-anchor TOC shape -- must survive.
        """Verify leaves legitimate internal link list untouched."""
        text = (
            "# Related Topics\n\n"
            "[See Section Alpha](#section-alpha)\n\n"
            "[See Section Beta](#section-beta)\n\n"
            "[See Section Gamma](#section-gamma)\n"
        )
        assert strip_raw_toc(text) == text

    # Verify leaves single legitimate link adjacent to stripped TOC.
    def test_leaves_single_legitimate_link_adjacent_to_stripped_toc(self):
        """Verify leaves single legitimate link adjacent to stripped TOC."""
        text = (
            "**Table of Contents**\n\n"
            "[Section Alpha [1](#section-alpha)](#section-alpha)\n\n"
            "[Section Beta [2](#section-beta)](#section-beta)\n\n"
            "# Section Alpha\n\n"
            "See [Section Beta](#section-beta) for details.\n"
        )
        expected = (
            "# Section Alpha\n\n"
            "See [Section Beta](#section-beta) for details.\n"
        )
        assert strip_raw_toc(text) == expected

    # Verify strips TOC preceded by title heading.
    def test_strips_toc_preceded_by_title_heading(self):
        # A common real-world document shape: a title/cover-page heading
        # appears before the Word-generated TOC block, so the TOC does not
        # start at line 1.
        """Verify strips TOC preceded by title heading."""
        text = (
            "# Company Manual\n\n"
            "[]{#_Toc1 .anchor}\n\n"
            "[Section One](#_Toc111111)\n\n"
            "[Section Two](#_Toc222222)\n\n"
            "# Section One\n\n"
            "Body text.\n"
        )
        expected = (
            "# Company Manual\n\n"
            "# Section One\n\n"
            "Body text.\n"
        )
        assert strip_raw_toc(text) == expected
