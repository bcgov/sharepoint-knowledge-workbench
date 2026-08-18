#!/usr/bin/env python
# Purpose: Scaffold a SPFx Master-Detail Web Part boilerplate from a JSON layout specification.
# Layer: Plugin Engineering / SPFx Scaffolding Generator

"""
scaffold_spfx_master_detail.py

Generates TypeScript (.ts), SCSS module (.module.scss), and SPFx manifest (.manifest.json)
for a consolidated Master-Detail dossier component based on a JSON layout specification.
"""

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Tuple


def generate_spfx_ts_code(spec: Dict[str, Any]) -> str:
    """
    Generates TypeScript code for the Master-Detail SPFx Web Part based on specification.

    Args:
        spec: Dictionary containing webPartName, primaryList, lookupList, childLists, etc.

    Returns:
        Formatted TypeScript source code as a string.
    """
    web_part_name = spec.get("webPartName", "MasterDetail")
    class_name = f"{web_part_name}WebPart"
    title = spec.get("title", "SharePoint Dossier Dashboard")
    primary_list = spec.get("primaryList", "Persons")
    lookup_list = spec.get("lookupList", "Authors")
    child_lists = spec.get("childLists", [])
    image_lib = spec.get("imageLibrary", "Images")

    child_fetches = ""
    for idx, child in enumerate(child_lists):
        c_name = child.get("listName", f"ChildList{idx}")
        c_filter = child.get("filterField", "RelatedAuthorId")
        child_fetches += f"""
      const childUrl{idx} = `${{siteUrl}}/_api/web/lists/getbytitle('{c_name}')/items?$filter={c_filter} eq ${{lookupId}}&$select=Id,Title`;
"""

    return f"""import {{ Version }} from '@microsoft/sp-core-library';
import {{
  BaseClientSideWebPart,
  IPropertyPaneConfiguration,
  PropertyPaneTextField
}} from '@microsoft/sp-webpart-base';
import {{ SPHttpClient }} from '@microsoft/sp-http';
import styles from './{class_name}.module.scss';

export interface I{class_name}Props {{
  description: string;
}}

export default class {class_name} extends BaseClientSideWebPart<I{class_name}Props> {{
  private _renderToken: number = 0;

  private _escapeHtml(text: string | null | undefined): string {{
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }}

  public async render(): void {{
    const token = ++this._renderToken;
    const urlParams = new URLSearchParams(window.location.search);
    const selectedIdParam = urlParams.get('SelectedID') || urlParams.get('selectedid') || urlParams.get('ID');

    if (!selectedIdParam) {{
      this.domElement.innerHTML = `
        <div class="${{styles.masterDetailContainer}}">
          <div class="${{styles.banner}}"><h1>{title}</h1></div>
          <div class="${{styles.emptyNotice}}">No SelectedID provided in URL query string (e.g. ?SelectedID=1).</div>
        </div>`;
      return;
    }}

    const primaryId = parseInt(selectedIdParam, 10);
    if (isNaN(primaryId)) {{
      this.domElement.innerHTML = `
        <div class="${{styles.masterDetailContainer}}">
          <div class="${{styles.banner}}"><h1>{title}</h1></div>
          <div class="${{styles.emptyNotice}}">Invalid SelectedID: ${{this._escapeHtml(selectedIdParam)}}</div>
        </div>`;
      return;
    }}

    const siteUrl = this.context.pageContext.web.absoluteUrl;
    const primaryUrl = `${{siteUrl}}/_api/web/lists/getbytitle('{primary_list}')/items(${{primaryId}})?$select=Id,Title`;

    try {{
      const primaryRes = await this.context.spHttpClient.get(primaryUrl, SPHttpClient.configurations.v1, {{
        headers: {{ Accept: 'application/json;odata=nometadata' }}
      }});

      if (!primaryRes.ok) {{
        this.domElement.innerHTML = `
          <div class="${{styles.masterDetailContainer}}">
            <div class="${{styles.banner}}"><h1>{title}</h1></div>
            <div class="${{styles.emptyNotice}}">Record not found for SelectedID: ${{primaryId}}</div>
          </div>`;
        return;
      }}

      const primaryData = await primaryRes.json();
      const lookupId = primaryData.Id;
      {child_fetches}

      if (token !== this._renderToken) {{
        return;
      }}

      this.domElement.innerHTML = `
        <div class="${{styles.masterDetailContainer}}">
          <div class="${{styles.banner}}">
            <h1>{title}</h1>
          </div>

          <div class="${{styles.section}}">
            <div class="${{styles.sectionHeader}}">
              <h3>Identification Details ({primary_list})</h3>
            </div>
            <div class="${{styles.idCardContainer}}">
              <div class="${{styles.photoBox}}">
                <span class="${{styles.noPhotoText}}">{image_lib}</span>
              </div>
              <div class="${{styles.detailGrid}}">
                <div class="${{styles.detailItem}}">
                  <span class="${{styles.label}}">Item Title</span>
                  <span class="${{styles.value}}">${{this._escapeHtml(primaryData.Title || 'None')}}</span>
                </div>
                <div class="${{styles.detailItem}}">
                  <span class="${{styles.label}}">Record ID</span>
                  <span class="${{styles.value}}">${{lookupId}}</span>
                </div>
              </div>
            </div>
          </div>
        </div>`;
    }} catch (error) {{
      this.domElement.innerHTML = `<div class="${{styles.emptyNotice}}">Error loading dossier: ${{error}}</div>`;
    }}
  }}

  protected get dataVersion(): Version {{
    return Version.parse('1.0');
  }}
}}
"""


