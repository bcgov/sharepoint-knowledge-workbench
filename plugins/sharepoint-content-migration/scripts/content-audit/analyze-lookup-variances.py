"""
analyze-lookup-variances.py (sp-audit-list Comprehensive Analyzer)

Full-spectrum parity, row-level discrepancy, and granular lookup reconciliation engine:
  - SP2016 source: .agents/scratch/pii-data/<ListName>-sp2016-onprem.csv
  - SPO PROD target: .agents/scratch/pii-data/<ListName>-spo-prod.csv

Key Architectural Features:
  1. Tripartite Natural Key Matching: Joins items by canonical business key (Case ID, Title) or id-mapping-verified.json for Persons.
  2. Suffix Skew Diagnostics: Measures and samples Case ID numeric suffix vs SharePoint integer ID divergence.
  3. Granular Lookup Reconciliation: Evaluates every single-value and multi-value lookup column (Matching vs Blank vs Stale Old IDs vs False Misbinds).
  4. Full-Column Parity: Compares text, choice, rich text (HTML-stripped), dates (ISO-normalized), and numbers across all business columns.
  5. 100% Zero-PII Guarantee: Outputs only anonymized case keys, structural metrics, and statistical frequency counts.
  6. Outputs:
       - Console: Multi-section rich terminal report with top column variance frequencies and sample diagnostics.
       - Console Log: .agents/scratch/audit-reports/CONSOLE-OUTPUT-LOG.md (full duplicate of console output)
       - Markdown: .agents/scratch/audit-reports/SITE-FULL-CONTENT-PARITY-REPORT.md
       - Discrepancy CSVs:
           .agents/scratch/audit-reports/<ListName>-variances-only.csv
           .agents/scratch/audit-reports/site-full-content-parity-audit.csv
"""

import os
import re
import csv
import json
import sys
import argparse
from pathlib import Path
from collections import defaultdict

class Tee:
    """Duplicates writes to multiple streams (e.g. console + log file)."""
    def __init__(self, *streams):
        self.streams = streams
    def write(self, data):
        for s in self.streams:
            s.write(data)
    def flush(self):
        for s in self.streams:
            s.flush()

