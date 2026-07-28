"""
Unit tests for scripts/plans.py — draft plan construction (Task 6) plus
confirmation and verification (Task 7).

Task 7 adds:
    - confirm_plan(draft_plan) -> ConversionPlan (status "confirmed",
      plan_id computed over finalized content)
    - verify_plan_against_source(plan, source_path) -> raises on sha256
      mismatch between the plan's recorded fingerprint and the source file
      as it exists on disk right now.
    - verify_plan_integrity(plan) -> raises if the plan's stored plan_id no
      longer matches a fresh hashing.compute_plan_id() over its content
      (detects hand-tampering of a confirmed plan JSON file).
    - require_confirmed(plan) -> raises unless confirmation.status ==
      "confirmed" (shared precondition helper).
"""

import json

import pytest

import contracts
import hashing
import plans


def _make_draft_plan(source_path):
    sha256 = hashing.content_hash(source_path.read_bytes())
    fingerprint = contracts.SourceFingerprint(
        path=str(source_path), sha256=sha256, size_bytes=source_path.stat().st_size,
    )
    anchors = [
        contracts.StructuralAnchor(
            stable_key="intro--abcd1234",
            heading_text="Introduction",
            heading_level=1,
            occurrence=1,
            source_heading_path=["Introduction"],
        )
    ]
    return plans.build_draft_plan(
        source_fingerprint=fingerprint,
        strategy="heading-split",
        chunk_level=1,
        chunk_anchors=anchors,
    )


# ---------------------------------------------------------------------------
# "grouped" strategy (Task 17-topic-grouping, Task 6)
# ---------------------------------------------------------------------------

def test_build_draft_plan_accepts_grouped_strategy(tmp_path):
    source = tmp_path / "source.docx"
    source.write_bytes(b"fake docx bytes")
    sha256 = hashing.content_hash(source.read_bytes())
    fingerprint = contracts.SourceFingerprint(
        path=str(source), sha256=sha256, size_bytes=source.stat().st_size,
    )
    plan = plans.build_draft_plan(
        source_fingerprint=fingerprint,
        strategy="grouped",
        chunk_level=1,
        chunk_anchors=[],
    )
    assert plan.strategy == "grouped"


# ---------------------------------------------------------------------------
# confirm_plan: new object, new file, not a mutation of the draft
# ---------------------------------------------------------------------------

def test_confirm_plan_sets_status_confirmed(tmp_path):
    source = tmp_path / "source.docx"
    source.write_bytes(b"fake docx bytes")
    draft = _make_draft_plan(source)

    confirmed = plans.confirm_plan(draft, confirmed_by="tester")

    assert confirmed.confirmation.status == "confirmed"
    assert confirmed.confirmation.confirmed_by == "tester"
    assert confirmed.confirmation.confirmed_at  # non-empty ISO-8601 timestamp


def test_confirm_plan_does_not_mutate_input_draft(tmp_path):
    source = tmp_path / "source.docx"
    source.write_bytes(b"fake docx bytes")
    draft = _make_draft_plan(source)

    plans.confirm_plan(draft, confirmed_by="tester")

    assert draft.confirmation.status == "draft"
    assert draft.confirmation.confirmed_at == ""


def test_confirm_plan_computes_plan_id_over_finalized_content(tmp_path):
    source = tmp_path / "source.docx"
    source.write_bytes(b"fake docx bytes")
    draft = _make_draft_plan(source)

    confirmed = plans.confirm_plan(draft, confirmed_by="tester")

    expected_plan_id = hashing.compute_plan_id(confirmed)
    assert confirmed.plan_id == expected_plan_id


