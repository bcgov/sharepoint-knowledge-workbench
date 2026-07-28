# Resume `docx-to-content` Phase 1 — Task 18 (real CEIS cutover), awaiting plan confirmation

## Authoritative Inputs

Before changing anything, read in full:

1. `docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design-v3-ammendments.md` — the authoritative v3 spec (includes the v3.1 Deviation Notice, Section 14a authoring guidance, Section 14b future-output-profiles/SharePoint boundary).
2. `docs/superpowers/plans/2026-07-25-docx-to-content-phase1-implementation-plan-v3-ammendments.md` — the authoritative v3 plan for Tasks 0–16.
3. `docs/superpowers/plans/2026-07-28-docx-to-content-topic-grouping.md` — the plan for the grouped-strategy work (Tasks 1–9 of that plan), **complete and merged** — see Actual Current Status below.
4. `docs/implementation-baseline.md` — Task 0 reconnaissance findings (dated 2026-07-25; paths in it reference the pre-rename `sourcedocuments/`/`output/` directory names — historically accurate, not a live reference).
5. This file — the actual, verified current status. Trust this over any other handoff summary; verify against `git log` regardless.

The v1 spec/plan (`2026-07-25-docx-to-content-plugin-design.md` / `...-implementation-plan.md`, no `-ammendments` suffix) are superseded, kept only for historical comparison.

**Broader context:** this repo is Phase 1 of a larger initiative — see `docs/vision/README.md` and `docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md` for direction beyond Phase 1 (repository/plugin boundaries, SharePoint delivery, agents, publication, evaluation). Those documents propose future direction; they do not authorize work beyond the current approved Phase 1 plan.

## Where the work lives (changed since the last resume)

**There is no separate worktree anymore.** The `docx-to-content-phase1` worktree (branch `worktree-docx-to-content-phase1`) that hosted Tasks 0–16 and the topic-grouping work has been merged into `main` and removed (both the worktree directory and the branch). All work now happens directly on `main` in this repo:

```text
plugin path:   plugins/docx-to-content/
run tests:     cd plugins/docx-to-content && python3 -m pytest tests/ -q
```

`main` is **10 commits ahead of `origin/main`** as of this session (the topic-grouping work has not been pushed yet) — check `git log origin/main..main --oneline` before assuming remote state matches local.

The old task-by-task SDD ledger for Tasks 0–16
(`.superpowers/sdd/2026-07-25-docx-to-content-phase1-implementation-plan-v3-ammendments/progress.md`)
lived inside that now-removed worktree under a gitignored (`.superpowers/`), uncommitted path — it
no longer exists. This is expected per the `subagent-driven-development` skill's own design ("the
git history is the record now"), not data loss: `git log` on `main` is the authoritative record for
those tasks' commits. The topic-grouping plan (Tasks 1–9) was executed via `executing-plans`
(inline), not SDD, so it never had a ledger file — the 9 commits on `main` (`b903224`..`90a6033`,
merged via `99faab2`) are its record.

