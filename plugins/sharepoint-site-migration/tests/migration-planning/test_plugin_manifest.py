"""
test_plugin_manifest.py -- guards against plugin.yaml's `skills:` list
silently drifting out of sync with the skills actually shipped on disk.

Purpose:
    An external audit (2026-08-08) found four plugins across this workbench
    where plugin.yaml declared fewer skills than skills/ actually contained
    -- e.g. this plugin declared 2 skills while shipping 4. Any loader that
    trusts plugin.yaml.skills as the authoritative list would silently never
    load the undeclared skills. This test makes that class of drift a hard
    failure instead of a silent gap.

    Parses plugin.yaml's flat `skills:` list with plain string handling
    rather than importing PyYAML -- this plugin ships zero runtime
    dependencies (pyproject.toml `dependencies = []`) and a test importing a
    package the isolated wheel install doesn't have would break that
    contract's own verification.

Layer: sharepoint-schema / plugin-local tests

Key Input Dependencies: plugin.yaml, SKILL.md.
"""

import re
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]


def _declared_skills(plugin_yaml_text: str) -> set[str]:
    """Extract the flat `skills:` list's item names. Stops at the next
    top-level (non-indented) key, so a following `agents:` block is never
    absorbed into the skills set."""
    match = re.search(r"^skills:\n((?:[ \t]+-.*\n?)*)", plugin_yaml_text, re.MULTILINE)
    if not match:
        return set()
    return {line.strip().lstrip("-").strip() for line in match.group(1).splitlines() if line.strip()}


def test_plugin_yaml_skills_matches_skills_directory():
    """Verify plugin yaml skills matches skills directory."""
    declared = _declared_skills((PLUGIN_ROOT / "plugin.yaml").read_text(encoding="utf-8"))
    on_disk = {
        p.name
        for p in (PLUGIN_ROOT / "skills").iterdir()
        if p.is_dir() and (p / "SKILL.md").is_file()
    }
    assert declared == on_disk, (
        f"plugin.yaml skills list has drifted from skills/ on disk -- "
        f"missing from plugin.yaml: {on_disk - declared}; "
        f"declared but not shipped: {declared - on_disk}"
    )
