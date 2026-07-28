#!/usr/bin/env python
"""
test_images.py
==============

TDD-first: failing tests for pandoc_fixes/images.py.
Covers detecting and fixing images glued directly onto heading lines or
list-item markers (no separating blank line/paragraph break), moving the
image reference to its own paragraph while preserving heading text and the
image reference itself.

Usage:
    pytest plugins/docx-to-content/tests/unit/test_images.py -v
"""

from pandoc_fixes.images import fix_glued_images


class TestFixGluedImages:
    def test_separates_image_glued_to_heading(self):
        text = "## Introduction ![](media/image1.png){width=\"100\" height=\"50\"}\n"
        expected = (
            "## Introduction\n\n"
            "![](media/image1.png){width=\"100\" height=\"50\"}\n"
        )
        assert fix_glued_images(text) == expected

    def test_separates_image_glued_to_list_item(self):
        text = "- First item ![](media/image2.png)\n- Second item\n"
        expected = (
            "- First item\n\n"
            "![](media/image2.png)\n\n"
            "- Second item\n"
        )
        assert fix_glued_images(text) == expected

    def test_leaves_image_already_on_own_line(self):
        text = "## Introduction\n\n![](media/image1.png)\n\nSome text.\n"
        assert fix_glued_images(text) == text

    def test_leaves_plain_heading_untouched(self):
        text = "## Section One\n\nA normal paragraph.\n"
        assert fix_glued_images(text) == text

    def test_separates_image_glued_to_start_of_heading(self):
        # Real-world shape (CEIS Manual): the image is glued to the START
        # of the heading text, with (often bold) text following on the
        # same line, no separating space.
        text = (
            "### ![](media/image12.png){width=\"5.45in\" height=\"2.2in\"}"
            "**Central Divorce** (Supreme Court Divorce Files only*)*\n"
        )
        expected = (
            "### **Central Divorce** (Supreme Court Divorce Files only*)*\n\n"
            "![](media/image12.png){width=\"5.45in\" height=\"2.2in\"}\n"
        )
        assert fix_glued_images(text) == expected

    def test_separates_image_glued_to_start_of_list_item(self):
        text = "- ![](media/image3.png) First item\n- Second item\n"
        expected = (
            "- First item\n\n"
            "![](media/image3.png)\n\n"
            "- Second item\n"
        )
        assert fix_glued_images(text) == expected

    def test_handles_multiple_headings_with_glued_images(self):
        text = (
            "## Section One ![](media/image1.png)\n\n"
            "Body text.\n\n"
            "## Section Two ![](media/image2.png)\n"
        )
        expected = (
            "## Section One\n\n"
            "![](media/image1.png)\n\n"
            "Body text.\n\n"
            "## Section Two\n\n"
            "![](media/image2.png)\n"
        )
        assert fix_glued_images(text) == expected
