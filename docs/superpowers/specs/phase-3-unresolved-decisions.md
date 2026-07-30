# Phase 3 Unresolved-Decision Register

**Status:** draft, companion to `phase-3-governed-sharepoint-knowledge-pilot-spec.md`. Not implementation-
ready. Every open item below is classified; none uses a bare "TBD".

Classification key: `BLOCKS_SPEC` (cannot finalize the spec without this) / `BLOCKS_PLAN` (spec can finalize
provisionally, but the implementation plan cannot be made task-ready) / `BLOCKS_EXECUTION` (plan can be
written, but no task touching this may run) / `MAY_DEFER` (safe to leave open through Phase 3) /
`PHASE_4_PLUS` (not Phase 3's decision to make at all).

## 1. Pilot site/library identity

- **Decision:** which SharePoint site and library is the Phase 3 pilot target.
- **Why it matters:** every downstream schema/reconciliation/upload step needs a real target.
- **Evidence needed:** Phase 3.0 Stage 3.0.1.1/3.0.1.2 output, plus a named non-production site.
- **Decision owner:** technical lead + tenant admin.
- **Latest responsible decision point:** before Subphase 3.1 (schema mapping) can be reconciled against
  real constraints.
- **Safe default if unresolved:** none — this blocks Phase 3 entirely. Classification: `BLOCKS_EXECUTION`
  (spec/plan may reference it as a placeholder; no upload/reconciliation task may run without it).

## 2. Direct-edit / republish policy (warn vs. block vs. silent overwrite)

- **Decision:** whether republish blocks on unexpected drift (recommended), warns only, or overwrites
  silently.
- **Why it matters:** determines whether the source-of-truth rule is actually enforceable or merely stated.
- **Evidence needed:** none required from the tenant — this is a design choice within this repo's control.
- **Decision owner:** user (design review).
- **Latest responsible decision point:** before Subphase 3.3 (reconciliation/republish) implementation
  begins.
- **Safe default if unresolved:** block (the spec's `RECOMMENDED` default) — blocking is the safer failure
  mode (no silent data loss) and can be relaxed to warn-only later if the pilot shows it's too strict.
  Classification: `BLOCKS_PLAN` — the plan scaffold's Subphase 3.3 tasks need this decided before task-level
  detail (exact block/disposition mechanism) can be written.

## 3. Unit of publication (all 25 / subset publication map / one assembled item)

- **Decision:** confirmed as all 25 rendered topics, one item per publication-map entry (Section 5 of the
  spec) — recommended, not yet user-confirmed as final.
- **Why it matters:** determines whether Stage 3.3.1's reconciliation requirement is actually satisfied.
- **Evidence needed:** none required from the tenant; user confirmation of the recommendation.
- **Decision owner:** user.
- **Latest responsible decision point:** before Subphase 3.2 (package-only deployment) task detail is
  written.
- **Safe default if unresolved:** proceed with all-25 (already the spec's recommendation) since it requires
  no new contract and directly satisfies the master plan's literal reconciliation requirement.
  Classification: `BLOCKS_PLAN`.

## 4. SharePoint-to-Git backflow (permanently excluded, or Phase 3-only boundary)

- **Decision:** confirmed as a Phase 3 implementation boundary (no backflow built in Phase 3), explicitly
  not framed as a permanent architectural rejection.
- **Why it matters:** avoids either quietly building an unscoped sync mechanism or quietly foreclosing a
  future editing model (`editing-workflow-options-for-external-review.md` Models C/E/hybrid).
- **Evidence needed:** none for Phase 3; Phase 3.0's experiment (per that document's "what Phase 3.0 should
  test" section) will inform whether a later phase builds this.
- **Decision owner:** user / initiative technical lead.
- **Latest responsible decision point:** already effectively decided for Phase 3's scope; revisit only if a
  later phase proposes backflow.
- **Safe default if unresolved:** no backflow in Phase 3 (current state). Classification: `MAY_DEFER`.

## 5. Separate `PublishedVersion` column vs. relying on native versioning + `TopicContentSHA256` + publication event

- **Decision:** whether a dedicated version column is needed at all.
- **Why it matters:** avoids adding a redundant field "because it seemed useful" (per the brainstorming
  correction).
- **Evidence needed:** Phase 3.0 Stage 3.0.2.4 (native versioning enabled?) and Stage 3.0.2.5 (system column
  availability).
- **Decision owner:** technical lead.
- **Latest responsible decision point:** before Subphase 3.1's schema is finalized for upload.
- **Safe default if unresolved:** do not add the column; rely on native version history + `TopicContentSHA256`
  + publication event fields (plus the `TransitionAction` transition record for genuine supersession, spec
  Section 7/13) until evidence shows a gap. Classification: `BLOCKS_PLAN`.

## 6. `Sensitivity`/records-classification column availability and pilot content selection

- **Decision:** which sensitivity/classification mechanism (tenant MIP label vs. custom choice column) is
  used, and whether the CEIS pilot content set needs narrowing to avoid genuinely Protected B content.
- **Why it matters:** a Protected B discoverability risk is a first-class governance concern per the master
  plan.
- **Evidence needed:** Phase 3.0 Stage 3.0.1.2 (available classification columns/labels).
- **Decision owner:** technical lead + pilot library owner (once named).
- **Latest responsible decision point:** before Subphase 3.2's manual upload (content selection must be
  finalized by then).
- **Safe default if unresolved:** select CEIS pilot content that avoids any topic plausibly classified above
  the tenant's lowest sensitivity tier, until this is resolved. Classification: `BLOCKS_EXECUTION` (upload
  may not proceed without this).

## 7. Structural-anchor representation (evidence package vs. SharePoint column)

- **Decision:** confirmed as evidence package/sidecar, not a SharePoint column (`NOT_MAPPED` in the field-
  authority matrix), since anchors aren't needed for item-level reconciliation.
- **Why it matters:** avoids inventing an unnecessary column.
- **Evidence needed:** none.
- **Decision owner:** technical lead (already decided in this spec revision).
- **Latest responsible decision point:** N/A — settled for this spec version, open to revisit if a
  reconciliation need surfaces.
- **Safe default if unresolved:** keep as evidence-package-only. Classification: `MAY_DEFER`.

## 8. Reviewer and publisher role assignment

- **Decision:** who specifically is the pilot's reviewer and publisher (Section 14 currently names both
  roles as not yet assigned).
