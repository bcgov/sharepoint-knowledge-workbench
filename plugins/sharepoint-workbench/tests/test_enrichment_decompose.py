"""Tests for agent-mediated decomposition: consent gate, requests, response validation, topic files, staleness.

Purpose: check invariants (consent, boundaries, verbatim slices, provenance, retries, partial completion, reproducible
manifests). No model is called and generated titles are never compared.

Key Input Dependencies: scripts/enrichment/decompose.py, provenance.py.
"""
import json
import sys
from pathlib import Path

import pytest

_plugin_dir = Path(__file__).resolve().parents[1]
_skills_dir = _plugin_dir / ".apm" / "skills" if (_plugin_dir / ".apm" / "skills").exists() else _plugin_dir / "skills"
sys.path.insert(0, str(_skills_dir / "converting-sharepoint-documents" / "scripts" / "enrichment"))

import decompose as dc  # noqa: E402
import provenance  # noqa: E402

TABLE = "| a | b |\n| --- | --- |\n| 1 | 2 |\n| 3 | 4 |"
TEXT = ("Intro paragraph one.\n\nIntro paragraph two.\n\n" + TABLE + "\n\nAfter the table.\n\n"
        "Second part starts here.\n\nMore of the second part.\n")
PAGE_MAP = [{"page": 1, "start": 0, "end": 60}, {"page": 2, "start": 60, "end": len(TEXT)}]


def _setup(tmp_path, text=TEXT, window=24000, approved=True):
    nav = tmp_path / "ai-navigation"
    if approved:
        dc.record_consent(nav, approved=True, provider="host-agent", scope="document", estimated_tokens=10)
    regions = [{"kind": "whole_document", "start": 0, "end": None}]
    return nav, regions, window


def _respond(request, titles=("Part A", "Part B"), uncertain=False):
    starts = request["allowed_starts"]
    picks = [starts[0], starts[-1]] if len(starts) > 1 else [starts[0]]
    return {"topics": [{"start": s, "title": t, "uncertain": uncertain} for s, t in zip(picks, titles)]}


def test_no_request_is_written_without_consent(tmp_path):
    nav, regions, _ = _setup(tmp_path, approved=False)
    with pytest.raises(PermissionError):
        dc.build_requests(nav, TEXT, PAGE_MAP, regions, source_document="m.pdf")
    assert not (nav / "requests").exists()
    dc.record_consent(nav, approved=False, provider="x", scope="document")
    with pytest.raises(PermissionError):
        dc.require_consent(nav)


def test_block_edges_never_split_a_table():
    edges = dc.block_edges(TEXT)
    table_start, table_end = TEXT.index("| a |"), TEXT.index("| 3 | 4 |")
    assert not any(table_start < e <= table_end for e in edges)
    assert TEXT.index("After the table.") in edges


def test_large_documents_are_windowed_at_block_edges(tmp_path):
    big = "\n\n".join(f"Paragraph {i} " + "word " * 40 for i in range(200)) + "\n"
    nav, regions, _ = _setup(tmp_path)
    requests = dc.build_requests(nav, big, [], regions, source_document="m.pdf", max_window_chars=3000)
    assert len(requests) > 3
    edges = set(dc.block_edges(big))
    assert all(r["window"][0] in edges for r in requests)
    assert requests[0]["window"][0] == 0 and requests[-1]["window"][1] == len(big)
    assert all(a["window"][1] == b["window"][0] for a, b in zip(requests, requests[1:]))
    assert dc.estimate_cost(requests)["windows"] == len(requests)


def test_response_validation_rejects_malformed_and_off_edge_boundaries(tmp_path):
    nav, regions, _ = _setup(tmp_path)
    request = dc.build_requests(nav, TEXT, PAGE_MAP, regions, source_document="m.pdf")[0]
    assert dc.validate_response(request, "not json")
    assert dc.validate_response(request, {"topics": []})
    mid_table = {"topics": [{"start": 0, "title": "A"}, {"start": TEXT.index("| 3 |"), "title": "B"}]}
    assert any("allowed block edge" in p for p in dc.validate_response(request, mid_table))
    assert dc.validate_response(request, {"topics": [{"start": 5, "title": "A"}]})
    assert dc.validate_response(request, {"topics": [{"start": 0, "title": " "}]})
    assert dc.validate_response(request, _respond(request)) == []


