"""Tests for pdf_extraction.py (real PyMuPDF-generated PDFs; no network or tenant access).

Purpose: verify PDF extraction yields a valid normalized-source-document with headings, page numbers and images.

Key Input Dependencies: scripts/extraction/pdf_extraction.py, PyMuPDF.
"""
import sys
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")

_plugin_dir = Path(__file__).resolve().parents[1]
_skills_dir = _plugin_dir / ".apm" / "skills" if (_plugin_dir / ".apm" / "skills").exists() else _plugin_dir / "skills"
_EXTRACTION = _skills_dir / "converting-sharepoint-documents" / "scripts" / "extraction"
sys.path.insert(0, str(_EXTRACTION))
import pdf_extraction  # noqa: E402


def _make_pdf(path, pages, toc=None):
    doc = fitz.open()
    for lines in pages:
        page = doc.new_page()
        y = 72
        for text, size in lines:
            page.insert_text((72, y), text, fontsize=size)
            y += size * 2
    if toc:
        doc.set_toc(toc)
    doc.save(path)
    doc.close()


def test_outline_headings_and_pages(tmp_path):
    pdf = tmp_path / "manual.pdf"
    _make_pdf(
        pdf,
        [
            [("Overview", 18), ("Intro text here.", 11)],
            [("Details", 18), ("More text here.", 11)],
        ],
        toc=[[1, "Overview", 1], [1, "Details", 2]],
    )
    result = pdf_extraction.extract_pdf_and_normalize(pdf, tmp_path / "out")
    assert result["heading_source"] == "outline"
    assert [h["text"] for h in result["headings"]] == ["Overview", "Details"]
    assert result["heading_pages"] == [1, 2]
    assert result["page_count"] == 2
    assert "Intro text here." in result["markdown_text"]
    assert (tmp_path / "out" / "raw" / "extracted.md").exists()


def test_no_text_layer_is_flagged(tmp_path):
    pdf = tmp_path / "scan.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(pdf)
    doc.close()
    result = pdf_extraction.extract_pdf_and_normalize(pdf, tmp_path / "out")
    assert result["defect_signals"]["no_text_layer"] is True
    assert result["heading_source"] == "none"


def test_missing_source_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        pdf_extraction.extract_pdf_and_normalize(tmp_path / "nope.pdf", tmp_path / "out")
