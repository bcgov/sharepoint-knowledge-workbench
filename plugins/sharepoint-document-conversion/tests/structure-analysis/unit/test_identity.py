"""test_identity.py
================

Purpose:
    Tests for scripts/structure-analysis/identity.py — stable structural chunk identity (spec Section 6.6, "Stable chunk identity").

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - re
    - identity

Tests for scripts/structure-analysis/identity.py — stable structural chunk identity (spec
Section 6.6, "Stable chunk identity"). A chunk ID must not depend on ordinal
position alone; it is derived from the normalized full heading path, the
occurrence number needed to disambiguate repeated paths, and a short hash of
the normalized structural key.

Fixture heading names are synthetic placeholders (e.g. "Section Alpha",
"Widget Configuration").

Key Functions Index:
    - test_normalize_heading_path_basic_ascii()
    - test_normalize_heading_path_collapses_punctuation_and_whitespace()
    - test_normalize_heading_path_is_unicode_safe_non_ascii_not_dropped()
    - test_normalize_heading_path_is_unicode_safe_non_latin_script()
    - test_make_chunk_id_shape_matches_spec_example_pattern()
    - test_make_chunk_id_is_deterministic()
    - test_make_chunk_id_repeated_identical_paths_disambiguated_by_occurrence()
    - test_make_chunk_id_different_paths_produce_different_ids()
    - test_make_chunk_id_no_positional_index_parameter_exists()
    - test_chunk_id_position_independence_across_document_insertion()
    - test_make_topic_id_uses_only_top_level_path()
    - test_make_topic_id_differs_by_occurrence()
    - test_make_topic_id_matches_slug_hash_shape()
    - test_make_topic_id_differs_from_chunk_id_for_same_top_level_path()"""

import re

from identity import make_chunk_id, make_topic_id, normalize_heading_path


# Verify normalize heading path basic ascii.
def test_normalize_heading_path_basic_ascii():
    """Verify normalize heading path basic ascii."""
    result = normalize_heading_path(["Section Alpha", "Getting Started"])
    assert result == "section-alpha-getting-started"


# Verify normalize heading path collapses punctuation and whitespace.
def test_normalize_heading_path_collapses_punctuation_and_whitespace():
    """Verify normalize heading path collapses punctuation and whitespace."""
    result = normalize_heading_path(["Widget   Configuration!!", "Step  1: Setup"])
    assert result == "widget-configuration-step-1-setup"
    assert not result.startswith("-")
    assert not result.endswith("-")
    assert "--" not in result


# Verify normalize heading path is unicode safe non ascii not dropped.
def test_normalize_heading_path_is_unicode_safe_non_ascii_not_dropped():
    # Accented characters must not crash and must not collapse to an
    # empty/all-hyphen string.
    """Verify normalize heading path is unicode safe non ascii not dropped."""
    result = normalize_heading_path(["Configuración General"])
    assert result != ""
    assert re.fullmatch(r"[a-z0-9-]+", result)


# Verify normalize heading path is unicode safe non latin script.
def test_normalize_heading_path_is_unicode_safe_non_latin_script():
    # Non-Latin script (e.g. CJK) must not crash and must not silently
    # produce an empty string.
    """Verify normalize heading path is unicode safe non latin script."""
    result = normalize_heading_path(["設定 概要"])
    assert result != ""
    assert re.fullmatch(r"[a-z0-9-]+", result)


# Verify make chunk ID shape matches spec example pattern.
def test_make_chunk_id_shape_matches_spec_example_pattern():
    """Verify make chunk ID shape matches spec example pattern."""
    chunk_id = make_chunk_id(["Section Alpha", "Getting Started"])
    # Spec shape: <slug>--<8-hex-char-hash>
    assert re.fullmatch(r"[a-z0-9-]+--[0-9a-f]{8}", chunk_id)
    assert chunk_id.startswith("section-alpha-getting-started--")


# Verify make chunk ID is deterministic.
def test_make_chunk_id_is_deterministic():
    """Verify make chunk ID is deterministic."""
    id1 = make_chunk_id(["Section Alpha", "Getting Started"])
    id2 = make_chunk_id(["Section Alpha", "Getting Started"])
    assert id1 == id2


# Verify make chunk ID repeated identical paths disambiguated by occurrence.
def test_make_chunk_id_repeated_identical_paths_disambiguated_by_occurrence():
    """Verify make chunk ID repeated identical paths disambiguated by occurrence."""
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


# Verify make chunk ID different paths produce different ids.
def test_make_chunk_id_different_paths_produce_different_ids():
    """Verify make chunk ID different paths produce different ids."""
    id_a = make_chunk_id(["Section Alpha"])
    id_b = make_chunk_id(["Section Beta"])
    assert id_a != id_b


# Verify make chunk ID no positional index parameter exists.
def test_make_chunk_id_no_positional_index_parameter_exists():
    # Position-independence-by-construction: the function signature has no
    # ordinal/index parameter, so there is no way for document position to
    # leak into the ID. This inspects the callable's parameter names.
    """Verify make chunk ID no positional index parameter exists."""
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


# Verify make topic ID uses only top level path.
def test_make_topic_id_uses_only_top_level_path():
    """Verify make topic ID uses only top level path."""
    topic_id_a = make_topic_id(["File Access"])
    topic_id_b = make_topic_id(["File Access"])
    assert topic_id_a == topic_id_b
    assert topic_id_a.startswith("file-access--")


# Verify make topic ID differs by occurrence.
def test_make_topic_id_differs_by_occurrence():
    """Verify make topic ID differs by occurrence."""
    first = make_topic_id(["Overview"], occurrence=1)
    second = make_topic_id(["Overview"], occurrence=2)
    assert first != second


# Verify make topic ID matches slug hash shape.
def test_make_topic_id_matches_slug_hash_shape():
    """Verify make topic ID matches slug hash shape."""
    topic_id = make_topic_id(["Sample Topic"])
    slug, _, digest = topic_id.partition("--")
    assert slug == "sample-topic"
    assert len(digest) == 8


# Verify make topic ID differs from chunk ID for same top level path.
def test_make_topic_id_differs_from_chunk_id_for_same_top_level_path():
    """Verify make topic ID differs from chunk ID for same top level path."""
    topic_id = make_topic_id(["File Access"])
    chunk_id_for_child = make_chunk_id(["File Access", "How to Seal a File"], occurrence=1)
    assert topic_id != chunk_id_for_child
    assert topic_id.split("--")[0] == "file-access"
