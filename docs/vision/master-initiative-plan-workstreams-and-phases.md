# Master Initiative Implementation Plan — AI-Assisted Structured Knowledge Workbench

**Status:** Whole-spectrum plan. Every phase (1–8, plus 3.0 and 5.5) is decomposed into subphases, and every
subphase into implementation stages with entry/exit criteria and evidence requirements. This is the
superordinate planning artifact; the Phase 2 contract-hardening plan
(`docs/superpowers/plans/2026-07-28-phase2-canonical-publication-contract-hardening.md`) is the detailed
execution plan for one phase (2) inside it.

**Revision history:** Supersedes an earlier, workstream-only version of this document. This revision
incorporates external adversarial review (GPT 5.6 + Opus, `temp/plan-reviews/full-plan-review/round3/`)
that found several full-vision capabilities named in traceability but never assigned an actual phase/stage
home, an unjustified hard dependency (Phase 5 on Phase 4), vague stage completion criteria, a missing
SharePoint publication-reconciliation/rollback concern, a missing source-of-truth lifecycle decision, an
under-specified Phase 6 shared-capability derivation, and two labeling issues (Workstream G mislabeled
REJECTED instead of RESEARCH; Phase 1's status inconsistent with Phase 2 Task 0's precondition wording).
All are fixed below.

**Detail-level discipline (unchanged):** Near phases (1, 2, 3.0, 3) carry concrete, implementation-ready
stages. Far phases (4–8) carry real subphase/stage *structure* with honest evidence gates — not fabricated
implementation detail, because their real requirements depend on tenant facts and pilot outcomes that do
not exist yet. Structure is planned; speculative internals are not invented.

**Disposition legend:** NOW = authorized to build · NEXT = next to plan in detail · LATER = deferred
pending prerequisite · RESEARCH = spike/discovery only, gated on a missing fact or use case, not a decision
against scope · REJECTED-for-now = revisit on trigger (reserved for items with a stated architectural
objection, not merely missing evidence — see the Workstream G fix below for why this legend distinction
matters).

---

## How To Read This Plan

Each phase below follows the same shape:

- **Goal** — the one outcome the phase exists to produce.
- **Entry gate** — what must be true before the phase may start.
- **Subphases** — the phase broken into independently reviewable units.
- **Implementation stages** — inside each subphase, the ordered work with its own test/evidence cycle.
  Every stage below states **deliverable / verification / evidence**, even for far phases — this is
  structural planning, not speculative technical design (see Stage 5.1.1 for the pattern this follows).
- **Exit gate** — the evidence (not narrative) that closes the phase.

A stage is the smallest unit that carries its own test cycle and is worth a fresh reviewer's gate.

---

## Per-Phase Git & Session Workflow (applies to every phase below)

Every phase in this plan follows the same integration and session-hygiene pattern, so context doesn't
bloat across a multi-month, multi-phase initiative and so each phase leaves a clean, resumable state behind
it. This section is referenced, not repeated, at each phase's exit gate below.

1. **Branch/worktree per phase.** Before a phase's first task starts, create an isolated workspace —
   a git worktree (`superpowers:using-git-worktrees`) or, at minimum, a dedicated feature branch named
   after the phase (e.g. `phase-2-contract-hardening`, `phase-3-sharepoint-pilot`). Never work a new
   phase directly on `main`. This applies even to Phase 2, which is already scoped to run inside one
   plugin — isolation still protects `main` from an in-progress phase's intermediate, possibly-broken
   states.
2. **Commit per task, not per phase.** Each task (or stage, for far phases once they reach implementation
   detail) gets its own commit(s) on the phase branch, per this plan's and the Phase 2 plan's existing
   task-level commit instructions — nothing new here, just confirming it happens on the phase branch, not
   `main`.
3. **Phase exit gate = merge gate.** A phase's exit gate (defined per-phase above) is also the merge gate:
   do not merge the phase branch into `main` until its exit gate's evidence exists and has been reviewed.
   Merge via a reviewed PR when working with GitHub remotes, or a direct fast-forward/no-ff merge with the
   user's explicit go-ahead when working locally — either way, this is a "confirm before merging" action
   per this repo's standing git-safety conventions, not an autonomous one.
4. **Update `start-here.md` as the last step before ending a phase's session, and immediately after
   merging.** `start-here.md` is this repo's authoritative, kept-current resume document (see `CLAUDE.md`).
   At the close of every phase: record what was actually done (not narrative — evidence, exact test/suite
   counts, exit-gate proof), what's still open, and the exact next action for whoever resumes. This is what
   makes starting a clean session for the next phase safe.
5. **Start the next phase in a fresh session.** Once a phase is merged to `main` and `start-here.md` is
   updated, the next phase should start in a **new session**, not a continuation of the current one — this
   repo's own multi-round review process across this session is itself a case study in context bloat
   (dozens of tool calls, multiple large bundles, several full-file reads) that a fresh session for the
   next phase avoids inheriting. The fresh session reads `start-here.md` first, per `CLAUDE.md`'s own
   resume convention, and does not need this session's full history to proceed correctly.
6. **Worktree cleanup after merge.** Once a phase branch is merged and `start-here.md` reflects it, remove
   the worktree/branch (`git worktree remove`, delete the merged branch) rather than leaving stale
   worktrees to accumulate — this repo has hit that exact problem before (`.claude/worktrees/` had a stale
   entry from a prior phase's worktree still present as of this session's own reconnaissance).

---

## Phase 1 — Structured Knowledge Conversion & Canonical Content POC

**Disposition:** Engineering-complete; formal closure pending. **Not "DONE"** — stated this way
deliberately, consistently with Phase 2's Task 0 precondition below, so starting Phase 2 before this
phase's Subphase 1.3 is actually complete doesn't come as a surprise halt at Task 0. **Detail level:**
Implemented.

**Goal:** Prove the content/format separation exists and is genuinely extensible, using the CEIS Manual as
the evidence vehicle.

**Entry gate:** (historical) approved Phase 1 design spec.

### Subphase 1.1 — Analyze / Convert / Render pipeline
- Stage 1.1.1 — `analyze-document`: structural scan → conversion plan. **DONE**
- Stage 1.1.2 — `convert-document`: cleanup pipeline + chunk + metadata sidecars. **DONE**
- Stage 1.1.3 — `render-content`: `multipage_markdown` renderer proving the contract is pluggable. **DONE**

### Subphase 1.2 — Validation & defect remediation
- Stage 1.2.1 — canonical + rendered validators. **DONE**
- Stage 1.2.2 — image239 regex defect: root-caused, regression-tested, media count 319/319, suite 449/1. **DONE**

### Subphase 1.3 — Formal closure (the only open work)
- Stage 1.3.1 — human spot-check: title/front-matter, image-heavy section, deep-hierarchy heading,
  begin/middle/end. **Deliverable:** four filled rows in `evidence-report.md`. **Verification:** a human
  actually opened `runs/ceis-manual-v2/render/rendered-output/` and recorded what they saw. **Evidence:**
  the filled checklist rows themselves. **PENDING HUMAN.**
