#!/usr/bin/env python
"""test_attrs.py
=============

Purpose:
    TDD-first: failing tests for pandoc/attrs.py.

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - pandoc.attrs

TDD-first: failing tests for pandoc/attrs.py.
Covers stripping of leftover pandoc attribute syntax that renders as literal
visible text in GitHub/VS Code/standard markdown viewers:
  - image dimension attrs: {width="624" height="325"}
  - bracketed span attrs: [text]{.underline}, [text]{.mark}

Usage:
    pytest plugins/sharepoint-document-conversion/tests/extraction/unit/test_attrs.py -v

Key Functions Index:
    - TestStripPandocAttrs.test_strips_image_dimension_attrs()
    - TestStripPandocAttrs.test_strips_underline_span_preserving_text()
    - TestStripPandocAttrs.test_strips_mark_span_preserving_text()
    - TestStripPandocAttrs.test_leaves_plain_text_untouched()
    - TestStripPandocAttrs.test_leaves_normal_brackets_untouched()
    - TestStripPandocAttrs.test_strips_multiple_attrs_in_document()"""

from pandoc.attrs import strip_pandoc_attrs


class TestStripPandocAttrs:
    # Verify strips image dimension attrs.
    def test_strips_image_dimension_attrs(self):
        """Verify strips image dimension attrs."""
        text = '![](media/image1.png){width="624" height="325"}'
        assert strip_pandoc_attrs(text) == "![](media/image1.png)"

    # Verify strips underline span preserving text.
    def test_strips_underline_span_preserving_text(self):
        """Verify strips underline span preserving text."""
        text = "This is [important]{.underline} text."
        assert strip_pandoc_attrs(text) == "This is important text."

    # Verify strips mark span preserving text.
    def test_strips_mark_span_preserving_text(self):
        """Verify strips mark span preserving text."""
        text = "Please [note this]{.mark} carefully."
        assert strip_pandoc_attrs(text) == "Please note this carefully."

    # Verify leaves plain text untouched.
    def test_leaves_plain_text_untouched(self):
        """Verify leaves plain text untouched."""
        text = "Section One\n\nThis is a normal paragraph with no attributes."
        assert strip_pandoc_attrs(text) == text

    # Verify leaves normal brackets untouched.
    def test_leaves_normal_brackets_untouched(self):
        # A real markdown link should not be mistaken for a pandoc span.
        """Verify leaves normal brackets untouched."""
        text = "See [Section One](#section-one) for details."
        assert strip_pandoc_attrs(text) == text

    # Verify strips multiple attrs in document.
    def test_strips_multiple_attrs_in_document(self):
        """Verify strips multiple attrs in document."""
        text = (
            "## Introduction ![](media/image1.png){width=\"100\" height=\"50\"}\n\n"
            "The [term]{.underline} is defined below.\n"
        )
        expected = (
            "## Introduction ![](media/image1.png)\n\n"
            "The term is defined below.\n"
        )
        assert strip_pandoc_attrs(text) == expected
