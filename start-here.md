# Resume `docx-to-content` Phase 1 Implementation — Task 17 (CEIS pilot), awaiting plan confirmation

## Authoritative Inputs

Before changing anything, read in full:

1. `docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design-v3-ammendments.md` — the authoritative v3 spec (includes the v3.1 Deviation Notice, Section 14a authoring guidance, Section 14b future-output-profiles/SharePoint boundary).
2. `docs/superpowers/plans/2026-07-25-docx-to-content-phase1-implementation-plan-v3-ammendments.md` — the authoritative v3 plan (includes rewritten Task 0/Task 2 build-from-scratch deviation, Task 15a, Task 15b).
3. `docs/implementation-baseline.md` — Task 0 reconnaissance findings.
4. This file — the actual, verified current status. Trust this over any other handoff summary; verify against `git log` in the worktree regardless.

The v1 spec/plan (`2026-07-25-docx-to-content-plugin-design.md` / `...-implementation-plan.md`, no `-ammendments` suffix) are superseded, kept only for historical comparison.

## Where the work lives

All implementation work is happening in a git worktree, **not** on `main`:

```text
worktree path:   .claude/worktrees/docx-to-content-phase1
branch:          worktree-docx-to-content-phase1
plugin path:     plugins/docx-to-content/
SDD ledger:      .superpowers/sdd/2026-07-25-docx-to-content-phase1-implementation-plan-v3-ammendments/progress.md
```

The SDD ledger is the authoritative task-by-task record — every task's commits, review outcomes, fix rounds, and deferred/parked findings are logged there. Read it before assuming anything about what's done.

## Actual Current Status (verified, not reported)

**Tasks 1–16 are complete**, each independently reviewed via `superpowers:subagent-driven-development` (fresh implementer per task, fresh reviewer per task, TDD throughout). Plus these follow-up fixes discovered and closed along the way:

- **Task 10b** — fixed a media-ref normalization false-positive in canonical content-loss/duplication validation.
- **Task 14b** — wired `cmd_render` in `cli.py` (was a stub through Task 14).
- **cmd_convert fix** — wired `cmd_convert` to `convert_and_promote` (was calling the raw, unvalidated builder). This was the fix that made the full `analyze → confirm → convert → render` chain genuinely work end-to-end via the real CLI for the first time.

As of Task 16, the pipeline is proven to generalize beyond CEIS via two synthetic fixtures (`small_single.docx`, `repeated_headings.docx`), including the architecturally central proof that chunk IDs remain stable when an unrelated section is inserted earlier in a document.

**Two items remain tracked but non-blocking** (logged in the SDD ledger, not yet done): consolidating three independent path-safety implementations into one shared module; adding test coverage for `cmd_convert`'s WARN-without-disposition exit path.

## Task 17 — CEIS pilot run — IN PROGRESS, gated on human confirmation

Task 17 is explicitly gated: `analyze` runs freely, but `confirm`/`convert`/`render`/Task 18 require **explicit human confirmation** before proceeding — this is a deliberate architectural control (see spec Section 7.1/7.2: "no all-in-one command may bypass plan confirmation"), not an oversight.

### What's happened so far in Task 17

1. **Task 17A — initial analysis.** Ran `analyze` against the real CEIS Manual (`sourcedocuments/CEIS MANUAL - working version.docx`, SHA-256 `c804b65559ff8ad8d3a8dd66f01067ab468191a3487384514cdd1614a9f9178c`, 92MB, 159 headings, 320 images incl. 37 legacy `.emf`). Found two real, confirmed defect-detection false negatives in the analysis stage itself (not the source document):
   - `raw_toc_detected: false` when a real Word TOC dump was present (the CEIS TOC uses a slug-anchor link shape, not the previously-tested `_Toc`-bookmark shape).
   - `glued_images: false` when two real glued-image headings were present (the CEIS pattern has the image *before* the heading text; only the reverse ordering was previously tested).
   - Also found: ~133 of 159 headings use whole-heading bold wrapping (`### **Data Capture Requirements**`) that pandoc's extraction preserves as literal markdown — not a detection bug, a genuine document-quality/normalization need.