- **Why it matters:** Stage 3.4.1's review workflow (Draft→Reviewed→Published, Model A per Section 14)
  needs named humans to walk through it.
- **Evidence needed:** Phase 3.0 Stage 3.0.2.3-adjacent (who can be authorized), plus a human decision.
- **Decision owner:** user / pilot library owner.
- **Latest responsible decision point:** before Subphase 3.4 (governance controls) task detail is written.
- **Safe default if unresolved (external review correction):** the same person (e.g. the technical lead)
  acting as both reviewer and publisher is allowed **only as an explicitly accepted pilot exception**,
  recorded here with the name and date it was accepted — not treated as this spec's normal governance
  default, since combining the two roles weakens the evidence for review governance. If accepted as an
  exception for the first pilot pass, record: exception accepted by ______, date ______, revisit trigger:
  once dedicated roles are assigned. Classification: `BLOCKS_PLAN`.

## 9. Two-identity oversharing test — which identities

- **Decision:** which two distinct permission identities are used for Stage 3.4.2's oversharing test.
- **Why it matters:** the test result is only meaningful if the two identities represent a genuine
  permission boundary the pilot library actually needs to enforce.
- **Evidence needed:** Phase 3.0 proposed addition (see evidence-consumption matrix) — not currently a named
  probe.
- **Decision owner:** technical lead + pilot library owner.
- **Latest responsible decision point:** before Subphase 3.4's permission test task is executed.
- **Safe default if unresolved:** cannot safely default — this is the entire point of the test.
  Classification: `BLOCKS_EXECUTION`.

## 10. `ActualLibraryState` provider implementation for manual-edit detection in reconciliation

- **Decision:** which concrete implementation backs the `ActualLibraryState` provider boundary (spec
  Section 12) — a manually prepared CSV/export, an approved read-only Graph/PnP API call, an approved
  administrative export, or another tenant-supported evidence source. This is an implementation-choice
  question, not an architectural one: the pure reconciliation comparator (Task 3.3.1) is designed against
  the abstract provider interface regardless of which implementation is eventually chosen (external review
  correction — an earlier revision of this item implied Graph/PnP specifically was the likely mechanism,
  which overstated what has actually been decided).
