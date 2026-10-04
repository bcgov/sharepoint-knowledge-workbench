"""
project_setup.py
==================

Purpose:
    Stage 1 (`initialize-migration-project`) logic: confirm this
    repository's own connection config (`config.psd1`, owned by
    `sharepoint-workbench-setup`'s `workbench-initialize-connection-config` skill) already exists
    before creating a per-migration working directory to hold this
    pipeline's later-stage outputs (export, dependency-matrix.json,
    generated wave scripts, wave guide). Pure filesystem + text check --
    no tenant I/O, no PowerShell parsing (a lightweight regex presence
    check on the `Connection` key is sufficient, matching this workbench's
    existing lightweight `config.psd1` convention -- see
    `plugins/sharepoint-workbench-setup/scripts/config_setup.py`, which owns the only
    real `.psd1` writer/validator; this module never re-implements that,
    it only checks the file already exists with a `Connection` block).

Layer: sharepoint-site-migration / stage 1 (project setup)

Key Input Dependencies:
    - provisioning_outcomes.Outcome (symlinked from sharepoint-site-build-and-publish)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from provisioning_outcomes import Outcome

CONFIG_PSD1_NAME = "config.psd1"

# Per-migration working directory convention, matching this repo's existing
# `runs/<doc-name>/` convention for the content-pipeline plugins (see root
# CLAUDE.md's "Layout" section), adapted for migration-planning runs.
MIGRATION_RUNS_SUBDIR = ("runs", "sharepoint-migration-planning")


@dataclass(frozen=True)
class ConfigCheckResult:
    """Result of checking for a repository-root `config.psd1` with a
    `Connection` block. Never fabricates a config -- a missing file or
    missing `Connection` block is reported as `Outcome.FAILED` with an
    actionable message, never silently worked around."""

    outcome: str
    message: str = ""


@dataclass(frozen=True)
class ProjectPaths:
    """The per-migration working directory layout this skill creates.
    ``dependency_matrix`` and ``wave_guide`` name file paths that later
    stages write -- this skill itself does not create those files, only
    the directories that hold them."""

    root: Path
    export: Path
    generated_scripts: Path
    dependency_matrix: Path
    wave_guide: Path

    def to_dict(self) -> dict:
        return {
            "root": str(self.root),
            "export": str(self.export),
            "generated_scripts": str(self.generated_scripts),
            "dependency_matrix": str(self.dependency_matrix),
            "wave_guide": str(self.wave_guide),
        }


@dataclass(frozen=True)
class SetupResult:
    """Combined outcome of `setup_migration_project`: the config check plus
    (if the config check passed) the created project paths."""

    outcome: str
    message: str
    config_check: ConfigCheckResult
    paths: "ProjectPaths | None" = None


_CONNECTION_KEY_RE = re.compile(r"^\s*Connection\s*=", re.MULTILINE)


def check_config_psd1(repo_root: "Path | str") -> ConfigCheckResult:
    """Check for a repository-root `config.psd1` containing a `Connection`
    key. Text-level check only (no PowerShell DSC parsing) -- this module
    never writes or validates `config.psd1` itself, that is
    `sharepoint-workbench-setup`'s `workbench-initialize-connection-config` skill's job."""
    config_path = Path(repo_root) / CONFIG_PSD1_NAME
    if not config_path.is_file():
        return ConfigCheckResult(
            outcome=Outcome.FAILED,
            message=(
                f"{config_path} not found -- run sharepoint-workbench-setup's "
                "workbench-initialize-connection-config skill first to create it."
            ),
        )

    text = config_path.read_text(encoding="utf-8")
    if not _CONNECTION_KEY_RE.search(text):
        return ConfigCheckResult(
            outcome=Outcome.FAILED,
            message=(
                f"{config_path} exists but has no 'Connection' block -- run "
                "sharepoint-workbench-setup's workbench-initialize-connection-config skill to populate it."
            ),
        )

    return ConfigCheckResult(outcome=Outcome.OBSERVED, message=f"{config_path} has a Connection block.")


def project_paths(repo_root: "Path | str", project_slug: str) -> ProjectPaths:
    """Compute (but do not create) the per-migration working directory
    layout for `project_slug` under `runs/sharepoint-site-migration/`."""
    root = Path(repo_root).joinpath(*MIGRATION_RUNS_SUBDIR, project_slug)
    return ProjectPaths(
        root=root,
        export=root / "export",
        generated_scripts=root / "generated-scripts",
        dependency_matrix=root / "dependency-matrix.json",
        wave_guide=root / "wave-guide.md",
    )


def create_project_directories(paths: ProjectPaths) -> None:
    """Create the directories `paths` names (not the files -- those are
    written by later stages). Idempotent: safe to call again on an
    existing project directory."""
    paths.root.mkdir(parents=True, exist_ok=True)
    paths.export.mkdir(parents=True, exist_ok=True)
    paths.generated_scripts.mkdir(parents=True, exist_ok=True)


def setup_migration_project(
    repo_root: "Path | str",
    *,
    source_site_url: str,
    target_site_url: str,
    project_slug: str,
) -> SetupResult:
    """Stage 1 entry point: confirm `config.psd1` exists with a
    `Connection` block, then create the per-migration working directory.
    Never creates the working directory if the config check fails --
    reports `Outcome.FAILED` and stops, matching this plugin's honest-
    outcome vocabulary (`provisioning_outcomes.Outcome`)."""
    if not source_site_url:
        return SetupResult(
            outcome=Outcome.FAILED,
            message="source_site_url is required",
            config_check=ConfigCheckResult(outcome=Outcome.FAILED, message="source_site_url is required"),
        )
    if not target_site_url:
        return SetupResult(
            outcome=Outcome.FAILED,
            message="target_site_url is required",
            config_check=ConfigCheckResult(outcome=Outcome.FAILED, message="target_site_url is required"),
        )
    if not project_slug:
        return SetupResult(
            outcome=Outcome.FAILED,
            message="project_slug is required",
            config_check=ConfigCheckResult(outcome=Outcome.FAILED, message="project_slug is required"),
        )

    config_check = check_config_psd1(repo_root)
    if config_check.outcome != Outcome.OBSERVED:
        return SetupResult(
            outcome=Outcome.FAILED,
            message=config_check.message,
            config_check=config_check,
            paths=None,
        )

    paths = project_paths(repo_root, project_slug)
    create_project_directories(paths)

    return SetupResult(
        outcome=Outcome.OBSERVED,
        message=f"migration project directory ready at {paths.root}",
        config_check=config_check,
        paths=paths,
    )
