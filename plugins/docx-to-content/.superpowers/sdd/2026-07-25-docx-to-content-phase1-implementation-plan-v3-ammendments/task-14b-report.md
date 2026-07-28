# Task 14b Report — Wire `cmd_render` in `cli.py`

## `cmd_render` implementation (summary)

`scripts/cli.py`:

1. Added a module-level renderer registry (Task 12's `RendererRegistry`),
   populated once at import time with the one shipped renderer:

   ```python
   _RENDERER_REGISTRY = renderer_protocol.RendererRegistry()
   _RENDERER_REGISTRY.register(multipage_markdown.MultipageMarkdownRenderer())
   SUPPORTED_RENDERERS = frozenset(_RENDERER_REGISTRY._renderers.keys())
   ```

   `SUPPORTED_RENDERERS` is kept (now derived from the registry rather than
   hand-maintained) because `tests/contract/test_future_output_profiles.py`
   already asserts against it.

2. `cmd_render` body:

   ```python
   def cmd_render(args):
       try:
           renderer = _RENDERER_REGISTRY.get_renderer(args.renderer)
       except renderer_protocol.UnknownRendererError as exc:
           raise UsageError(str(exc)) from exc

       canonical_path = Path(args.canonical)
       if not canonical_path.exists():
           raise PreconditionError(f"canonical directory not found: {args.canonical}")

       try:
           loaded_package = package.CanonicalPackage.load(canonical_path)
       except package.CanonicalPackageError as exc:
           raise ValidationFailError(str(exc)) from exc

       _result, report, promoted, _output_dir = validate_rendered.render_and_promote(
           loaded_package, Path(args.output), renderer=renderer
       )
       if not promoted:
           raise ValidationFailError(
               f"render validation FAILED for canonical package {args.canonical} "
               f"with renderer {args.renderer!r}: "
               f"{[issue.message for issue in report.issues]}"
           )
       return EXIT_PASS
   ```

   Steps: (1) resolve `--renderer` through the Task 12 registry — unknown
   name -> `UnknownRendererError` -> `UsageError` (exit 4); (2) precondition
   check the `--canonical` path exists (exit 3, matching every other
   `_require_source`-style precondition in this file); (3) load+fully
   revalidate the canonical package via `package.CanonicalPackage.load()`
   (Task 12) — any `CanonicalPackageError` (schema, integrity, or
   undispositioned-WARN/FAIL) maps to `ValidationFailError` (exit 2); (4)
   call `render_and_promote()` (Task 14) with the loaded package and
   `--output` as `output_root`; (5) map its `promoted` flag to the exit
   code.

## Exit-code mapping — confirmed reuse of `cmd_convert`'s pattern

- `cmd_convert` maps `PlanVerificationError` (untrustworthy plan) to
  `UsageError` (4), and `AnchorReconciliationError`/`MediaError` (malformed
  content discovered while building the package) to `ValidationFailError`
  (2).
- `cmd_render` mirrors this exactly: `CanonicalPackageError` (the
  equivalent "this content cannot be trusted as-is" failure class, raised
  by `CanonicalPackage.load()`) -> `ValidationFailError` (2). No new
  exit-code mapping pattern was invented.
- `render_and_promote()`'s PASS/FAIL -> promoted/not-promoted result is
  mapped to exit 0 / exit 2, exactly mirroring how `cmd_convert` implicitly
  relies on `convert.convert_document` never leaving a FAIL state
  unraised — here it is explicit because `render_and_promote()` returns a
  `promoted: bool` rather than raising, so `cmd_render` raises
  `ValidationFailError` itself on `promoted is False`.
- Unknown `--renderer` -> `UsageError` (4) matches the CLI's other
  "unsupported input" cases (unsupported subcommand, missing required
  argument, unconfirmed plan passed to `run`).

No print statements were added on success/failure paths — `cmd_analyze`
and `cmd_convert` print nothing on success either (errors are reported
centrally by `main()`'s `except CLIError` handler), so `cmd_render` follows
that same convention.

## Tests added (`tests/unit/test_cli.py`)

All three required tests were added, plus the reused `_build_canonical_package`
helper (built via `convert.convert_and_promote` directly — the Task 9/10/11
helper — rather than through `cli.main(["convert", ...])`, because
`cmd_convert` currently calls the unvalidated `convert.convert_document`
entry point, not `convert_and_promote`; `CanonicalPackage.load()` requires
an actually-validated/promoted package. This is a pre-existing gap in
`cmd_convert`'s own wiring, out of this task's scope, and is called out
in a comment in the test file and again here for visibility).

1. **Real end-to-end CLI success** —
   `test_render_end_to_end_via_cli_produces_rendered_output`: builds a
   real canonical package from `tests/fixtures/repeated_headings.docx`,
   runs `cli.main(["render", "--canonical", ..., "--renderer",
   "multipage-markdown", "--output", ...])`, asserts `rc == 0` and that
   `rendered-output/{index.md, pages/*.md, renderer-validation.json}`
   exist with `renderer-validation.json["status"] == "PASS"`. **Result:
   PASS.**
2. **Unknown renderer rejected (exit 4)** — pre-existing
   `test_unsupported_renderer_exits_4` already covered this case exactly
   (unregistered renderer name -> exit 4); verified it still passes
   unchanged against the new registry-based implementation. **Result:
   PASS.**
3. **Validation FAIL -> exit 2** —
   `test_render_validation_fail_exits_2`: builds a real canonical package,
   then tampers with one chunk's on-disk content (breaking its recorded
   `content_sha256`), which makes `CanonicalPackage.load()` raise
   `CanonicalPackageIntegrityError`. Asserts `rc == 2`. **Result: PASS.**
4. Also added `test_render_missing_canonical_dir_exits_3` (precondition
   check, exit 3) for completeness alongside the three required tests.

No pre-existing "`cmd_render` raises `NotImplementedError`" stub test
existed in `tests/unit/test_cli.py` to convert into a failing-test-first
proof; the closest thing was `test_unsupported_renderer_exits_4`, which
already asserted correct behavior for a different code path (unknown
renderer, checked before the old `NotImplementedError` was ever reached).
Confirmed by running the full suite against `git stash` (pre-change state)
that `cli.SUPPORTED_RENDERERS`/`cmd_render` previously hit the
`NotImplementedError` -> exit 1 path for any *supported* renderer name —
this was verified manually (not committed as a separate failing test)
before implementing, per the task's "confirm this now proves real
rendering happens end-to-end" instruction being satisfied by test #1 above.

## `render-content/SKILL.md` update

Removed the "Known gap" paragraph documenting `cmd_render` as a
`NotImplementedError` stub. Replaced with a paragraph stating `cmd_render`
is fully wired (registry resolution -> `CanonicalPackage.load()` ->
`render_and_promote()`), and that the rest of the document describes the
actual, tested contract rather than an intended future one.

A pre-existing contract test,
`tests/contract/test_skill_contracts.py::TestRenderContentSkillContract::test_documents_known_gap_honestly`,
had encoded the *old* gap as a requirement (asserting the skill doc must
say "not yet" or "NotImplementedError"). Since this task closes that gap,
the test itself was updated to
`test_documents_cmd_render_as_fully_wired` — asserting the skill doc says
"wired" and no longer contains "not yet" / "NotImplementedError". This is
a deliberate, in-scope change: the test encoded a contract that this task
is explicitly meant to close.

## Full suite results

- **Before** (`git stash`, pre-change state): `356 passed, 1 skipped`
- **After** (all changes applied): `359 passed, 1 skipped`
- 3 net new tests (`test_render_end_to_end_via_cli_produces_rendered_output`,
  `test_render_missing_canonical_dir_exits_3`,
  `test_render_validation_fail_exits_2`); no regressions. The 1 skip is
  pre-existing and unrelated to this task.

## Commit

Commit hash: to be filled in after `git commit` (see below — recorded
after the commit is created).

## Deviations, with rationale

1. **`_build_canonical_package` test helper uses `convert.convert_and_promote`
   directly, not `cli.main(["convert", ...])`.** The task prompt says to
   reuse "helper infrastructure to construct [canonical packages] from
   fixtures" from Tasks 9-14, and separately says the CLI-path test's value
   is proving the CLI path works for *render* specifically (the identified
   gap). Discovered during implementation: `cmd_convert` in `cli.py` calls
   `convert.convert_document` (Task 9's original, unvalidated/unpromoted
   entry point), not `convert.convert_and_promote` (Task 9/10/11's full
   validate-then-atomically-promote pipeline) — so a canonical package
   produced via `cli.main(["convert", ...])` has only a placeholder
   `validation.json` (`status: "PENDING"`) and fails
   `CanonicalPackage.load()`'s own schema check. This is a pre-existing gap
   in `cmd_convert`'s wiring (not `cmd_render`'s, and not something this
   task's scope covers), so rather than silently work around it or expand
   scope to fix `cmd_convert`, the test uses `convert_and_promote` directly
   (matching how `test_validate_rendered.py`/`test_multipage_markdown.py`
   already build packages) and documents the reason in a code comment.
   Flagging this for the user: **`cmd_convert` does not currently produce a
   package that `cmd_render` (or any `CanonicalPackage.load()` caller) can
   consume** — a real `analyze -> confirm -> convert -> render` CLI
   pipeline run end-to-end today would fail at the `render` step with a
   validation error, because `convert`'s output was never actually
   validated/promoted. This looks like it needs its own follow-up task
   (wiring `cmd_convert` to `convert_and_promote` instead of
   `convert_document`) but was left untouched here since it's outside this
   task's explicit scope (`cmd_render` only).
2. Updated the pre-existing `test_documents_known_gap_honestly` contract
   test in `tests/contract/test_skill_contracts.py` rather than leaving it
   failing — it directly encoded the gap this task was scoped to close, so
   leaving it unmodified would have meant the suite could never pass with
   the gap actually closed.
