#!/usr/bin/env python
"""
test_toc.py
===========

TDD-first: failing tests for pandoc/toc.py.
Covers detecting and stripping a raw Word-generated table-of-contents field
dump: a nested bracket-link tree (e.g. `[Section Name](#_Toc123456)`
repeated many times), often preceded by a bookmark anchor, that pandoc
converts literally instead of as real document structure.

Usage:
    pytest plugins/docx-to-content/tests/unit/test_toc.py -v
"""

from pandoc.toc import strip_raw_toc


class TestStripRawToc:
    def test_strips_raw_toc_block(self):
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

    def test_leaves_normal_links_untouched(self):
        text = (
            "# Introduction\n\n"
            "See [Section One](#section-one) for details.\n\n"
            "[Section Two](#section-two) has more.\n"
        )
        assert strip_raw_toc(text) == text

    def test_leaves_document_with_no_toc_untouched(self):
        text = "# Section One\n\nJust a normal document body.\n"
        assert strip_raw_toc(text) == text

    def test_strips_toc_without_bookmark_anchor(self):
        text = (
            "[Section One](#_Toc111111)\n\n"
            "[Section Two](#_Toc222222)\n\n"
            "# Section One\n\n"
            "Body text.\n"
        )
        expected = "# Section One\n\nBody text.\n"
        assert strip_raw_toc(text) == expected

    def test_strips_slug_anchor_toc_block(self):
        # Real-world shape (CEIS Manual): pandoc converts a Word-generated
        # TOC field into nested markdown links -- an outer bracket-link
        # wrapping an inner bracket-link (the page number), both targeting
        # the same slugified-heading `#anchor`, repeated per TOC entry,
        # preceded by a "Table of Contents" marker line.
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

    def test_leaves_legitimate_internal_link_list_untouched(self):
        # A legitimate list of internal cross-reference links -- NOT the
        # double-nested-link-to-same-anchor TOC shape -- must survive.
        text = (
            "# Related Topics\n\n"
            "[See Section Alpha](#section-alpha)\n\n"
            "[See Section Beta](#section-beta)\n\n"
            "[See Section Gamma](#section-gamma)\n"
        )
        assert strip_raw_toc(text) == text

    def test_leaves_single_legitimate_link_adjacent_to_stripped_toc(self):
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

    def test_strips_toc_preceded_by_title_heading(self):
        # A common real-world document shape: a title/cover-page heading
        # appears before the Word-generated TOC block, so the TOC does not
        # start at line 1.
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
