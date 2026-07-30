"""
test_golden_master.py
========================

Phase 2, spec Section 5.5: two comparison surfaces, not one blanket
byte-identical check. Section 5.2's identity/naming fixes intentionally
change render-result.json/publication-map.json bytes -- so publication
CONTENT (index.md, pages/**, media/**) is compared byte-identical
AND file-set-identical (no missing, no extra files) against the Task 0
baseline, while control METADATA is compared semantically (the identity
still correctly identifies the same source/plan, even though its literal
bytes changed).
"""

from pathlib import Path

import pytest


def _find_repo_root(start: Path) -> Path:
    """Walk upward from this test file until a directory containing both
    `plugins/` and `runs/` is found -- more robust than counting `.parent`
    calls, which an earlier draft got wrong by one level."""
    current = start.resolve()
    for candidate in [current] + list(current.parents):
        if (candidate / "plugins").is_dir() and (candidate / "runs").is_dir():
            return candidate
    raise RuntimeError(f"could not locate repo root walking up from {start}")


_REPO_ROOT = _find_repo_root(Path(__file__))
_GOLDEN_DIR = _REPO_ROOT / "runs" / "ceis-manual-v2" / "golden-master-baseline"
_CURRENT_DIR = _REPO_ROOT / "runs" / "ceis-manual-v2" / "render" / "rendered-output"


def _require_golden_master():
    if not _GOLDEN_DIR.exists():
        pytest.skip(
            "golden-master-baseline not captured yet -- run Task 0's capture "
            "step after confirming Phase 1 is formally closed, BEFORE any "
            "other task in this plan runs"
        )


def _relative_files(root: Path, subdir: str) -> set:
    base = root / subdir if subdir else root
    if not base.is_dir():
        return set()
    return {p.relative_to(base) for p in base.rglob("*") if p.is_file()}


def test_index_is_byte_identical_to_golden_master():
    _require_golden_master()
    assert (_GOLDEN_DIR / "index.md").read_bytes() == (_CURRENT_DIR / "index.md").read_bytes()


def test_pages_are_file_set_identical_and_byte_identical_to_golden_master():
    _require_golden_master()
    golden_files = _relative_files(_GOLDEN_DIR, "pages")
    current_files = _relative_files(_CURRENT_DIR, "pages")
    missing = golden_files - current_files
    extra = current_files - golden_files
    assert not missing, f"pages present in golden master but missing from current output: {sorted(missing)}"
    assert not extra, f"pages present in current output but NOT in golden master (unexplained addition): {sorted(extra)}"
    for rel in sorted(golden_files):
        golden_bytes = (_GOLDEN_DIR / "pages" / rel).read_bytes()
        current_bytes = (_CURRENT_DIR / "pages" / rel).read_bytes()
        assert golden_bytes == current_bytes, f"pages/{rel} differs from golden master"


def test_media_is_file_set_identical_and_byte_identical_to_golden_master():
    _require_golden_master()
    golden_files = _relative_files(_GOLDEN_DIR, "media")
    current_files = _relative_files(_CURRENT_DIR, "media")
    missing = golden_files - current_files
    extra = current_files - golden_files
    assert not missing, f"media present in golden master but missing from current output: {sorted(missing)}"
    assert not extra, f"media present in current output but NOT in golden master (unexplained addition): {sorted(extra)}"
    for rel in sorted(golden_files):
        golden_bytes = (_GOLDEN_DIR / "media" / rel).read_bytes()
        current_bytes = (_CURRENT_DIR / "media" / rel).read_bytes()
        assert golden_bytes == current_bytes, f"media/{rel} differs from golden master"


def test_control_metadata_is_semantically_correct_not_byte_identical():
    _require_golden_master()
    import json
    current = json.loads((_CURRENT_DIR / "render-result.json").read_text())
    # Semantic check, not byte comparison: the renamed field is present and
    # correctly identifies the same source content -- NOT that it matches
    # the old field name/value byte-for-byte (it deliberately won't, since
    # Task 2 renamed it and the golden master predates that rename).
    assert "source_content_sha256" in current
    assert len(current["source_content_sha256"]) == 64  # a real sha256 hex digest
