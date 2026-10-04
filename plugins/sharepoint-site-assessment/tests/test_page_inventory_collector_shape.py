import json
import re
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "page-inventory.json"
COLLECTOR = Path(__file__).parent.parent / "scripts" / "collect-sharepoint-page-inventory.ps1"


def test_collector_output_fields_match_fixture_schema():
    fixture_records = json.loads(FIXTURE.read_text(encoding="utf-8"))
    fixture_fields = set(fixture_records[0].keys())

    collector_source = COLLECTOR.read_text(encoding="utf-8")
    match = re.search(r"\$pages \+= \[pscustomobject\]@\{(.*?)\}", collector_source, re.DOTALL)
    assert match, "collector script must build $pages entries via [pscustomobject]@{...}"
    collector_fields = set(re.findall(r"^\s*(\w+)\s*=", match.group(1), re.MULTILINE))

    assert collector_fields == fixture_fields, (
        f"collector output fields {collector_fields} do not match "
        f"page_inventory_analysis.py's expected fixture fields {fixture_fields}"
    )


def test_collector_webpart_fields_match_fixture_schema():
    fixture_records = json.loads(FIXTURE.read_text(encoding="utf-8"))
    fixture_wp_fields = set(fixture_records[1]["WebParts"][0].keys())  # links.aspx has WebParts

    collector_source = COLLECTOR.read_text(encoding="utf-8")
    matches = re.findall(r"\[pscustomobject\]@\{ Category = .*? \}", collector_source)
    assert matches, "collector script must build WebParts entries via [pscustomobject]@{...}"
    collector_wp_fields = set(re.findall(r"(\w+)\s*=", matches[0]))

    assert collector_wp_fields == fixture_wp_fields
