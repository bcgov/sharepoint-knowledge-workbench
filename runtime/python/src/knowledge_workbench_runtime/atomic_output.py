"""
atomic_output.py
=================

Approved-scope extraction (Wave 1, 2026-08-01) of the pure, generic
filesystem-atomicity primitives from plugins/docx-to-content/scripts/
atomic_output.py's original `create_staging_dir`/`promote` pair — the only
two functions in that module with zero dependency on any domain plugin.
`build_generator_info`/`write_generator_info` are deliberately NOT included
here: they call `dependencies.probe_pandoc()`/`probe_soffice()`, and
`dependencies.py` is source-document-extraction-domain logic, which this
neutral runtime distribution must never import (see the dependency-boundary
rule in docs/superpowers/plans/2026-08-01-phase-4-5-core-knowledge-plugin-
domain-refactoring.md). Each consuming plugin (canonical-knowledge,
knowledge-publication) implements its own thin generator-info wrapper
instead.

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
"""
from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path


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
