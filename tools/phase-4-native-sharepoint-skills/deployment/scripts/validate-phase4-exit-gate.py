#!/usr/bin/env python3
"""
validate-phase4-exit-gate.py

Exit gate validator for Phase 4 (Native SharePoint Skills Pilot).
Fails closed and rejects required evidence files if any required file is missing,
empty, or contains unexecuted placeholder tokens such as NOT_EXECUTED, NOT_RECORDED,
NOT_ASSIGNED, or PENDING.
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple

REQUIRED_REPORTS = [
    "candidate-selection.md",
    "input-availability-report.md",
    "metadata-visibility-report.md",
    "deployment-summary.md",
    "evaluation-summary.md",
    "permission-and-safety-summary.md",
    "skill-lifecycle-summary.md",
    "phase-4-exit-gate-evidence.md",
]

# Alternate acceptable report names for compatibility
ALTERNATE_REPORTS = {
    "skill-lifecycle-summary.md": "lifecycle-and-rollback-summary.md",
    "phase-4-exit-gate-evidence.md": "phase-4-consolidated-evidence-report.md",
}

DISALLOWED_TOKENS = [
    "NOT_EXECUTED",
    "NOT_RECORDED",
    "NOT_ASSIGNED",
    "PENDING",
    "PENDING_HUMAN_DECISION",
]

def validate_exit_gate(reports_dir: Path) -> Tuple[bool, List[str]]:
    """
    Validates all Phase 4 exit evidence report files in reports_dir.
    Returns (is_valid, list_of_error_messages).
    """
    errors: List[str] = []
    
    if not reports_dir.exists() or not reports_dir.is_dir():
        return False, [f"Reports directory '{reports_dir}' does not exist or is not a directory."]
    
    for report_name in REQUIRED_REPORTS:
        target_path = reports_dir / report_name
        if not target_path.exists() and report_name in ALTERNATE_REPORTS:
            alt_path = reports_dir / ALTERNATE_REPORTS[report_name]
            if alt_path.exists():
                target_path = alt_path
        
        if not target_path.exists():
            errors.append(f"MISSING: Required report '{report_name}' was not found in '{reports_dir}'.")
            continue
        
        content = target_path.read_text(encoding="utf-8")
        if not content.strip():
            errors.append(f"EMPTY: Report '{target_path.name}' is empty.")
            continue
        
        found_tokens = [tok for tok in DISALLOWED_TOKENS if tok in content]
        if found_tokens:
            errors.append(
                f"UNEXECUTED: Report '{target_path.name}' contains placeholder token(s): {', '.join(found_tokens)}."
            )
            
    is_valid = len(errors) == 0
    return is_valid, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Phase 4 Exit Gate Evidence")
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path(__file__).resolve().parents[3] / "docs" / "reports" / "phase-4-native-sharepoint-skills",
        help="Path to Phase 4 reports directory",
    )
    args = parser.parse_args()

    print(f"Validating Phase 4 Exit Gate Evidence in: {args.reports_dir}")
    is_valid, errors = validate_exit_gate(args.reports_dir)

    if is_valid:
        print("SUCCESS: All Phase 4 exit gate evidence reports are present, complete, and verified.")
        return 0
    else:
        print(f"EXIT GATE VALIDATION FAILED: {len(errors)} error(s) found.")
        for err in errors:
            print(f"  - {err}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
