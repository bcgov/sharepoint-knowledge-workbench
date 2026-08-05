# Review Point 1 — Corpus and Proposed Information Architecture

**Purpose of this document:** Orientation for reviewing `research-migration-manifest.json` (the authoritative source). This is a summary, not a duplicate source of truth — if this document and the manifest ever disagree, the manifest is correct.

**Status: PROPOSED, NOT APPROVED. No files moved, renamed, archived, or consolidated. No references updated. No directories created.**

---

## 1. Candidate-Count Reconciliation (68 → 29 → 56)

| Figure | Method | Status |
|---|---|---|
| 218 | Broad, unfiltered `find` across research/vision/architecture/reports/superpowers/tools | Superseded — too broad |
| 68 | **Never independently verified against the filesystem** | **INVALID** — cross-checking every path named as a "candidate" in prior sessions' Markdown tables found only ~29 actually exist. ~39 were *proposed destination paths* from an earlier premature taxonomy, miscounted as source files. |
| 29 | `docs/research/` (16) + `docs/architecture/docx-to-content-legacy-references/` (13), filesystem-verified | Superseded — correct but too narrow; excluded folders user subsequently confirmed in-scope |
| **56** | **29 (above) + `docs/architecture/` top-level (4) + `docs/diagrams/` (11) + `docs/vision/` (11) + `docs/` root (1)** | **CURRENT AND AUTHORITATIVE** |

**Reproduction command:**
```bash
find docs/research -maxdepth 1 -name '*.md' -type f
find docs/architecture -maxdepth 1 -type f
find docs/architecture/docx-to-content-legacy-references -type f
find docs/diagrams -type f
find docs/vision -maxdepth 1 -name '*.md' -type f
find docs -maxdepth 1 -name '*.md' -type f | grep -v README
# Total: 56
```

**Explicitly excluded:** `docs/superpowers/` (~68 files, phase specs/plans, separate lifecycle), `docs/reports/` (~37 files, phase evidence), `tools/phase-*/` (raw discovery artifacts), `plugins/*/skills|docs|evaluations` (operational plugin documentation). Three corpus entries (arch-015, arch-016, vis-011) have confirmed **scope tension** — physically in-scope but content-sourced from or functionally continuous with an excluded tree.

---

## 2. Read-Completeness — Honest Disclosure

**This is not "56/56 fully content-based."** Every entry has a `readCompleteness` field (linesShown/totalLines/percent/depth) computed from real line counts, not estimated.

| Depth | Count | Meaning |
|---|---|---|
| `full` | 5 | ≥95% of content read (arch-001, arch-007, arch-008 [3-line stubs], diag-000, vis-011) |
| `substantial-partial` | 5 | 50–94% read |
| `minimal-sample` | 46 | <50% read, many under 15% |

**Three highest-authority documents were fully read this session after the gap was discovered:**
- **vis-011** (master plan, 1110 lines) — reassessed `uncertain` → `current`. Already reflects Phase 7's actual status.
- **vis-002** (broader plan, 1147 lines) — **major correction**: reassessed from "current strategic direction" to "mostly-superseded-with-current-banner." Its body (repo rename, plugin architecture, roadmap) did not happen as written; only a 2026-08-02 banner at the top is current. Real defect found: **CLAUDE.md Section 0 points readers to a section of this document whose body text is exactly what the document's own banner marks superseded.**
- **vis-003** (government vision, 1384 lines) — classification **held up** under full read; genuinely durable capability vision, honestly self-labeled.

**Remaining 44 minimal-sample entries were NOT fully read in this session** — a deliberate, disclosed trade-off given turn constraints, not a silent gap. Every entry's `readCompleteness` is visible in the manifest for independent reviewer judgment. The lowest-read entries (<10%) are: `vis-002`, `vis-003` *(now full)*, `arch-016`, `vis-004`, `vis-005`, `vis-007`, `vis-009`, `res-012`, `arch-005`, `vis-008`.

---

## 3. Architecture Alternatives — Comparison and Recommendation

Five alternatives evaluated against real corpus signal (27 distinct `artifact_type` values across 56 files; 2 of 6 subject domains have only 2–3 entries; 3 confirmed scope-tension entries; 4 pre-decided dispositions already recorded in the repo itself). Full detail in manifest's `architecture_alternatives_status`.

| # | Alternative | Verdict |
|---|---|---|
| A | Separate trees, reorganized internally | Candidate |
| B | One unified corpus, artifact-type as metadata | Rejected — 27 types / 56 files means most subfolders would hold 1–2 files |
| C | Subject folders + artifact-type subfolders | Rejected — same reason as B |
| D | Durable knowledge vs. phase-evidence separation (the already-agreed scope) | **Recommended, implemented via A's structure** |
| E | Minimal movement, index-only | Candidate but doesn't resolve the original navigability complaint |

