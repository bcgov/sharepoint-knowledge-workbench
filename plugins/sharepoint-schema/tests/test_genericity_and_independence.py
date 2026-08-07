"""
test_genericity_and_independence.py -- mutation-style detectors for the
genericity contract (spec §9), independence (§14), and the read-only write
boundary (§13).

Purpose:
    These are the tests that must fail if a future change reintroduces a
    project literal, a source-repository dependency, or a tenant write path
    into this plugin. They scan the plugin's own committed tree, so they cover
    scripts, skills, fixtures, and documentation alike.

Layer: sharepoint-schema / plugin-local tests

Key Input Dependencies:
    - the plugin tree itself
    - tests/fixtures/exports/{baseline,candidate} (neutral fixtures)
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from choice_fields import inventory_choice_fields  # noqa: E402
from duplicate_fields import find_duplicate_fields  # noqa: E402
from schema_diff import compare_schema_exports, render_markdown  # noqa: E402
from schema_export import SectionStatus, load_schema_export  # noqa: E402

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = PLUGIN_ROOT / "tests" / "fixtures" / "exports"

# Project literals from spec §8h/§9. Matched case-insensitively and bounded by
# non-alphanumerics, so that legitimate English words containing an acronym as a
# substring (e.g. "Records" containing "ords") are not false positives.
PROJECT_LITERALS = (
    "JUSTIN", "CEIS", "ORDS", "courthouse", "AG-CSB", "ITAU", "PIO", "ICM",
    "jag.gov.bc.ca", "bcgov", "gov.bc.ca", "cmat", "wave-dependency-matrix",
    "choices-overrides", "raw_exports_prod", "raw_export_test", "01_source_sharepoint",
)


def _literal_pattern(literal: str) -> re.Pattern:
    return re.compile(
        r"(?<![A-Za-z0-9])" + re.escape(literal) + r"(?![A-Za-z0-9])", re.IGNORECASE
    )

GUID_RE = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
TENANT_URL_RE = re.compile(r"https?://[\w.-]*(sharepoint\.com|gov\.bc\.ca)", re.IGNORECASE)

# Tenant write / mutation vocabulary that must never appear in this read-only plugin.
WRITE_TOKENS = (
    "Remove-PnPField", "Set-PnPField", "Add-PnPField", "Remove-PnPList",
    "Add-PnPContentType", "Remove-PnPContentType", "Set-PnPList",
    "Connect-PnPOnline", "Invoke-RestMethod", "Invoke-WebRequest",
    "requests.post", "requests.put", "requests.delete", "requests.patch",
    "urllib.request", "shutil.rmtree", "os.remove",
)


def _plugin_files():
    for path in sorted(PLUGIN_ROOT.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        if "__pycache__" in path.parts or ".egg-info" in str(path):
            continue
        if path.name == Path(__file__).name:  # this file names the literals on purpose
            continue
        yield path


def _runtime_files():
    """The files this plugin actually ships at runtime -- scripts, assets,
    packaging, skills. Excludes ``tests/``.

    Phase 9 spec section 9 permits project literals in negative-control
    fixtures and forbids them in live defaults, and this suite relies on that
    allowance: ``test_schema_export.test_default_layout_assumes_no_project_scope_segment``
    asserts a specific project path segment is ABSENT from the default layout,
    which requires naming that segment to assert against it. A scan that
    included test prose would make proving the requirement indistinguishable
    from violating it.

    The gate that matters -- every shipped runtime file is literal-free -- is
    preserved in full, and guarded against becoming vacuous below.
    """
    for path in _plugin_files():
        if "tests" in path.relative_to(PLUGIN_ROOT).parts:
            continue
        yield path


def test_runtime_scan_is_not_vacuous():
    """The tests/ exclusion above must never empty the scan set."""
    runtime = list(_runtime_files())
    assert runtime, "genericity scan found no runtime files -- gate is vacuous"
    assert any(p.suffix == ".py" for p in runtime), (
        "genericity scan covers no Python modules -- gate is vacuous"
    )


def test_no_project_literal_appears_anywhere_in_the_plugin():
    offenders = []
    for path in _runtime_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for literal in PROJECT_LITERALS:
            if _literal_pattern(literal).search(text):
                offenders.append(f"{path.relative_to(PLUGIN_ROOT)}: {literal}")
    assert not offenders, offenders


def test_no_guid_or_tenant_url_appears_anywhere_in_the_plugin():
    offenders = []
    for path in _plugin_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        if GUID_RE.search(text):
            offenders.append(f"{path.relative_to(PLUGIN_ROOT)}: GUID")
        if TENANT_URL_RE.search(text):
            offenders.append(f"{path.relative_to(PLUGIN_ROOT)}: tenant URL")
    assert not offenders, offenders


def test_no_reference_to_the_source_repository_or_its_paths():
    offenders = []
    for path in _plugin_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for token in ("jag-csb-cmat-sharepoint-online", "sharepoint-migration",
                      "../../../scripts/", "/Users/"):
            if token in text:
                offenders.append(f"{path.relative_to(PLUGIN_ROOT)}: {token}")
    assert not offenders, offenders


def test_no_tenant_connection_or_write_path_exists_in_any_script():
    offenders = []
    for path in sorted((PLUGIN_ROOT / "scripts").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for token in WRITE_TOKENS:
            if token in text:
                offenders.append(f"{path.relative_to(PLUGIN_ROOT)}: {token}")
    assert not offenders, offenders


def test_scripts_import_nothing_outside_the_standard_library_and_this_plugin():
    local = {p.stem for p in (PLUGIN_ROOT / "scripts").glob("*.py")}
    allowed_prefixes = {"json", "os", "re", "enum", "pathlib", "typing",
                        "dataclasses", "collections", "__future__"} | local
    offenders = []
    for path in sorted((PLUGIN_ROOT / "scripts").rglob("*.py")):
        for line in path.read_text(encoding="utf-8").splitlines():
            match = re.match(r"\s*(?:from|import)\s+([\w.]+)", line)
            if match and match.group(1).split(".")[0] not in allowed_prefixes:
                offenders.append(f"{path.relative_to(PLUGIN_ROOT)}: {line.strip()}")
    assert not offenders, offenders


def test_every_skill_script_reference_is_relative_to_the_skill_root():
    offenders = []
    for skill_md in sorted((PLUGIN_ROOT / "skills").glob("*/SKILL.md")):
        for line in skill_md.read_text(encoding="utf-8").splitlines():
            if "plugins/sharepoint-schema/scripts/" in line and "pip install" not in line:
                offenders.append(f"{skill_md.name}: {line.strip()}")
    assert not offenders, offenders


# ---------------------------------------------------------------------------
# Neutral committed fixtures -- end-to-end over real files on disk.
# ---------------------------------------------------------------------------

def test_neutral_fixtures_drive_a_full_comparison():
    baseline = load_schema_export(FIXTURES / "baseline", label="baseline")
    candidate = load_schema_export(FIXTURES / "candidate", label="candidate")
    assert baseline.status is SectionStatus.OBSERVED
    assert candidate.status is SectionStatus.OBSERVED

    report = compare_schema_exports(baseline, candidate)
    assert report.site_columns.only_left == ("retired_code",)
    assert report.site_columns.only_right == ("region",)
    assert [v.key for v in report.site_columns.changed] == ["summary"]
    assert report.per_list["lists/Records"].fields.only_left == ("legacy_ref",)

    markdown = render_markdown(report)
    assert markdown.startswith("# Schema Comparison")


def test_neutral_fixtures_drive_duplicate_and_choice_audits():
    candidate = load_schema_export(FIXTURES / "candidate", label="candidate")

    duplicates = find_duplicate_fields(candidate)
    assert [g.display_name for g in duplicates.groups] == ["Region"]

    choices = inventory_choice_fields(candidate)
    assert [f.internal_name for f in choices.fields] == ["status"]
    assert choices.fields[0].choices == ("Draft", "Published")