- Stage 1.3.2 — disposition the "plugin/marketplace metadata not verified" acceptance row. **PENDING.**
- Stage 1.3.3 — finalize `evidence-report.md`, mark Final Acceptance Checklist complete. **PENDING.**

**Exit gate:** All four spot-check rows recorded; metadata row dispositioned; evidence report finalized.
This gate is identical to Phase 2's Task 0 precondition — Phase 1 must be *actually* closed, not
"engineering-complete," before Phase 2's golden-master baseline is captured.

---

## Phase 2 — Canonical / Publication Contract Hardening

**Disposition:** NOW — spec approved; 18-task execution plan (including Task 0) reviewed across four
rounds of external technical review and technically ready. **External review does not itself authorize
implementation (round-5 correction, GPT 5.6)** — execution remains pending the user's explicit approval
and Phase 1's formal closure (Phase 1's own exit gate above). **Detail level:** Implementation-ready.

**On deliverable/verification/evidence for this phase's stages (round-5 clarification, GPT 5.6):** unlike
every other phase in this document, Phase 2's stages below are deliberately summarized without repeating
deliverable/verification/evidence inline — that detail already exists, per-task, in the subordinate plan
(`docs/superpowers/plans/2026-07-28-phase2-canonical-publication-contract-hardening.md`), which is
implementation-ready and would make this section redundant if duplicated. Every other phase's stages below
state deliverable/verification/evidence directly, since no subordinate plan exists for them yet.

**Goal:** Make the canonical→publication boundary explicit, independently testable, provably free of
DOCX-runtime dependencies, and *provably validated* (validators demonstrated on purpose to catch specific
corruption at the specific layer meant to catch it).

**Entry gate:** Phase 1 formally closed (Subphase 1.3 complete).

### Subphase 2.0 — Immutable baseline (must run first)
- Stage 2.0.1 — capture Phase-1-accepted `index.md`/`pages/`/`media/` as `golden-master-baseline/` before
  any code change; write `MANIFEST.sha256`; commit immutable.

### Subphase 2.1 — Identity & contract corrections
- Stage 2.1.1 — fix `package_identity` double-prefix.
- Stage 2.1.2 — rename `source_manifest_hash` → `source_content_sha256`; rename the stale-check code.
- Stage 2.1.3 — split schema-version constants per contract; repoint renderer version-gate at the manifest
  constant (not the conversion-plan alias — a real re-coupling bug found and fixed in round-3 review).
- Stage 2.1.4 — give `PublicationMapEntry.chunk_id` real chunk-ID semantics; remove `parent_topic_id`.

### Subphase 2.2 — Validator credibility
- Stage 2.2.1 — cross-artifact lineage checks (chunk sidecar `plan_id`/`source_sha256` vs manifest).
- Stage 2.2.2 — malformed / unexpected publication-map handling; strategy-conditional requirement; the
  publication-map validation check itself validates `entry.chunk_id` (what the renderer actually consumes),
  not `entry.topic_id` — a load-bearing divergence found and fixed in round-3 review.
- Stage 2.2.3 — close the content-comparison-skip loophole via manifest provenance
  (`manifest.generator.plugin`). **Known, accepted limitation (round-4 finding, Opus):** this provenance
  signal is self-asserted in the manifest, not independently verified — a package can claim
  `generator.plugin: "hand-authored-fixture"` and receive the same content-check exemption a genuine
  fixture gets. This is acceptable inside Phase 2's threat model (the producer is trusted; no untrusted
  second producer exists yet), but it is a narrowed bypass, not a closed one. When a second, less-trusted
  producer exists (see extraction triggers, Stage 2.5.3), this must become a verified provenance signal
  (e.g. a signed/hashed producer identity), not a self-declared string — tracked here so a future reader
  doesn't trust this mechanism further than it currently earns.

### Subphase 2.3 — Runtime independence
- Stage 2.3.1 — split `package.py`: extract read-only `canonical_package.py`; harden `load()` to re-derive
  lineage + publication-map integrity. **Sequencing note (round-4 finding, Opus):** this stage ships new
  enforcement logic in `load()` (publication-map re-validation, lineage cross-checks) with no dedicated
  test exercising it until Subphase 2.4's Layer-2 mutation suite runs several stages later. This gap is
  explicit, not accidental: the Layer-2 mutation tests are written after the module split so they can
  target the *final* `load()` shape rather than an intermediate one, but it means Stage 2.3.1's own
  "tests pass" claim covers only pre-existing behavior, not the new enforcement — the new enforcement is
  unverified until Stage 2.4.2 runs. Do not treat Stage 2.3.1 as self-verifying on its own.
- Stage 2.3.2 — transitive import-boundary test with negative-control self-tests.

### Subphase 2.4 — Adversarial mutation suites (headline deliverable)
- Stage 2.4.1 — Layer-1 (`validate_canonical_package`) mutations. **Meta-proof durability (round-4 finding,
  Opus):** for the two checks closest to the image239 lesson — content-comparison and media-reference —
  the "prove this test depends on its check" step must land as a **permanent** test (monkeypatch the check
  to a no-op inside the test itself and assert the mutation then goes undetected), not only a one-time
  throwaway script recorded in a commit message. The other three checks (manifest consistency, orphans,
  plan/source fingerprint) may use the throwaway-script form the Phase 2 plan already specifies.
- Stage 2.4.2 — Layer-2 (`CanonicalPackage.load()`) mutations incl. publication-map/lineage post-promotion
  attacks — this is where Stage 2.3.1's new enforcement logic actually gets its first real test coverage.
- Stage 2.4.3 — Layer-3 (`validate_rendered_output`) mutations incl. index-completeness with adversarial
  link cases.

### Subphase 2.5 — Independence proof & closure
- Stage 2.5.1 — independent hand-authored canonical fixture, validated by the real validator.
- Stage 2.5.2 — runtime-independence behavioral test (DOCX/intake/temp physically absent).
- Stage 2.5.3 — document extraction triggers, including the Stage 2.2.3 provenance-verification trigger
  above.
- Stage 2.5.4 — golden-master comparison against the Subphase 2.0 baseline (byte-identical content,
  semantic metadata).
- Stage 2.5.5 — full-suite run; Task 16's golden-master test must PASS, not SKIP, before completion is
  declared.

**Exit gate:** Mutation coverage matrix complete with every case reaching its intended detector (including
the two now-permanent meta-proof tests); two identity bugs fixed with regression tests; `chunk_id`
resolution proven against the field the renderer actually consumes; publication-map requirement enforced
all three ways; module split + transitive import test green, with Stage 2.3.1's new `load()` enforcement
confirmed covered by Stage 2.4.2 (not merely assumed); golden-master both surfaces pass; intentionally-
changed tests accounted for; exact suite counts reported.

---

## Phase 3.0 — SharePoint Tenant-Capability Discovery

**Disposition:** NEXT. **Detail level:** Research-spike-ready.

**Goal:** Replace assumption with observed tenant facts. Sole deliverable: `tenant-capability-report.md`.