**Recommendation (PROPOSED, NOT APPROVED): 4 separate top-level trees** (`docs/research/`, `docs/architecture/`, `docs/diagrams/`, `docs/vision/`), not a unified corpus.

### Proposed Directory Tree (tentative)

```
docs/vision/                                    ← STRONGEST recommendation: adopt vis-001's
├── README.md (needs authority-table fix:          OWN already-written, never-executed plan
│   missing vis-009/vis-010)                       (blocked only on "the repository rename and
├── ai-assisted-structured-knowledge-workbench-     restructuring decision" — this effort may
│   broader-plan.md (vis-002, RETAIN, strengthen    now BE that decision)
│   corrective banner)
├── ai-assisted-sharepoint-knowledge-workbench-
│   government-vision.md (vis-003, RETAIN)
├── key-unanswered-questions.md (vis-005, RETAIN)
├── editing-workflow-options-for-external-
│   review.md (vis-009, RETAIN — still draft)
├── open-question-ongoing-editing-...md
│   (vis-010, RETAIN — RESOLVED, needs listing)
├── master-initiative-plan-workstreams-and-
│   phases.md (vis-011, RETAIN — highest
│   reference fan-out in corpus)
└── archive/
    ├── government-structured-knowledge-...-v2.md (vis-004 — repo's OWN README already
    │                                                names this exact disposition)
    ├── vision-original.md (vis-006)
    ├── plan-content-management-proposal.md (vis-007)
    └── plan-copilot-knowledge-access-proposal.md (vis-008)

docs/architecture/
├── phase-4-5-target-architecture.md (arch-014, RETAIN — stable historical record)
├── complete-plugin-skill-catalog-after-phase-9.{md,json} + validate_plugin_skill_catalog.py
│   (arch-015/016/017 — SCOPE TENSION: content-sourced from excluded docs/superpowers/,
│    hard executable coupling between all 3 files — recommend RETAIN or move-as-atomic-unit,
│    not resolved here)
└── docx-to-content-legacy-references/  →  proposed move to docs/research/structured-content-
                                             engineering/legacy/ (13 files, arch-001–013)

docs/diagrams/                          ← NOT homogeneous (01-05 authorized-historical vs.
                                            06-08 speculative-paired-with-vis-009 vs.
                                            09 speculative-paired-with-vis-010).
                                            TWO OPTIONS, NEITHER DECIDED:
                                            (1) keep together, rely on metadata to signal split
                                            (2) split: 01-05+high-level stay; 06-08 move near
                                                vis-009; 09 moves near vis-010

docs/research/                          ← Reorganized internally by subject domain
├── sharepoint-platforms-capabilities/
├── structured-content-engineering/ (includes legacy/ from docs/architecture/)
├── publication-delivery/
├── knowledge-discovery-retrieval/
├── architecture-design-patterns/
└── research-experimentation/
```

**Only 3 sample tentative path mappings are populated in the manifest** (vis-004, arch-002, res-012) to illustrate mechanics. Full 56-entry mapping is explicitly NOT populated — all `destination_status` remain `unassigned` or `tentative`.

---

## 4. Proposed Titles and Filenames (56/56)

Every entry has `proposedLogicalTitle`, `proposedFilename`, `filenameRationale`, `filenameStatus: "proposed"`. Rule applied: filenames describe enduring subject/artifact type, **except** where phase identity is essential (13 entries kept phase-numbered or dated names — field notes, phase-scoped diagrams, dated evidence — because they *are* historical records of one specific phase).

**Most consequential rename:** `res-012` — `research-summary-phase3-sharepoint-write-capability-discovery.md` → `field-note-sharepoint-write-capability-discovery.md`. Confirmed by content to be a raw evidence log, not a research summary. This file has **2 live plugin `SKILL.md` references** (see §5) — any rename requires those updated as runtime dependencies, not navigation.

### Collision and Confusability Findings

- **1 exact collision:** `README.md` × 5 (index files in 5 different folders) — **not a real issue**, directory-index convention.
- **1 high-risk confusable pair:** `vis-009`/`vis-010` — both originally `open-question-*` despite **opposite resolution status** (vis-009 still draft, vis-010 RESOLVED). Recommend vis-010's title lead with "RESOLVED"; a filename-prefix change is flagged for architecture approval, not executed.
- 3 lower-risk confusable groups documented in manifest (`arch-002`/`arch-009`, `vis-007`/`vis-008`, `diag-006`–`009`) — assessed as intentional/low-risk given distinct subject nouns.

---

## 5. Reference and Dependency Findings

**Runtime dependencies (live plugin `SKILL.md` files citing corpus documents by path — moving the target breaks the citation):**

