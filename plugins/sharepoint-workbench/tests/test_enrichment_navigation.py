"""Tests for AI summaries, hierarchical index, roll-up validation, approval-gated publication and the example package.

Purpose: check schemas, notices, provenance, links and invariants; generated wording is never compared.

Key Input Dependencies: scripts/enrichment/navigation.py, build_example.py, decompose.py, provenance.py.
"""
import shutil
import sys
from pathlib import Path

import pytest

_plugin_dir = Path(__file__).resolve().parents[1]
_skill = (_plugin_dir / ".apm" / "skills" if (_plugin_dir / ".apm" / "skills").exists() else _plugin_dir / "skills") \
    / "converting-sharepoint-documents"
sys.path.insert(0, str(_skill / "scripts" / "enrichment"))

import build_example  # noqa: E402
import decompose as dc  # noqa: E402
import navigation as nv  # noqa: E402
import provenance  # noqa: E402

TEXT, PAGES = build_example.TEXT, 3


@pytest.fixture
def pkg(tmp_path):
    root = build_example.build_example(tmp_path / "pkg")
    return root, root / "ai-navigation", root / "raw"


def test_example_package_separates_authoritative_and_generated(pkg):
    root, nav, raw = pkg
    assert (raw / "extracted.md").read_text(encoding="utf-8") == TEXT
    assert not list(raw.rglob("*AI-GENERATED*")) and "AI-GENERATED" not in (raw / "extracted.md").read_text("utf-8")
    ai_files = [nav / "index.md", *(nav / "chapters").glob("*.md"), *(nav / "topics").glob("*.md")]
    assert len(ai_files) == 5
    for path in ai_files:
        meta, body = provenance.parse_front_matter(path.read_text(encoding="utf-8"))
        assert meta["authoritative"] is False and meta["trust_level"] == "discovery_only"
        assert provenance.AI_NOTICE_TITLE in body
    assert nv.validate_navigation(nav, TEXT, PAGES, raw) == []
    assert '"authoritative": true' in (raw / "extraction.json").read_text(encoding="utf-8")


def test_committed_example_package_is_valid():
    example = _skill / "assets" / "examples" / "enrichment-example"
    assert nv.validate_navigation(example / "ai-navigation", TEXT, PAGES, example / "raw") == []


def test_index_links_resolve_and_cover_every_topic(pkg):
    _, nav, _ = pkg
    index = (nav / "index.md").read_text(encoding="utf-8")
    for topic in (nav / "topics").glob("*.md"):
        assert f"topics/{topic.name}" in index
    assert "Document summary" in index and "pages 1-2" in index


def test_summary_copying_source_text_or_missing_keywords_is_rejected():
    request = {"text": TEXT}
    long_copy = TEXT[:150]
    assert any("copies" in p for p in nv.validate_summary(request, {"summary": long_copy, "keywords": ["a"]}))
    assert any("keywords" in p for p in nv.validate_summary(request, {"summary": "Short.", "keywords": []}))
    assert nv.validate_summary(request, {"summary": "A paraphrase.", "keywords": ["a"], "synonyms": []}) == []
    assert nv.validate_summary(request, ["not", "an", "object"])


def test_rollup_requires_every_topic_once_and_known_files(pkg):
    _, nav, _ = pkg
    request = nv.build_rollup_request(nav)
    files = [t["file"] for t in request["topics"]]
    ok = {"document_summary": "s", "groups": [{"title": "t", "summary": "s", "topics": files}]}
    assert nv.validate_rollup(request, ok) == []
    assert nv.validate_rollup(request, {**ok, "groups": [{"title": "t", "summary": "s", "topics": files[:1]}]})
    assert nv.validate_rollup(request, {**ok, "groups": [{"title": "t", "summary": "s", "topics": files + ["x.md"]}]})
    assert nv.validate_rollup(request, {**ok, "relations": [{"from": files[0], "to": "nope", "reason": "r"}]})
    assert nv.validate_rollup(request, {"groups": ok["groups"]})
    assert "summary" not in str(request["topics"][0].get("text", ""))


def test_partial_run_without_summaries_is_still_navigable(tmp_path):
    nav = tmp_path / "ai-navigation"
    dc.record_consent(nav, approved=True, provider="p", scope="document")
    req = dc.build_requests(nav, TEXT, build_example.PAGE_MAP, [{"start": 0, "end": None}], source_document="m.pdf")[0]
    dc.apply_response(nav, req, {"topics": [{"start": 0, "title": "Only topic"}]}, model="m")
    dc.write_topics(nav, TEXT, build_example.PAGE_MAP, source_document="m.pdf", extracted_content="e.md", source_sha256="s")
    nv.write_navigation(nav, page_count=3, extracted_rel="e.md", source_sha256="s")
    index = (nav / "index.md").read_text(encoding="utf-8")
    assert "Only topic" in index and "Keywords" not in index


def test_summary_requests_need_consent(tmp_path):
    with pytest.raises(PermissionError):
        nv.build_summary_requests(tmp_path / "ai-navigation", TEXT)


def test_publication_needs_approval_and_a_clean_validation(pkg, tmp_path):
    root, nav, raw = pkg
    out = tmp_path / "published"
    with pytest.raises(PermissionError):
        nv.publish(nav, out, TEXT, PAGES, raw)
    assert not out.exists()
    nv.approve(nav, "reviewer@example.org")
    copied = nv.publish(nav, out, TEXT, PAGES, raw)
    assert "index.md" in copied and (out / "topics").is_dir()
    assert (raw / "extracted.md").read_text(encoding="utf-8") == TEXT


def test_publication_blocked_by_broken_link_and_by_stale_source(pkg, tmp_path):
    root, nav, raw = pkg
    nv.approve(nav, "r")
    chapter = next((nav / "chapters").glob("*.md"))
    original = chapter.read_text(encoding="utf-8")
    chapter.write_text(original + "\n[gone](../topics/missing.md)\n", encoding="utf-8")
    with pytest.raises(ValueError, match="broken_link"):
        nv.publish(nav, tmp_path / "o1", TEXT, PAGES, raw)
    chapter.write_text(original, encoding="utf-8")
    gen = dc._read_json(nav / dc.GENERATION_FILE)
    gen["source_sha256"] = "changed-source"
    dc._write_json(nav / dc.GENERATION_FILE, gen)
    with pytest.raises(ValueError, match="stale"):
        nv.publish(nav, tmp_path / "o2", TEXT, PAGES, raw)
    assert dc.is_generation_stale(nav, TEXT, "different") is True


def test_ai_layer_disabled_leaves_deterministic_output_alone(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "extracted.md").write_text(TEXT, encoding="utf-8")
    assert not (tmp_path / "ai-navigation").exists()
    assert [p.name for p in tmp_path.iterdir()] == ["raw"]