- **Why it matters:** determines whether "manual edits, if detectable" (Section 12) is actually achievable
  in Phase 3 or must be scoped down to "detectable only via periodic manual export."
- **Evidence needed:** Phase 3.0 Stage 3.0.2.1-adjacent / a specific reconciliation-identity permission
  check (proposed addition).
- **Decision owner:** technical lead.
- **Latest responsible decision point:** before Subphase 3.3's `ActualLibraryState` adapter (not the
  comparator itself) is implemented.
- **Safe default if unresolved:** scope reconciliation's manual-edit detection to whatever `ActualLibraryState`
  implementation is confirmed available; do not assume Graph/PnP write-adjacent read access exists.
  Classification: `BLOCKS_PLAN`.

## 11. `PublicationID` — resolved (Option A adopted)

- **Decision:** an earlier spec revision proposed a `PublicationID` field with no grounding in an actual
  Phase 2 contract field. This is resolved: Option A is adopted — `PackageIdentity`
  (`publication-map.package_identity`) is the sole current publication/package identity; no separate
  `PublicationID` is added (spec Section 7).
- **Why it matters:** prevents Phase 3 from silently inventing a contract field while claiming it doesn't
  modify or supplement Phase 2 contracts.
- **Evidence needed:** none — resolved by re-reading the actual Phase 2 contract.
- **Decision owner:** technical lead (resolved in this spec revision).
- **Latest responsible decision point:** N/A — settled.
- **Safe default if unresolved:** N/A — already resolved. Classification: `MAY_DEFER` (revisit only if a
  future need for a publication identity independent of package identity is concretely demonstrated —
  Option B in Section 7).

## 12. Rename vs. retirement vs. supersession — resolved (explicit transition record adopted)

- **Decision:** an earlier spec revision treated any topic ID missing from the current publication map as
  "renamed or retired," which cannot distinguish rename from retirement from deletion/corruption/map error.
  This is resolved: a human-confirmed transition record (`old_topic_id`, `action`, `new_topic_id`,
  `reason`, `decision_owner`, `effective_date`) is now required for any of these three events, and
  reconciliation classifies items into `ACTIVE_EXPECTED`/`RETIRED_EXPECTED`/`UNEXPECTED_ACTIVE`/
  `UNEXPECTED_RETIRED` rather than treating a missing ID alone as proof of any specific event (spec
  Sections 7, 12, 13).
- **Why it matters:** without this, every properly retired item would be reported as "unexpected" forever,
  and rename/retirement/supersession could not be distinguished for governance or evidence purposes.
- **Evidence needed:** none — a design/contract-level fix within this repo's control.
- **Decision owner:** technical lead (resolved in this spec revision).
- **Latest responsible decision point:** N/A — settled; the plan scaffold's Task 3.3.3–3.3.5 exercises
  produce the actual transition records once a pilot library exists.
- **Safe default if unresolved:** N/A — already resolved. Classification: `MAY_DEFER`.

## 13. Master-plan exit-gate correction

- **Decision:** whether to formally amend the master plan's Phase 3 exit-gate sentence to the corrected
  version proposed in the spec (Section 19).
- **Why it matters:** the current exit-gate sentence understates Subphase 3.3's actual required evidence.
- **Evidence needed:** none — this is an editorial/governance decision.
- **Decision owner:** user (this document's own authority; the master plan is not edited without separate
  authorization).
- **Latest responsible decision point:** whenever the user chooses to authorize the master-plan edit;
  not blocking for this spec, which already preserves the fuller Subphase 3.3 evidence regardless of the
  master plan's wording.
- **Safe default if unresolved:** this spec continues to require the fuller evidence set regardless of
  whether the master plan's sentence is ever amended. Classification: `MAY_DEFER`.

## 14. AgentAssets / native skills / SharePoint agents (Phase 4/5 scope)

- **Decision:** none required in Phase 3; explicitly out of scope.
- **Classification:** `PHASE_4_PLUS`.
