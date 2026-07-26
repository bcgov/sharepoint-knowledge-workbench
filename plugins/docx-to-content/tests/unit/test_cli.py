"""
Unit tests for scripts/cli.py — the argparse-based CLI skeleton for
analyze/confirm/convert/render/run.

Business logic (real pandoc analysis, canonical package building, actual
rendering) lands in Tasks 6/9/13. These tests only exercise: argument
parsing, exit-code wiring, dependency-precondition checks, and the
"run cannot bypass plan confirmation" behavioral contract.
"""

import json

import pytest

import cli
import contracts


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
