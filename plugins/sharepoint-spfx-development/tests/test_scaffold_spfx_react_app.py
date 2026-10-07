"""Purpose: Verify the generated files and configured values for the React SPFx scaffold.

Key Input Dependencies:
    - scripts/scaffold_spfx_react_app.py
    - A scaffold specification mapping and a temporary output directory.

Function Index:
    - test_scaffold_react_app_writes_configured_project_files
"""

import json
from pathlib import Path
from typing import Any, Dict

from scripts.scaffold_spfx_react_app import scaffold_react_app


# Verifies that the public scaffolder preserves configured metadata and emits all expected artifacts.
def test_scaffold_react_app_writes_configured_project_files(tmp_path: Path) -> None:
    """Checks generated file names, manifest values, and application setup content."""
    spec: Dict[str, Any] = {
        "webPartName": "FieldGuide",
        "title": "Field Guide",
        "description": "A project field guide.",
        "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    }
    output_dir = tmp_path / "webpart"

    scaffold_react_app(spec, output_dir)

    expected_files = {
        output_dir / "FieldGuideWebPart.manifest.json",
        output_dir / "FieldGuideWebPart.ts",
        output_dir / "components" / "FieldGuide.tsx",
        output_dir / "components" / "pnpjsConfig.ts",
        output_dir / "style" / "tailwind.css",
        output_dir / "style" / "tailwind.output.css",
    }
    assert expected_files.issubset(set(output_dir.rglob("*")))

    manifest = json.loads((output_dir / "FieldGuideWebPart.manifest.json").read_text(encoding="utf-8"))
    assert manifest["id"] == spec["id"]
    assert manifest["preconfiguredEntries"][0]["title"]["default"] == spec["title"]
    assert manifest["preconfiguredEntries"][0]["properties"]["description"] == spec["description"]

    component_source = (output_dir / "components" / "FieldGuide.tsx").read_text(encoding="utf-8")
    assert "export const FieldGuide:" in component_source
    assert "props.webpartTitle" in component_source
    assert "Ready for custom data binding and filters." in component_source

    webpart_source = (output_dir / "FieldGuideWebPart.ts").read_text(encoding="utf-8")
    assert "getSP(this.context);" in webpart_source
    assert "PropertyPaneSlider('maxItems'" in webpart_source

    pnp_config = (output_dir / "components" / "pnpjsConfig.ts").read_text(encoding="utf-8")
    assert "export const getSP" in pnp_config
    assert "export const getWeb" in pnp_config