**Entry gate:** Phase 2 exit gate met (a hardened canonical/publication contract exists to map against).

### Subphase 3.0.1 — Access & inventory
- Stage 3.0.1.1 — confirm tenant access, licence ring, and who is asking on whose authority. **Deliverable:**
  a one-page access record. **Verification:** a named person confirms tenant admin/licensing facts
  directly, not inferred. **Evidence:** the access record, dated and attributed.
- Stage 3.0.1.2 — inventory available surfaces (SharePoint Online site types, content types, column
  types). **Deliverable:** surface inventory. **Verification:** each surface confirmed present in the
  actual tenant, not from generic SharePoint documentation. **Evidence:** inventory with screenshots or
  admin-center exports.

### Subphase 3.0.2 — Capability probes (evidence, not assumption)

**Discovery is read-only by default; any write is staged and authorized (round-5 finding, GPT 5.6) —
discovering what a governance capability permits must not itself create an unauthorized governance
exception.** Every probe below that could involve writing anything follows this staged order, not a direct
production write attempt:
1. Confirm existence and inspect schema/permissions **read-only** first.
2. Identify the resource's owner and the permission actually required to write to it.
3. Use a designated non-production/test site or location, never a production knowledge library.
4. Obtain explicit authorization for a specific, reversible test write before attempting one.
5. Write a clearly labeled synthetic artifact (e.g. name-prefixed `TEST-DO-NOT-USE-...`).
6. Remove the synthetic artifact after the probe and preserve only the evidence (screenshots/transcripts),
   not the artifact itself.

- Stage 3.0.2.1 — AgentAssets: does it exist, where, who can write? **Deliverable:** probe result.
  **Verification:** read-only existence/schema check first (steps 1-2 above); a reversible authorized test
  write (steps 3-6) only if read-only inspection can't answer "who can write" definitively. **Evidence:**
  probe transcript/screenshot, with any test write's removal confirmed in the same record.
- Stage 3.0.2.2 — native `SKILL.md` authoring: available on this ring? what schema does it accept?
  **Deliverable:** schema sample or "not available" finding. **Verification:** an authoring attempt in a
  designated non-production test surface only (never a production knowledge location), following the
  staged order above. **Evidence:** the accepted/rejected sample and error text if rejected, plus
  confirmation the test artifact was removed.
- Stage 3.0.2.3 — agent creation: possible, by whom, what approval path, what write identity?
  **Deliverable:** approval-path record. **Verification:** confirmed with tenant admin, not inferred from
  general M365 licensing tiers — this stage is a read-only administrative confirmation, no test agent
  creation needed to answer it. **Evidence:** the approval-path record, named owner attached.
- Stage 3.0.2.4 — native Markdown rendering: enabled? **Deliverable:** yes/no finding. **Verification:**
  a rendering attempt against a designated non-production test item, following the staged order above.
  **Evidence:** screenshot of rendered (or failed) output, test item removed afterward.
- Stage 3.0.2.5 — metadata field types/constraints available for a pilot library. **Deliverable:** field
  type inventory. **Verification:** created against an explicitly designated, authorized non-production
  test library in the tenant (not an ad hoc write against whatever is convenient). **Evidence:** the field
  inventory with observed type constraints, test library's authorization recorded.

### Subphase 3.0.3 — Report & gating decision
- Stage 3.0.3.1 — write `tenant-capability-report.md` with observed evidence per probe. **Deliverable:**
  the report itself. **Verification:** every probe from Subphase 3.0.2 has a corresponding section citing
  its actual evidence, not a summary written from memory. **Evidence:** the report, cross-checked against
  each probe's own evidence artifact.
- Stage 3.0.3.2 — map each Phase 3–5 dependency to a "confirmed available / confirmed blocked / needs
  escalation" status. **Deliverable:** the dependency-status map. **Verification:** every Phase 3/4/5 entry
  gate item traced to a specific probe result. **Evidence:** the map. **Decision owner:** the initiative's
  technical lead, with tenant admin sign-off on any "confirmed blocked" finding.

**Exit gate:** `tenant-capability-report.md` answers all five probe questions with observed evidence;
Phase 3 scope confirmed feasible or explicitly re-gated.

---

## Phase 3 — Governed SharePoint Knowledge Pilot

**Disposition:** NEXT, gated behind 3.0. **Detail level:** Bounded pilot scope, provisional architecture.

**Goal:** Publish hardened canonical content into a governed SharePoint knowledge library — package-only by
default, no autonomous write — proving the metadata/source-of-truth model on one real library.

**Entry gate:** Phase 3.0 report confirms library metadata fields and (at minimum) package-only deployment
is feasible.

### Subphase 3.1 — Metadata schema mapping & source-of-truth lifecycle
- Stage 3.1.1 — map canonical/publication contract → minimal library schema: owner, status, review date,
  topic ID, publication ID, validation state. **Deliverable:** schema-mapping document. **Verification:**
  every canonical/publication field has an explicit mapped library column or a stated reason it's omitted.
  **Evidence:** the mapping document.
- Stage 3.1.2 — reconcile schema against Phase 3.0's observed field-type constraints; adjust, don't guess.
  **Deliverable:** reconciled schema. **Verification:** every field type checked against Stage 3.0.2.5's
  actual observed constraints, not assumed compatible. **Evidence:** the reconciled schema with the 3.0.2.5
  reference cited per field.
- Stage 3.1.3 — define canonical-vs-published source-of-truth rule (canonical is authoritative; published
  is a rendered projection). **Deliverable:** one-paragraph rule statement. **Verification:** the rule is
  unambiguous about which artifact wins in a disagreement. **Evidence:** the rule statement, folded into
  Stage 3.1.4's document below.
- Stage 3.1.4 — **source-of-truth lifecycle rules (round-4 finding, GPT 5.6 — "canonical is authoritative"
  is an architectural slogan without these decisions).** Before any publication happens, decide and
  document, explicitly:
  - Is manual editing of published SharePoint content prohibited, tolerated, or reconciled?
  - What happens when someone edits published content directly — is that drift?
  - Must drift flow back into canonical content, or is it discarded on next republish?
  - How does republishing behave when manual edits exist (overwrite silently, warn, block)?
  - Which repository/package/version is authoritative when canonical and published disagree?
  - How are superseded versions marked in the library?
  **Deliverable:** `source-of-truth-lifecycle.md`. **Verification:** each question above has an explicit
  answer, not a default-by-omission. **Evidence:** the document itself, reviewed before Subphase 3.2 pilots
  anything.
  **Related open question (not yet decided, informs but does not resolve this stage):**
  `docs/vision/editing-workflow-options-for-external-review.md` explores where content authors would
  actually edit content (Git vs. SharePoint vs. a hybrid), candidate editing/synchronization models
  A–G, a proposed non-negotiable rule that routine authoring must hide Git/publication machinery from
  business authors, and a concrete supervised human-technical-publisher bridge (three named repository
  skills: get-approved-chunks / render / publish) usable before any GitHub↔SharePoint integration
  exists. Stage 3.1.4's answers should be informed by that document's eventual Phase 3.0 findings, not
  assume any of its candidate models in advance.

