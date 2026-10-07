"""Purpose:
    Exercise native skill file creation and its overwrite and input safeguards.

Key Input Dependencies:
    - scripts/create-sharepoint-native-skill.ps1
    - PowerShell (pwsh) when available

Executable tests for create-sharepoint-native-skill.ps1, run via pwsh (no tenant
connection required -- this script performs zero tenant I/O by design).

Function Index:
    - run_script
    - test_writes_valid_skill_md
    - test_rejects_invalid_skill_name
    - test_requires_instructions_source
    - test_refuses_to_overwrite_without_flag
    - test_overwrite_flag_allows_replace
"""
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "create-sharepoint-native-skill.ps1"

pwsh = shutil.which("pwsh")
pytestmark = pytest.mark.skipif(pwsh is None, reason="pwsh not installed")


# Run the agent-creation PowerShell script with the supplied arguments.
def run_script(args: list[str]) -> subprocess.CompletedProcess:
    """Run the agent-creation PowerShell script with the supplied arguments."""
    return subprocess.run(
        [pwsh, "-NoProfile", "-NonInteractive", "-File", str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


# The command writes a skill file containing the supplied metadata, instructions, and boundaries.
def test_writes_valid_skill_md(tmp_path):
    """The command writes a skill file containing the supplied metadata, instructions, and boundaries."""
    out = tmp_path / "example-skill" / "SKILL.md"
    result = run_script([
        "-SkillName", "example-skill",
        "-SkillDescription", "Does one clearly bounded thing.",
        "-Instructions", "## Purpose\n\nDoes the thing.",
        "-InputBoundary", "One target per invocation.",
        "-ProhibitedScope", "Read-only; no write actions.",
        "-OutputPath", str(out),
    ])
    assert result.returncode == 0, result.stderr
    content = out.read_text()
    assert "name: example-skill" in content
    assert "description: Does one clearly bounded thing." in content
    assert "Does the thing." in content
    assert "One target per invocation." in content
    assert "Read-only; no write actions." in content


# Skill creation rejects a name that violates the skill-name format.
def test_rejects_invalid_skill_name(tmp_path):
    """Skill creation rejects a name that violates the skill-name format."""
    out = tmp_path / "SKILL.md"
    result = run_script([
        "-SkillName", "Not Valid Name",
        "-SkillDescription", "x",
        "-Instructions", "x",
        "-OutputPath", str(out),
    ])
    assert result.returncode != 0
    assert not out.exists()


# Skill creation rejects requests without inline or file-based instructions.
def test_requires_instructions_source(tmp_path):
    """Skill creation rejects requests without inline or file-based instructions."""
    out = tmp_path / "SKILL.md"
    result = run_script([
        "-SkillName", "example-skill",
        "-SkillDescription", "x",
        "-OutputPath", str(out),
    ])
    assert result.returncode != 0
    assert not out.exists()


# An existing skill file is preserved unless overwrite is explicitly requested.
def test_refuses_to_overwrite_without_flag(tmp_path):
    """An existing skill file is preserved unless overwrite is explicitly requested."""
    out = tmp_path / "SKILL.md"
    out.write_text("existing content")
    result = run_script([
        "-SkillName", "example-skill",
        "-SkillDescription", "x",
        "-Instructions", "x",
        "-OutputPath", str(out),
    ])
    assert result.returncode != 0
    assert out.read_text() == "existing content"


# The overwrite flag replaces an existing skill file with the new instructions.
def test_overwrite_flag_allows_replace(tmp_path):
    """The overwrite flag replaces an existing skill file with the new instructions."""
    out = tmp_path / "SKILL.md"
    out.write_text("existing content")
    result = run_script([
        "-SkillName", "example-skill",
        "-SkillDescription", "x",
        "-Instructions", "new body",
        "-OutputPath", str(out),
        "-Overwrite",
    ])
    assert result.returncode == 0, result.stderr
    assert "new body" in out.read_text()
