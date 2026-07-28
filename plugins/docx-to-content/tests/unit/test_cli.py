"""
Unit tests for scripts/cli.py — the argparse-based CLI skeleton for
analyze/confirm/convert/render/run.

Business logic (real pandoc analysis, canonical package building, actual
rendering) lands in Tasks 6/9/13. These tests only exercise: argument
parsing, exit-code wiring, dependency-precondition checks, and the
"run cannot bypass plan confirmation" behavioral contract.
"""

import json
import shutil
from pathlib import Path

import pytest

import cli
import contracts
import convert as convert_module


def _write_plan(path, status="confirmed"):
    plan = {
        "schema_version": "1.0",
        "plan_id": "plan-1",
        "source": {"path": "sourcedocuments/x.docx", "sha256": "a" * 64, "size_bytes": 10},
        "strategy": "heading-split",
        "chunk_level": 2,
        "chunk_anchors": [],
        "content_type": "procedure",
        "template_profile": "default",
        "confirmation": {
            "status": status,
            "confirmed_by": "tester",
            "confirmed_at": "2026-07-25T00:00:00Z",
        },
        "analysis_warnings": [],
    }
    path.write_text(json.dumps(plan))
    return path


# ---------------------------------------------------------------------------
# Missing source -> exit code 3
# ---------------------------------------------------------------------------

def test_analyze_missing_source_exits_3(tmp_path):
    rc = cli.main([
        "analyze",
        "--source", str(tmp_path / "does-not-exist.docx"),
        "--output", str(tmp_path / "out"),
    ])
    assert rc == 3


def test_convert_missing_source_exits_3(tmp_path):
    plan_path = _write_plan(tmp_path / "plan.json")
    rc = cli.main([
        "convert",
        "--source", str(tmp_path / "does-not-exist.docx"),
        "--plan", str(plan_path),
        "--output", str(tmp_path / "out"),
    ])
    assert rc == 3


def test_run_missing_source_exits_3(tmp_path):
    plan_path = _write_plan(tmp_path / "plan.json")
    rc = cli.main([
        "run",
        "--source", str(tmp_path / "does-not-exist.docx"),
        "--confirmed-plan", str(plan_path),
        "--output", str(tmp_path / "out"),
    ])
    assert rc == 3


# ---------------------------------------------------------------------------
# Missing pandoc -> exit code 3
# ---------------------------------------------------------------------------

def test_analyze_missing_pandoc_exits_3(tmp_path, monkeypatch):
    source = tmp_path / "source.docx"
    source.write_text("fake docx")
    monkeypatch.setattr(
        cli.dependencies, "probe_pandoc",
        lambda: cli.dependencies.DependencyStatus(name="pandoc", available=False),
    )
    rc = cli.main([
        "analyze",
        "--source", str(source),
        "--output", str(tmp_path / "out"),
    ])
    assert rc == 3


def test_convert_missing_pandoc_exits_3(tmp_path, monkeypatch):
    source = tmp_path / "source.docx"
    source.write_text("fake docx")
    plan_path = _write_plan(tmp_path / "plan.json")
    monkeypatch.setattr(
        cli.dependencies, "probe_pandoc",
        lambda: cli.dependencies.DependencyStatus(name="pandoc", available=False),
    )
    rc = cli.main([
        "convert",
        "--source", str(source),
        "--plan", str(plan_path),
        "--output", str(tmp_path / "out"),
    ])
    assert rc == 3


def test_run_missing_pandoc_exits_3(tmp_path, monkeypatch):
    source = tmp_path / "source.docx"
    source.write_text("fake docx")
    plan_path = _write_plan(tmp_path / "plan.json")
    monkeypatch.setattr(
        cli.dependencies, "probe_pandoc",
        lambda: cli.dependencies.DependencyStatus(name="pandoc", available=False),
    )
    rc = cli.main([
        "run",
        "--source", str(source),
        "--confirmed-plan", str(plan_path),
        "--output", str(tmp_path / "out"),
    ])
    assert rc == 3


# ---------------------------------------------------------------------------
# Missing soffice when legacy conversion is required -> exit code 3
# ---------------------------------------------------------------------------

def test_dependencies_reports_soffice_available_when_present(monkeypatch):
    monkeypatch.setattr(cli.dependencies.shutil, "which", lambda name: "/opt/homebrew/bin/soffice")
    status = cli.dependencies.probe_soffice()
    assert status.available is True


