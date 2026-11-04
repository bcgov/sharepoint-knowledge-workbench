"""Deterministic structure-quality assessment of an extracted document (no model calls).

Purpose: decide how much, if any, of the optional generative enrichment layer a document needs. Good source structure
(bookmarks, consistent headings, bounded sections) is preferred; AI is recommended only to fill structural gaps.

Key Input Dependencies: a `normalized-source-document` dict as returned by `pdf_extraction.extract_pdf_and_normalize`
(`markdown_text`, `headings`, `heading_source`, `page_count`, `page_map`, `warnings`, `defect_signals`).

Key Functions Index:
    - assess_structure()
    - decide_enrichment()
    - load_overrides()
"""

import json
import re
from pathlib import Path

ASSESSMENT_VERSION = "1"

# Thresholds are data, not code: callers may pass a modified copy and the values used are recorded in the result.
DEFAULT_THRESHOLDS = {
    "sufficient_score": 70,  # >= : deterministic structure is enough
    "weak_score": 40,  # <  : structure cannot be relied on
    "max_section_chars": 15000,  # a section longer than this is an unstructured gap
    "min_preamble_chars": 3000,  # untitled text before the first heading counts as a gap
    "target_pages_per_heading": 12,  # more pages than this per heading on average is sparse
}

MODES = ("off", "gaps", "full")
OVERRIDE_VALUES = ("auto",) + MODES

_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.M)
_NUMBERED = re.compile(r"^(\d+(\.\d+)*|[A-Z]\d*(\.\d+)*|[IVX]+)[.)]?\s+\S")
_RESOLVE_WARNING = "outline heading not found"


def _sections(markdown_text: str) -> list:
    """[(title, start, end)] for each ATX heading; text before the first heading is the preamble."""
    matches = list(_HEADING.finditer(markdown_text))
    return [
        (m.group(2), m.start(), matches[i + 1].start() if i + 1 < len(matches) else len(markdown_text))
        for i, m in enumerate(matches)
    ]


def _pages_for(page_map: list, start: int, end: int) -> list:
    """[first_page, last_page] whose extracted ranges overlap [start, end), or [] without a page map."""
    hit = [p["page"] for p in page_map if p["start"] < end and p["end"] > start]
    return [min(hit), max(hit)] if hit else []


def assess_structure(normalized: dict, thresholds: dict = None) -> dict:
    """Score how well the document's own structure supports progressive discovery.

    Returns {assessment_version, thresholds, signals, score, grade, recommendation, gap_regions, reasons}.
    grade: sufficient | partial | weak | none | not_assessable. recommendation: off | gaps | full | ocr_first.
    A gap region is {kind, title, start, end, pages}: the oversized sections and untitled preamble that the
    generative layer may subdivide while the sufficient parts keep their deterministic structure."""
    t = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    text = normalized.get("markdown_text", "")
    page_count = max(1, int(normalized.get("page_count") or 1))
    page_map = normalized.get("page_map") or []

    if normalized.get("defect_signals", {}).get("no_text_layer"):
        return _result(t, {}, 0, "not_assessable", "ocr_first", [], ["no text layer: OCR before assessing structure"])

    sections = _sections(text)
    headings = normalized.get("headings") or []
    source = normalized.get("heading_source", "none")
    if not sections or not headings:
        gap = {"kind": "whole_document", "title": "", "start": 0, "end": len(text), "pages": [1, page_count]}
        return _result(t, {"heading_source": source, "headings": 0}, 0, "none", "full", [gap], ["no headings"])

    reasons = []
    preamble = sections[0][1]
    sizes = [end - start for _, start, end in sections]
    outline_warnings = sum(1 for w in normalized.get("warnings", []) if _RESOLVE_WARNING in w)
    resolved = 1.0 if source != "outline" else max(0.0, 1 - outline_warnings / max(1, len(headings) + outline_warnings))
    numbered = sum(1 for title, _, _ in sections if _NUMBERED.match(title)) / len(sections)
    titles = [title.lower() for title, _, _ in sections]
    unique = len(set(titles)) / len(titles)
    levels = {h["level"] for h in headings}
    pages_per_heading = page_count / len(headings)
    oversized = [(title, s, e) for (title, s, e), size in zip(sections, sizes) if size > t["max_section_chars"]]
    oversized_share = sum(e - s for _, s, e in oversized) / max(1, len(text))
    gaps = [
        {"kind": "oversized_section", "title": title, "start": s, "end": e, "pages": _pages_for(page_map, s, e)}
        for title, s, e in oversized
    ]
    if preamble > t["min_preamble_chars"]:
        gaps.insert(0, {"kind": "untitled_preamble", "title": "", "start": 0, "end": preamble, "pages": _pages_for(page_map, 0, preamble)})

    signals = {
        "heading_source": source,
        "headings": len(headings),
        "levels_used": len(levels),
        "pages_per_heading": round(pages_per_heading, 2),
        "outline_resolved_ratio": round(resolved, 3),
        "numbered_ratio": round(numbered, 3),
        "unique_title_ratio": round(unique, 3),
        "oversized_sections": len(oversized),
        "oversized_text_share": round(oversized_share, 3),
        "untitled_preamble_chars": preamble,
    }

    # Weighted 0-100: source reliability and coverage dominate; numbering/depth are supporting evidence.
    score = {"outline": 30, "inferred": 15, "none": 0}.get(source, 0)
    score += 25 * (1 - min(1.0, oversized_share * 2))
    score += 15 * min(1.0, t["target_pages_per_heading"] / max(pages_per_heading, 1e-9))
    score += 10 * resolved + 8 * numbered + 7 * unique + 5 * min(1.0, len(levels) / 2)
    score = round(min(100, score))
    if source == "outline":
        reasons.append("PDF bookmarks present")
    if oversized:
        reasons.append(f"{len(oversized)} section(s) over {t['max_section_chars']} chars")
    if preamble > t["min_preamble_chars"]:
        reasons.append("large untitled preamble")
    if pages_per_heading > t["target_pages_per_heading"]:
        reasons.append("headings are sparse for the page count")

    if score >= t["sufficient_score"] and not gaps:
        grade, rec = "sufficient", "off"
    elif score >= t["weak_score"]:
        grade, rec = "partial", "gaps" if gaps else "off"
    else:
        grade, rec = "weak", "full"
    return _result(t, signals, score, grade, rec, gaps, reasons or ["structure is consistent"])


