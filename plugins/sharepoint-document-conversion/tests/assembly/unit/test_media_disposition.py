"""
test_media_disposition.py
==========================

Tests for scripts/assembly/media_disposition.py — the general media classification/
disposition proposal mechanism (Task 18), scoped to preamble media (front
matter before the first structural anchor, which is never copied into
canonical output). Proposals are objective-signal-only; they never
conclude a final classification/disposition on their own -- that requires
`plans.apply_media_decision`.
"""

import media_disposition


def test_propose_media_decisions_finds_preamble_image_ref(tmp_path):
    media_dir = tmp_path / "media"
    media_dir.mkdir()
    (media_dir / "image1.png").write_bytes(b"fake-png-bytes")
    preamble = "![](media/image1.png){width=\"4in\"}\n\n**Title**\n"
    proposals = media_disposition.propose_media_decisions(preamble, media_dir)
    assert len(proposals) == 1
    assert proposals[0]["source_media_id"] == "image1.png"


def test_propose_media_decisions_defaults_to_requires_review():
    preamble = "![](media/image1.png)\n"
    proposals = media_disposition.propose_media_decisions(preamble, None)
    assert proposals[0]["classification"] == "requires-human-review"
    assert proposals[0]["disposition"] == "requires-human-decision"
    assert proposals[0]["canonical_inclusion"] is False
    assert proposals[0]["publication_inclusion"] is False
    assert proposals[0]["derived_asset_allowed"] is False


def test_propose_media_decisions_position_is_preamble():
    preamble = "![](media/image1.png)\n"
    proposals = media_disposition.propose_media_decisions(preamble, None)
    assert proposals[0]["source_position"] == "preamble-before-first-heading"


def test_propose_media_decisions_computes_hash_when_file_exists(tmp_path):
    media_dir = tmp_path / "media" / "media"
    media_dir.mkdir(parents=True)
    (media_dir / "image1.png").write_bytes(b"fake-png-bytes")
    preamble = "![](media/image1.png)\n"
    # pandoc's --extract-media nests under <dir>/media/ -- proposal must
    # find the file recursively, not just at the top level.
    proposals = media_disposition.propose_media_decisions(preamble, tmp_path / "media")
    assert proposals[0]["source_hash"] is not None
    assert proposals[0]["size_bytes"] == len(b"fake-png-bytes")


def test_propose_media_decisions_no_refs_returns_empty_list():
    assert media_disposition.propose_media_decisions("no images here\n", None) == []


def test_propose_media_decisions_ignores_remote_urls():
    preamble = "![](https://example.com/image.png)\n"
    assert media_disposition.propose_media_decisions(preamble, None) == []
