"""
test_validate_canonical_mutations.py
======================================

Layer-1 mutation suite (Phase 2, spec Section 5.1): takes a known-good
canonical package, deliberately corrupts it one way at a time, and asserts
validate_canonical_package's status/issue-code for each -- proving the
validator actually catches each corruption, not just "doesn't currently
fail by accident." Each test name states the artifact/field mutated.
"""

import json
import importlib.util
from pathlib import Path

import validate_canonical
# Reuse whatever helper tests/assembly/unit/test_validate_canonical.py already uses
# to build a minimal valid package + its plan -- import it directly rather
# than duplicating construction logic. Pytest may not expose the sibling
# test module as an importable name during collection, so fall back to
# loading the file by path when necessary.
try:
    from test_validate_canonical import _build_minimal_valid_package, _load_plan_used_to_build
except Exception:
    spec = importlib.util.spec_from_file_location(
        "test_validate_canonical",
        Path(__file__).resolve().parent / "test_validate_canonical.py",
    )
    _mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_mod)
    _build_minimal_valid_package = _mod._build_minimal_valid_package
    _load_plan_used_to_build = _mod._load_plan_used_to_build


def test_deleted_media_file_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, with_media=True)
    media_file = next((package_dir / "media").iterdir())
    media_file.unlink()

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "broken_media_reference" for i in report.issues)


def test_absolute_media_reference_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, with_media=True)
    chunk_path = next((package_dir / "chunks").glob("*.md"))
    text = chunk_path.read_text()
    chunk_path.write_text(text.replace("../media/", "/etc/media/"))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "path_traversal_or_absolute_reference" for i in report.issues)


def test_removed_publication_map_entry_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, strategy="grouped")
    pub_map_path = package_dir / "publication-map.json"
    data = json.loads(pub_map_path.read_text())
    data["entries"].pop()
    pub_map_path.write_text(json.dumps(data))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "publication_map_chunk_mismatch" for i in report.issues)


def test_duplicate_publication_map_entry_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, strategy="grouped")
    pub_map_path = package_dir / "publication-map.json"
    data = json.loads(pub_map_path.read_text())
    data["entries"].append(dict(data["entries"][0]))
    pub_map_path.write_text(json.dumps(data))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(
        i.code in ("publication_map_chunk_mismatch", "publication_map_order_invalid")
        for i in report.issues
    )


def test_non_contiguous_publication_map_order_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, strategy="grouped")
    pub_map_path = package_dir / "publication-map.json"
    data = json.loads(pub_map_path.read_text())
    data["entries"][0]["order"] = 99
    pub_map_path.write_text(json.dumps(data))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "publication_map_order_invalid" for i in report.issues)


def test_manifest_plan_id_mismatch_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path)
    manifest_path = package_dir / "manifest.json"
    data = json.loads(manifest_path.read_text())
    data["plan_id"] = "sha256:" + "1" * 64
    manifest_path.write_text(json.dumps(data))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "plan_fingerprint_mismatch" for i in report.issues)


def test_duplicate_manifest_chunk_content_path_is_detected(tmp_path):
    # Round-3 review (GPT 5.6 blocking #6) caught that a single-chunk
    # fixture makes `data["chunks"][0] == data["chunks"][-1]` the SAME
    # entry -- overwriting a path with itself introduces no duplicate and
    # proves nothing. This fixture must have >= 2 chunks with genuinely
    # different paths BEFORE the mutation, asserted explicitly.
    package_dir = _build_minimal_valid_package(tmp_path, chunk_count=2)
    manifest_path = package_dir / "manifest.json"
    data = json.loads(manifest_path.read_text())
    assert len(data["chunks"]) >= 2, "fixture must have at least 2 chunks for this test to mean anything"
    assert data["chunks"][0]["content_file"] != data["chunks"][1]["content_file"], (
        "precondition: the two chunks must start with genuinely different paths"
    )
    data["chunks"][0]["content_file"] = data["chunks"][1]["content_file"]
    manifest_path.write_text(json.dumps(data))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "duplicate_content_path" for i in report.issues)


def test_orphan_media_file_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, with_media=True)
    (package_dir / "media" / "orphan.png").write_bytes(b"not-referenced")

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "orphan_media_file" for i in report.issues)


def test_encoded_traversal_media_reference_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, with_media=True)
    chunk_path = next((package_dir / "chunks").glob("*.md"))
    text = chunk_path.read_text()
    chunk_path.write_text(text.replace("../media/", "../media/%2e%2e/"))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"


def test_malformed_chunk_sidecar_json_is_a_controlled_validation_error(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path)
    meta_path = next((package_dir / "chunks").glob("*.meta.json"))
    meta_path.write_text("{not valid json")

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "malformed_json" for i in report.issues)


def test_publication_map_order_as_string_is_a_controlled_validation_error(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, strategy="grouped")
    pub_map_path = package_dir / "publication-map.json"
    data = json.loads(pub_map_path.read_text())
    data["entries"][0]["order"] = "zero"  # wrong type: string, not int
    pub_map_path.write_text(json.dumps(data))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"


def test_empty_publication_map_entries_for_nonempty_grouped_package_is_detected(tmp_path):
    package_dir = _build_minimal_valid_package(tmp_path, strategy="grouped", chunk_count=2)
    pub_map_path = package_dir / "publication-map.json"
    data = json.loads(pub_map_path.read_text())
    data["entries"] = []
    pub_map_path.write_text(json.dumps(data))

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status == "FAIL"
    assert any(i.code == "publication_map_chunk_mismatch" for i in report.issues)


# ---------------------------------------------------------------------------
# Standing-guard permanent meta-tests (round-4 requirement)
# ---------------------------------------------------------------------------

def test_deleted_media_file_detection_actually_depends_on_check_media_references(tmp_path, monkeypatch):
    """Standing guard (round-4 review): if _check_media_references is ever
    neutralized (accidentally or via a bad refactor), this test must go
    red -- proving test_deleted_media_file_is_detected depends on the real
    check, not on some other check incidentally catching the same case."""
    monkeypatch.setattr(validate_canonical, "_check_media_references", lambda *a, **kw: [])

    package_dir = _build_minimal_valid_package(tmp_path, with_media=True)
    media_file = next((package_dir / "media").iterdir())
    media_file.unlink()

    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)

    assert report.status != "FAIL" or not any(
        i.code == "broken_media_reference" for i in report.issues
    ), (
        "with _check_media_references neutralized, the deleted-media "
        "corruption should NOT be caught -- if this assertion fails "
        "(i.e. it WAS still caught), some other check is also detecting "
        "this case; find out which and note it, don't just delete this test"
    )


def test_content_comparison_skip_detection_actually_depends_on_its_own_check(tmp_path, monkeypatch):
    """Standing guard for the check closest to the image239 lesson itself
    -- the content-loss/duplication comparison. If this check is ever
    neutralized, the producer-path skip-is-an-error test (Task 7) must
    stop catching the omission."""
    monkeypatch.setattr(validate_canonical, "_check_content_loss_and_duplication", lambda *a, **kw: [])

    package_dir = _build_minimal_valid_package(tmp_path)
    plan = _load_plan_used_to_build(package_dir)
    report = validate_canonical.validate_canonical_package(package_dir, plan)  # cleaned_markdown_text omitted

    assert not any(i.code == "content_comparison_skipped" for i in report.issues), (
        "with _check_content_loss_and_duplication neutralized, the "
        "content-comparison-skip error should NOT appear -- if it does, "
        "the neutralization didn't actually take effect"
    )
