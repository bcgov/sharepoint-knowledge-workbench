# Phase 3 — Governed SharePoint Knowledge Pilot Implementation-Plan Scaffold

> **Status: SCAFFOLD, NOT AN IMPLEMENTATION-READY PLAN.** This document deliberately deviates from
> `superpowers:writing-plans`' "no placeholders" rule: every task below that depends on a fact Phase 3.0
> has not yet produced is marked `DEFERRED UNTIL PHASE 3.0 EVIDENCE: <specific missing fact>` rather than
> inventing a value. Do not execute any task in this document. Once Phase 3.0's `tenant-capability-report.md`
> exists and the unresolved-decision register (`phase-3-unresolved-decisions.md`) is settled, this scaffold
> is the input to writing the real, placeholder-free implementation plan — not a substitute for that step.
>
> **REQUIRED SUB-SKILL when the real plan is written:** `superpowers:subagent-driven-development`
> (recommended) or `superpowers:executing-plans`.

**Goal:** Publish the complete 25-topic CEIS rendered publication into one governed, non-production
SharePoint pilot library via package-only deployment, proving metadata schema, source-of-truth,
reconciliation, republish, rollback, rename/retirement, and governance behavior — with zero autonomous
writes.

**Architecture:** A local package-builder reads the confirmed canonical package + publication map and
produces an upload-ready package (content + metadata sidecar + validation result) entirely offline; a human
publisher performs every SharePoint-side action manually; a local reconciliation tool compares expected
(publication-map-derived) state against actual SharePoint state using data the publisher exports or a
confirmed-available read mechanism supplies.

