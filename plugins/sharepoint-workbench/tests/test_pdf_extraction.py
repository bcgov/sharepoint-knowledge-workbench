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


def test_table_is_markdown_and_continues_across_pages(tmp_path):
    pdf = tmp_path / "table.pdf"
    doc = fitz.open()
    for rows in (
        [["Sentence", "Code"], ["Absolute", "AD"], ["Conditional", "CND"]],
        [["Sentence", "Code"], ["Custody", "CC"]],
    ):
        page = doc.new_page()
        top, row_h, col_w = 100, 30, 150
        for r, row in enumerate(rows):
            for c, text in enumerate(row):
                rect = fitz.Rect(72 + c * col_w, top + r * row_h, 72 + (c + 1) * col_w, top + (r + 1) * row_h)
                page.draw_rect(rect)
                page.insert_text((rect.x0 + 4, rect.y0 + 20), text, fontsize=11)
    doc.save(pdf)
    doc.close()
    result = pdf_extraction.extract_pdf_and_normalize(pdf, tmp_path / "out")
    md = result["markdown_text"]
    assert "| Sentence | Code |" in md and "| --- | --- |" in md
    assert md.count("| Sentence | Code |") == 1  # repeated header row dropped
    assert "| Custody | CC |" in md and "| Absolute | AD |" in md
    assert result["statistics"]["table_count"] == 1


def test_rotated_page_keeps_table_text_out_of_body(tmp_path):
    pdf = tmp_path / "rotated.pdf"
    doc = fitz.open()
    page = doc.new_page()
    for r, row in enumerate([["Name", "Code"], ["Alpha", "A1"]]):
        for c, text in enumerate(row):
            rect = fitz.Rect(72 + c * 150, 100 + r * 30, 72 + (c + 1) * 150, 130 + r * 30)
            page.draw_rect(rect)
            page.insert_text((rect.x0 + 4, rect.y0 + 20), text, fontsize=11)
    page.set_rotation(90)
    doc.save(pdf)
    doc.close()
    md = pdf_extraction.extract_pdf_and_normalize(pdf, tmp_path / "out")["markdown_text"]
    assert md.count("Alpha") == 1 and "| --- | --- |" in md  # one copy, inside the table (not duplicated as body text)


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
