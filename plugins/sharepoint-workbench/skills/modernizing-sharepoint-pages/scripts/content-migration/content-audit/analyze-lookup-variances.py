"""
analyze-lookup-variances.py (sp-audit-list Comprehensive Analyzer)

Purpose:
  Compare paired source and SharePoint Online exports for configured lookup
  pointer health and field parity, then emit zero-PII audit reports.

Key Input Dependencies:
  - Audit-config JSON supplied with --audit-config or found under --data-dir.
  - Optional dependency-matrix JSON and identity-mapping JSON.
  - Paired source/target CSV exports under --data-dir.
  - Caller-selected Markdown, CSV, and console-log output paths.

Function Index:
  key_value, load_audit_config, Tee.__init__, Tee.write, Tee.flush, normalize,
  sanitize_identifier, count_case_id_suffix_mismatches, _parse_args, _apply_audit_config, _open_console_log, _new_definitions,
  _add_matrix_entry, _load_matrix_definitions, _merge_config_lookups, _load_id_map,
  _discover_pairs, _load_rows, _new_tally, _new_lookup_stats, _check_spo_suffix_drift, _check_case_suffix,
  _match_case_row,
  _match_row, _sample, _classify_pointer, _audit_lookup_pointers, _target_column,
  _lookup_ids_translate, _column_parity, _identity_shift, _record_discrepancy, _audit_row,
  _summarize, _analyze_list, _write_discrepancy_csv, _lookup_status, _print_lookup_health,
  _print_top_columns, _print_list_report, _lookup_cause, _lookup_markdown_row,
  _build_markdown, main

Full-spectrum parity, row-level discrepancy, and granular lookup reconciliation engine:
  - SP2016 source: .agents/scratch/pii-data/<ListName>-sp2016-onprem.csv
  - SPO PROD target: .agents/scratch/pii-data/<ListName>-spo-prod.csv

Key Architectural Features:
  1. Tripartite Natural Key Matching: Joins items by configured business key columns (default: Title) or id-mapping-verified.json for the identity list.
  2. Suffix Skew Diagnostics: Measures and samples business-key numeric suffix vs SharePoint integer ID divergence.
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

# Site-specific knowledge lives in an --audit-config JSON file, never in this script. Defaults are deliberately generic.
DEFAULT_ID_PATTERN = r"^[A-Za-z][A-Za-z0-9]*_[0-9]{4}_[0-9]+$"
ID_PATTERN = re.compile(DEFAULT_ID_PATTERN)
KEY_COLUMNS = ["Title"]
IDENTITY_LIST = None   # the list whose IDs are translated through id-mapping-verified.json (identity_mapping.list in the audit config)


def key_value(row, default=""):
    """First non-empty business-key column of a row (columns come from the audit config; default: Title)."""
    for col in KEY_COLUMNS:
        value = row.get(col)
        if value not in (None, ""):
            return str(value).strip()
    return str(default).strip() if default else ""


def load_audit_config(path, required=True):
    """Load the audit config: {"id_pattern": str, "key_columns": [str], "lookups": {list: {spoColumn: [onPremColumn, targetList]}}, ...}.

    A missing config is an error (the audit would otherwise run with no site mapping and look complete); pass --allow-default-config
    to run deliberately with the generic defaults (key column Title, no lookups).
    """
    cfg = {"id_pattern": DEFAULT_ID_PATTERN, "key_columns": ["Title"], "lookups": {}}
    if path and Path(path).is_file():
        with open(path, "r", encoding="utf-8") as handle:
            cfg.update(json.load(handle))
    elif required:
        raise SystemExit(f"Audit config not found: {path}. Copy audit-config.example.json, describe the site's lists, key columns and lookups, "
                         "and pass it with --audit-config (or pass --allow-default-config to run with generic defaults).")
    return cfg


class Tee:
    """Duplicates writes to multiple streams (e.g. console + log file)."""
    def __init__(self, *streams):
        """Store each output stream that should receive duplicated console text."""
        self.streams = streams

    def write(self, data):
        """Write the same text fragment to every configured stream."""
        for s in self.streams:
            s.write(data)

    def flush(self):
        """Flush each configured stream after buffered output is written."""
        for s in self.streams:
            s.flush()

def normalize(val):
    """Normalize rich text, numeric values, dates, and whitespace for parity checks."""
    if val is None:
        return ""
    s = str(val).strip()
    
    # 1. HTML tag & entity stripping for rich text / multi-line notes
    if "<" in s and ">" in s:
        s = re.sub(r'<style[^>]*>.*?</style[^>]*>', '', s, flags=re.DOTALL | re.IGNORECASE)
        s = re.sub(r'<script[^>]*>.*?</script[^>]*>', '', s, flags=re.DOTALL | re.IGNORECASE)
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
    """Return a report-safe identifier for a business key or source item."""
    if not raw_id:
        return f"Item #{onprem_id}" if onprem_id else "Item"
    raw_str = str(raw_id).strip()
    if ID_PATTERN.match(raw_str):
        return raw_str
    if raw_str.isdigit():
        return f"Item #{raw_str}"
    if raw_str.upper().startswith("ITEM_"):
        return raw_str
    if onprem_id:
        return f"Row (On-Prem ID #{onprem_id})"
    return "Row Item"


def count_case_id_suffix_mismatches(rows):
    """Count rows whose trailing business-key digits do not match the item ID."""
    count = 0
    for row in rows:
        item_id = row.get("ID") if row.get("ID") is not None else row.get("Id")
        case_id = key_value(row) or None
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


IGNORE_COLS = {
    "id", "__sp_id__", "modified", "created", "author", "editor",
    "attachments", "guid", "contenttype", "contenttypeid",
    "filesystemobjecttype", "iscurrent", "dob_plain_text"
}
DISCREPANCY_FIELDS = ["ListName", "BusinessKey", "OnPremID", "SpoItemID", "TotalVariances", "DifferingColumns"]


def _parse_args(repo_root):
    """Parse the analyzer CLI; default inputs and outputs live under <cwd>/.agents/scratch."""
    parser = argparse.ArgumentParser(description="Full-Spectrum List & Lookup Variance Analyzer (Zero PII)")
    parser.add_argument("--data-dir", default=str(repo_root / ".agents" / "scratch" / "pii-data"), help="Directory containing CSV exports")
    parser.add_argument("--matrix-path", default=str(repo_root / ".agents" / "scratch" / "wave-dependency-matrix.json"), help="Wave matrix path")
    parser.add_argument("--mapping-path", default=str(repo_root / ".agents" / "scratch" / "audit-reports" / "id-mapping-verified.json"), help="Verified identity-list ID mapping path")
    parser.add_argument("--output-md", default=str(repo_root / ".agents" / "scratch" / "audit-reports" / "SITE-FULL-CONTENT-PARITY-REPORT.md"), help="Executive report output path")
    parser.add_argument("--output-csv", default=str(repo_root / ".agents" / "scratch" / "audit-reports" / "site-full-content-parity-audit.csv"), help="Discrepancies CSV output path")
    parser.add_argument("--console-log", default=str(repo_root / ".agents" / "scratch" / "audit-reports" / "CONSOLE-OUTPUT-LOG.md"), help="Full console output log (markdown) path")
    parser.add_argument("--list-name", default="ALL", help="Specific list name to analyze or 'ALL'")
    parser.add_argument("--allow-default-config", action="store_true", help="Run without an audit config, using generic defaults (key column Title, no lookups)")
    parser.add_argument("--audit-config", default=None, help="JSON with id_pattern, key_columns and lookups for the site being audited (default: <data-dir>/audit-config.json if present)")
    return parser.parse_args()


def _apply_audit_config(args):
    """Load the audit config and publish its id pattern, key columns and identity list as module settings."""
    global ID_PATTERN, KEY_COLUMNS, IDENTITY_LIST
    config_path = args.audit_config or str(Path(args.data_dir) / "audit-config.json")
    audit_cfg = load_audit_config(config_path, required=not args.allow_default_config)
    ID_PATTERN = re.compile(audit_cfg["id_pattern"], re.IGNORECASE)
    KEY_COLUMNS = list(audit_cfg["key_columns"])
    IDENTITY_LIST = audit_cfg.get("identity_mapping", {}).get("list")
    return audit_cfg


def _open_console_log(console_log_path):
    """Start duplicating console output into the markdown console log; return the log handle and real stdout."""
    console_log_path.parent.mkdir(parents=True, exist_ok=True)
    log_file = open(console_log_path, "w", encoding="utf-8")
    log_file.write("# Console Output Log — Full-Spectrum Variance Analysis\n\n```text\n")
    original_stdout = sys.stdout
    sys.stdout = Tee(original_stdout, log_file)
    return log_file, original_stdout


def _new_definitions():
    """Return empty per-list field maps, exclusions, identity lookups and lookup definitions."""
    return {
        "field_maps": defaultdict(dict),
        "exclusions": defaultdict(set),
        "identity_lookups": defaultdict(set),
        "lookups": defaultdict(dict),
    }


def _add_matrix_entry(d_name, entry, defs):
    """Record one dependency-matrix entry's field renames, lookup columns and exclusions."""
    fmap = {}
    for fr in entry.get("fieldRenames", []):
        op_col = fr.get("onPrem")
        sp_col = fr.get("spo")
        if op_col and sp_col:
            fmap[op_col] = sp_col
        if "Lookup" in fr.get("type", ""):
            target_list = fr.get("lookupList", "Unknown")
            defs["lookups"][d_name][sp_col] = {
                "onPrem": op_col,
                "target": target_list,
                "type": fr.get("type")
            }
            if target_list == IDENTITY_LIST:
                defs["identity_lookups"][d_name].add(sp_col)
    defs["field_maps"][d_name] = fmap

    for ex in entry.get("fieldExclusions", []):
        ex_name = ex.get("sp2016InternalName") or ex.get("field")
        if ex_name:
            defs["exclusions"][d_name].add(ex_name)