def test_retries_then_failure_and_partial_completion(tmp_path):
    big = "\n\n".join(f"Paragraph {i} " + "word " * 40 for i in range(60)) + "\n"
    nav, regions, _ = _setup(tmp_path)
    requests = dc.build_requests(nav, big, [], regions, source_document="m.pdf", max_window_chars=3000)
    good, bad = requests[0], requests[1]
    assert dc.apply_response(nav, good, _respond(good), model="m") == []
    for attempt in range(dc.MAX_ATTEMPTS):
        assert dc.pending_windows(nav).count(bad["id"]) == 1
        assert dc.apply_response(nav, bad, {"oops": 1}, model="m")
    gen = json.loads((nav / dc.GENERATION_FILE).read_text())
    assert gen["windows"][bad["id"]]["status"] == "failed" and gen["windows"][bad["id"]]["attempts"] == 3
    assert bad["id"] not in dc.pending_windows(nav) and good["id"] not in dc.pending_windows(nav)
    entries = dc.write_topics(nav, big, [], source_document="m.pdf", extracted_content="raw/extracted.md",
                              source_sha256="s1")
    assert entries and all(e["end"] <= requests[0]["window"][1] for e in entries)


def test_topics_are_verbatim_flagged_and_separate_from_extraction(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "extracted.md").write_text(TEXT, encoding="utf-8")
    nav, regions, _ = _setup(tmp_path)
    nav = tmp_path / "ai-navigation"
    request = dc.build_requests(nav, TEXT, PAGE_MAP, regions, source_document="m.pdf")[0]
    dc.apply_response(nav, request, _respond(request, uncertain=True), model="any-model")
    entries = dc.write_topics(nav, TEXT, PAGE_MAP, source_document="m.pdf", extracted_content="raw/extracted.md",
                              source_sha256="s1")
    assert (raw / "extracted.md").read_text(encoding="utf-8") == TEXT
    assert all(nav in (tmp_path / e["file"]).parents or (nav / e["file"]).is_file() for e in entries)
    joined = "".join(TEXT[e["start"]:e["end"]] for e in entries)
    assert joined == TEXT
    assert entries[0]["source_pages"][0] == 1 and entries[-1]["source_pages"][-1] == 2
    assert dc.validate_topics(nav, TEXT, 2, raw_dir=raw) == []
    meta, body = provenance.parse_front_matter((nav / entries[0]["file"]).read_text(encoding="utf-8"))
    assert meta["authoritative"] is False and meta["uncertain_boundary"] is True
    assert "AI-GENERATED NAVIGATION AID" in body


def test_tampered_topic_missing_notice_and_stale_source_are_caught(tmp_path):
    nav, regions, _ = _setup(tmp_path)
    request = dc.build_requests(nav, TEXT, PAGE_MAP, regions, source_document="m.pdf")[0]
    dc.apply_response(nav, request, _respond(request), model="m")
    entries = dc.write_topics(nav, TEXT, PAGE_MAP, source_document="m.pdf", extracted_content="e.md",
                              source_sha256="s1")
    topic = nav / entries[0]["file"]
    topic.write_text(topic.read_text(encoding="utf-8").replace("Intro paragraph one.", "Rewritten."), encoding="utf-8")
    assert "not_verbatim" in {p["code"] for p in dc.validate_topics(nav, TEXT, 2)}
    topic.write_text(topic.read_text(encoding="utf-8").replace(provenance.AI_NOTICE_TITLE, "x"), encoding="utf-8")
    assert "missing_notice" in {p["code"] for p in dc.validate_topics(nav, TEXT, 2)}
    assert dc.is_generation_stale(nav, TEXT, "s1") is False
    assert dc.is_generation_stale(nav, TEXT, "s2") is True
    assert dc.is_generation_stale(nav, TEXT + "changed", "s1") is True


def test_manifest_offsets_are_reproducible_when_wording_varies(tmp_path):
    results = []
    for titles in (("Part A", "Part B"), ("Opening material", "Closing material")):
        nav, regions, _ = _setup(tmp_path / titles[0].replace(" ", "_"))
        request = dc.build_requests(nav, TEXT, PAGE_MAP, regions, source_document="m.pdf")[0]
        dc.apply_response(nav, request, _respond(request, titles), model="m")
        entries = dc.write_topics(nav, TEXT, PAGE_MAP, source_document="m.pdf", extracted_content="e.md",
                                  source_sha256="s1")
        results.append([(e["start"], e["end"], e["source_pages"]) for e in entries])
    assert results[0] == results[1]


def test_poorly_structured_text_without_headings_still_decomposes(tmp_path):
    plain = "\n\n".join(f"Plain paragraph {i} with no headings at all." for i in range(30)) + "\n"
    nav, regions, _ = _setup(tmp_path)
    request = dc.build_requests(nav, plain, [], regions, source_document="m.pdf")[0]
    assert len(request["allowed_starts"]) == 30
    assert dc.apply_response(nav, request, _respond(request), model="m") == []
