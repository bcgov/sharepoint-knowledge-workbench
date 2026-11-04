"""Tests for the page context header in multipage_markdown.py (no network or tenant access).

Purpose: verify rendered topic pages name their document and section, and that every mode round-trips.

Key Input Dependencies: scripts/rendering/renderers/multipage_markdown.py.
"""
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_plugin_dir = Path(__file__).resolve().parents[1]
_skills_dir = _plugin_dir / ".apm" / "skills" if (_plugin_dir / ".apm" / "skills").exists() else _plugin_dir / "skills"
_RENDERING = _skills_dir / "converting-sharepoint-documents" / "scripts" / "rendering"
sys.path.insert(0, str(_RENDERING))
sys.path.insert(0, str(_RENDERING.parent / "assembly"))
from renderers import multipage_markdown as mpm  # noqa: E402


def _package(path="source-documents/Crown_Counsel_Manual.pdf"):
    meta = SimpleNamespace(chunk_id="c1", topic="Bail", source_heading_path=["Part 2", 'Bail "Orders"'])
    chunk = SimpleNamespace(metadata=meta, content="Body text.\n")
    return SimpleNamespace(manifest=SimpleNamespace(source=SimpleNamespace(path=path))), chunk


def test_breadcrumb_names_document_and_section():
    pkg, chunk = _package()
    text = mpm.expected_page_content(pkg, chunk, {"c1"}, "breadcrumb")
    assert text.startswith('> Document: Crown Counsel Manual | Section: Part 2 > Bail "Orders"\n\n')
    assert text.endswith("Body text.\n")


def test_front_matter_escapes_quotes():
    pkg, chunk = _package()
    text = mpm.expected_page_content(pkg, chunk, {"c1"}, "front-matter")
    assert text.startswith("---\n") and '  - "Bail \\"Orders\\""' in text


def test_none_is_bare_content_and_bad_mode_rejected():
    pkg, chunk = _package()
    assert mpm.expected_page_content(pkg, chunk, {"c1"}, "none") == "Body text.\n"
    with pytest.raises(ValueError):
        mpm.MultipageMarkdownRenderer(context_mode="bogus")


def test_falls_back_to_topic_without_heading_path():
    pkg, chunk = _package()
    chunk.metadata.source_heading_path = []
    assert "Section: Bail" in mpm.expected_page_content(pkg, chunk, {"c1"}, "breadcrumb")
