"""
test_compare_rendered_output.py
=================================

Tests for `compare_rendered_output` (Phase 6 Task 0.16's
`compare-rendered-output` skill): the golden-master comparison pattern
from Phase 2 Subphase 2.5.4 (byte-identical proof between a fresh render
and a recorded baseline), packaged as a standalone, reusable primitive
-- usable against either a Markdown or ASPX rendered-output tree.
"""

from pathlib import Path

import compare_rendered_output as cro


def _write_tree(root: Path, files: dict) -> None:
    for rel_path, content in files.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def test_identical_trees_match(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    files = {"index.md": "# Index\n", "pages/x.md": "content\n"}
    _write_tree(a, files)
    _write_tree(b, files)

    report = cro.compare_rendered_trees(a, b)
    assert report.status == "MATCH"
    assert report.issues == []


def test_missing_file_in_b_detected(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    _write_tree(a, {"index.md": "# Index\n", "pages/x.md": "content\n"})
    _write_tree(b, {"index.md": "# Index\n"})

    report = cro.compare_rendered_trees(a, b)
    assert report.status == "MISMATCH"
    assert any(i.code == "missing_in_b" for i in report.issues)


def test_extra_file_in_b_detected(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    _write_tree(a, {"index.md": "# Index\n"})
    _write_tree(b, {"index.md": "# Index\n", "pages/extra.md": "extra\n"})

    report = cro.compare_rendered_trees(a, b)
    assert report.status == "MISMATCH"
    assert any(i.code == "extra_in_b" for i in report.issues)


def test_content_mismatch_detected(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    _write_tree(a, {"index.md": "# Index\n"})
    _write_tree(b, {"index.md": "# Different\n"})

    report = cro.compare_rendered_trees(a, b)
    assert report.status == "MISMATCH"
    assert any(i.code == "content_mismatch" for i in report.issues)


def test_excluded_filenames_are_ignored(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    _write_tree(a, {"index.md": "# Index\n", "generator-info.json": '{"run_timestamp": "t1"}'})
    _write_tree(b, {"index.md": "# Index\n", "generator-info.json": '{"run_timestamp": "t2"}'})

    report = cro.compare_rendered_trees(a, b)
    assert report.status == "MATCH", report.issues


def test_default_exclusions_cover_generator_info_and_render_result():
    assert "generator-info.json" in cro.DEFAULT_EXCLUDED_FILENAMES
    assert "render-result.json" in cro.DEFAULT_EXCLUDED_FILENAMES