**Tech Stack:** Python (matching `plugins/docx-to-content`'s existing stack and conventions), the existing
`docx-to-content` plugin's contracts/hashing modules (no reimplementation), pytest for repository-side unit
tests. SharePoint-side tooling (PnP PowerShell, Graph, Power Automate) is **not** part of Phase 3 build
scope per the spec's Non-goals — any such tool named here is a `DEFERRED`/human-manual step, not a task this
plan implements.

## Global Constraints

- Package-only deployment only — no task in this scaffold may implement an autonomous SharePoint write.
- No new plugin (`sharepoint-knowledge` or similar) is created in Phase 3 — new code lives inside
  `plugins/docx-to-content/` as an additional CLI-backed capability, following that plugin's existing
  hub-and-spoke/TDD conventions, unless a separate spec/plan proposes otherwise.
- Every new script/module follows this repo's existing symlink/skill conventions
  (`.agent/rules/symlink-cross-platform.md`) if it is exposed as a skill.
- TDD throughout: failing test first, per `.agent/rules/test-driven-development.md`.
- No task may be executed until: (a) Phase 2 exit gate — already met; (b) Phase 3.0's accepted
  `tenant-capability-report.md` exists; (c) this scaffold's `DEFERRED` markers for that task are resolved.

---

## Subphase 3.1 — Metadata schema and source-of-truth lifecycle

### Task 3.1.1: Schema-mapping document

**Files:**
- Create: `docs/reports/phase-3-sharepoint-pilot/schema-mapping.md`

**Interfaces:**
- Consumes: `phase-3-governed-sharepoint-knowledge-pilot-spec.md` Section 7 (field-authority matrix).
- Produces: the canonical/publication contract → SharePoint column mapping later tasks (3.1.2, 3.2.1) read.

- [ ] **Step 1:** Copy Section 7's field-authority matrix into this document verbatim as the starting
  mapping.
- [ ] **Step 2:** For every field, add a column citing the exact source field/attribute in
  `plugins/docx-to-content/scripts/contracts.py` (e.g. `ManifestChunk.chunk_id`,
  `ChunkMetadata.content_sha256`) so the mapping is traceable to real code, not narrative description.
- [ ] **Step 3:** Commit.

```text
DEFERRED UNTIL PHASE 3.0 EVIDENCE: cannot reconcile proposed column types (Choice/Person/Date/Lookup)
against actual tenant constraints until Stage 3.0.2.5's field-type inventory exists — Task 3.1.2 below.
```

### Task 3.1.2: Reconcile schema against observed tenant field constraints

**Files:**
- Modify: `docs/reports/phase-3-sharepoint-pilot/schema-mapping.md`

- [ ] **Step 1:** `DEFERRED UNTIL PHASE 3.0 EVIDENCE: Stage 3.0.2.5's field-type inventory does not exist
  yet — this task cannot be started, only scaffolded.` Once it exists, for every field marked
  `TENANT_DEPENDENT` or with a "3.0.2.5" dependency in Section 7, replace the proposed type with the
  actually-confirmed type or explicitly note a type mismatch requiring a design change.
- [ ] **Step 2:** Commit the reconciled mapping, citing the specific `tenant-capability-report.md` section
  used for each field.

### Task 3.1.3–3.1.4: Source-of-truth lifecycle document

**Files:**
- Create: `docs/reports/phase-3-sharepoint-pilot/source-of-truth-lifecycle.md`

**Interfaces:**
- Consumes: spec Section 8 (already answers all six Stage 3.1.4 questions plus the restated Stage 3.1.3
  rule).
- Produces: the lifecycle rule later tasks (3.3.x republish/rollback) implement against.

- [ ] **Step 1:** Copy spec Section 8 verbatim into this standalone document (Stage 3.1.4 names this as its
  own deliverable file, separate from the main spec).
- [ ] **Step 2:** Have the user/pilot-library-owner explicitly sign off on the "block until reviewed"
  republish policy (currently `RECOMMENDED`, see unresolved-decision register item 2) before this document
  is treated as final — record the sign-off inline (name, date).
- [ ] **Step 3:** Commit.

---

## Subphase 3.2 — Package-only deployment

### Task 3.2.1: Upload-ready package builder

**Files:**
- Create: `plugins/docx-to-content/scripts/sharepoint_package.py`
- Test: `plugins/docx-to-content/tests/unit/test_sharepoint_package.py`

**Interfaces:**
- Consumes: `contracts.Manifest`, `contracts.PublicationMap`-equivalent load functions already present in
  `plugins/docx-to-content/scripts/package.py` / `canonical-contract.md`'s documented loaders; the rendered
  output at `runs/ceis-manual-v2/render/`.
- Produces: `build_upload_package(canonical_dir: Path, render_dir: Path, output_dir: Path) ->
  UploadPackage` — a new dataclass (fields: `topics: list[UploadPackageTopic]`,
  `metadata_sidecar_path: Path`, `validation_status: str`), where `UploadPackageTopic` carries
  `topic_id`, `title`, `order`, `content_path` (rendered Markdown file), `media_paths: list[Path]`, and the
  Section 7 REQUIRED_FOR_PHASE_3 fields (`package_identity`, `source_content_sha256`, `publication_id`,
  `validation_state`, `publication_order`). Later tasks (3.2.2, 3.2.3) consume `UploadPackage`.

- [ ] **Step 1: Write the failing test** asserting `build_upload_package` produces exactly 25
  `UploadPackageTopic` entries for the real `runs/ceis-manual-v2` package, each with a non-null
  `package_identity`/`source_content_sha256`/`publication_id`/`validation_state`/`publication_order`, and
  that `validation_status == "PASS"` (reusing the real fixture, not a synthetic one, per this repo's Task
  18 lesson that synthetic fixtures previously masked real defects).
- [ ] **Step 2:** Run it, confirm it fails with `ModuleNotFoundError` or `AttributeError` for the
  not-yet-written function.
- [ ] **Step 3:** Implement `build_upload_package` using existing `package.py`/`contracts.py` loaders — no
  new hashing/identity logic, only composition of already-hardened Phase 2 contract data.
- [ ] **Step 4:** Run the test, confirm PASS.
- [ ] **Step 5:** Commit.

```text
DEFERRED UNTIL PHASE 3.0 EVIDENCE: metadata sidecar file format (CSV vs JSON) is not fixed — Stage
3.0.2.5's confirmed column types determine which format is easiest to bulk-populate. Task 3.2.1's
`metadata_sidecar_path` writer is scaffolded as JSON for now (matches this repo's existing contract
conventions); confirm or change once Phase 3.0 evidence exists, before this task is executed for real.
```

### Task 3.2.2: Dry-run validation

**Files:**
- Create: `plugins/docx-to-content/scripts/sharepoint_dry_run.py`
- Test: `plugins/docx-to-content/tests/unit/test_sharepoint_dry_run.py`

**Interfaces:**
- Consumes: `UploadPackage` from Task 3.2.1.
- Produces: `validate_upload_package(pkg: UploadPackage) -> DryRunReport` (fields: `status:
  Literal["PASS","FAIL"]`, `issues: list[str]`), consumed by Task 3.2.3's upload-log task as a
  precondition check.

- [ ] **Step 1: Write the failing test** for: all-PASS package → `DryRunReport(status="PASS", issues=[])`;
  a package with one topic's `validation_state != "PASS"` → `status="FAIL"` with an issue naming that topic.
- [ ] **Step 2:** Run, confirm fail.
- [ ] **Step 3:** Implement the minimal checks listed in spec Section 10 (PASS-only, required-field
  non-null, no duplicate `topic_id`/`publication_id`, media references resolve) — reuse
  `validate_canonical.py`'s media-reference regex fix (the escaped-bracket fix from this repo's Task 18
  work) rather than reimplementing it.