def test_confirm_plan_cli_writes_new_file_leaves_draft_untouched(tmp_path):
    source = tmp_path / "source.docx"
    source.write_bytes(b"fake docx bytes")
    draft = _make_draft_plan(source)

    draft_path = tmp_path / "conversion-plan.draft.json"
    draft_path.write_text(json.dumps(draft.to_dict()))
    draft_bytes_before = draft_path.read_bytes()

    output_path = tmp_path / "conversion-plan.confirmed.json"

    import cli
    rc = cli.main([
        "confirm",
        "--draft-plan", str(draft_path),
        "--output", str(output_path),
    ])

    assert rc == 0
    assert output_path.exists()
    assert draft_path.read_bytes() == draft_bytes_before  # untouched
    written = contracts.ConversionPlan.from_dict(json.loads(output_path.read_text()))
    assert written.confirmation.status == "confirmed"


# ---------------------------------------------------------------------------
# verify_plan_against_source: source-hash mismatch after modification
# ---------------------------------------------------------------------------

def test_verify_plan_against_source_passes_when_unmodified(tmp_path):
    source = tmp_path / "source.docx"
    source.write_bytes(b"fake docx bytes")
    draft = _make_draft_plan(source)
    confirmed = plans.confirm_plan(draft, confirmed_by="tester")

    plans.verify_plan_against_source(confirmed, source)  # should not raise


def test_verify_plan_against_source_rejects_modified_source(tmp_path):
    source = tmp_path / "source.docx"
    source.write_bytes(b"fake docx bytes")
    draft = _make_draft_plan(source)
    confirmed = plans.confirm_plan(draft, confirmed_by="tester")

    source.write_bytes(b"tampered bytes -- different content entirely")

    with pytest.raises(plans.PlanVerificationError):
        plans.verify_plan_against_source(confirmed, source)


# ---------------------------------------------------------------------------
# verify_plan_integrity: plan_id mismatch after tampering with plan content
# ---------------------------------------------------------------------------

def test_verify_plan_integrity_passes_when_untampered(tmp_path):
    source = tmp_path / "source.docx"
    source.write_bytes(b"fake docx bytes")
    draft = _make_draft_plan(source)
    confirmed = plans.confirm_plan(draft, confirmed_by="tester")

    plans.verify_plan_integrity(confirmed)  # should not raise


def test_verify_plan_integrity_rejects_tampered_plan(tmp_path):
    source = tmp_path / "source.docx"
    source.write_bytes(b"fake docx bytes")
    draft = _make_draft_plan(source)
    confirmed = plans.confirm_plan(draft, confirmed_by="tester")

    plan_path = tmp_path / "conversion-plan.confirmed.json"
    plan_path.write_text(json.dumps(confirmed.to_dict()))

    data = json.loads(plan_path.read_text())
    data["chunk_anchors"][0]["heading_text"] = "Tampered Heading"
    # stored plan_id is left untouched -- that's the point of the test
    plan_path.write_text(json.dumps(data))

    reloaded = contracts.ConversionPlan.from_dict(json.loads(plan_path.read_text()))

    with pytest.raises(plans.PlanVerificationError):
        plans.verify_plan_integrity(reloaded)


# ---------------------------------------------------------------------------
# require_confirmed: shared precondition helper
# ---------------------------------------------------------------------------

def test_require_confirmed_passes_for_confirmed_plan(tmp_path):
    source = tmp_path / "source.docx"
    source.write_bytes(b"fake docx bytes")
    draft = _make_draft_plan(source)
    confirmed = plans.confirm_plan(draft, confirmed_by="tester")

    plans.require_confirmed(confirmed)  # should not raise


def test_require_confirmed_rejects_draft_plan(tmp_path):
    source = tmp_path / "source.docx"
    source.write_bytes(b"fake docx bytes")
    draft = _make_draft_plan(source)

    with pytest.raises(plans.PlanVerificationError):
        plans.require_confirmed(draft)


