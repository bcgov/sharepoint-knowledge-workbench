"""
Purpose: Verify permissions collector output shapes against representative fixtures.

Key Input Dependencies:
    - pytest, the plugin module under test, and temporary JSON fixtures created by the test cases.

Function index:
    - test_collector_base_fields_match_fixture_schema
    - test_collector_supports_both_object_and_list_variants
"""

import json
import re
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "permissions-flat.json"
COLLECTOR = Path(__file__).parent.parent / "scripts" / "collect-sharepoint-permissions.ps1"


# Collector base fields match fixture schema.
def test_collector_base_fields_match_fixture_schema():
    """Collector base fields match fixture schema."""
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


# Collector supports both object and list variants.
def test_collector_supports_both_object_and_list_variants():
    """Collector supports both object and list variants."""
    collector_source = COLLECTOR.read_text(encoding="utf-8")
    assert '"objectTitle"' in collector_source or "objectTitle" in collector_source
    assert '"listName"' in collector_source or "listName" in collector_source