def _load_matrix_definitions(matrix_path, defs):
    """Read column definitions from the dependency matrix, when one exists."""
    if not matrix_path.exists():
        return
    with open(matrix_path, "r", encoding="utf-8") as f:
        matrix_data = json.load(f)
    for entry in matrix_data:
        d_name = entry.get("destinationName")
        if d_name:
            _add_matrix_entry(d_name, entry, defs)


def _merge_config_lookups(audit_cfg, defs):
    """Add lookup definitions supplied by the audit config (the wave matrix is the other source)."""
    config_lookups = {
        list_name: {sp_col: tuple(pair) for sp_col, pair in columns.items()}
        for list_name, columns in audit_cfg.get("lookups", {}).items()
    }

    for l_key, l_dict in config_lookups.items():
        for sp_col, (op_col, tgt) in l_dict.items():
            defs["lookups"][l_key][sp_col] = { "onPrem": op_col, "target": tgt, "type": "Lookup" }
            if tgt == IDENTITY_LIST:
                defs["identity_lookups"][l_key].add(sp_col)
            if op_col not in defs["field_maps"][l_key]:
                defs["field_maps"][l_key][op_col] = sp_col


def _load_id_map(locations):
    """Return the first readable identity-list ID mapping, or an empty mapping."""
    for p in locations:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return {}