### Subphase 3.2 — Package-only deployment mode
- Stage 3.2.1 — produce an upload-ready package (artifacts + metadata sidecar) that writes nothing
  autonomously. **Deliverable:** the upload-ready package. **Verification:** package contents traced back
  to Stage 3.1.1's schema mapping, field by field. **Evidence:** the package plus its schema-mapping trace.
- Stage 3.2.2 — dry-run validation: package matches target library schema; no field type violations.
  **Deliverable:** dry-run validation report. **Verification:** every field checked against the actual
  reconciled schema (Stage 3.1.2), not a generic schema. **Evidence:** the validation report.
- Stage 3.2.3 — manual, human-performed upload of the pilot library; record what the human had to do.
  **Deliverable:** upload log. **Verification:** a named human actually performed the upload and recorded
  every manual step (this is deliberate evidence for later automation scoping, not busywork). **Evidence:**
  the upload log.

### Subphase 3.3 — Publication Reconciliation and Recovery

**(New subphase, round-4 finding, GPT 5.6 — publication packaging/validation/upload alone does not cover
what happens when published state and canonical state drift, which is a first-class concern for any
system moving content into a second store, not an implicit metadata afterthought.)**

- Stage 3.3.1 — reconcile expected publications (from the publication map) against actual SharePoint
  library items — detect missing, duplicate, stale, and unexpected items. **Deliverable:** reconciliation
  report. **Verification:** every publication-map entry checked against an actual library item.
  **Evidence:** the reconciliation report.
- Stage 3.3.2 — preserve canonical package identity, publication identity, and validation lineage on every
  published item, so any item can be traced back to the exact canonical package/version that produced it.
  **Deliverable:** lineage-field mapping on the library schema. **Verification:** one real published item
  traced back to its exact source package. **Evidence:** the trace record.
- Stage 3.3.3 — define safe republish behavior (what happens when the same topic is published again —
  overwrite in place, version, or block on conflict). **Deliverable:** republish-behavior policy.
  **Verification:** exercised against one real republish in the non-production pilot. **Evidence:** the
  exercised republish's before/after record.
- Stage 3.3.4 — define rollback/unpublish behavior for a bad publication. **Deliverable:** rollback
  procedure. **Verification:** exercised against a deliberately "bad" non-production pilot item.
  **Evidence:** before/after inventory, execution log, and reviewer acceptance.
- Stage 3.3.5 — handle renamed or retired topic IDs without orphaning previously published items.
  **Deliverable:** rename/retirement handling policy. **Verification:** exercised against one deliberately
  renamed topic ID in the pilot. **Evidence:** the exercised test's before/after record.
- Stage 3.3.6 — require dry-run reconciliation reporting before any future authorized-write mode is
  approved (Subphase 3.4 below). **Deliverable:** the dry-run reporting mechanism itself. **Verification:**
  run at least once against the pilot library with zero autonomous writes performed. **Evidence:** the
  dry-run report.

### Subphase 3.4 — Governance controls
- Stage 3.4.1 — versioning + topic/publication review workflow (draft → reviewed → published).
  **Deliverable:** review-workflow definition. **Verification:** one real item walked through all three
  states. **Evidence:** the walked-through item's history.
- Stage 3.4.2 — permission review and oversharing/discoverability check (Protected B discoverability risk
  explicitly tested). **Deliverable:** oversharing-test report. **Verification:** tested under at least two
  distinct permission identities against the pilot library. **Evidence:** the test report.
- Stage 3.4.3 — authorized-write identity: *design only*, gated behind an approved write credential; do
  not build the write path until an owner and identity are approved, and until Subphase 3.3's reconciliation
  dry-run reporting exists to gate it. **Deliverable:** write-identity design document (no implementation).
  **Verification:** an accountable owner and identity are named, not left TBD. **Evidence:** the design
  document with named owner/identity.

### Subphase 3.5 — Pilot evaluation
- Stage 3.5.1 — content readiness checks against the live library. **Deliverable:** readiness-check report.
  **Verification:** every pilot item checked against the Stage 3.1.1 schema for completeness.
  **Evidence:** the report.
- Stage 3.5.2 — pilot retrospective: what the model got right, what governance gaps surfaced.
  **Deliverable:** `phase-3-retrospective.md`. **Verification:** every stage above's evidence is cited, not
  summarized from memory. **Evidence:** the retrospective document, which becomes the entry-gate evidence
  for Phase 4/5's "real (not assumed) requirements."

**Exit gate:** One real governed library populated via package-only deployment; metadata schema proven
against actual tenant constraints; source-of-truth lifecycle rules documented and followed; reconciliation/
rollback behavior demonstrated in dry-run; oversharing controls tested; retrospective documents real (not
assumed) requirements for Phases 4–5. Records/retention/audit remain LATER (Phase 8, Subphase 8.4) unless
this pilot surfaces a concrete need to pull that work forward.

---

## Phase 4 — Native SharePoint Skills Pilot

**Disposition:** RESEARCH, gated behind 3.0/3. **Detail level:** Requirements + subphase structure only;
internals await 3.0 findings.

**Goal:** Pilot one native SharePoint skill (`SKILL.md`-authored) end-to-end, manually deployed before any
automation.

**Entry gate:** Phase 3.0 confirms native skill authoring + AgentAssets are available and writable by an
identified owner; Phase 3 library exists as grounding substrate.

### Subphase 4.1 — Candidate selection & feasibility
- Stage 4.1.1 — pick one candidate skill (review-manual-topics is the leading candidate) against 3.0's real
  permission findings. **Deliverable:** candidate selection memo. **Verification:** selection checked
  against actual (not assumed) 3.0 permission findings. **Evidence:** the memo, citing the specific 3.0
  probe results it relies on.
- Stage 4.1.2 — confirm the skill's inputs exist in the Phase 3 library. **Deliverable:** input-availability
  check. **Verification:** each required input traced to a real item in the Phase 3 pilot library.
  **Evidence:** the check record.

### Subphase 4.2 — Authoring & manual deployment
- Stage 4.2.1 — author `SKILL.md`; validate against the schema 3.0 observed the tenant accepts.
  **Deliverable:** the authored `SKILL.md`. **Verification:** validated against Stage 3.0.2.2's observed
  schema, not a generic template. **Evidence:** the validation result.
- Stage 4.2.2 — manual deployment (no automation yet); record every manual step for later automation
  scoping. **Deliverable:** deployment log. **Verification:** a named human performed every step.
  **Evidence:** the deployment log.

### Subphase 4.3 — Evaluation harness
- Stage 4.3.1 — normal-case evaluation set. **Deliverable:** normal-case test set + results.
  **Verification:** every case checked for correct skill behavior. **Evidence:** the results.
- Stage 4.3.2 — negative / ambiguous / permission / safety evaluation sets. **Deliverable:** the four
  evaluation sets + results. **Verification:** each category has at least one real test case exercised
  against the deployed skill. **Evidence:** the results per category.
