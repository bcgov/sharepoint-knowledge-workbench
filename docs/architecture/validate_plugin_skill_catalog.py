#!/usr/bin/env python3
"""
Validates docs/architecture/complete-plugin-skill-catalog-after-phase-9.{json,md}:
computed totals must match the totals object's own claims, and the two files
must describe the same plugin/skill inventory. Proves the reported counts from
the actual entries rather than trusting hand-written numbers.

Usage: python3 docs/architecture/validate_plugin_skill_catalog.py
Exit 0 = all checks pass. Exit 1 = a mismatch was found, printed to stderr.
"""
import json
import re
import sys
from pathlib import Path

JSON_PATH = Path(__file__).parent / "complete-plugin-skill-catalog-after-phase-9.json"
MD_PATH = Path(__file__).parent / "complete-plugin-skill-catalog-after-phase-9.md"

WORKBENCH_EXISTING_STATUSES = ("existing", "existing_plus_phase_6_additions")
WORKBENCH_PHASE6_STATUSES = ("phase_6_planned", "phase_6_planned_new_plugin")
PHASE_6_TASK_0_16_PLUGIN = "structured-content-rendering"


def count_implemented_workbench_skills(data) -> set:
    """Only skills actually implemented today. review-manual-topics counts once
    (its native-sharepoint runtime is implemented; repository-claude is not)."""
    names = set()
    for plugin in data["plugins"]:
        if plugin.get("status") not in WORKBENCH_EXISTING_STATUSES + WORKBENCH_PHASE6_STATUSES:
            continue
        for skill in plugin["skills"]:
            if skill.get("status") == "implemented":
                names.add(skill["name"])
            elif skill.get("name") == "review-manual-topics":
                if any(r.get("status") == "implemented" for r in skill.get("runtimes", [])):
                    names.add(skill["name"])
    return names


def count_phase_6_skill_names(data) -> set:
    """All 30 skill names Phase 6 Task 0 approves, across all 4 plugins it touches."""
    names = set()
    for plugin in data["plugins"]:
        status = plugin.get("status")
        if status in WORKBENCH_PHASE6_STATUSES:
            for skill in plugin["skills"]:
                names.add(skill["name"])
        elif plugin["name"] == PHASE_6_TASK_0_16_PLUGIN:
            for skill in plugin["skills"]:
                if "phase_6" in skill.get("status", ""):
                    names.add(skill["name"])
    return names


def count_cmat_dispositions(data) -> dict:
    buckets = {
        "extraction_candidates": set(),
        "keep_cmat_specific": set(),
        "requires_human_decision": set(),
        "unverified_active_claim": set(),
        "planned_with_no_implementation": set(),
    }
    for plugin in data["plugins"]:
        if plugin.get("status") != "phase_9_candidate":
            continue
        for skill in plugin["skills"]:
            src = skill.get("cmat_source")
            if not src:
                continue
            disp = skill.get("disposition", "")
            cmat_status = skill.get("cmat_status", "")
            if cmat_status == "claimed_active_unverified":
                buckets["unverified_active_claim"].add(src)
            elif cmat_status == "planned_no_implementation":
                buckets["planned_with_no_implementation"].add(src)
            elif disp == "KEEP_CMAT_SPECIFIC":
                buckets["keep_cmat_specific"].add(src)
            elif disp == "REQUIRES_HUMAN_DECISION":
                buckets["requires_human_decision"].add(src)
            elif disp.startswith("PHASE_9_EXTRACT_AS_NEW_PLUGIN") or disp in (
                "PHASE_9_EXTRACT_TO_EXISTING_PLUGIN", "PHASE_9_MERGE_WITH_EXISTING_SKILL"
            ):
                buckets["extraction_candidates"].add(src)
            else:
                raise ValueError(f"Unclassified skill: {src} (cmat_status={cmat_status}, disposition={disp})")
    return buckets


def check_phase9_candidates_have_path_and_disposition(data) -> list:
    errors = []
    for plugin in data["plugins"]:
        if plugin.get("status") != "phase_9_candidate":
            continue
        for skill in plugin["skills"]:
            src = skill.get("cmat_source")
            if not src:
                continue
            if not skill.get("cmat_source_path"):
                errors.append(f"{plugin['name']}/{src}: missing cmat_source_path")
            if not skill.get("disposition"):
                errors.append(f"{plugin['name']}/{src}: missing disposition")
    return errors


def extract_md_json_skill_names(md_text: str) -> set:
    """Every backtick-quoted skill/CMAT-source name appearing in the Markdown catalog,
    for a coarse cross-check against the JSON's plugin/skill inventory."""
    names = set()
    for match in re.finditer(r"`([a-z][a-z0-9-]+)`", md_text):
        names.add(match.group(1))
    return names


