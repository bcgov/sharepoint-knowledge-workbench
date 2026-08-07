"""
test_component_mapping.py
=========================

Stage 4 tests -- map classified components to modern sections and target list
views, and record what could not be migrated.

Semantic-parity oracle: CMAT `tests/test_map_components.py`. Retained
behaviours: ContentEditor -> TextWebPart; Primary list view -> ListWebPart
plus a view-plan entry; connected consumer -> NOT_MIGRATED with the
GAP-001-CRITICAL reason and relationship captured; a gap-notice section
appended once when gaps exist; deterministic prefixed view names.

Intentional improvements:
  * CMAT's tests loaded a mapping file from a project-analysis directory five
    levels outside the plugin. This plugin ships its own neutral mapping file.
  * CMAT hardcoded the `CMAT_Migration_` view-name prefix; here it is a CLI
    option with a neutral default.
  * CMAT's gap notice was a hardcoded HTML literal naming specific project
    lists; here it is rendered from a template using the lists that were
    actually not migrated.
"""

import json
import subprocess
import sys

LAYOUT = {"selectedLayout": "Home", "sectionTemplate": "OneColumn", "ruleApplied": "LR-001"}


def run_map(scripts_dir, components, tmp_path, *extra) -> tuple[dict, dict]:
    comp_file = tmp_path / "component-model.json"
    layout_file = tmp_path / "layout-decision.json"
    map_out = tmp_path / "mapping-plan.json"
    view_out = tmp_path / "view-plan.json"
    comp_file.write_text(json.dumps({"components": components}), encoding="utf-8")
    layout_file.write_text(json.dumps(LAYOUT), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(scripts_dir / "component_mapping.py"),
         "--components", str(comp_file),
         "--layout", str(layout_file),
         "--output-mapping", str(map_out),
         "--output-views", str(view_out), *extra],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(map_out.read_text(encoding="utf-8")), json.loads(view_out.read_text(encoding="utf-8"))


def _primary():
    return {"role": "Primary", "type": "XsltListView", "variant": "standalone",
            "listName": "Project_Requests", "viewQuery": "<Where/>", "zone": "wpz4",
            "confidence": "medium", "evidence": {}}


def _consumer():
    return {"role": "Child", "type": "XsltListView", "variant": "connected-consumer",
            "listName": "Request_Tasks", "relationship": "Parent(Project_Requests).ID -> RequestId",
            "zone": "wpz5", "confidence": "manual-hint", "evidence": {}}


def test_content_editor_maps_to_text_web_part(scripts_dir, tmp_path):
    plan, _ = run_map(scripts_dir, [{"role": "Banner", "type": "ContentEditor",
                                     "rawHtml": "<p>Hi</p>", "zone": "wpz1",
                                     "confidence": "high", "evidence": {}}], tmp_path)
    section = next(s for s in plan["sections"] if s["webPart"]["sourceZone"] == "wpz1")
    assert section["webPart"]["type"] == "TextWebPart"
    assert section["webPart"]["content"] == "<p>Hi</p>"


def test_primary_listview_maps_to_list_web_part_and_a_view_entry(scripts_dir, tmp_path):
    plan, views = run_map(scripts_dir, [_primary()], tmp_path)
    section = next(s for s in plan["sections"] if s["webPart"].get("listName") == "Project_Requests")
    assert section["webPart"]["type"] == "ListWebPart"
    view = next(v for v in views["views"] if v["listName"] == "Project_Requests")
    assert view["camlQuery"] == "<Where/>"
    assert view["viewName"] == section["webPart"]["viewName"]


def test_caml_lives_in_the_view_not_the_page(scripts_dir, tmp_path):
    """ARCH-001: the page web part references a view by name; it carries no CAML."""
    plan, _ = run_map(scripts_dir, [_primary()], tmp_path)
    section = next(s for s in plan["sections"] if s["webPart"].get("listName"))
    assert "camlQuery" not in section["webPart"]
    assert "viewQuery" not in section["webPart"]


