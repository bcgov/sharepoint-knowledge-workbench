# Phase 3 — Governed SharePoint Knowledge Pilot Specification

## 1. Status and authority

**This is a draft specification. No implementation is authorized.**

Authoritative source: `docs/vision/master-initiative-plan-workstreams-and-phases.md`, Phase 3 section
(and its Subphases 3.1–3.5). This document elaborates that section into an implementation-ready shape; it
does not supersede it, and any conflict is resolved in the master plan's favor.

Entry gates, both required before execution begins:
1. **Phase 2 exit gate** — met (509 passed/1 skipped, golden-master proof passed, merged to `main` — see
   `start-here.md`'s "Phase 2 ... complete" section). Verified against the repo, not assumed.
2. **Phase 3.0 exit gate** — **not yet met.** `tenant-capability-report.md` does not exist in this repo as
   of this writing. Phase 3.0 (SharePoint Tenant-Capability Discovery) has not been executed.

Every section below marked **[PROVISIONAL — Phase 3.0 pending]** contains a best-effort design that must be
reconciled against Phase 3.0's actual findings before it is implementation-ready. Where a concrete fact
(URL, library name, field type, identity, permission) cannot yet be known, this document uses an explicit
placeholder rather than inventing one. See `phase-3-tenant-evidence-consumption-matrix.md` for the full
mapping of which Phase 3.0 probe each provisional section depends on, and `phase-3-unresolved-decisions.md`
for every open decision with an owner and a safe default.

**Status markers used throughout this document:**
- `CONFIRMED` — already established by the master plan or accepted Phase 1/2 architecture; not open for
  re-litigation in this spec.
- `RECOMMENDED` — a proposal this document argues for, with alternatives compared, but not yet accepted by
  the user/design review.
- `PROVISIONAL` — a best-effort design that depends on a Phase 3.0 finding that does not exist yet.
- `DEFERRED_UNTIL_PHASE_3_0` — a specific fact this document deliberately does not invent.
- `BLOCKED` — cannot proceed at all until a named precondition is met.

## 2. Goal

> Publish hardened canonical content into one governed SharePoint knowledge library using package-only
> deployment by default, proving the metadata, source-of-truth, reconciliation, rollback, permission,
> review, and governance model without autonomous production writes.

Measurable outcome: one real, non-production-tenant SharePoint library populated with a pilot set of CEIS
canonical topics via a human-performed, package-only upload; the metadata schema, source-of-truth rule,
reconciliation report, and at least one deliberate republish/rollback/rename exercise are each demonstrated
against that real library, with evidence captured per Section 16.

## 3. Non-goals

Explicitly out of scope for Phase 3 (per master-plan Phase 4/5/6/7/8 and Stage-3.4.3 gating):

- AgentAssets integration (Phase 3.0 discovery only; no Phase 3 build).
- Native `SKILL.md` authoring on SharePoint (Phase 4).
- SharePoint knowledge agents / grounded retrieval (Phase 5).
- Copilot Cowork packaging, Copilot Studio integration (Phase 7).
- A general-purpose routing/orchestration agent.
- A new `sharepoint-knowledge` plugin, unless separately proposed and approved outside this spec.
- Autonomous SharePoint writes of any kind (all writes in Phase 3 are human-performed).
- Production write credentials, Entra app registrations, Microsoft Graph write scopes, or PnP automation
  for writing — Phase 3 is package-only by design (Subphase 3.4.3's authorized-write path is *design-only*
  and explicitly deferred).
- Repository renaming or restructuring beyond what Phase 3 itself needs.
- Records/retention/audit policy design (Phase 8, Subphase 8.4) — unless Phase 3 evidence surfaces a
  concrete requirement that must be pulled forward (per the master plan's own carve-out).
- Localization/multi-jurisdiction variants (deferred per `key-unanswered-questions.md` §12).
- Broad content reuse-by-reference across publications (deferred per `key-unanswered-questions.md` §6) —
  Phase 3's pilot content set is copied into the library as-is, one library, one deployment.

## 4. Preconditions

| Precondition | Source | Status |
|---|---|---|
| Hardened canonical/publication contract | Phase 2 exit gate | Met — `canonical-contract.md`/`publication-map-contract.md`, 509/1 suite, golden-master proof |
| Tenant access confirmed, licence ring known | Phase 3.0 Stage 3.0.1.1 | **Not met** |
| SharePoint surface inventory (site/library/column types) | Phase 3.0 Stage 3.0.1.2 | **Not met** |
| AgentAssets probe result | Phase 3.0 Stage 3.0.2.1 | Not applicable to Phase 3 build (informs later phases only) |
| Metadata field-type inventory for a pilot library | Phase 3.0 Stage 3.0.2.5 | **Not met** |
| Native Markdown rendering finding | Phase 3.0 Stage 3.0.2.4 | **Not met** |
| Pilot site/library identity, named owner | Human decision, post-3.0 | **Not decided** — see unresolved-decision register |
| Source-of-truth lifecycle rules documented | This spec, Section 8 | Drafted here; requires human review/sign-off before Subphase 3.2 pilots anything (per master plan Stage 3.1.4) |
| Package-only deployment confirmed feasible | Phase 3.0 exit gate | **Not met** — Phase 3's own entry gate |

## 5. Pilot scope

- **Pilot site:** `DEFERRED UNTIL PHASE 3.0 EVIDENCE: designated non-production pilot site URL/identity,
  confirmed by tenant admin (Stage 3.0.1.1)`.
- **Pilot library:** `DEFERRED UNTIL PHASE 3.0 EVIDENCE: pilot library name and location, created against
  Stage 3.0.2.5's authorized non-production test library`.
- **Pilot content set `RECOMMENDED`:** all 25 rendered topics of the CEIS publication
  (`runs/ceis-manual-v2/render/`), one SharePoint library item per `publication-map.json` entry —
  **not** a smaller subset. A subset was considered and rejected: master-plan Stage 3.3.1 requires
  "every publication-map entry checked against an actual library item," and the accepted CEIS publication
  map has all 25 entries. A 3–5-topic subset cannot satisfy that requirement without inventing a second,
  unaccepted subset-publication-map artifact — which is out of scope (see Non-goals: no new publication
  contract beyond Phase 2's). Twenty-five items is still small enough to be a bounded pilot, while proving
  the complete accepted publication relationship. See `phase-3-unresolved-decisions.md` for the full
  three-option comparison (all 25 / formal subset publication map / one assembled item).
  - **Execution prerequisite (external review correction):** "all 25 topics" and "avoid publishing any topic
    plausibly above the tenant's lowest sensitivity tier" (see the `Sensitivity` handling below and Section
    14) cannot both be true automatically — sensitivity screening must not be allowed to silently shrink the
    25-topic publication into an undocumented subset. The gate is: all 25 topics must be reviewed and
    approved for the pilot site's sensitivity and permission boundary before Stage 3.3's execution begins.
    If any topic cannot be approved as-is, Phase 3 does **not** silently proceed with a smaller,
    undocumented set — it either (a) re-gates Phase 3 execution until the blocking sensitivity concern is
    resolved tenant-side, or (b) defines a formal, separately reviewed pilot publication map that
    explicitly documents which topics are excluded and why (the same "formal subset publication map"
    option already named above, now invoked as a documented exception rather than a silent default).
- **User roles:** publisher (human, performs the manual upload), reviewer (approves content before
  publish), pilot library owner (tenant-side accountable owner, confirmed in Phase 3.0). See Section 14.
- **Supported deployment mode:** package-only. No other mode is in scope for Phase 3 build (Subphase 3.4.3
  authorized-write is design-only).
- **Environment restrictions:** non-production tenant surface only; no production knowledge library is
  touched during Phase 3.

## 6. Canonical input contract

Phase 3 consumes, unmodified, the Phase-2-hardened canonical package contract:

- `manifest.json` (`Manifest` — schema version per `MANIFEST_SCHEMA_VERSION`), specifically its
  `chunks[]` (`ManifestChunk`), `media`, `validation_report` (`ValidationReport`), `plan_id`.
- `publication-map.json` (grouped-strategy packages only — `package_identity`, `entries[].topic_id`,
  `.title`, `.order`, `.chunk_id`).
- Per-chunk sidecars (`ChunkMetadata`) — `chunk_id`, `topic`, `source_heading_path`, `content_sha256`,
  `local_links`, `media_refs`, `anchors` (structural-anchor list per the publication-map contract's "Where
  structural-anchor identity lives instead" section).
- `RenderResult`/rendered `multipage-markdown` output (`runs/ceis-manual-v2/render/`) as the human-readable
  content actually uploaded (SharePoint pilot content is rendered Markdown/media, not raw canonical JSON).

Phase 3 does not modify any of these contracts. If a Phase 3 need reveals a genuine contract gap, that is
raised as a new, separately-reviewed contract change — not implemented ad hoc inside Phase 3.

## 7. Target SharePoint schema **[PROVISIONAL — Phase 3.0 pending]**

Minimal intended mapping. Every "proposed SharePoint column"/"proposed field type" cell is provisional until
reconciled against Stage 3.0.2.5's observed field-type inventory (master-plan Stage 3.1.2). Each field is
classified per the field-authority matrix (`REQUIRED_FOR_PHASE_3` / `RECOMMENDED` / `TENANT_DEPENDENT` /
`DEFERRED` / `NOT_MAPPED`) rather than assumed to need a SharePoint column merely because it seemed useful.

**Correction (external review round):** an earlier revision of this table invented a `PublicationID` field
with no actual Phase 2 contract source, conflated the source-document fingerprint with the topic content
hash under one ambiguous `SourceContentSHA256` name, and implied the validator produces per-topic validation
results when it produces one package-level result. All three are corrected below.

| Business name | Class | Canonical source | Authority | Proposed column | Proposed type | Human or generated | Conflict rule | Phase 3.0 dependency | Omission consequence |
|---|---|---|---|---|---|---|---|---|---|
| Topic identity (`TopicID`) | REQUIRED_FOR_PHASE_3 | `publication-map.entries[].topic_id` | Canonical | `TopicID` | Single line text | Generated | Canonical wins | 3.0.2.5 | Reconciliation cannot match items at all |
| Chunk identity (`ChunkID`) | REQUIRED_FOR_PHASE_3 | `publication-map.entries[].chunk_id` | Canonical | `ChunkID` | Single line text | Generated | Canonical wins | 3.0.2.5 | Cannot detect which physical canonical artifact produced the item, independent of topic identity |
| Package identity | REQUIRED_FOR_PHASE_3 | `publication-map.package_identity` | Canonical | `PackageIdentity` | Single line text | Generated | Canonical wins | 3.0.2.5 | Cannot detect stale/mismatched content |
| Topic content hash | REQUIRED_FOR_PHASE_3 | `ChunkMetadata.content_sha256` | Canonical | `TopicContentSHA256` | Single line text | Generated | Canonical wins | 3.0.2.5 | Cannot detect topic-content drift — this is the actual drift-detection signal used in Section 12/13 |
| Source document fingerprint | RECOMMENDED (provenance only, not used for drift detection) | `ManifestSourceFingerprint.sha256` | Canonical | `SourceDocumentSHA256` | Single line text | Generated | Canonical wins | 3.0.2.5 | Loses traceability to the original DOCX, but does not affect reconciliation, which relies on `TopicContentSHA256` instead — may live in the evidence sidecar rather than a SharePoint column if the tenant column budget is tight |
| ~~Publication membership~~ *(removed — see below)* | — | — | — | — | — | — | — | — | — |
| Source package validation status | REQUIRED_FOR_PHASE_3 | `ValidationReport.status` (one status per canonical package, not per topic) | Generated validation evidence | `SourcePackageValidationStatus` | Choice (PASS/WARN/FAIL) | Generated | Canonical wins | 3.0.2.5 | Cannot enforce "only upload from a PASS-validated package" — see the corrected wording in Section 10 |
| Title | REQUIRED_FOR_PHASE_3 | `publication-map.entries[].title` | Canonical | `Title` | Single line text | Generated (human may propose pre-publish edits, not post) | Canonical wins | 3.0.2.5 | Item unusable to a reader |
| Publication order | REQUIRED_FOR_PHASE_3 | `publication-map.entries[].order` | Publication map | `PublicationOrder` | Number | Generated | Canonical wins | 3.0.2.5 | Cannot detect ordering drift |
| Owner | RECOMMENDED | Human decision | SharePoint operational governance | `Owner` | Person/Group | Human-maintained | SharePoint wins | 3.0.2.5 (person/group column availability) | Weaker governance only, not reconciliation-breaking |
| Status | RECOMMENDED | Section 14 workflow (Model A — see Section 14) | SharePoint operational governance | `Status` | Choice (Draft/Reviewed/Published/Retired) | Human-maintained | SharePoint wins | 3.0.2.5 | Cannot show Stage 3.4.1's review-workflow evidence |
| Review date | RECOMMENDED | Human decision | SharePoint operational governance | `ReviewDate` | Date | Human-maintained | SharePoint wins | 3.0.2.5 (date column type) | Minor — deferrable |
| Publication event (upload timestamp + publisher) | RECOMMENDED | Generated at upload | SharePoint operational governance | native system columns if available, else `PublishedAt`/`PublishedBy` | Date/Person or native | Generated at upload | SharePoint wins | 3.0.2.4 (native versioning/system columns) | Cannot distinguish two uploads of unchanged content; needed before deciding whether a separate version column is redundant |
| Structural anchor IDs | NOT_MAPPED | `ChunkMetadata.anchors[].stable_key` | Canonical | *(not a SharePoint column)* | — | — | — | — | None — not needed for item-level reconciliation; retained in the evidence package/sidecar (Section 16) instead |
| Sensitivity | TENANT_DEPENDENT | Human decision, not yet made | SharePoint operational governance | `Sensitivity` (or tenant MIP label) | Choice / sensitivity label | Human-maintained | SharePoint wins | 3.0.1.2 (available sensitivity/classification columns) | Gates the pilot content set — see Section 5's execution-prerequisite gate; does not block schema work |
| Retirement/transition record | REQUIRED_FOR_PHASE_3 (was `DEFERRED` `SupersededBy`) | Section 13 | Publication map / SharePoint operational governance | `TransitionAction` (RENAMED / RETIRED / SUPERSEDED), `TransitionTarget` (new `TopicID`, optional), `TransitionReason`, `TransitionDate` | Choice + text + text + date | Generated + human-confirmed | Canonical wins for "what replaced it"; SharePoint wins for "is this retired" | 3.0.2.5 (lookup/choice column availability) | Without this, Section 13/Section 12's retired-item handling cannot be exercised or evidenced (see Section 12's corrected retirement classes) |
| Separate `PublishedVersion` column | DEFERRED | Derived at upload time | — | *(not added pending evidence)* | — | — | — | 3.0.2.4 | Must first confirm native version history + `TopicContentSHA256` + publication event don't already cover this before adding a column |
| Records classification | DEFERRED | Not decided — Phase 8 default | Not represented in SharePoint (Phase 3) | — | — | — | — | Deferred to Phase 8 unless Phase 3 surfaces a concrete need |

**On the removed `PublicationID` field:** an earlier revision proposed a `PublicationID` field with "the
publication-map identity" as its canonical source, but no actual Phase 2 contract field supplies a value
distinct from `package_identity`. Three options were considered:
- *Option A (adopted):* use `PackageIdentity` (`publication-map.package_identity`) as the sole current
  publication/package identity; do not add a separate `PublicationID`.
- *Option B:* derive a publication-map fingerprint deterministically from the accepted publication-map
  contract, explicitly named as a Phase 3-derived value (not a Phase 2 contract field) — only pursued if a
  stable publication identity independent of package identity is genuinely required, which has not been
  demonstrated.
- *Option C:* propose a reviewed Phase 2 contract extension before Phase 3 — not pursued; Phase 3 does not
  modify Phase 2 contracts (Section 6).
Option A is adopted throughout this document; every prior reference to `PublicationID` below has been
replaced with `PackageIdentity` + `PublicationOrder` (publication membership is expressed as "this topic,
per `TopicID`, appears at this `PublicationOrder` within the package identified by `PackageIdentity`").

**`TopicID` vs. `ChunkID` (external review clarification):** `TopicID` is the logical topic's stable
identity — it must survive a republish of unchanged content and is the key reconciliation matches items on.
`ChunkID` is the physical canonical artifact identity (which chunk file actually produced this topic's
content) — it changes if the chunk-grouping/regeneration process produces a different physical artifact for
the same logical topic, which reconciliation can then read as "artifact replaced, topic unchanged." Phase 3
does not currently have a concrete scenario where these diverge (grouped-strategy topics are 1:1 with chunks
today per the publication-map contract), but both are captured as separate columns so that if Phase 2's
identity model diverges in the future, Phase 3's reconciliation is not silently relying on an ambiguous
composite of the two.

**Field-level authority principle (per Section B of the brainstorming input):** canonical package and
publication map are authoritative for *content identity and provenance* fields (topic ID, chunk ID, package
identity, topic content hash, source document fingerprint, title-as-authored, publication order).
SharePoint operational governance is authoritative for *operational/workflow* fields that have no canonical
equivalent (owner, status, review date, sensitivity as classified in the tenant, publication event). No
field is dual-authoritative; where a field could plausibly be either (e.g. title, if a reviewer edits it in
SharePoint), Section 8 states the rule explicitly rather than leaving it ambiguous.

## 8. Source-of-truth lifecycle

Answering master-plan Stage 3.1.4's explicit questions:

1. **Is manual editing of published SharePoint content prohibited, tolerated, or reconciled?**
   **Tolerated but flagged as drift, not silently accepted.** Phase 3 does not block a human from editing
   published content directly (SharePoint's own permission model governs that, not this pipeline), but any
   edit to a field whose authority is "canonical" (Section 7) is detected as drift by the reconciliation
   step (Section 12) and reported, never silently absorbed.
2. **What happens when someone edits published content directly — is that drift?**
   Yes, if the edited field's authority is canonical (content, title-as-authored, topic/publication
   identity). No, if the edited field's authority is SharePoint-operational (owner, status, review date,
   sensitivity) — those are expected to be edited in SharePoint.
3. **Must drift flow back into canonical content, or is it discarded on next republish?**
   **Discarded on next republish, for Phase 3.** Canonical-authority fields are always re-derived from the
   canonical package on republish; a SharePoint-side edit to a canonical-authority field does not flow back
   into the Git-tracked canonical content during Phase 3. This is an implementation boundary for Phase 3,
   not a permanent rejection of later authoring models (see
   `docs/vision/editing-workflow-options-for-external-review.md`'s Models C/E and its "three named
   repository skills" bridge, which explicitly keep this door open for a later phase). Flagged in the
   unresolved-decision register as a documented limitation, not silently assumed acceptable forever.
4. **How does republishing behave when manual edits exist (overwrite silently, warn, block)?**
   `RECOMMENDED`, not yet `CONFIRMED`: **block until reviewed, then require explicit human disposition**
   (authorize overwrite, or cancel the republish). Three policies were compared:
   - *A — warn and overwrite*: publisher is informed but can proceed without disposition; warnings risk
     being ignored.
   - *B — block until reviewed* (recommended): republish halts on unexpected drift in a canonical-authority
     field; a human must explicitly authorize overwrite or cancel. Makes the source-of-truth rule
     enforceable and produces a real disposition record as pilot evidence, not just a log line.
   - *C — silently overwrite*: conceals loss of any SharePoint-side change; no evidence trail; rejected.
   Blocking is the Phase 3 default recommendation; it does not halt Phase 3 itself (only that one
   republish action), and every block/disposition is captured as evidence per Section 16.
5. **Which repository/package/version is authoritative when canonical and published disagree?**
   **The canonical Git repository's confirmed package is authoritative for content**, per the source-
   of-truth rule below. SharePoint's published copy is a rendered, human-consumable projection of that
   package — never the other way around.
6. **How are superseded versions marked in the library?**
   A republished topic in place is not "superseded" — it is the same `TopicID` overwritten with new
   content (Section 13's safe-republish rule), and relies on SharePoint's native version history (confirmed
   available or not per Stage 3.0.2.4) for the byte-level prior content. Genuine supersession (a topic
   replaced by a *different* topic) is recorded via the `TransitionAction = SUPERSEDED` transition record
   (Section 7/13), not a same-item version marker. Phase 3 does not build a separate versioning store.

**One-paragraph source-of-truth rule (Stage 3.1.3):** The canonical package in this Git repository
(`runs/ceis-manual-v2/canonical-content/`, produced and validated by the `docx-to-content` plugin) is the
sole authoritative source for topic content, identity, and provenance. The SharePoint library is a governed,
rendered publication of that canonical content — never an independent editing surface for canonical-
authority fields. Where canonical and published disagree on a canonical-authority field, canonical wins,
always, without exception, for the duration of Phase 3.

**Editing-workflow relationship (informs, does not resolve, per master plan's own note):**
`docs/vision/editing-workflow-options-for-external-review.md` explores where business authors would
actually edit content long-term (candidate models A–G) and a supervised human-technical-publisher bridge.
Phase 3's answers above are the narrowest possible interim answer sufficient to run one pilot; they do not
foreclose adopting one of that document's candidate models in a later phase, once Phase 3.0/Phase 3
evidence exists to choose among them.

## 9. Package-only deployment contract

The package a human publisher receives, produced from a confirmed canonical package + publication map:

- **Content artifacts:** the rendered Markdown pages and media for the full 25-topic pilot publication
  (Section 5), sourced from `runs/ceis-manual-v2/render/`.
- **Metadata sidecar:** one record per topic mapping every Section 7 field to its value, keyed by
  `topic_id`, in a format the publisher can read (e.g. a CSV or JSON file — exact format `DEFERRED UNTIL
  PHASE 3.0 EVIDENCE: which format Stage 3.0.2.5's confirmed column types make easiest to bulk-populate,
  e.g. CSV for SharePoint list bulk-import vs. one-by-one manual entry`).
- **Target-library mapping:** which SharePoint library/columns each metadata field goes into (Section 7,
  reconciled).
- **Package and publication identities:** `package_identity`, `plan_id`, and each topic's `publication
  order` and `chunk_id`, so the publisher (and later reconciliation) can trace every uploaded item back to
  its exact canonical source.
- **Validation result:** the canonical package's `ValidationReport.status` (must be PASS before a package
  is offered for upload — WARN/FAIL packages are not eligible for Phase 3 pilot upload).
- **Upload instructions:** step-by-step manual instructions for the publisher (what to create, in what
  order, which fields to fill from the sidecar) — see Section 11.
- **Reconciliation instructions:** how to run the dry-run reconciliation check after upload (Section 12).
- **Rollback references:** which items to remove/restore and in what order if a rollback is needed
  (Section 13).

The package-only path has zero dependency on an Entra application registration, Microsoft Graph write
scope, PnP PowerShell/CLI automation, or any autonomous SharePoint write — every upload step is human-
performed through the SharePoint UI (or a human-run, read-only-to-the-tenant tool that only *prepares* the
package locally).

## 10. Dry-run validation

Before a human uploads anything, the package is validated locally (no tenant interaction). The complete
dry-run report cannot return `PASS` until every required check below has actually executed — a check that
cannot yet run must report `NOT_EVALUATED` or `BLOCKED`, never a silent passing no-op (external review
correction; see Section 15 and the plan scaffold's corrected Task 3.2.2):

- The source canonical package has accepted validation status `SourcePackageValidationStatus == PASS`
  (`ValidationReport.status` is a single, package-level result — not independently computed per topic —
  and each of the pilot publication's 25 topics belongs to that one validated package. This replaces an
  earlier, inaccurate statement that "every topic ... has `ValidationReport.status == PASS`," which implied
  per-topic validation that does not exist).
- Every Section 7 required field has a non-null value for every topic in the publication.
- Metadata sidecar field types are checked against the **reconciled** schema (Stage 3.1.2). This check
  cannot run meaningfully until Phase 3.0's field-type inventory exists; until then it reports
  `status = BLOCKED, issue = TARGET_SCHEMA_NOT_OBSERVED` — it is not scaffolded as a no-op that always
  passes, and its `BLOCKED` status prevents the overall dry-run report from returning `PASS`.
- No duplicate `TopicID`/`ChunkID` within the package being prepared.
- Media references in the pilot publication resolve to actual files present in the package (reusing
  the Phase 1/2 canonical validator's media-reference check logic where applicable, not reimplementing it).

## 11. Manual upload evidence

The human publisher records, for each upload session:
- Date/time, publisher identity, pilot library/site target.
- Which topics (by `TopicID`) were uploaded, in what order.
- Every manual step actually performed (not a generic checklist — the literal sequence of clicks/actions),
  per master-plan Stage 3.2.3's explicit intent that this log itself is evidence for later automation
  scoping.
- Any deviation from the upload instructions (Section 9) and why.
- Screenshot or export confirming each item exists in the library post-upload with its metadata populated.
  Per Section 16, the screenshot/export itself is controlled-original evidence, not committed verbatim to
  this repository; the tracked report records a sanitized summary and a pointer to the controlled location.

## 12. Reconciliation contract

Reconciliation identity is deliberately split into four distinct concepts, not one composite key (an
earlier draft conflated these into a composite key including an invented `PublicationID` field without
analyzing the semantics; see Section 7's correction):

- **Stable published-item identity** — which logical topic/item this is: `TopicID`, matching Section 7's
  `TopicID` column. Never changes across republish; only changes on a genuine rename (Section 13).
  `ChunkID` is tracked alongside it to detect physical-artifact replacement independent of topic identity
  (Section 7).
- **Expected-content identity** — which canonical content version should be present: `PackageIdentity` +
  `TopicContentSHA256` + `SourcePackageValidationStatus`. Changes whenever the canonical content actually
  changes.
- **Publication membership** — which publication map expects the item: `PackageIdentity` +
  `PublicationOrder` (there is no separate `PublicationID`; see Section 7). Changes if the publication
  map's composition or ordering changes, independent of content changes.
- **Publication event** — which human upload/republish operation produced the current SharePoint state:
  upload timestamp + publisher (Section 7's "publication event" row). Distinguishes two uploads of otherwise
  unchanged content, e.g. a deliberate re-upload for a pilot test. A separate `PublishedVersion` column is
  **not** added pending evidence that native version history + `TopicContentSHA256` + publication event
  don't already cover this need (Section 7).

Comparing expected (publication-map-derived) state against actual SharePoint state, using the above,
detecting:

- **Missing items** — a `publication-map` entry with no corresponding library item (matched on stable
  published-item identity).
- **Duplicate items** — more than one library item claiming the same stable published-item identity.
- **Stale items** — a library item whose expected-content identity no longer matches the current confirmed
  canonical package for that topic.
- **Item classification (external review correction — retirement must not become permanently
  "unexpected"):** every library item is classified into exactly one of four classes before "unexpected" is
  reported, so that a deliberately retired item is never flagged as unexpected forever:
  - `ACTIVE_EXPECTED` — matches a current publication-map entry.
  - `RETIRED_EXPECTED` — no current publication-map entry, but appears in the retirement ledger
    (Section 13's transition record, `TransitionAction = RETIRED` or `SUPERSEDED`) with this item as the
    old identity.
  - `UNEXPECTED_ACTIVE` — no current publication-map entry and no retirement-ledger record. This is the
    only class that constitutes an actual reconciliation problem requiring investigation.
  - `UNEXPECTED_RETIRED` — marked `Status = Retired` in SharePoint but with no corresponding
    retirement-ledger record explaining why (a governance gap even though it's not content-loss risk).
  Only `UNEXPECTED_ACTIVE` (and, at lower severity, `UNEXPECTED_RETIRED`) are reported as "unexpected items"
  in the reconciliation report; `RETIRED_EXPECTED` items are reported as expected retired state.
- **Mismatched package identity** — item's `PackageIdentity` present but does not match the expected value.
- **Mismatched publication identity** — item's `PackageIdentity`/`PublicationOrder` inconsistent with the
  current publication map.
- **Mismatched validation lineage** — item's `SourcePackageValidationStatus` does not match the canonical
  package's actual `ValidationReport.status` at time of upload.
- **Renamed, retired, or superseded topic IDs** — see Section 13's explicit transition record; a missing ID
  alone is never treated as proof of any specific one of these three events.
- **Manual edits, if detectable** — a canonical-authority field's value in SharePoint differs from the
  value the canonical package would produce, detectable only through the `ActualLibraryState` provider
  boundary (see below).

**`ActualLibraryState` provider boundary (external review correction):** the exact mechanism used to read
back current SharePoint item state is an implementation detail behind an abstract `ActualLibraryState`
provider interface, not a hard dependency on any specific tenant API. Possible implementations, none of
which change the pure reconciliation comparator's logic: a manually prepared CSV/export, an approved
read-only Graph/PnP API call, an approved administrative export, or another tenant-supported evidence
source. Which implementation is available is `DEFERRED UNTIL PHASE 3.0 EVIDENCE` (Stage 3.0's read-access
findings); the reconciliation comparator itself is designed against the provider interface, independent of
that choice.

Phase 3 explicitly does not treat "upload succeeded" as "publication succeeded" — the reconciliation report
is the actual proof of publication correctness, run after every upload/republish/rollback exercise, never
skipped.

## 13. Republish, rollback, rename, and retirement

- **Safe republish:** re-uploading the same stable published-item identity **overwrites the existing item's
  canonical-authority fields in place** (not append/duplicate) — **but only after the block-and-disposition
  policy in Section 8 answer 4 is satisfied**: if unexpected drift is detected on a canonical-authority
  field, republish halts until a human explicitly authorizes the overwrite or cancels. SharePoint's native
  version history (if confirmed available, Stage 3.0.2.4) preserves the prior copy; Phase 3 does not build a
  separate history mechanism.
- **Conflict handling:** if a canonical-authority field has drifted (Section 8) and the republish is
  blocked, the human publisher must record an explicit disposition (authorize or cancel) before it
  proceeds — SharePoint is never treated as more authoritative for that field class, per the source-of-truth
  rule, and the disposition itself becomes evidence (Section 16).
- **Rollback/unpublish:** removing a deliberately-bad pilot item is a manual deletion (or SharePoint's own
  "restore previous version" if version history is available), followed by a mandatory reconciliation run
  to confirm the library state matches the expected pre-bad-item state. Evidence: before/after inventory,
  the deletion/restore action log, and reviewer acceptance (Stage 3.3.4).
- **Rename, retirement, and supersession are distinct events, each requiring an explicit transition record
  (external review correction — a missing `TopicID` alone cannot prove which of these three occurred; it
  could equally indicate deletion, corruption, or a publication-map error):**
  - **Rename** — the old stable identity maps explicitly to a new stable identity; the underlying topic
    still exists and is still published, just under a new `TopicID`.
  - **Retirement** — the old identity has no replacement; the topic is deliberately withdrawn from the
    active publication.
  - **Supersession** — the old identity is replaced by a *different* topic for business reasons (not a
    pure rename of the same content).
  A `TopicID` disappearing from the current publication map is never, by itself, classified as one of
  these three without a human-confirmed transition record:
  ```text
  old_topic_id
  action = RENAMED | RETIRED | SUPERSEDED
  new_topic_id   (required if RENAMED or SUPERSEDED, absent if RETIRED)
  reason
  decision_owner
  effective_date
  ```
  This record is the retirement ledger referenced in Section 12's `RETIRED_EXPECTED` classification. Its
  item is retained in the library (not orphaned or deleted), marked `Status = Retired` and linked to
  `TransitionTarget` where applicable (Section 7), and the reconciliation report classifies it per Section
  12 rather than treating it as an error or a silent no-op.
- **Partial-upload recovery:** if a manual upload session is interrupted partway through the 25-topic pilot publication,
  the reconciliation report (run against whatever portion was actually uploaded) is the recovery mechanism —
  it surfaces exactly which publication-map entries are "missing" so the publisher knows what remains to be
  uploaded, rather than requiring the publisher to remember or guess.

## 14. Governance controls

- **Owner:** the pilot library's accountable owner, named in Phase 3.0 (Stage 3.0.2.3/3.0.2.5) — not yet
  named; see unresolved decisions.
- **Reviewer:** a human who approves pilot content before it moves to `Status: Reviewed` (see the corrected
  Draft → Reviewed → Published sequence below) — role holder not yet named.
- **Publisher:** the human who performs the manual upload — role holder not yet named. **Safe default
  (external review correction):** the same person may act as both reviewer and publisher only as an
  explicitly accepted pilot exception (recorded in `phase-3-unresolved-decisions.md`), not as this spec's
  normal governance default — a pilot of this size may operationally require it, but it weakens the
  evidence for review governance and must be named as such, not silently normalized.
- **Permissions:** tested under **at least two distinct permission identities** against the pilot library
  (Stage 3.4.2), to directly exercise oversharing/discoverability risk, not just assume the pilot library's
  default permission inheritance is correct.
- **Versioning:** relies on SharePoint's native version history if confirmed available (Stage 3.0.2.4);
  otherwise Phase 3 must fall back to `TopicContentSHA256` + the publication event columns + the
  `TransitionAction` transition record as the sole version signal (a materially weaker fallback, flagged in
  the unresolved-decision register).
- **Draft → Reviewed → Published states (external review correction — a SharePoint item cannot hold a
  SharePoint `Status` of `Draft` or `Reviewed` before it exists in SharePoint at all):** this spec adopts
  **Model A (SharePoint workflow)** rather than a package-preparation-time state model:
  1. The item is uploaded to the pilot library with `Status = Draft`.
  2. A reviewer reviews the item *in SharePoint* (not the pre-upload package).
  3. The reviewer marks it `Status = Reviewed`.
  4. Reconciliation runs (Section 12).
  5. Once reconciliation confirms correctness, the item is marked `Status = Published`.
  This sequence is walked through end-to-end for at least one real pilot item (Stage 3.4.1). The rejected
  alternative (Model B — package-level `Draft`/`Reviewed` status prior to any upload, then a single
  publish-on-upload step) does not satisfy Stage 3.4.1's requirement that a SharePoint item itself move
  through all three states.
- **Oversharing and discoverability checks:** run against the pilot library specifically, using the two
  distinct identities above, checking whether content is discoverable beyond its intended audience (Stage
  3.4.2) — a first-class Protected B concern per the master plan, not a checkbox.
- **Protected B considerations:** the pilot content set (Section 5) should be chosen, in part, to avoid any
  genuinely Protected B-classified CEIS content until sensitivity/classification handling (Section 7's
  `Sensitivity` field, reconciled against Stage 3.0.1.2's available classification columns) is confirmed
  workable — this is a scope-narrowing recommendation for topic selection, not a governance bypass.
- **Validation evidence:** every reconciliation, republish, rollback, and permission-test run produces the
  evidence artifacts named in Section 16; nothing is asserted "complete" from memory.
- **Named decision authorities:** the pilot library's accountable owner (Phase 3.0-named) is the decision
  owner for any "confirmed blocked" tenant-capability finding that affects Phase 3 scope; the initiative's
  technical lead is the decision owner for schema-mapping and reconciliation-behavior choices within this
  spec's already-stated bounds.

## 15. Error and partial-failure behaviour

No step in Phase 3 reports success without evidence:

- A dry-run validation failure (Section 10) blocks package preparation from proceeding to Section 11 — the
  publisher is told exactly which check failed and why, not just "validation failed."
- A reconciliation run that finds any issue category (Section 12) is reported in full, every issue listed,
  never summarized as "mostly fine."
- A partial manual upload (interrupted mid-session) is never silently treated as complete; the next
  reconciliation run is the explicit source of truth for what remains.
- A rollback/rename/retirement exercise that cannot complete cleanly (e.g. SharePoint permission denies a
  deletion) is recorded as a blocked exercise with the specific error, not retried silently or waved off.

## 16. Evidence model

Every stage in this spec produces a named evidence artifact. **Correction (external review round):** "this
path is tracked by Git" does not automatically mean it is an appropriate place for sensitive tenant
evidence — screenshots, identities, site URLs, permission-test results, and Protected B discoverability
evidence may not belong in this Git repository at all, tracked or not. Evidence is therefore split into two
tiers:

- **Tracked evidence index / sanitized summary** — stored under `docs/reports/phase-3-sharepoint-pilot/`
  (a tracked path, chosen after checking this repo's existing convention — `docs/reports/sdd-task-reports/`
  already exists for a similar purpose — and confirming neither `docs/reports/` nor `evidence/` are
  excluded by `.gitignore`, which ignores `.agents/`, `.claude/`, `context/`, `temp/`, `.superpowers/`, and
  cache directories, not documentation/evidence paths). Each entry in this tier records:
  - evidence ID;
  - sanitized finding (no raw identities, site URLs, tenant screenshots, or permission-test contents);
  - controlled-source location (a pointer, not the content itself);
  - access classification;
  - reviewer;
  - date;
  - an explicit note that the original is intentionally not committed to this repository.
- **Controlled original evidence** — the actual screenshots, exports, permission-test outputs, and any
  artifact containing real tenant identities, site URLs, or discoverability results, stored in an approved
  restricted, non-Git location named by Phase 3.0 (Stage 3.0.1's access-boundary findings) — never
  committed to this repository. Which specific restricted location is `DEFERRED UNTIL PHASE 3.0 EVIDENCE`.

Persistent Phase 3 evidence must not live only under an ignored path, and sensitive originals must not live
in this repository at all — both halves of this rule are correction targets fixed together, since fixing
only "make sure it's tracked" without also fixing "should tenant evidence live in Git at all" would have
been an incomplete correction.

| Evidence | Tier | Produced by | Section |
|---|---|---|---|
| Access record | Sanitized summary (tracked) | Phase 3.0 (external, referenced not owned by Phase 3) | 4 |
| Schema-mapping document | Sanitized summary (tracked) | Section 7's reconciliation | 7, 3.1.1/3.1.2 |
| `source-of-truth-lifecycle.md` | Sanitized summary (tracked) | Section 8 (may be split into its own file per Stage 3.1.4's naming) | 8 |
| Dry-run validation report | Sanitized summary (tracked) | Section 10 | 10, 3.2.2 |
| Upload log | Sanitized summary (tracked); underlying screenshots/exports are controlled originals | Section 11 | 11, 3.2.3 |
| Reconciliation report(s) | Sanitized summary (tracked) | Section 12, run at least once with zero autonomous writes | 12, 3.3.1/3.3.6 |
| Lineage trace record | Sanitized summary (tracked) | one real item traced to its source package | 12, 3.3.2 |
| Republish before/after record | Sanitized summary (tracked) | Section 13 | 13, 3.3.3 |
| Rollback before/after record + execution log + reviewer acceptance | Sanitized summary (tracked); raw execution log may be a controlled original if it contains tenant identities | Section 13 | 13, 3.3.4 |
| Rename/retirement before/after record | Sanitized summary (tracked) | Section 13 | 13, 3.3.5 |
| Review-workflow walked-through item history | Sanitized summary (tracked) | Section 14 | 14, 3.4.1 |
| Oversharing-test report | Sanitized summary (tracked); raw permission-test identities/results are controlled originals | Section 14 | 14, 3.4.2 |
| Write-identity design document | Sanitized summary (tracked) | 3.4.3, design-only | out of Phase 3 build scope |
| Readiness-check report | Sanitized summary (tracked) | Section 14/pilot content completeness | 3.5.1 |
| `phase-3-retrospective.md` | Sanitized summary (tracked) | citing every evidence artifact above | 3.5.2 |

## 17. Security and privacy boundaries

Package-only deployment is the default and, for Phase 3, the *only* build target — no autonomous write path
exists or is built. The pilot library is a designated non-production surface (never a production knowledge
library). Content selection (Section 5) deliberately avoids untested Protected B content until sensitivity
handling is confirmed. Any test artifact created during Phase 3.0-style probing that Phase 3 itself needs
(e.g. confirming a column accepts a value) follows the same staged, reversible, clearly-labeled convention
Phase 3.0 uses (name-prefixed `TEST-DO-NOT-USE-...`, removed after, evidence preserved instead).

## 18. Testing strategy

- **Repository unit and contract tests:** any new Phase 3 code (package-builder, dry-run validator,
  reconciliation comparator) gets unit tests under `plugins/docx-to-content/tests/` or a new Phase-3-scoped
  test location, following this repo's existing TDD convention — red test first, then implementation.
- **Dry-run validation:** exercised against the real pilot canonical package/publication map, offline, no
  tenant call.
- **Human-performed tenant tests:** the actual manual upload, republish, rollback, rename exercises — these
  are inherently human-performed and cannot be automated in Phase 3 (package-only, no write credential).
- **Multi-identity permission tests:** Stage 3.4.2's two-identity oversharing check, human-performed.
- **Deliberate reconciliation and rollback exercises:** at least one intentionally "bad" item is published
  and then rolled back, specifically to prove the rollback procedure works, not just to prove the happy
  path.

## 19. Exit criteria

**Confirmed contradiction with the master plan:** the master plan's literal Phase 3 exit-gate sentence
("reconciliation/rollback behavior demonstrated in dry-run") understates what Subphase 3.3 actually defines
and requires exercised: reconciliation, safe republish, rollback/unpublish, rename/retirement, and a
dry-run gate for any future authorized-write mode. This spec preserves the full Subphase 3.3 evidence
requirement rather than weakening Phase 3 to match the shorter exit-gate sentence. A correction to the
master plan's exit-gate wording is proposed below for separate authorization — **not edited in this spec
or session**.

**Proposed corrected exit gate (`RECOMMENDED`, not yet applied to the master plan):**

> One real governed library populated via package-only deployment of the complete 25-topic CEIS
> publication (one item per publication-map entry); metadata schema proven against actual tenant
> constraints; source-of-truth lifecycle rules documented and followed; a reconciliation report, a
> safe-republish exercise, a rollback/unpublish exercise, and a rename/retirement exercise are each
> demonstrated with recorded evidence; a dry-run reconciliation gate is proven functional before any future
> authorized-write mode is considered; oversharing controls tested under at least two distinct permission
> identities; retrospective documents real (not assumed) requirements for Phases 4–5, citing every piece of
> evidence above by reference.

**Binding criteria for this spec** (restating the master plan's exit gate as literally written, plus the
full Subphase 3.3 evidence this spec does not weaken):

- One real governed library populated via package-only deployment.
- Metadata schema proven against actual tenant constraints (Stage 3.1.2 reconciliation evidence exists).
- Source-of-truth lifecycle rules documented and followed (Section 8, exercised at least once).
- Reconciliation, safe-republish, rollback/unpublish, and rename/retirement each demonstrated with recorded
  evidence (Sections 12–13; Stages 3.3.1, 3.3.3, 3.3.4, 3.3.5) — not merely "reconciliation/rollback in
  dry-run."
- A dry-run reconciliation gate is proven functional (Stage 3.3.6) before any future authorized-write mode
  is considered.
- Oversharing controls tested under at least two distinct permission identities (Section 14).
- `phase-3-retrospective.md` documents real (not assumed) requirements for Phases 4–5, citing every
  evidence artifact in Section 16 by reference, not summarized from memory.

Every criterion above requires the cited evidence artifact to exist and be reviewable — a narrative claim of
completion without the artifact does not satisfy the exit gate.

## 20. Deferred capabilities

| Capability | Traced to |
|---|---|
| AgentAssets integration | Phase 3.0 (discovery only), Phase 4/5 (build) |
| Native `SKILL.md` authoring | Phase 4 |
| SharePoint knowledge agent / grounded retrieval | Phase 5 |
| Content-model expansion beyond current chunk/topic shape | Phase 5.5A |
| Renderer expansion (beyond `multipage-markdown`) | Phase 5.5B |
| Multi-runtime capability model | Phase 6 |
| Copilot Cowork / Copilot Studio evaluation | Phase 7 |
| Authorized-write (autonomous) SharePoint deployment | Phase 3 Subphase 3.4.3 design only; build gated behind an approved write identity, likely realized in a later phase |
| Records/retention/audit policy | Phase 8, Subphase 8.4 |
| Promotion/lifecycle management at scale | Phase 8, Subphases 8.1/8.3 |
| Bidirectional canonical↔SharePoint synchronization | Not currently planned in any phase; would require a dedicated design decision informed by `editing-workflow-options-for-external-review.md` |
| Localization/multi-jurisdiction variants | Not phase-assigned; `key-unanswered-questions.md` §12 |
| Broad reuse-by-reference across publications | Not phase-assigned; `key-unanswered-questions.md` §6 |
