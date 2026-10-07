"""Purpose:
    Unit tests for scripts/structure-analysis/plans.py — draft plan construction (Task 6) plus confirmation and verification (Task 7).

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - json
    - pytest
    - plan_schema
    - plan_hashing
    - plans

Unit tests for scripts/structure-analysis/plans.py — draft plan construction (Task 6) plus
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

Key Functions Index:
    - _make_draft_plan()
    - test_build_draft_plan_accepts_grouped_strategy()
    - test_confirm_plan_sets_status_confirmed()
    - test_confirm_plan_does_not_mutate_input_draft()
    - test_confirm_plan_computes_plan_id_over_finalized_content()
    - test_verify_plan_against_source_passes_when_unmodified()
    - test_verify_plan_against_source_rejects_modified_source()
    - test_verify_plan_integrity_passes_when_untampered()
    - test_verify_plan_integrity_rejects_tampered_plan()
    - test_require_confirmed_passes_for_confirmed_plan()
    - test_require_confirmed_rejects_draft_plan()
    - _draft_plan_with_pending_media()
    - test_apply_media_decision_overrides_pending_record()
    - test_apply_media_decision_raises_for_unknown_media_id()
    - test_apply_media_decision_raises_on_already_confirmed_plan()
    - test_confirm_plan_carries_media_decisions_forward_unchanged()"""

import json

import pytest

from plan_schema import analysis_plan as contracts
import plan_hashing as hashing
import plans


# Build a draft ConversionPlan from the supplied source and anchors.
def _make_draft_plan(source_path):
    """Build a draft ConversionPlan from the supplied source and anchors."""
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
    """Verify build draft plan accepts grouped strategy."""
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
    """Verify confirm plan sets status confirmed."""
    source = tmp_path / "source.docx"
    source.write_bytes(b"fake docx bytes")
    draft = _make_draft_plan(source)

    confirmed = plans.confirm_plan(draft, confirmed_by="tester")

    assert confirmed.confirmation.status == "confirmed"
    assert confirmed.confirmation.confirmed_by == "tester"
    assert confirmed.confirmation.confirmed_at  # non-empty ISO-8601 timestamp


# Verify confirm plan does not mutate input draft.
def test_confirm_plan_does_not_mutate_input_draft(tmp_path):
    """Verify confirm plan does not mutate input draft."""
    source = tmp_path / "source.docx"
    source.write_bytes(b"fake docx bytes")
    draft = _make_draft_plan(source)

    plans.confirm_plan(draft, confirmed_by="tester")

    assert draft.confirmation.status == "draft"
    assert draft.confirmation.confirmed_at == ""


# Verify confirm plan computes plan ID over finalized content.
def test_confirm_plan_computes_plan_id_over_finalized_content(tmp_path):
    """Verify confirm plan computes plan ID over finalized content."""
    source = tmp_path / "source.docx"
    source.write_bytes(b"fake docx bytes")
    draft = _make_draft_plan(source)

    confirmed = plans.confirm_plan(draft, confirmed_by="tester")

    expected_plan_id = hashing.compute_plan_id(confirmed)
    assert confirmed.plan_id == expected_plan_id


# cli.py integration tests for `confirm`/`convert` (test_confirm_plan_cli_writes_new_file_leaves_draft_untouched,
# test_convert_cli_rejects_draft_plan_status_exit_4) moved to
# docx-to-content/tests/unit/test_cli_plan_integration.py -- cli.py stays
# in docx-to-content as the compatibility orchestrator, so its own
# integration tests must not create a document-structure-analysis -> docx-to-content
# dependency.

# ---------------------------------------------------------------------------
# verify_plan_against_source: source-hash mismatch after modification
# ---------------------------------------------------------------------------

def test_verify_plan_against_source_passes_when_unmodified(tmp_path):
    """Verify verify plan against source passes when unmodified."""
    source = tmp_path / "source.docx"
    source.write_bytes(b"fake docx bytes")
    draft = _make_draft_plan(source)
    confirmed = plans.confirm_plan(draft, confirmed_by="tester")

    plans.verify_plan_against_source(confirmed, source)  # should not raise


# Verify verify plan against source rejects modified source.
def test_verify_plan_against_source_rejects_modified_source(tmp_path):
    """Verify verify plan against source rejects modified source."""
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
    """Verify verify plan integrity passes when untampered."""
    source = tmp_path / "source.docx"
    source.write_bytes(b"fake docx bytes")
    draft = _make_draft_plan(source)
    confirmed = plans.confirm_plan(draft, confirmed_by="tester")

    plans.verify_plan_integrity(confirmed)  # should not raise


# Verify verify plan integrity rejects tampered plan.
def test_verify_plan_integrity_rejects_tampered_plan(tmp_path):
    """Verify verify plan integrity rejects tampered plan."""
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
    """Verify require confirmed passes for confirmed plan."""
    source = tmp_path / "source.docx"
    source.write_bytes(b"fake docx bytes")
    draft = _make_draft_plan(source)
    confirmed = plans.confirm_plan(draft, confirmed_by="tester")

    plans.require_confirmed(confirmed)  # should not raise


# Verify require confirmed rejects draft plan.
def test_require_confirmed_rejects_draft_plan(tmp_path):
    """Verify require confirmed rejects draft plan."""
    source = tmp_path / "source.docx"
    source.write_bytes(b"fake docx bytes")
    draft = _make_draft_plan(source)

    with pytest.raises(plans.PlanVerificationError):
        plans.require_confirmed(draft)


# ---------------------------------------------------------------------------
# apply_media_decision (Task 18 general media-disposition mechanism)
# ---------------------------------------------------------------------------

def _draft_plan_with_pending_media(tmp_path):
    """Build a draft plan that retains unresolved media decisions for validation tests."""
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


# Verify apply media decision overrides pending record.
def test_apply_media_decision_overrides_pending_record(tmp_path):
    """Verify apply media decision overrides pending record."""
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


# Verify apply media decision raises for unknown media ID.
def test_apply_media_decision_raises_for_unknown_media_id(tmp_path):
    """Verify apply media decision raises for unknown media ID."""
    draft = _draft_plan_with_pending_media(tmp_path)
    with pytest.raises(ValueError):
        plans.apply_media_decision(
            draft,
            source_media_id="does-not-exist.png",
            classification="decorative",
            disposition="omit-as-reviewed-artifact",
            reason="n/a",
        )


# Verify apply media decision raises on already confirmed plan.
def test_apply_media_decision_raises_on_already_confirmed_plan(tmp_path):
    """Verify apply media decision raises on already confirmed plan."""
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


# Verify confirm plan carries media decisions forward unchanged.
def test_confirm_plan_carries_media_decisions_forward_unchanged(tmp_path):
    """Verify confirm plan carries media decisions forward unchanged."""
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
