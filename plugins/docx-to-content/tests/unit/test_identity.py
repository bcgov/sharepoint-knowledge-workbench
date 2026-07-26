"""
test_identity.py
================

Tests for scripts/identity.py — stable structural chunk identity (spec
Section 6.6, "Stable chunk identity"). A chunk ID must not depend on ordinal
position alone; it is derived from the normalized full heading path, the
occurrence number needed to disambiguate repeated paths, and a short hash of
the normalized structural key.

Fixture heading names are invented placeholders (e.g. "Section Alpha",
"Widget Configuration") — no real CEIS manual section names appear here.
"""

import re

from identity import make_chunk_id, normalize_heading_path


def test_normalize_heading_path_basic_ascii():
    result = normalize_heading_path(["Section Alpha", "Getting Started"])
    assert result == "section-alpha-getting-started"


def test_normalize_heading_path_collapses_punctuation_and_whitespace():
    result = normalize_heading_path(["Widget   Configuration!!", "Step  1: Setup"])
    assert result == "widget-configuration-step-1-setup"
    assert not result.startswith("-")
    assert not result.endswith("-")
    assert "--" not in result


def test_normalize_heading_path_is_unicode_safe_non_ascii_not_dropped():
    # Accented characters must not crash and must not collapse to an
    # empty/all-hyphen string.
    result = normalize_heading_path(["Configuración General"])
    assert result != ""
    assert re.fullmatch(r"[a-z0-9-]+", result)


def test_normalize_heading_path_is_unicode_safe_non_latin_script():
    # Non-Latin script (e.g. CJK) must not crash and must not silently
    # produce an empty string.
    result = normalize_heading_path(["設定 概要"])
    assert result != ""
    assert re.fullmatch(r"[a-z0-9-]+", result)


def test_make_chunk_id_shape_matches_spec_example_pattern():
    chunk_id = make_chunk_id(["Section Alpha", "Getting Started"])
    # Spec shape: <slug>--<8-hex-char-hash>
    assert re.fullmatch(r"[a-z0-9-]+--[0-9a-f]{8}", chunk_id)
    assert chunk_id.startswith("section-alpha-getting-started--")


def test_make_chunk_id_is_deterministic():
    id1 = make_chunk_id(["Section Alpha", "Getting Started"])
    id2 = make_chunk_id(["Section Alpha", "Getting Started"])
    assert id1 == id2


def test_make_chunk_id_repeated_identical_paths_disambiguated_by_occurrence():
    path = ["Overview"]
    id_occurrence_1 = make_chunk_id(path, occurrence=1)
    id_occurrence_2 = make_chunk_id(path, occurrence=2)
    assert id_occurrence_1 != id_occurrence_2
    # Occurrence must not be appended as a visible "-2" suffix on the slug;
    # it participates in the hash instead. Both IDs share the same slug
    # prefix but differ only in the hash segment.
    slug1, hash1 = id_occurrence_1.split("--")
    slug2, hash2 = id_occurrence_2.split("--")
    assert slug1 == slug2
    assert hash1 != hash2


def test_make_chunk_id_different_paths_produce_different_ids():
    id_a = make_chunk_id(["Section Alpha"])
    id_b = make_chunk_id(["Section Beta"])
    assert id_a != id_b


def test_make_chunk_id_no_positional_index_parameter_exists():
    # Position-independence-by-construction: the function signature has no
    # ordinal/index parameter, so there is no way for document position to
    # leak into the ID. This inspects the callable's parameter names.
    import inspect

    params = inspect.signature(make_chunk_id).parameters
    for forbidden in ("index", "position", "order", "source_order", "ordinal"):
        assert forbidden not in params


def test_chunk_id_position_independence_across_document_insertion():
    """The critical stability test (spec Section 6.6).

    Build heading tree A, B, C in document order. Compute chunk_ids from
    (path, occurrence) alone. Then simulate inserting an unrelated earlier
    section X before A, shifting document order to X, A, B, C. Recompute
    chunk_ids for A, B, C using the same (path, occurrence) inputs and prove
    they are identical to before — only source_order (tracked separately by
    the caller, not by make_chunk_id) would have shifted.
    """
    section_a_path = ["Section Alpha"]
    section_b_path = ["Section Alpha", "Widget Configuration"]
    section_c_path = ["Section Beta"]

    # Document order 1: A, B, C (source_order 0, 1, 2 — tracked externally)
    before = {
        "A": make_chunk_id(section_a_path, occurrence=1),
        "B": make_chunk_id(section_b_path, occurrence=1),
        "C": make_chunk_id(section_c_path, occurrence=1),
    }

    # Simulate document order 2: X, A, B, C (unrelated section X inserted
    # before A). source_order for A/B/C would now be 1, 2, 3 instead of
    # 0, 1, 2 — but that shift is not an input to make_chunk_id at all.
    section_x_path = ["Getting Started"]
    _ = make_chunk_id(section_x_path, occurrence=1)  # X's own id, unrelated

    after = {
        "A": make_chunk_id(section_a_path, occurrence=1),
        "B": make_chunk_id(section_b_path, occurrence=1),
        "C": make_chunk_id(section_c_path, occurrence=1),
    }

    assert before == after