| Entry | Cited from |
|---|---|
| res-012 | `plugins/sharepoint-content-publication/skills/publish-aspx-to-sharepoint/SKILL.md` |
| res-012 | `plugins/structured-content-rendering/skills/render-sharepoint-aspx/SKILL.md` |
| res-013 | `plugins/sharepoint-agents-and-skills/skills/configure-sharepoint-agent-knowledge/SKILL.md` |

**Repository-governance references (CLAUDE.md citations — highest severity class):**

| Entry | Reference |
|---|---|
| res-014 | CLAUDE.md line 288, "Critical Learning (2026-07-31)" section |
| vis-002 | CLAUDE.md Section 0 — **and confirmed to point at superseded body text within vis-002 itself (see §2)** |
| vis-011 | CLAUDE.md, extensively, as "the authoritative master plan" |

**Stale/broken references found (2, pattern not yet fully swept):**
- `.agent/rules/plugin-architecture-policy.md` cites `docs/diagrams/workflows/discovery.mmd` — this path does not exist (no `workflows/` subfolder in this repo's `docs/diagrams/`).
- `docs/vision/vision-original.md` (vis-006) cites `docs/superpowers/specs/diagrams/docx-to-content-workflow.png` — under the excluded tree, existence not verified.

**Reference inventory completeness:** Not systematic. Entries carry `inbound_references`/`outbound_references` gathered opportunistically during content reading, not from a full grep-and-line-number pass. This is disclosed, not claimed complete.

---

## 6. Content-Currency Remediation (See Full Report)

Full detail: `phase-7-content-currency-and-remediation-plan.md` (generated from the manifest).

| contentCurrency | Count | recommendedContentAction | Count |
|---|---|---|---|
| historical | 23 | none | 18 |
| current | 11 | add-status-note | 14 |
| partially-current | 10 | update | 10 |
| uncertain | 9 → 7 after this session's 2 reassessments | archive | 8 |
| superseded | 3 | cross-link | 6 |

**No source document was edited.** All content-update fields carry `contentUpdateApproval: "pending"`.

---

## 7. Unresolved Decisions Requiring User Input

1. **`docs/diagrams/` split or stay together** — resolves the diag-006/009 ↔ vis-009/010 coupling if split, but fragments the folder.
2. **`arch-015/016/017` scope-tension trio** — content-sourced from excluded `docs/superpowers/`, hard executable coupling. Retain in place, or move as an atomic unit with the validator's hardcoded paths updated?
3. **`vis-011` — retain in place regardless of `docs/vision/`'s reorganization?** Highest reference fan-out in the corpus (10+ citations including CLAUDE.md); strong recommendation to leave it, not resolved.
4. **`vis-009`/`vis-010` filename-prefix change** — should the misleading `open-question-*` prefix on the RESOLVED vis-010 be corrected?
5. **`vis-002`'s corrective banner** — strengthen in place, or is a rename/restructure also warranted given CLAUDE.md Section 0 points at its superseded body text?
6. **`arch-007`/`arch-008` unfilled placeholder stubs** — archive/delete, or complete them? (Empty content; not a migration question.)
7. **`arch-005` future-output-profiles.md** — only 4% read (310 lines); flagged as needing a full read if the Phase 6 ASPX-renderer cross-link (currency plan) is to be written accurately.
8. **`res-006`/`res-007` and `res-013`/`res-014` overlap pairs** — consolidate into a synthesis, or retain separately with cross-links? (Detailed disposition recommendations exist in prior commits; not re-litigated here.)
9. **`vis-004`'s already-repo-recorded disposition** ("extract unique content, then archive") — execute as part of file-move migration, or as separate content work?

---

## 8. Minimum Source Evidence for Ambiguous/High-Impact Classifications

Included in the bundle (see manifest for full list of `source_path`s):

- `docs/vision/master-initiative-plan-workstreams-and-phases.md` (vis-011) — full text, now fully read
- `docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md` (vis-002) — full text, corrected classification
- `docs/vision/README.md` (vis-001) — contains its own authority table and pre-existing reorganization plan
- `docs/vision/government-structured-knowledge-sharepoint-governance-vision-v2.md` (vis-004) — confirmed superseded, pre-decided disposition
- `docs/architecture/docx-to-content-legacy-references/README.md` (arch-001) — explains why 10 of 12 sibling files are NOT superseded despite folder framing
- `docs/research/research-summary-phase3-sharepoint-write-capability-discovery.md` (res-012) — highest reference fan-out research file, misnamed genre
- `CLAUDE.md` — Section 0 and the "Phase 4+ SharePoint Copilot Agent Configuration" section, both directly implicated in findings above

---

## 9. What Has NOT Been Done

- No files moved, renamed, archived, or consolidated
- No references updated
- No source document content edited
- No directories created
- No Python migration script written (Review Point 2, after this review)
- No branch push, no PR