def _discover_pairs(data_dir, list_name):
    """Find paired source/target CSV exports in data_dir that fall within the --list-name scope."""
    seen_bases = set()
    target_lists = []
    for pattern in ["*-sp2016-onprem.csv", "*-full-onprem.csv"]:
        for op_f in data_dir.glob(pattern):
            base_name = op_f.name.replace("-sp2016-onprem.csv", "").replace("-full-onprem.csv", "")
            if base_name in seen_bases:
                continue
            if list_name != "ALL" and list_name.lower() not in base_name.lower():
                continue
            spo_f = data_dir / f"{base_name}-spo-prod.csv"
            if not spo_f.exists():
                spo_f = data_dir / f"{base_name}-full-spo.csv"
            if spo_f.exists():
                seen_bases.add(base_name)
                target_lists.append((base_name, op_f, spo_f))
    return target_lists


def _load_rows(op_path, spo_path):
    """Read source rows, plus target rows indexed by item ID and by upper-cased business key."""
    with open(op_path, mode="r", encoding="utf-8-sig", errors="ignore") as f:
        onprem_rows = list(csv.DictReader(f))

    spo_by_id = {}
    spo_by_natural = {}
    with open(spo_path, mode="r", encoding="utf-8-sig", errors="ignore") as f:
        for r in csv.DictReader(f):
            rid = str(r.get("ID", "")).strip()
            if rid:
                spo_by_id[rid] = r
            case_val = key_value(r)
            if case_val:
                spo_by_natural[case_val.upper()] = r
    return onprem_rows, spo_by_id, spo_by_natural


