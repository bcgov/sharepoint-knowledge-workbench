"""test_compare_rendered_output.py
=================================

Purpose:
    Tests for `compare_rendered_output` (Phase 6 Task 0.16's `compare-rendered-output` skill): the golden-master comparison pattern from Phase 2 Subphase 2.5.4 (byte-identical proof between a fresh render and a recorded baseline), packaged as a standalone, reusable primitive -- usable against either a Markdown or ASPX rendered-output tree.

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - pathlib
    - compare_rendered_output

Tests for `compare_rendered_output` (Phase 6 Task 0.16's
`compare-rendered-output` skill): the golden-master comparison pattern
from Phase 2 Subphase 2.5.4 (byte-identical proof between a fresh render
and a recorded baseline), packaged as a standalone, reusable primitive
-- usable against either a Markdown or ASPX rendered-output tree.

Key Functions Index:
    - _write_tree()
    - test_identical_trees_match()
    - test_missing_file_in_b_detected()
    - test_extra_file_in_b_detected()
    - test_content_mismatch_detected()
    - test_excluded_filenames_are_ignored()
    - test_default_exclusions_cover_generator_info_and_render_result()"""

from pathlib import Path

import compare_rendered_output as cro


# Write the supplied nested file tree for rendered-output comparison tests.
def _write_tree(root: Path, files: dict) -> None:
    """Write the supplied nested file tree for rendered-output comparison tests."""
    for rel_path, content in files.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


# Verify identical trees match.
def test_identical_trees_match(tmp_path):
    """Verify identical trees match."""
    a, b = tmp_path / "a", tmp_path / "b"
    files = {"index.md": "# Index\n", "pages/x.md": "content\n"}
    _write_tree(a, files)
    _write_tree(b, files)

    report = cro.compare_rendered_trees(a, b)
    assert report.status == "MATCH"
    assert report.issues == []


# Verify missing file in b detected.
def test_missing_file_in_b_detected(tmp_path):
    """Verify missing file in b detected."""
    a, b = tmp_path / "a", tmp_path / "b"
    _write_tree(a, {"index.md": "# Index\n", "pages/x.md": "content\n"})
    _write_tree(b, {"index.md": "# Index\n"})

    report = cro.compare_rendered_trees(a, b)
    assert report.status == "MISMATCH"
    assert any(i.code == "missing_in_b" for i in report.issues)


# Verify extra file in b detected.
def test_extra_file_in_b_detected(tmp_path):
    """Verify extra file in b detected."""
    a, b = tmp_path / "a", tmp_path / "b"
    _write_tree(a, {"index.md": "# Index\n"})
    _write_tree(b, {"index.md": "# Index\n", "pages/extra.md": "extra\n"})

    report = cro.compare_rendered_trees(a, b)
    assert report.status == "MISMATCH"
    assert any(i.code == "extra_in_b" for i in report.issues)


# Verify content mismatch detected.
def test_content_mismatch_detected(tmp_path):
    """Verify content mismatch detected."""
    a, b = tmp_path / "a", tmp_path / "b"
    _write_tree(a, {"index.md": "# Index\n"})
    _write_tree(b, {"index.md": "# Different\n"})

    report = cro.compare_rendered_trees(a, b)
    assert report.status == "MISMATCH"
    assert any(i.code == "content_mismatch" for i in report.issues)


# Verify excluded filenames are ignored.
def test_excluded_filenames_are_ignored(tmp_path):
    """Verify excluded filenames are ignored."""
    a, b = tmp_path / "a", tmp_path / "b"
    _write_tree(a, {"index.md": "# Index\n", "generator-info.json": '{"run_timestamp": "t1"}'})
    _write_tree(b, {"index.md": "# Index\n", "generator-info.json": '{"run_timestamp": "t2"}'})

    report = cro.compare_rendered_trees(a, b)
    assert report.status == "MATCH", report.issues


# Verify default exclusions cover generator info and render result.
def test_default_exclusions_cover_generator_info_and_render_result():
    """Verify default exclusions cover generator info and render result."""
    assert "generator-info.json" in cro.DEFAULT_EXCLUDED_FILENAMES
    assert "render-result.json" in cro.DEFAULT_EXCLUDED_FILENAMES
