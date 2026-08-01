"""Wave 0 Step 2: AST-based internal dependency graph for plugins/docx-to-content scripts."""
from __future__ import annotations

import ast
from pathlib import Path


def _module_files(scripts_dir: Path) -> dict[str, Path]:
    """Map importable module name -> file, for every .py file under scripts_dir (recursive)."""
    mapping: dict[str, Path] = {}
    for path in scripts_dir.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(scripts_dir).with_suffix("")
        mapping[".".join(rel.parts)] = path
        mapping[rel.parts[-1]] = path  # bare last-segment name, for `import convert` style
    return mapping


def build_dependency_graph(plugin_root: Path) -> dict:
    scripts_dir = plugin_root / "scripts"
    edges: list[dict] = []
    if not scripts_dir.exists():
        return {"edges": edges}

    module_files = _module_files(scripts_dir)

    for path in sorted(scripts_dir.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            targets: list[str] = []
            if isinstance(node, ast.Import):
                targets = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    targets = [node.module.split(".")[0]]
                elif node.level and node.level > 0:
                    targets = [alias.name for alias in node.names]
            for target in targets:
                target_path = module_files.get(target)
                if target_path is None or target_path == path:
                    continue
                edges.append(
                    {
                        "from": str(path.relative_to(plugin_root)),
                        "to": str(target_path.relative_to(plugin_root)),
                        "line": node.lineno,
                    }
                )
    return {"edges": edges}
