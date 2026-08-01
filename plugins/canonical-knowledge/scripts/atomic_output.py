"""
atomic_output.py
=================

Shared staging/promotion mechanism (spec Section 13, "Output Safety and
Reproducibility") for BOTH canonical-content packages (Task 9/10/11) and
rendered output packages (Task 13/14). Nothing about this module is
canonical-package-specific: `create_staging_dir`/`promote` operate on
plain directories and know nothing about manifests, chunks, or renderers.
Task 14's render promotion is expected to call the exact same two
functions this task's `convert.convert_and_promote` calls.

Function Index:
    - create_staging_dir(output_root, prefix="staging") -> Path
        Creates a fresh, uniquely-named directory under `output_root`
        (never reuses/overlays an existing directory).
    - promote(staging_dir, final_dir) -> None
        Atomic-as-possible directory replacement: `final_dir` ends up
        containing exactly `staging_dir`'s content, and nothing of a
        previous `final_dir` survives unless `staging_dir` also produced
        it. Never merges/overlays.
    - build_generator_info(plugin_version) -> dict
        Plugin/Python/pandoc/soffice version record, reusing
        `dependencies.probe_pandoc()`/`probe_soffice()`.
    - write_generator_info(staging_dir, plugin_version, run_timestamp) -> dict
        Writes `generator-info.json` into `staging_dir` using the same
        canonical (sort_keys, UTF-8) JSON convention as
        `contracts`/`package.py`/`validate_canonical.py`.

Atomicity primitive and its guarantee
--------------------------------------
`create_staging_dir` uses `Path.mkdir(parents=True)` on a name that
includes a `uuid4` suffix -- collision-proof (never overlays a previous
run's directory), unlike a bare timestamp which two runs in the same
second could collide on.

`promote` uses `os.rename()` (POSIX: atomic for same-filesystem renames;
Windows via `os.rename`/`os.replace` semantics through pathlib are
likewise a single filesystem operation, not a copy loop). Directly
`os.rename(staging_dir, final_dir)` cannot be used unconditionally because
POSIX `rename()` fails with `ENOTEMPTY`/`EEXIST` when the destination is
an existing non-empty directory (this is why "promote a directory over
another directory" cannot be one syscall in general, only "promote a
directory into a name that does not yet exist" can). `promote` therefore:

    1. If `final_dir` exists, `os.rename` it out of the way to a sibling
       backup path (`<final_dir>.replaced-<uuid4>`) -- this rename is
       itself atomic and instantaneous (no content is copied).
    2. `os.rename(staging_dir, final_dir)` -- now that the destination
       name is free, this is the single atomic operation that actually
       exposes the new content at `final_dir`. No file-by-file copy ever
       runs against `final_dir`, so there is no window where `final_dir`
       is half-old/half-new content.
    3. On success, the backup from step 1 is deleted (`shutil.rmtree`) --
       this cleanup happens only AFTER `final_dir` already reflects the
       new content, so a crash during cleanup leaves an inert leftover
       backup directory, never a broken `final_dir`.
    4. If step 2 raises (e.g. `final_dir` reappears from another process,
       cross-device rename failure), the backup from step 1 is renamed
       back into place before re-raising, so `final_dir` is restored to
       exactly what it was before `promote` was called -- promote() never
       leaves `final_dir` missing or partially replaced.

This is why a FAILED validation run never touches `final_dir` at all:
callers (see `convert.convert_and_promote`) only ever call `promote()`
after validation of the STAGED package under `staging_dir` has already
passed; a failed package's `staging_dir` is simply never passed to
`promote()`, so it is left on disk untouched for diagnosis and
`final_dir` is never even opened.
"""

import json
import os
import platform
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

DEFAULT_PLUGIN_VERSION = "0.1.0"


