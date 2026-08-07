"""
test_plugin_independence.py
===========================

Purpose:
    Plugin-wide independence and genericity gates required by the Phase 9 spec
    sections 9 (genericity contract), 13 (security/write boundary) and 14
    (independence verification): no project literals, no source-repository
    dependency, no live tenant identifiers anywhere in the shipped tree.

Layer: sharepoint-link-remediation / tests
"""

from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]

PROJECT_LITERALS = [
    "JUSTIN", "CEIS", "ORDS", "courthouse", "AG-CSB", "AG-BCPS", "AG-PSSG",
    "ITAU", "PIO", "ICM", "CrownNet", "MediaInfo", "SP2016-MediaInfo",
    "jag.gov.bc.ca", "bcgov.sharepoint.com", "cmat",
]

SOURCE_REPO_MARKERS = [
    "jag-csb-cmat-sharepoint-online",
    "sharepoint-migration",
    "link-conversion",
]


def _shipped_files():
    for path in sorted(PLUGIN_ROOT.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix in {".pyc"}:
            continue
        yield path


@pytest.mark.parametrize("literal", PROJECT_LITERALS)
def test_no_project_literal_anywhere_in_the_plugin(literal):
    offenders = []
    for path in _shipped_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        if literal.lower() in text.lower():
            offenders.append(str(path.relative_to(PLUGIN_ROOT)))

    assert offenders == [], f"project literal {literal!r} found in: {offenders}"


@pytest.mark.parametrize("marker", SOURCE_REPO_MARKERS)
def test_no_runtime_reference_to_the_source_repository(marker):
    offenders = []
    for path in _shipped_files():
        if path.suffix not in {".py", ".json", ".toml", ".yaml"}:
            continue
        if marker in path.read_text(encoding="utf-8", errors="ignore"):
            offenders.append(str(path.relative_to(PLUGIN_ROOT)))

    assert offenders == [], f"source-repository marker {marker!r} found in: {offenders}"


def test_no_guid_shaped_identifier_is_shipped():
    import re

    guid = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.IGNORECASE)
    offenders = [
        str(path.relative_to(PLUGIN_ROOT))
        for path in _shipped_files()
        if guid.search(path.read_text(encoding="utf-8", errors="ignore"))
    ]

    assert offenders == []


def test_every_script_module_imports_with_no_third_party_dependency():
    import importlib
    import sys

    sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))
    for module in ("link_outcomes", "link_rules", "link_extraction", "link_remediation", "link_integrity"):
        importlib.import_module(module)


def test_no_module_lives_only_inside_a_skill_directory():
    """Hub-and-spoke: every file under skills/ must be a symlink back to the
    plugin root, never the only real copy (self-evolution Hard Gate #12)."""
    offenders = []
    for path in (PLUGIN_ROOT / "skills").rglob("*"):
        if path.is_file() and not path.is_symlink() and path.name != "SKILL.md":
            offenders.append(str(path.relative_to(PLUGIN_ROOT)))

    assert offenders == []