- [ ] **Step 4:** Run, confirm pass.
- [ ] **Step 5:** Commit.

```text
DEFERRED UNTIL PHASE 3.0 EVIDENCE: the reconciled schema type-check sub-item (spec Section 10, third
bullet) cannot run meaningfully until Task 3.1.2's reconciled mapping exists. Scaffold this check as a
no-op that always passes until then, clearly logged as skipped, not silently omitted.
```

### Task 3.2.3: Manual upload log template + execution

**Files:**
- Create: `docs/reports/phase-3-sharepoint-pilot/upload-log-template.md`

- [ ] **Step 1:** Write a template capturing every item in spec Section 11 (date/time, publisher identity,
  pilot library target, topics uploaded in order, every manual step performed, deviations, screenshot/export
  confirmation).
- [ ] **Step 2:** Commit the template.
- [ ] **Step 3 (human-performed, not automatable):**
  `DEFERRED UNTIL PHASE 3.0 EVIDENCE: pilot site/library does not exist yet (unresolved-decision register
  item 1) — the actual upload cannot be performed. This step remains blocked until that decision is made
  and Phase 3.0/Phase 3 entry gates are met.`

---

## Subphase 3.3 — Publication reconciliation and recovery

### Task 3.3.1: Reconciliation comparator

**Files:**
- Create: `plugins/docx-to-content/scripts/sharepoint_reconcile.py`
- Test: `plugins/docx-to-content/tests/unit/test_sharepoint_reconcile.py`

**Interfaces:**
- Consumes: `UploadPackage` (Task 3.2.1) as "expected state"; an `ActualLibraryState` input (fields:
  `items: list[ActualLibraryItem]`, each with `topic_id`, `package_identity`, `source_content_sha256`,
  `publication_id`, `publication_order`, `validation_state`) representing whatever the publisher exports
  from SharePoint.
- Produces: `reconcile(expected: UploadPackage, actual: ActualLibraryState) -> ReconciliationReport` (fields:
  `missing: list[str]`, `duplicate: list[str]`, `stale: list[str]`, `unexpected: list[str]`,
  `mismatched_package_identity: list[str]`, `mismatched_publication_identity: list[str]`,
  `mismatched_validation_lineage: list[str]`, `renamed_or_retired: list[str]`), matching spec Section 12's
  four-concept identity split (stable matching key / expected-content identity / publication membership /
  publication event).

