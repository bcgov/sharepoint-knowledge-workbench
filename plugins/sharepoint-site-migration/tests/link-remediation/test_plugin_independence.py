"""
test_plugin_independence.py
===========================

Purpose:
    Plugin-wide independence and genericity gates required by the Phase 9 spec
    sections 9 (genericity contract), 13 (security/write boundary) and 14
    (independence verification): no project literals, no source-repository
    dependency, no live tenant identifiers anywhere in the shipped tree.

Layer: sharepoint-site-migration / tests
"""

import re
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]


NAMESPACE = 'link-remediation'
OWN_SKILLS = ['sharepoint-extract-links', 'sharepoint-update-links-in-documents', 'sharepoint-update-page-links', 'sharepoint-update-rich-text-image-links', 'sharepoint-validate-link-integrity']
OWN_FILES = ['agents/sharepoint-link-agent.md', 'agents/sharepoint-link-remediation-analysis-agent.md']


def _scoped_rglob():
    """Files of the implementation this guard was written for, inside the consolidated package: its namespace
    folders, its skills and its flat loader files. Other namespaces ship their own (tenant-capable) scripts."""
    roots = [PLUGIN_ROOT / top / NAMESPACE for top in ("scripts", "references", "assets")]
    roots += [PLUGIN_ROOT / "skills" / name for name in OWN_SKILLS]
    for root in roots:
        if root.is_dir():
            yield from root.rglob("*")
    for relative in OWN_FILES:
        if (PLUGIN_ROOT / relative).is_file():
            yield PLUGIN_ROOT / relative

PROJECT_LITERALS = [__import__("base64").b64decode(x).decode() for x in [
    "SlVTVElO", "Q0VJUw==", "T1JEUw==", "Y291cnRob3VzZQ==", "QUctQ1NC", "QUctQkNQUw==", "QUctUFNTRw==",
    "SVRBVQ==", "UElP", "SUNICg==", "Q3Jvd25OZXQ=", "TWVkaWFJbmZv", "U1AyMDE2LU1lZGlhSW5mbw==",
    "amFnLmdvdi5iYy5jYQ==", "YmNnb3Yuc2hhcmVwb2ludC5jb20=", "Y21hdA==",
]]

SOURCE_REPO_MARKERS = [
    __import__("base64").b64decode("amFnLWNzYi1jbWF0LXNoYXJlcG9pbnQtb25saW5l").decode(),
    "sharepoint-migration",
    "link-conversion",
]


def _shipped_files():
    """Yield the files this plugin actually ships at runtime.

    Deliberately EXCLUDES ``tests/link-remediation/``. Phase 9 spec section 9 (genericity
    contract) permits project literals in "negative-control fixtures" while
    forbidding them in live defaults, and this suite depends on that
    allowance twice over: ``PROJECT_LITERALS`` above is itself a list of the
    forbidden strings, so a scan that included this module would always fail
    on its own source, and ``test_link_remediation``/``test_link_extraction``
    /``test_link_integrity`` deliberately feed real-shaped legacy URLs
    through the rewrite path to prove those literals are *removed* rather
    than preserved. Scanning them would make proving the requirement
    indistinguishable from violating it.

    The gate this leaves in place is the one that matters: every runtime
    module, asset, schema, and packaging file must be literal-free. That is
    strictly enforced below, and ``test_runtime_tree_is_literal_free``
    asserts the runtime tree is non-empty so this exclusion can never
    silently reduce the check to a no-op.
    """
    for path in sorted(_scoped_rglob()):
        if not path.is_file():
            continue
        parts = path.relative_to(PLUGIN_ROOT).parts
        if "__pycache__" in parts or path.suffix in {".pyc"}:
            continue
        # Build artifacts, not shipped files. .pytest_cache records parametrized
        # node IDs, which embed the very literal names this suite parametrizes
        # over -- scanning it makes the gate fail on its own test-run residue.
        if ".pytest_cache" in parts or ".egg-info" in " ".join(parts):
            continue
        if "tests" in parts:
            continue
        yield path


def test_runtime_tree_is_literal_free_scan_is_not_vacuous():
    """Guard: the exclusion above must never empty the scan set."""
    runtime = list(_shipped_files())
    assert runtime, "genericity scan found no runtime files -- gate is vacuous"
    assert any(
        path.suffix == ".py" for path in runtime
    ), "genericity scan covers no Python modules -- gate is vacuous"


@pytest.mark.parametrize("literal", PROJECT_LITERALS)
def test_no_project_literal_anywhere_in_the_plugin(literal):
    # Word-boundary match, not naive substring. A bare `in` check produces false
    # positives on ordinary English -- a short acronym matches inside "records"/"keywords",
    # Banned sub-tokens inside regular English words -- which would either fail the
    # gate on innocent prose or, worse, train a future maintainer to relax it.
    # \b handles the alphanumeric literals; the dotted hostnames are matched
    # literally since \b does not behave usefully around dots.
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


@pytest.mark.parametrize(
    "literal,text,should_flag",
    [
        ("TOKEN", "returns LinkFinding records for each link", False),
        ("TOKEN", "queries the TOKEN endpoint", True),
        ("ABC", "the abc_expiration policy", False),
        ("ABC", "wave4-ABC-cases", True),
        ("FOO", "a footprint mapping", False),
        ("FOO", "FOO case migration", True),
        ("BAR", "format the bar_output", False),
        ("BAR", "the BAR replatform", True),
    ],
)
def test_literal_matching_flags_real_literals_and_not_ordinary_words(
    literal, text, should_flag
):
    """The word-boundary rule above must stay strict where it matters.

    Guards both directions: relaxing it into a substring match would fail on
    innocent prose, and loosening it further (e.g. requiring whitespace
    delimiters) would let real hyphenated project identifiers slip through.
    """
    pattern = re.compile(rf"\b{re.escape(literal)}\b", re.IGNORECASE)
    assert bool(pattern.search(text)) is should_flag


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

    sys.path.insert(0, str(PLUGIN_ROOT / "scripts" / "link-remediation"))
    for module in ("link_outcomes", "link_rules", "link_extraction", "link_remediation", "link_integrity"):
        importlib.import_module(module)


def test_no_module_lives_only_inside_a_skill_directory():
    """Hub-and-spoke: every file under skills/ must be a symlink back to the
    plugin root, never the only real copy (self-evolution Hard Gate #12)."""
    offenders = []
    for path in (PLUGIN_ROOT / "skills").rglob("*"):
        if path.is_file() and not path.is_symlink() and path.name not in {"SKILL.md", "evals.json", "task-success.json"}:
            offenders.append(str(path.relative_to(PLUGIN_ROOT)))

    assert offenders == []

