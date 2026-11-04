"""Tests for the enrichment foundations: page map, structure assessment, overrides, trust metadata, provenance.

Purpose: verify deterministic behaviour and trust invariants; no model is called and no generated wording is compared.

Key Input Dependencies: scripts/extraction/pdf_extraction.py, scripts/enrichment/*, PyMuPDF.
"""
import json
import sys
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")

_plugin_dir = Path(__file__).resolve().parents[1]
_skills_dir = _plugin_dir / ".apm" / "skills" if (_plugin_dir / ".apm" / "skills").exists() else _plugin_dir / "skills"
_SCRIPTS = _skills_dir / "converting-sharepoint-documents" / "scripts"
for sub in ("enrichment", "extraction"):
    sys.path.insert(0, str(_SCRIPTS / sub))
sys.path.insert(0, str(_SCRIPTS))

import pdf_extraction  # noqa: E402
import provenance  # noqa: E402
import structure_quality as sq  # noqa: E402


def _pdf(path, pages, toc=None):
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


def _synthetic(headings, section_chars, page_count=10, source="outline", no_text=False):
    text = ""
    for i in range(headings):
        text += f"## {i + 1}. Part {i}\n\n" + ("word " * (section_chars // 5)) + "\n\n"
    return {
        "markdown_text": text,
        "headings": [{"level": 2, "text": f"{i + 1}. Part {i}"} for i in range(headings)],
        "heading_source": source,
        "page_count": page_count,
        "page_map": [{"page": 1, "start": 0, "end": len(text)}],
        "warnings": [],
        "defect_signals": {"no_text_layer": no_text},
    }


def test_page_map_covers_extracted_text_by_page(tmp_path):
    pdf = tmp_path / "m.pdf"
    _pdf(pdf, [[("Alpha", 18), ("First page text.", 11)], [("Beta", 18), ("Second page text.", 11)]],
         toc=[[1, "Alpha", 1], [1, "Beta", 2]])
    result = pdf_extraction.extract_pdf_and_normalize(pdf, tmp_path / "out")
    text, pages = result["markdown_text"], result["page_map"]
    assert [p["page"] for p in pages] == [1, 2]
    assert pages[0]["start"] == 0 and pages[0]["end"] <= pages[1]["start"] < pages[1]["end"] <= len(text)
    assert "First page text." in text[pages[0]["start"]:pages[0]["end"]]
    assert "Second page text." in text[pages[1]["start"]:pages[1]["end"]]
    assert json.loads((tmp_path / "out" / "raw" / "page_map.json").read_text())["pages"] == pages


def test_well_structured_document_needs_no_enrichment():
    result = sq.assess_structure(_synthetic(headings=8, section_chars=2000))
    assert result["grade"] == "sufficient" and result["recommendation"] == "off"
    assert result["gap_regions"] == []


def test_partial_structure_recommends_gaps_only_for_oversized_sections():
    doc = _synthetic(headings=6, section_chars=2000)
    doc["markdown_text"] += "## 7. Huge\n\n" + "word " * 8000
    doc["headings"].append({"level": 2, "text": "7. Huge"})
    doc["page_map"] = [{"page": 1, "start": 0, "end": len(doc["markdown_text"])}]
    result = sq.assess_structure(doc)
    assert result["recommendation"] == "gaps"
    assert [g["title"] for g in result["gap_regions"]] == ["7. Huge"]
    assert result["gap_regions"][0]["pages"] == [1, 1]


def test_no_headings_recommends_full_and_scans_need_ocr_first():
    doc = _synthetic(headings=0, section_chars=0, source="none")
    doc["markdown_text"] = "plain text " * 400
    assert sq.assess_structure(doc)["recommendation"] == "full"
    scan = _synthetic(headings=0, section_chars=0, source="none", no_text=True)
    assert sq.assess_structure(scan)["recommendation"] == "ocr_first"


def test_assessment_is_deterministic():
    doc = _synthetic(headings=5, section_chars=3000)
    assert sq.assess_structure(doc) == sq.assess_structure(doc)


def test_override_precedence_and_ocr_guard(tmp_path):
    good = sq.assess_structure(_synthetic(headings=8, section_chars=2000))
    assert sq.decide_enrichment(good, "a.pdf")["mode"] == "off"
    batch = {"batch_default": "gaps", "documents": {"a.pdf": "full"}}
    assert sq.decide_enrichment(good, "a.pdf", batch)["decided_by"] == "document_override"
    assert sq.decide_enrichment(good, "b.pdf", batch)["decided_by"] == "batch_override"
    forced = sq.decide_enrichment(good, "a.pdf", batch)
    assert forced["mode"] == "full" and forced["overridden"] is True
    scan = sq.assess_structure(_synthetic(headings=0, section_chars=0, source="none", no_text=True))
    assert sq.decide_enrichment(scan, "s.pdf", {"batch_default": "full", "documents": {}})["mode"] == "ocr_first"
    path = tmp_path / "o.json"
    path.write_text(json.dumps({"batch_default": "sometimes"}))
    with pytest.raises(ValueError):
        sq.load_overrides(path)
    assert sq.load_overrides(tmp_path / "missing.json")["batch_default"] == "auto"


def _ai_file(tmp_path, **changes):
    meta = provenance.ai_metadata(
        source_document="m.pdf", extracted_content="extracted/m.md", source_sha256="abc", model="any-model",
        prompt_version="v1", timestamp="2026-11-04T10:00:00-07:00", source_pages=[1, 2], uncertain=True)
    meta.update(changes)
    path = tmp_path / "summary.md"
    path.write_text(provenance.ai_artifact_header(meta) + "Some generated wording.\n", encoding="utf-8")
    return path


def test_valid_ai_artifact_passes_and_carries_notice_and_trust_flags(tmp_path):
    path = _ai_file(tmp_path)
    assert provenance.validate_ai_artifact(path, "x", page_count=5, current_source_sha256="abc") == []
    meta, body = provenance.parse_front_matter(path.read_text(encoding="utf-8"))
    assert (meta["content_type"], meta["trust_level"], meta["authoritative"]) == (
        "ai_generated_navigation", "discovery_only", False)
    assert meta["source_pages"] == [1, 2] and "AI-GENERATED NAVIGATION AID" in body
    assert "marked uncertain" in body


def test_missing_notice_wrong_trust_and_bad_pages_are_rejected(tmp_path):
    path = _ai_file(tmp_path, authoritative=True, source_pages=[4, 9])
    path.write_text(path.read_text(encoding="utf-8").replace("AI-GENERATED NAVIGATION AID", "Summary"), encoding="utf-8")
    codes = {p["code"] for p in provenance.validate_ai_artifact(path, "x", page_count=5)}
    assert {"wrong_trust", "missing_notice", "bad_source_pages"} <= codes
    bare = tmp_path / "bare.md"
    bare.write_text("# no metadata\n", encoding="utf-8")
    assert provenance.validate_ai_artifact(bare, "x", 5)[0]["code"] == "missing_metadata"


def test_broken_link_and_stale_source_are_reported(tmp_path):
    path = _ai_file(tmp_path)
    path.write_text(path.read_text(encoding="utf-8") + "See [topic](topics/gone.md).\n", encoding="utf-8")
    codes = {p["code"] for p in provenance.validate_ai_artifact(path, "x", 5, current_source_sha256="changed")}
    assert codes == {"broken_link", "stale"}
    assert provenance.is_stale({"source_sha256": "abc"}, "def") and not provenance.is_stale({"source_sha256": "abc"}, "abc")


def test_topic_slices_must_be_verbatim_extracted_text():
    extracted = "Alpha text.\n\nBeta text.\n"
    assert provenance.is_verbatim_slice("Beta text.\n", extracted, 13, 24)
    assert not provenance.is_verbatim_slice("Beta rewritten.\n", extracted, 13, 24)
    assert not provenance.is_verbatim_slice("x", extracted, 5, 99)


def test_deterministic_metadata_is_authoritative():
    meta = provenance.deterministic_metadata("m.pdf", "abc")
    assert meta["authoritative"] is True and meta["trust_level"] == "authoritative_extraction"