def test_dependencies_reports_soffice_unavailable_when_absent(monkeypatch):
    monkeypatch.setattr(cli.dependencies.shutil, "which", lambda name: None)
    status = cli.dependencies.probe_soffice()
    assert status.available is False


def test_cli_maps_missing_soffice_for_legacy_media_to_exit_3(tmp_path, monkeypatch):
    """No real legacy-media detection exists yet (Task 6+); this proves the
    CLI layer's exception-to-exit-code mapping is wired correctly by
    substituting a command handler that hits the require_soffice_if_needed
    seam directly, with soffice mocked absent."""
    source = tmp_path / "source.docx"
    source.write_text("fake docx")

    def fake_cmd_analyze(args):
        cli.dependencies.require_soffice_if_needed(needs_legacy_conversion=True)
        raise AssertionError("should not reach here")

    monkeypatch.setattr(cli.dependencies.shutil, "which", lambda name: None)
    monkeypatch.setattr(cli, "cmd_analyze", fake_cmd_analyze)

    rc = cli.main([
        "analyze",
        "--source", str(source),
        "--output", str(tmp_path / "out"),
    ])
    assert rc == 3


# ---------------------------------------------------------------------------
# Unsupported command -> exit code 4
# ---------------------------------------------------------------------------

def test_unsupported_command_exits_4(capsys):
    rc = cli.main(["frobnicate", "--source", "x"])
    assert rc == 4


def test_missing_required_argument_exits_4(capsys):
    rc = cli.main(["analyze", "--source", "x.docx"])  # missing --output
    assert rc == 4


def test_unsupported_renderer_exits_4(tmp_path):
    canonical = tmp_path / "canonical"
    canonical.mkdir()
    rc = cli.main([
        "render",
        "--canonical", str(canonical),
        "--renderer", "some-unsupported-renderer",
        "--output", str(tmp_path / "out"),
    ])
    assert rc == 4


# ---------------------------------------------------------------------------
# run cannot bypass plan confirmation
# ---------------------------------------------------------------------------

def test_run_rejects_draft_plan_exit_4(tmp_path):
    source = tmp_path / "source.docx"
    source.write_text("fake docx")
    plan_path = _write_plan(tmp_path / "plan.json", status="draft")

    rc = cli.main([
        "run",
        "--source", str(source),
        "--confirmed-plan", str(plan_path),
        "--output", str(tmp_path / "out"),
    ])
    assert rc == 4


def test_run_accepts_confirmed_plan_and_reaches_stub(tmp_path):
    source = tmp_path / "source.docx"
    source.write_text("fake docx")
    plan_path = _write_plan(tmp_path / "plan.json", status="confirmed")

    rc = cli.main([
        "run",
        "--source", str(source),
        "--confirmed-plan", str(plan_path),
        "--output", str(tmp_path / "out"),
    ])
    # Business logic isn't implemented yet (Tasks 9/13) -- the important
    # assertion is that this did NOT get rejected as an unconfirmed plan (4)
    # or a missing dependency (3); it reaches the not-implemented stub.
    assert rc == 1


def test_run_missing_confirmed_plan_file_exits_3(tmp_path):
    source = tmp_path / "source.docx"
    source.write_text("fake docx")
    rc = cli.main([
        "run",
        "--source", str(source),
        "--confirmed-plan", str(tmp_path / "no-such-plan.json"),
        "--output", str(tmp_path / "out"),
    ])
    assert rc == 3


# ---------------------------------------------------------------------------
# `convert` (Task 9): real end-to-end wiring through cli.main
# ---------------------------------------------------------------------------

_FIXTURES = Path(__file__).parent.parent / "fixtures"
_REPEATED_HEADINGS_DOCX = _FIXTURES / "repeated_headings.docx"


def test_convert_end_to_end_via_cli_writes_canonical_package(tmp_path):
    analysis_dir = tmp_path / "analysis"
    rc = cli.main([
        "analyze", "--source", str(_REPEATED_HEADINGS_DOCX), "--output", str(analysis_dir),
    ])
    assert rc == 0

    confirmed_path = tmp_path / "confirmed.json"
    rc = cli.main([
        "confirm",
        "--draft-plan", str(analysis_dir / "conversion-plan.draft.json"),
        "--output", str(confirmed_path),
    ])
    assert rc == 0

    out_dir = tmp_path / "run"
    rc = cli.main([
        "convert",
        "--source", str(_REPEATED_HEADINGS_DOCX),
        "--plan", str(confirmed_path),
        "--output", str(out_dir),
    ])
    assert rc == 0

    manifest = json.loads((out_dir / "canonical-content" / "manifest.json").read_text())
    assert manifest["chunk_count"] > 1
    assert (out_dir / "canonical-content" / "validation.json").exists()


