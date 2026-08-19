"""Wave 0 Step 1: baseline artifact inventory for plugins/docx-to-content."""
from __future__ import annotations

from pathlib import Path


def _relative_py_files(plugin_root: Path, subdir: str) -> list[str]:
    base = plugin_root / subdir
    if not base.exists():
        return []
    return sorted(
        str(p.relative_to(plugin_root))
        for p in base.rglob("*.py")
        if "__pycache__" not in p.parts
    )


def build_inventory(plugin_root: Path) -> dict:
    skills_dir = plugin_root / "skills"
    skills = sorted(p.name for p in skills_dir.iterdir() if p.is_dir()) if skills_dir.exists() else []
    return {
        "scripts": _relative_py_files(plugin_root, "scripts"),
        "tests": _relative_py_files(plugin_root, "tests"),
        "skills": skills,
    }
