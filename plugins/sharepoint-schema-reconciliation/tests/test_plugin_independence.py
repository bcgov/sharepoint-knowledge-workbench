"""
test_plugin_independence.py
===========================

Purpose:
    Plugin-wide independence and genericity gates required by the Phase 9 spec
    sections 9 (genericity contract), 13 (security/write boundary) and 14
    (independence verification): no project literals, no source-repository
    dependency, no live tenant identifiers, and no live tenant transport
    anywhere in the shipped tree.

Layer: sharepoint-provisioning / tests
"""

import re
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]

PROJECT_LITERALS = [__import__("base64").b64decode(x).decode() for x in [
    "SlVTVElO", "Q0VJUw==", "T1JEUw==", "Y291cnRob3VzZQ==", "QUctQ1NC", "QUctQkNQUw==", "QUctUFNTRw==",
    "SVRBVQ==", "UElP", "SUNICg==", "Q3Jvd25OZXQ=", "TWVkaWFJbmZv", "U1AyMDE2LU1lZGlhSW5mbw==",
    "amFnLmdvdi5iYy5jYQ==", "YmNnb3Yuc2hhcmVwb2ludC5jb20=", "Y21hdA==", "SkFHLUNTQg==",
    "TW9kZXJuX01hbnVhbF9BcHBlYXJhbmNlcw==", "TW9kZXJuX1NjaGVkdWxlZF9BcHBlYXJhbmNlcw==",
]]

SOURCE_REPO_MARKERS = [
    __import__("base64").b64decode("amFnLWNzYi1jbWF0LXNoYXJlcG9pbnQtb25saW5l").decode(),
    "sharepoint-migration",
    "ords-integration-migration",
]


def _shipped_files():
    """Yield the files this plugin actually ships at runtime (excludes
    ``tests/`` -- see sharepoint-link-remediation's identical exclusion
    rationale: this module's own PROJECT_LITERALS list would otherwise fail
    the scan on itself)."""
    for path in sorted(PLUGIN_ROOT.rglob("*")):
        if not path.is_file():
            continue
        parts = path.relative_to(PLUGIN_ROOT).parts
        if "__pycache__" in parts or path.suffix in {".pyc"}:
            continue
        if ".pytest_cache" in parts or ".egg-info" in " ".join(parts):
            continue
        if "tests" in parts:
            continue
        yield path


def test_runtime_tree_is_literal_free_scan_is_not_vacuous():
    runtime = list(_shipped_files())
    assert runtime, "genericity scan found no runtime files -- gate is vacuous"
    assert any(path.suffix == ".py" for path in runtime), (
        "genericity scan covers no Python modules -- gate is vacuous"
    )


@pytest.mark.parametrize("literal", PROJECT_LITERALS)
def test_no_project_literal_anywhere_in_the_plugin(literal):
    if re.fullmatch(r"[\w.-]+", literal) and "." in literal:
        pattern = re.compile(re.escape(literal), re.IGNORECASE)
    else:
        pattern = re.compile(rf"\b{re.escape(literal)}\b", re.IGNORECASE)

    offenders = []
    for path in _shipped_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        if pattern.search(text):
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
    for module in (
        "provisioning_outcomes",
        "field_provisioning",
        "content_type_provisioning",
        "list_provisioning",
    ):
        importlib.import_module(module)


def test_no_module_lives_only_inside_a_skill_directory():
    """Hub-and-spoke: every file under skills/ must be a symlink back to the
    plugin root, never the only real copy (self-evolution Hard Gate #12)."""
    offenders = []
    for path in (PLUGIN_ROOT / "skills").rglob("*"):
        if path.is_file() and not path.is_symlink() and path.name not in {"SKILL.md", "evals.json"}:
            offenders.append(str(path.relative_to(PLUGIN_ROOT)))

    assert offenders == []


def test_no_live_pnp_or_csom_or_network_transport_ships():
    """Zero tenant I/O ships in this plugin (Phase 9 spec s13, task hard
    requirement #2): no PnP/CSOM call, no raw network call, anywhere in the
    runtime script/code tree -- scans all code files (.py, .ps1, .sh), and bans
    every PnP write-verb prefix, not an enumerable cmdlet list that goes
    stale as new executors are written elsewhere in this ecosystem."""
    forbidden_exact = [
        "Connect-PnPOnline", "Get-PnPContext", "New-ClientContext",
        "requests.get", "requests.post", "urllib.request", "http.client",
        "socket.socket",
    ]
    forbidden_prefixes = ["Add-PnP", "New-PnP", "Set-PnP", "Remove-PnP", "Invoke-PnPSPRestMethod"]
    offenders = []
    for path in sorted(PLUGIN_ROOT.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in {".py", ".ps1", ".sh", ".cmd", ".bat"}:
            continue
        parts = path.relative_to(PLUGIN_ROOT).parts
        if "__pycache__" in parts or path.suffix in {".pyc"}:
            continue
        if ".pytest_cache" in parts or ".egg-info" in " ".join(parts):
            continue
        if "tests" in parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for call in forbidden_exact:
            if call in text:
                offenders.append(f"{path.relative_to(PLUGIN_ROOT)}: {call}")
        for prefix in forbidden_prefixes:
            for match in re.finditer(re.escape(prefix) + r"[A-Za-z]+", text):
                offenders.append(f"{path.relative_to(PLUGIN_ROOT)}: {match.group()}")

    assert offenders == []


