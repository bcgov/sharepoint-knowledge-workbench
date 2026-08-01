#!/usr/bin/env python
"""
test_regression_pipeline.py
=============================

Regression fixture proving all six pandoc modules plus emf_convert
and pandoc_validate compose correctly, in the spec Section 7.2 pipeline
order (attrs -> images -> toc -> tables -> footnotes -> legacy image
conversion -> validation), against a single synthetic markdown fixture
(`tests/fixtures/regression_raw.md`) that exercises every defect category
at once: a raw Word TOC dump, an image glued to a heading, an image glued
to a list item, pandoc attribute artifacts (image dims, .underline, .mark),
a malformed table (missing separator row), a matched footnote, an orphaned
reference, an orphaned definition, and a legacy .emf image reference.

Wiring these calls into one reusable pipeline function is Task 9's job, not
this task's — this test only proves the modules don't conflict when run
together in the documented order.

Usage:
    pytest plugins/docx-to-content/tests/unit/test_regression_pipeline.py -v
"""

import shutil
import struct
from pathlib import Path

import pytest

from emf_convert import convert_legacy_media
from pandoc.attrs import strip_pandoc_attrs
from pandoc.footnotes import clean_orphaned_footnotes
from pandoc.images import fix_glued_images
from pandoc.tables import fix_malformed_tables
from pandoc.toc import strip_raw_toc
from pandoc.validate import validate_cleaned_markdown

FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "regression_raw.md"
SOFFICE_AVAILABLE = shutil.which("soffice") is not None


def _write_minimal_emf(path: Path) -> None:
    """Minimal but structurally valid .emf (bare EMR_HEADER + EMR_EOF),
    real enough for `soffice` to convert, matching test_emf_convert.py."""
    header_size = 88
    eof_size = 20
    total = header_size + eof_size

    header = struct.pack("<II", 1, header_size)
    header += struct.pack("<4i", 0, 0, 99, 99)
    header += struct.pack("<4i", 0, 0, 2540, 2540)
    header += struct.pack("<I", 0x464D4520)
    header += struct.pack("<I", 0x00010000)
    header += struct.pack("<I", total)
    header += struct.pack("<I", 2)
    header += struct.pack("<HH", 1, 0)
    header += struct.pack("<I", 0)
    header += struct.pack("<I", 0)
    header += struct.pack("<I", 0)
    header += struct.pack("<2i", 320, 240)
    header += struct.pack("<2i", 96, 72)

    eof = struct.pack("<II", 14, eof_size)
    eof += struct.pack("<III", 0, 0, eof_size)

    path.write_bytes(header + eof)


class TestRegressionPipeline:
    def test_all_modules_compose_without_conflict(self, tmp_path: Path):
        media_dir = tmp_path / "media"
        media_dir.mkdir()
        (media_dir / "image1.png").write_bytes(b"stub-png-1")
        (media_dir / "image2.png").write_bytes(b"stub-png-2")

        text = FIXTURE_PATH.read_text(encoding="utf-8")

        # Pipeline order per spec Section 7.2.
        text = strip_pandoc_attrs(text)
        text = fix_glued_images(text)
        text = strip_raw_toc(text)
        text = fix_malformed_tables(text)
        text = clean_orphaned_footnotes(text)

        # --- attrs.py: pandoc attribute artifacts removed ---
        assert '{width="100" height="50"}' not in text
        assert "{.underline}" not in text
        assert "{.mark}" not in text
        assert "[term]" not in text  # span unwrapped
        assert "a term that pandoc" in text
        assert "highlighted note" in text

        # --- images.py: glued images separated onto their own paragraph ---
        assert "# Introduction\n\n![](media/image1.png)" in text
        assert "First bullet with an inline image\n\n![](media/image2.png)" in text

        # --- toc.py: raw Word TOC dump removed, real heading kept ---
        assert "_Toc" not in text
        assert text.lstrip().startswith("# Introduction")

        # --- tables.py: missing header separator row inserted ---
        assert "| --- | --- |" in text

        # --- footnotes.py: matched pair kept, orphans removed ---
        assert "[^1]" in text
        assert "[^1]: This footnote has a matching reference." in text
        assert "[^2]" not in text  # orphaned reference removed
        assert "[^3]" not in text  # orphaned definition removed

        # Legacy .emf reference is still present pre-conversion.
        assert "media/legacy1.emf" in text

        # --- emf_convert.py: legacy media converted to .png ---
        _write_minimal_emf(media_dir / "legacy1.emf")
        if SOFFICE_AVAILABLE:
            rename_map = convert_legacy_media(media_dir)
            assert rename_map.get("legacy1.emf") == "legacy1.png"
            assert (media_dir / "legacy1.png").exists()
            for old_name, new_name in rename_map.items():
                text = text.replace(f"media/{old_name}", f"media/{new_name}")
            assert "media/legacy1.png" in text
            assert ".emf" not in text
        else:
            pytest.skip("soffice not found on PATH in this environment; skipping legacy media conversion step")

        # --- pandoc_validate.py: cleaned+converted document passes ---
        result = validate_cleaned_markdown(text, tmp_path)
        assert result["status"] == "PASS", result["errors"]
        assert result["errors"] == []