def _new_tally():
    """Return zeroed per-list counters and an empty discrepancy list."""
    return {
        "co_existing": 0, "perfect": 0, "differing": 0, "group1": 0, "group2": 0, "suffix_mismatch": 0,
        "col_diff_counts": defaultdict(int), "cat_issues": defaultdict(int), "discrepancies": [],
    }


def _new_lookup_stats(lookups_def):
    """Return per-lookup-column pointer counters, seeded with each column's target list."""
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
    return lookup_col_stats

def _check_spo_suffix_drift(l_name, case_key, op_id, spo_row, ctx, tally):
    """Count matched SPO rows whose business-key suffix no longer matches their own item ID."""
    # The drift bug is caused by SPO business-key values no longer matching their own Item ID,
    # not by the source on-prem rows, so the live SPO record is checked.
    if spo_row is None:
        return
    spo_case_id = key_value(spo_row)
    spo_item_id = str(spo_row.get("ID") or "").strip()
    if not (spo_case_id and spo_item_id):
        return
    m_sfx = re.search(r'(\d+)$', spo_case_id)
    if not m_sfx:
        return
    suffix_digits = m_sfx.group(1)
    item_id_width = len(spo_item_id)
    match_candidate = suffix_digits[-item_id_width:] if item_id_width > 0 else suffix_digits
    if match_candidate == spo_item_id:
        return
    tally["suffix_mismatch"] += 1
    tally["col_diff_counts"]["KEY_SUFFIX_MISMATCH"] += 1
    if len(ctx["skew_samples"][l_name]) < 5:
        ctx["skew_samples"][l_name].append({
            "Case": case_key,
            "SpoBusinessKey": spo_case_id,
            "TrailingSuffix": suffix_digits,
            "RightmostMatchCandidate": match_candidate,
            "SpoItemID": spo_item_id,
            "OnPremRowID": op_id,
            "MismatchType": "SPO_ROW_SUFFIX_DRIFT"
        })


def _check_case_suffix(l_name, raw_case_key, case_key, op_id, spo_row, ctx, tally):
    """Check SPO suffix drift, then flag source rows whose own key suffix differs from their item ID."""
    _check_spo_suffix_drift(l_name, case_key, op_id, spo_row, ctx, tally)
    # Separate on-prem source check retained for audit context so future runs can
    # distinguish whether the source export itself is already inconsistent.
    m_sfx = re.search(r'(\d+)$', raw_case_key)
    if m_sfx and op_id and int(m_sfx.group(1)) != int(op_id):
        tally["col_diff_counts"]["KEY_SUFFIX_ONPREM_MISMATCH"] += 1


def _match_case_row(l_name, op_row, op_id, ctx, spo_index, tally):
    """Match a case-list row by business key (falling back to item ID) and check its suffix drift."""
    spo_by_id, spo_by_natural = spo_index
    raw_case_key = key_value(op_row, f"ITEM_{op_id}")
    case_key = sanitize_identifier(raw_case_key, op_id)
    spo_row = None
    if raw_case_key.upper() in spo_by_natural:
        spo_row = spo_by_natural[raw_case_key.upper()]
    elif op_id in spo_by_id:
        spo_row = spo_by_id[op_id]
    _check_case_suffix(l_name, raw_case_key, case_key, op_id, spo_row, ctx, tally)
    return spo_row, case_key


def _match_row(l_name, op_row, op_id, ctx, spo_index, tally):
    """Find the target row for a source row and return it with the row's report-safe key."""
    spo_by_id = spo_index[0]
    id_map = ctx["id_map"]
    if l_name == IDENTITY_LIST and id_map:
        if op_id in id_map:
            target_spo_id = str(id_map[op_id])
            if target_spo_id in spo_by_id:
                return spo_by_id[target_spo_id], f"Identity row (Old ID #{op_id} -> SPO #{target_spo_id})"
        return None, ""
    if "Cases" in l_name:
        return _match_case_row(l_name, op_row, op_id, ctx, spo_index, tally)
    return spo_by_id.get(op_id), f"Row #{op_id}"


