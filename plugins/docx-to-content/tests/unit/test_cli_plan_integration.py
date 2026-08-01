"""
Integration tests for cli.py's `confirm`/`convert` commands against a
draft/confirmed ConversionPlan (Task 5/7). Split out of
tests/unit/test_plans.py during Phase 4.5 Wave 3: plan construction/
confirmation/verification logic itself moved to `knowledge-analysis`
(`scripts/plans.py`), but cli.py stays in docx-to-content as the
compatibility orchestrator -- these two tests exercise cli.py's own
command wiring, not knowledge-analysis's plan logic, so they stay here
rather than creating a knowledge-analysis -> docx-to-content dependency.

Requires `knowledge-analysis` to be `pip install -e`'d into whatever
environment runs this plugin's tests -- cli.py's `confirm` command calls
into it (transition-only dependency, per the compatibility-shim pattern;
see docs/superpowers/plans/phase-4-5-evidence/wave-3-analysis-plan-split-decision.md).
"""

import json

from plan_schema import analysis_plan as contracts
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


def test_convert_cli_rejects_draft_plan_status_exit_4(tmp_path):
    """Proves 'convert rejects confirmation.status = draft' without
    building the real convert pipeline -- the CLI's existing
    _require_confirmed_plan precondition already gates this."""
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