- Stage 4.3.3 — evidence capture: what passed, what the skill refused, what leaked. **Deliverable:**
  consolidated evidence report. **Verification:** every category from 4.3.1/4.3.2 accounted for.
  **Evidence:** the consolidated report — this is Phase 4's exit-gate evidence.

### Subphase 4.4 — Lifecycle
- Stage 4.4.1 — versioning, promotion, retirement policy for the piloted skill. **Deliverable:** lifecycle
  policy document. **Verification:** names a decision owner and a review cadence, not left open-ended.
  **Evidence:** the policy document.

**Exit gate:** One native skill deployed and evaluated with evidence across all five evaluation categories;
manual deployment steps documented as automation candidates; no oversharing/permission failures.

---

## Phase 5 — SharePoint Knowledge Agent Pilot

**Disposition:** RESEARCH, gated behind Phase 3 (not unconditionally behind Phase 4 — see entry gate,
round-4 finding, GPT 5.6). **Detail level:** Requirements + structure only.

**Goal:** Pilot one grounded knowledge agent over the Phase 3 library, with strict source scoping and
honest handling of stale/superseded content.

**Entry gate (corrected — round-4 finding, GPT 5.6):** an earlier version of this plan hard-coded "Phase 4
must complete before Phase 5," reasoning "an agent needs something to be grounded in." That over-states the
real dependency: the actual grounding source is Phase 3's governed library, not a native SharePoint skill.
The corrected gate is:
- Phase 3's governed knowledge library exists and is populated.
- Phase 3.0 confirms agent-creation permissions and an approval path for a write/agent-creation identity.
- Phase 4 is a **prerequisite only if** the specific agent scenario selected actually invokes or depends
  on a native skill (e.g., an agent that calls `review-manual-topics` as a tool). For a scenario that only
  needs to read/ground on the Phase 3 library directly, Phase 4 and Phase 5 may run as **parallel sibling
  pilots** after Phase 3, not sequentially. Decide which case applies per selected scenario at the start of
  Subphase 5.1, do not assume the stronger dependency by default.

