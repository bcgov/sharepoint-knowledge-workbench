# Research IA Migration Tool

Consumes `../research-migration-manifest.json` (the approved proposal manifest) and, in `execute` mode only, performs the file moves/archives and reference rewrites for entries with `destination_status == "approved"`. Dry-run is the default expectation; `execute` must be invoked explicitly.

## Dependencies

Python 3.8+, `jsonschema` (`pip install jsonschema`). No other external packages.

## Design

- **Manifest is the single source of truth.** No move list is hardcoded in this tool.
- **Proposal manifest vs. execution plan are two different documents.** The full manifest (`research-migration-manifest.json`) legitimately contains `recommended`/`tentative` entries that are not execution-ready. `gen-exec-plan` extracts only `approved` entries into a standalone `execution-plan.json`, which is what `research-migration-schema-execution.json` validates. This keeps "propose" and "ready to run" as separate documents instead of overloading one schema to mean both.
- **Three-tier tree policy**, not one blanket exclusion list:
  - `PROHIBITED_MODIFICATION_TREES` (`docs/superpowers/`, `plugins/`) — never writable, no exception possible.
  - `RESTRICTED_DESTINATION_TREES` (`docs/reports/`) — writable only when the specific manifest entry carries `destination_exception_approved: true` (this is how `res-015`'s archive into `docs/reports/phase-4-native-sharepoint-skills/` is authorized without opening `docs/reports/` to arbitrary writes).
  - Everything else — no special restriction.
- **Idempotency via state classification**, not "fail on rerun." `determine_operation_state()` compares source/destination existence and hash:
  - source exists, dest absent → `pending` (do the move)
  - source absent, dest exists, dest hash == recorded source hash → `already-applied` (skip, success)
  - anything else (both exist, neither exists, hash mismatch) → fail closed, refuse to guess
- **Reference rewriting** handles two forms: Markdown link syntax `[text](path)` (relative-path-aware, anchor-preserving) and backtick-quoted bare repo-relative paths. Anything else found in a referencing file (plain prose mentioning a path) is left alone — `verify_no_stale_references` flags it after execution rather than the rewriter guessing at a risky text substitution.

## Usage

```bash
# 1. Validate the full proposal manifest's shape
python3 migrate.py validate --manifest ../research-migration-manifest.json --schema ../research-migration-schema.json

# 2. Generate and validate the execution plan (approved entries only)
python3 migrate.py gen-exec-plan --manifest ../research-migration-manifest.json --out execution-plan.json
python3 migrate.py validate-exec --plan execution-plan.json --schema ../research-migration-schema-execution.json

# 3. Dry-run against the real repository (default safe mode; makes no changes)
python3 migrate.py dry-run --manifest ../research-migration-manifest.json --repo-root ../../../.. --report dry-run-report.json

# 4. Execute (only after explicit approval; only approved entries act)
python3 migrate.py execute --manifest ../research-migration-manifest.json --repo-root ../../../.. --report execution-report.json

# 5. Verify the completed execution
python3 migrate.py verify --manifest ../research-migration-manifest.json --repo-root ../../../.. --report execution-report.json

# 6. Rollback if needed
python3 migrate.py rollback --report execution-report.json --repo-root ../../../..
```

`--repo-root` should point at the repository root (four `..` levels up from this tool's own location under `docs/reports/research-information-architecture/migration-tool/`).

## Testing

```bash
cd docs/reports/research-information-architecture/migration-tool
python3 -m pytest tests/test_migrate.py -v
```

All tests run against throwaway git fixture repositories created per-test (`FixtureRepo` in `tests/test_migrate.py`) — never the real corpus.

## Known limitations

- Reference detection covers Markdown-link syntax and backtick-quoted bare paths only. Plain-prose mentions of a path (no link, no backticks) are not rewritten — `verify_no_stale_references` flags these post-execution rather than the tool guessing at a text substitution that could corrupt unrelated prose.
- The tool does not currently scan for references itself; it relies on each manifest entry's `inbound_references` field, which was gathered opportunistically during corpus reading, not from a systematic repository-wide grep. A move/rename entry with an incomplete `inbound_references` list will leave references outside that list unrewritten. `verify_no_stale_references` performs a repo-wide post-execution scan as a backstop, but only for the specific old paths of entries that were actually moved this run.
