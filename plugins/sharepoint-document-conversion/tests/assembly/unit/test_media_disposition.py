"""test_media_disposition.py
==========================

Purpose:
    Tests for scripts/assembly/media_disposition.py — the general media classification/ disposition proposal mechanism (Task 18), scoped to preamble media (front matter before the first structural anchor, which is never copied into canonical output).

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - media_disposition

Tests for scripts/assembly/media_disposition.py — the general media classification/
disposition proposal mechanism (Task 18), scoped to preamble media (front
matter before the first structural anchor, which is never copied into
canonical output). Proposals are objective-signal-only; they never
conclude a final classification/disposition on their own -- that requires
`plans.apply_media_decision`.

Key Functions Index:
    - test_propose_media_decisions_finds_preamble_image_ref()
    - test_propose_media_decisions_defaults_to_requires_review()
    - test_propose_media_decisions_position_is_preamble()
    - test_propose_media_decisions_computes_hash_when_file_exists()
    - test_propose_media_decisions_no_refs_returns_empty_list()
    - test_propose_media_decisions_ignores_remote_urls()"""

import media_disposition


# Verify propose media decisions finds preamble image ref.
def test_propose_media_decisions_finds_preamble_image_ref(tmp_path):
    """Verify propose media decisions finds preamble image ref."""
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    (media_dir / "image1.png").write_bytes(b"fake-png-bytes")
    preamble = "![](media/image1.png){width=\"4in\"}\n\n**Title**\n"
    proposals = media_disposition.propose_media_decisions(preamble, media_dir)
    assert len(proposals) == 1
    assert proposals[0]["source_media_id"] == "image1.png"


# Verify propose media decisions defaults to requires review.
def test_propose_media_decisions_defaults_to_requires_review():
    """Verify propose media decisions defaults to requires review."""
    preamble = "![](media/image1.png)\n"
    proposals = media_disposition.propose_media_decisions(preamble, None)
    assert proposals[0]["classification"] == "requires-human-review"
    assert proposals[0]["disposition"] == "requires-human-decision"
    assert proposals[0]["canonical_inclusion"] is False
    assert proposals[0]["publication_inclusion"] is False
    assert proposals[0]["derived_asset_allowed"] is False


# Verify propose media decisions position is preamble.
def test_propose_media_decisions_position_is_preamble():
    """Verify propose media decisions position is preamble."""
    preamble = "![](media/image1.png)\n"
    proposals = media_disposition.propose_media_decisions(preamble, None)
    assert proposals[0]["source_position"] == "preamble-before-first-heading"


# Verify propose media decisions computes hash when file exists.
def test_propose_media_decisions_computes_hash_when_file_exists(tmp_path):
    """Verify propose media decisions computes hash when file exists."""
    media_dir = tmp_path / "media" / "media"
    media_dir.mkdir(parents=True)
    (media_dir / "image1.png").write_bytes(b"fake-png-bytes")
    preamble = "![](media/image1.png)\n"
    # pandoc's --extract-media nests under <dir>/media/ -- proposal must
    # find the file recursively, not just at the top level.
    proposals = media_disposition.propose_media_decisions(preamble, tmp_path / "media")
    assert proposals[0]["source_hash"] is not None
    assert proposals[0]["size_bytes"] == len(b"fake-png-bytes")


# Verify propose media decisions no refs returns empty list.
def test_propose_media_decisions_no_refs_returns_empty_list():
    """Verify propose media decisions no refs returns empty list."""
    assert media_disposition.propose_media_decisions("no images here\n", None) == []


# Verify propose media decisions ignores remote urls.
def test_propose_media_decisions_ignores_remote_urls():
    """Verify propose media decisions ignores remote urls."""
    preamble = "![](https://example.com/image.png)\n"
    assert media_disposition.propose_media_decisions(preamble, None) == []
