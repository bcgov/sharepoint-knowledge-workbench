"""
test_genericity_and_independence.py -- mutation-style detectors for the
genericity contract, independence, and the read-only write boundary for schema
analysis modules in sharepoint-discovery.

Purpose:
    These are the tests that must fail if a future change reintroduces a
    project literal or a tenant write path into the schema analysis tools.
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

PROJECT_LITERALS = (
    "JUSTIN", "CEIS", "ORDS", "courthouse", "AG-CSB", "PIO", "ICM",
    "cmat", "wave-dependency-matrix", "choices-overrides",
    "raw_exports_prod", "raw_export_test",
)


def _literal_pattern(literal: str) -> re.Pattern:
    return re.compile(
        r"(?<![A-Za-z0-9])" + re.escape(literal) + r"(?![A-Za-z0-9])", re.IGNORECASE
    )


GUID_RE = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
TENANT_URL_RE = re.compile(r"https?://[\w.-]*(sharepoint\.com|gov\.bc\.ca)", re.IGNORECASE)

WRITE_TOKENS = (
    "Remove-PnPField", "Set-PnPField", "Add-PnPField", "Remove-PnPList",
    "Add-PnPContentType", "Remove-PnPContentType", "Set-PnPList",
    "requests.post", "requests.put", "requests.delete", "requests.patch",
    "shutil.rmtree", "os.remove",
)

SCHEMA_SCRIPTS = [
    "calculated_columns.py",
    "choice_fields.py",
    "duplicate_fields.py",
    "schema_definition.py",
    "schema_diff.py",
    "schema_export.py",
]


def test_no_project_literal_in_schema_scripts():
    offenders = []
    for script_name in SCHEMA_SCRIPTS:
        path = PLUGIN_ROOT / "scripts" / script_name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for literal in PROJECT_LITERALS:
            if _literal_pattern(literal).search(text):
                offenders.append(f"{script_name}: {literal}")
    assert not offenders, offenders


def test_no_tenant_write_path_in_schema_scripts():
    offenders = []
    for script_name in SCHEMA_SCRIPTS:
        path = PLUGIN_ROOT / "scripts" / script_name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for token in WRITE_TOKENS:
            if token in text:
                offenders.append(f"{script_name}: {token}")
    assert not offenders, offenders


def test_neutral_fixtures_drive_a_full_comparison():
    baseline = load_schema_export(FIXTURES / "baseline", label="baseline")
    candidate = load_schema_export(FIXTURES / "candidate", label="candidate")
    assert baseline.status is SectionStatus.OBSERVED
    assert candidate.status is SectionStatus.OBSERVED
    diff = compare_schema_exports(baseline, candidate)
"""
test_genericity_and_independence.py -- mutation-style detectors for the
genericity contract, independence, and the read-only write boundary for schema
analysis modules in sharepoint-discovery.

Purpose:
    These are the tests that must fail if a future change reintroduces a
    project literal or a tenant write path into the schema analysis tools.
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

PROJECT_LITERALS = (
    "JUSTIN", "CEIS", "ORDS", "courthouse", "AG-CSB", "PIO", "ICM",
    "cmat", "wave-dependency-matrix", "choices-overrides",
    "raw_exports_prod", "raw_export_test",
)


def _literal_pattern(literal: str) -> re.Pattern:
    return re.compile(
        r"(?<![A-Za-z0-9])" + re.escape(literal) + r"(?![A-Za-z0-9])", re.IGNORECASE
    )


GUID_RE = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
TENANT_URL_RE = re.compile(r"https?://[\w.-]*(sharepoint\.com|gov\.bc\.ca)", re.IGNORECASE)

WRITE_TOKENS = (
    "Remove-PnPField", "Set-PnPField", "Add-PnPField", "Remove-PnPList",
    "Add-PnPContentType", "Remove-PnPContentType", "Set-PnPList",
    "requests.post", "requests.put", "requests.delete", "requests.patch",
    "shutil.rmtree", "os.remove",
)

SCHEMA_SCRIPTS = [
    "calculated_columns.py",
    "choice_fields.py",
    "duplicate_fields.py",
    "schema_definition.py",
    "schema_diff.py",
    "schema_export.py",
]


def test_no_project_literal_in_schema_scripts():
    offenders = []
    for script_name in SCHEMA_SCRIPTS:
        path = PLUGIN_ROOT / "scripts" / script_name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for literal in PROJECT_LITERALS:
            if _literal_pattern(literal).search(text):
                offenders.append(f"{script_name}: {literal}")
    assert not offenders, offenders


def test_no_tenant_write_path_in_schema_scripts():
    offenders = []
    for script_name in SCHEMA_SCRIPTS:
        path = PLUGIN_ROOT / "scripts" / script_name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for token in WRITE_TOKENS:
            if token in text:
                offenders.append(f"{script_name}: {token}")
    assert not offenders, offenders


def test_neutral_fixtures_drive_a_full_comparison():
    baseline = load_schema_export(FIXTURES / "baseline", label="baseline")
    candidate = load_schema_export(FIXTURES / "candidate", label="candidate")
    assert baseline.status is SectionStatus.OBSERVED
    assert candidate.status is SectionStatus.OBSERVED
    report = compare_schema_exports(baseline, candidate)
    assert report.site_columns.only_left == ("retired_code",)
    assert report.site_columns.only_right == ("region",)
    rendered = render_markdown(report)
    assert "Schema Comparison" in rendered



def test_neutral_fixtures_drive_duplicate_and_choice_audits():
    candidate = load_schema_export(FIXTURES / "candidate", label="candidate")
    duplicates = find_duplicate_fields(candidate)
    assert [g.display_name for g in duplicates.groups] == ["Region"]
    choices = inventory_choice_fields(candidate)
    assert len(choices.ambiguities) == 0
    assert [f.internal_name for f in choices.fields] == ["status"]
    assert choices.fields[0].choices == ("Draft", "Published")
