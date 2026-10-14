"""Contract tests for the sharepoint-develop-spfx-application-customizer skill.

Purpose:
    Verifies the skill's wiring (manifests, symlinks, evals) and the safety
    contract of register-application-customizer.ps1 (dry-run default,
    confirmation token, JSON validation) without touching any tenant.

Key Input Dependencies:
    - plugins/sharepoint-spfx-development/plugin.json, plugin.yaml
    - plugin-retention.json and symlinks.json at the repo root
    - scripts/register-application-customizer.ps1 (read as text)

Index:
    - test_skill_files_exist
    - test_skill_registered_in_manifests
    - test_script_symlinks_registered
    - test_script_safety_contract
    - test_evals_are_valid_json
"""

import json
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
REPO = PLUGIN.parents[1]
SKILL_NAME = "sharepoint-develop-spfx-application-customizer"
SKILL = PLUGIN / "skills" / SKILL_NAME
SCRIPT = PLUGIN / "scripts" / "register-application-customizer.ps1"


def test_skill_files_exist() -> None:
    """The skill ships SKILL.md, references and evals."""
    assert (SKILL / "SKILL.md").is_file()
    assert any((SKILL / "references").glob("*.md"))
    assert (SKILL / "evals" / "evals.json").is_file()


def test_skill_registered_in_manifests() -> None:
    """plugin.json, plugin.yaml and plugin-retention.json all list the skill."""
    manifest = json.loads((PLUGIN / "plugin.json").read_text(encoding="utf-8"))
    assert SKILL_NAME in manifest["skills"]
    assert f"- {SKILL_NAME}" in (PLUGIN / "plugin.yaml").read_text(encoding="utf-8")
    retention = json.loads((REPO / "plugin-retention.json").read_text(encoding="utf-8"))
    assert retention["plugins"]["sharepoint-spfx-development"]["skills"][SKILL_NAME] is True


def test_script_symlinks_registered() -> None:
    """Both skill-local scripts are recorded in symlinks.json."""
    links = json.loads((REPO / "symlinks.json").read_text(encoding="utf-8"))
    entries = links["links"] if isinstance(links, dict) else links
    dsts = {e["dst"].replace("\\", "/") for e in entries}
    for name in ("check-spfx-toolchain.ps1", "register-application-customizer.ps1"):
        assert f"plugins/sharepoint-spfx-development/skills/{SKILL_NAME}/scripts/{name}" in dsts


def test_script_safety_contract() -> None:
    """Writes require -Execute plus the confirmation token; JSON is validated."""
    text = SCRIPT.read_text(encoding="utf-8")
    assert "REGISTER-SPO-APPCUSTOMIZER" in text
    assert "$Execute" in text
    assert "ConvertFrom-Json" in text
    assert "ClientSideExtension.ApplicationCustomizer" in text


def test_evals_are_valid_json() -> None:
    """Eval files parse as JSON."""
    for name in ("evals.json", "task-success.json"):
        json.loads((SKILL / "evals" / name).read_text(encoding="utf-8"))
