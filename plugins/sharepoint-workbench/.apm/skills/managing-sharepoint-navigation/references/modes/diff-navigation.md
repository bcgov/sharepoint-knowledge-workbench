# Mode: Diff Navigation

Validate the Excel workbook structure and compute operations diff against live snapshot.

## Workflow

1. Validate and compile workbook into navigation plan:
   ```bash
   python3 scripts/navigation_plan.py plan --workbook <path.xlsx> --out <plan.json>
   ```
   Add `--allow-missing-urls` if leaf nodes are permitted to lack URLs (otherwise treated as validation error).

2. Diff plan against snapshot:
   ```bash
   python3 scripts/navigation_plan.py diff --plan <plan.json> --snapshot <live-snapshot.json> --out <ops.json>
   ```

## Output Operations
The resulting `ops.json` contains ordered declarative operations:
- `create`: Node exists in workbook but not in live snapshot.
- `update`: Node exists in both but title, URL, or open-in-new-tab changed.
- `prune`: Node exists in live snapshot but not in workbook.
- `unchanged`: Node matches perfectly.
