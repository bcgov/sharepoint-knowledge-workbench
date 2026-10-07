"""
analyze-list-mapping-assurance.py

Purpose:
    Build a deterministic source-to-target SharePoint item-ID map by matching
    configured identity columns in ordered tiers, and report aggregate coverage.

Key Input Dependencies:
    - Audit-config JSON containing identity_mapping.list and identity_mapping.tiers.
    - Source and target list CSV exports under --data-dir.
    - Optional output path and --delete-pii-after flag supplied by the caller.

Function Index:
    normalize, load_identity_config, tier_key, read_rows, match_rows, main

Config-driven, deterministic identity mapping between a source list (on-premises SharePoint) and the same list in SharePoint Online.
It reads the two CSV exports written by export-list-content-pairs.ps1:
    <data-dir>/<List>-sp2016-onprem.csv   (source)
    <data-dir>/<List>-spo-prod.csv        (target)
and matches each source row to a target row tier by tier. The list and the match tiers come from the "identity_mapping" section of
the audit config (see audit-config.example.json):

    "identity_mapping": {
        "list": "Customers",
        "tiers": [
            {"name": "T1_ExactKey",  "columns": ["Title"]},
            {"name": "T2_NameAndDate", "columns": ["LastName", "FirstName", "BirthDate"]}
        ]
    }

Each tier matches rows whose (normalized, upper-cased) values in all of its columns are equal and non-empty; earlier tiers win.
Only columns named in the config are read. Outputs a zero-PII numerical summary to the console, writes an ID-to-ID mapping JSON
(source ID -> target ID) and can delete the raw CSV files when done (--delete-pii-after).
"""

import argparse
import csv
import json
import os
from pathlib import Path


def normalize(val):
    """Trim and uppercase an identity value before comparing tier keys."""
    if val is None:
        return ""
    return str(val).strip().upper()


def load_identity_config(path):
    """Load and validate the identity-mapping settings from the audit config."""
    cfg = {"list": None, "tiers": [{"name": "T1_Title", "columns": ["Title"]}]}
    if path and Path(path).is_file():
        with open(path, "r", encoding="utf-8") as handle:
            section = json.load(handle).get("identity_mapping")
        if section:
            cfg.update(section)
    if not cfg.get("list"):
        raise SystemExit("identity_mapping.list is not set in the audit config: name the list whose IDs are being mapped.")
    for tier in cfg["tiers"]:
        if not tier.get("columns"):
            raise SystemExit(f"Tier {tier.get('name')!r} has no columns")
    return cfg


def tier_key(row, columns):
    """Return a normalized compound key, or None when any configured value is blank."""
    values = [normalize(row.get(c)) for c in columns]
    return "|".join(values) if all(values) else None


def read_rows(path):
    """Read a CSV export while accepting a UTF-8 BOM from SharePoint downloads."""
    with open(path, mode="r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def match_rows(source_rows, target_rows, tiers):
    """Return ({source_id: target_id}, {tier name: matched count}, unmatched count). The first tier that matches wins."""
    indexes = []
    for tier in tiers:
        index = {}
        for row in target_rows:
            key = tier_key(row, tier["columns"])
            if key is not None:
                index.setdefault(key, int(row["ID"]))
        indexes.append(index)
    id_map, per_tier, unmatched = {}, {t["name"]: 0 for t in tiers}, 0
    for row in source_rows:
        for tier, index in zip(tiers, indexes):
            key = tier_key(row, tier["columns"])
            if key is not None and key in index:
                id_map[int(row["ID"])] = index[key]
                per_tier[tier["name"]] += 1
                break
        else:
            unmatched += 1
    return id_map, per_tier, unmatched


def main():
    """Parse CLI options, generate the configured ID mapping, and optionally purge input exports."""
    parser = argparse.ArgumentParser(description="Deterministic identity mapping between a source list and its SharePoint Online counterpart")
    parser.add_argument("--audit-config", default=None, help="audit config JSON with an identity_mapping section (default: <data-dir>/audit-config.json)")
    parser.add_argument("--data-dir", default=".agents/scratch/pii-data", help="Directory containing the exported CSV files")
    parser.add_argument("--out-map", default=".agents/scratch/audit-reports/id-mapping-verified.json", help="Path to write the ID mapping")
    parser.add_argument("--delete-pii-after", action="store_true", help="Delete the raw CSV files after analysis")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    cfg = load_identity_config(args.audit_config or data_dir / "audit-config.json")
    safe_list = cfg["list"].replace(" ", "_")
    source_csv = data_dir / f"{safe_list}-sp2016-onprem.csv"
    target_csv = data_dir / f"{safe_list}-spo-prod.csv"

    if not source_csv.exists() or not target_csv.exists():
        print(f"Error: required CSV files not found in {data_dir}")
        print(f"  source exists: {source_csv.exists()} ({source_csv})")
        print(f"  target exists: {target_csv.exists()} ({target_csv})")
        print(f"Run export-list-content-pairs.ps1 -ListName {cfg['list']} first.")
        raise SystemExit(2)

    source_rows, target_rows = read_rows(source_csv), read_rows(target_csv)
    print("=" * 70)
    print(f" IDENTITY MAPPING ASSURANCE: {cfg['list']}")
    print("=" * 70)
    print(f"Loaded {len(source_rows)} source rows and {len(target_rows)} target rows.")

    id_map, per_tier, unmatched = match_rows(source_rows, target_rows, cfg["tiers"])
    pct = round(len(id_map) / len(source_rows) * 100, 2) if source_rows else 0
    print(f"Total matched : {len(id_map)} ({pct}%)")
    for tier in cfg["tiers"]:
        print(f"  [{tier['name']}] matched by {' + '.join(tier['columns'])}: {per_tier[tier['name']]}")
    print(f"Unmatched / dropped: {unmatched}")

    out_map_path = Path(args.out_map)
    out_map_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_map_path, "w", encoding="utf-8") as out_f:
        json.dump(id_map, out_f, indent=2)
    print(f"\nSaved ID translation table ({len(id_map)} pairs) to: {out_map_path}")

    if args.delete_pii_after:
        for path in (source_csv, target_csv):
            if path.exists():
                os.remove(path)
        print("Raw CSV files deleted.")
    else:
        print("Note: pass --delete-pii-after to purge the raw CSV files after analysis.")


if __name__ == "__main__":
    main()