- [ ] **Step 1: Write the failing test** for at least one case per issue category in spec Section 12 (9
  synthetic fixture cases: missing, duplicate, stale, unexpected, mismatched package identity, mismatched
  publication identity, mismatched validation lineage, renamed/retired, and a clean no-issues case).
- [ ] **Step 2:** Run, confirm fail.
- [ ] **Step 3:** Implement `reconcile` — pure Python, no tenant I/O, since `ActualLibraryState` is an
  already-exported/read-back data structure (the export/read-back mechanism itself is deferred, see below).
- [ ] **Step 4:** Run, confirm pass.
- [ ] **Step 5:** Commit.

```text
DEFERRED UNTIL PHASE 3.0 EVIDENCE: how `ActualLibraryState` is actually populated (Graph/PnP read access
vs. manual UI export) depends on unresolved-decision register item 10. The comparator itself (pure
function over two already-structured inputs) can be implemented and unit-tested now; the adapter that
produces `ActualLibraryState` from a real tenant cannot be written until that decision is resolved.
```

### Task 3.3.2: Lineage trace record

**Files:**
- Create: `docs/reports/phase-3-sharepoint-pilot/lineage-trace-template.md`

- [ ] **Step 1:** Template: given one published item, show the full chain — SharePoint item →
  `topic_id`/`publication_id` → `package_identity` → confirmed canonical package (`plan_id`) → source DOCX
  fingerprint (`ManifestSourceFingerprint.sha256`).
- [ ] **Step 2:** Commit template.
- [ ] **Step 3 (human-performed):**
  `DEFERRED UNTIL PHASE 3.0 EVIDENCE + Subphase 3.2 upload completion — cannot trace a real published item
  until one exists.`

### Task 3.3.3–3.3.5: Republish, rollback, rename/retirement exercises

**Files:**
- Create: `docs/reports/phase-3-sharepoint-pilot/republish-exercise.md`
- Create: `docs/reports/phase-3-sharepoint-pilot/rollback-exercise.md`
- Create: `docs/reports/phase-3-sharepoint-pilot/rename-retirement-exercise.md`

**Interfaces:**
- Consumes: `ReconciliationReport` (Task 3.3.1), source-of-truth-lifecycle.md's block-until-reviewed policy
  (Task 3.1.4).

- [ ] **Step 1 (per exercise):** Write the before-state expected inventory (from the publication map).
- [ ] **Step 2 (per exercise, human-performed):**
  `DEFERRED UNTIL PHASE 3.0 EVIDENCE + Subphase 3.2 upload completion — every exercise requires a real
  published pilot item to republish/roll back/rename against. None of these steps can run until Task
  3.2.3's upload has happened at least once.`
- [ ] **Step 3 (per exercise):** Run `reconcile` (Task 3.3.1) against the post-exercise actual state; record
  the before/after `ReconciliationReport` output as the exercise's evidence.
- [ ] **Step 4:** Commit each exercise's evidence file.

### Task 3.3.6: Dry-run reconciliation gate

**Files:**
- Modify: `plugins/docx-to-content/scripts/sharepoint_reconcile.py` (add a `--dry-run` CLI entry point if
  none exists from Task 3.3.1)
- Test: extend `test_sharepoint_reconcile.py`

- [ ] **Step 1: Write the failing test** asserting the CLI entry point runs `reconcile` and prints a
  human-readable report without performing any write.
