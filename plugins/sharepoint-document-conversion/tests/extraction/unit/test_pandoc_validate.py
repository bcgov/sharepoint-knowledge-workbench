#!/usr/bin/env python
"""test_pandoc_validate.py
========================

Purpose:
    Tests for pandoc/validate.py's hard-fail validator: unresolved image links (relative paths that don't exist under base_dir), leftover pandoc attribute artifacts (proves attrs.py actually ran), and images still embedded directly in heading lines.

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - pathlib
    - pandoc.validate

Tests for pandoc/validate.py's hard-fail validator: unresolved image
links (relative paths that don't exist under base_dir), leftover pandoc
attribute artifacts (proves attrs.py actually ran), and images still
embedded directly in heading lines.

Usage:
    pytest plugins/sharepoint-document-conversion/tests/extraction/unit/test_pandoc_validate.py -v

Key Functions Index:
    - TestValidateCleanedMarkdown.test_passes_clean_document()
    - TestValidateCleanedMarkdown.test_fails_on_unresolved_image_link()
    - TestValidateCleanedMarkdown.test_fails_on_leftover_attribute_artifact()
    - TestValidateCleanedMarkdown.test_fails_on_image_embedded_in_heading()
    - TestValidateCleanedMarkdown.test_reports_multiple_errors_together()"""

from pathlib import Path

from pandoc.validate import validate_cleaned_markdown


class TestValidateCleanedMarkdown:
    # Verify passes clean document.
    def test_passes_clean_document(self, tmp_path: Path):
        """Verify passes clean document."""
        (tmp_path / "media").mkdir()
        (tmp_path / "media" / "image1.png").write_bytes(b"stub")

        text = (
            "## Introduction\n\n"
            "![](media/image1.png)\n\n"
            "Body text with no artifacts.\n"
        )
        result = validate_cleaned_markdown(text, tmp_path)
        assert result["status"] == "PASS"
        assert result["errors"] == []

    # Verify fails on unresolved image link.
    def test_fails_on_unresolved_image_link(self, tmp_path: Path):
        """Verify fails on unresolved image link."""
        text = "![](media/missing.png)\n"
        result = validate_cleaned_markdown(text, tmp_path)
        assert result["status"] == "FAIL"
        assert any("missing.png" in e for e in result["errors"])

    # Verify fails on leftover attribute artifact.
    def test_fails_on_leftover_attribute_artifact(self, tmp_path: Path):
        """Verify fails on leftover attribute artifact."""
        (tmp_path / "media").mkdir()
        (tmp_path / "media" / "image1.png").write_bytes(b"stub")
        text = '![](media/image1.png){width="624" height="325"}\n'
        result = validate_cleaned_markdown(text, tmp_path)
        assert result["status"] == "FAIL"
        assert any("attribute" in e.lower() for e in result["errors"])

    # Verify fails on image embedded in heading.
    def test_fails_on_image_embedded_in_heading(self, tmp_path: Path):
        """Verify fails on image embedded in heading."""
        (tmp_path / "media").mkdir()
        (tmp_path / "media" / "image1.png").write_bytes(b"stub")
        text = "## Introduction ![](media/image1.png)\n"
        result = validate_cleaned_markdown(text, tmp_path)
        assert result["status"] == "FAIL"
        assert any("heading" in e.lower() for e in result["errors"])

    # Verify reports multiple errors together.
    def test_reports_multiple_errors_together(self, tmp_path: Path):
        """Verify reports multiple errors together."""
        text = '## Intro ![](media/missing.png){width="1"}\n'
        result = validate_cleaned_markdown(text, tmp_path)
        assert result["status"] == "FAIL"
        assert len(result["errors"]) >= 2
