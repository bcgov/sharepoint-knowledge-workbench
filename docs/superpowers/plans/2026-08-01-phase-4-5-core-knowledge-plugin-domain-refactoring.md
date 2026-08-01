# Phase 4.5: Core Knowledge Plugin Domain Refactoring — Implementation Plan (Revision 3)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decompose the mature combined `plugins/docx-to-content/` plugin (v0.1.0, 530 tests collected / 529 passed / 1 skipped, 4 skills, 30 scripts) into four independently installable, independently testable domain plugins — `source-document-extraction`, `knowledge-analysis`, `canonical-knowledge`, `knowledge-publication` — each a real, buildable, `pip`-installable Python distribution, connected by an independently installable public-contracts distribution, while preserving the existing analyze→confirm→convert→render CEIS workflow byte-identically.

**Architecture:** Nine sequential waves (Wave 0 through Wave 8). Each plugin is a `src/`-layout Python package with its own `pyproject.toml`, built into a wheel and installed into a clean virtual environment as its wave's independence proof — not merely a `sys.path`-manipulated checkout. Every wave closes only when the full applicable test-layer set is green, including a real isolated-install gate. Temporary compatibility skills bridge the existing workflow during migration; new plugins never depend on them.

**Tech Stack:** Python 3, `pyproject.toml`/`build`/`pip` (new to this repository — no prior Python packaging existed; this plan introduces it deliberately, per the specification's Revision 3 amendment), pytest, `venv`, Pandoc (external), LibreOffice/`soffice` (external).

## Revision 3 Changelog (addresses 9 remaining blockers from the second implementation-plan review, 2026-08-01)

1. Replaced the `conftest.py`/`sys.path` production-import model (Revision 2) with real `src/`-layout `pyproject.toml` packages per plugin, per the specification's Revision 3 amendment (§13b) — applied to the spec **before** this plan, not deferred to Wave 1.
2. Replaced the neutral `contracts/` directory (walked-to via `find_repo_root()`) with an independently installable `contracts/python/` distribution (`knowledge_workbench_contracts`), declared as a normal dependency by each plugin's `pyproject.toml` — no plugin runtime code performs repository-root discovery.
3. Separated repository-level fixtures (`tests/contracts/fixtures/`, monorepo integration evidence) from plugin-packaged fixtures (`plugins/<name>/tests/fixtures/`, shipped with that plugin's own test suite) — installed/isolated tests never search upward for the repository.
4. Replaced the copy-into-tempdir + `PYTHONPATH` isolated-install check with a real `build` → `pip install` (clean venv) → import-outside-pytest → metadata-inspection harness, plus a negative control and a combined four-distribution collision test.
5. Confirmed the specification amendment (§13b, Revision 3) was applied to the spec file **before** this plan revision, not scheduled as a Wave 1 execution task.
6. Replaced `git reset --hard` as the default per-wave rollback with a stop/capture/verify/`git revert`-based procedure; hard reset is now documented only as a `DISPOSABLE_UNPUBLISHED_WORKTREE_OPTION` requiring explicit conditions and human authorization.
7. Investigated the `TASK-12-*` deletions fully (hashes verified identical between the tracked-at-HEAD version and the `temp/` copy; confirmed user-authorized, unrelated to this branch); the plan's commit steps now stage only the two Phase 4.5 documents, never `git add -A`.
8. Replaced the three "stale worktree" findings' implicit "consumer" framing with an explicit six-value classification (`REGISTERED_ACTIVE_WORKTREE` / `REGISTERED_STALE_WORKTREE` / `ORPHANED_BROKEN_WORKTREE` / `SEPARATE_CLONE` / `UNREGISTERED_COPY` / `UNKNOWN`), and reworded all "no consumer found" claims to `NO_CONSUMER_OBSERVED_IN_INSPECTED_SCOPE`.
9. Made Wave 6's golden-master comparison non-skippable at wave closure — a `pytest.skip` is permitted only during ordinary development; the Wave 6 exit gate requires zero skips on that specific test, with actual recorded hashes.

---

## Specification Alignment Statement

This plan conforms to `docs/superpowers/specs/phase-4-5-core-knowledge-plugin-domain-refactoring-spec.md` **Revision 3** (§13b, amended 2026-08-01, before this plan revision). Every packaging, contract-distribution, and installability claim in this plan traces directly to §13b's requirements. Where this plan makes a provisional choice within §13b's boundaries (e.g., the exact contracts-distribution import name `knowledge_workbench_contracts`), it is flagged `PROVISIONAL — Wave 1 confirms`, consistent with the specification's existing decision-deferral pattern for genuinely open naming/versioning choices (§12, §13).

## Global Constraints

- Full applicable test suite must be green at every wave boundary (spec §19) — no wave may knowingly carry a failing test into the next wave.
- Accepted CEIS canonical and rendered outputs remain byte-identical by default (spec §16); any difference requires a written exception record with human approval before the wave can close.
- **Independent installability means a built wheel, installed into a clean virtual environment with only declared dependencies, works** (spec §13b) — not a checkout with `sys.path` manipulation. Every plugin wave's gate includes this real installation proof.
- No plugin may import another plugin's implementation package — only the independently installable `knowledge_workbench_contracts` distribution (spec §11, §13b).
- Contract versions, plugin starting versions, marketplace adoption, contracts-distribution naming, and original-skill dispositions are all `REQUIRES_HUMAN_DECISION` — resolved once in Wave 1 Step 6 into `wave-1-decisions.json`. No later wave repeats a hardcoded illustrative value.
- **This plan does not authorize implementation.** Execution requires: this plan approved, Phase 4 exit evidence reverified accepted and merged to main, a fresh session, and the dedicated `phase-4-5-core-plugin-refactoring` branch/worktree (never `phase-4-5-planning`).
- Rollback is `git revert`-based by default (Rollback Model section below) — `git reset --hard` is a documented exception requiring explicit conditions, never the ordinary procedure.
- Every shell command resolves the repository root dynamically via `repo_root="$(git rev-parse --show-toplevel)"` — this is repository-tooling-only usage (Wave 0/1 scripts under `tools/`), never plugin production code (§13b explicitly prohibits the latter).
- Commits in this plan stage named files explicitly — never `git add -A` — to keep unrelated working-tree state (e.g. the user's own `temp/` reorganization) out of Phase 4.5 commits.

---

## Rollback Model (applies to every wave — replaces per-wave `git reset --hard`)

**Standard procedure, every wave:**

1. **Stop** execution at the failing step.
2. **Capture** `git status --short`, `git diff`, the failing test's full output, and any evidence artifacts already written — save these to `docs/superpowers/plans/phase-4-5-evidence/wave-N-incident-<timestamp>.md` before touching anything else.
3. **Verify the exact wave commit range**: `git log <pre-wave-commit>..HEAD --oneline`.
4. **Confirm no unrelated changes** are mixed into that range (`git diff --stat <pre-wave-commit>..HEAD` — every path must belong to this wave's declared Files list).
5. **Revert with history-preserving commits**: `git revert --no-commit <newest-wave-commit>..<oldest-wave-commit>` (reverse order), review the combined diff, then `git commit -m "revert(phase4.5-waveN): <reason>, see wave-N-incident-<timestamp>.md"`.
6. **Restore documentation/evidence consistently** — the reverted wave's report, ledger entries, and diagrams must be marked `REVERTED` with a link to the incident record, not silently deleted.
7. **Rerun the pre-wave validation gate** (the previous wave's gate conditions) to confirm the revert landed cleanly.
8. **Push the revert commit** if the wave's commits were already pushed: `git push origin phase-4-5-core-plugin-refactoring`.

**`git reset --hard` — documented exception only, `DISPOSABLE_UNPUBLISHED_WORKTREE_OPTION`:**

Permitted only when **all** of the following hold, confirmed and recorded before use:
- The worktree is confirmed clean of any unique, non-reproducible evidence (`git status --short` reviewed line-by-line, not assumed).
- No commit in the range to be discarded has been pushed to `origin` (`git log origin/phase-4-5-core-plugin-refactoring..HEAD` shows the full range).
- Explicit human authorization is recorded for this specific reset, naming the exact target commit.

If any condition fails, use the standard revert procedure above instead.

---

> **Correction (2026-08-01, mid-Wave-2, per spec §13d):** the "Contract Distribution Model" and
> "Isolated-Install Harness" sections immediately below describe the **original, superseded**
> shared-pip-distribution model (every plugin depends on `contracts/python/`/`runtime/python/` via
> pip). That model made standalone plugin installation impossible and is corrected in
> `docs/superpowers/plans/phase-4-5-evidence/wave-2-contract-materialization-correction.md`: each
> contract is materialized inside its producer plugin's own package; consumers carry generated,
> hash-checked local copies; no plugin's `pyproject.toml` may depend on a workbench-family
> distribution; `contracts/python/`/`runtime/python/` are `DEVELOPMENT_CODEGEN_SOURCE` only. The
> Waves 2-5 common step sequence below is amended accordingly (see the note at Step 10). Read the
> correction doc before starting Wave 3.

## Packaging Model (per specification §13b)

**Plugin distribution ID vs. Python import package:**

| Distribution ID (hyphenated, Claude Code identity) | Python import package (underscored) |
|---|---|
| `source-document-extraction` | `source_document_extraction` |
| `knowledge-analysis` | `knowledge_analysis` |
| `canonical-knowledge` | `canonical_knowledge` |
| `knowledge-publication` | `knowledge_publication` |

**Per-plugin layout:**

```
plugins/source-document-extraction/
├── .claude-plugin/plugin.json
├── plugin.yaml
├── pyproject.toml
├── src/
│   └── source_document_extraction/
│       ├── __init__.py
│       ├── extraction.py
│       └── ...
├── skills/extract-docx/SKILL.md
└── tests/
    ├── unit/
    └── fixtures/
```

**Minimal `pyproject.toml` template (adapted per plugin; version/dependency values read from `wave-1-decisions.json`, not hardcoded):**

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "source-document-extraction"
version = "<from wave-1-decisions.json>"
description = "Source-format inspection and extraction for the SharePoint Knowledge Workbench."
requires-python = ">=3.10"
dependencies = [
    "knowledge-workbench-contracts==<contracts version from wave-1-decisions.json>",
]

[tool.setuptools.packages.find]
where = ["src"]
```

`conftest.py` (if present) may define pytest fixtures only. Production imports (`import source_document_extraction.extraction`) work after `pip install -e .` or a built-wheel install, with zero `sys.path` manipulation — this is the executable proof of independent installability required by spec §23 Criteria 4-5.

---

## Contract Distribution Model (per specification §13b)

**Independently installable, owned by no domain plugin:**

```
contracts/python/
├── pyproject.toml
└── src/
    └── knowledge_workbench_contracts/   # PROVISIONAL name — Wave 1 confirms/renames
        ├── __init__.py
        ├── repo_root.py                  # tooling-only marker — see prohibition below
        ├── tree_hash.py
        ├── normalized_source_document.py
        ├── analysis_plan.py
        ├── canonical_package.py
        ├── publication_map.py
        └── rendered_output_profile.py
```

```toml
# contracts/python/pyproject.toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "knowledge-workbench-contracts"
version = "<from wave-1-decisions.json>"
description = "Neutral, independently installable public data contracts for the SharePoint Knowledge Workbench plugin family."
requires-python = ">=3.10"
dependencies = []

[tool.setuptools.packages.find]
where = ["src"]
```

Each `knowledge_workbench_contracts/<name>.py` module contains only a dataclass + `validate(data: dict) -> None` — zero domain logic, zero dependency on any plugin.

**`repo_root.py`'s prohibition:** this module exists inside the contracts distribution **only** as a historical artifact of the tree-hash/evidence tooling used by repository-level integration tests (Wave 6); it is exported but **must never be imported by any plugin's `src/` production code** — enforced by the dependency-boundary checker's Wave 2-5 gate (see below). Plugin production code resolves contract types via the normal `import knowledge_workbench_contracts.canonical_package` — a declared dependency, not a filesystem search.

**Repository-level fixtures vs. plugin-packaged fixtures:**

`tests/contracts/fixtures/` (repository root) is the authoritative, human-reviewed evidence for monorepo-level integration testing (spec §14 Tier 2/3) — never installed, never shipped. Each plugin's own `tests/fixtures/` carries the minimal fixtures its **isolated, installed** test run needs — generated from the repository-level fixtures during that wave, but physically distinct, small, and packaged with the plugin's own test suite.

---

## Isolated-Install Harness (real installation, not a copy-and-`PYTHONPATH` check)

```python
# tools/phase-4-5-core-plugin-refactoring/isolated_install_check.py
"""Builds a plugin's wheel, installs it (plus the contracts distribution and
declared dependencies only) into a clean virtual environment, and proves the
package works from that installation — not from the monorepo checkout."""
from __future__ import annotations
import argparse
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path


def build_wheel(project_dir: Path, dist_dir: Path) -> Path:
    subprocess.run([sys.executable, "-m", "build", "--wheel", "--outdir", str(dist_dir), str(project_dir)], check=True)
    wheels = sorted(dist_dir.glob("*.whl"))
    if not wheels:
        raise RuntimeError(f"No wheel produced for {project_dir}")
    return wheels[-1]


def check_isolated_install(
    plugin_dir: Path, contracts_dir: Path, repo_root: Path, import_package: str
) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        venv_dir = tmp_path / "venv"
        venv.EnvBuilder(with_pip=True).create(venv_dir)
        pip = venv_dir / "bin" / "pip"
        python = venv_dir / "bin" / "python"

        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()
        contracts_wheel = build_wheel(contracts_dir, dist_dir)
        plugin_wheel = build_wheel(plugin_dir, dist_dir)

        subprocess.run([str(pip), "install", str(contracts_wheel), str(plugin_wheel), "pytest"], check=True, capture_output=True)

        # Confirm NO upstream plugin distribution is installed (undeclared-dependency negative control)
        freeze = subprocess.run([str(pip), "freeze"], capture_output=True, text=True, check=True).stdout
        for other in ["source-document-extraction", "knowledge-analysis", "canonical-knowledge", "knowledge-publication"]:
            if other in freeze and other != plugin_dir.name:
                raise AssertionError(f"Undeclared upstream plugin {other} found installed: {freeze}")

        # Import the package outside pytest, from the installed distribution only
        import_check = subprocess.run(
            [str(python), "-c", f"import {import_package}; print({import_package}.__file__)"],
            capture_output=True, text=True,
        )
        if import_check.returncode != 0 or "site-packages" not in import_check.stdout:
            raise AssertionError(f"Import did not resolve from installed site-packages: {import_check.stdout} {import_check.stderr}")

        # Run this plugin's own tests using the installed distribution
        test_result = subprocess.run(
            [str(python), "-m", "pytest", str(plugin_dir / "tests"), "-v"],
            capture_output=True, text=True,
        )
        return test_result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--plugin", required=True)
    parser.add_argument("--import-package", required=True)
    args = parser.parse_args()
    repo_root = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).decode().strip())
    result = check_isolated_install(
        repo_root / "plugins" / args.plugin,
        repo_root / "contracts" / "python",
        repo_root,
        args.import_package,
    )
    print(result.stdout)
    print(result.stderr)
    sys.exit(result.returncode)
```

**Negative control (required before this harness is trusted as a real gate):**

```python
# tools/phase-4-5-core-plugin-refactoring/tests/test_isolated_install_check.py
from pathlib import Path
import pytest
from isolated_install_check import check_isolated_install

def test_harness_fails_on_undeclared_upstream_import(tmp_path):
    """A fixture 'broken plugin' whose src/ imports a module only available in
    another plugin's package must cause the isolated install (or its test run)
    to fail — proving the harness actually detects the violation it exists to
    catch, not merely that it runs without crashing."""
    # Implementer builds a minimal broken-plugin fixture under
    # tools/phase-4-5-core-plugin-refactoring/tests/fixtures/broken_plugin/
    # (a pyproject.toml + src/broken_plugin/__init__.py that does
    # `import canonical_knowledge.package`, which is never installed in the
    # isolated venv) and asserts check_isolated_install raises or the
    # returned test_result.returncode != 0.
    ...  # concrete fixture built during Wave 1 Step 5 (see below) — not a
         # deferred design decision, a construction task with a fixed target

def test_harness_fails_on_missing_declared_dependency(tmp_path):
    """A fixture plugin whose pyproject.toml omits the contracts dependency
    but whose code imports it anyway must fail to install or fail at import
    time — proving metadata-completeness is actually enforced."""
    ...  # same construction pattern as above
```

**Combined-environment collision test** (Wave 6 gate — installs all four plugin wheels plus the contracts wheel into one venv, confirms zero import or dependency collisions, and that each plugin's own tests still pass in that shared environment).

---

## Public Interface Contract (fixed signatures)

```python
# source_document_extraction/extraction.py
def extract_and_normalize(source: Path, output_dir: Path) -> dict:
    """Returns a normalized-source-document v1 dict."""

# knowledge_analysis/analysis.py
def recommend_from_normalized(normalized_source_document: dict) -> dict:
    """Returns an analysis-plan v1 dict."""

# canonical_knowledge/package.py
def build_canonical_package(analysis_plan: dict, source_dir: Path, output_dir: Path) -> dict:
    """Returns a canonical-package v1 dict."""

# knowledge_publication/renderers/multipage_markdown.py
def render(canonical_package_dir: Path, output_dir: Path) -> dict:
    """Returns a rendered-output-profile v1 dict."""
```

**Deterministic tree-hash algorithm** (`knowledge_workbench_contracts/tree_hash.py`):

```python
import hashlib
from pathlib import Path

def compute_tree_hash(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            h.update(path.relative_to(root).as_posix().encode("utf-8"))
            h.update(path.read_bytes())
    return h.hexdigest()
```

---

## Known File Inventory

(Same domain assignments as Revision 2 — re-verified against the actual Phase 4.5 start commit in Wave 0 Task 1.)

| File | Lines | Provisional domain |
|---|---|---|
| `validate_canonical.py` | 855 | canonical-knowledge |
| `analyze_structure.py` | 577 | **split** — Wave 1 Step 1 |
| `contracts.py` | 533 | **split into `knowledge_workbench_contracts`** — Wave 1 Step 2 |
| `package.py` | 484 | canonical-knowledge |
| `cli.py` | 385 | compatibility orchestrator (not moved) |
| `convert.py` | 316 | split source-extraction/canonical-knowledge |
| `canonical_package.py` | 278 | canonical-knowledge |
| `plans.py` | 272 | canonical-knowledge |
| `chunking.py` | 272 | canonical-knowledge |
| `topic_grouping.py` | 197 | knowledge-analysis |
| `sharepoint_package.py` | 174 | OUT_OF_PHASE_4_5_SCOPE |
| `atomic_output.py` | 173 | duplicated: canonical-knowledge + knowledge-publication |
| `dispositions.py` | 156 | canonical-knowledge |
| `sharepoint_reconcile.py` | 138 | OUT_OF_PHASE_4_5_SCOPE |
| `media_disposition.py` | 118 | canonical-knowledge |
| `identity.py` | 111 | canonical-knowledge |
| `sharepoint_dry_run.py` | 100 | OUT_OF_PHASE_4_5_SCOPE |
| `dependencies.py` | 87 | source-document-extraction |
| `emf_convert.py` | 76 | source-document-extraction |
| `path_safety.py` | 73 | source-document-extraction |
| `pandoc_validate.py` | 72 | source-document-extraction |
| `sharepoint_cli.py` | 69 | OUT_OF_PHASE_4_5_SCOPE |
| `publication_map.py` | 64 | canonical-knowledge |
| `hashing.py` | 53 | canonical-knowledge |

`scripts/pandoc_fixes/` (6 modules) → source-document-extraction. `scripts/renderers/` (3 modules) → knowledge-publication. 4 skills → `PROPOSED_DISPOSITION`, resolved Wave 1 Step 6. 45 test files → exact mapping via Wave 0's generated ledger.

---

## Wave 0 — Baseline Inventory, Dependency Graph, Test Ledger, External-Consumer Discovery

**Files:**
- Create: `tools/phase-4-5-core-plugin-refactoring/wave0_inventory.py`, `wave0_dependency_graph.py`, `wave0_test_ledger.py`, `wave0_external_consumers.py`
- Create: `tools/phase-4-5-core-plugin-refactoring/tests/test_wave0_*.py`
- Create: `docs/superpowers/plans/phase-4-5-evidence/wave-0-*.json`, `wave-0-external-consumer-report.md`, `wave-0-live-reference-report.md`, `wave-0-report.md`

**Interfaces:** Consumes nothing. Produces the three JSON artifacts and the external-consumer report, consumed by Wave 1 and Waves 2-5.

**Rollback:** Standard revert procedure (see Rollback Model). Pre-wave commit = the commit where `phase-4-5-core-plugin-refactoring` was created.

- [ ] **Step 0: Verify entry gate and create the execution branch**

```bash
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
git fetch origin
git log origin/main -1 --oneline
git status --short   # must be empty
git branch --show-current   # must NOT be phase-4-5-planning
```

**STOP if:** Phase 4's exit-evidence merge commit is not visible on `origin/main`, or the working tree is not clean.

```bash
git checkout main && git pull origin main
git checkout -b phase-4-5-core-plugin-refactoring
```

(Provisional branch name — confirm the final name at execution-authorization time.)

- [ ] **Step 1-4: Inventory, dependency graph, test-ledger generators (TDD, identical structure to prior revision)**

Write failing tests, then implement `wave0_inventory.py::build_inventory()`, `wave0_dependency_graph.py::build_dependency_graph()`, `wave0_test_ledger.py::build_test_ledger()` — exact code as Revision 2's Wave 0 Steps 1-6 (AST-based, `tools/`-located, unchanged by this revision's packaging correction since Wave 0 tooling is repository-only, not plugin production code, and was already correctly placed outside `plugins/` in Revision 2).

Run: `cd "$repo_root/tools/phase-4-5-core-plugin-refactoring" && python3 -m pytest tests/ -v` — Expected: PASS for all three generators.

- [ ] **Step 5: Generate all Wave 0 evidence artifacts**

```bash
cd "$repo_root/tools/phase-4-5-core-plugin-refactoring"
mkdir -p "$repo_root/docs/superpowers/plans/phase-4-5-evidence"
python3 -c "
import json
from pathlib import Path
from wave0_inventory import build_inventory
from wave0_dependency_graph import build_dependency_graph
from wave0_test_ledger import build_test_ledger

repo_root = Path('$repo_root')
plugin_root = repo_root / 'plugins' / 'docx-to-content'
out_dir = repo_root / 'docs' / 'superpowers' / 'plans' / 'phase-4-5-evidence'
inv = build_inventory(plugin_root)
graph = build_dependency_graph(plugin_root)
ledger = build_test_ledger(plugin_root)
(out_dir / 'wave-0-artifact-inventory.json').write_text(json.dumps(inv, indent=2))
(out_dir / 'wave-0-dependency-graph.json').write_text(json.dumps(graph, indent=2))
(out_dir / 'wave-0-test-ledger.json').write_text(json.dumps(ledger, indent=2))
print(f'{len(inv[\"scripts\"])} scripts, {len(inv[\"tests\"])} tests, {len(graph[\"edges\"])} edges')
"
```

- [ ] **Step 6: Manually classify each dependency edge** (same nine-value classification as Revision 2)

- [ ] **Step 7: External-consumer discovery with corrected classification**

```python
# tools/phase-4-5-core-plugin-refactoring/wave0_external_consumers.py
from __future__ import annotations
from pathlib import Path


def find_external_consumer_signals(repo_root: Path) -> dict:
    signals = {"skills_lock_files": [], "claude_settings": [], "marketplace_files": [], "worktrees": []}
    for p in repo_root.rglob("skills-lock.json"):
        signals["skills_lock_files"].append(str(p.relative_to(repo_root)))
    settings = repo_root / ".claude" / "settings.json"
    if settings.exists():
        signals["claude_settings"].append(str(settings.relative_to(repo_root)))
    for p in repo_root.rglob("marketplace.json"):
        signals["marketplace_files"].append(str(p.relative_to(repo_root)))
    worktrees_dir = repo_root / ".worktrees"
    if worktrees_dir.exists():
        signals["worktrees"] = sorted(p.name for p in worktrees_dir.iterdir() if p.is_dir())
    return signals
```

```bash
cd "$repo_root/tools/phase-4-5-core-plugin-refactoring"
python3 -c "
from pathlib import Path
from wave0_external_consumers import find_external_consumer_signals
import json
print(json.dumps(find_external_consumer_signals(Path('$repo_root')), indent=2))
"
```

For each `.worktrees/` entry found, classify using `git worktree list` output cross-referenced against each worktree's own branch state:

```text
REGISTERED_ACTIVE_WORKTREE   — git worktree list shows it, branch has recent commits/open work
REGISTERED_STALE_WORKTREE    — git worktree list shows it, branch's phase is merged/closed
ORPHANED_BROKEN_WORKTREE     — directory exists but git worktree list does not show it (broken registration)
SEPARATE_CLONE                — not a git worktree at all, an independent checkout
UNREGISTERED_COPY             — a copy that was never a proper worktree/clone
UNKNOWN                       — insufficient evidence to classify; requires human review
```

```bash
git worktree list
```

Cross-reference each of the three found (`phase-4-native-sharepoint-skills`, `phase-3-governed-sharepoint-pilot`, `phase-3-0-tenant-capability-discovery`) against this output. All three correspond to **merged, closed phases** per `start-here.md`'s own record — the expected classification is `REGISTERED_STALE_WORKTREE`, but this must be confirmed against the actual `git worktree list` output at Wave 0 execution time, not assumed. A stale worktree's presence of a `skills-lock.json` copy is **not evidence of an active external consumer of the old skill names** — it is evidence only that a worktree exists; the skill-name search (Wave 7 Step 1) still separately checks whether anything inside that worktree's *content* (not merely its presence) references the compatibility skills.

Write `wave-0-external-consumer-report.md` recording each signal, its classification (from the six-value list above), and supporting evidence (`git worktree list` output, last-commit date on that worktree's branch). Where the inspected scope is genuinely exhausted and nothing is found, state `NO_CONSUMER_OBSERVED_IN_INSPECTED_SCOPE` — never an unqualified "no external consumer exists."

**Do not delete, repair, or modify any `.worktrees/` entry during Phase 4.5 planning or execution** — that is out of scope for this plan.

- [ ] **Step 8: Live-reference scan and full-suite baseline confirmation**

Same as Revision 2 Wave 0 Step 10 — record `529 passed, 1 skipped` (or the newly confirmed baseline) and the live-reference classification.

- [ ] **Step 9: Write the Wave 0 report and commit**

```bash
cd "$repo_root"
git add tools/phase-4-5-core-plugin-refactoring/ docs/superpowers/plans/phase-4-5-evidence/
git commit -m "feat(phase4.5-wave0): baseline inventory, dependency graph, test ledger, external-consumer discovery"
git push origin phase-4-5-core-plugin-refactoring
```

**Wave 0 Gate:** Confirmed test baseline recorded. Every dependency edge classified. Test ledger generated. External-consumer signals discovered and classified using the six-value model (not treated as automatic "consumers"). Live-reference report complete. All tooling under `tools/`. Report committed to `phase-4-5-core-plugin-refactoring`.

---

## Wave 1 — Contracts Distribution, Ownership, Migration Strategy, Decision Artifact

**Files:**
- Create: `contracts/python/pyproject.toml`, `src/knowledge_workbench_contracts/{__init__,repo_root,tree_hash,normalized_source_document,analysis_plan,canonical_package,publication_map,rendered_output_profile}.py`
- Create: `contracts/python/tests/test_repo_root.py`, `test_tree_hash.py`
- Create: `docs/superpowers/plans/phase-4-5-evidence/wave-1-decisions.json`, `wave-1-analyze-structure-split-decision.md`, `wave-1-shared-contract-decision.md`
- Create: `docs/architecture/phase-4-5-target-architecture.md`
- Create: `tools/phase-4-5-core-plugin-refactoring/dependency_boundary.py`, `isolated_install_check.py` + tests, including the negative-control fixtures
- Modify: `docs/superpowers/plans/phase-4-5-evidence/wave-0-test-ledger.json` (fill `proposed_owner_domain`)

**Interfaces:** Consumes Wave 0's artifacts. Produces `wave-1-decisions.json` and the built, installable `knowledge_workbench_contracts` wheel — consumed by every later wave.

**Rollback:** Standard revert procedure. Pre-wave commit = Wave 0's final commit.

**Note (specification alignment):** the spec amendment (§13b) is already applied to the specification file as a prerequisite to this plan revision — there is no "Step 0: amend spec" task in this wave (unlike Revision 2, which incorrectly deferred it here).

- [ ] **Step 1: Resolve the `analyze_structure.py` split** — same content as Revision 2 Wave 1 Step 1, unchanged (a code-organization decision, independent of the packaging correction).

- [ ] **Step 2: Resolve `contracts.py`/`cli.py`/`convert.py`/`atomic_output.py` disposition** — same content as Revision 2 Wave 1 Step 2, with one correction: `contracts.py`'s five dataclasses map to `knowledge_workbench_contracts/*.py` (the installable distribution), not a repository-root directory.

- [ ] **Step 3: Write failing tests for the contracts distribution, then implement it**

```python
# contracts/python/tests/test_tree_hash.py
from knowledge_workbench_contracts.tree_hash import compute_tree_hash

def test_tree_hash_is_deterministic(tmp_path):
    (tmp_path / "a.txt").write_text("hello")
    assert compute_tree_hash(tmp_path) == compute_tree_hash(tmp_path)

def test_tree_hash_changes_when_content_changes(tmp_path):
    (tmp_path / "a.txt").write_text("hello")
    h1 = compute_tree_hash(tmp_path)
    (tmp_path / "a.txt").write_text("goodbye")
    assert compute_tree_hash(tmp_path) != h1
```

```python
# contracts/python/tests/test_repo_root.py
# NOTE: repo_root.py is exported for repository-tooling use only (Wave 6's
# integration test evidence generation) — this test proves it works, but
# Wave 2-5's dependency-boundary check independently proves no plugin
# production code imports it (see Wave 2 Step 9).
from pathlib import Path
from knowledge_workbench_contracts.repo_root import find_repo_root

def test_finds_repo_root_marker(tmp_path):
    (tmp_path / ".git").mkdir()
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    assert find_repo_root(nested, markers=(".git",)) == tmp_path
```

Run (from a fresh venv or with `pip install -e contracts/python` first — see Step 4): FAIL with `ModuleNotFoundError`.

Implement `contracts/python/pyproject.toml` (per the Contract Distribution Model template above) and the eight `src/knowledge_workbench_contracts/*.py` modules (schema dataclasses + `validate()` for the five contracts, plus `tree_hash.py` and `repo_root.py` exactly as specified above).

```bash
cd "$repo_root/contracts/python"
python3 -m venv .venv-wave1 && source .venv-wave1/bin/activate
pip install -e . pytest
pytest tests/ -v
```
Expected: PASS (3 tests). Deactivate and remove the throwaway venv after confirming: `deactivate && rm -rf .venv-wave1`.

- [ ] **Step 4: Write and pass the dependency-boundary checker**

```python
# tools/phase-4-5-core-plugin-refactoring/dependency_boundary.py
from __future__ import annotations
import ast
from pathlib import Path

def check_no_prohibited_imports(plugin_src_dir: Path, prohibited_module_names: list[str]) -> list[dict]:
    violations = []
    for path in sorted(plugin_src_dir.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            module = None
            if isinstance(node, ast.ImportFrom) and node.module:
                module = node.module.split(".")[0]
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split(".")[0]
            if module in prohibited_module_names:
                violations.append({"file": str(path), "import": module, "line": node.lineno})
    return violations

def check_no_repo_root_import_in_production_code(plugin_src_dir: Path) -> list[dict]:
    """Specification §13b's explicit prohibition: repo_root is tooling-only."""
    violations = []
    for path in sorted(plugin_src_dir.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if "repo_root" in text and "import" in text:
            violations.append({"file": str(path), "reason": "production code must not import repo_root"})
    return violations
```

Test both functions (positive + negative cases), matching Revision 2's dependency-boundary test pattern, adding one new test for `check_no_repo_root_import_in_production_code`.

- [ ] **Step 5: Build the isolated-install harness and its two negative-control fixtures**

Implement `isolated_install_check.py` exactly as specified in the Isolated-Install Harness section above. Build the two negative-control fixture plugins under `tools/phase-4-5-core-plugin-refactoring/tests/fixtures/broken_plugin_undeclared_import/` (imports an uninstalled upstream module) and `broken_plugin_missing_dependency/` (imports the contracts distribution without declaring it in `pyproject.toml`) — each a minimal 2-file `pyproject.toml` + `src/<name>/__init__.py`. Run `test_isolated_install_check.py`'s two tests against these fixtures and confirm both correctly fail/raise.

- [ ] **Step 6: Human decision checkpoint — produce `wave-1-decisions.json`**

**STOP.** Present for explicit human approval:

```json
{
  "contract_versions": {
    "normalized-source-document": "v1", "analysis-plan": "v1",
    "canonical-package": "v1", "publication-map": "v1", "rendered-output-profile": "v1"
  },
  "contracts_distribution_name": "knowledge-workbench-contracts",
  "contracts_distribution_version": "0.1.0-alpha.1",
  "plugin_starting_versions": {
    "source-document-extraction": "0.1.0-alpha.1", "knowledge-analysis": "0.1.0-alpha.1",
    "canonical-knowledge": "0.1.0-alpha.1", "knowledge-publication": "0.1.0-alpha.1"
  },
  "marketplace_adoption": "NOT_APPLICABLE_WITH_DECISION",
  "analyze_structure_split_approved": true,
  "shared_contract_decision_approved": true,
  "original_skill_dispositions": {
    "analyze-document": "PROPOSED_DISPOSITION: TEMPORARY_COMPATIBILITY_WRAPPER",
    "convert-document": "PROPOSED_DISPOSITION: TEMPORARY_COMPATIBILITY_WRAPPER",
    "render-content": "PROPOSED_DISPOSITION: TEMPORARY_COMPATIBILITY_WRAPPER",
    "orchestrate-conversion": "PROPOSED_DISPOSITION: REPLACED_AND_RETIRED"
  }
}
```

Every value is a proposal; record the human's actual decision, which may differ. Using the approved `original_skill_dispositions`, fill `wave-0-test-ledger.json`'s `proposed_owner_domain` for every test.

- [ ] **Step 7: Target-architecture diagram, Wave 1 report, commit**

```bash
cd "$repo_root"
git add contracts/python/ docs/superpowers/plans/phase-4-5-evidence/wave-1-*.json docs/superpowers/plans/phase-4-5-evidence/wave-1-*.md docs/superpowers/plans/phase-4-5-evidence/wave-0-test-ledger.json docs/architecture/phase-4-5-target-architecture.md tools/phase-4-5-core-plugin-refactoring/dependency_boundary.py tools/phase-4-5-core-plugin-refactoring/isolated_install_check.py tools/phase-4-5-core-plugin-refactoring/tests/
git commit -m "feat(phase4.5-wave1): installable contracts distribution, dependency-boundary and isolated-install harnesses, approved decisions"
git push origin phase-4-5-core-plugin-refactoring
```

**Wave 1 Gate:** `knowledge_workbench_contracts` wheel builds and installs cleanly in a throwaway venv; its tests pass. Dependency-boundary checker (including the `repo_root` production-code prohibition) implemented and tested. Isolated-install harness implemented, with both negative controls proven to correctly fail. `wave-1-decisions.json` committed with human-approved values. `wave-0-test-ledger.json` fully assigned. Target architecture diagram committed.

---

## Waves 2-5 — Extract Each Plugin as a Real Installable Package

Each of the four extraction waves (source-document-extraction, knowledge-analysis, canonical-knowledge, knowledge-publication) follows this identical structure — detailed once here, applied per-plugin with that plugin's specific files/functions from the Known File Inventory (unchanged domain assignments from Revision 2).

> **Correction (2026-08-01, per spec §13d):** Steps 2 and 4 below are amended from the original
> (superseded) shared-contracts-dependency model. See
> `docs/superpowers/plans/phase-4-5-evidence/wave-2-contract-materialization-correction.md`.

**Common step sequence per wave:**

1. Scaffold `plugins/<name>/{pyproject.toml, src/<import_name>/, references/contracts/, skills/, tests/{unit,fixtures}}`, with `pyproject.toml`'s `version` read from `wave-1-decisions.json`, never hardcoded, and `dependencies = []` unless a genuine third-party (PyPI) package is required — **never** a workbench-family distribution.
2. If this plugin **produces** a contract: write its authoritative schema + `validate()` inside this plugin's own `src/<import_name>/contracts/<contract>.py`, plus human-readable docs at `references/contracts/<contract>.md`. If this plugin **consumes** a contract another plugin produces: generate/hand-sync a local copy of the schema subset needed into this plugin's own `src/<import_name>/contracts/<contract>.py`, recording authoritative source path, contract version, source SHA-256, generated SHA-256, and the generation command in a comment header or sidecar file, with a drift test. Either way, also generate that plugin's input contract fixture (e.g. `normalized-source-document` for knowledge-analysis) by actually running the upstream plugin's installed public function — stored under **both** `tests/contracts/fixtures/<contract>/v1/` (repository-level evidence) and a minimal copy under this plugin's own `tests/fixtures/` (for isolated/installed test runs).
3. Write the failing test for that plugin's Public Interface Contract function, importing via the real package name (`from source_document_extraction.extraction import extract_and_normalize`), never a bare/sys.path-hacked name.
4. Move/adapt the assigned legacy scripts into `src/<import_name>/`, fixing internal imports to use the package-relative form (`from .pandoc_fixes import images` etc.) and importing contract types via this plugin's own **plugin-local** contract module (`from .contracts.canonical_package import validate`) — never `from knowledge_workbench_contracts...` and never a pip dependency on another plugin's package.
5. Run the test to pass, using `pip install -e .` in a scratch venv during development (not a permanent artifact — cleaned up before commit).
6. Migrate every `wave-0-test-ledger.json` entry assigned to this plugin's domain — `git mv`, fix imports to the new package-relative form, record in `wave-N-test-migration-ledger.md`.
7. Add the compatibility shim in `plugins/docx-to-content/scripts/<old-module>.py` — this shim is exempt from the "no sys.path hacking" rule since it exists specifically to bridge the *old, still-`sys.path`-based* `docx-to-content` plugin during migration, not to define the new plugin's own import model:
   ```python
   # Compatibility shim (Phase 4.5, retire per wave-1-decisions.json) — imports
   # from the now-installed new package, not from a sys.path-injected checkout.
   from source_document_extraction.extraction import parse_headings, detect_defect_signals  # noqa: F401
   ```
   (Requires the new plugin to be `pip install -e`'d into whatever environment runs the old plugin's tests during the transition — document this explicitly in the wave's report as a transition-only dependency, removed in Wave 7/8.)
8. Write the skill(s) and README (README now documents the real `pip install <plugin only>` command and package name, with no other package installed first). Any skill-local `references/`/non-Python `scripts/`/`assets/` copy is created via `.agents/skills/symlink-manager/scripts/symlink_manager.py` (never `ln -s` directly, never a hand-copy).
9. Run the dependency-boundary check (`check_no_prohibited_imports` + `check_no_repo_root_import_in_production_code`) against `src/<import_name>/`, plus `check_no_workbench_family_dependency()` against `pyproject.toml`.
10. Run the **Plugin Self-Containment Gate**: `isolated_install_check.py --plugin <name> --import-package <import_name>` — build wheel, install *only that wheel* (plus third-party deps) in a clean venv, confirm no other workbench distribution (sibling plugin, contracts, or runtime) is installed, confirm no repository-root lookup occurs, import outside pytest from site-packages, locate bundled contract references, validate representative output against the bundled schema, run this plugin's tests from the installed distribution. A coordinated multi-package install does not satisfy this gate.
11. Commit named files explicitly (never `git add -A`); push.

**Wave-specific Public Interface Contract function and consumed/produced contract, per plugin (unchanged from Revision 2's domain assignments):**

| Wave | Plugin | Import package | Function | Consumes | Produces |
|---|---|---|---|---|---|
| 2 | source-document-extraction | `source_document_extraction` | `extract_and_normalize` | — | `normalized-source-document` |
| 3 | knowledge-analysis | `knowledge_analysis` | `recommend_from_normalized` | `normalized-source-document` | `analysis-plan` |
| 4 | canonical-knowledge | `canonical_knowledge` | `build_canonical_package` | `analysis-plan` | `canonical-package`, `publication-map` |
| 5 | knowledge-publication | `knowledge_publication` | `render` | `canonical-package`, `publication-map` | `rendered-output-profile` |

**Wave 4's additional requirement (corrected per §13d):** since `canonical-knowledge` now owns its
`canonical-package` contract materialized at its own
`src/canonical_knowledge/contracts/canonical_package.py` (schema-only: dataclass + `validate()`),
prove the schema module and the plugin's own implementation module (e.g.
`src/canonical_knowledge/package.py`, carrying the actual `CanonicalPackage` construction logic)
are genuinely distinct, non-colliding modules within the same package:

```python
def test_contract_schema_and_implementation_are_distinct_modules():
    import canonical_knowledge.contracts.canonical_package as schema
    import canonical_knowledge.package as impl
    assert schema.__name__ != impl.__name__
    assert hasattr(schema, "validate")
    assert not hasattr(schema, "CanonicalPackage")  # the implementation class stays in impl only
```

**Rollback (each of Waves 2-5):** Standard revert procedure. Pre-wave commit = the previous wave's final commit.

**Gate (each of Waves 2-5):**
- `isolated_install_check.py --plugin <name> --import-package <import_name>` exits 0 — wheel builds, installs **only that wheel** (plus third-party deps, zero workbench-family packages) in a clean venv, imports outside pytest from `site-packages` (not the checkout), confirms no other workbench distribution installed (sibling plugin, contracts, or runtime), tests pass. The full Plugin Self-Containment Gate (§13d) is satisfied, not merely a coordinated multi-package install.
- Zero dependency-boundary violations, including zero `repo_root` imports in production code and zero `check_no_workbench_family_dependency()` violations in `pyproject.toml`.
- Old `docx-to-content` suite still green via the compatibility shim (which itself now depends on the new plugin being `pip install -e`'d — documented, not hidden).
- Every ledger-assigned test migrated and recorded.
- README/skill(s) written with real install instructions.
- (Wave 4 only) CEIS canonical output confirmed byte-identical. (Wave 5 only) CEIS rendered output confirmed byte-identical, and Wave 5's `combined-environment` collision test is deferred to Wave 6 (needs all four wheels, not available until Wave 5 completes) — noted here so Wave 5's own gate does not falsely require it.

---

## Wave 6 — Repository-Wide Reconciliation

**Files:**
- Create: `docs/superpowers/plans/phase-4-5-evidence/wave-6-final-test-migration-ledger.md`, `wave-6-final-fixture-migration-ledger.md`, `wave-6-golden-master-manifest.json`
- Create: `tools/phase-4-5-core-plugin-refactoring/combined_install_check.py` + test
- Create: `tests/golden-master/ceis/manifest.json` (evidence-safety gated)
- Create: `tests/integration/test_full_ceis_pipeline_across_plugins.py` (fully specified, non-skippable at wave closure)
- Modify: `CLAUDE.md`, `DEPENDENCIES.md`, `start-here.md`, `docs/architecture/phase-4-5-target-architecture.md`

**Rollback:** Standard revert procedure. Pre-wave commit = Wave 5's final commit.

- [ ] **Step 1: Consolidate test migration ledgers; reconcile the 45-test total** — same as Revision 2 Wave 6 Step 1.

- [ ] **Step 2: Evidence-safety classification** — same as Revision 2 (default: reference `runs/ceis-manual-v2/` by path+hash, do not duplicate 248MB tracked evidence).

- [ ] **Step 3: Combined-environment collision test**

> **Corrected per §13d:** no contracts/runtime wheel is built or installed here — under the
> materialized-contract model each plugin is self-contained, so the combined-install proof is
> "these four independently-standalone plugins also don't collide when co-installed," not "these
> plugins plus a shared distribution work together."

```python
# tools/phase-4-5-core-plugin-refactoring/combined_install_check.py
"""Installs all four plugin wheels (no shared contracts/runtime wheel --
each plugin materializes its own contract/runtime code per spec §13d) into
ONE clean venv, proving zero namespace/dependency collisions and that every
plugin's own test suite still passes in the shared environment."""
import subprocess, sys, tempfile, venv
from pathlib import Path
from isolated_install_check import build_wheel, check_no_workbench_family_dependency

def check_combined_install(repo_root: Path) -> dict:
    plugins = ["source-document-extraction", "knowledge-analysis", "canonical-knowledge", "knowledge-publication"]
    for p in plugins:
        if check_no_workbench_family_dependency(repo_root / "plugins" / p):
            raise AssertionError(f"{p} declares a prohibited workbench-family dependency")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        venv_dir = tmp_path / "venv"
        venv.EnvBuilder(with_pip=True).create(venv_dir)
        pip, python = venv_dir / "bin" / "pip", venv_dir / "bin" / "python"
        dist_dir = tmp_path / "dist"; dist_dir.mkdir()
        wheels = [build_wheel(repo_root / "plugins" / p, dist_dir) for p in plugins]
        subprocess.run([str(pip), "install", *[str(w) for w in wheels], "pytest"], check=True, capture_output=True)
        results = {}
        for p in plugins:
            r = subprocess.run([str(python), "-m", "pytest", str(repo_root / "plugins" / p / "tests"), "-v"], capture_output=True, text=True)
            results[p] = r.returncode
        return results
```

Run and confirm all four return code 0 in the shared environment.

- [ ] **Step 4: Write and run the full, non-placeholder integration test**

Same structure as Revision 2 Wave 6 Step 3, with imports corrected to real package paths:

```python
from source_document_extraction.extraction import extract_and_normalize
from knowledge_analysis.analysis import recommend_from_normalized
from canonical_knowledge.package import build_canonical_package
from knowledge_publication.renderers.multipage_markdown import render
from knowledge_workbench_contracts.tree_hash import compute_tree_hash
```

The `pytest.skip` branch for the missing gitignored confirmed-plan (documented, real constraint per `start-here.md`) is retained for **ordinary development runs only**. **Wave 6 cannot close on a skip** — before the wave's gate is evaluated, the implementer must have actually populated `temp/ceis-manual-analysis/conversion-plan.confirmed.json` (via a real `analyze`+`confirm` run) and executed the full non-skip assertion path at least once, recording the actual computed hashes in `wave-6-golden-master-manifest.json`.

- [ ] **Step 5: Update documentation; run the complete gate; commit**

```bash
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
for p in source-document-extraction knowledge-analysis canonical-knowledge knowledge-publication; do
  cd "$repo_root/plugins/$p" && python3 -m pip install -e . >/dev/null && python3 -m pytest tests/ -v --tb=short 2>&1 | tail -5
done
cd "$repo_root/plugins/docx-to-content" && python3 -m pytest tests/ -v --tb=short 2>&1 | tail -5
cd "$repo_root" && python3 -m pytest tests/ -v --tb=short 2>&1 | tail -10
cd "$repo_root/tools/phase-4-5-core-plugin-refactoring" && python3 -c "
from pathlib import Path
from combined_install_check import check_combined_install
results = check_combined_install(Path('$repo_root'))
assert all(rc == 0 for rc in results.values()), results
print('Combined install: all four plugins pass', results)
"
```

```bash
cd "$repo_root"
git add tests/golden-master/ tests/integration/test_full_ceis_pipeline_across_plugins.py docs/superpowers/plans/phase-4-5-evidence/wave-6-*.md docs/superpowers/plans/phase-4-5-evidence/wave-6-*.json tools/phase-4-5-core-plugin-refactoring/combined_install_check.py CLAUDE.md DEPENDENCIES.md start-here.md docs/architecture/phase-4-5-target-architecture.md
git commit -m "feat(phase4.5-wave6): repository-wide reconciliation, combined-install collision test, non-skipped golden-master proof"
git push origin phase-4-5-core-plugin-refactoring
```

**Wave 6 Gate:** 45/45 tests reconciled. Evidence-safety classification applied, no unauthorized duplication. Combined four-distribution install passes with zero collisions. Integration test's golden-master assertion executed with **zero skips** and real recorded hashes — a skip at this point blocks the wave. All suites green (isolated per-plugin, old-plugin compatibility, repository-level). Documentation updated. Wave 6 report committed.

---

## Wave 7 — Retire Approved Compatibility Facades

**Files:** Modify `plugins/docx-to-content/scripts/*.py` (remove shims, now removing the transition-only `pip install -e` dependency on the new packages too), `plugins/docx-to-content/skills/*/SKILL.md`. Create `wave-7-compatibility-retirement-record.md`.

**Rollback:** Standard revert procedure. Pre-wave commit = Wave 6's final commit.

- [ ] **Step 1: Re-run external-consumer discovery** — re-classify the `.worktrees/` entries and any other signal using the six-value model, re-confirm against Wave 1's approved dispositions. A worktree previously classified `REGISTERED_STALE_WORKTREE` blocks this wave only if its branch shows new activity since Wave 0's classification — re-check `git worktree list` and each worktree's last-commit date, don't assume staleness persists.
- [ ] **Step 2: Apply confirmed disposition per skill** — same as Revision 2.
- [ ] **Step 3: Run the complete repository suite; write retirement record; commit** — same structure as Revision 2, using the real installed-package test commands from Wave 6 Step 5.

**Wave 7 Gate:** Same as Revision 2, plus: worktree re-classification confirms no `.worktrees/` entry has changed status since Wave 0.

---

## Wave 8 — Remove `plugins/docx-to-content/` After Explicit Approval

**Files:** Delete `plugins/docx-to-content/`. Create `wave-8-removal-gate-checklist.md`, `phase-4-5-exit-statement.md`. Modify `start-here.md`.

**Rollback:** Standard revert procedure — **this wave is the one place a hard reset is most plausible as the `DISPOSABLE_UNPUBLISHED_WORKTREE_OPTION`** if the removal commit has not yet been pushed and the worktree is confirmed clean; otherwise, use the standard revert (re-adding the deleted directory via `git revert`).

- [ ] **Step 1: Verify the removal gate checklist**, extended for packaging:

```text
[ ] wave-6-final-test-migration-ledger.md / fixture ledger: zero unresolved entries
[ ] Contract distribution tests pass in isolation
[ ] Combined four-distribution install still passes (re-run combined_install_check.py)
[ ] Golden-master integration test passes with zero skips, real hashes recorded
[ ] Four plugin wheels build and install cleanly, each with zero upstream-plugin cross-installs
[ ] wave-0-live-reference-report.md re-scanned: zero remaining LIVE_REFERENCE to docx-to-content
[ ] wave-7 external-consumer re-scan: zero unaccounted-for consumers, including re-classified .worktrees/
[ ] No package pyproject.toml/metadata references plugins/docx-to-content
```

- [ ] **Step 2: STOP — human removal approval.**

- [ ] **Step 3: Remove the old plugin directory; Step 4: fresh-install proof, final verification, exit statement, commit.**

```bash
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
git rm -r plugins/docx-to-content/
ls plugins/docx-to-content 2>&1  # must report "No such file or directory"

# Fresh-installation proof: clone-equivalent check from the final repository state
for p in source-document-extraction knowledge-analysis canonical-knowledge knowledge-publication; do
  cd "$repo_root/tools/phase-4-5-core-plugin-refactoring"
  python3 isolated_install_check.py --plugin "$p" --import-package "$(echo $p | tr '-' '_')"
done

grep -rn "plugins/docx-to-content" --include="*.md" --include="*.py" --include="*.toml" . 2>/dev/null | grep -v "HISTORICAL\|GOLDEN_MASTER"
```

```bash
git add -- plugins docs/superpowers/plans/phase-4-5-evidence start-here.md
git status --short   # confirm nothing unrelated is staged before committing
git commit -m "feat(phase4.5-wave8): remove obsolete docx-to-content plugin, Phase 4.5 complete

Human removal approval: <approver, date>"
git push origin phase-4-5-core-plugin-refactoring
```

**Wave 8 Gate (= Phase 4.5 exit gate):** All 17 success criteria (spec §23) satisfied, now including real installability proof (not sys.path). Fresh-install check passes for all four plugins from the final repository state, with no reference to `docx-to-content` anywhere in package metadata. Repository clean. `plugins/docx-to-content/` fully removed. Exit statement recorded. **This plan does not merge the branch.**

---

## Self-Review Notes (Revision 3)

**Reviewer's 9 remaining findings — resolution map:** #1 Packaging Model section (real `src/`-layout + `pyproject.toml`, no `conftest.py` production imports); #2 Contract Distribution Model (`contracts/python/`, independently installable, no repository-root discovery); #3 fixture separation (repository-level vs. plugin-packaged); #4 Isolated-Install Harness (real `build`→`pip install`→import-outside-pytest→metadata check, plus two negative controls and a combined-environment collision test); #5 Specification Amendment applied to the spec file's §13b **before** this plan revision (see Specification Alignment Statement); #6 Rollback Model (revert-based standard procedure, hard reset demoted to a narrowly-conditioned exception); #7 Task 12 deletions fully investigated (hashes verified, user-authorized, excluded from every commit's staged-files list — never `git add -A`); #8 external-consumer classification (six-value model, `NO_CONSUMER_OBSERVED_IN_INSPECTED_SCOPE` phrasing, worktrees never touched); #9 Wave 6's golden-master test cannot close on a skip (explicit non-skip requirement with real recorded hashes).

**Placeholder scan:** zero `pass`/`TODO`/"confirm signature later" remain in executable steps beyond the one documented, real-constraint `pytest.skip` (permitted only for ordinary development, explicitly prohibited at Wave 6 closure).

**Hardcoded-path scan:** every command uses `repo_root="$(git rev-parse --show-toplevel)"`; the isolated-install and combined-install harnesses use `Path` objects derived from that same call, never a literal filesystem path.

**Plan/spec consistency check:** every packaging claim in this plan (`src/`-layout, `pyproject.toml`, `knowledge_workbench_contracts`, isolated-install-as-wheel-installation) traces to specification §13b, applied before this plan revision — no plan-level packaging decision is invented without a corresponding spec basis.
