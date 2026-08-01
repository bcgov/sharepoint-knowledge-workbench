# Wave 0 Report — Baseline Inventory, Dependency Graph, Test Ledger, External-Consumer Discovery

**Date:** 2026-08-01
**Branch:** `phase-4-5-core-plugin-refactoring` (created off `main` at `98c1943`, per Wave 0 Step 0)
**Plan:** `docs/superpowers/plans/2026-08-01-phase-4-5-core-knowledge-plugin-domain-refactoring.md`

## Step 0 — Entry gate

`origin/main` confirmed current (`98c1943`, includes the Phase 4 exit-gate reconciliation merged via PR #12). Working tree was clean. Branch created from `main`, not `phase-4-5-planning`.

## Steps 1–4 — Inventory, dependency graph, test-ledger generators (TDD)

Built under `tools/phase-4-5-core-plugin-refactoring/`: `wave0_inventory.py`, `wave0_dependency_graph.py`, `wave0_test_ledger.py`, `wave0_external_consumers.py`, `wave0_classify_edges.py` — each with a failing-first test in `tools/phase-4-5-core-plugin-refactoring/tests/`.

```
cd tools/phase-4-5-core-plugin-refactoring && python3 -m pytest tests/ -v
16 passed
```

(As of Step 4; the full tooling suite grows to 21 passed after Step 6's classifier tests — see that section.)

**Bug found and fixed during self-review (before Wave 0 was reported complete):** the first version of `wave0_test_ledger.py` used `ast.walk(tree)` for its top-level bare-function branch, which visits every descendant node including methods nested inside classes. Every class-based test method (`class TestFoo: def test_x(self): ...`) was therefore counted twice — once correctly as `TestFoo::test_x` via the `ClassDef` branch, once again incorrectly as a bare `test_x` via the walk-based branch. This inflated the ledger to **682 entries** against pytest's real **530 collected tests** — caught by cross-checking the ledger's count against `pytest --collect-only -q`, not assumed correct from a green test suite alone. Fixed by iterating only `tree.body` (true module-level statements) for the bare-function branch, plus two new regression tests (`test_build_test_ledger_does_not_double_count_class_methods`, `test_build_test_ledger_matches_pytest_collected_count_on_real_repo`). Corrected ledger: **526 entries** (the residual gap under 530 is expected — pytest's collected count includes each `@pytest.mark.parametrize` instance separately, while the AST ledger counts each `def test_*` once regardless of how many parametrized cases it expands to).

## Step 5 — Evidence artifacts generated

- `wave-0-artifact-inventory.json` — **36 scripts**, **51 test files**, **4 skills** (`analyze-document`, `convert-document`, `orchestrate-conversion`, `render-content`).
- `wave-0-dependency-graph.json` — **58 internal script-to-script edges** (AST-based, `import`/`from . import` only; stdlib and third-party imports excluded).
- `wave-0-test-ledger.json` — every `test_*` function across `tests/unit`, `tests/contract`, `tests/integration`: **526 entries** (`proposed_owner_domain` left `null`; filled in Wave 1 per the plan). See the double-counting bug note below — this is the corrected figure.

**Observed baseline vs. planning-time estimate:** the plan's own goal statement (line 5) and Known File Inventory note (line 348) cite planning-time estimates of **30 scripts** and **45 test files**, derived before Wave 0 ran. Wave 0's actual, tool-generated count is **36 scripts** and **51 test files** — 6 more of each than the planning estimate assumed. This is not an error requiring the earlier count to be rewritten; it is exactly what Wave 0 exists to establish — a real, tool-verified count supersedes a planning-time estimate for every later wave's purposes. **The Wave 0 observed inventory (36 scripts, 51 test files, 4 skills, 58 dependency edges) is authoritative for Phase 4.5 execution going forward; the plan's 30/45 figures remain valid as a record of what was estimated at planning time**, not as something Wave 0 disproved or needs to correct in place.

## Step 6 — Dependency-edge classification (Revision 2, human-review correction, 2026-08-01)

**Revision history:** the first Wave 0 pass invented a single nine-value classification that conflated dependency-type with proposed domain ownership, and used a from-scratch domain-ownership heuristic instead of the plan's own data. Human review corrected both:

1. **Vocabulary provenance.** The reviewer's stated `dependency_classification` vocabulary (`VALID_FORWARD_DEPENDENCY`, `REVERSE_DEPENDENCY`, `CROSS_DOMAIN_UTILITY`, `SOURCE_FORMAT_COUPLING`, `PRESENTATION_COUPLING`, `SHARED_CONTRACT`, `CLI_ORCHESTRATION`, `TEST_ONLY_DEPENDENCY`, `HISTORICAL_OR_DEAD`) was checked against the repository (`grep -rl` for each value name across every tracked file, including the approved spec and plan) and found in **zero** files — the claim that it was "already established in the approved specification" could not be verified and is not repeated as fact here. The vocabulary is adopted on the reviewer's direct authority in this correction round, with that provenance stated plainly rather than presented as pre-existing doctrine.
2. **Domain-ownership source.** While implementing the correction, a second, independent gap was found by re-reading the plan: it already contains a "Known File Inventory" table (`docs/superpowers/plans/2026-08-01-phase-4-5-core-knowledge-plugin-domain-refactoring.md`, lines 316–348) with its own provisional per-script domain assignments — real project data the first Wave 0 pass should have used instead of inventing a heuristic. That table disagreed with the invented heuristic on 6 scripts (`path_safety.py`, `pandoc_validate.py`, `publication_map.py`, `hashing.py`, `plans.py`, and all 6 `pandoc_fixes/*` modules) and explicitly flags three files (`analyze_structure.py`, `convert.py`, `atomic_output.py`) as **split or duplicated across domains**, not single-owned. `PROPOSED_OWNER_DOMAIN` in `wave0_classify_edges.py` now maps directly from that table, with the three split/duplicated files mapped to the allowed `UNRESOLVED` domain value (a real "pending Wave 1 decision" state, not the same as "unclassified" — `HISTORICAL_OR_DEAD` is reserved for scripts absent from the plan's table entirely, which none of the 58 edges' endpoints are).

Edge model per `wave-0-classified-edges.json` entry:

```json
{
  "from": "scripts/renderers/protocol.py",
  "to": "scripts/canonical_package.py",
  "dependency_classification": "PRESENTATION_COUPLING",
  "proposed_source_domain": "KNOWLEDGE_PUBLICATION",
  "proposed_target_domain": "CANONICAL_KNOWLEDGE",
  "disposition": "REQUIRES_HUMAN_DECISION",
  "rationale": "Renderer currently accesses canonical implementation rather than a public contract."
}
```

`wave0_classify_edges.py::validate_classified_edges()` asserts, for all 58 edges: `dependency_classification` is one of the 9 approved values, `proposed_source_domain`/`proposed_target_domain` are one of the 8 approved domain values, `disposition` is one of the 4 approved values, and `rationale` is non-empty. Zero validation errors on the real graph (enforced by `test_classify_all_covers_every_edge_on_real_graph_with_no_validation_errors`).

`wave-0-classified-edges.json` — 58/58 edges classified, no edge unclassified:

**`dependency_classification` counts:**

| Value | Count |
|---|---|
| `CROSS_DOMAIN_UTILITY` | 23 |
| `SHARED_CONTRACT` | 12 |
| `VALID_FORWARD_DEPENDENCY` | 12 |
| `CLI_ORCHESTRATION` | 8 |
| `SOURCE_FORMAT_COUPLING` | 2 |
| `PRESENTATION_COUPLING` | 1 |
| `REVERSE_DEPENDENCY` | 0 |
| `TEST_ONLY_DEPENDENCY` | 0 (expected — this graph is scripts/-only by construction) |
| `HISTORICAL_OR_DEAD` | 0 |

**`disposition` counts:**

| Value | Count |
|---|---|
| `PROVISIONALLY_ACCEPTED` | 32 |
| `REQUIRES_HUMAN_DECISION` | 22 |
| `OUT_OF_SCOPE_RETAIN_IN_PLACE` | 4 (sharepoint_*.py edges, deferred plugin) |
| `HISTORICAL_OR_DEAD_REQUIRES_CONFIRMATION` | 0 |

**22 edges carry `REQUIRES_HUMAN_DECISION`** for Wave 1 (up from the first pass's 17 — the increase reflects the more accurate plan-sourced ownership map correctly flagging every edge that touches `analyze_structure.py`, `convert.py`, or `atomic_output.py`, the three files the plan itself already marks as split/duplicated, not a new problem introduced by this correction). None of these 22 were resolved during Wave 0 — every one is preserved with `disposition: REQUIRES_HUMAN_DECISION` and a rationale for Wave 1 to act on. Full list in `wave-0-classified-edges.json`.

## Step 7 — External-consumer discovery

See `wave-0-external-consumer-report.md`. Summary: all three on-disk `.worktrees/` directories (`phase-4-native-sharepoint-skills`, `phase-3-governed-sharepoint-pilot`, `phase-3-0-tenant-capability-discovery`) are classified `ORPHANED_BROKEN_WORKTREE` — each `.git` file points at a `.git/worktrees/<name>` gitdir under this repository's pre-rename path (`manual-conversion-poc`), which no longer exists; `git worktree list` does not register any of them. Per the plan, none were touched.

**Correction (human review, 2026-08-01):** the first Wave 0 pass reported `no .claude/settings.json` / `no marketplace.json` but omitted a result for the repository-root `skills-lock.json`, even though the raw signal scan found it. Inspected explicitly now (path, tracking status, purpose, entries for `docx-to-content`/its four skills, install/source path, version, currency, active-consumer status — full detail in `wave-0-external-consumer-report.md`'s new section): tracked since a single commit (`f86352b`, the repo's initial commit), never modified since; zero entries reference `docx-to-content` or any of `analyze-document`/`convert-document`/`render-content`/`orchestrate-conversion`. It is a lockfile for externally-installed marketplace skills (`obra/superpowers`, `richfrem/agent-plugins-skills`, `anthropics/skills`) — a structurally separate mechanism from this repository's own `plugins/` directory, which `docx-to-content` was built directly into rather than installed through. **Classification: `NO_RELEVANT_ENTRY`.**

`NO_CONSUMER_OBSERVED_IN_INSPECTED_SCOPE` is now stated only after every discovered signal — including the root lock file — was individually inspected, not assumed.

## Step 8 — Live-reference scan and baseline

See `wave-0-live-reference-report.md`. Full docx-to-content suite baseline reconfirmed live: **529 passed, 1 skipped** — matches `start-here.md`'s recorded figure exactly. Every live-repo reference to `plugins/docx-to-content` outside the plugin's own tree and this wave's tooling is documentation or a historical evidence artifact — no executable external consumer found.

## Wave 0 Gate — status

- [x] Confirmed test baseline recorded (529 passed, 1 skipped, reconfirmed live).
- [x] Every dependency edge classified (58/58 against the approved `dependency_classification`/domain/disposition/rationale model; 0 validation errors; 22 flagged `REQUIRES_HUMAN_DECISION` for Wave 1, not silently resolved here).
- [x] Test ledger generated (51 test files / 526 distinct test functions enumerated, after fixing a double-counting bug found during self-review; `proposed_owner_domain` deferred to Wave 1 per plan).
- [x] External-consumer signals discovered and classified using the six-value model, including explicit inspection of the root `skills-lock.json` (`NO_RELEVANT_ENTRY`) — no signal treated as an automatic "consumer" or left uninspected.
- [x] Live-reference report complete.
- [x] All tooling under `tools/`.
- [x] Report committed to `phase-4-5-core-plugin-refactoring`.

**Wave 0 is conditionally complete pending human review of this correction pass.** Wave 1 (contracts distribution, ownership, migration strategy, decision artifact) is the next wave and requires a human decision checkpoint (`wave-1-decisions.json`) before proceeding — **not started**.
