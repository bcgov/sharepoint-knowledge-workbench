"""Tests for navigation_plan.py (real xlsx/JSON file I/O and a real CLI subprocess; no tenant access).

Purpose: verify workbook validation, plan building, plan-vs-live diffing and snapshot-to-workbook export.

Key Input Dependencies: scripts/navigation/navigation_plan.py, openpyxl.
"""
import json
import subprocess
import sys
from pathlib import Path

import openpyxl

_plugin_dir = Path(__file__).resolve().parents[1]
_skills_dir = _plugin_dir / ".apm" / "skills" if (_plugin_dir / ".apm" / "skills").exists() else _plugin_dir / "skills"
SCRIPT = _skills_dir / "managing-sharepoint-navigation" / "scripts" / "navigation_plan.py"
sys.path.insert(0, str(SCRIPT.parent))
import navigation_plan as nav  # noqa: E402

HEADER = ["Top Level", "2nd Level", "3rd Level", "Url", "OpenInNewTab", "Enabled"]
SITE = "https://tenant.sharepoint.com/sites/dev"


def make_workbook(tmp_path, rows, header=HEADER):
    path = tmp_path / "nav.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(header)
    for row in rows:
        ws.append(row)
    wb.save(path)
    return path


def plan_of(tmp_path, rows, **kwargs):
    return nav.build_plan(nav.read_workbook(make_workbook(tmp_path, rows)), **kwargs)


def live(*nodes):
    return {"topNav": list(nodes)}


def node(id_, title, url="", *children):
    return {"id": id_, "title": title, "url": url, "children": list(children)}


def ops_by_kind(result):
    out = {}
    for op in result["ops"]:
        out.setdefault(op["op"], []).append(op)
    return out


def test_builds_nested_tree_in_row_order(tmp_path):
    plan = plan_of(tmp_path, [
        ["Home", None, None, "/sites/dev", None, None],
        ["Operations", None, None, None, None, None],
        ["Operations", "Safety", None, "/sites/dev/s", None, None],
        ["Operations", "Safety", "Incidents", "/sites/dev/i", "Y", None],
        ["Operations", "Alpha", None, "/sites/dev/a", None, None],
    ])
    assert plan["errors"] == []
    titles = [n["title"] for n in plan["nodes"]]
    assert titles == ["Home", "Operations"]
    operations = plan["nodes"][1]
    assert [c["title"] for c in operations["children"]] == ["Safety", "Alpha"]
    incidents = operations["children"][0]["children"][0]
    assert incidents["url"] == "/sites/dev/i" and incidents["openInNewTab"] is True


def test_duplicate_full_path_is_an_error(tmp_path):
    plan = plan_of(tmp_path, [
        ["Home", None, None, "/a", None, None],
        ["Home", None, None, "/b", None, None],
    ])
    assert any("duplicate" in e.lower() for e in plan["errors"])


def test_repeated_title_under_different_parents_is_allowed(tmp_path):
    plan = plan_of(tmp_path, [
        ["A", None, None, "/a", None, None],
        ["A", "Onboarding", None, "/a/o", None, None],
        ["B", None, None, "/b", None, None],
        ["B", "Onboarding", None, "/b/o", None, None],
    ])
    assert plan["errors"] == []


def test_hierarchy_gap_is_an_error(tmp_path):
    plan = plan_of(tmp_path, [["Home", None, "Deep", "/x", None, None]])
    assert any("gap" in e.lower() for e in plan["errors"])


def test_replacement_character_is_an_error(tmp_path):
    plan = plan_of(tmp_path, [["Bill C-78 \ufffd Divorce Act", None, None, "/x", None, None]])
    assert any("encoding" in e.lower() for e in plan["errors"])


def test_fragment_and_bad_scheme_urls_are_errors(tmp_path):
    plan = plan_of(tmp_path, [
        ["A", None, None, "/page#frag", None, None],
        ["B", None, None, "ftp://x/y", None, None],
    ])
    assert len([e for e in plan["errors"] if "url" in e.lower()]) == 2


def test_leaf_without_url_errors_unless_allowed(tmp_path):
    rows = [["Home", None, None, None, None, None]]
    assert any("url" in e.lower() for e in plan_of(tmp_path, rows)["errors"])
    relaxed = plan_of(tmp_path, rows, allow_missing_urls=True)
    assert relaxed["errors"] == [] and relaxed["warnings"]


def test_group_header_without_url_is_valid(tmp_path):
    plan = plan_of(tmp_path, [
        ["Operations", None, None, None, None, None],
        ["Operations", "Safety", None, "/s", None, None],
    ])
    assert plan["errors"] == []


def test_implicit_parent_is_created_with_warning(tmp_path):
    plan = plan_of(tmp_path, [["Operations", "Safety", None, "/s", None, None]])
    assert plan["errors"] == []
    assert plan["nodes"][0]["title"] == "Operations" and plan["warnings"]


