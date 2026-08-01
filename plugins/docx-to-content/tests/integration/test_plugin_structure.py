#!/usr/bin/env python
"""
test_plugin_structure.py
=======================

TDD-first: Structure test for the docx-to-content plugin.
Validates that all required directories, metadata files, and skill definitions exist
and are well-formed.

Usage:
    pytest plugins/docx-to-content/tests/integration/test_plugin_structure.py -v
"""

import json
from pathlib import Path

import pytest
import yaml


PLUGIN_ROOT = Path(__file__).parent.parent.parent
EXPECTED_SKILLS = ["analyze-document", "convert-document", "render-content"]


class TestPluginStructure:
    """Validate the docx-to-content plugin directory structure."""

    def test_plugin_directory_exists(self):
        """Plugin root directory must exist."""
        assert PLUGIN_ROOT.exists(), f"Plugin directory does not exist: {PLUGIN_ROOT}"
        assert PLUGIN_ROOT.is_dir(), f"Plugin path is not a directory: {PLUGIN_ROOT}"

    def test_plugin_json_exists_and_valid(self):
        """plugin.json must exist and be valid JSON."""
        plugin_json_path = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
        assert plugin_json_path.exists(), f"plugin.json does not exist: {plugin_json_path}"

        content = plugin_json_path.read_text(encoding="utf-8")
        data = json.loads(content)  # Will raise JSONDecodeError if invalid

        # Validate required fields
        assert data.get("name") == "docx-to-content", "Plugin name must be 'docx-to-content'"
        assert data.get("version") == "0.1.0", "Plugin version must be '0.1.0'"
        assert "author" in data, "plugin.json must have an 'author' field"
        assert data["author"].get("name") == "Richard Fremmerlid", "Author name mismatch"

    def test_plugin_yaml_exists_and_valid(self):
        """plugin.yaml must exist and be valid YAML."""
        plugin_yaml_path = PLUGIN_ROOT / "plugin.yaml"
        assert plugin_yaml_path.exists(), f"plugin.yaml does not exist: {plugin_yaml_path}"

        content = plugin_yaml_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)  # Will raise YAMLError if invalid

        # Validate required fields
        assert data.get("name") == "docx-to-content", "Plugin name must be 'docx-to-content'"
        assert data.get("version") == "0.1.0", "Plugin version must be '0.1.0'"
        assert data.get("author") == "Richard Fremmerlid", "Author mismatch in plugin.yaml"

        # Validate skills list
        skills = data.get("skills", [])
        for expected_skill in EXPECTED_SKILLS:
            assert expected_skill in skills, f"Skill '{expected_skill}' not found in plugin.yaml skills list"

    def test_skills_directories_exist(self):
        """All three skill directories must exist."""
        for skill_name in EXPECTED_SKILLS:
            skill_dir = PLUGIN_ROOT / "skills" / skill_name
            assert skill_dir.exists(), f"Skill directory does not exist: {skill_dir}"
            assert skill_dir.is_dir(), f"Skill path is not a directory: {skill_dir}"

    def test_skill_metadata_files_exist(self):
        """Each skill must have a SKILL.md file."""
        for skill_name in EXPECTED_SKILLS:
            skill_md_path = PLUGIN_ROOT / "skills" / skill_name / "SKILL.md"
            assert skill_md_path.exists(), f"SKILL.md does not exist for {skill_name}: {skill_md_path}"

    def test_scripts_directory_exists(self):
        """scripts/ directory must exist."""
        scripts_dir = PLUGIN_ROOT / "scripts"
        assert scripts_dir.exists(), f"scripts directory does not exist: {scripts_dir}"
        assert scripts_dir.is_dir(), f"scripts path is not a directory: {scripts_dir}"

    def test_required_script_files_exist(self):
        """All required script files must exist (as placeholders).

        `dependencies.py` is intentionally absent (Phase 4.5 Wave 2),
        `plans.py` is intentionally absent (Phase 4.5 Wave 3), and
        `hashing.py`/`convert.py`/`chunking.py`/`package.py`/
        `validate_canonical.py` are intentionally absent (Phase 4.5 Wave 4):
        all now live in installed packages (`source-document-extraction`,
        `knowledge-analysis`, and `canonical-knowledge` respectively;
        compatibility path during the migration), not as local files -- see
        docs/superpowers/plans/phase-4-5-evidence/wave-2-flat-scripts-correction.md,
        wave-3-analysis-plan-split-decision.md,
        wave-4-canonical-knowledge-split-decision.md, and
        wave-5-knowledge-publication-split-decision.md.
        """
        required_scripts = [
            "cli.py",
            "analyze_structure.py",
        ]

        for script_name in required_scripts:
            script_path = PLUGIN_ROOT / "scripts" / script_name
            assert script_path.exists(), f"Script file does not exist: {script_path}"

    def test_pandoc_directory_no_longer_local(self):
        """scripts/pandoc/ (formerly scripts/pandoc_fixes/) is intentionally
        absent (Phase 4.5 Wave 2): it now lives in the installed
        `source-document-extraction` package (compatibility path during the
        migration), not as a local directory -- see
        docs/superpowers/plans/phase-4-5-evidence/wave-2-flat-scripts-correction.md.
        """
        pandoc_dir = PLUGIN_ROOT / "scripts" / "pandoc"
        assert not pandoc_dir.exists(), (
            f"scripts/pandoc/ should not exist locally -- it's supplied by "
            f"the installed source-document-extraction package: {pandoc_dir}"
        )

    def test_renderers_directory_no_longer_local(self):
        """scripts/renderers/ is intentionally absent (Phase 4.5 Wave 5):
        it now lives in the installed `knowledge-publication` package
        (compatibility path during the migration), not as a local
        directory -- see
        docs/superpowers/plans/phase-4-5-evidence/wave-5-knowledge-publication-split-decision.md.
        """
        renderers_dir = PLUGIN_ROOT / "scripts" / "renderers"
        assert not renderers_dir.exists(), (
            f"scripts/renderers/ should not exist locally -- it's supplied by "
            f"the installed knowledge-publication package: {renderers_dir}"
        )

    def test_tests_directories_exist(self):
        """Test subdirectories must exist."""
        test_subdirs = ["unit", "contract", "integration", "fixtures"]
        for subdir in test_subdirs:
            test_dir = PLUGIN_ROOT / "tests" / subdir
            assert test_dir.exists(), f"Test subdirectory does not exist: {test_dir}"
            assert test_dir.is_dir(), f"Test path is not a directory: {test_dir}"

    def test_references_directory_exists(self):
        """references/ directory must exist."""
        references_dir = PLUGIN_ROOT / "references"
        assert references_dir.exists(), f"references directory does not exist: {references_dir}"
        assert references_dir.is_dir(), f"references path is not a directory: {references_dir}"

    def test_required_reference_files_exist(self):
        """All required reference files must exist."""
        required_refs = [
            "pandoc-docx-setup.md",
            "known-pandoc-gaps.md",
            "canonical-contract.md",
        ]

        for ref_name in required_refs:
            ref_path = PLUGIN_ROOT / "references" / ref_name
            assert ref_path.exists(), f"Reference file does not exist: {ref_path}"

    def test_requirements_in_exists(self):
        """requirements.in must exist."""
        requirements_in_path = PLUGIN_ROOT / "requirements.in"
        assert requirements_in_path.exists(), f"requirements.in does not exist: {requirements_in_path}"

        # Validate it contains pytest
        content = requirements_in_path.read_text(encoding="utf-8")
        assert "pytest" in content, "requirements.in must contain 'pytest'"

    def test_requirements_txt_exists(self):
        """requirements.txt must exist (lock file)."""
        requirements_txt_path = PLUGIN_ROOT / "requirements.txt"
        assert requirements_txt_path.exists(), f"requirements.txt does not exist: {requirements_txt_path}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