def test_convert_cli_rejects_draft_plan_status_exit_4(tmp_path):
    """Proves 'convert rejects confirmation.status = draft' without
    building Task 9's real convert pipeline -- the CLI's existing
    _require_confirmed_plan precondition (Task 5) already gates this."""
    import cli

    source = tmp_path / "source.docx"
    source.write_bytes(b"fake docx bytes")

    draft_plan_dict = {
        "schema_version": "1.0",
        "plan_id": "",
        "source": {"path": str(source), "sha256": "a" * 64, "size_bytes": 10},
        "strategy": "heading-split",
        "chunk_level": 1,
        "chunk_anchors": [],
        "content_type": "manual",
        "template_profile": "source-structure-v1",
        "confirmation": {"status": "draft", "confirmed_by": "", "confirmed_at": ""},
        "analysis_warnings": [],
    }
    plan_path = tmp_path / "conversion-plan.draft.json"
    plan_path.write_text(json.dumps(draft_plan_dict))

    rc = cli.main([
        "convert",
        "--source", str(source),
        "--plan", str(plan_path),
        "--output", str(tmp_path / "out"),
    ])
    assert rc == 4


# ---------------------------------------------------------------------------
# apply_media_decision (Task 18 general media-disposition mechanism)
# ---------------------------------------------------------------------------

def _draft_plan_with_pending_media(tmp_path):
    source = tmp_path / "source.docx"
    source.write_bytes(b"fake docx bytes")
    sha256 = hashing.content_hash(source.read_bytes())
    fingerprint = contracts.SourceFingerprint(
        path=str(source), sha256=sha256, size_bytes=source.stat().st_size,
    )
    return plans.build_draft_plan(
        source_fingerprint=fingerprint,
        strategy="grouped",
        chunk_level=1,
        chunk_anchors=[],
        media_decisions=[
            {
                "source_media_id": "image1.png",
                "source_position": "preamble-before-first-heading",
                "source_hash": "deadbeef",
                "media_type": "image/png",
                "classification": "requires-human-review",
                "disposition": "requires-human-decision",
                "canonical_inclusion": False,
                "publication_inclusion": False,
                "derived_asset_allowed": False,
                "reason": "preamble media requires human review",
                "decision_authority": "pending",
                "requires_alt_text": None,
            }
        ],
    )


def test_apply_media_decision_overrides_pending_record(tmp_path):
    draft = _draft_plan_with_pending_media(tmp_path)
    updated = plans.apply_media_decision(
        draft,
        source_media_id="image1.png",
        classification="obsolete-source-layout-artifact",
        disposition="omit-as-reviewed-artifact",
        reason="stale browser screenshot, not an authoritative branding asset",
    )
    record = updated.media_decisions[0]
    assert record["classification"] == "obsolete-source-layout-artifact"
    assert record["disposition"] == "omit-as-reviewed-artifact"
    assert record["decision_authority"] == "human-confirmed"
    # never mutates the original draft
    assert draft.media_decisions[0]["classification"] == "requires-human-review"
    # plan_id recomputed over the new content
    assert updated.plan_id != draft.plan_id


def test_apply_media_decision_raises_for_unknown_media_id(tmp_path):
    draft = _draft_plan_with_pending_media(tmp_path)
    with pytest.raises(ValueError):
        plans.apply_media_decision(
            draft,
            source_media_id="does-not-exist.png",
            classification="decorative",
            disposition="omit-as-reviewed-artifact",
            reason="n/a",
        )


def test_apply_media_decision_raises_on_already_confirmed_plan(tmp_path):
    draft = _draft_plan_with_pending_media(tmp_path)
    confirmed = plans.confirm_plan(draft, confirmed_by="tester")
    with pytest.raises(ValueError):
        plans.apply_media_decision(
            confirmed,
            source_media_id="image1.png",
            classification="decorative",
            disposition="omit-as-reviewed-artifact",
            reason="n/a",
        )


def test_confirm_plan_carries_media_decisions_forward_unchanged(tmp_path):
    draft = _draft_plan_with_pending_media(tmp_path)
    reviewed = plans.apply_media_decision(
        draft,
        source_media_id="image1.png",
        classification="obsolete-source-layout-artifact",
        disposition="omit-as-reviewed-artifact",
        reason="stale browser screenshot",
    )
    confirmed = plans.confirm_plan(reviewed, confirmed_by="tester")
    assert confirmed.media_decisions == reviewed.media_decisions
