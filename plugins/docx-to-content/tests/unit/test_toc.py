#!/usr/bin/env python
"""
test_toc.py
===========

TDD-first: failing tests for pandoc_fixes/toc.py.
Covers detecting and stripping a raw Word-generated table-of-contents field
dump: a nested bracket-link tree (e.g. `[Section Name](#_Toc123456)`
repeated many times), often preceded by a bookmark anchor, that pandoc
converts literally instead of as real document structure.

Usage:
    pytest plugins/docx-to-content/tests/unit/test_toc.py -v
"""

from pandoc_fixes.toc import strip_raw_toc


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