def _sample(store, key, sample, limit=4):
    """Keep at most `limit` diagnostic samples per key."""
    if len(store[key]) < limit:
        store[key].append(sample)


def _classify_pointer(old_ptr, spo_ids, tgt_list, sample_key, case_key, stat, ctx):
    """Tally one source lookup pointer as matching, blank, stale or misbound in the target row."""
    id_map = ctx["id_map"]
    stat["total_pointers"] += 1
    expected_target_id = str(id_map.get(old_ptr, old_ptr)) if tgt_list == IDENTITY_LIST and id_map else old_ptr

    if expected_target_id in spo_ids:
        stat["matching"] += 1
    elif len(spo_ids) == 0:
        stat["blank_in_spo"] += 1
        _sample(ctx["missing_lookup_samples"], sample_key, {
            "Case": case_key,
            "OnPremID": old_ptr,
            "ExpectedSpoID": expected_target_id
        })
    elif old_ptr in spo_ids:
        stat["stale_old_id"] += 1
        _sample(ctx["missing_lookup_samples"], sample_key, {
            "Case": case_key,
            "OnPremID": old_ptr,
            "ExpectedSpoID": f"{expected_target_id} (Holds SP2016 ID {old_ptr})"
        })
    else:
        stat["misbound"] += 1
        _sample(ctx["false_lookup_samples"], sample_key, {
            "Case": case_key,
            "OnPremID": old_ptr,
            "ExpectedSpoID": expected_target_id,
            "ActualSpoID": ",".join(spo_ids)
        })


def _audit_lookup_pointers(l_name, op_row, spo_row, case_key, lookups_def, lookup_col_stats, ctx):
    """Classify every single- and multi-value lookup pointer of one source row."""
    for sp_col, info in lookups_def.items():
        op_col = info["onPrem"]
        raw_op_val = str(op_row.get(op_col) or op_row.get(sp_col) or "").strip()
        raw_spo_val = str(spo_row.get(sp_col) or spo_row.get(op_col) or "").strip()

        if not raw_op_val and not raw_spo_val:
            continue

        op_ids = re.findall(r'\d+', raw_op_val)
        spo_ids = re.findall(r'\d+', raw_spo_val)
        for old_ptr in op_ids:
            _classify_pointer(old_ptr, spo_ids, info["target"], f"{l_name}.{sp_col}", case_key,
                              lookup_col_stats[sp_col], ctx)


def _target_column(op_col, spo_row, rules):
    """Return the target column compared with a source column, or None when it is skipped or absent."""
    if not op_col or op_col.lower() in IGNORE_COLS or op_col.startswith("_") or op_col in rules["exclusions"]:
        return None
    spo_col = rules["fmap"].get(op_col, op_col)
    if spo_col not in spo_row and op_col in spo_row:
        spo_col = op_col
    return spo_col if spo_col in spo_row else None


def _lookup_ids_translate(v1, v2, id_map):
    """True when the source lookup IDs, translated through the identity map, equal the target IDs."""
    exp_parts = [str(id_map.get(oid, oid)) for oid in re.findall(r'\d+', v1)]
    return sorted(exp_parts) == sorted(re.findall(r'\d+', v2))


def _column_parity(op_row, spo_row, rules, id_map, tally):
    """Compare every comparable business column and return the target names of differing columns."""
    differing_cols = []
    for op_col, val_op_raw in op_row.items():
        spo_col = _target_column(op_col, spo_row, rules)
        if spo_col is None:
            continue

        v1 = normalize(val_op_raw)
        v2 = normalize(spo_row.get(spo_col, ""))
        is_lookup = spo_col in rules["identity_lookups"] or spo_col in rules["lookups"]

        # Identity lookup translation check
        if is_lookup and id_map and v1 and _lookup_ids_translate(v1, v2, id_map):
            continue

        if v1 != v2:
            differing_cols.append(spo_col)
            tally["col_diff_counts"][spo_col] += 1
            if is_lookup:
                tally["cat_issues"]["LookupDrift"] += 1
            elif not v2 and v1:
                tally["cat_issues"]["DroppedBlank"] += 1
            else:
                tally["cat_issues"]["TextVariance"] += 1
    return differing_cols


