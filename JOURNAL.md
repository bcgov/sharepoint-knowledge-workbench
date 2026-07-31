# Conversion Process Journal

A chronological log of the CEIS Manual → Markdown conversion, kept for learning from the
process (what was tried, what broke, what fixed it). Newest entries at the bottom.

---

## 2026-07-25 — Session 1: Docx → Markdown conversion

### 1. Reviewed the `docx` skill and the goal document

- Read `.agents/skills/docx/SKILL.md` to understand the recommended approach for reading an
  existing `.docx`: `pandoc -t markdown file.docx` for read-only extraction (as opposed to the
  unzip/edit-XML/rezip path, which is only needed for *editing* an existing document).
- Read `plan.md` to understand the broader goal: this conversion is the pilot step for a
  content-centric knowledge management proposal — the CEIS Manual is the named pilot candidate.

### 2. First conversion pass

Command used:
```bash
mkdir -p output/ceis-manual/images
pandoc -t markdown --extract-media=output/ceis-manual/images --wrap=none \
  "sourcedocuments/CEIS MANUAL - working version.docx" -o output/ceis-manual/CEIS-Manual.md
```

- `--extract-media` was the key flag — it pulls embedded images out to disk and rewrites the
  markdown `![]()` links to point at them **in place**, which is what keeps images positioned
  where they occur in the original document instead of dumping them all at the end.
- Result: 4587-line markdown file, 320 images extracted, headings preserved (`## DATA CAPTURE
  STANDARDS`, `### Data Capture Requirements`, etc.), 330 image references detected.

### 3. Found a rendering problem: `.emf` images

- Checked file extensions in the extracted media folder:
  `273 png · 37 emf · 7 jpeg · 3 gif`
- `.emf` (Enhanced Metafile) is a legacy Windows vector image format. It does not render in
  browsers, GitHub, VS Code's markdown preview, or nearly any modern markdown viewer — so 37 of
  the 320 images would have appeared broken in the final output.
- **Lesson:** always check extracted-image file extensions after a pandoc conversion with
  `--extract-media` — old `.docx` files (this one had a "working version" edit history) often
  carry forward `.emf`/`.wmf` images from early Word versions or copy-pasted content.

### 4. Attempted to convert `.emf` → `.png` — no converter installed

- Tried `soffice --headless --convert-to png *.emf` directly: `soffice not found`.
- Tried the skill's `scripts/office/soffice.py` wrapper: also failed —
  `FileNotFoundError: soffice` (the skill assumes LibreOffice is already installed; it doesn't
  install it).
- Checked for alternatives: no `convert`/`magick` (ImageMagick), no `inkscape` — nothing on the
  machine could rasterize `.emf`.

### 5. Attempted `brew install --cask libreoffice` — user intervention

- First attempt to just run the brew install directly was **rejected by the user**, who pointed
  to `.agent/rules/dependency-management.md` and asked that dependency rules be followed before
  installing anything.
- Read that rule file: it governs **Python** dependencies only (`.in` → `pip-compile` → `.txt`
  lockfile workflow) — it doesn't have an equivalent process for macOS system/cask installs.
- **Lesson:** even when a rule doesn't literally apply, a system-level install (especially a
  ~1GB cask) is exactly the kind of action that should be surfaced and confirmed with the user
  first, not just run. Asked via a structured question instead of re-attempting the command.
- User chose to run the install themselves rather than have the agent run it.

### 6. Created `DEPENDENCIES.md`

- No existing dependency-tracking file for non-Python tools existed in the repo, so created one:
  a simple table of tool / purpose / macOS install command / status.
