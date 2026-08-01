"""Repository-tooling-only helper (Wave 6 integration-evidence generation).

Exported for tooling use, never for plugin production code — specification
§13b's explicit prohibition, independently enforced by
tools/phase-4-5-core-plugin-refactoring/dependency_boundary.py's
check_no_repo_root_import_in_production_code()."""
from __future__ import annotations

from pathlib import Path


def find_repo_root(start: Path, markers: tuple[str, ...] = (".git",)) -> Path:
    current = Path(start).resolve()
    for candidate in (current, *current.parents):
        if any((candidate / marker).exists() for marker in markers):
            return candidate
    raise FileNotFoundError(f"no repo-root marker {markers!r} found above {start!r}")
