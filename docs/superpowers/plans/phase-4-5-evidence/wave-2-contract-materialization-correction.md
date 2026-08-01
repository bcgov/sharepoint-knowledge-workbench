# Wave 2 Correction — Plugin-Local Contract/Runtime Materialization

**Date:** 2026-08-01
**Status:** ✓ APPROVED (human decision, 2026-08-01) — supersedes
`wave-1-shared-contract-decision.md`'s approved shared-distribution model
for contracts, and reverses the plan's assumption that a plugin may
declare a pip dependency on `knowledge-workbench-contracts` or
`knowledge-workbench-runtime`.

## What was wrong

Wave 1 approved, and Wave 2 initially implemented, a model where every
domain plugin's `pyproject.toml` declares a pip dependency on a shared
`knowledge-workbench-contracts` distribution (and, for later waves,
`knowledge-workbench-runtime`) living outside `plugins/` at the repository
root (`contracts/python/`, `runtime/python/`).

This conflicts with this repository's own plugin-independence rule
(`.agent/rules/plugin-architecture-policy.md` §1.3: *"If a user runs
`npx skills add <some-plugin>`, that plugin MUST function completely in
isolation... It cannot crash or halt because [something outside it]
happens to be missing"*) and with basic pip-distribution reality:
`knowledge-workbench-contracts` is not published to any package index, so
`pip install source-document-extraction` in true isolation — the exact
scenario the isolated-install harness exists to prove — would fail to
resolve its own declared dependency. The original harness masked this by
always co-installing the contracts wheel alongside every plugin wheel, so
it proved "these two wheels work together," not "this plugin is
standalone-installable."

A subtler point, worth recording so it isn't rediscovered later: the
originally-proposed fix (file-level symlinks via `symlink_manager.py`,
matching `symlink-cross-platform.md`'s marketplace-skill convention)
**cannot fix this specific problem either** — `setuptools build_meta`
bundles regular files into a wheel; a symlink pointing outside the package
tree is not portably preserved through a wheel build. Symlinks remain the
correct mechanism for skill-local *references*/*scripts* copies (see
below), but the underlying Python contract/runtime *code* must be a real,
physically-included module inside each plugin's own package — generated or
hand-synced from an authoritative source, not linked.

## Corrected model

**Producer plugins own the authoritative contract.** Each contract's
schema + `validate()` lives inside the plugin that *produces* it, as a
real module in that plugin's own `src/<import_name>/contracts/` package —
not in a shared distribution:

| Contract | Producer plugin | Authoritative module |
|---|---|---|
| `normalized-source-document` | `source-document-extraction` | `src/source_document_extraction/contracts/normalized_source_document.py` |
| `analysis-plan` | `knowledge-analysis` (Wave 3) | `src/knowledge_analysis/contracts/analysis_plan.py` |
| `canonical-package`, `publication-map` | `canonical-knowledge` (Wave 4) | `src/canonical_knowledge/contracts/{canonical_package,publication_map}.py` |
| `rendered-output-profile` | `knowledge-publication` (Wave 5) | `src/knowledge_publication/contracts/rendered_output_profile.py` |

Human-readable documentation for each contract lives alongside the
producer's code at `plugins/<producer>/references/contracts/<contract>.md`
— a real file (see Skill Packaging below for how it also reaches the
skill folder).

**Consumer plugins carry their own copy, never a live import.** A consumer
(e.g. `knowledge-analysis` consuming `normalized-source-document`) does
**not** `pip install` or `import` the producer plugin's package. It
carries its own plugin-local copy of the subset of the schema it actually
needs (schema-version check + required-field validation), generated or
hand-synced from the producer's authoritative module during development.
Each generated copy must record, as a comment header or sidecar file:
authoritative source path, contract version, source SHA-256, generated
SHA-256, and the generation command used — with a test that fails if the
generated copy diverges from what regenerating it now would produce.
(No consumer plugin exists yet as of this correction — Wave 3 is the first
to implement this pattern for real, once `knowledge-analysis` is built.)

**Cross-plugin compatibility is proven by tests, not imports:** a fixed
`schema_version` string, a recorded schema hash, and a producer-side test
+ consumer-side test that both validate the same
`tests/contracts/fixtures/<contract>/v1/` repository-level fixture (this
directory's role is unchanged — shared interoperability-test fixtures
only, never installed, never a runtime dependency).

**`pyproject.toml` dependency lists must never contain a workbench-family
entry** (`knowledge-workbench-contracts`, `knowledge-workbench-runtime`,
or a sibling plugin's distribution name). Enforced mechanically by
`isolated_install_check.py`'s `check_no_workbench_family_dependency()`
(static) and its runtime install/import/test proof (dynamic) — see below.

## Runtime utility correction (`atomic_output.py`)

Wave 1's `knowledge-workbench-runtime` distribution (`runtime/python/`) is
corrected the same way: `create_staging_dir`/`promote` will be
materialized as a real module inside each of `canonical-knowledge` and
`knowledge-publication` (Waves 4/5) when those plugins are built — not
imported from a shared distribution. As of this correction, **no plugin
yet consumes `runtime/python/`** (`atomic_output.py` still lives in
`docx-to-content`, unmoved until Waves 4/5), so no plugin code changes are
needed today; this is a governance-only correction to prevent Wave 4/5
from repeating Wave 2's mistake.

## Disposition of the top-level directories

| Directory | Disposition |
|---|---|
| `contracts/python/` | `DEVELOPMENT_CODEGEN_SOURCE` — may remain as a reviewed reference/generation source during repository development (e.g. to mechanically diff a consumer's generated copy against it), but is **not** a required runtime dependency of any installed plugin. `source-document-extraction`'s dependency on it has been removed (this correction). |
| `runtime/python/` | `DEVELOPMENT_CODEGEN_SOURCE` — same status; zero current consumers. |

Neither directory is deleted by this correction — deleting still-useful
development source without replacing its function would violate
`.agent/rules/self-evolution-policy.md`'s no-autonomous-deletion rule.
Removal (`REMOVE_AFTER_PLUGIN_MATERIALIZATION`) requires: every intended
consumer plugin has its own materialized copy, an equivalence/compatibility
test suite proves no drift, and explicit human approval — tracked as a
Wave 8-style gate, not decided here.

## Skill packaging (unchanged principle, now applied correctly)

Every skill must contain every resource it references at its installed
location. `plugins/<plugin>/references/<x>` and `plugins/<plugin>/scripts/<x>`
(when scripts exist outside the pip package, e.g. non-Python helper
scripts) are the canonical masters; skill-local copies are **file-level
symlinks created via `.agents/skills/symlink-manager/scripts/symlink_manager.py`**
(never `ln -s` directly, never a hand-copy) per `.agent/rules/symlink-cross-platform.md`.
This applies to `references/`/`assets`/non-Python `scripts/` — it does
**not** apply to the plugin's installable Python package itself, which
must be a real file for wheel-building reasons (see "What was wrong"
above). `source-document-extraction`'s `skills/extract-docx/references/contracts/normalized-source-document.md`
is symlinked to `plugins/source-document-extraction/references/contracts/normalized-source-document.md`
via `symlink_manager.py` as the first real instance of this pattern.

## Mandatory Plugin Self-Containment Gate (added to the Waves 2-5 common sequence)

Before any wave changed by a plugin extraction is reported complete, for
every plugin that wave touched:

```text
PLUGIN SELF-CONTAINMENT GATE
- build the exact distributable artifact (wheel);
- install ONLY that artifact and third-party (PyPI) dependencies into a
  clean venv;
- confirm no unpublished sibling workbench package is required or present;
- confirm no repository-root lookup occurs (contracts/, runtime/,
  and the monorepo checkout are absent from that venv/sys.path);
- import the plugin's public API outside pytest, from site-packages;
- locate the plugin's bundled contract references/schema;
- validate representative produced output against that bundled schema;
- execute required runtime utilities where applicable (e.g. atomic
  output promotion, once a plugin owns that code);
- run the plugin's own tests from the installed distribution;
- confirm every installed skill's referenced scripts/references resolve
  at the skill-relative path a real installer would produce (symlinks
  materialized, not broken).
```

A coordinated multi-package install (the old harness's behavior) does
**not** satisfy this gate — it proves packages work together, not that one
plugin is independently distributable. This gate is now permanently part
of the Waves 2-5 common step sequence's Step 10
(`docs/superpowers/plans/2026-08-01-phase-4-5-core-knowledge-plugin-domain-refactoring.md`)
and of each wave's exit gate.

## Evidence this correction actually holds for `source-document-extraction`

- `pyproject.toml` `dependencies = []` — zero workbench-family entries.
- `isolated_install_check.py --plugin source-document-extraction
  --import-package source_document_extraction`: exit 0, real wheel build,
  clean venv, **no contracts/runtime wheel built or installed**, `pip
  freeze` contains only `source-document-extraction` and third-party
  packages, import resolves from `site-packages`, 78/78 tests pass.
- Manual confirmation: `import knowledge_workbench_contracts` fails
  (`ImportError`) in that same venv.
- `docx-to-content`'s compatibility-shim suite unaffected (452 passed/1
  skipped, unchanged) — it never imported `contracts.py`'s replacement
  through `source_document_extraction`, only the moved
  observation/extraction functions.

## Governance documents amended alongside this correction

- `docs/superpowers/specs/phase-4-5-core-knowledge-plugin-domain-refactoring-spec.md`
  §13b/§13c — amended to describe plugin-local contract/runtime
  materialization instead of shared pip distributions, and to add the
  Plugin Self-Containment Gate.
- `docs/superpowers/plans/phase-4-5-evidence/wave-1-decisions.json` —
  `shared_contract_decision_approved` flipped to `false` with a
  `superseded_by` pointer to this document; `contracts_distribution_*` and
  `runtime_distribution_*` fields annotated `DEVELOPMENT_CODEGEN_SOURCE`.
- `docs/superpowers/plans/phase-4-5-evidence/wave-1-shared-contract-decision.md` —
  superseded-notice header added, content retained for the record.
- `docs/superpowers/plans/2026-08-01-phase-4-5-core-knowledge-plugin-domain-refactoring.md` —
  Packaging Model / Contract Distribution Model / Isolated-Install Harness
  sections amended; Waves 2-5 common step sequence's Step 10 updated to the
  Plugin Self-Containment Gate.
- `start-here.md` — records this correction and that Wave 2 was reopened
  and re-closed under the corrected model.