def _probe_version(name: str) -> "str | None":
    """Thin, plugin-local version probe (Wave 1 decision: this plugin must
    not depend on source-document-extraction's `dependencies.py` --
    duplicating only the ~15-line version-probing glue, not the atomicity
    primitive above. See
    docs/superpowers/plans/phase-4-5-evidence/wave-4-canonical-knowledge-split-decision.md).
    """
    path = shutil.which(name)
    if path is None:
        return None
    try:
        result = subprocess.run(
            [path, "--version"], capture_output=True, text=True, timeout=10, check=False,
        )
        output = (result.stdout or result.stderr or "").strip()
        return output.splitlines()[0] if output else None
    except (OSError, subprocess.SubprocessError):
        return None


def create_staging_dir(output_root: Path, prefix: str = "staging") -> Path:
    """Create and return a fresh, uniquely-named directory under
    `output_root`. Uses a uuid4 suffix (not a bare timestamp) so two runs
    started in the same second never collide, and never reuses an
    existing directory (`mkdir` without `exist_ok`)."""
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    staging_dir = output_root / f"{prefix}-{uuid.uuid4().hex}"
    staging_dir.mkdir(parents=True, exist_ok=False)
    return staging_dir


def promote(staging_dir: Path, final_dir: Path) -> None:
    """Atomically (as much as the filesystem allows -- see module
    docstring) replace `final_dir` with the contents of `staging_dir`.

    - If `final_dir` does not exist yet, this is a single `os.rename`.
    - If `final_dir` exists, its OLD content is fully replaced, never
      merged: any file present in the old `final_dir` but absent from
      `staging_dir` does not survive.
    - On any failure, `final_dir` is restored to its pre-call state
      before the exception propagates.
    """
    staging_dir = Path(staging_dir)
    final_dir = Path(final_dir)
    final_dir.parent.mkdir(parents=True, exist_ok=True)

    backup_dir = None
    if final_dir.exists():
        backup_dir = final_dir.with_name(f"{final_dir.name}.replaced-{uuid.uuid4().hex}")
        os.rename(final_dir, backup_dir)

    try:
        os.rename(staging_dir, final_dir)
    except OSError:
        if backup_dir is not None:
            os.rename(backup_dir, final_dir)
        raise
    else:
        if backup_dir is not None:
            shutil.rmtree(backup_dir)


def build_generator_info(plugin_version: str = DEFAULT_PLUGIN_VERSION) -> dict:
    """Return the content-affecting generator record (no timestamp):
    plugin name/version, Python version, pandoc version, soffice version."""
    return {
        "plugin": "canonical-knowledge",
        "plugin_version": plugin_version,
        "python_version": platform.python_version(),
        "pandoc_version": _probe_version("pandoc"),
        "soffice_version": _probe_version("soffice"),
    }


def write_generator_info(
    staging_dir: Path,
    plugin_version: str = DEFAULT_PLUGIN_VERSION,
    run_timestamp: "str | None" = None,
) -> dict:
    """Write `generator-info.json` into `staging_dir` and return the
    record written (including `run_timestamp`).

    `run_timestamp` is the ONLY field in this record that is explicitly
    run-specific / excluded from reproducibility comparisons (consistent
    with Task 3's `hashing.compute_plan_id` pattern of excluding
    `confirmation.confirmed_at` from the plan's content hash): every other
    field (plugin/plugin_version/python_version/pandoc_version/
    soffice_version) is expected to be byte-identical across two runs
    against identical source/plan/tool versions. Uses the same
    `sort_keys=True` canonical-JSON convention as
    `package.py`/`validate_canonical.py` for deterministic ordering, and
    writes explicit UTF-8 bytes (not platform-default text encoding).
    """
    record = build_generator_info(plugin_version)
    record["run_timestamp"] = run_timestamp or datetime.now(timezone.utc).isoformat()
    (Path(staging_dir) / "generator-info.json").write_bytes(
        json.dumps(record, indent=2, sort_keys=True).encode("utf-8")
    )
    return record