def test_connected_consumer_is_not_migrated_and_keeps_its_relationship(scripts_dir, tmp_path):
    plan, views = run_map(scripts_dir, [_consumer()], tmp_path)
    nm = [n for n in plan["notMigrated"] if n["listName"] == "Request_Tasks"]
    assert len(nm) == 1
    assert "GAP-001-CRITICAL" in nm[0]["reason"]
    assert nm[0]["relationship"] == "Parent(Project_Requests).ID -> RequestId"
    assert not any(v["listName"] == "Request_Tasks" for v in views["views"])


def test_gap_notice_section_added_exactly_once_when_gaps_exist(scripts_dir, tmp_path):
    plan, _ = run_map(scripts_dir, [_primary(), _consumer()], tmp_path)
    gap_sections = [s for s in plan["sections"] if s["webPart"].get("isGapNotice")]
    assert len(gap_sections) == 1


def test_gap_notice_names_the_lists_that_were_actually_not_migrated(scripts_dir, tmp_path):
    """The notice is generated from evidence, not a hardcoded project-specific literal."""
    plan, _ = run_map(scripts_dir, [_primary(), _consumer()], tmp_path)
    notice = next(s for s in plan["sections"] if s["webPart"]["isGapNotice"])["webPart"]["content"]
    assert "Request_Tasks" in notice


def test_no_gap_notice_when_nothing_was_dropped(scripts_dir, tmp_path):
    plan, _ = run_map(scripts_dir, [_primary()], tmp_path)
    assert not any(s["webPart"].get("isGapNotice") for s in plan["sections"])


def test_view_name_prefix_defaults_to_a_neutral_value(scripts_dir, tmp_path):
    _, views = run_map(scripts_dir, [_primary()], tmp_path)
    assert views["views"][0]["viewName"] == "Migrated_ProjectRequests"


def test_view_name_prefix_is_configurable(scripts_dir, tmp_path):
    _, views = run_map(scripts_dir, [_primary()], tmp_path, "--view-name-prefix", "Acme_")
    assert views["views"][0]["viewName"] == "Acme_ProjectRequests"


def test_rules_applied_comes_from_the_mapping_file_not_a_hardcoded_list(scripts_dir, tmp_path):
    custom = tmp_path / "mapping.json"
    custom.write_text(json.dumps({"mappingVersion": "9.9.9", "architecturalRules": [
        {"id": "X-001", "rule": "only rule"},
    ]}), encoding="utf-8")
    plan, _ = run_map(scripts_dir, [_primary()], tmp_path, "--mapping-rules", str(custom))
    assert plan["mappingVersion"] == "9.9.9"
    assert plan["rulesApplied"] == ["X-001"]


def test_packaged_mapping_rules_are_used_by_default(scripts_dir, tmp_path):
    plan, _ = run_map(scripts_dir, [_primary()], tmp_path)
    assert plan["rulesApplied"] == ["ARCH-001", "ARCH-002", "ARCH-003", "ARCH-004", "ARCH-005"]


def test_mapping_with_gaps_reports_partial(scripts_dir, tmp_path):
    plan, _ = run_map(scripts_dir, [_primary(), _consumer()], tmp_path)
    assert plan["outcome"]["status"] == "Partial"
    assert "Request_Tasks" in plan["outcome"]["detail"]


def test_fully_mapped_page_reports_observed(scripts_dir, tmp_path):
    plan, _ = run_map(scripts_dir, [_primary()], tmp_path)
    assert plan["outcome"]["status"] == "Observed"


def test_page_whose_components_are_all_unmappable_reports_not_supported(scripts_dir, tmp_path):
    plan, _ = run_map(scripts_dir, [{"role": "Unknown", "type": "SPUserCodeWebPart",
                                     "zone": "wpz9", "confidence": "none", "evidence": {}}], tmp_path)
    assert plan["sections"] == []
    assert plan["outcome"]["status"] == "NotSupported"
    assert "SPUserCodeWebPart" in plan["outcome"]["detail"]


def test_empty_component_model_reports_empty(scripts_dir, tmp_path):
    plan, _ = run_map(scripts_dir, [], tmp_path)
    assert plan["outcome"]["status"] == "Empty"
