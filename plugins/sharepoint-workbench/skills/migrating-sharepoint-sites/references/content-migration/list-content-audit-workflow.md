# List content audit: the three phases

## Contents

- [Why two phases must both run](#why-two-phases-must-both-run)
- [Phase 1: deterministic script execution](#phase-1-deterministic-script-execution)
- [Phase 2: interpretive analysis](#phase-2-interpretive-analysis)
- [Repair boundary (not part of the read-only audit)](#repair-boundary-not-part-of-the-read-only-audit)

Run every command from the skill's root.

## Why two phases must both run

- **Phase 1** is 100% deterministic script execution, with no interpretation or judgment. It produces raw,
  zero-PII data tables (`SITE-FULL-CONTENT-PARITY-REPORT.md`, `site-full-content-parity-audit.csv`). It answers
  "what differs", never "why" or "does it matter".
- **Phase 2** is where the agent reads the Phase 1 output and does the analysis: root-causing variances, flagging
  false positives, writing one-off scratch scripts to dig into a specific column or list, and fixing bugs in the
  Phase 1 scripts when the data proves the script (not the migration) is wrong.

Never treat Phase 1 numbers as the final word. The report has been silently wrong before and was caught only by
someone reading it.

## Phase 1: deterministic script execution

### Step 0. Describe the site and build or refresh the identity-list ID mapping

Copy `scripts/audit-config.example.json` to `audit-config.json` and describe the site being audited: its lists, lookup
columns and business-key columns (see the audit config section of the scripts reference). Keep your copy out of version control.

Rebuilding the identity-list ID mapping is only needed after a re-migration of the identity list. Required whenever the target
identity list was wiped or re-migrated (for example by a migration-tool redeploy), which shifts item IDs and invalidates the previous `id-mapping-verified.json`.

```powershell
pwsh -File scripts/export-list-content-pairs.ps1 -ListName Authors -OnPremUrl https://onprem.example.com/sites/demo -UseDefaultCredentials
python -B scripts/analyze-list-mapping-assurance.py --audit-config audit-config.json --delete-pii-after
```

### Step 1. Export fresh paired list content (source and SharePoint Online)

```powershell
pwsh -File scripts/export-list-content-pairs.ps1 -OnPremUrl https://onprem.example.com/sites/demo -UseDefaultCredentials
pwsh -File scripts/audit-list-lookup-reconciliation.ps1 -OnPremUrl https://onprem.example.com/sites/demo -ConfigPath <config-file>.psd1 -UseDefaultCredentials
```

### Step 2. Generate the zero-PII executive data tables

```powershell
python -B scripts/analyze-lookup-variances.py --list-name ALL
```

Always pass `--list-name ALL` explicitly for the real run. If you smoke-test a single list (for example
`--list-name <ListName>`) you must also override `--output-md` and `--output-csv` to a scratch path. Otherwise the
default output paths silently overwrite (thin out) the canonical site-wide report. This exact failure happened once
already.

This step produces only raw tables: per-list parity %, root-cause category counts, and per-lookup-column pointer
health. It does not produce a narrative or root-cause writeup; that is Phase 2.

## Phase 2: interpretive analysis

Required after every Phase 1 run. Phase 1's `SITE-FULL-CONTENT-PARITY-REPORT.md` is intentionally thin: it is
data, not analysis. The analysis lives in a separate, agent-authored narrative document,
`.agents/scratch/audit-reports/COMPREHENSIVE-LIST-BY-LIST-VARIANCE-ANALYSIS.md`. After every Phase 1 run,
refresh it (do not leave a stale one-off from a prior session) with at least these sections:

1. **Column / Schema Metadata Variance Summary.** Which columns were renamed, excluded or restructured between
   the source and SharePoint Online for each list, sourced from the wave matrix and field renames, not just row-level diffs.
2. **Absolute 100% Match List Roster.** Lists with zero real variance (source rows equal co-existing rows equal
   perfect rows). Call out any list where Phase 1's "100.0%" is misleading because `Co-Existing` rows are far below
   `Source Rows` (rows missing entirely from SPO are excluded from the Parity Rate denominator, a confirmed blind
   spot).
3. **Lists With Real Variances: Breakdown.** For every list below 100%, the actual top differing columns with
   counts, tallied from `site-full-content-parity-audit.csv` (not the truncated "Top Differing Columns" preview in
   the executive table), and a call on whether each is a false positive (cosmetic or expected) or a real gap.
4. **Consolidated Lookup Column Gap Analysis (site-wide, single section).** One master table of every lookup column
   across every list, each row showing total pointers, % matched, % blank or stale, and root cause, sorted so the
   biggest real gaps are first. This section is the most likely to surface script bugs, for example a lookup definition that
   names the wrong column.
5. **Known Script Bugs Found This Pass.** Anything where the Phase 1 script itself is wrong (bad column-name guess,
   stale duplicate lookup definitions, misleading metric), with the fix applied and confirmed by re-running Phase 1.

Use targeted scratch PowerShell or Python (in `.agents/scratch/`) to investigate any suspicious number, such as
comparing a raw CSV header against the script's hardcoded column-name guess. A `0 Source Pointers in Dataset` row is
a signal to check the script, not a real finding.

Findings root-caused here that are expected to recur belong in your local notes of known issues (see the scripts reference).

## Repair boundary (not part of the read-only audit)

The audit ends after Phase 2. This skill ships no repair script. If a human confirms that Phase 2 shows a real gap (not
a script bug or a false positive) and chooses to repair it, that is a separate, explicitly authorized activity with its
own dry run, confirmation gate and evidence, run by the user and never by an agent as the next step of this audit.