2. **Task 17A.1 remediation** (via subagent, TDD, independently reviewed with one fix round for a marker-mismatch corruption bug in the new normalizer): fixed both detection false negatives, added a new `pandoc_fixes/heading_emphasis.py` cleanup module (strips whole-heading emphasis wrapping, wired into the real convert pipeline), extended `analyze-report.json` with new statistics (tables: 17, local links: 185, image refs: 341, footnotes: 0, generated TOC entries: 159). Rerun against the real CEIS document confirmed all defect signals now correctly report `true`.

3. **CRITICAL FIX — anchor identity normalization** (applied directly, not via subagent, after a session-limit interruption mid-dispatch): the new heading-emphasis normalization from step 2 created a real architectural bug — `analyze_structure.py` computed structural-anchor `stable_key` from **raw** (unnormalized) heading text at analysis time, while `chunking.py`'s reconciliation recomputed `stable_key` from **cleaned** (normalized) text at convert time. For any heading affected by the new normalizer (~133 of 159 real CEIS headings), these would diverge, causing `MissingAnchorError` on nearly the whole document during a real `convert` run. **Fixed** by normalizing heading text inside the single shared function (`iter_heading_matches`) both analysis and reconciliation call, guaranteeing identical identity computation on both sides. TDD-verified (`test_anchor_identity_survives_whole_heading_emphasis_normalization`, red→green), full suite 386 passed/1 skipped, and independently spot-checked against a fresh real-CEIS `analyze` rerun (confirmed clean `stable_key` values, e.g. `data-capture-standards-data-capture-requirements--6eaa3803` with no `**` anywhere). Commit `af34d66`.

### What is NOT done yet — explicitly withheld pending your decision

- **`confirm`/`convert`/`render` have NOT been run against the real CEIS document.** No canonical or rendered CEIS output exists yet.
- **Task 18 (cutover) has not started.**
- **The interactive orchestration sub-agent has not been created.** Authorized future deliverable, explicitly sequenced *after* Task 17 completes — the completed Task 17 interaction is meant to be the primary design input for it, not invented ahead of time.

### Decision made — constrained Option B, approved

The user reviewed the Task 17A final decision report and made these calls (do not re-litigate, do not re-ask):

1. **Approved constrained Option B**: ~159 structural anchors retained for lineage/addressability, but grouped into **~25 maintainable canonical topic files** (one per normalized top-level section; level-3/4 headings stay as in-file structure inside their parent topic, not separate files). Explicitly rejected treating 159 files as the default just because the current code already produces that.
2. **Approved a minimal `publication-map.json`** contract — must reference the canonical package identity (not just a manifest hash), reference canonical topic IDs, define explicit order, and support hierarchy via `parent_topic_id` (small, versioned, no generalized publishing engine).
3. **Approved the preamble disposition** as recommended: title/subtitle/version preserved as publication metadata; "New this Version" needs inspection against the real source before deciding if it's meaningful; `Ctrl+F` instruction omitted from canonical content (destination-specific, misleading once split into multiple files); `image1.png` needs classification (branding/publication/decorative/obsolete) before deciding whether to retain, with alt text if retained; Word-generated TOC removed (already working).
4. **Table fidelity — DONE, resolved.** Root cause found and fixed directly (not via subagent): `_TABLE_SEPARATOR_ROW`'s regex was matching bare dash-only horizontal-rule lines as if they were table separator rows. Fixed to require a pipe character. Corrected real CEIS counts: 0 raw valid tables (every real table lacks a separator row before cleanup) → 19 post-cleanup (cleanup repairs all of them). Table-block count stable at ~20 before/after — no table split, duplicated, or lost. Commit `0d8320b`.

Also required (from the same approval): **topic identity must be independent of grouping strategy** — three distinct identities (structural anchor / canonical topic / publication-map entry), a structural anchor must survive its parent topic being renamed/reorganized/split, and topic IDs must be deterministic (not derived from filenames or array position alone).

### Next action on resume — this is the actual remaining work

