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
