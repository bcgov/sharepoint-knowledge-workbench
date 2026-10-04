import json
import re
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "permissions-flat.json"
COLLECTOR = Path(__file__).parent.parent / "scripts" / "collect-sharepoint-permissions.ps1"


def test_collector_base_fields_match_fixture_schema():
    fixture_records = json.loads(FIXTURE.read_text(encoding="utf-8"))
    base_fields = {"webUrl", "principalTitle", "permissionLevels"}

    collector_source = COLLECTOR.read_text(encoding="utf-8")
    match = re.search(r"\$record = \[ordered\]@\{(.*?)\}", collector_source, re.DOTALL)
    assert match, "collector script must build records via [ordered]@{...}"
    collector_fields = set(re.findall(r"^\s*(\w+)\s*=", match.group(1), re.MULTILINE))

    assert base_fields <= collector_fields, (
        f"collector base fields {collector_fields} do not cover the fixture's "
        f"required base fields {base_fields}"
    )
    fixture_all_keys = set()
    for record in fixture_records:
        fixture_all_keys.update(record.keys())
    assert fixture_all_keys - base_fields <= {"objectTitle", "listName"}


def test_collector_supports_both_object_and_list_variants():
    collector_source = COLLECTOR.read_text(encoding="utf-8")
    assert '"objectTitle"' in collector_source or "objectTitle" in collector_source
    assert '"listName"' in collector_source or "listName" in collector_source
