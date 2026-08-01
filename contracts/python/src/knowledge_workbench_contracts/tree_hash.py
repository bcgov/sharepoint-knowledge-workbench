"""Deterministic tree-hash algorithm, per the approved Wave 1 plan."""
from __future__ import annotations

import hashlib
from pathlib import Path


def compute_tree_hash(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            h.update(path.relative_to(root).as_posix().encode("utf-8"))
            h.update(path.read_bytes())
    return h.hexdigest()