def json_all_skill_and_cmat_names(data) -> set:
    names = set()
    for plugin in data["plugins"]:
        names.add(plugin["name"])
        for skill in plugin.get("skills", []):
            names.add(skill["name"])
            if skill.get("cmat_source"):
                names.add(skill["cmat_source"])
    for plugin in data.get("excluded_plugins", []):
        names.add(plugin["name"])
    return names


def main() -> int:
    data = json.loads(JSON_PATH.read_text())
    md_text = MD_PATH.read_text()
    errors = []

    # 1. JSON loads successfully - implicit (above).

    # 2. 30 unique Phase 6 skill names.
    phase_6_names = count_phase_6_skill_names(data)
    if len(phase_6_names) != 30:
        errors.append(f"Phase 6 skill names: computed {len(phase_6_names)}, expected 30: {sorted(phase_6_names)}")

    # 3. review-manual-topics appears once with two runtimes.
    rmt_count = 0
    rmt_runtimes = []
    for plugin in data["plugins"]:
        for skill in plugin.get("skills", []):
            if skill["name"] == "review-manual-topics":
                rmt_count += 1
                rmt_runtimes = [r["runtime"] for r in skill.get("runtimes", [])]
    if rmt_count != 1:
        errors.append(f"review-manual-topics: appears as {rmt_count} skill entries, expected exactly 1")
    if sorted(rmt_runtimes) != ["native-sharepoint", "repository-claude"]:
        errors.append(f"review-manual-topics runtimes: found {rmt_runtimes}, expected ['native-sharepoint', 'repository-claude']")

    # 4. 34 CMAT source skills; 5. CMAT categories sum exactly to 34.
    cmat = count_cmat_dispositions(data)
    total_cmat = sum(len(v) for v in cmat.values())
    if total_cmat != 34:
        errors.append(f"CMAT total: computed {total_cmat}, expected 34")
    claimed_total = data["totals"]["cmat_phase_9_source"]["phase_9_source_skills_audited"]
    if claimed_total != 34:
        errors.append(f"CMAT total claimed in totals block: {claimed_total}, expected 34")
    for key, expected_key in [
        ("extraction_candidates", "phase_9_extraction_candidates"),
        ("keep_cmat_specific", "keep_cmat_specific"),
        ("requires_human_decision", "requires_human_decision"),
        ("unverified_active_claim", "unverified_active_claim"),
        ("planned_with_no_implementation", "planned_with_no_implementation"),
    ]:
        computed = len(cmat[key])
        claimed = data["totals"]["cmat_phase_9_source"][expected_key]
        if computed != claimed:
            errors.append(f"{key}: computed {computed}, claimed {claimed}")

    # Workbench implemented (secondary, cross-checked against totals block).
    implemented = count_implemented_workbench_skills(data)
    claimed_implemented = data["totals"]["workbench"]["unique_installed_skill_names_currently_implemented"]
    if len(implemented) != claimed_implemented:
        errors.append(f"workbench implemented: computed {len(implemented)} {sorted(implemented)}, claimed {claimed_implemented}")

    # 6. Markdown and JSON plugin/skill inventories match (coarse cross-check: every
    #    JSON plugin name and skill/cmat_source name must appear as a backtick token
    #    somewhere in the Markdown catalog).
    md_names = extract_md_json_skill_names(md_text)
    json_names = json_all_skill_and_cmat_names(data)
    missing_from_md = json_names - md_names
    if missing_from_md:
        errors.append(f"names present in JSON but not found in Markdown: {sorted(missing_from_md)}")

    # 7. Every Phase 9 candidate has a source path and disposition.
    path_disp_errors = check_phase9_candidates_have_path_and_disposition(data)
    errors.extend(path_disp_errors)

    if errors:
        print("VALIDATION FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("ALL CHECKS PASSED:")
    print(f"  - JSON loads successfully")
    print(f"  - Phase 6 skill names: {len(phase_6_names)} (expected 30)")
    print(f"  - review-manual-topics: 1 entry, runtimes={sorted(rmt_runtimes)}")
    print(f"  - CMAT source skills: {total_cmat} (expected 34)")
    print(f"  - CMAT categories: extraction_candidates={len(cmat['extraction_candidates'])}, "
          f"keep_cmat_specific={len(cmat['keep_cmat_specific'])}, "
          f"requires_human_decision={len(cmat['requires_human_decision'])}, "
          f"unverified={len(cmat['unverified_active_claim'])}, "
          f"planned_empty={len(cmat['planned_with_no_implementation'])} "
          f"(sum={total_cmat})")
    print(f"  - workbench implemented: {len(implemented)} {sorted(implemented)}")
    print(f"  - Markdown/JSON name cross-check: all {len(json_names)} JSON plugin/skill/cmat_source names found in Markdown")
    print(f"  - Phase 9 candidates: all have cmat_source_path and disposition")
    return 0


if __name__ == "__main__":
    sys.exit(main())