def _identity_shift(l_name, op_id, spo_row, tally):
    """Report an identity-list item whose SharePoint Online ID differs from its source ID."""
    if l_name != IDENTITY_LIST:
        return []
    spo_id_val = str(spo_row.get("ID", "")).strip()
    if op_id == spo_id_val:
        return []
    tally["col_diff_counts"]["Item_ID_Shift (+18k Offset)"] += 1
    tally["cat_issues"]["LookupDrift"] += 1
    return [f"Item_ID_Shift (Old #{op_id} -> SPO #{spo_id_val})"]


def _record_discrepancy(tally, l_name, case_key, op_id, spo_item_id, total, columns):
    """Append one zero-PII discrepancy row for the list."""
    tally["discrepancies"].append({
        "ListName": l_name,
        "BusinessKey": case_key,
        "OnPremID": op_id,
        "SpoItemID": spo_item_id,
        "TotalVariances": total,
        "DifferingColumns": columns
    })


def _audit_row(l_name, op_row, spo_index, rules, lookup_col_stats, ctx, tally):
    """Match one source row, audit its lookup pointers and columns, and record any discrepancy."""
    op_id = str(op_row.get("ID") or op_row.get("Id") or "").strip()
    spo_row, case_key = _match_row(l_name, op_row, op_id, ctx, spo_index, tally)

    if not spo_row:
        tally["group2"] += 1
        tally["col_diff_counts"]["ROW_MISSING_IN_SPO"] += 1
        _record_discrepancy(tally, l_name, case_key, op_id, "MISSING_IN_SPO", 1, "ROW_MISSING_IN_SPO")
        return

    tally["co_existing"] += 1
    differing_cols = _identity_shift(l_name, op_id, spo_row, tally)
    _audit_lookup_pointers(l_name, op_row, spo_row, case_key, rules["lookups"], lookup_col_stats, ctx)
    differing_cols += _column_parity(op_row, spo_row, rules, ctx["id_map"], tally)

    if len(differing_cols) == 0:
        tally["perfect"] += 1
        return
    tally["differing"] += 1
    tally["group1"] += 1
    _record_discrepancy(tally, l_name, case_key, op_id, spo_row.get("ID", ""), len(differing_cols),
                        "; ".join(differing_cols))


def _summarize(l_name, onprem_rows, spo_index, tally):
    """Build the list's summary row: counts, parity score, top differing columns and root-cause tallies."""
    spo_by_id, spo_by_natural = spo_index
    col_diff_counts = tally["col_diff_counts"]
    cat_issues = tally["cat_issues"]
    co_existing_count = tally["co_existing"]
    score = round((tally["perfect"] / co_existing_count) * 100, 2) if co_existing_count else 100.0
    top_diffs = ", ".join([f"{k} ({v})" for k, v in sorted(col_diff_counts.items(), key=lambda x: x[1], reverse=True)[:3]])
    return {
        "ListName": l_name,
        "TotalSource": len(onprem_rows),
        "TotalSPO": len(spo_by_id) if spo_by_id else len(spo_by_natural),
        "CoExisting": co_existing_count,
        "Perfect": tally["perfect"],
        "Differing": tally["differing"],
        "Group1_Diffs": tally["group1"],
        "Group2_Missing": tally["group2"],
        "Score": score,
        "TopDiffs": top_diffs,
        "LookupDrift": cat_issues["LookupDrift"],
        "DroppedBlanks": cat_issues["DroppedBlank"],
        "TextVariances": cat_issues["TextVariance"],
        "ColumnDetails": dict(col_diff_counts),
        "SuffixMismatch": tally["suffix_mismatch"]
    }