def test_disabled_row_and_its_children_are_dropped(tmp_path):
    plan = plan_of(tmp_path, [
        ["Home", None, None, "/h", None, None],
        ["Later", None, None, "/l", None, "N"],
        ["Later", "Child", None, "/lc", None, None],
    ])
    assert [n["title"] for n in plan["nodes"]] == ["Home"]


def test_missing_level_header_raises(tmp_path):
    path = make_workbook(tmp_path, [["x"]], header=["Name"])
    try:
        nav.read_workbook(path)
    except ValueError as exc:
        assert "Top Level" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_diff_create_update_unchanged_prune_and_order(tmp_path):
    plan = plan_of(tmp_path, [
        ["Home", None, None, "/sites/dev", None, None],
        ["New", None, None, "/sites/dev/new", None, None],
        ["Tools", None, None, "/sites/dev/tools-v2", None, None],
    ])
    snapshot = live(
        node(1, "Home", SITE),
        node(2, "Tools", f"{SITE}/tools"),
        node(3, "Old", "/sites/dev/old", node(4, "OldChild", "/sites/dev/oc")),
    )
    result = nav.diff_plan(plan, snapshot, site_url=SITE)
    kinds = ops_by_kind(result)
    assert [o["path"] for o in kinds["unchanged"]] == [["Home"]]
    assert kinds["create"][0]["path"] == ["New"]
    assert kinds["create"][0]["previousPath"] == ["Home"]
    assert kinds["update"][0]["id"] == 2 and kinds["update"][0]["url"] == "/sites/dev/tools-v2"
    assert [o["path"] for o in kinds["prune"]] == [["Old"]]
    assert result["summary"]["prune"] == 1


def test_diff_is_idempotent_when_live_matches_plan(tmp_path):
    plan = plan_of(tmp_path, [
        ["Operations", None, None, None, None, None],
        ["Operations", "Safety", None, "/sites/dev/s", None, None],
    ])
    snapshot = live(node(1, "Operations", "http://linkless.header/", node(2, "Safety", f"{SITE}/s")))
    result = nav.diff_plan(plan, snapshot, site_url=SITE)
    assert set(ops_by_kind(result)) == {"unchanged"}


def test_diff_reports_order_drift_without_creating(tmp_path):
    plan = plan_of(tmp_path, [
        ["A", None, None, "/a", None, None],
        ["B", None, None, "/b", None, None],
    ])
    snapshot = live(node(1, "B", "/b"), node(2, "A", "/a"))
    result = nav.diff_plan(plan, snapshot, site_url=SITE)
    kinds = ops_by_kind(result)
    assert "order-drift" in kinds and "create" not in kinds


def test_diff_first_item_has_no_previous(tmp_path):
    plan = plan_of(tmp_path, [["A", None, None, "/a", None, None]])
    result = nav.diff_plan(plan, live(), site_url=SITE)
    create = ops_by_kind(result)["create"][0]
    assert create["previousPath"] is None and create["parentPath"] is None


def test_snapshot_to_workbook_round_trips_through_plan(tmp_path):
    snapshot = live(
        node(1, "Home", "/sites/dev"),
        node(2, "Operations", "http://linkless.header/", node(3, "Safety", "/s", node(4, "Incidents", "/i"))),
    )
    out = tmp_path / "download.xlsx"
    nav.snapshot_to_workbook(snapshot, out)
    plan = nav.build_plan(nav.read_workbook(out), allow_missing_urls=False)
    assert plan["errors"] == []
    result = nav.diff_plan(plan, snapshot, site_url=SITE)
    assert set(ops_by_kind(result)) == {"unchanged"}


def test_cli_plan_diff_and_exit_codes(tmp_path):
    wb = make_workbook(tmp_path, [["Home", None, None, "/h", None, None]])
    plan_path = tmp_path / "plan.json"
    run = subprocess.run([sys.executable, str(SCRIPT), "plan", "--workbook", str(wb), "--out", str(plan_path)],
                         capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    snap = tmp_path / "snap.json"
    snap.write_text(json.dumps(live()), encoding="utf-8")
    ops_path = tmp_path / "ops.json"
    run = subprocess.run([sys.executable, str(SCRIPT), "diff", "--plan", str(plan_path), "--snapshot", str(snap),
                          "--out", str(ops_path)], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert json.loads(ops_path.read_text(encoding="utf-8"))["summary"]["create"] == 1

    bad = make_workbook(tmp_path, [["Home", None, None, None, None, None]])
    run = subprocess.run([sys.executable, str(SCRIPT), "plan", "--workbook", str(bad), "--out", str(tmp_path / "x.json")],
                         capture_output=True, text=True)
    assert run.returncode == 2 and "url" in run.stderr.lower()
    assert not (tmp_path / "x.json").exists()
