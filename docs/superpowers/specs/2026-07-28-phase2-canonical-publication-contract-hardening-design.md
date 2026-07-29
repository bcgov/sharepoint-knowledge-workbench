# Phase 2 Design — Canonical/Publication Contract Hardening

**Status:** Revised after round 2 external review (Opus + GPT 5.6, `temp/plan-reviews/phase2/opus.md` and
`temp/plan-reviews/phase2/gpt5.6.md`), incorporating every finding both reviewers marked mandatory before
an implementation plan is written. Pending user approval before `writing-plans` is invoked.
**Depends on:** Phase 1 (`docx-to-content`) formal closure — see "Preconditions" below; this design assumes
Phase 1 will be closed before Phase 2 implementation starts, not before Phase 2 is *planned*.
**Supersedes nothing.** This is the first Phase 2 design document; the broader roadmap in
`docs/vision/ai-assisted-structured-knowledge-workbench-broader-plan.md` proposes Phase 2 at a high level
("Publication and Renderer Separation" as a new `knowledge-publication` plugin) — this design deliberately
narrows and re-scopes that proposal based on two rounds of independent adversarial review (round 1:
`temp/plan-reviews/opus.md`, `temp/plan-reviews/gpt5.6.md`; round 2:
`temp/plan-reviews/phase2/opus.md`, `temp/plan-reviews/phase2/gpt5.6.md`) plus direct code verification in
this session. It does not authorize the plugin extraction the vision doc originally proposed for Phase 2.

## 1. Why This Design Differs From the Vision Doc

The vision doc's Phase 2 goal ("establish canonical content as independent of the original DOCX converter")
is correct. Its implied mechanism — extracting a `knowledge-publication` plugin — is premature: no second
producer of canonical content and no independent consumer of publication output exists yet. Both external
reviews and this session's own architecture review agree: **do Phase 2 as internal contract-hardening
inside the existing plugin, not a plugin extraction.** Extraction becomes justified later, behind an
explicit trigger (see Section 7).

The deeper finding driving this design is not organizational — it is a real defect class found in Phase 1.
The `image239` media-reference bug survived undetected through canonical **and** rendered validation
because both validators reported PASS without ever examining the actual broken reference (a regex silently
failed to recognize it as media at all). The lesson: **a validator can pass by not looking.** Nothing in
the current design measures a validator's actual coverage, only its verdict. Phase 2 must fix this
directly, not just re-document the existing contracts as stable.

## 2. Preconditions

- Phase 1 must be **formally closed** (human spot-check checklist completed, evidence report finalized)
  before Phase 2's golden-master baseline is captured — capturing "byte-identical to current output" before
  human acceptance risks enshrining an unaccepted result as the reference. Phase 2 *design and planning*
  can proceed in parallel with the outstanding spot-check; Phase 2 *implementation* of the golden-master
  comparison step should not start until Phase 1 is closed.
- No repository rename, no new plugin, no new agent — all deferred per both reviews' convergent
  recommendation, unchanged from the round-1 architecture review.

## 3. Goal

Make the existing canonical-package-to-publication boundary **explicit, independently testable, provably
free of DOCX-runtime dependencies, and provably validated** (not merely "validated" by validators whose
actual coverage has never been tested).

## 4. Non-Goals (Explicit — Do Not Implement)

