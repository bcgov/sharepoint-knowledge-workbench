#!/usr/bin/env python
"""test_images.py
==============

Purpose:
    TDD-first: failing tests for pandoc/images.py.

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - pandoc.images

TDD-first: failing tests for pandoc/images.py.
Covers detecting and fixing images glued directly onto heading lines or
list-item markers (no separating blank line/paragraph break), moving the
image reference to its own paragraph while preserving heading text and the
image reference itself.

Usage:
    pytest plugins/sharepoint-document-conversion/tests/extraction/unit/test_images.py -v

Key Functions Index:
    - TestFixGluedImages.test_separates_image_glued_to_heading()
    - TestFixGluedImages.test_separates_image_glued_to_list_item()
    - TestFixGluedImages.test_leaves_image_already_on_own_line()
    - TestFixGluedImages.test_leaves_plain_heading_untouched()
    - TestFixGluedImages.test_separates_image_glued_to_start_of_heading()
    - TestFixGluedImages.test_separates_image_glued_to_start_of_list_item()
    - TestFixGluedImages.test_handles_multiple_headings_with_glued_images()"""

from pandoc.images import fix_glued_images


class TestFixGluedImages:
    # Verify separates image glued to heading.
    def test_separates_image_glued_to_heading(self):
        """Verify separates image glued to heading."""
        text = "## Introduction ![](media/image1.png){width=\"100\" height=\"50\"}\n"
        expected = (
            "## Introduction\n\n"
            "![](media/image1.png){width=\"100\" height=\"50\"}\n"
        )
        assert fix_glued_images(text) == expected

    # Verify separates image glued to list item.
    def test_separates_image_glued_to_list_item(self):
        """Verify separates image glued to list item."""
        text = "- First item ![](media/image2.png)\n- Second item\n"
        expected = (
            "- First item\n\n"
            "![](media/image2.png)\n\n"
            "- Second item\n"
        )
        assert fix_glued_images(text) == expected

    # Verify leaves image already on own line.
    def test_leaves_image_already_on_own_line(self):
        """Verify leaves image already on own line."""
        text = "## Introduction\n\n![](media/image1.png)\n\nSome text.\n"
        assert fix_glued_images(text) == text

    # Verify leaves plain heading untouched.
    def test_leaves_plain_heading_untouched(self):
        """Verify leaves plain heading untouched."""
        text = "## Section One\n\nA normal paragraph.\n"
        assert fix_glued_images(text) == text

    # Verify separates image glued to start of heading.
    def test_separates_image_glued_to_start_of_heading(self):
        # Real-world shape: the image is glued to the START of the heading
        # text, with (often bold) text following on the same line.
        """Verify separates image glued to start of heading."""
        text = (
            "### ![](media/image12.png){width=\"5.45in\" height=\"2.2in\"}"
            "**Primary Module** (Technical Overview)\n"
        )
        expected = (
            "### **Primary Module** (Technical Overview)\n\n"
            "![](media/image12.png){width=\"5.45in\" height=\"2.2in\"}\n"
        )
        assert fix_glued_images(text) == expected

    # Verify separates image glued to start of list item.
    def test_separates_image_glued_to_start_of_list_item(self):
        """Verify separates image glued to start of list item."""
        text = "- ![](media/image3.png) First item\n- Second item\n"
        expected = (
            "- First item\n\n"
            "![](media/image3.png)\n\n"
            "- Second item\n"
        )
        assert fix_glued_images(text) == expected

    # Verify handles multiple headings with glued images.
    def test_handles_multiple_headings_with_glued_images(self):
        """Verify handles multiple headings with glued images."""
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
