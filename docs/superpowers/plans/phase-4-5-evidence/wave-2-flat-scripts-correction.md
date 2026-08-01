# Wave 2 Correction — Flat `scripts/` Layout, Cohesive Subfolders Only

**Date:** 2026-08-01
**Status:** ✓ APPROVED (human decision, 2026-08-01) — supersedes the
`src/<import_name>/` nested-package layout `wave-2-contract-materialization-correction.md`
still showed. This document is the durable convention going forward for
every plugin's `scripts/` directory (this repo's own `plugins/*`, not the
marketplace-skill model described in `CLAUDE.md`'s Skill Development
Protocol section).

## The rule

1. **One canonical `scripts/` directory per plugin**, at the plugin root
   (`plugins/<plugin>/scripts/`) — not nested under a package-name
   subfolder (`scripts/<plugin_name>/...` is **not approved** unless a
   verified packaging requirement makes that additional namespace
   genuinely unavoidable; flat bare-module imports satisfy real pip
   installability just as well, proven below).
2. **Group into a subfolder only when the grouping is meaningful** — a
   cohesive family of multiple related modules. A single-purpose module
   stays flat at `scripts/` root. Do not create empty or speculative
   taxonomy folders.
3. **Skills receive only what they need, via managed file-level symlinks**
   — `.agents/skills/symlink-manager/scripts/symlink_manager.py create
   --src <plugin-root-file> --dst <skill-folder-file>`, never `ln -s`
   directly, never a hand-copy. This applies to `references/`, `assets/`,
   and any non-Python `scripts/` a skill invokes via Bash — **not** to the
   plugin's installable Python package itself (see "Why not `src/`" below).
4. **Bare top-level module/package names must be globally unique across
   every plugin that might ever be co-installed or run in the same
   process** (see the `contracts` collision below) — this is the actual
   cost of dropping the `src/<import_name>/` namespace, and the reason
   naming still needs real thought, not just "flatten everything."

## Concrete example — `source-document-extraction`

```
plugins/source-document-extraction/
├── scripts/
│   ├── extraction.py        # public interface: extract_and_normalize()
│   ├── dependencies.py      # single-purpose -- stays flat
│   ├── emf_convert.py       # single-purpose -- stays flat
│   ├── heading_parsing.py   # single-purpose -- stays flat
│   ├── path_safety.py       # single-purpose -- stays flat
│   ├── schema/              # cohesive: this plugin's own schema for what it produces
│   │   ├── __init__.py
│   │   ├── normalized_source_document.py
│   │   └── shared.py
│   └── pandoc/              # cohesive: pandoc cleanup + validation, one family
│       ├── __init__.py
│       ├── attrs.py
│       ├── footnotes.py
│       ├── heading_emphasis.py
│       ├── images.py
│       ├── tables.py
│       ├── toc.py
│       └── validate.py      # folded in here, not left flat as pandoc_validate.py --
│                             # it's part of the same pandoc-output family as the fixes
├── references/contracts/
│   └── normalized-source-document.md         # canonical
├── skills/extract-docx/
│   ├── SKILL.md
│   └── references/contracts/
│       └── normalized-source-document.md      # managed symlink to the canonical copy above
└── tests/
```

Matches `docx-to-content`'s own pre-existing convention exactly
(`scripts/*.py` flat, `scripts/pandoc_fixes/`/`scripts/renderers/` as the
only cohesive subfolders) — this was always the right model; Wave 2's
first pass got it wrong by introducing an unnecessary
`src/source_document_extraction/` nesting layer, corrected here.

## Why not `src/<import_name>/`

The nested layout was chosen originally to satisfy real `pip`
installability (spec §13b) — Python packaging conventionally uses
`src/<package>/` so the installed import name is namespaced and collision-
safe. That's a real, legitimate concern (see "The `contracts` collision"
below), but the fix is **careful naming**, not an extra directory layer:
`pip`/`setuptools` can build a real, standalone-installable wheel from a
flat `scripts/` directory just as well, using `py-modules` for loose
top-level modules and `packages.find` (with `package-dir = {"" = "scripts"}`)
for subpackages:

