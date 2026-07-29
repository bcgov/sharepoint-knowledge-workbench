# Resume `docx-to-content` Phase 1 — engineering complete, one human sign-off item remains

## Authoritative Inputs

Before changing anything, read in full:

1. `docs/superpowers/specs/2026-07-25-docx-to-content-plugin-design-v3-ammendments.md` — the authoritative v3 spec (includes the v3.1 Deviation Notice, Section 14a authoring guidance, Section 14b future-output-profiles/SharePoint boundary).
2. `docs/superpowers/plans/2026-07-25-docx-to-content-phase1-implementation-plan-v3-ammendments.md` — the authoritative v3 plan for Tasks 0–16.
3. `docs/superpowers/plans/2026-07-28-docx-to-content-topic-grouping.md` — the plan for the grouped-strategy work (Tasks 1–9 of that plan), **complete and merged**.
4. `docs/implementation-baseline.md` — Task 0 reconnaissance findings (dated 2026-07-25; paths in it reference the pre-rename `sourcedocuments/`/`output/` directory names — historically accurate, not a live reference).
5. This file — the actual, verified current status. Trust this over any other handoff summary; verify against `git log` regardless.

The v1 spec/plan (`2026-07-25-docx-to-content-plugin-design.md` / `...-implementation-plan.md`, no `-ammendments` suffix) are superseded, kept only for historical comparison.

**Broader context:** this repo is Phase 1 of a larger initiative — see `docs/vision/README.md` and `docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md` for direction beyond Phase 1 (repository/plugin boundaries, SharePoint delivery, agents, publication, evaluation). Those documents propose future direction; they do not authorize work beyond the current approved Phase 1 plan.

## Where the work lives

Work happens directly on `main` in this repo — there is no separate worktree:

```text
plugin path:   plugins/docx-to-content/
run tests:     cd plugins/docx-to-content && python3 -m pytest tests/ -q
```