**Task 17-topic-grouping** (tracked in the task list, not yet started): the bounded engineering for constrained Option B. Per the user's explicit scope:

1. Topic-boundary grouping: normalize level-1/level-2 tier inconsistency into ~25 explicit topic boundaries (present them for review before conversion, don't implement as a blind "all level-1/2 are equivalent" rule).
2. Topic identity (deterministic, independent of filename/array position) — separate from structural-anchor identity.
3. Internal-anchor metadata on topic chunks (`stable_key`, `source_heading_path`, `occurrence`, `heading_level` for every anchor a topic contains, ordered if sequence matters — don't duplicate full source content).
4. Minimal `publication-map.json` contract + writer.
5. Packaging / validation / rendering consumption changes for the new grouped shape.
6. Full test list from the user's directive: every anchor assigned exactly once; no unassigned/multiply-assigned anchors; child headings stay in source order; topic IDs deterministic; structural-anchor IDs stable across grouping-strategy changes; publication-map order independent of directory order; rendered navigation follows the publication map; no generated TOC survives; meaningful preamble retained per the approved disposition; grouped reconstruction is lossless/non-duplicating; stale files absent after promotion; failed grouping/map validation retains prior accepted output.
7. Preserve the existing fine-grained (159-file) mode as a still-supported, still-tested strategy — do not silently remove or redefine what `strategy`/`chunk_level` mean without presenting the contract change first.

**After that's built and reviewed**, per the user's checkpoint requirements: rerun CEIS analysis, present the proposed ~25 topic boundaries (topic ID, title, first anchor, anchor count, approx size, child-heading count each), present the preamble/image findings, produce a new draft plan + plan identity, and **stop for explicit plan confirmation** — same gate as before. Do not run `confirm`/`convert`/`render`/Task 18 without it.

## Efficiency notes for continuing this session or a fresh one

- The SDD ledger (`.superpowers/sdd/2026-07-25-docx-to-content-phase1-implementation-plan-v3-ammendments/progress.md`, inside the worktree) is the fastest way to reconstruct full task-by-task history without re-reading the whole conversation — every commit hash, review verdict, fix round, and deferred/parked finding is there. It also has a live task list (via TaskCreate/TaskUpdate) tracking exactly what's done vs. pending, including the follow-up items below.
- Real CEIS `analyze` output currently lives at `/tmp/ceis-task17a/analysis-fixed/` (post all fixes as of the table-fidelity fix) — earlier snapshots (`analysis/`, `analysis-final/`, `analysis-v2/`) are stale, non-authoritative comparison artifacts. This is `/tmp`, so it may not survive a machine restart — rerun `analyze` if it's gone, it's cheap (a few minutes).
- This repo's `CLAUDE.md`: use the cheapest viable sub-agent model per dispatch, and don't spawn a sub-agent when the job doesn't need one — several fixes this session (the critical anchor-identity fix, the table-count regex fix) were applied directly via Read/Edit/Bash rather than a dispatched agent, specifically because they were small, well-understood, and self-verifiable. Use that same judgment: dispatch `superpowers:subagent-driven-development` (fresh implementer + fresh reviewer per task) for the topic-grouping engine above — it's genuinely large, multi-file, architecturally significant work — but don't reflexively dispatch an agent for a five-line fix.
- **Continue work in the existing worktree, do not create a new one.** Worktree path: `.claude/worktrees/docx-to-content-phase1`, branch `worktree-docx-to-content-phase1`. As of this session, `main` and the worktree branch are in sync (both pushed to `origin`, `main` fast-forwarded to match) — but new work should still land on `worktree-docx-to-content-phase1` first (or a fresh branch off it), reviewed, then merged, not committed straight to `main`.
- `origin` is `https://github.com/richfrem/manual-conversion-poc.git`. `main` is the default branch on GitHub as of this session (it wasn't before — the worktree branch was accidentally first-pushed and became default; this was corrected).
- A `temp/bundles/manifest.json` exists for bundling key files via the `context-bundler` skill into a single `.md` for external review (e.g. sharing with another model) — keep it updated as files change if that hand-off is still wanted.