- Repository rename or restructuring.
- Extracting `knowledge-publication`, `sharepoint-knowledge`, or `knowledge-evaluation` as separate plugins.
- New renderer output formats (PDF, Word, PowerPoint, HTML) — `multipage-markdown` remains the only renderer.
- Any SharePoint-facing code, schema, or integration.
- New agents of any kind.
- A generic template engine, semantic remapping, or canonical-authoring UI (already explicitly out of scope
  per the Phase 1 spec's Task 15a and still out of scope here).
- A multi-target capability catalogue (vision doc Phase 6) — not relevant until a second runtime exists.
- Declaring the current contract shape a frozen, backward-compatible "v1." Nothing external depends on it
  yet; freezing now would manufacture premature-commitment cost. This design **stabilizes and corrects**
  the contracts instead — see Section 5.2.
- Adding "future flexibility" fields with no current consumer. This rule applies retroactively to
  `PublicationMapEntry.parent_topic_id` (see Section 5.2) — it is removed, not preserved, unless the
  implementation planner finds the current CEIS output actually needs nested topic relationships (it does
  not, per this session's inspection: the real `publication-map.json` has 25 flat entries, no nesting).
- Building multi-version *migration/adapter* machinery (version ranges, compatibility shims) for the
  schema-version split in Section 5.2 — only distinct per-contract version constants and single-version
  checks are in scope, not a general versioning framework.

## 5. In Scope

### 5.1 Adversarial/Mutation Test Suite Against the Validators (headline deliverable)

Per Opus's round-1 review: a hand-authored clean fixture proves a consumer reads the public shape; it does
not prove a validator can actually catch corruption, because a clean fixture has no adversarial content.
Build a test suite that takes a known-good canonical package and, for each targeted mutation, corrupts it
and asserts the **specific expected layer and detector** rejects it — not just "some failure occurred."

**Three validation layers, per GPT 5.6's round-2 finding — a mutation must name which layer(s) it targets:**

1. **Pre-promotion canonical validation** — `validate_canonical_package()` (`validate_canonical.py`).
2. **Post-promotion package acceptance/loading** — `CanonicalPackage.load()` (`package.py`). Per both
   reviewers' round-2 findings, this is itself a validator (schema loading, content-hash verification,
   media existence, warning-disposition handling) and was wrongly omitted from round 1's target list. The
   tamper-after-promotion path runs through `load()`; it must be mutated against explicitly.
3. **Rendered-output validation** — `validate_rendered_output()` (`renderers/validate_rendered.py`).

**Mutation matrix — every case below must record: artifact mutated, field mutated, validator/loader layer
expected to reject it, expected issue code or exception, and whether promotion/loading must be blocked
(the implementation plan turns this into an actual table, not prose):**

Media/reference corruption (layers 1-3 as noted):
- Delete a media file referenced by a chunk, both pre-promotion (layer 1) and post-promotion (layer 2) —
  reproduces the actual `image239` failure mode at both points it could have been caught.
- Rewrite a relative media reference to an absolute path (layer 1).
- Inject alt text containing a markdown-escaped `]` into a media reference NOT already covered by the
  existing regression test (`tests/unit/test_package.py`'s
  `test_alt_text_with_escaped_brackets_still_recognized_as_media_ref`) — confirm the class of bug is
  closed at the validator level, not just the copy/rewrite level (layer 1).
- Duplicate-name/different-content media collision path (the `-<shorthash>` dedupe rewrite) — confirm it's
  actually exercised, not just theoretically supported (layer 1).
- Orphan media file present on disk but referenced by no chunk (`_check_orphans`) (layer 1).
- Media file present in manifest but absent on disk, and the inverse: file on disk but absent from
  manifest (layers 1-2).
- Encoded path traversal (`%2e%2e`) and a Windows-style absolute/UNC reference as a media ref (layer 1).

Cross-artifact lineage/identity mismatch (layer 1 and/or 2 as noted — GPT 5.6's precise matrix, replacing
round 1's vague "corrupt a recorded content hash / plan_id / source_sha256"):
- Manifest `plan_id` differs from the confirmed plan's `plan_id` (layer 1).
- Chunk-sidecar `plan_id` differs from the manifest's `plan_id` (layer 1 — not currently checked per this
  session's code read; confirm during implementation whether this is a real gap or already covered).
- Chunk-sidecar `source_sha256` differs from the manifest's recorded source hash (layer 1, same caveat).
- Validation-report `plan_id`/`source_sha256` differ from the manifest (layer 1).
- Render-result package/manifest identity differs from the loaded package (layer 3).
- Chunk metadata's content path differs from its manifest-declared content path (layers 1-2).
- Chunk metadata ID differs from its manifest-declared chunk ID (layers 1-2).
- Duplicate manifest chunk path (layer 1).

Publication-map corruption (layer 1, and layer 2 via `CanonicalPackage.load()`):
- Remove a `publication-map.json` entry that a chunk's `source_order` implies should exist.
- Duplicate a `publication-map.json` entry (same `topic_id` twice).
- Break ordering contiguity (gap or duplicate `order` value).
- Reference an unknown/nonexistent chunk from an entry.
- Publication-map identity mismatches the canonical package's own identity.
- Missing publication map for a `"grouped"`-strategy package (must be a hard FAIL, not the current silent
  `None` — see Section 5.2).
- An *unexpected* publication map present for a `"single"`/`"chunked"`-strategy package — Section 5.2
  requires an explicit accept/reject policy decision for this case; whichever is chosen, add the test.

Malformed-contract mutations (new category per GPT 5.6's round-2 finding — the included code does not
visibly show `_check_publication_map_consistency()` catching a load failure, i.e. a malformed file may
raise rather than return a controlled validation issue):
- Malformed JSON in `publication-map.json` (and, for symmetry, a malformed `manifest.json`/chunk sidecar).
- Missing required field in any of the above.
- Unsupported publication-map schema version.
- Wrong field type (e.g. `order` as a string).
- Empty `entries` list for a non-empty grouped manifest.
- An extra/unknown field, with an explicit decision on whether strict unknown-field rejection is intended.
Every case here must assert a controlled validation issue is raised, not an uncaught exception.

**The content-comparison-skip loophole (Opus round-2 Finding C.1, the sharpest addition, "the purest
`image239` lesson in the codebase"):** `validate_canonical._check_content_loss_and_duplication` returns a
**WARN** (`content_comparison_skipped`) when `cleaned_markdown_text` is `None`, and `CanonicalPackage.load()`
accepts a WARN once dispositioned. This means the single most important semantic check — did we lose or
duplicate body text — can be skipped and dispositioned away, and the package still loads and renders.
**Decision (GPT 5.6's recommendation, adopted):** a producer-generated canonical package cannot be
promoted as fully accepted unless the aggregate content comparison actually ran and passed; a hand-authored
independent fixture (Section 5.3) may use a distinct provenance/validation profile, since no source
conversion exists for it to compare against. Add a mutation asserting a producer-path package whose content
comparison was skipped cannot be silently treated as equivalent to one where it ran and passed.

Rendered-output specific (layer 3):
- Rendered index omits a page that still exists on disk.
- Rendered page exists but the index link points elsewhere.
- Renderer claims support for the wrong manifest version.
- A validation report claims PASS but its lineage fields don't actually match the package (a "the verdict
  lies about what it checked" case — the general form of the `image239` lesson).

Until a validator/loader has been demonstrated to fail on a specific, deliberately introduced defect at the
specific layer that should catch it, its PASS carries no evidentiary weight for that defect class. This
suite, plus the exit-evidence requirement in Section 8 that every mutation reach its intended detector, is
what makes future PASS results trustworthy.

### 5.2 Contract Stabilization (Not Freezing)

Confirmed by direct code inspection this session, and decided (not left open) after round-2 review:

- **Schema versioning — narrow split, no migration machinery (GPT 5.6's round-2 proposal, adopted as the
  decision, resolving the round-2 disagreement between the two reviewers).** `contracts.
  SUPPORTED_SCHEMA_VERSION = "1.0"` currently governs `ConversionPlan`, `ChunkMetadata`, `Manifest`, and
  `PublicationMap` as if they evolve together. **Decision:** introduce separately named current-version
  constants — `CONVERSION_PLAN_SCHEMA_VERSION`, `MANIFEST_SCHEMA_VERSION`, `CHUNK_METADATA_SCHEMA_VERSION`,
  `PUBLICATION_MAP_SCHEMA_VERSION` — each with its own version-check, each supporting **exactly one**
  version. Do **not** implement adapters, migration logic, version ranges, or backward-compatibility
  machinery (Opus's round-2 objection to full multi-version handling stands — there is still no second
  version and no external consumer). This removes the accidental coupling now without building speculative
  infrastructure.
- **Fix the `package_identity` double-prefix bug.** Confirmed in `package.py`:
  ```python
  pub_map = publication_map.build_publication_map(
      boundaries, topic_chunk_ids, package_identity=f"sha256:{manifest.plan_id}"
  )
  ```
  `manifest.plan_id` is already `sha256:`-prefixed (`hashing.compute_plan_id`), producing
  `"sha256:sha256:<hash>"` — confirmed present in the real CEIS run's `publication-map.json`. Fix: use
  `manifest.plan_id` directly, or make the prefixing logic in `hashing.py` idempotent, and add a
  regression test. **This intentionally changes the byte content of `publication-map.json`** — see the
  golden-master comparison-surface split in Section 5.5, which exists specifically because of this.
- **Resolve `PublicationMapEntry.chunk_id` decisively (GPT 5.6's round-2 recommendation, adopted as the
  decision — not left as three options for the implementation planner to choose among).**
  `topic_id` identifies the publication topic; `chunk_id` identifies the canonical chunk that topic
  consumes — two separate concepts, even though the current grouped producer happens to make them
  equal-in-practice today. Concretely:
  - `content_file` (the path) stays in canonical chunk metadata/manifest — it must not be smuggled through
    `chunk_id`, which is what happens today.
  - `chunk_id` is populated with the actual logical chunk identifier (`chunk.metadata.chunk_id`'s value),
    not a path.
  - The renderer resolves each publication entry via `entry.chunk_id` (not `entry.topic_id`, which is
    today's behavior) against the canonical package's chunks.
  - Validation proves every `chunk_id` resolves to exactly one canonical chunk, and every chunk required by
    the manifest appears exactly once across all publication-map entries.
  - **This is an intentional, tested behavior change to the renderer's resolution logic**, not a
    documentation-only fix — flag it explicitly in the implementation plan and in the "tests that must
    change" accounting (Section 7), not silently absorbed into "the suite still passes."
- **Remove `PublicationMapEntry.parent_topic_id`** (GPT 5.6's round-2 finding 6, adopted): it is optional,
  unvalidated, and unconsumed by the renderer — the exact "future flexibility field with no current
  consumer" the non-goals (Section 4) already prohibit. The real CEIS `publication-map.json` has 25 flat
  entries with no nesting; there is no current need. Remove it rather than half-implement hierarchy
  validation for a feature nothing uses yet.
- **Disambiguate identity/hash naming.** `RenderResult.source_manifest_hash` is populated from
  `package.manifest.source.sha256` — the source **DOCX** fingerprint, not a hash of `manifest.json`. The
  validator's check is named `manifest_hash_mismatch`, which is misleading (it's actually a
  source-staleness check). Introduce clearly distinct names: `source_content_sha256`, `manifest_sha256`
  (an actual hash of the manifest content, if one is needed), `package_identity`, `plan_id`. Rename the
  validator check accordingly. **This intentionally changes `render-result.json`'s field name** — same
  comparison-surface consequence as the `package_identity` fix, see Section 5.5.
- **Make publication-map requirements explicit per strategy, with an explicit policy for the inverse
  case too (GPT 5.6's round-2 addition).** `CanonicalPackage.publication_map` defaults to `None`, and
  `load_publication_map()` silently returns `None` if the file is missing. Decide and enforce, with a test
  for each:
  - A `"grouped"`-strategy package **requires** a publication map — missing one is a validation FAIL, not
    a silent `None`.
  - A `"single"`/`"chunked"`-strategy package legitimately has none — expected, not an error.
  - An *unexpected* publication map present on a `"single"`/`"chunked"` package — pick one explicit policy
    (ignore it, or reject it as inconsistent state) and test it; "silently ignored" is itself a
    validator-does-not-look risk per this phase's own theme, so lean toward rejecting rather than ignoring
    unless a concrete reason to allow it surfaces during implementation.
- **Audit remaining optionality.** `confirmed_topic_roots` and `media_decisions` being optional (for
  non-grouped/no-preamble-media plans) is legitimate — document why. `ChunkMetadata.anchors` being
  optional needs the same treatment: is it legitimately optional for `"single"`/`"chunked"` chunks, or is
  it a gap? Resolve and document, don't leave ambiguous.

### 5.3 Independent Canonical Fixture

Build a small, hand-authored canonical-content package (chunks, media, manifest, publication map) that was
**never produced by running the real DOCX pipeline** — constructed directly to match the documented
contract shape. Use it to prove the renderer and validators depend on the *documented* public shape, not
on incidental behavior of the current producer. This is necessary but, per Opus, insufficient alone — pair
it with Section 5.1's mutation suite, which is the stronger proof.

### 5.4 Runtime-Independence Proof

**Both reviewers independently found the same hole in round 1's version of this section (Opus Finding B,
GPT 5.6 item 2): a direct/textual import check on `renderers/` alone is too shallow.**
`renderers/protocol.py` imports `CanonicalPackage` from `package.py`, and `package.py` itself imports
`topic_grouping` and calls `compute_topic_boundaries` inside `build_grouped_canonical_package` — a
producer/analysis concern. A check that only inspects `renderers/`'s own import statements would pass
while the renderer's dependency chain still transitively pulls in topic-grouping — exactly the "green
check that isn't looking in the right place" failure mode this whole phase exists to close.

**Decision (GPT 5.6's round-2 recommendation, adopted):** this requires an actual internal module split,
not just a smarter test:
- Extract the read-only package consumer (today's `CanonicalPackage.load()` and related loading logic)
  out of `package.py` into a new, narrowly scoped internal module (working name: `canonical_package.py`).
- Leave the package-*building* functions (`build_canonical_package`, `build_grouped_canonical_package`, and
  anything that depends on `topic_grouping`) in `package.py`.
- The renderer side is permitted to import: contract definitions (`contracts.py`), hashing/identity
  primitives, disposition-check logic needed for package acceptance, and the new read-only
  `canonical_package.py` loader. It is explicitly prohibited from importing anything from
  `package.py`'s builder functions or from `analyze_structure`, `pandoc_fixes`, `convert`, `plans`,
  `chunking`, `emf_convert`, or `topic_grouping`.
- **This is an internal module split, not plugin extraction or repository restructuring** — both reviewers
  agree it does not violate Section 4's non-goals, since nothing here moves across a plugin boundary or
  changes the repo layout at the top level.
- Test the **transitive** import graph, not only each module's direct import statements — a static check
  that walks the full dependency closure of `renderers/` and confirms no forbidden module appears anywhere
  in it, not just at the top level.
- Render from a canonical package with the source `.docx`, `intake/`, and `temp/` analysis artifacts
  entirely absent from the filesystem (not just unused — physically inaccessible in the test environment),
  as a behavioral complement to the structural import-graph proof above.

### 5.5 Golden-Master Comparison (Deferred Until Phase 1 Closes) — Split Into Two Surfaces

**Both reviewers independently found the same internal contradiction in round 1 (Opus Finding A, GPT 5.6
item 1): Section 5.2 requires fixing the `package_identity` double-prefix and renaming
`source_manifest_hash` — and the accepted Phase 1 output *contains* both of those bugs (the real
`publication-map.json` has the double-prefixed identity; `render-result.json` carries the old field name).
The moment either bug is fixed and output is regenerated, it is provably not byte-identical to the
accepted master. As written, Section 5.2 guaranteed this section would fail. Resolved by splitting the
comparison into two explicit surfaces (GPT 5.6's proposal, adopted):**

**1. Publication-content golden master — byte-identical comparison, no exceptions:**
- `index.md`
- `pages/**`
- `media/**`

**2. Control-metadata comparison — semantic assertions, not byte comparison, since Section 5.2 intentionally
changes these:**
- `render-result.json`
- `renderer-validation.json` (and the canonical-side `validation.json`)
- generator metadata
- manifest/package/publication identity fields (`plan_id`, `package_identity`, the renamed
  `source_content_sha256`, etc.)

Semantic assertions for surface 2 mean: the *meaning* is verified to be correct (e.g., the identity value
correctly identifies the same source/plan, once double-prefixing is fixed and the field is correctly
named) — not that the bytes match the old, buggy values.

This is preferred over re-baselining everything after implementation (which was round 1's implicit
fallback) specifically because re-baselining blindly risks Phase 2 accidentally changing user-visible
rendered content and simply declaring the new output the new baseline without anyone noticing the
difference was more than metadata.

**Sequencing (unchanged from round 1, confirmed correct by both reviewers in round 2):**
- Once Phase 1's human spot-check is complete and the evidence report is finalized, capture
  `runs/ceis-manual-v2/render/rendered-output/` as the accepted golden master for surface 1 above.
- An earlier, explicitly non-authoritative diagnostic comparison against the *current* (not yet accepted)
  output may optionally be run to catch nondeterminism early — it must never be treated as the baseline,
  and is not a required deliverable unless nondeterminism is already suspected.

### 5.6 Document Extraction Triggers

Write down, in `references/` or a decision doc, the explicit conditions under which `knowledge-publication`
(or `sharepoint-knowledge`, `knowledge-evaluation`) would become a real plugin-extraction candidate — e.g.
"an independently invoked consumer, a second canonical-content producer, a distinct release cadence, or a
separate ownership/security boundary requires it." This is documentation only; it authorizes nothing by
itself.

## 6. Likely Files Touched

Primarily:
- `scripts/contracts.py` (schema-version split, field semantics/naming, `parent_topic_id` removal)
- `scripts/hashing.py` (make `compute_plan_id`'s prefixing idempotent — this is where the double-prefix
  fix must actually land per Section 5.2; round-1 omitted this file)
- `scripts/package.py` (identity bug fix, `chunk_id` resolution; package-*building* functions remain here
  per the module split in Section 5.4)
- New: `scripts/canonical_package.py` (the extracted read-only package-loading module — see Section 5.4)
- `scripts/publication_map.py` (identity bug fix, strategy-conditional requirement enforcement)
- `scripts/renderers/protocol.py`, `renderers/multipage_markdown.py`, `renderers/validate_rendered.py`
  (naming fixes, transitive import-boundary provability, `chunk_id`-based resolution)
- `scripts/validate_canonical.py` (mutation-test target across all three layers, publication-map
  requirement enforcement, content-comparison-skip decision enforcement)
- `scripts/path_safety.py` — if encoded-traversal (`%2e%2e`) and Windows-style path rejection policies from
  Section 5.1's mutation matrix are consolidated here
- CLI-facing tests — if renamed result fields (`source_manifest_hash` → `source_content_sha256`) affect any
  serialized output the CLI tests assert against
- New: a mutation-test module/fixture set (exact location TBD in the implementation plan)
- New: an independent hand-authored canonical fixture (exact location TBD in the implementation plan)
- Focused unit/contract/integration tests throughout
- `references/` — extraction-trigger documentation, contract/version documentation updates
- Existing real-run artifacts under `runs/ceis-manual-v2/` — touched only through an explicit, documented
  regeneration decision once the identity/naming fixes land, not silently overwritten

## 7. Testing Plan

- TDD throughout, per this repo's standing rule: write each failing mutation/contract test before the
  corresponding fix.
- **Full existing suite (449 passed/1 skipped as of this session) must continue passing, with intentional
  exceptions explicitly called out** (Opus round-2 Finding E): Section 5.2's identity-value fix, field
  rename, and `chunk_id`-resolution behavior change **will** turn some existing tests red on purpose. The
  implementation plan must enumerate which tests are expected to change and why, so a reviewer can tell
  "expected, intentional change" apart from "regression" — do not treat every red test as a bug to silently
  work around, and do not treat "some tests changed" as evidence something went wrong.
- New tests: the mutation suite across all three validation layers (Section 5.1), the independent-fixture
  tests (Section 5.3), the transitive import-boundary test and the module-split tests (Section 5.4), and
  per-bug regression tests for the confirmed identity bugs and the `chunk_id` resolution change (Section
  5.2).
- No CEIS-specific literal strings in new generalization tests, consistent with the Phase 1 spec's
  Section 11 rule.

## 8. Exit Evidence

Phase 2 is done when, with evidence (not narrative):
- A mutation coverage matrix exists (artifact, field, layer, expected detector/issue code, promotion
  outcome for every case in Section 5.1) and every case demonstrates the targeted layer's
  validator/loader actually failing on the targeted corruption — not just "some failure occurred."
- No uncaught exception results from any malformed-contract mutation (Section 5.1) — every one produces a
  controlled validation issue.
- The content-comparison-skip loophole is closed: a producer-path package whose content comparison was
  skipped cannot be promoted as fully accepted (Section 5.1's decision is enforced and tested).
- The two confirmed identity bugs (`package_identity` double-prefix, `source_manifest_hash` naming) are
  fixed with passing regression tests.
- `chunk_id` has the decided semantics (Section 5.2: real logical-chunk-ID value, not a path; renderer
  resolves via `entry.chunk_id`) with a passing test proving every `chunk_id` resolves exactly once and
  every required chunk appears exactly once. `parent_topic_id` is removed.
- Schema-version constants are split per contract type (Section 5.2) with no migration/adapter machinery
  added.
- Publication-map requirement-by-strategy is enforced and tested for all three cases: required-and-missing
  → FAIL, not-required-and-absent → fine, and not-required-but-present → the explicitly decided policy.
- The package-loader module split (Section 5.4) is complete: `canonical_package.py` exists as the read-only
  consumer module, `package.py` retains only builder functions, and a **transitive** import-graph test
  (not just direct imports) proves `renderers/` never reaches a forbidden producer/analysis module.
- The independent canonical fixture renders successfully through the existing renderer with no DOCX-side
  code invoked, using a validation profile appropriate to a fixture that was never DOCX-converted (Section
  5.1's content-comparison-skip decision).
- **Golden-master comparison passes on both defined surfaces** (Section 5.5): byte-identical for
  publication content (`index.md`, `pages/**`, `media/**`), and semantically correct (not byte-identical)
  for control metadata — captured after Phase 1's formal closure, not before.
- Every intentionally-changed pre-existing test is explicitly accounted for (Section 7) — not silently
  absorbed into a pass/fail count.
- No unexplained changes to accepted CEIS pages or media — only the documented, intentional metadata
  changes.
- Full test suite passes; exact pass/fail counts reported, not claimed.

## 9. Explicit Approval Gate

This design does not authorize implementation. It has now been through two rounds of external review
(Opus, GPT 5.6 — round 1: `temp/plan-reviews/opus.md`, `temp/plan-reviews/gpt5.6.md`; round 2:
`temp/plan-reviews/phase2/opus.md`, `temp/plan-reviews/phase2/gpt5.6.md`) with every mandatory finding from
both rounds incorporated above. Per this repo's brainstorming/writing-plans workflow, this document now
goes to the user for approval before `writing-plans` is invoked; the resulting draft implementation plan
will itself go to a third round of external review before execution.
