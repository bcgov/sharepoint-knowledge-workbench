"""Wave 0 Step 3: AST-based test-function ledger for plugins/docx-to-content."""
from __future__ import annotations

import ast
from pathlib import Path


def build_test_ledger(plugin_root: Path) -> dict:
    tests_dir = plugin_root / "tests"
    entries: list[dict] = []
    if not tests_dir.exists():
        return {"entries": entries}

    for path in sorted(tests_dir.rglob("test_*.py")):
        if "__pycache__" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                entries.append(
                    {
                        "file": str(path.relative_to(plugin_root)),
                        "test_name": node.name,
                        "proposed_owner_domain": None,
                    }
                )
            elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name.startswith("test_"):
                        entries.append(
                            {
                                "file": str(path.relative_to(plugin_root)),
                                "test_name": f"{node.name}::{item.name}",
                                "proposed_owner_domain": None,
                            }
                        )
    return {"entries": entries}