```toml
[tool.setuptools]
py-modules = ["extraction", "dependencies", "emf_convert", "heading_parsing", "path_safety"]

[tool.setuptools.packages.find]
where = ["scripts"]
include = ["schema", "schema.*", "pandoc", "pandoc.*"]

[tool.setuptools.package-dir]
"" = "scripts"
```

Verified: `python -m build --wheel` produces a real wheel; installing it in
a clean venv resolves `import extraction`/`import schema.normalized_source_document`/
`import pandoc.attrs` from `site-packages`, not the checkout; all 78 of
this plugin's tests pass from the installed distribution;
`isolated_install_check.py --plugin source-document-extraction
--import-package extraction` exits 0.

## The `contracts` collision (a real bug this correction fixed)

The first flattening pass named this plugin's schema module `contracts/`
(matching the "Approved structure" example initially given). That
collided with `docx-to-content/scripts/contracts.py` — a real, unrelated,
heavily-used module (`ConversionPlan`/`SourceFingerprint` dataclasses,
imported by 9+ files there) that predates Phase 4.5. Both end up on
`sys.path` in the same process once `source-document-extraction` is
`pip install -e`'d for `docx-to-content`'s compatibility shim to use —
same bare name, different content, direct collision. Renamed to `schema/`
to fix it. **Lesson: before picking a bare top-level name for a new
plugin's module, grep every other plugin likely to be co-installed for
that exact name first** — this is the real cost of the flat model, and the
dependency-boundary/isolated-install/combined-install gates should ideally
catch this mechanically in a later wave (not yet automated as of this
correction).

## Compatibility-shim files must not shadow their own target

`docx-to-content`'s original compatibility shims
(`scripts/dependencies.py`, `scripts/emf_convert.py`,
`scripts/pandoc_validate.py`, `scripts/path_safety.py`,
`scripts/pandoc_fixes/*.py`) were themselves named identically to the
modules they re-exported from `source-document-extraction`. Once the
target became a flat, bare-named module, `from dependencies import *`
inside a file literally named `dependencies.py`, with that same directory
on `sys.path`, self-shadows (Python resolves the name to the
partially-initialized shim file itself, not the real installed module).
**Fix: delete the shim files entirely.** Once `source-document-extraction`
is `pip install -e`'d, `docx-to-content`'s existing bare `import
dependencies` / `from pandoc.attrs import ...` calls resolve directly to
the real installed package — no shim needed, and no self-collision
possible, as long as `docx-to-content/scripts/` no longer contains a
same-named file to shadow the installed one.

## Verification

- `source-document-extraction`: 78/78 tests pass, both via `pip install -e
  .` and via a real built-and-installed wheel in a clean venv.
- `docx-to-content`: 452 passed/1 skipped, unchanged, with the
  compatibility shim files removed (not just rewritten) and
  `source-document-extraction` `pip install -e`'d alongside it.
- `tools/phase-4-5-core-plugin-refactoring`: 40/40 tests pass.
- `isolated_install_check.py --plugin source-document-extraction
  --import-package extraction`: exit 0.
- `symlink_manager.py diagnose`: all links OK, zero broken/real-file
  imposters.

## Governance documents amended alongside this correction

- This document (new).
- `plugins/source-document-extraction/`: `pyproject.toml`, `README.md`,
  `skills/extract-docx/SKILL.md`, `references/contracts/normalized-source-document.md`,
  all script/test file headers rewritten to describe the plugin from its
  own present-tense perspective, not "extracted from docx-to-content."
- `plugins/docx-to-content/scripts/analyze_structure.py`,
  `validate_canonical.py`, `convert.py`, `chunking.py` and their tests —
  updated to the flat bare-import form; shim files deleted.
- `tools/phase-4-5-core-plugin-refactoring/isolated_install_check.py`'s
  usage example now uses `--import-package extraction`, not
  `source_document_extraction`.
