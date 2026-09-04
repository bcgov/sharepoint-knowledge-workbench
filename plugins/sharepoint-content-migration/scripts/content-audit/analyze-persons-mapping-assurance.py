"""
analyze-persons-mapping-assurance.py

Performs multi-tiered deterministic matching between On-Prem SP2016 and SPO Persons exports.
Calculates exact assurance levels across:
  Tier 1: CS Number (Title)
  Tier 2: FPS Number
  Tier 3: Strict Name + DOB (LastName + FirstName + MiddleName + DOB)
  Tier 4: Name + DOB + Role + Active + InCustody (Extended composite)

Outputs a zero-PII numerical summary to console, writes an anonymized ID-to-ID mapping JSON,
and offers to delete the raw PII CSV files upon completion.
"""

import os
import csv
import json
import argparse
from pathlib import Path

def normalize(val):
    if val is None:
        return ""
    return str(val).strip().upper()

def main():
    parser = argparse.ArgumentParser(description="Analyze Person mapping assurance between SP2016 and SPO")
    parser.add_argument("--data-dir", default=r".agents\scratch\pii-data", help="Directory containing the exported CSV files")
    parser.add_argument("--out-map", default=r".agents\scratch\audit-reports\id-mapping-verified.json", help="Path to write anonymized ID mapping")
    parser.add_argument("--delete-pii-after", action="store_true", help="Delete the raw CSV files after analysis")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    sp2016_csv = data_dir / "persons-sp2016-onprem.csv"
    spo_csv = data_dir / "persons-spo-prod.csv"

    if not sp2016_csv.exists() or not spo_csv.exists():
        print(f"Error: Required CSV files not found in {data_dir}")
        print(f"  SP2016 Exists: {sp2016_csv.exists()} ({sp2016_csv})")
        print(f"  SPO Exists   : {spo_csv.exists()} ({spo_csv})")
        print("Please run export-persons-sp2016-to-csv.ps1 and export-persons-spo-to-csv.ps1 first.")
        return

    print("=" * 70)
    print(" PERSON MAPPING ASSURANCE & DETERMINISTIC MATCHING ANALYSIS")
    print("=" * 70)

    # 1. Load SP2016 Persons
    onprem_records = []
    with open(sp2016_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            onprem_records.append(row)

    # 2. Load SPO Persons
    spo_records = []
    with open(spo_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            spo_records.append(row)

    print(f"Loaded {len(onprem_records)} On-Prem SP2016 records.")
    print(f"Loaded {len(spo_records)} Live SPO records.")

    # 3. Build Multi-Index on SPO
    spo_by_cs = {}
    spo_by_fps = {}
    spo_by_name_dob = {}
    spo_by_extended = {}

    for row in spo_records:
        spo_id = int(row["ID"])
        cs = normalize(row.get("CS_Number"))
        fps = normalize(row.get("FPS"))
        lname = normalize(row.get("LastName"))
        fname = normalize(row.get("FirstName"))
        mname = normalize(row.get("MiddleName"))
        dob = normalize(row.get("DateOfBirth"))
        active = normalize(row.get("Active"))
        role = normalize(row.get("Role"))
        custody = normalize(row.get("InCustody"))

        if cs:
            spo_by_cs[cs] = spo_id
        if fps:
            spo_by_fps[fps] = spo_id
        if lname and fname:
            k_name = f"{lname}|{fname}|{mname}|{dob}"
            spo_by_name_dob[k_name] = spo_id
            k_ext = f"{lname}|{fname}|{dob}|{role}|{active}|{custody}"
            spo_by_extended[k_ext] = spo_id

    # 4. Match Evaluation
    t1_cs = 0
    t2_fps = 0
    t3_namedob = 0
    t4_extended = 0
    unmatched = 0

    id_map = {}  # OnPrem_ID -> SPO_ID

    for row in onprem_records:
        op_id = int(row["ID"])
        cs = normalize(row.get("CS_Number"))
        fps = normalize(row.get("FPS"))
        lname = normalize(row.get("LastName"))
        fname = normalize(row.get("FirstName"))
        mname = normalize(row.get("MiddleName"))
        dob = normalize(row.get("DateOfBirth"))
        active = normalize(row.get("Active"))
        role = normalize(row.get("Role"))
        custody = normalize(row.get("InCustody"))

        resolved_id = None
        tier = None

        if cs and cs in spo_by_cs:
            resolved_id = spo_by_cs[cs]
            tier = "T1_CS"
            t1_cs += 1
        elif fps and fps in spo_by_fps:
            resolved_id = spo_by_fps[fps]
            tier = "T2_FPS"
            t2_fps += 1
        elif lname and fname:
            k_name = f"{lname}|{fname}|{mname}|{dob}"
            if k_name in spo_by_name_dob:
                resolved_id = spo_by_name_dob[k_name]
                tier = "T3_NameDOB"
                t3_namedob += 1
            else:
                k_ext = f"{lname}|{fname}|{dob}|{role}|{active}|{custody}"
                if k_ext in spo_by_extended:
                    resolved_id = spo_by_extended[k_ext]
                    tier = "T4_Extended"
                    t4_extended += 1

        if resolved_id is not None:
            id_map[op_id] = resolved_id
        else:
            unmatched += 1

    total_matched = len(id_map)
    pct = round((total_matched / len(onprem_records)) * 100, 2) if onprem_records else 0

    print("\n" + "=" * 70)
    print(" DETERMINISTIC MATCHING RESULTS SUMMARY (ZERO PII)")
    print("=" * 70)
    print(f"Total Source (SP2016) Records : {len(onprem_records)}")
    print(f"Total Matched into SPO        : {total_matched} ({pct}%)")
    print(f"  [Tier 1] Matched by CS Number               : {t1_cs}")
    print(f"  [Tier 2] Matched by FPS Number              : {t2_fps}")
    print(f"  [Tier 3] Matched by Strict Name + DOB       : {t3_namedob}")
    print(f"  [Tier 4] Matched by Extended Composite Key  : {t4_extended}")
    print(f"Unmatched / Dropped Records   : {unmatched}")
    print("=" * 70)

    # Save ID-only mapping table
    out_map_path = Path(args.out_map)
    with open(out_map_path, "w", encoding="utf-8") as out_f:
        json.dump(id_map, out_f, indent=2)
    print(f"\nSaved anonymized ID translation table ({len(id_map)} pairs) to: {out_map_path}")

    # Clean up PII if requested or prompt
    if args.delete_pii_after:
        print("\nCleaning up raw PII CSV files...")
        if sp2016_csv.exists(): os.remove(sp2016_csv)
        if spo_csv.exists(): os.remove(spo_csv)
        print("Raw CSV files deleted successfully.")
    else:
        print("\nNote: Pass '--delete-pii-after' when running python to automatically purge raw CSVs after analysis.")

if __name__ == "__main__":
    main()
