"""
test_analysis_plan_contract.py
===============================

Contract tests for the `analysis-plan` wire shape: SourceFingerprint,
StructuralAnchor, Confirmation, ConversionPlan (see
plan_schema/analysis_plan.py), plus plan_id computation (plan_hashing.py).

Split out of docx-to-content's tests/contract/test_contracts.py during
Phase 4.5 Wave 3 -- this plugin is now the sole producer/owner of this
contract. See
docs/superpowers/plans/phase-4-5-evidence/wave-3-analysis-plan-split-decision.md.

These tests exercise:
- round-trip to_dict()/from_dict() for every required field,
- strict rejection of dicts missing required fields,
- strict rejection of unsupported/missing schema_version,
- plan_id exclusion of plan_id itself and confirmation.confirmed_at.
"""

import pytest

from plan_schema.analysis_plan import (
    SourceFingerprint,
    StructuralAnchor,
    ConversionPlan,
    Confirmation,
)
from plan_hashing import compute_plan_id


def make_plan_dict(confirmed_at="2026-07-25T00:00:00Z"):
    return {
        "schema_version": "1.0",
        "plan_id": "sha256:" + "0" * 64,
        "source": {
            "path": "sourcedocuments/CEIS MANUAL - working version.docx",
            "sha256": "a" * 64,
            "size_bytes": 12345,
        },
        "strategy": "chunked",
        "chunk_level": 2,
        "chunk_anchors": [
            {
                "stable_key": "file-access",
                "heading_text": "FILE ACCESS",
                "heading_level": 2,
                "occurrence": 1,
                "source_heading_path": ["FILE ACCESS"],
            }
        ],
        "content_type": "manual",
        "template_profile": "source-structure-v1",
        "confirmation": {
            "status": "confirmed",
            "confirmed_by": "user-or-supervising-agent",
            "confirmed_at": confirmed_at,
        },
        "analysis_warnings": [],
    }


# ---------------------------------------------------------------------------
# SourceFingerprint
# ---------------------------------------------------------------------------

class TestSourceFingerprint:
    def test_round_trip(self):
        data = {
            "path": "sourcedocuments/x.docx",
            "sha256": "a" * 64,
            "size_bytes": 100,
        }
        fp = SourceFingerprint.from_dict(data)
        assert fp.to_dict() == data

    def test_missing_required_field_raises(self):
        data = {"path": "x.docx", "sha256": "a" * 64}
        with pytest.raises(ValueError):
            SourceFingerprint.from_dict(data)


# ---------------------------------------------------------------------------
# StructuralAnchor
# ---------------------------------------------------------------------------

class TestStructuralAnchor:
    def test_round_trip(self):
        data = {
            "stable_key": "file-access",
            "heading_text": "FILE ACCESS",
            "heading_level": 2,
            "occurrence": 1,
            "source_heading_path": ["FILE ACCESS"],
        }
        anchor = StructuralAnchor.from_dict(data)
        assert anchor.to_dict() == data

    def test_missing_required_field_raises(self):
        data = {
            "stable_key": "file-access",
            "heading_text": "FILE ACCESS",
            "heading_level": 2,
        }
        with pytest.raises(ValueError):
            StructuralAnchor.from_dict(data)


# ---------------------------------------------------------------------------
# ConversionPlan
# ---------------------------------------------------------------------------

class TestConversionPlan:
    def test_round_trip_all_fields(self):
        data = make_plan_dict()
        plan = ConversionPlan.from_dict(data)
        assert plan.to_dict() == data

    def test_missing_required_field_raises(self):
        data = make_plan_dict()
        del data["strategy"]
        with pytest.raises(ValueError):
            ConversionPlan.from_dict(data)

    def test_missing_schema_version_raises(self):
        data = make_plan_dict()
        del data["schema_version"]
        with pytest.raises(ValueError):
            ConversionPlan.from_dict(data)

    def test_unsupported_schema_version_raises(self):
        data = make_plan_dict()
        data["schema_version"] = "99.9"
        with pytest.raises(ValueError):
            ConversionPlan.from_dict(data)

    def test_confirmation_status_values(self):
        data = make_plan_dict()
        data["confirmation"]["status"] = "draft"
        plan = ConversionPlan.from_dict(data)
        assert plan.confirmation.status == "draft"

    def test_nested_source_and_anchors_are_typed(self):
        plan = ConversionPlan.from_dict(make_plan_dict())
        assert isinstance(plan.source, SourceFingerprint)
        assert all(isinstance(a, StructuralAnchor) for a in plan.chunk_anchors)
        assert isinstance(plan.confirmation, Confirmation)


# ---------------------------------------------------------------------------
# compute_plan_id
# ---------------------------------------------------------------------------

class TestComputePlanId:
    def test_plan_id_prefixed(self):
        plan = ConversionPlan.from_dict(make_plan_dict())
        plan_id = compute_plan_id(plan)
        assert plan_id.startswith("sha256:")
        assert len(plan_id) == len("sha256:") + 64

    def test_plan_id_excludes_confirmed_at_timestamp(self):
        plan_a = ConversionPlan.from_dict(
            make_plan_dict(confirmed_at="2026-07-25T00:00:00Z")
        )
        plan_b = ConversionPlan.from_dict(
            make_plan_dict(confirmed_at="2030-01-01T12:34:56Z")
        )
        assert compute_plan_id(plan_a) == compute_plan_id(plan_b)

    def test_plan_id_excludes_plan_id_field_itself(self):
        data_a = make_plan_dict()
        data_a["plan_id"] = "sha256:" + "1" * 64
        data_b = make_plan_dict()
        data_b["plan_id"] = "sha256:" + "2" * 64
        plan_a = ConversionPlan.from_dict(data_a)
        plan_b = ConversionPlan.from_dict(data_b)
        assert compute_plan_id(plan_a) == compute_plan_id(plan_b)

    def test_plan_id_changes_with_content(self):
        data_a = make_plan_dict()
        data_b = make_plan_dict()
        data_b["chunk_level"] = 3
        plan_a = ConversionPlan.from_dict(data_a)
        plan_b = ConversionPlan.from_dict(data_b)
        assert compute_plan_id(plan_a) != compute_plan_id(plan_b)


def test_conversion_plan_schema_version_constant():
    from plan_schema.analysis_plan import CONVERSION_PLAN_SCHEMA_VERSION

    assert CONVERSION_PLAN_SCHEMA_VERSION == "1.0"

    with pytest.raises(ValueError, match="schema_version"):
        ConversionPlan.from_dict({**make_plan_dict(), "schema_version": "9.9"})
