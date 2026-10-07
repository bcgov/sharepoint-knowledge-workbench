"""
test_variance_analyzers_characterization.py

Purpose:
    Golden-master characterization of the two list-content variance analyzers
    (analyze-all-variances.py, analyze-lookup-variances.py). A fixture site that
    exercises every matching, lookup-pointer, parity and reporting branch is run
    through each script's real CLI; every console line and every written file must
    equal the recorded baseline, so internal refactors cannot change behaviour.

Layer: plugins/sharepoint-site-migration -- tests

Key Input Dependencies:
    - scripts/content-migration/content-audit/analyze-all-variances.py
    - scripts/content-migration/content-audit/analyze-lookup-variances.py
    - fixtures/variance-golden/<script-stem>.json (recorded baseline outputs).
    - Set UPDATE_VARIANCE_GOLDEN=1 to re-record the baseline deliberately.

Function Index:
    write_csv, build_site, run_scenario, collect_outputs,
    test_variance_analyzer_output_matches_recorded_baseline
"""

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

AUDIT = Path(__file__).resolve().parents[2] / "scripts" / "content-migration" / "content-audit"
GOLDEN = Path(__file__).resolve().parent / "fixtures" / "variance-golden"
SCRIPTS = ["analyze-all-variances.py", "analyze-lookup-variances.py"]