def _result(thresholds, signals, score, grade, recommendation, gaps, reasons) -> dict:
    return {
        "assessment_version": ASSESSMENT_VERSION,
        "thresholds": thresholds,
        "signals": signals,
        "score": score,
        "grade": grade,
        "recommendation": recommendation,
        "gap_regions": gaps,
        "reasons": reasons,
    }


def load_overrides(path: Path) -> dict:
    """Read `{"batch_default": "auto|off|gaps|full", "documents": {"<source path>": "auto|off|gaps|full"}}`.

    A missing file means no overrides. Unknown values raise ValueError rather than being ignored."""
    path = Path(path)
    if not path.is_file():
        return {"batch_default": "auto", "documents": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    overrides = {"batch_default": data.get("batch_default", "auto"), "documents": dict(data.get("documents", {}))}
    for value in [overrides["batch_default"], *overrides["documents"].values()]:
        if value not in OVERRIDE_VALUES:
            raise ValueError(f"unknown enrichment override {value!r}; expected one of {OVERRIDE_VALUES}")
    return overrides


def decide_enrichment(assessment: dict, source_path: str, overrides: dict = None) -> dict:
    """Mode for one document: per-document override, else batch default, else the assessment's recommendation.

    Returns {mode: off|gaps|full|ocr_first, decided_by: document_override|batch_override|assessment, recommendation,
    overridden: bool, regions}. `regions` lists the gap regions for `gaps`, the whole document for `full`, and is
    empty for `off`. Nothing here runs a model: the user still confirms cost before any generation."""
    overrides = overrides or {"batch_default": "auto", "documents": {}}
    recommended = assessment["recommendation"]
    chosen, decided_by = recommended, "assessment"
    batch = overrides.get("batch_default", "auto")
    doc = overrides.get("documents", {}).get(source_path, "auto")
    if batch != "auto":
        chosen, decided_by = batch, "batch_override"
    if doc != "auto":
        chosen, decided_by = doc, "document_override"
    if recommended == "ocr_first" and chosen != "off":
        chosen = "ocr_first"  # an override cannot enrich text that does not exist yet
    regions = []
    if chosen == "gaps":
        regions = assessment["gap_regions"]
    elif chosen == "full":
        regions = [{"kind": "whole_document", "title": "", "start": 0, "end": None, "pages": []}]
    return {
        "mode": chosen,
        "decided_by": decided_by,
        "recommendation": recommended,
        "overridden": chosen != recommended,
        "regions": regions,
    }
