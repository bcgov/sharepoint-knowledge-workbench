"""
Unit tests for scripts/dependencies.py — dependency probing for pandoc and
soffice, and the require_soffice_if_needed() seam used by later tasks'
legacy-media detection.
"""

import subprocess

import pytest

import dependencies


def test_probe_pandoc_real_environment_is_available():
    """Integration-ish: this repo's documented baseline (Task 0) has pandoc
    3.8.3 on PATH, so a real (non-mocked) probe should succeed here."""
    status = dependencies.probe_pandoc()
    assert status.name == "pandoc"
    assert status.available is True
    assert status.path is not None
    assert status.version is not None
    assert "pandoc" in status.version.lower()


@pytest.mark.skipif(
    dependencies.shutil.which("soffice") is None,
    reason="soffice / LibreOffice is not installed on PATH in this environment",
)
def test_probe_soffice_real_environment_is_available():
    """Integration-ish: verifies probe_soffice when soffice is on PATH."""
    status = dependencies.probe_soffice()
    assert status.name == "soffice"
    assert status.available is True
    assert status.path is not None


def test_probe_pandoc_missing_is_reported_unavailable(monkeypatch):
    monkeypatch.setattr(dependencies.shutil, "which", lambda name: None)
    status = dependencies.probe_pandoc()
    assert status.available is False
    assert status.path is None
    assert status.version is None


def test_probe_soffice_missing_is_reported_unavailable(monkeypatch):
    monkeypatch.setattr(dependencies.shutil, "which", lambda name: None)
    status = dependencies.probe_soffice()
    assert status.available is False
    assert status.path is None
    assert status.version is None


def test_probe_version_subprocess_failure_still_reports_available(monkeypatch):
    """If the executable exists but --version explodes, we still report
    available=True (it's on PATH) with version=None rather than crashing."""
    monkeypatch.setattr(dependencies.shutil, "which", lambda name: "/usr/bin/pandoc")

    def _boom(*args, **kwargs):
        raise subprocess.SubprocessError("boom")

    monkeypatch.setattr(dependencies.subprocess, "run", _boom)
    status = dependencies.probe_pandoc()
    assert status.available is True
    assert status.path == "/usr/bin/pandoc"
    assert status.version is None


def test_require_soffice_if_needed_noop_when_not_needed(monkeypatch):
    monkeypatch.setattr(dependencies.shutil, "which", lambda name: None)
    # should not raise even though soffice is "absent"
    dependencies.require_soffice_if_needed(needs_legacy_conversion=False)


def test_require_soffice_if_needed_raises_when_missing_and_needed(monkeypatch):
    monkeypatch.setattr(dependencies.shutil, "which", lambda name: None)
    with pytest.raises(dependencies.MissingDependencyError) as exc_info:
        dependencies.require_soffice_if_needed(needs_legacy_conversion=True)
    assert exc_info.value.dependency_name == "soffice"


def test_require_soffice_if_needed_passes_when_available(monkeypatch):
    monkeypatch.setattr(dependencies.shutil, "which", lambda name: "/opt/homebrew/bin/soffice")
    # should not raise
    dependencies.require_soffice_if_needed(needs_legacy_conversion=True)