def _analyze_list(l_name, op_path, spo_path, defs, ctx):
    """Audit one paired list; return its summary row, discrepancy rows and lookup pointer metrics."""
    onprem_rows, spo_by_id, spo_by_natural = _load_rows(op_path, spo_path)
    spo_index = (spo_by_id, spo_by_natural)
    lookups_def = defs["lookups"].get(l_name, {})
    rules = {
        "fmap": defs["field_maps"].get(l_name, {}),
        "exclusions": defs["exclusions"][l_name],
        "identity_lookups": defs["identity_lookups"][l_name],
        "lookups": lookups_def,
    }
    lookup_col_stats = _new_lookup_stats(lookups_def)
    tally = _new_tally()

    for op_row in onprem_rows:
        _audit_row(l_name, op_row, spo_index, rules, lookup_col_stats, ctx, tally)

    metrics = [{
        "ColumnName": sp_col,
        "TargetList": stat["target"],
        "TotalPointers": stat["total_pointers"],
        "Matching": stat["matching"],
        "Blank": stat["blank_in_spo"],
        "Stale": stat["stale_old_id"],
        "Misbound": stat["misbound"]
    } for sp_col, stat in lookup_col_stats.items()]
    return _summarize(l_name, onprem_rows, spo_index, tally), tally["discrepancies"], metrics


def _write_discrepancy_csv(path, rows):
    """Write discrepancy rows to a UTF-8 (BOM) CSV with the standard columns."""
    with open(path, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=DISCREPANCY_FIELDS)
        writer.writeheader()
        for d in rows:
            writer.writerow(d)


def _lookup_status(lm):
    """Return the console status label for one lookup column's pointer health."""
    tot = lm["TotalPointers"]
    if tot == 0:
        return "0 Source Pointers"
    if lm["Blank"] > 0 and lm["Stale"] > 0:
        return f"{lm['Blank']} Blank, {lm['Stale']} Stale"
    if lm["Blank"] > 0:
        return f"{lm['Blank']} Blank in SPO"
    if lm["Stale"] > 0:
        return f"{lm['Stale']} Stale SP2016 IDs"
    if lm["Misbound"] > 0:
        return f"{lm['Misbound']} Misbound Target"
    return "Fully Resolved"


def _print_lookup_health(l_name, l_lookups):
    """Print the dedicated lookup pointer health table for one list."""
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
        print(f"{lm['ColumnName']:<26} | {lm['TargetList']:<10} | {tot:<6} | {mat_str:<14} | {lm['Blank']:<7} | {lm['Stale']:<7} | {_lookup_status(lm)}")
    print("=" * 85)


def _print_top_columns(r):
    """Print the ten most frequently differing columns for one list."""
    print(f"\nTop Columns with Variances (Frequency):")
    for col_name, cnt in sorted(r["ColumnDetails"].items(), key=lambda x: x[1], reverse=True)[:10]:
        pct = round((cnt / r["CoExisting"]) * 100, 1) if r["CoExisting"] else 0.0
        print(f"  * {col_name:<32}: {cnt:>5} row(s) ({pct:>4.1f}%)")
    print("=" * 85)


def _print_list_report(r, l_lookups, output_csv_path):
    """Print the full console variance report for one list."""
    l_name = r["ListName"]
    print("=" * 85)
    print(f" FULL VARIANCE AUDIT REPORT: {l_name.upper()} (source vs SharePoint Online)")
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
    print(f"  * Business-key suffix != item ID discrepancies     : {r['SuffixMismatch']}")
    print("=" * 85)

    if l_lookups:
        _print_lookup_health(l_name, l_lookups)
    if r["ColumnDetails"]:
        _print_top_columns(r)

    list_var_csv = output_csv_path.parent / f"{l_name}-variances-only.csv"
    print(f"Saved {r['Differing'] + r['Group2_Missing']} discrepant rows to: {list_var_csv}\n")


def _lookup_cause(lm, mat_pct):
    """Return the executive-report root-cause text for one lookup column."""
    cause_parts = []
    if lm["Blank"] > 0:
        cause_parts.append(f"{lm['Blank']} Blank in SPO")
    if lm["Stale"] > 0:
        cause_parts.append(f"{lm['Stale']} Stale Old SP2016 IDs")
    if lm["Misbound"] > 0:
        cause_parts.append(f"{lm['Misbound']} Misbound Target")

    cause_str = ", ".join(cause_parts) if cause_parts else "Fully Resolved"
    if lm["TotalPointers"] == 0:
        cause_str = "0 Source Pointers in Dataset"
    elif mat_pct == 0.0 and lm["Stale"] > 0:
        cause_str = f"**Stale/Unlinked**: Holds Old SP2016 IDs ({lm['Stale']} rows require backfill)"
    return cause_str


