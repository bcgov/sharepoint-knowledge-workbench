#!/usr/bin/env python3
"""Purpose:
    Generate and check the repository plugin and skill catalog from manifests and skill files.

Key Input Dependencies:
    - .claude-plugin/marketplace.json
    - plugins/*/plugin.yaml
    - plugins/*/skills/*/SKILL.md
    - docs/architecture/seven-domain-plugin-skill-catalog.json and .md

Generate and verify the seven-domain plugin/skill catalog from the repository itself.

Writes docs/architecture/seven-domain-plugin-skill-catalog.{json,md} from plugins/*/plugin.yaml and
plugins/*/skills/*/SKILL.md, so the published counts are computed, never hand-written.

Usage:
    python3 plugins/sharepoint-workbench-setup/scripts/generate_domain_catalog.py            # check only
    python3 plugins/sharepoint-workbench-setup/scripts/generate_domain_catalog.py --write    # regenerate both files
    python3 plugins/sharepoint-workbench-setup/scripts/generate_domain_catalog.py --write --history-csv final-skill-names.csv
        (seeds the previous-identity history once; later runs preserve it from the existing JSON)

Checks: every package listed in .claude-plugin/marketplace.json exists; plugin.yaml `skills:` equals the skill
folders on disk; every SKILL.md `name:` equals its folder; skill names are unique across all packages; and the
committed catalog files equal what this script would generate now.

Function Index:
    - frontmatter_value
    - yaml_scalar
    - yaml_list
    - build
    - render_md
    - _load_history
    - _write_or_check_catalog
    - main
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
JSON_PATH = ROOT / "docs/architecture/seven-domain-plugin-skill-catalog.json"
MD_PATH = ROOT / "docs/architecture/seven-domain-plugin-skill-catalog.md"


# Read a scalar or folded-block value for one key from a skill Markdown frontmatter block.
def frontmatter_value(text, key):
    """Read a scalar or folded-block value for one key from a skill Markdown frontmatter block."""
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        return ""
    lines = match.group(1).split("\n")
    for index, line in enumerate(lines):
        if re.match(rf"^{key}:", line):
            value = line.split(":", 1)[1].strip()
            if value in (">", "|", ">-", "|-"):
                parts = []
                for follow in lines[index + 1:]:
                    if follow[:1] in (" ", "\t"):
                        parts.append(follow.strip())
                    else:
                        break
                return " ".join(parts)
            return value.strip("'\"")
    return ""


# Read one top-level scalar value from the repository YAML text.
def yaml_scalar(text, key):
    """Read one top-level scalar value from the repository YAML text."""
    match = re.search(rf"(?m)^{key}:\s*(.*)$", text)
    return match.group(1).strip().strip('"') if match else ""


# Read the indented item values belonging to one top-level YAML list key.
def yaml_list(text, key):
    """Read the indented item values belonging to one top-level YAML list key."""
    match = re.search(rf"(?m)^{key}:\n((?:[ \t]+-.*\n?)*)", text)
    return [line.strip()[1:].strip() for line in match.group(1).splitlines() if line.strip()] if match else []


# Assemble the catalog and validation problems from marketplace and plugin manifests.
def build(history):
    """Assemble the catalog and validation problems from marketplace and plugin manifests."""
    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    problems, packages = [], []
    seen = {}
    for entry in marketplace["plugins"]:
        name = entry["name"]
        base = ROOT / entry["source"].lstrip("./")
        manifest = base / "plugin.yaml"
        if not manifest.is_file():
            problems.append(f"{name}: missing plugin.yaml")
            continue
        text = manifest.read_text(encoding="utf-8")
        declared = yaml_list(text, "skills")
        folders = sorted(p.name for p in (base / "skills").iterdir() if p.is_dir()) if (base / "skills").is_dir() else []
        if sorted(declared) != folders:
            problems.append(f"{name}: plugin.yaml skills differ from skills/ on disk: {sorted(set(declared) ^ set(folders))}")
        skills = []
        for folder in folders:
            skill_md = base / "skills" / folder / "SKILL.md"
            body = skill_md.read_text(encoding="utf-8") if skill_md.is_file() else ""
            if frontmatter_value(body, "name") != folder:
                problems.append(f"{name}/{folder}: SKILL.md name is {frontmatter_value(body, 'name')!r}")
            if folder in seen:
                problems.append(f"duplicate skill name {folder} in {seen[folder]} and {name}")
            seen[folder] = name
            prior = history.get(folder, {})
            skills.append({"name": folder, "description": frontmatter_value(body, "description"),
                           "previous_name": prior.get("previous_name", folder), "previous_plugin": prior.get("previous_plugin", "")})
        packages.append({"name": name, "version": yaml_scalar(text, "version"), "description": yaml_scalar(text, "description"),
                         "agents": yaml_list(text, "agents"), "skill_count": len(skills), "skills": skills})
    catalog = {"schema": 1, "package_count": len(packages), "skill_count": sum(p["skill_count"] for p in packages),
               "unique_skill_names": len(seen), "packages": packages}
    return catalog, problems


# Render the catalog data as the generated Markdown summary and skill table.
def render_md(catalog):
    """Render the catalog data as the generated Markdown summary and skill table."""
    lines = ["# Seven-domain plugin and skill catalog", "",
             "Generated by `plugins/sharepoint-workbench-setup/scripts/generate_domain_catalog.py` from the repository; do not edit by hand.", "",
             f"**{catalog['package_count']} plugins, {catalog['skill_count']} skills ({catalog['unique_skill_names']} unique names).**", "",
             "| Plugin | Version | Skills | Agents |", "|---|---|---|---|"]
    for package in catalog["packages"]:
        lines.append(f"| [`{package['name']}`](../../plugins/{package['name']}/README.md) | {package['version']} | {package['skill_count']} | {len(package['agents'])} |")
    for package in catalog["packages"]:
        lines += ["", f"## `{package['name']}`", "", package["description"], "",
                  "| Skill | Previous name | Previous plugin |", "|---|---|---|"]
        for skill in package["skills"]:
            previous = skill["previous_name"] if skill["previous_name"] != skill["name"] else "(unchanged)"
            lines.append(f"| `{skill['name']}` | {('`' + previous + '`') if previous != '(unchanged)' else previous} | `{skill['previous_plugin']}` |")
        if package["agents"]:
            lines += ["", "Agents: " + ", ".join(f"`{a}`" for a in package["agents"])]
    return "\n".join(lines) + "\n"


# Load previous skill identities from a supplied CSV or the current catalog.
def _load_history(argv: list[str]) -> dict:
    """Load previous skill identities from a supplied CSV or the current catalog."""
    history = {}
    if "--history-csv" in argv:
        for row in csv.DictReader(open(argv[argv.index("--history-csv") + 1], encoding="utf-8")):
            history[row["final_name"]] = {"previous_name": row["current_name"], "previous_plugin": row["current_plugin"]}
    elif JSON_PATH.is_file():
        for package in json.loads(JSON_PATH.read_text(encoding="utf-8"))["packages"]:
            for skill in package["skills"]:
                history[skill["name"]] = {"previous_name": skill["previous_name"], "previous_plugin": skill["previous_plugin"]}
    return history


# Write generated catalog files or report which committed outputs are stale.
def _write_or_check_catalog(write: bool, json_text: str, md_text: str) -> list[str]:
    """Write generated catalog files or report which committed outputs are stale."""
    problems = []
    if write:
        JSON_PATH.write_text(json_text, encoding="utf-8")
        MD_PATH.write_text(md_text, encoding="utf-8")
    else:
        if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != json_text:
            problems.append("seven-domain-plugin-skill-catalog.json is stale; run with --write")
        if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != md_text:
            problems.append("seven-domain-plugin-skill-catalog.md is stale; run with --write")
    return problems


# Run the catalog consistency check and optionally write regenerated JSON and Markdown outputs.
def main(argv: list[str]) -> int:
    """Run the catalog consistency check and optionally write regenerated JSON and Markdown outputs."""
    write = "--write" in argv
    catalog, problems = build(_load_history(argv))
    json_text = json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"
    md_text = render_md(catalog)
    problems.extend(_write_or_check_catalog(write, json_text, md_text))
    if problems:
        print("CATALOG CHECK FAILED:\n  - " + "\n  - ".join(problems), file=sys.stderr)
        return 1
    print(f"catalog ok: {catalog['package_count']} plugins, {catalog['skill_count']} skills, {catalog['unique_skill_names']} unique")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
