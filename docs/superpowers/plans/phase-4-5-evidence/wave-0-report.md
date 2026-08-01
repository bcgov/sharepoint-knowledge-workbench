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
14 passed
```

## Step 5 — Evidence artifacts generated

- `wave-0-artifact-inventory.json` — **36 scripts**, **51 test files**, **4 skills** (`analyze-document`, `convert-document`, `orchestrate-conversion`, `render-content`).
- `wave-0-dependency-graph.json` — **58 internal script-to-script edges** (AST-based, `import`/`from . import` only; stdlib and third-party imports excluded).
- `wave-0-test-ledger.json` — every `test_*` function across `tests/unit`, `tests/contract`, `tests/integration` (`proposed_owner_domain` left `null`; filled in Wave 1 per the plan).

## Step 6 — Dependency-edge classification

**Note on provenance:** the plan's Step 6 instruction is "same nine-value classification as Revision 2" — that earlier plan revision is not present in this repository's history (only Revision 3 was ever committed), so no authoritative nine-value list could be located or reused. A nine-value classification was constructed fresh for this run, grounded in the four active target domain plugins named in `CLAUDE.md`/the approved spec (`source-document-extraction`, `knowledge-analysis`, `canonical-knowledge`, `knowledge-publication`) plus shared-contract/orchestration/deferred/unclassified buckets. Full rationale and the per-script ownership heuristic are documented in `tools/phase-4-5-core-plugin-refactoring/wave0_classify_edges.py`'s module docstring. This classification is explicitly **PROVISIONAL** — confirmed or revised by Wave 1 Step 1 (`analyze_structure.py` split decision) and Step 6 (`wave-1-decisions.json`), per the plan's own decision-deferral pattern; nothing here is treated as final.

`wave-0-classified-edges.json` — 58/58 edges classified:

| Classification | Count |
|---|---|
| `SHARED_CONTRACT_CANDIDATE` | 19 |
| `CROSS_DOMAIN_REQUIRES_HUMAN_DECISION` | 17 |
| `CANONICAL_KNOWLEDGE_INTERNAL` | 8 |
| `CLI_ORCHESTRATION_EDGE` | 8 |
| `SHAREPOINT_DEFERRED_EDGE` | 4 |
| `KNOWLEDGE_ANALYSIS_INTERNAL` | 2 |
| `SOURCE_EXTRACTION_INTERNAL` | 0 |
| `KNOWLEDGE_PUBLICATION_INTERNAL` | 0 |
| `UNCLASSIFIED_REQUIRES_HUMAN_DECISION` | 0 |

**17 edges require an explicit Wave 1 human decision** (either the shared-contract boundary needs to move, or one of the two connected scripts' proposed domain ownership is wrong) — full from/to list in `wave-0-classified-edges.json`, filtered to `CROSS_DOMAIN_REQUIRES_HUMAN_DECISION`. Notably: `renderers/*` → `atomic_output.py`/`canonical_package.py` (publication reading canonical internals — a likely real Wave 1 contract boundary), and several `analyze_structure.py`/`convert.py`/`validate_canonical.py` edges into `identity.py`/`plans.py`/`publication_map.py`/`dependencies.py` (candidates for promotion into the shared `knowledge_workbench_contracts` distribution alongside `contracts.py`/`hashing.py`/`path_safety.py`, which already classified as `SHARED_CONTRACT_CANDIDATE`).

`SOURCE_EXTRACTION_INTERNAL` and `KNOWLEDGE_PUBLICATION_INTERNAL` both show 0 — expected at this stage: `source-document-extraction`'s only two proposed-owned scripts (`dependencies.py`, `emf_convert.py`) don't currently import each other, and `knowledge-publication`'s three renderer scripts' only classified edges point outward (to `canonical-knowledge`-owned targets), not to each other.

## Step 7 — External-consumer discovery

See `wave-0-external-consumer-report.md`. Summary: all three on-disk `.worktrees/` directories (`phase-4-native-sharepoint-skills`, `phase-3-governed-sharepoint-pilot`, `phase-3-0-tenant-capability-discovery`) are classified `ORPHANED_BROKEN_WORKTREE` — each `.git` file points at a `.git/worktrees/<name>` gitdir under this repository's pre-rename path (`manual-conversion-poc`), which no longer exists; `git worktree list` does not register any of them. Per the plan, none were touched. `NO_CONSUMER_OBSERVED_IN_INSPECTED_SCOPE` for all worktree signals; no `.claude/settings.json` and no repo-root `marketplace.json` found.

## Step 8 — Live-reference scan and baseline

See `wave-0-live-reference-report.md`. Full docx-to-content suite baseline reconfirmed live: **529 passed, 1 skipped** — matches `start-here.md`'s recorded figure exactly. Every live-repo reference to `plugins/docx-to-content` outside the plugin's own tree and this wave's tooling is documentation or a historical evidence artifact — no executable external consumer found.

## Wave 0 Gate — status

- [x] Confirmed test baseline recorded (529 passed, 1 skipped, reconfirmed live).
- [x] Every dependency edge classified (58/58; 17 flagged `CROSS_DOMAIN_REQUIRES_HUMAN_DECISION` for Wave 1, not silently resolved here).
- [x] Test ledger generated (51 test files enumerated; `proposed_owner_domain` deferred to Wave 1 per plan).
- [x] External-consumer signals discovered and classified using the six-value model — no signal treated as an automatic "consumer."
- [x] Live-reference report complete.
- [x] All tooling under `tools/`.
- [ ] Report committed to `phase-4-5-core-plugin-refactoring` — done immediately after this file is written (see commit following this report).

**Wave 0 is complete.** Wave 1 (contracts distribution, ownership, migration strategy, decision artifact) is the next wave and requires a human decision checkpoint (`wave-1-decisions.json`) before proceeding — not started in this session.
