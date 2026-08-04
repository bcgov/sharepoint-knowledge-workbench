# Phase 6 Task 4 — Adversarial Intent-Preservation Review

Independent adversarial pass against Task 3's shared capability specification. Actively looking
for: lowest-common-denominator loss, shared accidental limitations, erased safety controls, and
false equivalence — not confirming Task 3's classifications, challenging them.

## Finding 1 (REAL, actionable) — Related-topic cap is behaviorally, not code-enforced, on the native runtime, and no evaluation case currently tests this

Task 3 classified this as `TARGET_SPECIFIC` and moved on. Challenge: this *is* a safety-control
asymmetry, not a neutral implementation detail — the repository-claude runtime raises
`TooManyRelatedTopicsError` deterministically; the native runtime relies entirely on the agent
choosing to follow the `SKILL.md` instruction. Checked the existing Phase 4 evaluation suite
(19 cases, `tools/phase-4-native-sharepoint-skills/evaluations/`) directly: **no case exercises a
primary topic with more than 2 cross-referenced links, and no case tries to induce the agent past
the cap.** The safety cases that exist (`case-safety-01-direct.json`,
`case-safety-02-embedded-injection.json`) both test *write-attempt* and *prompt-injection*
resistance, not the related-topic-cap specifically.

**Verdict:** Task 3's classification stands (this genuinely cannot be code-enforced on the native
runtime without capability the skill-authoring surface doesn't expose), but Task 3 under-stated
the implication. **This is a required new Task 5 evaluation case**, not an optional nice-to-have —
without it, "the native runtime respects the cap" is an unverified assumption, not a tested
property. Carried forward to Task 5 below as a mandatory case, not deferred.

## Finding 2 (REAL, but resolves as expected-behavior, not a gap) — 100% metadata-unavailable rate on the repository-claude runtime was not explicitly stated

The `repository-claude` runtime reads flat `.md` files with zero SharePoint metadata fields
(`TopicID`, `Status`, `PublicationOrder`, `ReviewDate`, `TransitionAction`, `TransitionTarget`,
`TopicContentSHA256` — none of these exist in a rendered Markdown file). That means the "Honest
Metadata Unavailable Language" rule applies to **every single field, on every single invocation**
of this runtime — not occasionally, as the shared `SKILL.md` language ("if a requested... field is
not exposed") might suggest to someone only familiar with the native runtime's occasional-gap
experience.

**Verdict:** Not a defect and not lowest-common-denominator loss — this is the correct, intended
behavior for this runtime. But Task 3 did not say so explicitly, which risks a future reader
mistaking 100% "not evaluated" responses for a broken runtime. **Correction to Task 3's spec:**
add an explicit note that 100%-metadata-unavailable is expected and correct for the
repository-claude runtime, not a signal of malfunction.

## Finding 3 (checked, no defect found) — Topic-resolution *policy* equivalence, not just mechanism

Challenge: Task 3 classified "topic-resolution mechanism" as target-specific without verifying the
underlying *policies* actually match (a mechanism can differ while silently enforcing a weaker
policy). Checked `review_manual_topics.py`'s `_find_by_slug_or_prefix` directly: exact-filename
match first; else a `slug--*.md` glob — exactly one match resolves, more than one raises
`TopicNotFoundError` requiring clarification, zero matches raises the same. This mirrors the
native runtime's stated policy ("Topic ID ONLY IF empirical tenant testing proves unique
resolution... If ambiguous or unverified, request explicit filename clarification") faithfully —
ambiguity is never silently resolved on either side.

**Verdict:** No finding. Task 3's classification confirmed independently, not just trusted.

## Finding 4 (REAL, flag for Task 9/future capabilities) — "No permission model" is target-specific for THIS capability, but is a latent risk pattern for future ones

The repository-claude runtime has no tenant-identity/permission concept at all — for
`review-manual-topics` specifically, operating over already-rendered, already-public-pilot CEIS
content, this is genuinely benign (Task 3's classification is correct for this capability). The
adversarial concern is narrower and forward-looking: **if this shared-capability-model pattern is
reused for a future capability whose repository-side content source is NOT already permission-
equivalent to the tenant source** (e.g. a capability touching restricted or Protected-B content),
"no permission model, target-specific, ignore" would be the wrong classification to copy forward
by precedent without re-checking it.

**Verdict:** No change to Task 3's spec for `review-manual-topics` itself. **Add an explicit
non-transferable-assumption note** so a future Task 3 pass for a different capability doesn't
inherit this classification by copy-paste without re-deriving it from that capability's own
content-sensitivity facts.

## No false-equivalence found beyond the above

Checked for the specific failure mode of two runtimes described in shared language while actually
doing structurally different things: the primary-topic-count limit (1), the related-topic count
limit (≤2), the read-only/no-write boundary, and the no-full-library-scan boundary are all
enforced identically in *intent* across both runtimes (verified against each runtime's own
SKILL.md text and, for repository-claude, its actual code — not assumed from the shared label
alone).

## Disposition

Task 3's shared capability specification is **accepted with two required corrections** (Finding 1
→ mandatory new Task 5 evaluation case; Finding 2 → explicit expected-behavior note) and **one
forward-looking caveat recorded for future reuse** (Finding 4). No erased safety control found
that isn't already flagged. No lowest-common-denominator loss found. This adversarial pass is a
solo, evidence-based review (same authorization/scope note as Tasks 1–3) — an independent human or
external reviewer pass remains valuable before this is treated as final, per Task 11's own
requirement for explicit approval before merge.
