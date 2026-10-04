"""
test_audit_generic.py

Purpose:
    The list-content audit scripts must work for any site. A small, unrelated "second site" (Orders -> Customers) is described only
    through an audit config; the identity mapper and the variance analyzer must use that config and nothing else, and their
    reports must not carry anything from the site they were first written for.

Layer: plugins/sharepoint-site-migration -- tests
"""

import csv
import shutil
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

AUDIT = Path(__file__).resolve().parents[2] / "scripts" / "content-migration" / "content-audit"


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), AUDIT / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def second_site(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    # Customers were re-migrated: source IDs 1,2 became target IDs 11,12; matched on Title, then on Email.
    write_csv(data / "Customers-sp2016-onprem.csv", [
        {"ID": "1", "Title": "ACME", "Email": "a@example.org"},
        {"ID": "2", "Title": "", "Email": "b@example.org"},
        {"ID": "3", "Title": "GHOST", "Email": ""},
    ])
    write_csv(data / "Customers-spo-prod.csv", [
        {"ID": "11", "Title": "acme", "Email": "x@example.org"},
        {"ID": "12", "Title": "Other", "Email": "B@EXAMPLE.ORG"},
    ])
    config = tmp_path / "audit-config.json"
    config.write_text(json.dumps({
        "id_pattern": "^ORD-[0-9]+$", "key_columns": ["Title"],
        "identity_mapping": {"list": "Customers", "tiers": [
            {"name": "T1_Title", "columns": ["Title"]}, {"name": "T2_Email", "columns": ["Email"]}]},
        "lookups": {"Orders": {"Customer": ["CustomerId", "Customers"]}},
    }))
    return data, config, tmp_path


def test_identity_mapper_uses_the_configured_tiers_in_order(second_site):
    data, config, tmp = second_site
    out = tmp / "map.json"
    result = subprocess.run([sys.executable, str(AUDIT / "analyze-list-mapping-assurance.py"), "--audit-config", str(config),
                             "--data-dir", str(data), "--out-map", str(out)], capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert json.loads(out.read_text()) == {"1": 11, "2": 12}      # ID 3 has no counterpart
    assert "T1_Title" in result.stdout and "T2_Email" in result.stdout
    assert "Unmatched / dropped: 1" in result.stdout


def test_identity_mapper_fails_clearly_when_exports_are_missing(second_site):
    data, config, tmp = second_site
    (data / "Customers-spo-prod.csv").unlink()
    result = subprocess.run([sys.executable, str(AUDIT / "analyze-list-mapping-assurance.py"), "--audit-config", str(config),
                             "--data-dir", str(data), "--out-map", str(tmp / "map.json")], capture_output=True, text=True, timeout=60)
    assert result.returncode == 2 and "export-list-content-pairs.ps1 -ListName Customers" in result.stdout
    assert not (tmp / "map.json").exists()


def test_match_rows_ignores_rows_with_an_empty_key_column():
    mapper = load("analyze-list-mapping-assurance.py")
    ids, per_tier, unmatched = mapper.match_rows(
        [{"ID": "1", "Title": ""}], [{"ID": "9", "Title": ""}], [{"name": "T1", "columns": ["Title"]}])
    assert ids == {} and unmatched == 1 and per_tier == {"T1": 0}


@pytest.mark.parametrize("script", ["analyze-lookup-variances.py", "analyze-all-variances.py"])
def test_variance_analyzer_runs_from_the_config_alone(second_site, script):
    data, config, tmp = second_site
    write_csv(data / "Orders-sp2016-onprem.csv", [{"ID": "5", "Title": "ORD-1", "CustomerId": "1"}])
    write_csv(data / "Orders-spo-prod.csv", [{"ID": "5", "Title": "ORD-1", "Customer": "11"}])
    mapping = tmp / "id-mapping.json"
    mapping.write_text(json.dumps({"1": 11}))
    md, out_csv = tmp / "report.md", tmp / "report.csv"
    result = subprocess.run([sys.executable, str(AUDIT / script), "--data-dir", str(data), "--audit-config", str(config),
                             "--mapping-path", str(mapping), "--output-md", str(md), "--output-csv", str(out_csv), "--console-log", str(tmp / "console.md"), "--list-name", "ALL"],
                            capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stdout + result.stderr
    text = md.read_text(encoding="utf-8") + out_csv.read_text(encoding="utf-8") + result.stdout
    assert "Orders" in text
    assert not re.search(r"(?i)case\s?id|CaseIdentifier|SPOCaseID|SP2016 vs SPO PROD", text)


def test_audit_scripts_carry_no_site_specific_names():
    banned = re.compile(r"(?i)Case_x0020|CaseIdentifier|SPOCaseID|known_defaults|plugins/sharepoint-migration")
    offenders = [(p.name, m.group(0)) for p in AUDIT.iterdir() if p.suffix in {".py", ".ps1", ".json"}
                 for m in banned.finditer(p.read_text(encoding="utf-8", errors="ignore"))]
    assert not offenders, offenders


@pytest.mark.parametrize("script", ["analyze-lookup-variances.py", "analyze-all-variances.py"])
def test_default_output_locations_follow_the_working_directory(second_site, script):
    """Defaults must land under <cwd>/.agents/scratch, never next to the plugin sources (regression: a parents[N] root guess)."""
    data, config, tmp = second_site
    write_csv(data / "Orders-sp2016-onprem.csv", [{"ID": "5", "Title": "ORD-1", "CustomerId": "1"}])
    write_csv(data / "Orders-spo-prod.csv", [{"ID": "5", "Title": "ORD-1", "Customer": "11"}])
    work = tmp / "project"
    work.mkdir()
    result = subprocess.run([sys.executable, str(AUDIT / script), "--data-dir", str(data), "--audit-config", str(config), "--list-name", "ALL"],
                            capture_output=True, text=True, timeout=120, cwd=work)
    assert result.returncode == 0, result.stdout + result.stderr
    assert any((work / ".agents" / "scratch").rglob("*")), "nothing written under <cwd>/.agents/scratch"
    assert not (AUDIT.parents[3] / ".agents").exists(), "wrote beside the plugin sources"


@pytest.mark.parametrize("script", ["analyze-lookup-variances.py", "analyze-all-variances.py"])
def test_missing_audit_config_is_an_error_not_a_silent_default(second_site, script):
    data, config, tmp = second_site
    result = subprocess.run([sys.executable, str(AUDIT / script), "--data-dir", str(data), "--audit-config", str(tmp / "nope.json"),
                             "--console-log", str(tmp / "c.md"), "--output-md", str(tmp / "r.md"), "--output-csv", str(tmp / "r.csv")],
                            capture_output=True, text=True, timeout=60)
    assert result.returncode != 0 and "Audit config not found" in (result.stderr + result.stdout)
    assert not (tmp / "r.md").exists()


@pytest.mark.parametrize("script", ["analyze-lookup-variances.py", "analyze-all-variances.py"])
def test_allow_default_config_runs_deliberately_with_generic_defaults(second_site, script):
    data, config, tmp = second_site
    write_csv(data / "Orders-sp2016-onprem.csv", [{"ID": "5", "Title": "ORD-1"}])
    write_csv(data / "Orders-spo-prod.csv", [{"ID": "5", "Title": "ORD-1"}])
    config.unlink()
    result = subprocess.run([sys.executable, str(AUDIT / script), "--data-dir", str(data), "--allow-default-config", "--list-name", "ALL",
                             "--console-log", str(tmp / "c.md"), "--output-md", str(tmp / "r.md"), "--output-csv", str(tmp / "r.csv")],
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.skipif(shutil.which("pwsh") is None, reason="pwsh not installed")
@pytest.mark.parametrize("title, expected", [
    ("Orders", "Orders"),
    ("O'Brien Orders", "O%27%27Brien%20Orders"),          # apostrophe doubled (OData), then URL-encoded
    ("R&D #1 100%", "R%26D%20%231%20100%25"),
])
def test_list_titles_are_escaped_for_rest_urls(title, expected):
    result = subprocess.run(["pwsh", "-NoProfile", "-Command", f". '{AUDIT / 'audit-helpers.ps1'}'; ConvertTo-ODataListTitle @'\n{title}\n'@"],
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == expected


def test_audit_scripts_use_the_escaping_helper_for_every_title_in_a_rest_url():
    for name in ("audit-list-lookup-reconciliation.ps1", "export-list-content-pairs.ps1"):
        text = (AUDIT / name).read_text(encoding="utf-8")
        assert "getbytitle('$srcTitle')" not in text, name
        assert "ConvertTo-ODataListTitle" in text and "audit-helpers.ps1" in text, name