def _lookup_markdown_row(lm):
    """Return one executive-report table row for a lookup column."""
    tot = lm["TotalPointers"]
    mat = lm["Matching"]
    mat_pct = round((mat / tot) * 100, 1) if tot else 100.0
    var_cnt = tot - mat
    var_pct = round((var_cnt / tot) * 100, 1) if tot else 0.0
    return (
        f"| `{lm['ColumnName']}` | `{lm['TargetList']}` | {tot:,} | {mat:,} ({mat_pct}%) | {var_cnt:,} ({var_pct}%) | {_lookup_cause(lm, mat_pct)} |"
    )


def _build_markdown(summary_rows, all_lookup_metrics_by_list):
    """Build the executive Markdown report lines from list summaries and lookup metrics."""
    md_lines = [
        "# Site-Wide Full Content & Lookup Parity Executive Report (source vs SharePoint Online)",
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
            md_lines.append(_lookup_markdown_row(lm))
        md_lines.append("")
    return md_lines


def main():
    """Load configured source/target datasets and write lookup-parity reports without exposing PII."""
    # Default inputs/outputs live under .agents/scratch of the directory the script is run from (the project root), whether it runs
    # from the plugin source tree or from an installed skill folder.
    repo_root = Path.cwd()
    args = _parse_args(repo_root)
    audit_cfg = _apply_audit_config(args)

    data_dir = Path(args.data_dir)
    matrix_path = Path(args.matrix_path)
    mapping_path = Path(args.mapping_path)
    output_md_path = Path(args.output_md)
    output_csv_path = Path(args.output_csv)

    output_md_path.parent.mkdir(parents=True, exist_ok=True)
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)

    console_log_path = Path(args.console_log)
    log_file, original_stdout = _open_console_log(console_log_path)

    # 1. Load Matrix & Setup Column Lookups
    defs = _new_definitions()
    _load_matrix_definitions(matrix_path, defs)
    _merge_config_lookups(audit_cfg, defs)
    ctx = {
        "id_map": _load_id_map([
            mapping_path,
            repo_root / ".agents" / "scratch" / "id-mapping-verified.json",
            repo_root / ".agents" / "scratch" / "audit-reports" / "id-mapping-verified.json",
        ]),
        "skew_samples": defaultdict(list),
        "missing_lookup_samples": defaultdict(list),
        "false_lookup_samples": defaultdict(list),
    }

    # 2. Discover available CSV pairs in data_dir
    target_lists = _discover_pairs(data_dir, args.list_name)
    if not target_lists:
        print(f"Error: No matching paired datasets found in {data_dir} for scope '{args.list_name}'.")
        return

    summary_rows = []
    all_discrepancies = []
    all_lookup_metrics_by_list = {}
    for l_name, op_path, spo_path in sorted(target_lists):
        summary, list_discrepancies, metrics = _analyze_list(l_name, op_path, spo_path, defs, ctx)
        summary_rows.append(summary)
        if list_discrepancies:
            _write_discrepancy_csv(output_csv_path.parent / f"{l_name}-variances-only.csv", list_discrepancies)
        all_discrepancies.extend(list_discrepancies)
        if metrics:
            all_lookup_metrics_by_list[l_name] = metrics

    # Output Full Console Report Matching Expected Standard
    for r in summary_rows:
        _print_list_report(r, all_lookup_metrics_by_list.get(r["ListName"], []), output_csv_path)

    # 3. Output Executive Markdown Report
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(_build_markdown(summary_rows, all_lookup_metrics_by_list)) + "\n")

    # 4. Write Site-Wide Discrepancies CSV
    if all_discrepancies:
        _write_discrepancy_csv(output_csv_path, all_discrepancies)

    print(f"[PASS] Executive Markdown Report -> {output_md_path}")
    print(f"[PASS] Master Discrepancies CSV -> {output_csv_path}")

    sys.stdout = original_stdout
    log_file.write("```\n")
    log_file.close()
    print(f"[PASS] Console Output Log -> {console_log_path}")

if __name__ == "__main__":
    main()