Two commits landed this session on top of the prior session's merge (`99faab2`):
- `b325ae6` — mixed-level logical-root detection for the grouped topic strategy (topic_grouping.py's `classify_headings`, `confirmed_topic_roots` persisted on the plan, `.gitignore` hygiene: `.superpowers/`/`.pytest_cache/` at every depth, two tracked SDD reports preserved to `docs/reports/`).
- `40bf069` — general media-disposition mechanism (`media_disposition.py`, `plans.apply_media_decision`, `ConversionPlan.media_decisions`, `validate_canonical._check_media_decisions`) plus two real-document convert fixes (glued-image heading-identity normalization; preamble-aware content-loss comparison).

Check `git log origin/main..main --oneline` before assuming remote state matches local — confirm with the user before pushing.

## Actual Current Status (verified, not reported)

**Tasks 0–16 and Task 17-topic-grouping are complete** (see prior session detail in git history; `main` up through `90a6033`/merge `99faab2` documents itself).

**Task 18 (real CEIS pilot cutover) is now complete**, run end-to-end through the plugin CLI against the real document (`intake/CEIS MANUAL - working version.docx`):

1. **`analyze` rerun** found a real crash: `topic_grouping.compute_topic_boundaries` hardcoded "every level-1 heading starts a topic," but the real document authors its first 14 top-level sections as Heading 2 and the remaining 11 as Heading 1 (verified against raw docx XML — standard Word styles, no pandoc bug, a genuine source-authoring inconsistency; every section's children are consistently Heading 3, never a genuine Heading 2 child beneath a Heading 1). Fixed via `classify_headings`'s dynamic root-level tracking (`root`/`promoted-root`/`ambiguous-root`/`internal-heading` classification), with the confirmed root set persisted on the plan (`confirmed_topic_roots`) so `convert` consumes it rather than recomputing the heuristic.
2. **Real `proposed_topics` reviewed**: exactly 25 topics (14 at source level 2, 11 promoted from level 1), `MIXED_LOGICAL_ROOT_LEVELS`/`PROMOTED_TOPIC_ROOT` warnings surfaced and reviewed, zero ambiguous roots (the real document's inconsistency is one-directional).
3. **`strategy: "grouped"` set** on the draft plan (a process bug during this session set it only after an initial confirm defaulted to `"chunked"` — caught before proceeding, plan rebuilt with `strategy=grouped` preserving the already-reviewed `confirmed_topic_roots`/`media_decisions`, then reconfirmed).
4. **Preamble/image findings re-verified**: title ("Civil Electronic Information System")/subtitle ("SEARCHABLE GUIDE")/version ("Version 1.9") → publication metadata; `Ctrl+F` instruction → omitted; Word TOC → raw dump detected, removed and regenerated from the publication map; `image1.png` → directly inspected (not inferred from dimensions), found to be a stale (2021-02-11) Internet Explorer browser-window screenshot of the CEIS-in-Motion portal landing page (OS taskbar, tab bar, address bar, active Find-toolbar search state all visible; the CEIS wordmark is embedded within it, not a standalone branding asset) — classified `obsolete-source-layout-artifact`, dispositioned `omit-as-reviewed-artifact` (not cropped — cropping would have manufactured an unapproved derived branding asset). This is the first real use of the new general media-disposition mechanism (see below).
5. **Explicit human plan confirmation obtained** before any `confirm`/`convert`/`render` ran (spec Section 7.1/7.2 gate honored).
6. **`confirm` → `convert` → `render` run against the real document**: `convert` validation status **PASS**, 159 structural anchors retained for lineage, 25 topic chunks, every anchor assigned to exactly one topic, `publication-map.json` present (25 entries, contiguous order 0–24). `render` validation status **PASS**, 25 pages, `index.md` in publication-map order, no raw TOC survived, `image1.png` confirmed absent from both canonical and rendered media.
7. Output lives at `runs/ceis-manual-v2/` (canonical-content + render/rendered-output). **Decision (user-confirmed): kept side by side with the old pre-plugin `runs/ceis-manual/`, not replaced** — the old directory is retained deliberately as historical evidence of the bare-pandoc problem the plugin was built to solve; `runs/ceis-manual-v2/` is the current, authoritative, plugin-produced output. `CLAUDE.md`'s "Conversion workflow" section has been updated to describe both and say so explicitly.

**Two real, generalizable defects were found and fixed while running the real document for the first time** (every prior test used synthetic fixtures that happened not to exercise these paths):
- Heading-identity divergence for a heading with an image glued directly onto its own line: `analyze_structure._normalize_heading_text` now also applies `pandoc_fixes.images.fix_glued_images` (previously only `strip_whole_heading_emphasis`, Task 17's fix for a different divergence of the same class), matching what convert's cleanup pipeline actually does before reconciliation.
- Content-loss/duplication false positive on any document with non-empty preamble content: `convert.py`'s `_run_conversion_pipeline` now compares staged chunk content against **preamble-stripped** cleaned text (`sliced_document.preamble` is never copied into any chunk by design — chunking.py — but the validation comparison was using the full cleaned document, which every synthetic test fixture's empty preamble had masked).

**General media-disposition mechanism added** (`scripts/media_disposition.py`, `plans.apply_media_decision`, `ConversionPlan.media_decisions`, `validate_canonical._check_media_decisions`), scoped deliberately to preamble media only (the one concrete integration point that exists today — `SlicedDocument.preamble`, never copied into canonical output). `analyze` proposes objective-signal-only records (`requires-human-review`/`requires-human-decision`) for every preamble media reference; a human confirms the real classification/disposition via `plans.apply_media_decision` before `confirm`; a still-pending record blocks conversion (`unclassified_media`), a reviewed omission does not. **Full body-content media classification** (screenshots inside procedures, decorative-vs-meaningful, derived-asset authorization workflow) was explicitly scoped OUT as future work — not attempted this session.

Full plugin suite as of this session's last commit (`40bf069`): **448 passed, 1 skipped**.

### What is NOT done yet — explicitly withheld pending further direction

- **General (non-preamble) media classification/disposition** — screenshots inside procedures, decorative-vs-meaningful classification, derived-asset authorization — is future work per the media-disposition mechanism's deliberately narrow Task 18 scope.
- **Nothing has been pushed to `origin`** — `main` is ahead of `origin/main` (check exact count via `git log origin/main..main --oneline`); confirm with the user before pushing.

## Evidence-report assembly, a real defect found AND fixed, real output regenerated (this session)

Assembled `runs/ceis-manual-v2/evidence-report.md` (spec Section 10's required Task 17/18
deliverable, never previously produced) by reconciling `manifest.json`/`validation.json`/
`renderer-validation.json`/`analysis-report.json`/chunk metadata against each other. This
surfaced a real defect, not just a documentation gap — and it has since been **fixed, verified,
and the real CEIS output regenerated**, not just described:

**The defect:** `image239.emf` (body content in `PROTECTION ORDERS`, not preamble) was absent
from both promoted canonical and rendered media, with a dead absolute-path reference baked into
both promoted outputs, and **both validators reported PASS with zero issues** despite it.

**Root cause:** the image's alt text contains a markdown-escaped `]` (from Word content quoting
"[Order Terminating a Protection Order]"). Four copies of the same naive regex —
`!\[[^\]]*\]\(...\)` — silently stop matching alt text at that literal `]` byte, so the reference
was never recognized as media at all, in: `convert.py`'s `_ABS_MEDIA_REF`, `package.py`'s
`_IMAGE_REF`, and **two** places in `validate_canonical.py` (`_IMAGE_REF_FOR_COMPARISON` and,
critically, `_IMAGE_REF` inside `_check_media_references` — the actual broken-link validator,
which never saw the reference to check it). `renderers/validate_rendered.py` carried the
identical bug on the render side.

**Fix:** all four sites now use `(?:[^\]\\]|\\.)*` for alt/link text — correctly treats `\]` as
an escaped literal rather than a terminator. A regression test was added first and confirmed
failing against the old code, then passing after the fix:
`tests/unit/test_package.py::test_alt_text_with_escaped_brackets_still_recognized_as_media_ref`.
Full suite: **449 passed, 1 skipped** (up from 448 — the new test executes, nothing else broke).

**Regeneration:** `convert` and `render` were rerun against the *same* confirmed plan (source and
plan unchanged — only pipeline code was fixed) via:
```bash
python -m scripts.cli convert --source "../../intake/CEIS MANUAL - working version.docx" --plan ../../temp/ceis-manual-analysis/conversion-plan.confirmed.json --output ../../runs/ceis-manual-v2
python -m scripts.cli render --canonical ../../runs/ceis-manual-v2/canonical-content --renderer multipage-markdown --output ../../runs/ceis-manual-v2/render
```
Both PASS. `runs/ceis-manual-v2/` now has **319/319** media files on both the canonical and
rendered sides (up from 318/318), `image239.png` present and correctly referenced as
`../media/image239.png` in both the canonical chunk and the rendered page — confirmed by direct
file inspection, not validator status alone. 159/159 heading anchors, 25/25 topic chunks
unchanged (the fix only affected media handling, not chunking/anchoring).

**Process gap, flagged for the record:** this rerun reused the already-approved confirmed plan
from Task 18 without explicitly telling the user that's what was happening — no new
chunking/strategy questions were asked because none were needed (nothing about topic boundaries
changed), but silently reusing an old approval rather than stating "reusing plan `<id>`, no
chunking changes, only the media fix is being validated" is a real gap against this project's
approval-gate conventions, caught by the user after the fact, not surfaced proactively. See the
governance note in `runs/ceis-manual-v2/evidence-report.md`'s header for the full note. Going
forward: any time a prior confirmed plan is reused rather than re-derived, say so explicitly
before running `convert`/`render` again, even when re-analysis is genuinely unnecessary.

**Not fixed, deliberately out of scope:** three other files contain structurally similar
`[^\]]*` patterns not implicated in this specific defect (`pandoc_validate.py`,
`analyze_structure.py`, `pandoc_fixes/images.py` — analysis-time detection and glued-image
cleanup, not media copy/validation). Whether any of these has a live bug of the same class is
unverified; a dedicated pass if a future document surfaces one, not opportunistic changes here.

**Remaining item:** the human spot-check checklist (spec Section 10's six categories) is still
unfilled. Two of six are genuinely N/A for this document (zero tables, zero footnotes — verified
from objective statistics, not assumed); the other four (title/front matter, one image-heavy
section, the one deep-hierarchy heading, beginning/middle/end) require an actual human look at
`runs/ceis-manual-v2/render/rendered-output/` — this is the one item this session could not close
itself, per the spec's own rule that human review can't be automated. Full detail in
`runs/ceis-manual-v2/evidence-report.md`.

## Orchestrate-conversion skill (added this session, after Task 18)

Deferred work from before Task 18 is now done: `plugins/docx-to-content/skills/orchestrate-conversion/SKILL.md`
is a pure-instruction (no new code) skill that sequences the same
`analyze`/`confirm`/`convert`/`render` CLI calls the other three skills
already document, with the mandatory human plan-review and media-decision
gates made explicit (pause-and-summarize after `analyze`, inline
image-review + `plans.apply_media_decision` for unclassified preamble
media, loop until explicit approval before `confirm`, stop on any FAIL or
undispositioned WARN at `convert`/`render`). It has not yet had a real
dry run against an actual document in this session — do that before
relying on it for a second real conversion. No new tests were added since
no new code was written; full suite still 448 passed, 1 skipped
(unchanged, verified after adding the skill).

## Next action on resume — this is the actual remaining work

1. **Human spot-check pass** (the one item blocking Phase 1 formal sign-off): open
   `runs/ceis-manual-v2/render/rendered-output/` and fill in the four applicable rows of the
   checklist in `runs/ceis-manual-v2/evidence-report.md` (title/front matter, one image-heavy
   section, the one deep-hierarchy heading, beginning/middle/end) — this requires a person
   looking at the actual rendered pages, not something automatable.
2. Do a real (or fixture) dry run of `orchestrate-conversion` end-to-end to validate the instructions actually hold up in practice, or move to whatever's next per `docs/vision/` (Phase 2 direction) — per further user direction, not assumed.
3. If/when broader (non-preamble) media classification becomes a real need on a future document, design it as its own scoped task — the vocabularies (`CLASSIFICATIONS`/`DISPOSITIONS` in `scripts/media_disposition.py`) already sketch the fuller taxonomy discussed this session, but nothing beyond preamble media is implemented.

## Efficiency notes for continuing this session or a fresh one

- Work directly on `main` — there is no worktree to re-enter. If isolation is wanted for further work, create a fresh worktree via `superpowers:using-git-worktrees` rather than assuming an old one still exists.
- This repo's `CLAUDE.md`: use the cheapest viable sub-agent model per dispatch, and don't spawn a sub-agent when the job doesn't need one. This entire Task 18 session (mixed-level root detection, media-disposition mechanism, both real-document convert fixes) was done directly via Read/Edit/Bash, not dispatched sub-agents — the work was well-understood, self-verifiable via the test suite, and the human (via chat) was the actual source of the classification decisions the pipeline itself can't infer (e.g. image1.png's disposition required looking at the actual image, not just objective signals).
- `origin` is `https://github.com/richfrem/manual-conversion-poc.git`. `main` is the default branch on GitHub.
- A `temp/bundles/manifest.json` exists for bundling key files via the `context-bundler` skill into a single `.md` for external review — keep it updated as files change if that hand-off is still wanted.
- The confirmed plan used for the real Task 18 run lives at `temp/ceis-manual-analysis/conversion-plan.confirmed.json` (and its draft counterpart) — `temp/` is gitignored (scratch), so this is not a durable artifact; re-run `analyze`/`confirm` fresh if resuming after `temp/` has been cleared.
