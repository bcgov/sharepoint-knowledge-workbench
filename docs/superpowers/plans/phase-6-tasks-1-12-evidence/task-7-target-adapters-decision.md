# Phase 6 Task 7 — Target Adapters: Decision

**Decision: no new adapter code is required.** Per the task's own instruction ("adapters expose
the shared intent while declaring unsupported and target-specific behavior... avoid unnecessary
abstraction"), an adapter is only justified where a runtime's *native* implementation doesn't
already expose the shared intent on its own. Checked against Task 3's classification and Task 6's
real execution evidence:

- **`native-sharepoint`**: the shared intent (one primary + ≤2 related, read-only, no hash/
  identity/write claims, honest-unavailable language) is expressed directly in `SKILL.md` — the
  native runtime's own authoring surface *is* its adapter to the shared intent; there is no
  separate code layer to wrap.
- **`repository-claude`**: `review_manual_topics.py`'s `resolve_topic()` already implements the
  shared resolution policy (exact-match-or-unique-prefix, raise rather than guess) natively in
  Python, proven equivalent to the native runtime's stated policy independently at Task 4 Finding
  3 (not just assumed). The `primary_topic_slug` field added at Task 5 is the one place a real
  adapter-shaped normalization was needed (bridging the `.aspx`/`.md` extension difference for
  evaluation-case authoring) — already done, not deferred.

**What would have justified an adapter, and didn't apply here:** a runtime whose native mechanism
could only express a *subset* of the shared intent, requiring a wrapper to fill the gap or
explicitly declare the shortfall. Neither runtime has that problem for this capability — Task 3
found the differences (content format, resolution mechanism, permission-model applicability) are
all legitimately target-specific, not capability gaps needing translation.

**Declared unsupported/target-specific behavior** (per the task's own requirement to declare
this explicitly, even without a code adapter): `repository-claude` does not support permission-
scoped cases (`case-permission-*`, Task 5's `applicable_runtimes` field is the declaration
mechanism); `native-sharepoint`'s related-topic-cap enforcement is behavioral, not code-provable
(Task 4 Finding 1's flag, closed by Task 5's new `BOUND-01` case rather than an adapter).