**Reconciliation with the Global Gating Rules' "no new agents" rule (round-5 finding, GPT 5.6):** the
Global Gating Rules below say "no new agents until ≥2 plugins with ≥2 distinct user journeys exist," which
is a different, stricter gate than the one stated above — and as written, the two could contradict each
other (Phase 5's own gate could be met while the global rule still forbids proceeding). Resolved: the
global rule is about **general-purpose routing/orchestration agents** (e.g. a `knowledge-workbench-agent`
that decides which plugin/journey to invoke) — that class stays gated behind ≥2 plugins/journeys, unchanged.
A **bounded Phase 5 knowledge-agent pilot** (one specific, scoped agent grounded in one library, with its
own governance/evaluation gate above) is a different class and may proceed once Phase 5's own entry gate
above is met, independent of the plugin-count gate. See the Global Gating Rules section for the exact
restated rule.

### Subphase 5.1 — Grounding & scoping
- Stage 5.1.1 — define approved grounding sources; confirm source scoping honors library permissions.
  **Deliverable:** `approved-grounding-sources.md`. **Verification:** each source has an owner, permission
  scope, and review status. **Evidence:** governance approval plus permission-test results.
  **Decision owner:** the Phase 3 library's accountable owner.
- Stage 5.1.2 — agent instructions + explicit answer boundaries (what it must refuse). **Deliverable:**
  instruction/boundary document. **Verification:** boundary cases enumerated and each one tested against
  the deployed agent. **Evidence:** the boundary-test transcript. **Decision owner:** the agent's assigned
  owner (Stage 5.4.1).

### Subphase 5.2 — Content-currency behavior
- Stage 5.2.1 — current/stale/superseded handling using owner + review-date metadata from Phase 3.
  **Deliverable:** currency-handling policy. **Verification:** tested against at least one deliberately
  stale item in the pilot library. **Evidence:** the test transcript showing correct stale-content handling.
  **Decision owner:** the agent's assigned owner.
- Stage 5.2.2 — behavior when grounding content is out of review. **Deliverable:** out-of-review response
  policy (e.g., refuse, caveat, or escalate). **Verification:** tested against an item whose review date
  has lapsed. **Evidence:** the test transcript. **Decision owner:** the agent's assigned owner.

### Subphase 5.3 — Evaluation
- Stage 5.3.1 — answerable evaluation set (grounded, correct, cited). **Deliverable:** answerable-case
  evaluation set + results. **Verification:** each case checked for correct grounding and citation, not
  just a non-empty answer. **Evidence:** the evaluation run's recorded results. **Decision owner:** the
  agent's assigned owner.
- Stage 5.3.2 — unanswerable evaluation set (agent declines rather than fabricates). **Deliverable:**
  unanswerable-case evaluation set + results. **Verification:** each case confirms a decline, not a
  fabricated answer. **Evidence:** the evaluation run's recorded results. **Decision owner:** same.
- Stage 5.3.3 — permission/oversharing probes across identities. **Deliverable:** permission-probe set +
  results. **Verification:** probes run under at least two distinct permission identities, confirming no
  oversharing. **Evidence:** the probe transcripts. **Decision owner:** same, with the Phase 3 library
  owner co-signing.

### Subphase 5.4 — Deployment & lifecycle governance
- Stage 5.4.1 — deployment approval path; ownership; review cadence. **Deliverable:** deployment-approval
  record. **Verification:** named accountable owner signs off before deployment. **Evidence:** the signed
  approval record.

**Exit gate:** One grounded agent passing answerable + unanswerable + permission evaluation sets;
stale-content handling demonstrated; deployment governed by an accountable owner.

---

## Phase 5.5A — Content Model Expansion

**(Split from a single Phase 5.5, round-5 finding, GPT 5.6: an either/or exit gate across two
independently-triggered tracks created an accounting problem — completing only the renderer track could
mark the umbrella phase closed while the content-model track remained untouched, silently losing its
future home. Split into two independently tracked phases with their own status and exit gate.)**

**Disposition:** NOT TRIGGERED (RESEARCH once triggered). **Detail level:** Structure only.

**Goal:** Prove or disprove that the canonical content model generalizes beyond one content type
("manual"), using a real second case rather than speculative design.

**Entry gate:** A concrete second content type (policy, procedure, or training material) is identified with
a real document/need behind it — not invented to exercise this phase.

### Subphase 5.5A.1 — Content Model Expansion
- Stage 5.5A.1.1 — select a second real content type. **Deliverable:** selection memo. **Verification:**
  a real document of that type exists and has a real owner/need. **Evidence:** the memo naming the
  document and owner.
- Stage 5.5A.1.2 — analyze its structural and governance differences from "manual." **Deliverable:**
  gap-analysis document. **Verification:** every structural/governance difference from the manual profile
  is enumerated, not assumed absent. **Evidence:** the gap-analysis document.
- Stage 5.5A.1.3 — determine which canonical fields are shared vs. profile-specific. **Deliverable:**
  field-classification table. **Verification:** every canonical field classified shared/profile-specific
  with a stated reason. **Evidence:** the table.
- Stage 5.5A.1.4 — create authoring guidance and templates for the new type. **Deliverable:** authoring
  guide + template. **Verification:** a person unfamiliar with the type can follow the guide to author a
  valid example. **Evidence:** the guide/template plus a dry-run authoring attempt.
- Stage 5.5A.1.5 — convert one real example end-to-end. **Deliverable:** a real converted canonical
  package. **Verification:** passes the same canonical/render validators Phase 2 hardened, with no
  exceptions carved out for the new type. **Evidence:** validation reports.
- Stage 5.5A.1.6 — prove existing consumers (Phase 2's hardened contract, the renderer, any Phase 3-5
  pilots already live) do not break. **Deliverable:** regression-test run against existing consumers.
  **Verification:** full suite passes with the new type's fixture added, no existing test loosened.
  **Evidence:** the test run's exact pass/fail counts.
- Stage 5.5A.1.7 — decide, with evidence, whether the canonical model genuinely generalizes or needs a
  content-type-specific extension. **Deliverable:** decision record. **Verification:** the decision cites
  the evidence from Stages 5.5A.1.1-1.6, not a general impression. **Evidence:** the decision record.
  **Decision owner:** the initiative's technical lead.

**Exit gate:** One real second content type converted end-to-end, passing existing validators, with no
broken consumers, and an evidenced generalization decision recorded. Not evaluable until its entry gate is
met.

---

## Phase 5.5B — Renderer Expansion

**Disposition:** NOT TRIGGERED (RESEARCH once triggered) — independent of Phase 5.5A's status; completing
one does not close the other. **Detail level:** Structure only.

**Goal:** Prove or disprove that the publication contract generalizes beyond one renderer
("multipage-markdown"), using a real required output format rather than speculative design.

**Entry gate:** A concrete required output format (Word, PDF, HTML, PowerPoint) is identified with a real
need behind it — not invented to exercise this phase.

### Subphase 5.5B.1 — Renderer Expansion
- Stage 5.5B.1.1 — identify a real required output format (not speculative). **Deliverable:** format
  requirement memo. **Verification:** a real, named need exists for this format. **Evidence:** the memo.
- Stage 5.5B.1.2 — compare direct canonical-to-format rendering against transforming from the existing
  Markdown output. **Deliverable:** comparison memo. **Verification:** both approaches actually prototyped
  at a small scale before choosing. **Evidence:** the comparison memo with both prototypes' results.
- Stage 5.5B.1.3 — define the output profile/contract for the new renderer. **Deliverable:** renderer
  contract document. **Verification:** conforms to the `Renderer` protocol Phase 2 hardened
  (`supported_manifest_versions`, `render(package, output_dir) -> RenderResult`). **Evidence:** the
  contract document.
- Stage 5.5B.1.4 — implement one additional renderer. **Deliverable:** the renderer implementation.
  **Verification:** TDD per this repo's standing rule; registers with the existing renderer registry
  without modifying it. **Evidence:** the test suite for the new renderer.
- Stage 5.5B.1.5 — run fidelity and golden-master validation against it, same discipline as Phase 2's
  Subphase 2.5.4. **Deliverable:** golden-master comparison for the new renderer's output.
  **Verification:** byte-identical (or format-appropriate equivalent) comparison against an accepted
  baseline. **Evidence:** the comparison test results.
- Stage 5.5B.1.6 — decide whether renderer extraction into a separate module/plugin is warranted (per the
  extraction triggers, Stage 2.5.3). **Deliverable:** extraction decision record. **Verification:** checked
  against the actual extraction triggers, not a general preference. **Evidence:** the decision record.
  **Decision owner:** the initiative's technical lead.

**Exit gate:** One additional renderer implemented and passing fidelity/golden-master validation. Not
evaluable until its entry gate is met.

---

## Phase 6 — Multi-Runtime Capability Model

**Disposition:** LATER, gated behind ≥2 real runtimes. **Detail level:** Decision framework only.

**Goal:** Define a shared capability specification once two real runtimes (e.g. GitHub/Claude skill +
native SharePoint skill) exist to specify against — preventing behavioral drift across runtimes.

**Entry gate:** At least two runtimes implement the same capability in production (currently zero
SharePoint-side runtimes exist — gate not met).

### Subphase 6.1 — Capability specification format
- Stage 6.1.1 — extract the shared contract from the two existing runtime implementations (do not design
  speculatively). **Deliverable:** shared-contract document. **Verification:** every element traced to
  something both real implementations actually do. **Evidence:** the document with per-element traces.
- Stage 6.1.2 — common evaluation-case set both runtimes must pass. **Deliverable:** evaluation-case set.
  **Verification:** run against both real runtimes with recorded results. **Evidence:** both runtimes'
  results.
- Stage 6.1.3 — **adversarial intent-preservation check (round-4 finding, GPT 5.6).** Do not derive the
  "shared specification" merely by intersecting what the two implementations happen to do — both may share
  the same accidental limitation. Explicitly: compare both runtime implementations against the *original*
  user capability and governance intent (not against each other only); separate essential behavior from
  implementation coincidence; record intentional target-specific differences rather than erasing them;
  validate that shared evaluation cases test *meaning*, not merely matching output strings. **Deliverable:**
  intent-preservation review document. **Verification:** each shared-spec element checked against the
  originating capability/governance intent, not just cross-runtime agreement. **Evidence:** the review
  document. **Decision owner:** the initiative's technical lead.

### Subphase 6.2 — Adapters & drift detection
- Stage 6.2.1 — target-specific adapters over the shared spec. **Deliverable:** adapter implementations.
  **Verification:** each adapter passes the Stage 6.1.2 common evaluation set for its target.
  **Evidence:** per-adapter test results.
- Stage 6.2.2 — behavioral-drift detection comparing runtimes against the common cases. **Deliverable:**
  drift-detection mechanism. **Verification:** deliberately introduce a drift in one runtime and confirm
  detection. **Evidence:** the detection test result.
- Stage 6.2.3 — reuse-vs-target-specific-behavior decision rules. **Deliverable:** decision-rule document.
  **Verification:** at least one real reuse-vs-specific decision made using the rules, not hypothetically.
  **Evidence:** the applied decision record.

**Exit gate:** Shared spec + common evaluation cases demonstrably prevent drift across ≥2 runtimes, proven
against original intent (Stage 6.1.3), not just cross-runtime agreement. Not evaluable until the entry gate
is met.

---

## Phase 7 — Cowork & Copilot Studio Evaluation

**Disposition:** RESEARCH (owner-and-use-case gate). **Detail level:** Decision framework, candidate pilots
only.

**Goal:** Decide, per target, whether to build — only for a target that has a concrete use case and an
accountable owner.

**Entry gate:** A concrete use case with a named accountable owner emerges. Until then, do not scaffold
packaging plugins or manifests.

### Subphase 7.1 — Capability-gap analysis
- Stage 7.1.1 — identify what Cowork/Copilot Studio would do that existing plugins/skills/agents cannot.
  **Deliverable:** gap-analysis memo. **Verification:** each named gap checked against what Phases 1-6
  actually already provide, not assumed absent. **Evidence:** the memo.
- Stage 7.1.2 — candidate use cases with named owners. **Deliverable:** candidate list. **Evidence:** the
  list, empty if no owner has yet come forward — an empty list is a valid, honest result here.

### Subphase 7.2 — Build/no-build gate
- Stage 7.2.1 — connector/external-system, workflow/orchestration, licensing/capacity/environment
  requirements per candidate. **Deliverable:** requirements memo per candidate. **Verification:** checked
  against actual licensing/capacity facts, not assumed. **Evidence:** the memo.
- Stage 7.2.2 — explicit build/no-build decision per target; build only the one with a concrete use case +
  owner. **Deliverable:** decision record per target. **Verification:** cites the specific use case and
  owner, or explicitly states neither exists yet. **Evidence:** the decision record. **Decision owner:**
  the initiative's technical lead + the named use-case owner, jointly.

**Exit gate:** A documented build/no-build decision per target, each traceable to a concrete use case and
owner, or an explicit "no owner/use case yet — remain RESEARCH."

---

## Phase 8 — Scale, Promotion & Operations

**Disposition:** LATER, activates **incrementally per capability** (round-5 fix, GPT 5.6 — a single
monolithic "Phases 3-5 all complete" gate could block operationalizing a successful Phase 3 pilot merely
because Phase 4 or 5 stalled on an unrelated tenant/owner blocker). **Detail level:** Operational
capability categories + entry criteria only.

**Goal:** Turn proven pilots into operable, monitored, lifecycle-managed capabilities — designed from real
operational experience, not in advance of it.

**Entry gate (corrected — round-5 finding, GPT 5.6):** Phase 8 activates **per capability**, not as one
block:
- The Phase 3 library may enter promotion/lifecycle management (Subphases 8.1/8.3, scoped to the library)
  as soon as Phase 3's own exit gate is met — it does not wait for Phase 4 or 5.
- A Phase 4 skill may enter skill lifecycle management as soon as Phase 4's own exit gate is met.
- A Phase 5 agent may enter agent operations as soon as Phase 5's own exit gate is met.
- **Cross-capability** concerns — Subphase 8.2's monitoring/drift detection *across* multiple capabilities,
  and any shared release-compatibility policy spanning more than one capability — require at least two
  operational capabilities to exist first (i.e. at least two of Phase 3/4/5 have individually reached this
  gate).
- Records/retention/audit (Subphase 8.4) may be pulled forward as soon as the Phase 3 retrospective
  (Stage 3.5.2) surfaces a concrete need — it does not wait for the rest of Phase 8 either.

### Subphase 8.1 — Promotion & release management
- Stage 8.1.1 — dev/test/production promotion path. **Deliverable:** promotion-path document, scoped to
  whichever capability triggered it first. **Verification:** at least one real artifact (skill, agent, or
  library schema change) actually promoted through it. **Evidence:** the promotion record.
- Stage 8.1.2 — release management + version compatibility across contracts, skills, agents.
  **Deliverable:** version-compatibility policy — single-capability scope until the cross-capability
  entry gate above is met, then extended. **Verification:** at least one real version bump exercised
  against it. **Evidence:** the compatibility-check result for that bump.

### Subphase 8.2 — Monitoring & assurance

**(Cross-capability — requires ≥2 operational capabilities per the entry gate above.)**

- Stage 8.2.1 — monitoring + behavioral-drift detection in production. **Deliverable:** monitoring
  mechanism spanning the ≥2 live capabilities. **Verification:** a deliberately introduced drift in one
  capability is detected. **Evidence:** the detection test result.
- Stage 8.2.2 — release evidence/auditability at scale. **Deliverable:** cross-capability release-evidence
  process. **Verification:** at least one real release across ≥2 capabilities produces the required
  evidence. **Evidence:** that release's evidence record.

### Subphase 8.3 — Ownership & lifecycle
- Stage 8.3.1 — ownership/support model, review cycles, incident handling. **Deliverable:**
  ownership/support charter. **Verification:** a named owner and a real incident (or drill) run through
  the documented process. **Evidence:** the charter plus the incident/drill record.
- Stage 8.3.2 — deprecation/retirement. **Deliverable:** deprecation/retirement procedure. **Verification:**
  exercised against one real (or deliberately staged) retirement. **Evidence:** the exercised procedure's
  record.
- Stage 8.3.3 — onboarding/adoption patterns for reuse. **Deliverable:** onboarding guide. **Verification:**
  a person unfamiliar with the capability follows it to onboard. **Evidence:** the onboarding attempt's
  record.

### Subphase 8.4 — Records, Retention & Audit

**(New subphase, round-4 finding, GPT 5.6 — Workstream C named records/retention/audit as LATER but no
phase or subphase ever picked the work up; this gives it an explicit home without inventing the actual
rules before the Phase 3 pilot surfaces real requirements.)**

- Stage 8.4.1 — determine records classification requirements from the SharePoint pilot's actual content
  (Phase 3 retrospective, Stage 3.5.2). **Deliverable:** classification memo. **Verification:** every
  classification cites a specific Phase 3 pilot item, not a generic records category. **Evidence:** the
  memo.
- Stage 8.4.2 — define retention treatment for canonical and published artifacts. **Deliverable:** retention
  policy. **Verification:** approved by records/legal review (Stage 8.4.5) before any enforcement.
  **Evidence:** the approved policy.
- Stage 8.4.3 — define audit evidence requirements (what must be provable, to whom, for how long).
  **Deliverable:** audit-requirements document. **Verification:** approved by records/legal review.
  **Evidence:** the approved document.
- Stage 8.4.4 — define supersession and destruction handling. **Deliverable:** supersession/destruction
  policy. **Verification:** approved by records/legal review. **Evidence:** the approved policy.
- Stage 8.4.5 — obtain the appropriate policy/legal/records review before implementing any of the above —
  this subphase does not invent records-management rules unilaterally. **Deliverable:** the review
  sign-off itself. **Verification:** a named records/legal reviewer actually reviewed Stages 8.4.1-8.4.4,
  not a self-certification. **Evidence:** the signed review record. **Decision owner:** the named
  records/legal reviewer.

**Exit gate:** Each operational capability category (promotion, monitoring, ownership, records) has an
owner, a defined process exercised at least once, and — for records/retention/audit specifically — the
required policy/legal review completed before any rule is enforced in production.

---

## Full Traceability Matrix

Every major vision item, mapped to where it actually lives — not just a workstream, but a specific phase
and stage, its disposition, its prerequisite, its eventual exit evidence, and (where deferred/rejected) the
reason. This replaces the earlier workstream-only table, which GPT 5.6's round-4 review correctly noted
asserted completeness without demonstrating it.

| Vision item | Phase / stage | Disposition | Prerequisite | Exit evidence | Reason if deferred |
|---|---|---|---|---|---|
| DOCX is a transitional extraction format, not the canonical management format | Phase 1 (done), Phase 2 (hardens the independence) | NOW | — | **Combined evidence (round-5 correction, GPT 5.6 — a single import-boundary test proves only that the renderer doesn't transitively import DOCX-analysis modules, not the full claim):** Phase 2 Stage 2.3.2's import-boundary test, PLUS Stage 2.5.1's independent-fixture proof (canonical package loads/renders with no DOCX ever having produced it), PLUS Stage 2.5.2's runtime-independence test (DOCX/intake/temp physically absent), PLUS Phase 3 Stage 3.1.3's source-of-truth rule naming canonical (not DOCX, not published SharePoint pages) as authoritative | — |
| Structured content authoring guidance (manual) | Phase 1, `references/content-authoring-guide.md` | DONE | — | existing contract-test coverage | — |
| Policies, procedures, training content types | Phase 5.5A, Subphase 5.5A.1 | RESEARCH | a real second content type identified | Stage 5.5A.1.7's generalization decision | no second content type exists yet |
| SharePoint publication | Phase 3, Subphase 3.2 | NEXT | Phase 3.0 confirms feasibility | Stage 3.2.3's manual upload record | gated on 3.0 |
| Package-only vs. authorized-write deployment | Phase 3, Subphase 3.2/3.4.3 | NEXT (package-only), LATER (authorized-write) | approved write identity for authorized-write | Stage 3.2.3 (package-only); Stage 3.3.6 dry-run report (authorized-write gate) | write path needs an approved owner/identity first |
| Publication reconciliation, rollback, drift | Phase 3, Subphase 3.3 | NEXT | Subphase 3.2 pilot exists | Stage 3.3.6's dry-run reconciliation report | — |
| Source-of-truth lifecycle (editing/drift/republish rules) | Phase 3, Stage 3.1.4 | NEXT | — | `source-of-truth-lifecycle.md` | — |
| Native `SKILL.md` assets | Phase 4 | RESEARCH | Phase 3.0 confirms authoring availability | Stage 4.2.1's validated `SKILL.md` | tenant capability unconfirmed |
| `AgentAssets` | Phase 3.0, Stage 3.0.2.1 | NEXT (discovery only) | tenant access | probe transcript | — |
| Quiz generation (`generate-quiz-from-content`) | Phase 4, Subphase 4.1 (candidate list) | RESEARCH | Phase 4's first candidate (review-manual-topics) evaluated first | — | additional candidates only after first is evaluated, per original vision doc |
| Apply-content-outline capability | Phase 4, Subphase 4.1 (candidate list) | RESEARCH | same as quiz generation | — | same |
| SharePoint agent grounding | Phase 5 | RESEARCH | Phase 3 library exists; Phase 3.0 confirms agent-creation permissions | Stage 5.1.1's grounding-source record | gated on 3/3.0, NOT unconditionally on Phase 4 (corrected dependency) |
| Permission-aware / stale-content agent behavior | Phase 5, Subphase 5.2 | RESEARCH | Phase 5 entry gate | Stage 5.2.1/5.2.2 test transcripts | — |
| GitHub/Claude skills (existing `docx-to-content` skills) | Phase 1/2 | DONE/NOW | — | existing skill files | — |
| Common capability definitions across runtimes | Phase 6 | LATER | ≥2 real runtimes | Stage 6.1.3's intent-preservation check | no second runtime exists yet |
| Cowork | Phase 7 | RESEARCH | concrete use case + owner | Stage 7.2.2's build/no-build decision | no owner/use case yet — NOT a scope rejection |
| Copilot Studio | Phase 7 | RESEARCH | concrete use case + owner | Stage 7.2.2's build/no-build decision | same |
| Evaluation and governance (cross-cutting) | Phase 2 (mutation suites), Phase 3-6 (target-specific) | NOW (Phase 2 portion), LATER (rest) | each target phase's own entry gate | each phase's own exit gate | rest gated behind the capabilities they evaluate existing |
| Lifecycle and retirement | Phase 8, Subphase 8.3 | LATER | Phase 3-5 operational experience | Stage 8.3.1's charter + incident record | no operational experience yet |
| Oversharing risk | Phase 3, Stage 3.4.2 | NEXT | Phase 3 pilot | Stage 3.4.2's discoverability test result | — |
| Repository/plugin extraction triggers | `references/extraction-triggers.md` (Phase 2, Stage 2.5.3) | **NOW — planned in Phase 2, not yet executed** (round-5 correction, GPT 5.6: Phase 2 has not run yet, so this cannot be marked DONE) | Phase 2 execution | the document itself, once Stage 2.5.3 actually runs | triggers not yet met for any workstream |
| Additional output formats (Word/PDF/HTML/PowerPoint) | Phase 5.5B, Subphase 5.5B.1 | RESEARCH | a real required output format identified | Stage 5.5B.1.5's fidelity/golden-master validation | no required format exists yet |
| Records, retention, audit | Phase 8, Subphase 8.4 | LATER | Phase 3 retrospective surfaces real requirements | Stage 8.4.5's policy/legal review | no pilot has run yet to derive real requirements from |

---

## Global Gating Rules (carried from architecture review, unchanged)

- Repository rename: **deferred**, not rejected — low-urgency, revisit anytime.
- No new plugins beyond `docx-to-content` until Phase 3 justifies `sharepoint-knowledge`.
- **No new general-purpose routing/orchestration agent** (e.g. a `knowledge-workbench-agent` that decides
  which plugin/journey to invoke) **until ≥2 plugins with ≥2 distinct user journeys exist.** This is
  distinct from Phase 5's bounded knowledge-agent pilot (round-5 clarification, GPT 5.6): a single,
  scoped agent grounded in one library, gated by Phase 5's own entry gate (governed library + confirmed
  agent-creation permissions), may proceed independent of this plugin-count gate — it is not the class of
  agent this rule exists to prevent.
- Nothing past Phase 2 is authorized to *build*; Phases 3.0+ are planned in structure, gated on evidence.
- Every far-phase stage is deliberately structural, not speculative: real requirements (tenant facts, pilot
  outcomes, a second runtime) are prerequisites, not assumptions.
- **RESEARCH vs. REJECTED discipline (round-4 fix):** a phase/workstream gated on a missing *fact* (tenant
  capability, second runtime) or a missing *use case/owner* (Cowork, Copilot Studio) is RESEARCH, not
  REJECTED — REJECTED is reserved for something this plan has an actual architectural objection to, which
  currently applies to nothing in this document. Workstream G (Cowork/Copilot Studio) was previously
  mislabeled REJECTED; it is RESEARCH, same species as Workstreams D/E, gated on an owner-and-use-case
  trigger, not a decision against scope.

---

## Traceability Statement

Every subject raised across this initiative is accounted for in the Full Traceability Matrix above — as an
active NOW/NEXT stage, a stated gating dependency with its own phase/stage home, or an explicit
LATER/RESEARCH disposition with its reason and prerequisite. Nothing is silently dropped; nothing beyond
Phase 2 is silently promoted to "planned in detail" without its prerequisite evidence existing first; and
nothing is labeled REJECTED merely for lacking evidence that could still arrive.
