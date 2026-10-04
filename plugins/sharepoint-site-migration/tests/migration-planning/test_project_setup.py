"""Tests for project_setup.py -- stage 1 (initialize-migration-project):
confirms a repository-root config.psd1 with a Connection block exists (never
fabricates one), then creates a per-migration working directory. No tenant I/O."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "migration-planning"))

from project_setup import (
    ConfigCheckResult,
    check_config_psd1,
    create_project_directories,
    project_paths,
    setup_migration_project,
)
from provisioning_outcomes import Outcome


class TestCheckConfigPsd1:
    def test_missing_file_is_failed(self, tmp_path):
        result = check_config_psd1(tmp_path)
        assert result.outcome == Outcome.FAILED
        assert "workbench-initialize-connection-config" in result.message

    def test_file_without_connection_block_is_failed(self, tmp_path):
        (tmp_path / "config.psd1").write_text("@{\n    Defaults = @{}\n}\n")
        result = check_config_psd1(tmp_path)
        assert result.outcome == Outcome.FAILED
        assert "Connection" in result.message

    def test_file_with_connection_block_is_observed(self, tmp_path):
        (tmp_path / "config.psd1").write_text(
            "@{\n    Connection = @{\n        SiteUrl = 'https://contoso.sharepoint.com'\n    }\n}\n"
        )
        result = check_config_psd1(tmp_path)
        assert result.outcome == Outcome.OBSERVED


class TestProjectPaths:
    def test_computes_expected_layout(self, tmp_path):
        paths = project_paths(tmp_path, "acme-migration")
        assert paths.root == tmp_path / "runs" / "sharepoint-migration-planning" / "acme-migration"
        assert paths.export == paths.root / "export"
        assert paths.generated_scripts == paths.root / "generated-scripts"
        assert paths.dependency_matrix == paths.root / "dependency-matrix.json"
        assert paths.wave_guide == paths.root / "wave-guide.md"


class TestCreateProjectDirectories:
    def test_creates_root_export_and_generated_scripts_dirs(self, tmp_path):
        paths = project_paths(tmp_path, "acme-migration")
        create_project_directories(paths)
        assert paths.root.is_dir()
        assert paths.export.is_dir()
        assert paths.generated_scripts.is_dir()

    def test_idempotent(self, tmp_path):
        paths = project_paths(tmp_path, "acme-migration")
        create_project_directories(paths)
        create_project_directories(paths)  # must not raise
        assert paths.root.is_dir()


class TestSetupMigrationProject:
    def test_fails_without_config_psd1_and_creates_no_directory(self, tmp_path):
        result = setup_migration_project(
            tmp_path,
            source_site_url="https://contoso.sharepoint.com/sites/old",
            target_site_url="https://contoso.sharepoint.com/sites/new",
            project_slug="acme-migration",
        )
        assert result.outcome == Outcome.FAILED
        assert result.paths is None
        assert not (tmp_path / "runs").exists()

    def test_succeeds_with_valid_config_psd1(self, tmp_path):
        (tmp_path / "config.psd1").write_text("@{\n    Connection = @{\n        SiteUrl = 'x'\n    }\n}\n")
        result = setup_migration_project(
            tmp_path,
            source_site_url="https://contoso.sharepoint.com/sites/old",
            target_site_url="https://contoso.sharepoint.com/sites/new",
            project_slug="acme-migration",
        )
        assert result.outcome == Outcome.OBSERVED
        assert result.paths is not None
        assert result.paths.root.is_dir()
        assert result.paths.export.is_dir()

    def test_missing_required_arguments_fail_honestly(self, tmp_path):
        (tmp_path / "config.psd1").write_text("@{\n    Connection = @{}\n}\n")
        result = setup_migration_project(
            tmp_path, source_site_url="", target_site_url="https://x", project_slug="slug"
        )
        assert result.outcome == Outcome.FAILED
        assert result.paths is None