def write_csv(path, header, rows):
    """Write fixture rows under an explicit header so blank cells stay present."""
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def build_site(root):
    """Create exports, audit config, dependency matrix and identity map covering every analyzer branch."""
    data = root / "data"
    data.mkdir()
    cust = ["ID", "Title", "Email"]
    write_csv(data / "Customers-sp2016-onprem.csv", cust, [
        {"ID": "1", "Title": "ACME", "Email": "a@example.org"},
        {"ID": "2", "Title": "Beta", "Email": "b@example.org"},
        {"ID": "3", "Title": "Gamma", "Email": ""},
        {"ID": "4", "Title": "Delta", "Email": "d@example.org"},
    ])
    write_csv(data / "Customers-spo-prod.csv", cust, [
        {"ID": "11", "Title": "ACME", "Email": "a@example.org"},
        {"ID": "12", "Title": "Beta Two", "Email": "b@example.org"},
        {"ID": "3", "Title": "Gamma", "Email": ""},
    ])
    cases = ["ID", "Title", "Stat", "CustomerId", "AgentIds", "OwnerId", "Secret", "Amount", "Due", "Desc", "Modified"]
    write_csv(data / "OrderCases-sp2016-onprem.csv", cases, [
        {"ID": "5", "Title": "CASE-5", "Stat": "Open", "CustomerId": "1", "AgentIds": "1;#x;#2", "OwnerId": "1",
         "Secret": "s1", "Amount": "10", "Due": "2024/01/02", "Desc": "<p>Hi&nbsp;there</p>", "Modified": "x"},
        {"ID": "6", "Title": "CASE-7", "Stat": "Open", "CustomerId": "2", "AgentIds": "", "OwnerId": "",
         "Secret": "s2", "Amount": "5", "Due": "01/02/2024", "Desc": "a", "Modified": "x"},
        {"ID": "7", "Title": "", "Stat": "Open", "CustomerId": "1", "AgentIds": "1,2", "OwnerId": "2",
         "Secret": "", "Amount": "1.5", "Due": "", "Desc": "b", "Modified": "x"},
        {"ID": "9", "Title": "CASE-9", "Stat": "Open", "CustomerId": "1", "AgentIds": "", "OwnerId": "",
         "Secret": "", "Amount": "", "Due": "", "Desc": "", "Modified": "x"},
        {"ID": "10", "Title": "CASE-10", "Stat": "Done", "CustomerId": "2", "AgentIds": "2", "OwnerId": "",
         "Secret": "", "Amount": "3", "Due": "", "Desc": "<style>p{}</style><b>Bold</b>", "Modified": "x"},
        {"ID": "12", "Title": "Weird Name 12", "Stat": "Open", "CustomerId": "", "AgentIds": "", "OwnerId": "",
         "Secret": "", "Amount": "", "Due": "", "Desc": "", "Modified": "x"},
    ])
    spo_cases = ["ID", "Title", "Status", "Customer", "Agents", "Owner", "Secret", "Amount", "Due", "Desc", "Modified"]
    write_csv(data / "OrderCases-spo-prod.csv", spo_cases, [
        {"ID": "5", "Title": "CASE-5", "Status": "Open", "Customer": "11", "Agents": "11,12", "Owner": "11",
         "Secret": "other", "Amount": "10.0", "Due": "2024-01-02T00:00:00Z", "Desc": "hi there", "Modified": "y"},
        {"ID": "8", "Title": "CASE-7", "Status": "Closed", "Customer": "", "Agents": "", "Owner": "",
         "Secret": "", "Amount": "", "Due": "2024-01-02", "Desc": "A", "Modified": "y"},
        {"ID": "7", "Title": "Other", "Status": "Open", "Customer": "1", "Agents": "1,12", "Owner": "12",
         "Secret": "", "Amount": "1.50", "Due": "", "Desc": "b", "Modified": "y"},
        {"ID": "21", "Title": "CASE-10", "Status": "Done", "Customer": "11", "Agents": "", "Owner": "",
         "Secret": "", "Amount": "4", "Due": "", "Desc": "bold", "Modified": "y"},
        {"ID": "30", "Title": "Weird Name 12", "Status": "Open", "Customer": "", "Agents": "", "Owner": "",
         "Secret": "", "Amount": "", "Due": "", "Desc": "", "Modified": "y"},
    ])
    notes = ["ID", "Title", "Body", "Hidden", "RefId", "Empty", "Created", "_x"]
    write_csv(data / "Notes-sp2016-onprem.csv", notes, [
        {"ID": "1", "Title": "n1", "Body": "Same", "Hidden": "h", "RefId": "3", "Empty": "", "Created": "c", "_x": "1"},
        {"ID": "2", "Title": "n2", "Body": "Before", "Hidden": "h", "RefId": "", "Empty": "", "Created": "c", "_x": "1"},
        {"ID": "3", "Title": "n3", "Body": "Gone", "Hidden": "", "RefId": "", "Empty": "", "Created": "c", "_x": "1"},
    ])
    write_csv(data / "Notes-spo-prod.csv", ["ID", "Title", "Body", "Hidden", "Ref", "EmptyRef", "Created", "_x"], [
        {"ID": "1", "Title": "n1", "Body": "same", "Hidden": "zz", "Ref": "3", "EmptyRef": "", "Created": "d", "_x": "2"},
        {"ID": "2", "Title": "n2", "Body": "After", "Hidden": "zz", "Ref": "", "EmptyRef": "", "Created": "d", "_x": "2"},
    ])
    write_csv(data / "Notes-full-onprem.csv", notes, [
        {"ID": "1", "Title": "dup", "Body": "", "Hidden": "", "RefId": "", "Empty": "", "Created": "", "_x": ""},
    ])
    write_csv(data / "Archive-full-onprem.csv", ["ID", "Title", "ParentId", "PeerId"], [
        {"ID": "1", "Title": "a1", "ParentId": "1", "PeerId": "1"},
        {"ID": "2", "Title": "a2", "ParentId": "2", "PeerId": "2"},
    ])
    write_csv(data / "Archive-full-spo.csv", ["ID", "Title", "Parent", "Peer"], [
        {"ID": "1", "Title": "a1", "Parent": "1", "Peer": "1"},
        {"ID": "2", "Title": "a2", "Parent": "2", "Peer": ""},
    ])
    write_csv(data / "Orphan-sp2016-onprem.csv", ["ID", "Title"], [{"ID": "1", "Title": "o"}])

    config = root / "audit-config.json"
    config.write_text(json.dumps({
        "id_pattern": "^CASE-[0-9]+$", "key_columns": ["Title"],
        "identity_mapping": {"list": "Customers"},
        "lookups": {
            "OrderCases": {"Customer": ["CustomerId", "Customers"], "Agents": ["AgentIds", "Customers"]},
            "Notes": {"Ref": ["RefId", "Orders"]},
            "Archive": {"Parent": ["ParentId", "Customers"], "Peer": ["PeerId", "Customers"]},
        },
    }), encoding="utf-8")
    matrix = root / "matrix.json"
    matrix.write_text(json.dumps([
        {"destinationName": "OrderCases",
         "fieldRenames": [{"onPrem": "Stat", "spo": "Status", "type": "Choice"},
                          {"onPrem": "OwnerId", "spo": "Owner", "type": "Lookup", "lookupList": "Customers"}],
         "fieldExclusions": [{"sp2016InternalName": "Secret"}]},
        {"destinationName": "Notes",
         "fieldRenames": [{"onPrem": "Body", "spo": "Body", "type": "Note"},
                          {"onPrem": "Empty", "spo": "EmptyRef", "type": "Lookup", "lookupList": "Orders"}],
         "fieldExclusions": [{"field": "Hidden"}]},
        {"fieldRenames": [{"onPrem": "Z", "spo": "Z"}]},
    ]), encoding="utf-8")
    mapping = root / "id-mapping.json"
    mapping.write_text(json.dumps({"1": 11, "2": 12, "4": 99}), encoding="utf-8")
    return data, config, matrix, mapping