def test_convert_rejects_stale_source_exit_4(tmp_path):
    source = tmp_path / "source.docx"
    shutil.copy(_REPEATED_HEADINGS_DOCX, source)

    analysis_dir = tmp_path / "analysis"
    cli.main(["analyze", "--source", str(source), "--output", str(analysis_dir)])
    confirmed_path = tmp_path / "confirmed.json"
    cli.main([
        "confirm",
        "--draft-plan", str(analysis_dir / "conversion-plan.draft.json"),
        "--output", str(confirmed_path),
    ])

    # Source modified after confirmation.
    source.write_bytes(source.read_bytes() + b"\x00")

    rc = cli.main([
        "convert",
        "--source", str(source),
        "--plan", str(confirmed_path),
        "--output", str(tmp_path / "run"),
    ])
    assert rc == 4


# ---------------------------------------------------------------------------
# `render` (Task 14b): real end-to-end wiring through cli.main
# ---------------------------------------------------------------------------

def _build_canonical_package(tmp_path):
    """Analyze/confirm via the real CLI path, then build a fully
    VALIDATED and PROMOTED canonical package via `convert.convert_and_promote`
    (Task 9/10/11's own helper -- the same one `cmd_convert` itself does
    NOT yet use, see convert.py's `convert_document` vs `convert_and_promote`
    docstrings). `CanonicalPackage.load()` requires a package that has
    actually passed `validate_canonical` (PASS/dispositioned-WARN), which
    only `convert_and_promote` produces -- `cli.main(["convert", ...])`
    currently calls the unvalidated `convert_document` entry point instead,
    so it is not reused here for that reason (pre-existing, out of this
    task's scope: cli.py `convert.py` wiring gap, not `cmd_render`'s)."""
    analysis_dir = tmp_path / "analysis"
    rc = cli.main([
        "analyze", "--source", str(_REPEATED_HEADINGS_DOCX), "--output", str(analysis_dir),
    ])
    assert rc == 0

    confirmed_path = tmp_path / "confirmed.json"
    rc = cli.main([
        "confirm",
        "--draft-plan", str(analysis_dir / "conversion-plan.draft.json"),
        "--output", str(confirmed_path),
    ])
    assert rc == 0

    plan = contracts.ConversionPlan.from_dict(json.loads(confirmed_path.read_text()))
    out_dir = tmp_path / "run"
    _manifest, _report, promoted, final_dir = convert_module.convert_and_promote(
        _REPEATED_HEADINGS_DOCX, plan, out_dir
    )
    assert promoted
    return final_dir


def test_render_end_to_end_via_cli_produces_rendered_output(tmp_path):
    """Proves the CLI PATH works end to end -- not just render_and_promote()
    called directly (that's already covered by test_validate_rendered.py) --
    since the gap this task closes is specifically `cmd_render` wiring."""
    canonical_dir = _build_canonical_package(tmp_path)
    render_out = tmp_path / "rendered"

    rc = cli.main([
        "render",
        "--canonical", str(canonical_dir),
        "--renderer", "multipage-markdown",
        "--output", str(render_out),
    ])
    assert rc == 0

    rendered_dir = render_out / "rendered-output"
    assert (rendered_dir / "index.md").exists()
    assert (rendered_dir / "pages").is_dir()
    assert any((rendered_dir / "pages").glob("*.md"))
    assert (rendered_dir / "renderer-validation.json").exists()

    report = json.loads((rendered_dir / "renderer-validation.json").read_text())
    assert report["status"] == "PASS"


def test_render_missing_canonical_dir_exits_3(tmp_path):
    rc = cli.main([
        "render",
        "--canonical", str(tmp_path / "does-not-exist"),
        "--renderer", "multipage-markdown",
        "--output", str(tmp_path / "out"),
    ])
    assert rc == 3


def test_render_validation_fail_exits_2(tmp_path):
    """A canonical package that fails CanonicalPackage.load()'s own
    validation (tampered chunk content, breaking its recorded
    content_sha256) is rejected with exit 2, matching cmd_convert's
    validation-FAIL mapping."""
    canonical_dir = _build_canonical_package(tmp_path)

    chunk_files = sorted((canonical_dir / "chunks").glob("*.md"))
    assert chunk_files, "expected at least one chunk to tamper with"
    target = chunk_files[0]
    target.write_text(target.read_text() + "\ntampered content\n")

    rc = cli.main([
        "render",
        "--canonical", str(canonical_dir),
        "--renderer", "multipage-markdown",
        "--output", str(tmp_path / "rendered"),
    ])
    assert rc == 2