- [ ] **Step 2:** Run, confirm fail (entry point doesn't exist).
- [ ] **Step 3:** Implement the CLI wrapper.
- [ ] **Step 4:** Run, confirm pass.
- [ ] **Step 5 (human-performed):** run it once against the real pilot library with zero autonomous writes,
  per Stage 3.3.6 — `DEFERRED UNTIL PHASE 3.0 EVIDENCE + pilot library exists`.
- [ ] **Step 6:** Commit code; commit the run's evidence output separately once performed.

---

## Subphase 3.4 — Governance controls

### Task 3.4.1: Review-workflow walkthrough

**Files:**
- Create: `docs/reports/phase-3-sharepoint-pilot/review-workflow-walkthrough.md`

- [ ] **Step 1:** Template recording one real item's Draft → Reviewed → Published transition, with
  timestamps and the human who performed each transition.
- [ ] **Step 2 (human-performed):** `DEFERRED UNTIL PHASE 3.0 EVIDENCE + pilot library exists +
  unresolved-decision register item 8 (reviewer/publisher roles named)`.
- [ ] **Step 3:** Commit.

### Task 3.4.2: Oversharing/permission test

**Files:**
- Create: `docs/reports/phase-3-sharepoint-pilot/oversharing-test-report.md`

- [ ] **Step 1:** Template recording the two identities used, what each could/couldn't see, and whether the
  result matches the intended permission boundary.
- [ ] **Step 2 (human-performed):** `DEFERRED UNTIL PHASE 3.0 EVIDENCE (unresolved-decision register item 9
  — which two identities) + pilot library exists`.
- [ ] **Step 3:** Commit.

### Task 3.4.3: Authorized-write design-only document

**Files:**
- Create: `docs/superpowers/specs/phase-3-authorized-write-design.md`

- [ ] **Step 1:** Design-only document naming an accountable owner and identity for a future authorized-
  write path — **no implementation**, per Stage 3.4.3 and the spec's Non-goals.
- [ ] **Step 2:** `DEFERRED UNTIL PHASE 3.0 EVIDENCE: owner/identity not yet named` — this task produces a
  document with an explicit "not yet named" placeholder for owner/identity, which is itself the correct
  Stage 3.4.3 output at this point (design-only, gated), not a plan defect.
- [ ] **Step 3:** Commit.

---

## Subphase 3.5 — Pilot evaluation

### Task 3.5.1: Readiness-check report

**Files:**
- Create: `docs/reports/phase-3-sharepoint-pilot/readiness-check-report.md`

- [ ] **Step 1:** Check every uploaded pilot item against the reconciled Stage 3.1.1/3.1.2 schema for
  completeness.
- [ ] **Step 2 (human-performed):** `DEFERRED UNTIL PHASE 3.0 EVIDENCE + full pilot upload completion`.
- [ ] **Step 3:** Commit.

### Task 3.5.2: Retrospective

**Files:**
- Create: `docs/reports/phase-3-sharepoint-pilot/phase-3-retrospective.md`

- [ ] **Step 1:** Cite every evidence artifact from Tasks 3.1.1–3.5.1 by file path, per spec Section 16 —
  not summarized from memory.
- [ ] **Step 2:** State explicitly which Phase 4/5 requirements the pilot surfaced as real (not assumed).
- [ ] **Step 3:** Commit — this document becomes the entry-gate evidence for Phase 4/5.

---

## Sequence to make this scaffold implementation-ready

1. Phase 3.0 executes and produces an accepted `tenant-capability-report.md`.
2. `phase-3-unresolved-decisions.md` items 1, 6, 8, 9, 10 (the `BLOCKS_EXECUTION`/`BLOCKS_PLAN` items tied to
   tenant facts) are resolved using that report.
3. `phase-3-tenant-evidence-consumption-matrix.md` is checked row-by-row against the report; any row still
   unanswered is escalated per its "Blocking if absent?" column before proceeding.
4. This scaffold's `DEFERRED UNTIL PHASE 3.0 EVIDENCE` markers are replaced with real values or concrete
   task steps.
5. `superpowers:writing-plans` is re-invoked to produce the actual placeholder-free implementation plan from
   this scaffold, in a dedicated Phase 3 branch/worktree per the master plan's Per-Phase Git & Session
   Workflow.
6. Only then does `superpowers:subagent-driven-development` or `superpowers:executing-plans` begin real
   execution.
