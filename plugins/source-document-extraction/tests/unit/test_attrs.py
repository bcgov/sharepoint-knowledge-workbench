#!/usr/bin/env python
"""
test_attrs.py
=============

TDD-first: failing tests for pandoc/attrs.py.
Covers stripping of leftover pandoc attribute syntax that renders as literal
visible text in GitHub/VS Code/standard markdown viewers:
  - image dimension attrs: {width="624" height="325"}
  - bracketed span attrs: [text]{.underline}, [text]{.mark}

Usage:
    pytest plugins/docx-to-content/tests/unit/test_attrs.py -v
"""

from pandoc.attrs import strip_pandoc_attrs


class TestStripPandocAttrs:
    def test_strips_image_dimension_attrs(self):
        text = '![](media/image1.png){width="624" height="325"}'
        assert strip_pandoc_attrs(text) == "![](media/image1.png)"

    def test_strips_underline_span_preserving_text(self):
        text = "This is [important]{.underline} text."
        assert strip_pandoc_attrs(text) == "This is important text."

    def test_strips_mark_span_preserving_text(self):
        text = "Please [note this]{.mark} carefully."
        assert strip_pandoc_attrs(text) == "Please note this carefully."

    def test_leaves_plain_text_untouched(self):
        text = "Section One\n\nThis is a normal paragraph with no attributes."
        assert strip_pandoc_attrs(text) == text

    def test_leaves_normal_brackets_untouched(self):
        # A real markdown link should not be mistaken for a pandoc span.
        text = "See [Section One](#section-one) for details."
        assert strip_pandoc_attrs(text) == text

    def test_strips_multiple_attrs_in_document(self):
        text = (
            "## Introduction ![](media/image1.png){width=\"100\" height=\"50\"}\n\n"
            "The [term]{.underline} is defined below.\n"
        )
        expected = (
            "## Introduction ![](media/image1.png)\n\n"
            "The term is defined below.\n"
        )
        assert strip_pandoc_attrs(text) == expected
