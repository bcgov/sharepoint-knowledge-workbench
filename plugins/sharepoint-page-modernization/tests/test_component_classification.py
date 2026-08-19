"""
test_component_classification.py
================================

Stage 2 tests -- assign Role/Type/Variant to each detected zone.

Semantic-parity oracle: baseline test suite. Retained behaviours:
first unconnected list view is Primary, additional standalone views are
Secondary, connected consumers are Child/connected-consumer, ContentEditors
are Banner, zone confidence is inherited, an empty inventory yields an empty
model. Added behaviour (intentional improvement): an unrecognised web part
type is reported through the outcome vocabulary rather than being silently
labelled "Unknown" and forgotten.
"""

import json
import subprocess
import sys


def run_classify(scripts_dir, inventory: dict, tmp_path) -> dict:
    inv_file = tmp_path / "page-inventory.json"
    inv_file.write_text(json.dumps(inventory), encoding="utf-8")
    out_file = tmp_path / "component-model.json"
    result = subprocess.run(
        [sys.executable, str(scripts_dir / "component_classification.py"),
         "--input", str(inv_file), "--output", str(out_file)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(out_file.read_text(encoding="utf-8"))


def _inventory():
    return {
        "detectionMethod": "multi",
        "pageType": "BlankWebPartPage",
        "hasConnections": True,
        "zones": [
            {"zoneId": "wpz_ce_1", "webPartType": "ContentEditor", "rawHtml": "<div>Title</div>",
             "detectionSource": "rendered-html"},
            {"zoneId": "wpz_ce_2", "webPartType": "ContentEditor", "rawHtml": "<div>Subtitle</div>",
             "detectionSource": "rendered-html"},
            {"zoneId": "wpz_lv_1", "webPartType": "XsltListView", "listName": "Project_Requests",
             "isConnectedConsumer": False, "detectionSource": "views-json"},
            {"zoneId": "wpz_lv_2", "webPartType": "XsltListView", "listName": "Reference_Data",
             "isConnectedConsumer": False, "detectionSource": "views-json"},
            {"zoneId": "wpz_lv_child_Request_Tasks", "webPartType": "XsltListView",
             "listName": "Request_Tasks", "isConnectedConsumer": True,
             "relationship": "Parent(Project_Requests).ID -> RequestId",
             "detectionSource": "override-file", "confidence": "manual-hint"},
        ],
        "warnings": [],
    }


def test_first_unconnected_listview_is_primary(scripts_dir, tmp_path):
    model = run_classify(scripts_dir, _inventory(), tmp_path)
    primary = [c for c in model["components"] if c["role"] == "Primary"]
    assert len(primary) == 1
    assert primary[0]["listName"] == "Project_Requests"


def test_additional_standalone_listview_is_secondary(scripts_dir, tmp_path):
    model = run_classify(scripts_dir, _inventory(), tmp_path)
    secondary = [c for c in model["components"] if c["role"] == "Secondary"]
    assert [c["listName"] for c in secondary] == ["Reference_Data"]


def test_connected_consumer_is_child(scripts_dir, tmp_path):
    model = run_classify(scripts_dir, _inventory(), tmp_path)
    children = [c for c in model["components"] if c["role"] == "Child"]
    assert len(children) == 1
    assert children[0]["variant"] == "connected-consumer"
    assert children[0]["listName"] == "Request_Tasks"


def test_content_editor_role_is_banner(scripts_dir, tmp_path):
    model = run_classify(scripts_dir, _inventory(), tmp_path)
    assert len([c for c in model["components"] if c["role"] == "Banner"]) == 2


def test_confidence_is_inherited_from_the_zone(scripts_dir, tmp_path):
    model = run_classify(scripts_dir, _inventory(), tmp_path)
    child = next(c for c in model["components"] if c["role"] == "Child")
    assert child["confidence"] == "manual-hint"


def test_empty_inventory_produces_empty_model_and_empty_outcome(scripts_dir, tmp_path):
    inv = _inventory()
    inv["zones"] = []
    model = run_classify(scripts_dir, inv, tmp_path)
    assert model["components"] == []
    assert model["outcome"]["status"] == "Empty"
    assert model["outcome"]["detail"]


def test_all_zones_unsupported_reports_not_supported(scripts_dir, fixtures_dir, tmp_path):
    inv = json.loads((fixtures_dir / "unsupported-webpart.inventory.json").read_text(encoding="utf-8"))
    model = run_classify(scripts_dir, inv, tmp_path)
    assert all(c["role"] == "Unknown" for c in model["components"])
    assert model["outcome"]["status"] == "NotSupported"
    assert "SPUserCodeWebPart" in model["outcome"]["detail"]


def test_some_zones_unsupported_reports_partial(scripts_dir, tmp_path):
    inv = _inventory()
    inv["zones"].append({"zoneId": "wpz_x", "webPartType": "SPUserCodeWebPart",
                         "detectionSource": "rendered-html"})
    model = run_classify(scripts_dir, inv, tmp_path)
    assert model["outcome"]["status"] == "Partial"
    assert "SPUserCodeWebPart" in model["outcome"]["detail"]


def test_fully_supported_inventory_reports_observed(scripts_dir, tmp_path):
    model = run_classify(scripts_dir, _inventory(), tmp_path)
    assert model["outcome"]["status"] == "Observed"


def test_missing_input_file_fails_honestly(scripts_dir, tmp_path):
    result = subprocess.run(
        [sys.executable, str(scripts_dir / "component_classification.py"),
         "--input", str(tmp_path / "nope.json"), "--output", str(tmp_path / "o.json")],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "Unavailable" in result.stderr