- Logged: `pandoc` (installed), `LibreOffice`/`soffice` (pending), `pdftoppm`/Poppler (not yet
  checked, needed later for visually verifying generated `.docx` output per the skill's verify
  step), and the `docx` skill itself (installed via `npx anthropics/skills skill add docx`,
  noted at the user's request as a dependency worth tracking).
- **Lesson:** the user wants a *running* dependency log kept going forward — update this table
  any time a new external tool enters the workflow, not just at the start.

### 7. Rewrote `CLAUDE.md` for this repo

- The user copied a `CLAUDE.md` in from a different repo (the `agent-plugins-skills` monorepo
  this project's skills were installed from). It was ~460 lines entirely about that *other*
  repo's plugin architecture, ADRs, and skill inventory — none of it described this repo.
- Rewrote it to keep the universal behavioral guidelines (think-before-coding, simplicity-first,
  surgical changes, goal-driven execution) and replace the project-specific section with what's
  actually true here: purpose (the content-centric POC from `plan.md`), real directory layout,
  the pandoc conversion workflow (including the `.emf` gotcha as a documented pattern for next
  time), and pointers to `DEPENDENCIES.md` and the `.agent/rules/` files that are genuinely
  installed in this repo.
- **Lesson:** an instruction file copied wholesale from another repo can be actively misleading
  — it needs to be re-derived from what's actually present (`ls .agent/rules`, `ls .agents/skills`,
  `plugin-sources.json`) rather than trusted at face value.

### 8. LibreOffice installed, `.emf` conversion completed

- User ran `brew install --cask libreoffice` themselves (~297MB download). Install succeeded.
- Confusion point: `libreoffice --version` and `libraoffice --version` both failed with
  `command not found` — the brew cask links the actual binary as **`soffice`**, not
  `libreoffice`. `soffice --version` confirmed `LibreOffice 26.2.5.2`.
- **Lesson:** the `docx` skill's own docs always refer to the binary as `soffice` — this is why;
  it's not a typo or version-specific naming, it's just what the Homebrew cask exposes.
- Ran the conversion:
  ```bash
  cd output/ceis-manual/images/media
  soffice --headless --convert-to png *.emf
  ```
  All 37 `.emf` files converted to `.png` successfully (one harmless stderr line:
  `Task policy set failed: 4 ((os/kern) invalid argument)` — a macOS sandboxing warning from
  soffice, not a conversion failure).
- Updated the markdown's image links from `.emf` to `.png`:
  ```bash
  sed -i '' 's/\.emf)/\.png)/g' output/ceis-manual/CEIS-Manual.md
  ```
- Verified with a small Python check that every `![]()` reference in the markdown resolves to a
  file that exists on disk: 258 references, 0 missing.
- Deleted the now-superseded `.emf` source files from the media folder (kept `.png`/`.jpeg`/`.gif`
  only) since the markdown no longer references them.
- Updated `DEPENDENCIES.md` to mark LibreOffice as Installed, with the `soffice`-vs-`libreoffice`
  naming note preserved for future readers.

### Current state at end of session

- `output/ceis-manual/CEIS-Manual.md` — complete markdown conversion, structure and image
  placement preserved, all image links resolve, no legacy formats remaining.
- `output/ceis-manual/images/media/` — 310 PNG + 7 JPEG + 3 GIF, 320 total, no `.emf` left.
- `DEPENDENCIES.md` — up to date.
- `CLAUDE.md` — tailored to this repo.
- Not yet done: visual spot-check of the converted markdown against the original `.docx` (e.g.
  rendering a few pages side-by-side) to confirm image placement and heading structure actually
  match what a human would expect, not just that links resolve.

---

## 2026-07-25 — Session 2: user pushback on output quality, decision to build our own conversion skill

### 1. User review found the "complete" conversion wasn't good enough

- First real user feedback on `CEIS-Manual.md`: "format looks nothing like the word doc source,
  table of contents sucks, images seem to lack... not even close." This directly contradicted
  Session 1's "current state" summary, which had verified link *resolution* but never verified
  output *quality* — a gap the self-check in Session 1 explicitly flagged as "not yet done."
- **Lesson:** "all image links resolve" and "heading structure exists" are necessary checks, not
  sufficient ones. They prove pandoc didn't crash; they don't prove the output is usable. A
  document can pass every automated link/count check and still be structurally wrong in ways only
  a human reading it would notice (Word's TOC field literally dumped as nested brackets, images
  glued into heading text).

### 2. Diagnosed four concrete, reproducible pandoc gaps

Inspected the raw markdown directly and confirmed the complaint was specific and fixable, not
vague dissatisfaction:
1. Word's auto-generated TOC field rendered by pandoc as a literal nested bracket-link list
   (`[Title [6](#anchor)](#anchor)` repeated ~150 times) instead of a usable table of contents.
2. Images glued directly onto surrounding text with no line break — including *inside heading
   lines themselves* (`### ![](img)**Central Divorce**`), corrupting the heading text.
3. Pandoc's `{width="..." height="..."}` attribute syntax left on every image tag — this renders
   as literal text in GitHub, VS Code preview, and most standard markdown viewers; it is pandoc-
   internal syntax, not portable markdown.
4. `{.underline}`/`{.mark}` span markers and backslash-escaped quotes (`\'`, `\"`) left as raw
   pandoc artifacts in running text.

### 3. Wrote and iterated an ad-hoc post-processing script

- First pass handled all four fixes with regexes; verified against the file and found it *also*
  had bugs: images with alt text (`![some alt text](img){width=...}`) weren't matched by an
  attr-stripping regex written only for empty-alt images, and underline spans wrapping a nested
  markdown link (`[[COURT LIST MODULE](#anchor).]{.underline}`) broke a naive `[^\]]+` regex.
- **Lesson:** restored from a backup and fixed the regexes properly rather than patching around
  the failures in place — confirms the value of keeping a `.bak` copy before any bulk rewrite of
  a large generated file.
- This iteration — get it wrong once, diagnose precisely, fix properly — is itself the evidence
  that these are *real, generalizable* pandoc gaps worth solving once in a real tool, not
  one-off oddities to patch by hand on every future document.

### 4. Decision: do not build on or reference the Anthropic `docx` skill

- User's instinct, stated directly: "what we care about is pandoc, not anthropic's skill" —
  confirmed correct on inspection. The installed `docx` skill's read path was nothing more than
  `pandoc -t markdown` with zero post-processing; there was no meaningful logic to build on.
- Checked its `LICENSE.txt`: prohibits reproducing the skill's materials outside Anthropic's
  Services and creating derivative works. The user also asked to check
  `anthropics/skills`' `THIRD_PARTY_NOTICES.md` — that file only covers third-party components
  *bundled inside* Anthropic's tooling (imageio, ffmpeg, etc. under BSD/GPL), it is not a license
  grant for the skill's own content, which stays under the restrictive proprietary terms.
- **Decision:** build a brand-new, independent tool on pandoc alone (open source, used via plain
  CLI invocation, no code copied from Anthropic's skill), with our own original post-processing
  logic. Zero code or licensing dependency on the Anthropic `docx` skill.
- **Removed** `.agents/skills/docx` from this repo entirely (with explicit user approval — see
  `self-evolution-policy.md`'s no-autonomous-deletion rule), along with its `skills-lock.json`
  entry and its `DEPENDENCIES.md` row. The skill's only capabilities beyond what pandoc already
  covers — in-place tracked-changes/redlining edits and pixel-precise native `.docx` authoring via
  `docx-js` — aren't needed for this project's actual goal (content ↔ template ↔ output round-trip).

### 5. Decision: build our own skill(s) — scope may end up as one or split later

- Ran `superpowers:brainstorming` to design this properly rather than writing another ad-hoc
  script. Re-read `plan.md` to confirm the design serves its actual vision: moving from
  Content+Formatting=Document to Content+Template+Renderer=Published Output, with the CEIS Manual
  as the named pilot.
- Confirmed scope: bidirectional (`.docx`→markdown *and* markdown→`.docx`, since pandoc's
  `--reference-doc` flag genuinely supports the write direction too, not just read) — this maps
  directly onto plan.md's Content/Template/Renderer split rather than solving only half of it.
- **Current call is one skill** (`pandoc-docx-convert`, two scripts + shared validation,
  mirroring the existing `convert-mermaid` skill's shape in the `dev-utils` plugin) — but this is
  explicitly provisional. If the docx→md cleanup pipeline and the md→docx templating logic turn
  out to need very different maintenance/testing lifecycles as real usage accumulates, splitting
  into two skills later is expected, not a failure of this design. Time will tell; don't force a
  premature split now, but don't be surprised by one either.
- Wrote the design as a formal spec (source-of-truth repo convention, not this repo):
  `agent-plugins-skills/docs/superpowers/specs/2026-07-25-pandoc-docx-convert-design.md`.

### 6. Established the cross-repo skill development protocol

- This repo (`manual-conversion-poc`) has no `plugins/` source tree — it only consumes installed
  skills. Confirmed with the user: `agent-plugins-skills` (sibling repo) is the actual source of
  truth for any new/updated skill, published to GitHub and the Claude Code marketplace.
- Protocol, now documented in this repo's `CLAUDE.md`: author/update in `agent-plugins-skills`
  (TDD first, hub-and-spoke via `symlink_manager.py`, no autonomous deletions) → feature branch →
  PR → **user reviews and merges to `main` themselves** → reinstall here via
  `.agents/skills/plugin-installer/scripts/plugin_add.py <path-to-agent-plugins-skills> --plugins <name> -y`,
  which can run against the local checkout directly (no need to wait on a GitHub-sourced install
  for fast iteration before/after merge).
- **Lesson:** checked the actual `plugin_add.py --help` output before writing the install command
  into `CLAUDE.md` rather than guessing at its argument shape from an old copied-in doc — the
  `source` argument is a *repo root*, not a plugin subpath; the plugin is selected via `--plugins`.

### Current state at end of session

- `.agents/skills/docx` removed; `skills-lock.json` and `DEPENDENCIES.md` updated to match.
- Design spec written, self-reviewed, and approved:
  `agent-plugins-skills/docs/superpowers/specs/2026-07-25-pandoc-docx-convert-design.md`.
- `CLAUDE.md` updated with the skill development protocol for this repo going forward.
- Not yet done: the ad-hoc post-processing script's fixes were never re-applied to
  `output/ceis-manual/CEIS-Manual.md` after being reverted to the backup for debugging — that file
  is currently back in its Session-1 (unfixed) state. The plan is to let the *real* skill produce
  the fixed version once built, rather than re-patch by hand a second time.
- Next: implementation plan for `pandoc-docx-convert`, via `writing-plans`.

---

## Recurring lessons (cross-referenced across entries above)

1. **Check extracted-image extensions after every pandoc `--extract-media` conversion** — legacy
   `.emf`/`.wmf` formats are common in older/edited `.docx` files and silently produce broken
   image links in modern viewers.
2. **System-level/cask installs are a confirm-first action**, distinct from the Python
   `pip-compile` dependency rule — surface the need and let the user decide, especially for large
   downloads.
3. **`soffice` is the actual LibreOffice CLI binary name** on macOS via Homebrew cask — not
   `libreoffice`.
4. **Copied-in instruction files (CLAUDE.md, etc.) need to be re-derived from the actual repo
   state**, not trusted as accurate just because they look complete.
5. **Verify link integrity programmatically** (not just visually) after any bulk rename/edit of
   image paths — a quick existence check across every `![]()` reference catches silent breakage
   immediately.

---

## 2026-07-28 — Task 18: real CEIS pilot cutover through the plugin

Ran the plugin's full `analyze` → `confirm` → `convert` → `render` pipeline against the real
document for the first time since the grouped-strategy engineering (Task 17-topic-grouping)
landed. Every prior test — even the "prove conversion generalizes beyond CEIS" pass — used
synthetic fixtures. Running the actual document surfaced three real defects that no fixture had
exercised, each a genuine gap rather than a CEIS-specific quirk:

1. **Mixed-level topic roots.** `topic_grouping.compute_topic_boundaries` hardcoded "every
   level-1 heading starts a topic." The real document's first 14 top-level sections are styled
   Heading 2, the remaining 11 Heading 1 — verified against raw docx XML (`styles.xml`/
   `document.xml`) to rule out a pandoc bug before touching any code: standard Word outline
   levels, no trickery, a genuine source-authoring inconsistency (every section's children are
   consistently Heading 3, never a genuine Heading 2 child beneath a Heading 1). Fixed with
   dynamic root-level tracking (`classify_headings`) instead of a fixed level check, with the
   confirmed root set persisted on the plan so `convert` consumes it rather than recomputing.
2. **Heading-identity divergence for a glued image.** A heading with an image glued directly onto
   its own line normalizes differently at analyze time (raw pandoc text, image still embedded)
   than at convert time (cleanup strips it via `fix_glued_images` before reconciliation) — the
   same class of bug Task 17 already fixed for whole-heading emphasis stripping, just for a
   different pandoc-fix that hadn't been extended to analysis-time normalization yet.
3. **Content-loss false positive on real preamble content.** The aggregate content-loss
   comparison checked staged chunk content against the *full* cleaned document, but
   `SlicedDocument.preamble` (title page, TOC, version line) is never copied into any chunk by
   design — every synthetic fixture's empty preamble had masked this. Fixed by comparing against
   preamble-stripped cleaned text instead.

Also built a general (if deliberately narrow-scoped) **media classification/disposition
mechanism**: `analyze` proposes objective-signal-only records for preamble media (never a final
decision — browser-chrome/branding/decorative judgment calls aren't something the pipeline can
infer from text alone), a human confirms the real disposition before `confirm`, and a still-
pending decision blocks conversion. First real use: `image1.png`, inspected directly (not
inferred from its dimensions), turned out to be a stale 2021 Internet-Explorer screenshot of an
internal portal page with the CEIS wordmark incidentally embedded in it — classified an
`obsolete-source-layout-artifact` and omitted, rather than cropping out the wordmark (which would
have manufactured an unapproved derived branding asset from a screenshot, not a supplied logo).

**Result:** `convert` and `render` both PASS against the real document — 159 structural anchors
retained for lineage, grouped into 25 topic chunks in the correct publication order, zero content
loss, `image1.png` confirmed absent from canonical/rendered output. Output lives at
`runs/ceis-manual-v2/`, kept deliberately side by side with the original pre-plugin
`runs/ceis-manual/` (not replacing it) — the old broken output is retained as visible evidence of
the actual problem this plugin was built to solve, not scrubbed away now that a working version
exists. `CLAUDE.md` now describes both directories and why both are kept.

**Lesson:** a plugin fully proven against synthetic fixtures is not the same claim as "works on
the real document" — fixtures are, by construction, built to avoid exactly the messy
inconsistencies (mixed heading styles, glued images, non-trivial preambles) that real legacy
documents actually contain. The generalization tests proved the *mechanism* worked across
document shapes the fixtures modeled; they couldn't prove it against shapes nobody had modeled
yet. Running the real pilot document early and often — not just once at the very end — would have
surfaced these three defects sooner.

---

## 2026-07-30 — Phase 3: Governed SharePoint Knowledge Pilot

### Key Learnings & Platform Boundaries

1. **Automated Live Publishing**: Developed pure-Python packaging & reconciliation tools (`sharepoint_package.py`, `sharepoint_reconcile.py`) and executed `run-phase3-tenant-pilot.ps1` against live SharePoint site `AG-CSB-intranet-dev`. Successfully published 25 topic pages and 319 media assets directly into `CEISPilotKnowledgePages/`. Reconciliation against `actual-state.csv` verified **100% MATCH**.
2. **SharePoint Agent Grounding Boundaries**: Documented critical M365 platform limits through staged capability probes:
   - SharePoint custom agents **cannot use List data as a grounding source**, and Site Pages library cannot be added as an agent source.
   - ASPX modern pages (`Add-PnPPage` + `Add-PnPPageTextPart`) render inline HTML formatting and embedded media correctly, whereas raw `.aspx` uploads hit platform `Access denied` boundaries.

---

## 2026-07-31 — Phase 4: Native SharePoint Skills Pilot (Planning & Tasks 0–1)

### Key Architectural Learnings & Process Refinements

1. **Separation of Deterministic Integrity vs Semantic Reasoning**:
   - Hardened Phase 4 design to separate deterministic repository tooling (recalculating hashes, canonical package validation, publication map completeness, structural anchors) from LLM semantic reasoning (`review-manual-topics` auditing content clarity, expected sections, cross-reference consistency, and human recommendations).
2. **Never Prewrite Test Evidence**:
   - Refactored implementation plan to eliminate prewritten `PASS` results before tests are run. Initial report templates start with `Status: NOT_EXECUTED`, `Actual result: NOT_RECORDED`, and `Reviewer disposition: PENDING`. Actual findings are recorded ONLY after human-executed tenant runs occur.
3. **No-Skill Control Harness**:
   - Introduced Condition A (Custom Agent without skill) vs Condition B (Custom Agent with `review-manual-topics` invoked) benchmarks to quantify whether the skill adds differentiated value beyond built-in agent synthesis (`SKILL_ADDS_CLEAR_VALUE`).
4. **Read-Only Inventory vs Authorized Cleanup**:
   - Split skill deconfliction into a read-only script (`inventory-skills.ps1`) and explicit human-authorized cleanup checkpoints. Executed Task 1 read-only scan against `AG-CSB-intranet-dev`: reconciled **25/25 topic pages** and **319/319 media files** (**100% Match**), confirming a clean baseline (0 pre-existing skill collisions).
5. **Exact Target Readback Verification**:
   - Standardized deployment target path as `AgentAssets/Skills/review-manual-topics/SKILL.md`. Script `deploy-and-verify-skill.ps1` computes local SHA-256, uploads file, downloads readback from exact server-relative URL, and asserts 100% byte-matching before recording completion.

---

## 2026-07-31 — Long-Term Plugin Domain Architecture Decision

### Confirmed Workbench Plugin Taxonomy

Agreed to transition from the Phase 1 combined `docx-to-content` plugin to 6 domain-scoped plugins during a planned post-Phase 4 refactoring phase (gated on a second source format or second renderer profile):

1. **`source-document-extraction`**: DOCX / PDF / HTML / SharePoint page extraction, normalized representation, media extraction, defect detection.
2. **`knowledge-analysis`**: Source-agnostic structural analysis, topic boundary recommendation, content-type classification, cross-reference & missing section analysis.
3. **`canonical-knowledge`**: Canonical package construction, stable identities, lineage, content hashes, publication map, validation.
4. **`knowledge-templates`**: Content templates (manuals, procedures, policies, FAQs) & presentation templates (Markdown, ASPX, PDF, agent digests).
5. **`knowledge-publication`**: Rendering pipeline separating **human-facing profiles** (multipage markdown, SharePoint ASPX, PDF) from **agent-facing profiles** (SharePoint agent-grounding digests, topic summaries, source maps).
6. **`sharepoint-publication`**: Destination deployment, modern page assembly, PnP publishing, reconciliation, drift detection, rollback, retirement.

*Execution Discipline*: Phase 4 execution will NOT be interrupted for this refactoring. Native Phase 4 SharePoint skills remain in `tools/phase-4-native-sharepoint-skills/`. The refactoring will be executed as a dedicated post-Phase 4 phase.