def generate_spfx_manifest(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a standard SPFx web part manifest JSON dictionary.

    Args:
        spec: Specification dictionary containing webPartName and title.

    Returns:
        Manifest dictionary ready for JSON serialization.
    """
    web_part_name = spec.get("webPartName", "MasterDetail")
    title = spec.get("title", "Master Detail Web Part")
    component_id = str(uuid.uuid4())

    return {
        "$schema": "https://developer.microsoft.com/json-schemas/spfx/client-side-web-part-manifest.schema.json",
        "id": component_id,
        "alias": f"{web_part_name}WebPart",
        "componentType": "WebPart",
        "version": "*",
        "manifestVersion": 2,
        "requiresCustomScript": False,
        "preconfiguredEntries": [{
            "groupId": "5c454e10-5934-49c6-96c7-6292ef0137a8",
            "group": {"default": "Under Development"},
            "title": {"default": title},
            "description": {"default": f"{title} consolidated dossier component"},
            "officeFabricIconFontName": "Page",
            "properties": {
                "description": title
            }
        }]
    }


def scaffold_master_detail_webpart(spec_path: Path, output_dir: Path) -> List[Path]:
    """
    Reads a specification file and scaffolds TypeScript, SCSS, and Manifest files.

    Args:
        spec_path: Path to input JSON spec file.
        output_dir: Output directory where web part files will be written.

    Returns:
        List of created Path objects.
    """
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    web_part_name = spec.get("webPartName", "MasterDetail")
    class_name = f"{web_part_name}WebPart"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. TypeScript code
    ts_content = generate_spfx_ts_code(spec)
    ts_file = output_dir / f"{class_name}.ts"
    ts_file.write_text(ts_content, encoding="utf-8")

    # 2. SCSS module template
    scss_template_path = Path(__file__).resolve().parent.parent / "assets" / "templates" / "MasterDetailWebPart.module.scss.template"
    if scss_template_path.exists():
        scss_content = scss_template_path.read_text(encoding="utf-8")
    else:
        scss_content = f".{web_part_name}Container {{ padding: 20px; }}\n"
    scss_file = output_dir / f"{class_name}.module.scss"
    scss_file.write_text(scss_content, encoding="utf-8")

    # 3. Manifest JSON
    manifest_data = generate_spfx_manifest(spec)
    manifest_file = output_dir / f"{class_name}.manifest.json"
    manifest_file.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")

    print(f"✅ Generated SPFx Master-Detail Web Part: {class_name} in {output_dir}")
    return [ts_file, scss_file, manifest_file]


def main() -> None:
    """CLI entrypoint for scaffold_spfx_master_detail.py."""
    parser = argparse.ArgumentParser(description="Scaffold SPFx Master-Detail Web Part boilerplate.")
    parser.add_argument("--spec", required=True, type=Path, help="Path to input JSON spec file.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Target directory for web part files.")

    args = parser.parse_args()
    scaffold_master_detail_webpart(args.spec, args.output_dir)


if __name__ == "__main__":
    main()