Repo-root directory names changed this session: `sourcedocuments/` → `intake/`, `output/` →
`runs/` (git-mv'd, history preserved). `CLAUDE.md`/`architecture.md` reflect the new names.

## Actual Current Status (verified, not reported)

**Tasks 0–16 are complete** (Phase 1 core pipeline: analyze → confirm → convert → render, full CLI
wiring, atomic promotion, generalization proven beyond CEIS via synthetic fixtures). See prior
session detail in git history if needed — the ledger summarizing fix rounds/reviews is gone (see
above), but every commit message on `main` up through `890e031` documents itself.

**Task 17 (CEIS pilot analysis + defect-detection fixes) is complete:**
- Real CEIS `analyze` run found and fixed two real analysis-stage defect-detection false negatives (TOC slug-anchor shape, image-before-text glued images), added whole-heading emphasis normalization, and fixed a critical anchor-identity divergence bug (analysis-time vs. reconcile-time heading normalization) that would have broken `convert` on ~133/159 real CEIS headings.
- Table-fidelity bug fixed (a regex over-matched dash-only horizontal rules as table separators).
- **User-approved decision, still binding:** constrained Option B — ~159 structural anchors retained for lineage, grouped into ~25 canonical topic files (one per normalized top-level section); a minimal `publication-map.json` contract; specific preamble/image dispositions (title/subtitle/version as publication metadata, `Ctrl+F` instruction omitted, Word TOC removed, `image1.png` needs classification before disposition).

**Task 17-topic-grouping is complete, reviewed via inline TDD execution, and merged to `main`**
(commits `b903224`..`90a6033`, merge commit `99faab2`). Built exactly what Task 17's decision
required:
- `identity.make_topic_id` — deterministic topic identity, independent of structural-anchor identity.
- `topic_grouping.compute_topic_boundaries` — every level-1 heading starts a topic; child headings fold in, in source order; every heading assigned to exactly one topic.
- `proposed_topics` preview in `analyze-report.json` (topic_id, title, first_anchor_path, anchor_count, child_heading_count, approx_size_chars) — this is what a human reviews before confirming `strategy: "grouped"`.
- `contracts.PublicationMap`/`PublicationMapEntry` + `publication_map.py` writer/loader — `publication-map.json` sidecar, explicit `order` (contiguous, gap-free), `parent_topic_id` reserved for future hierarchy.
- `package.build_grouped_canonical_package` — one canonical chunk file per topic; `ChunkMetadata.anchors` preserves every folded structural anchor's `stable_key`/`source_heading_path`/`occurrence`/`heading_level`.
- `convert.py`/`plans.py`/`cli.py` wiring — `plan.strategy == "grouped"` dispatches to the grouped builder; no new CLI flags needed (strategy already flows through the plan JSON).
- `validate_canonical.py` grouped-aware checks — anchor-assignment completeness (`unassigned_structural_anchor`, `duplicate_structural_anchor_assignment`) and publication-map consistency (`missing_publication_map`, `publication_map_chunk_mismatch`, `publication_map_order_invalid`); existing content-loss/duplication check works unmodified (chunk-shape-agnostic).
- `renderers/multipage_markdown.py` — renders in publication-map order when present, falls back to manifest order otherwise (unchanged) when absent.
- Full real-CLI end-to-end proof (`analyze` → `confirm` with `strategy: "grouped"` → `convert` → `render`) against the `repeated_headings.docx` fixture, plus updated `SKILL.md`s and a new `references/publication-map-contract.md`.
- The existing fine-grained (`"single"`/`"chunked"`, one-file-per-heading) mode is unchanged and fully still tested — grouped is additive.
- Full plugin suite: **421 passed, 1 skipped** as of the merge.

### What is NOT done yet — explicitly withheld pending your decision

- **`confirm`/`convert`/`render` have NOT been run against the real CEIS document with the grouped strategy** (or any strategy, since Task 17A). No canonical or rendered CEIS output exists yet.
- **Task 18 (cutover) has not started.**
- **The interactive orchestration sub-agent has not been created** — explicitly sequenced after Task 18 completes, not invented ahead of time.
- **The preamble/image1.png dispositions from Task 17's approved decision have not been re-verified against the real document** since the grouped-strategy engineering landed — do this as part of the Task 18 rerun, not assumed still accurate.

## Next action on resume — this is the actual remaining work

**Task 18 — CEIS pilot cutover, gated on human confirmation:**

1. Rerun `analyze` against the real CEIS document (`intake/CEIS MANUAL - working version.docx`) — cheap, a few minutes. Confirm the defect-signal/statistics output still matches Task 17's findings (nothing since then should have changed analysis-stage behavior for the ungrouped path).
2. Review the real `proposed_topics` preview from `analysis-report.json` — present the actual ~25 topic boundaries (topic ID, title, first anchor, anchor count, approx size, child-heading count each) for explicit human review, per Task 17's approved decision. Do not assume the earlier ~25 estimate is exact; report the real count.
3. Set `strategy: "grouped"` on the draft plan and produce a new draft plan identity.
4. Present the preamble/image findings (title/subtitle/version, `Ctrl+F` omission, Word TOC removal, `image1.png` classification) re-verified against the current pipeline.
5. **Stop for explicit plan confirmation** — same gate as before (spec Section 7.1/7.2: "no all-in-one command may bypass plan confirmation"). Do not run `confirm`/`convert`/`render` without it.
6. Once confirmed: `confirm` → `convert` → `render` against the real CEIS document. Verify: validation status (PASS or a fully-dispositioned WARN — a FAIL on the real document is a real finding, not something to work around silently), chunk/topic counts match the confirmed plan, rendered index reflects all ~25 topics in the right order, no generated TOC survives, `publication-map.json` present and consistent.
7. Only after a clean, human-reviewed real CEIS run: consider Task 18 complete and move to whatever's next (the interactive orchestration sub-agent, or Phase 2 per `docs/vision/`, per further direction).

## Efficiency notes for continuing this session or a fresh one

- Work directly on `main` — there is no worktree to re-enter. If isolation is wanted for Task 18 (e.g. to keep `main` clean until the real CEIS run is reviewed), create a fresh worktree via `superpowers:using-git-worktrees` rather than assuming the old one still exists.
- This repo's `CLAUDE.md`: use the cheapest viable sub-agent model per dispatch, and don't spawn a sub-agent when the job doesn't need one. Several fixes across Tasks 17/17-topic-grouping were applied directly via Read/Edit/Bash rather than a dispatched agent because they were small, well-understood, and self-verifiable — use that same judgment for Task 18's real-document rerun (mechanical, not architecturally novel) versus anything that turns out to need new engineering (dispatch `superpowers:subagent-driven-development` for that, per the project's established pattern).
- `origin` is `https://github.com/richfrem/manual-conversion-poc.git`. `main` is the default branch on GitHub. Local `main` is ahead of `origin/main` by 10 commits (the topic-grouping work) — confirm with the user before pushing.
- A `temp/bundles/manifest.json` exists for bundling key files via the `context-bundler` skill into a single `.md` for external review — keep it updated as files change if that hand-off is still wanted.