def collect_outputs(out_dir, tmp):
    """Read every file the analyzer wrote, normalized for temp paths and line endings."""
    found = {}
    for path in sorted(out_dir.rglob("*")):
        if path.is_file():
            text = path.read_bytes().decode("utf-8").replace("\r\n", "\n")
            found[path.relative_to(out_dir).as_posix()] = text.replace(str(tmp), "<TMP>").replace("\\", "/")
    return found


def run_scenario(script, tmp, list_name):
    """Run one analyzer CLI over the fixture site and return its normalized stdout and files."""
    data, config, matrix, mapping = build_site(tmp)
    out = tmp / "out"
    out.mkdir()
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    result = subprocess.run(
        [sys.executable, str(AUDIT / script), "--data-dir", str(data), "--audit-config", str(config),
         "--matrix-path", str(matrix), "--mapping-path", str(mapping),
         "--output-md", str(out / "report.md"), "--output-csv", str(out / "all.csv"),
         "--console-log", str(out / "console.md"), "--list-name", list_name],
        capture_output=True, text=True, encoding="utf-8", timeout=120, cwd=tmp, env=env)
    assert result.returncode == 0, result.stdout + result.stderr
    stdout = result.stdout.replace(str(tmp), "<TMP>").replace("\\", "/")
    return {"stdout": stdout, "files": collect_outputs(out, tmp)}


@pytest.mark.parametrize("script", SCRIPTS)
def test_variance_analyzer_output_matches_recorded_baseline(tmp_path, script):
    """Every console line and output file must equal the recorded baseline for each scope."""
    actual = {}
    for scope in ("ALL", "cases", "nomatch"):
        work = tmp_path / scope
        work.mkdir()
        actual[scope] = run_scenario(script, work, scope)
    golden = GOLDEN / f"{Path(script).stem}.json"
    if os.environ.get("UPDATE_VARIANCE_GOLDEN") == "1":
        golden.parent.mkdir(parents=True, exist_ok=True)
        golden.write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert golden.is_file(), f"baseline missing: {golden} (record it with UPDATE_VARIANCE_GOLDEN=1 before refactoring)"
    assert actual == json.loads(golden.read_text(encoding="utf-8"))