def normalize(val):
    if val is None:
        return ""
    s = str(val).strip()
    
    # 1. HTML tag & entity stripping for rich text / multi-line notes
    if "<" in s and ">" in s:
        s = re.sub(r'<style[^>]*>.*?</style>', '', s, flags=re.DOTALL | re.IGNORECASE)
        s = re.sub(r'<script[^>]*>.*?</script>', '', s, flags=re.DOTALL | re.IGNORECASE)
        s = re.sub(r'<[^>]+>', ' ', s)
    
    # Decode common HTML entities
    s = s.replace('&nbsp;', ' ').replace('&#160;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
    
    # 2. Normalize numbers/floats
    try:
        f = float(s)
        if f.is_integer():
            return str(int(f))
        return f"{f:.2f}"
    except ValueError:
        pass

    # 3. Normalize ISO dates / Timestamps
    m = re.match(r'^(\d{4}[-/]\d{2}[-/]\d{2})', s)
    if m:
        return m.group(1).replace('/', '-')
    
    # Handle MM/DD/YYYY dates
    m2 = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if m2:
        m_month, m_day, m_year = m2.groups()
        return f"{m_year}-{int(m_month):02d}-{int(m_day):02d}"

    # 4. Collapse whitespace
    return " ".join(s.lower().split())

def sanitize_identifier(raw_id, onprem_id=None):
    if not raw_id:
        return f"Item #{onprem_id}" if onprem_id else "Item"
    raw_str = str(raw_id).strip()
    if re.match(r'^(ITAU|PIO|ICM|SMAT|CSB|CASE)_[0-9]{4}_[0-9]+$', raw_str, re.IGNORECASE):
        return raw_str
    if raw_str.isdigit():
        return f"Item #{raw_str}"
    if raw_str.upper().startswith("ITEM_"):
        return raw_str
    if onprem_id:
        return f"Row (On-Prem ID #{onprem_id})"
    return "Row Item"


def count_case_id_suffix_mismatches(rows):
    count = 0
    for row in rows:
        item_id = row.get("ID") if row.get("ID") is not None else row.get("Id")
        case_id = row.get("Case_x0020_ID") or row.get("CaseID") or row.get("Title")
        if item_id is None or not case_id:
            continue
        m = re.search(r'(\d+)\s*$', str(case_id).strip())
        if not m:
            count += 1
            continue
        trailing_digits = m.group(1)
        item_id_str = str(item_id).strip()
        width = len(item_id_str)
        candidate = trailing_digits[-width:] if width > 0 else trailing_digits
        if candidate != item_id_str:
            count += 1
    return count


def main():
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parents[3] if len(script_dir.parents) >= 4 else Path.cwd()

    parser = argparse.ArgumentParser(description="Full-Spectrum List & Lookup Variance Analyzer (Zero PII)")
    parser.add_argument("--data-dir", default=str(repo_root / ".agents" / "scratch" / "pii-data"), help="Directory containing CSV exports")
    parser.add_argument("--matrix-path", default=str(repo_root / "plugins" / "sharepoint-migration" / "references" / "wave-dependency-matrix.json"), help="Wave matrix path")
    parser.add_argument("--mapping-path", default=str(repo_root / ".agents" / "scratch" / "audit-reports" / "id-mapping-verified.json"), help="Persons verified ID mapping path")
    parser.add_argument("--output-md", default=str(repo_root / ".agents" / "scratch" / "audit-reports" / "SITE-FULL-CONTENT-PARITY-REPORT.md"), help="Executive report output path")
    parser.add_argument("--output-csv", default=str(repo_root / ".agents" / "scratch" / "audit-reports" / "site-full-content-parity-audit.csv"), help="Discrepancies CSV output path")
    parser.add_argument("--console-log", default=str(repo_root / ".agents" / "scratch" / "audit-reports" / "CONSOLE-OUTPUT-LOG.md"), help="Full console output log (markdown) path")
    parser.add_argument("--list-name", default="ALL", help="Specific list name to analyze or 'ALL'")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    matrix_path = Path(args.matrix_path)
    mapping_path = Path(args.mapping_path)
    output_md_path = Path(args.output_md)
    output_csv_path = Path(args.output_csv)

    output_md_path.parent.mkdir(parents=True, exist_ok=True)
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    console_log_path = Path(args.console_log)
    console_log_path.parent.mkdir(parents=True, exist_ok=True)
    log_file = open(console_log_path, "w", encoding="utf-8")
    log_file.write("# Console Output Log — Full-Spectrum Variance Analysis\n\n```text\n")
    original_stdout = sys.stdout
    sys.stdout = Tee(original_stdout, log_file)

    # 1. Load Matrix & Setup Column Lookups
    field_maps = defaultdict(dict)
    exclusions_by_list = defaultdict(set)
    person_lookups_by_list = defaultdict(set)
    lookup_definitions_by_list = defaultdict(dict)

    if matrix_path.exists():
        with open(matrix_path, "r", encoding="utf-8") as f:
            matrix_data = json.load(f)
            for entry in matrix_data:
                d_name = entry.get("destinationName")
                if not d_name:
                    continue
                fmap = {}
                for fr in entry.get("fieldRenames", []):
                    op_col = fr.get("onPrem")
                    sp_col = fr.get("spo")
                    if op_col and sp_col:
                        fmap[op_col] = sp_col
                    if "Lookup" in fr.get("type", ""):
                        target_list = fr.get("lookupList", "Unknown")
                        lookup_definitions_by_list[d_name][sp_col] = {
                            "onPrem": op_col,
                            "target": target_list,
                            "type": fr.get("type")
                        }
                        if target_list == "Persons":
                            person_lookups_by_list[d_name].add(sp_col)
                field_maps[d_name] = fmap

                for ex in entry.get("fieldExclusions", []):
                    ex_name = ex.get("sp2016InternalName") or ex.get("field")
                    if ex_name:
                        exclusions_by_list[d_name].add(ex_name)

    # Add standard CMAT lookup definitions for complete list coverage
    known_defaults = {
        "ITAU_Cases": {
            "Subjects_Accused": ("subject_x0028_s_x0029__x0020__x0Id", "Persons"),
            "Subjects_Victim_Witness": ("subject_x0028_s_x0029__x0020__x00Id", "Persons"),
            "Subjects_Gov_Employee": ("subject_x0028_s_x0029__x0020__x01Id", "Persons"),
            "Subjects_Other": ("subject_x0028_s_x0029__x0020__x02Id", "Persons"),
            "Affected_Crown": ("affected_x0020__x002d__x0020_CroId", "Persons"),
            "Affected_Judiciary": ("affected_x0020__x002d__x0020_JudId", "Persons"),
            "Affected_Gov_Employee": ("affected_x0020__x002d__x0020_GovId", "Persons"),
            "Affected_Other": ("affected_x0020__x002d__x0020_OthId", "Persons")
        },
        "PIO_Cases": {
            "Subjects_Accused": ("subject_x0028_s_x0029__x0020__x0Id", "Persons"),
            "Subjects_Victim_Witness": ("subject_x0028_s_x0029__x0020__x00Id", "Persons"),
            "Subjects_Gov_Employee": ("subject_x0028_s_x0029__x0020__x01Id", "Persons"),
            "Subjects_Other": ("subject_x0028_s_x0029__x0020__x02Id", "Persons"),
            "Affected_Crown": ("affected_x0020__x002d__x0020_CroId", "Persons"),
            "Affected_Judiciary": ("affected_x0020__x002d__x0020_JudId", "Persons"),
            "Affected_Gov_Employee": ("affected_x0020__x002d__x0020_GovId", "Persons"),
            "Affected_Other": ("affected_x0020__x002d__x0020_OthId", "Persons")
        },
        "ICM_Cases": {
            "Subjects_Accused": ("subject_x0028_s_x0029__x0020__x0Id", "Persons"),
            "Subjects_Victim_Witness": ("subject_x0028_s_x0029__x0020__x00Id", "Persons"),
            "Subjects_Gov_Employee": ("subject_x0028_s_x0029__x0020__x01Id", "Persons"),
            "Subjects_Other": ("subject_x0028_s_x0029__x0020__x02Id", "Persons"),
            "Affected_Crown": ("affected_x0020__x002d__x0020_CroId", "Persons"),
            "Affected_Judiciary": ("affected_x0020__x002d__x0020_JudId", "Persons"),
            "Affected_Gov_Employee": ("affected_x0020__x002d__x0020_GovId", "Persons"),
            "Affected_Other": ("affected_x0020__x002d__x0020_OthId", "Persons")
        },
        "ITAU_Narratives": { "Related_to_Person": ("Related_x0020_to_x0020_PersonId", "Persons") },
        "PIO_Narratives": { "Related_to_Person": ("Related_x0020_to_x0020_PersonId", "Persons") },
        "ICM_Narratives": { "Related_to_Person": ("Related_x0020_to_x0020_PersonId", "Persons") },
        "YAL": { "PersonID": ("PersonID", "Persons"), "Known_Associates": ("Known_x0020_AssociatesId", "Persons") },
        # NOTE (2026-09-01 Phase 2 review): onPrem column corrected to the real exported
        # CSV header "Related_x0020_to_x0020_CaseId" (verified against raw pii-data exports).
        # The previous guessed names ("...ITAU_x0Id" / "...PIO_x00Id") never matched any
        # real column, which silently produced "0 Source Pointers in Dataset" for every
        # Case_Tasks/Log_Entries/Documents list below.
        "ITAU_Case_Tasks": { "Related_to_ITAU_Case": ("Related_x0020_to_x0020_CaseId", "ITAU_Cases") },
        "PIO_Case_Tasks": { "Related_to_PIO_Case": ("Related_x0020_to_x0020_CaseId", "PIO_Cases") },
        "ITAU_Log_Entries": { "Related_to_ITAU_Case": ("Related_x0020_to_x0020_CaseId", "ITAU_Cases") },
        "PIO_Log_Entries": { "Related_to_PIO_Case": ("Related_x0020_to_x0020_CaseId", "PIO_Cases") },
        "ITAU_Documents": { "Related_to_ITAU_Case": ("Related_x0020_to_x0020_ITAU_x0020_Case_x003A_Id", "ITAU_Cases") },
        "PIO_Documents": { "Related_to_PIO_Case": ("Related_x0020_to_x0020_PIO_x0020_Case_x003A_Id", "PIO_Cases") }
    }

    for l_key, l_dict in known_defaults.items():
        for sp_col, (op_col, tgt) in l_dict.items():
            lookup_definitions_by_list[l_key][sp_col] = { "onPrem": op_col, "target": tgt, "type": "Lookup" }
            if tgt == "Persons":
                person_lookups_by_list[l_key].add(sp_col)
            if op_col not in field_maps[l_key]:
                field_maps[l_key][op_col] = sp_col

    id_map = {}
    id_map_locations = [
        mapping_path,
        repo_root / ".agents" / "scratch" / "id-mapping-verified.json",
        repo_root / ".agents" / "scratch" / "audit-reports" / "id-mapping-verified.json",
        repo_root / "plugins" / "sharepoint-migration" / "logs" / "id-mappings.json"
    ]
    for p in id_map_locations:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    id_map = json.load(f)
                    break
            except Exception:
                pass

    # 2. Discover available CSV pairs in data_dir
    seen_bases = set()
    target_lists = []
    for pattern in ["*-sp2016-onprem.csv", "*-full-onprem.csv"]:
        for op_f in data_dir.glob(pattern):
            base_name = op_f.name.replace("-sp2016-onprem.csv", "").replace("-full-onprem.csv", "")
            if base_name in seen_bases:
                continue
            if args.list_name != "ALL" and args.list_name.lower() not in base_name.lower():
                continue
            spo_f = data_dir / f"{base_name}-spo-prod.csv"
            if not spo_f.exists():
                spo_f = data_dir / f"{base_name}-full-spo.csv"
            if spo_f.exists():
                seen_bases.add(base_name)
                target_lists.append((base_name, op_f, spo_f))

    if not target_lists:
        print(f"Error: No matching paired datasets found in {data_dir} for scope '{args.list_name}'.")
        return

    summary_rows = []
    all_discrepancies = []
    all_lookup_metrics_by_list = defaultdict(list)
    all_skew_samples = defaultdict(list)
    all_missing_lookup_samples = defaultdict(list)
    all_false_lookup_samples = defaultdict(list)

    ignore_cols = {
        "id", "__sp_id__", "modified", "created", "author", "editor",
        "attachments", "guid", "contenttype", "contenttypeid",
        "filesystemobjecttype", "iscurrent", "dob_plain_text"
    }

    for l_name, op_path, spo_path in sorted(target_lists):
        # Load On-Prem Rows
        onprem_rows = []
        with open(op_path, mode="r", encoding="utf-8-sig", errors="ignore") as f:
            reader = csv.DictReader(f)
            for r in reader:
                onprem_rows.append(r)

        # Load SPO Rows
        spo_by_id = {}
        spo_by_natural = {}
        with open(spo_path, mode="r", encoding="utf-8-sig", errors="ignore") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rid = str(r.get("ID", "")).strip()
                if rid:
                    spo_by_id[rid] = r
                case_val = str(r.get("Case_x0020_ID") or r.get("CaseID") or r.get("Title") or "").strip()
                if case_val:
                    spo_by_natural[case_val.upper()] = r

        fmap = field_maps.get(l_name, {})
        excls = exclusions_by_list[l_name]
        person_lookups = person_lookups_by_list[l_name]
        lookups_def = lookup_definitions_by_list.get(l_name, {})

        lookup_col_stats = defaultdict(lambda: {
            "total_pointers": 0,
            "matching": 0,
            "blank_in_spo": 0,
            "stale_old_id": 0,
            "misbound": 0,
            "target": "Unknown"
        })

        for sp_col, info in lookups_def.items():
            lookup_col_stats[sp_col]["target"] = info["target"]

        co_existing_count = 0
        perfect_match_count = 0
        differing_row_count = 0
        group1_key_match_diffs = 0
        group2_missing_in_spo = 0
        col_diff_counts = defaultdict(int)
        cat_issues = defaultdict(int)
        case_suffix_mismatch_count = 0
        list_discrepancies = []

        for op_row in onprem_rows:
            op_id = str(op_row.get("ID") or op_row.get("Id") or "").strip()
            spo_row = None
            case_key = ""

            if l_name == "Persons" and id_map:
                if op_id in id_map:
                    target_spo_id = str(id_map[op_id])
                    if target_spo_id in spo_by_id:
                        spo_row = spo_by_id[target_spo_id]
                        case_key = f"Person (Old ID #{op_id} -> SPO #{target_spo_id})"
            elif "Cases" in l_name:
                raw_case_key = str(op_row.get("Case_x0020_ID") or op_row.get("CaseID") or op_row.get("Title") or f"ITEM_{op_id}").strip()
                case_key = sanitize_identifier(raw_case_key, op_id)
                if raw_case_key.upper() in spo_by_natural:
                    spo_row = spo_by_natural[raw_case_key.upper()]
                elif op_id in spo_by_id:
                    spo_row = spo_by_id[op_id]

                # Check numeric suffix divergence on the current live SPO record, because
                # the drift bug is caused by SPO Case_x0020_ID values no longer matching
                # their own Item ID, not by the source on-prem rows.
                if spo_row is not None:
                    spo_case_id = str(spo_row.get("Case_x0020_ID") or spo_row.get("CaseID") or "").strip()
                    spo_item_id = str(spo_row.get("ID") or "").strip()
                    if spo_case_id and spo_item_id:
                        m_sfx = re.search(r'(\d+)$', spo_case_id)
                        if m_sfx:
                            suffix_digits = m_sfx.group(1)
                            item_id_width = len(spo_item_id)
                            match_candidate = suffix_digits[-item_id_width:] if item_id_width > 0 else suffix_digits
                            if match_candidate != spo_item_id:
                                case_suffix_mismatch_count += 1
                                col_diff_counts["CASE_ID_SUFFIX_MISMATCH"] += 1
                                if len(all_skew_samples[l_name]) < 5:
                                    all_skew_samples[l_name].append({
                                        "Case": case_key,
                                        "SPOCaseID": spo_case_id,
                                        "TrailingSuffix": suffix_digits,
                                        "RightmostMatchCandidate": match_candidate,
                                        "SpoItemID": spo_item_id,
                                        "OnPremRowID": op_id,
                                        "MismatchType": "SPO_ROW_SUFFIX_DRIFT"
                                    })

                # Separate on-prem source check retained for audit context so future runs can
                # distinguish whether the source export itself is already inconsistent.
                m_sfx = re.search(r'(\d+)$', raw_case_key)
                if m_sfx and op_id:
                    sfx_int = int(m_sfx.group(1))
                    if sfx_int != int(op_id):
                        col_diff_counts["CASE_ID_SUFFIX_ONPREM_MISMATCH"] += 1
            else:
                case_key = f"Row #{op_id}"
                if op_id in spo_by_id:
                    spo_row = spo_by_id[op_id]

            if not spo_row:
                group2_missing_in_spo += 1
                col_diff_counts["ROW_MISSING_IN_SPO"] += 1
                item_disc = {
                    "ListName": l_name,
                    "CaseIdentifier": case_key,
                    "OnPremID": op_id,
                    "SpoItemID": "MISSING_IN_SPO",
                    "TotalVariances": 1,
                    "DifferingColumns": "ROW_MISSING_IN_SPO"
                }
                list_discrepancies.append(item_disc)
                all_discrepancies.append(item_disc)
                continue

            co_existing_count += 1
            differing_cols = []

            # Track Persons Item ID Shift
            if l_name == "Persons":
                spo_id_val = str(spo_row.get("ID", "")).strip()
                if op_id != spo_id_val:
                    differing_cols.append(f"Item_ID_Shift (Old #{op_id} -> SPO #{spo_id_val})")
                    col_diff_counts["Item_ID_Shift (+18k Offset)"] += 1
                    cat_issues["LookupDrift"] += 1

            # Granular Lookup Pointer Audit
            for sp_col, info in lookups_def.items():
                op_col = info["onPrem"]
                tgt_list = info["target"]
                raw_op_val = str(op_row.get(op_col) or op_row.get(sp_col) or "").strip()
                raw_spo_val = str(spo_row.get(sp_col) or spo_row.get(op_col) or "").strip()

                if not raw_op_val and not raw_spo_val:
                    continue

                op_ids = re.findall(r'\d+', raw_op_val)
                spo_ids = re.findall(r'\d+', raw_spo_val)

                for old_ptr in op_ids:
                    lookup_col_stats[sp_col]["total_pointers"] += 1
                    expected_target_id = str(id_map.get(old_ptr, old_ptr)) if tgt_list == "Persons" and id_map else old_ptr

                    if expected_target_id in spo_ids:
                        lookup_col_stats[sp_col]["matching"] += 1
                    elif len(spo_ids) == 0:
                        lookup_col_stats[sp_col]["blank_in_spo"] += 1
                        if len(all_missing_lookup_samples[f"{l_name}.{sp_col}"]) < 4:
                            all_missing_lookup_samples[f"{l_name}.{sp_col}"].append({
                                "Case": case_key,
                                "OnPremID": old_ptr,
                                "ExpectedSpoID": expected_target_id
                            })
                    elif old_ptr in spo_ids:
                        lookup_col_stats[sp_col]["stale_old_id"] += 1
                        if len(all_missing_lookup_samples[f"{l_name}.{sp_col}"]) < 4:
                            all_missing_lookup_samples[f"{l_name}.{sp_col}"].append({
                                "Case": case_key,
                                "OnPremID": old_ptr,
                                "ExpectedSpoID": f"{expected_target_id} (Holds SP2016 ID {old_ptr})"
                            })
                    else:
                        lookup_col_stats[sp_col]["misbound"] += 1
                        if len(all_false_lookup_samples[f"{l_name}.{sp_col}"]) < 4:
                            all_false_lookup_samples[f"{l_name}.{sp_col}"].append({
                                "Case": case_key,
                                "OnPremID": old_ptr,
                                "ExpectedSpoID": expected_target_id,
                                "ActualSpoID": ",".join(spo_ids)
                            })

            # General Column Parity
            for op_col, val_op_raw in op_row.items():
                if not op_col or op_col.lower() in ignore_cols or op_col.startswith("_") or op_col in excls:
                    continue

                spo_col = fmap.get(op_col, op_col)
                if spo_col not in spo_row and op_col in spo_row:
                    spo_col = op_col
                if spo_col not in spo_row:
                    continue

                val_spo_raw = spo_row.get(spo_col, "")
                v1 = normalize(val_op_raw)
                v2 = normalize(val_spo_raw)

                # Person lookup translation check
                if (spo_col in person_lookups or spo_col in lookups_def) and id_map and v1:
                    exp_parts = []
                    for oid in re.findall(r'\d+', v1):
                        exp_parts.append(str(id_map.get(oid, oid)))
                    if sorted(exp_parts) == sorted(re.findall(r'\d+', v2)):
                        continue

                if v1 != v2:
                    differing_cols.append(spo_col)
                    col_diff_counts[spo_col] += 1
                    if spo_col in person_lookups or spo_col in lookups_def:
                        cat_issues["LookupDrift"] += 1
                    elif not v2 and v1:
                        cat_issues["DroppedBlank"] += 1
                    else:
                        cat_issues["TextVariance"] += 1

            if len(differing_cols) == 0:
                perfect_match_count += 1
            else:
                differing_row_count += 1
                group1_key_match_diffs += 1
                item_disc = {
                    "ListName": l_name,
                    "CaseIdentifier": case_key,
                    "OnPremID": op_id,
                    "SpoItemID": spo_row.get("ID", ""),
                    "TotalVariances": len(differing_cols),
                    "DifferingColumns": "; ".join(differing_cols)
                }
                list_discrepancies.append(item_disc)
                all_discrepancies.append(item_disc)

        score = round((perfect_match_count / co_existing_count) * 100, 2) if co_existing_count else 100.0
        top_diffs = ", ".join([f"{k} ({v})" for k, v in sorted(col_diff_counts.items(), key=lambda x: x[1], reverse=True)[:3]])
        
        summary_rows.append({
            "ListName": l_name,
            "TotalSource": len(onprem_rows),
            "TotalSPO": len(spo_by_id) if spo_by_id else len(spo_by_natural),
            "CoExisting": co_existing_count,
            "Perfect": perfect_match_count,
            "Differing": differing_row_count,
            "Group1_Diffs": group1_key_match_diffs,
            "Group2_Missing": group2_missing_in_spo,
            "Score": score,
            "TopDiffs": top_diffs,
            "LookupDrift": cat_issues["LookupDrift"],
            "DroppedBlanks": cat_issues["DroppedBlank"],
            "TextVariances": cat_issues["TextVariance"],
            "ColumnDetails": dict(col_diff_counts),
            "SuffixMismatch": case_suffix_mismatch_count
        })

        # Save single-list variance CSV
        list_var_csv = output_csv_path.parent / f"{l_name}-variances-only.csv"
        if list_discrepancies:
            with open(list_var_csv, mode="w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["ListName", "CaseIdentifier", "OnPremID", "SpoItemID", "TotalVariances", "DifferingColumns"])
                writer.writeheader()
                for d in list_discrepancies:
                    writer.writerow(d)

        # Store lookup metrics for this list
        for sp_col, stat in lookup_col_stats.items():
            all_lookup_metrics_by_list[l_name].append({
                "ColumnName": sp_col,
                "TargetList": stat["target"],
                "TotalPointers": stat["total_pointers"],
                "Matching": stat["matching"],
                "Blank": stat["blank_in_spo"],
                "Stale": stat["stale_old_id"],
                "Misbound": stat["misbound"]
            })

    # Output Full Console Report Matching Expected Standard
    for r in summary_rows:
        l_name = r["ListName"]
        print("=" * 85)
        print(f" FULL VARIANCE AUDIT REPORT: {l_name.upper()} (SP2016 vs SPO)")
        print("=" * 85)
        print(f"Total SP2016 Records Loaded : {r['TotalSource']}")
        print(f"Total SPO Records Loaded    : {r['TotalSPO']}")
        print("\n" + "=" * 85)
        print(" AUDIT RESULTS GROUPED BY PRIMARY KEY ALIGNMENT (ZERO PII)")
        print("=" * 85)
        print(f"Total SP2016 Records Processed          : {r['TotalSource']}")
        print(f"  * 100% Perfect Matches (0 Diffs)      : {r['Perfect']} ({r['Score']}%)")
        print(f"  * Discrepant Rows (>= 1 Diff)         : {r['Differing'] + r['Group2_Missing']}")
        print(f"      - Group 1 (Key Matches, Field Diffs)      : {r['Group1_Diffs']}")
        print(f"      - Group 2 (Key Mismatches / Missing)      : {r['Group2_Missing']}")
        print(f"  * Case ID Suffix != Item ID Discrepancies     : {r['SuffixMismatch']}")
        print("=" * 85)

        # Dedicated Lookup Pointer Section for this List
        l_lookups = all_lookup_metrics_by_list.get(l_name, [])
        if l_lookups:
            print("\n" + "=" * 85)
            print(f" DEDICATED LOOKUP POINTER HEALTH AUDIT: {l_name.upper()}")
            print("=" * 85)
            print(f"{'Lookup Column Name':<26} | {'Target':<10} | {'Total':<6} | {'Matched (SPO)':<14} | {'Blank':<7} | {'Stale':<7} | {'Status'}")
            print("-" * 85)
            for lm in l_lookups:
                tot = lm["TotalPointers"]
                mat = lm["Matching"]
                mat_pct = round((mat / tot) * 100, 1) if tot else 100.0
                mat_str = f"{mat} ({mat_pct}%)"
                status_str = "Fully Resolved"
                if tot == 0:
                    status_str = "0 Source Pointers"
                elif lm["Blank"] > 0 and lm["Stale"] > 0:
                    status_str = f"{lm['Blank']} Blank, {lm['Stale']} Stale"
                elif lm["Blank"] > 0:
                    status_str = f"{lm['Blank']} Blank in SPO"
                elif lm["Stale"] > 0:
                    status_str = f"{lm['Stale']} Stale SP2016 IDs"
                elif lm["Misbound"] > 0:
                    status_str = f"{lm['Misbound']} Misbound Target"

                print(f"{lm['ColumnName']:<26} | {lm['TargetList']:<10} | {tot:<6} | {mat_str:<14} | {lm['Blank']:<7} | {lm['Stale']:<7} | {status_str}")
            print("=" * 85)

        # Top Columns with Variances
        if r["ColumnDetails"]:
            print(f"\nTop Columns with Variances (Frequency):")
            for col_name, cnt in sorted(r["ColumnDetails"].items(), key=lambda x: x[1], reverse=True)[:10]:
                pct = round((cnt / r["CoExisting"]) * 100, 1) if r["CoExisting"] else 0.0
                print(f"  * {col_name:<32}: {cnt:>5} row(s) ({pct:>4.1f}%)")
            print("=" * 85)

        list_var_csv = output_csv_path.parent / f"{l_name}-variances-only.csv"
        print(f"Saved {r['Differing'] + r['Group2_Missing']} discrepant rows to: {list_var_csv}\n")

    # 3. Output Executive Markdown Report
    md_lines = [
        "# Site-Wide Full Content & Lookup Parity Executive Report (SP2016 vs SPO PROD)",
        "> **Privacy Guarantee**: 100% Zero PII. All comparisons evaluate structural parity and pointer health.",
        "> **Generated**: Live dynamic calculation across active paired datasets.\n",
        "## 1. Full Content Parity Summary by List\n",
        "| List Name | Source Rows | Co-Existing | Perfect Rows (0 Diffs) | Differing Rows | Parity Rate | Top Differing Columns |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]

    total_src = sum(r["TotalSource"] for r in summary_rows)
    total_coex = sum(r["CoExisting"] for r in summary_rows)
    total_perf = sum(r["Perfect"] for r in summary_rows)
    total_diff = sum(r["Differing"] for r in summary_rows)

    for r in summary_rows:
        md_lines.append(f"| **{r['ListName']}** | {r['TotalSource']:,} | {r['CoExisting']:,} | {r['Perfect']:,} | {r['Differing']:,} | **{r['Score']}%** | {r['TopDiffs']} |")

    site_score = round((total_perf / total_coex) * 100, 2) if total_coex else 100.0
    md_lines.append(f"| **SITE-WIDE TOTALS** | **{total_src:,}** | **{total_coex:,}** | **{total_perf:,}** | **{total_diff:,}** | **{site_score}%** | **-** |\n")

    md_lines.extend([
        "## 2. Root Cause Categorization of Discrepancies\n",
        "| List Name | Lookup Pointer Drift | Dropped / Blank Values | Text / Choice / Note Variances | Missing in SPO |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ])

    for r in summary_rows:
        md_lines.append(f"| **{r['ListName']}** | {r['LookupDrift']:,} | {r['DroppedBlanks']:,} | {r['TextVariances']:,} | {r['Group2_Missing']:,} |")

    md_lines.extend([
        "\n## 3. Dedicated Dynamic Lookup Column & Pointer Integrity Analysis by List\n"
    ])

    for l_name, l_lookups in all_lookup_metrics_by_list.items():
        md_lines.append(f"### {l_name} Lookup Column Pointer Health\n")
        md_lines.append("| Lookup Column Name | Target List | Total Source Pointers | #1 Pointers Matching (Remapped/Valid) | #2 Pointer Variances (Stale / Blank) | Primary Root Cause Category |")
        md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for lm in l_lookups:
            tot = lm["TotalPointers"]
            mat = lm["Matching"]
            mat_pct = round((mat / tot) * 100, 1) if tot else 100.0
            var_cnt = tot - mat
            var_pct = round((var_cnt / tot) * 100, 1) if tot else 0.0

            cause_parts = []
            if lm["Blank"] > 0:
                cause_parts.append(f"{lm['Blank']} Blank in SPO")
            if lm["Stale"] > 0:
                cause_parts.append(f"{lm['Stale']} Stale Old SP2016 IDs")
            if lm["Misbound"] > 0:
                cause_parts.append(f"{lm['Misbound']} Misbound Target")
            
            cause_str = ", ".join(cause_parts) if cause_parts else "Fully Resolved"
            if tot == 0:
                cause_str = "0 Source Pointers in Dataset"
            elif mat_pct == 0.0 and lm["Stale"] > 0:
                cause_str = f"**Stale/Unlinked**: Holds Old SP2016 IDs ({lm['Stale']} rows require backfill)"

            md_lines.append(
                f"| `{lm['ColumnName']}` | `{lm['TargetList']}` | {tot:,} | {mat:,} ({mat_pct}%) | {var_cnt:,} ({var_pct}%) | {cause_str} |"
            )
        md_lines.append("")

    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")

    # 4. Write Site-Wide Discrepancies CSV
    if all_discrepancies:
        with open(output_csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["ListName", "CaseIdentifier", "OnPremID", "SpoItemID", "TotalVariances", "DifferingColumns"])
            writer.writeheader()
            for d in all_discrepancies:
                writer.writerow(d)

    print(f"[PASS] Executive Markdown Report -> {output_md_path}")
    print(f"[PASS] Master Discrepancies CSV -> {output_csv_path}")

    sys.stdout = original_stdout
    log_file.write("```\n")
    log_file.close()
    print(f"[PASS] Console Output Log -> {console_log_path}")

if __name__ == "__main__":
    main()
