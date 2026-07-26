#!/usr/bin/env python
"""
test_pandoc_validate.py
========================

TDD-first: failing tests for pandoc_validate.py.
Covers the hard-fail validator: unresolved image links (relative paths that
don't exist under base_dir), leftover pandoc attribute artifacts (proves
attrs.py actually ran), and images still embedded directly in heading
lines.

Usage:
    pytest plugins/docx-to-content/tests/unit/test_pandoc_validate.py -v
"""

from pathlib import Path

from pandoc_validate import validate_cleaned_markdown


class TestValidateCleanedMarkdown:
    def test_passes_clean_document(self, tmp_path: Path):
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

    def test_fails_on_unresolved_image_link(self, tmp_path: Path):
        text = "![](media/missing.png)\n"
        result = validate_cleaned_markdown(text, tmp_path)
        assert result["status"] == "FAIL"
        assert any("missing.png" in e for e in result["errors"])

    def test_fails_on_leftover_attribute_artifact(self, tmp_path: Path):
        (tmp_path / "media").mkdir()
        (tmp_path / "media" / "image1.png").write_bytes(b"stub")
        text = '![](media/image1.png){width="624" height="325"}\n'
        result = validate_cleaned_markdown(text, tmp_path)
        assert result["status"] == "FAIL"
        assert any("attribute" in e.lower() for e in result["errors"])

    def test_fails_on_image_embedded_in_heading(self, tmp_path: Path):
        (tmp_path / "media").mkdir()
        (tmp_path / "media" / "image1.png").write_bytes(b"stub")
        text = "## Introduction ![](media/image1.png)\n"
        result = validate_cleaned_markdown(text, tmp_path)
        assert result["status"] == "FAIL"
        assert any("heading" in e.lower() for e in result["errors"])

    def test_reports_multiple_errors_together(self, tmp_path: Path):
        text = '## Intro ![](media/missing.png){width="1"}\n'
        result = validate_cleaned_markdown(text, tmp_path)
        assert result["status"] == "FAIL"
        assert len(result["errors"]) >= 2