def test_run_invalid_plan_contract_exits_2(tmp_path):
    source = tmp_path / "source.docx"
    source.write_text("fake docx")
    plan_path = tmp_path / "bad-plan.json"
    plan_path.write_text(json.dumps({"schema_version": "1.0"}))  # missing required fields

    rc = cli.main([
        "run",
        "--source", str(source),
        "--confirmed-plan", str(plan_path),
        "--output", str(tmp_path / "out"),
    ])
    assert rc == 2


# ---------------------------------------------------------------------------
# confirm command
# ---------------------------------------------------------------------------

def _write_draft_plan_dict(source_path):
    return {
        "schema_version": "1.0",
        "plan_id": "",
        "source": {"path": str(source_path), "sha256": "a" * 64, "size_bytes": 10},
        "strategy": "heading-split",
        "chunk_level": 1,
        "chunk_anchors": [],
        "content_type": "manual",
        "template_profile": "source-structure-v1",
        "confirmation": {"status": "draft", "confirmed_by": "", "confirmed_at": ""},
        "analysis_warnings": [],
    }


def test_confirm_missing_draft_plan_exits_3(tmp_path):
    rc = cli.main([
        "confirm",
        "--draft-plan", str(tmp_path / "no-such-draft.json"),
        "--output", str(tmp_path / "confirmed.json"),
    ])
    assert rc == 3


def test_confirm_malformed_plan_json_exits_2(tmp_path):
    draft_path = tmp_path / "bad-draft.json"
    draft_path.write_text(json.dumps({"schema_version": "1.0"}))  # missing required fields

    rc = cli.main([
        "confirm",
        "--draft-plan", str(draft_path),
        "--output", str(tmp_path / "confirmed.json"),
    ])
    assert rc == 2


def test_confirm_writes_new_file_and_succeeds(tmp_path):
    source = tmp_path / "source.docx"
    source.write_text("fake docx")
    draft_path = tmp_path / "draft.json"
    draft_path.write_text(json.dumps(_write_draft_plan_dict(source)))
    output_path = tmp_path / "confirmed.json"

    rc = cli.main([
        "confirm",
        "--draft-plan", str(draft_path),
        "--output", str(output_path),
    ])
    assert rc == 0
    written = json.loads(output_path.read_text())
    assert written["confirmation"]["status"] == "confirmed"
    assert written["plan_id"]


def test_confirm_already_confirmed_plan_exits_4(tmp_path):
    """Double-confirming a plan whose confirmation.status is already
    "confirmed" is rejected (exit 4, unsupported input) rather than
    silently allowed -- confirming should be a one-way, deliberate action
    tied to the draft it reviewed, not idempotent over an already-confirmed
    plan (which could re-stamp confirmed_by/confirmed_at unexpectedly)."""
    already_confirmed = _write_plan(tmp_path / "already-confirmed.json", status="confirmed")

    rc = cli.main([
        "confirm",
        "--draft-plan", str(already_confirmed),
        "--output", str(tmp_path / "confirmed-again.json"),
    ])
    assert rc == 4


# ---------------------------------------------------------------------------
# --help contract tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("subcommand,expected_flags", [
    ("analyze", ["--source", "--output"]),
    ("confirm", ["--draft-plan", "--output"]),
    ("convert", ["--source", "--plan", "--output"]),
    ("render", ["--canonical", "--renderer", "--output"]),
    ("run", ["--source", "--confirmed-plan", "--output"]),
])
def test_help_mentions_required_arguments(capsys, subcommand, expected_flags):
    with pytest.raises(SystemExit) as exc_info:
        cli.main([subcommand, "--help"])
    assert exc_info.value.code == 0
    out = capsys.readouterr().out
    for flag in expected_flags:
        assert flag in out


# ---------------------------------------------------------------------------
# Unexpected exceptions never surface as a bare traceback
# ---------------------------------------------------------------------------

def test_unexpected_exception_is_caught_and_reported(tmp_path, capsys, monkeypatch):
    def blow_up(args):
        raise RuntimeError("kaboom")

    monkeypatch.setattr(cli, "cmd_analyze", blow_up)
    source = tmp_path / "source.docx"
    source.write_text("fake docx")

    rc = cli.main(["analyze", "--source", str(source), "--output", str(tmp_path / "out")])
    assert rc != 0
    err = capsys.readouterr().err
    assert "kaboom" in err
