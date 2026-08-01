"""
test_import_boundaries.py
==========================

Proves, via static analysis of the actual import graph (not just each
module's own direct import statements), that renderer-side code never
transitively reaches a DOCX-analysis/producer module. A DIRECT-import-only
check would have missed the real defect this repo found: renderers/protocol.py
imports CanonicalPackage from package.py, and package.py (before Phase 2's
Task 8 split) itself imported topic_grouping -- a producer/analysis concern
-- so a check that only inspected renderers/'s own import statements would
have passed while the dependency chain still pulled in topic_grouping.

Round-3 review (GPT 5.6 issue #11, confirmed by Opus) found the first draft
of `_direct_imports` truncated every dotted import to its first component
(`node.module.split(".")[0]`), so `from renderers import multipage_markdown`
was recorded as just `"renderers"` -- silently losing the submodule. This
version resolves `from X import Y` to `X.Y` whenever `X.Y` is itself a real
local submodule (not merely an attribute defined inside `X`), and includes a negative-control test proving the checker itself would
catch a real forbidden edge, not just happening to find none today.
"""

import ast
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _THIS_DIR.parent.parent / "scripts"

_FORBIDDEN_MODULES = {
    "analyze_structure", "pandoc", "convert", "plans", "chunking",
    "emf_convert", "topic_grouping", "package",  # package.py = builders only now
}

_ENTRY_MODULES = {
    "renderers.protocol", "renderers.multipage_markdown", "renderers.validate_rendered",
    "canonical_package",
}


def _module_path(module_name: str) -> "Path | None":
    """Resolve a dotted module name to a real .py file under scripts_dir,
    trying both `<parts>.py` and `<parts>/__init__.py` -- or None if it
    doesn't resolve locally (e.g. it's a stdlib module)."""
    parts = module_name.split(".")
    candidate = _SCRIPTS_DIR.joinpath(*parts).with_suffix(".py")
    if candidate.exists():
        return candidate
    init_candidate = _SCRIPTS_DIR.joinpath(*parts, "__init__.py")
    if init_candidate.exists():
        return init_candidate
    return None


def _direct_imports(module_path: Path) -> set:
    """Return every LOCALLY RESOLVABLE dotted module name this file
    directly imports -- e.g. {"renderers.multipage_markdown", "contracts"},
    never truncated to a package's first component when the real target is
    a submodule."""
    tree = ast.parse(module_path.read_text())
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            base = node.module
            for alias in node.names:
                dotted = f"{base}.{alias.name}"
                if _module_path(dotted) is not None:
                    # `from X import Y` where Y is itself a real submodule
                    # of X (e.g. `from renderers import multipage_markdown`)
                    # -- record the FULL dotted path, not just `base`.
                    names.add(dotted)
                else:
                    # Y is an attribute/name defined inside X's own file
                    # (e.g. `from contracts import RenderResult`) -- X
                    # itself is still the thing that gets imported/executed.
                    names.add(base)
    return names


def _transitive_imports(module_name: str, seen: set = None) -> set:
    seen = seen if seen is not None else set()
    if module_name in seen:
        return seen
    seen.add(module_name)
    path = _module_path(module_name)
    if path is None:
        return seen  # unresolvable locally (e.g. stdlib) -- harmless, nothing further to walk
    for imported in _direct_imports(path):
        if imported == module_name:
            continue
        _transitive_imports(imported, seen)
    return seen


def test_renderer_side_never_transitively_imports_a_forbidden_module():
    for entry in _ENTRY_MODULES:
        transitive = _transitive_imports(entry)
        forbidden_hit = transitive & _FORBIDDEN_MODULES
        assert not forbidden_hit, (
            f"{entry!r} transitively imports forbidden module(s) {forbidden_hit} "
            f"-- full transitive closure: {sorted(transitive)}"
        )


def test_checker_detects_a_synthetic_forbidden_transitive_edge(tmp_path, monkeypatch):
    """Negative control (round-3 review's explicit ask): prove this checker
    would actually catch a forbidden edge, not merely that it found none in
    the real graph today. Builds a tiny synthetic three-module chain
    (entry -> middle -> forbidden) in an isolated directory and asserts the
    transitive walk surfaces the forbidden module."""
    synthetic_scripts_dir = tmp_path / "scripts"
    synthetic_scripts_dir.mkdir()
    (synthetic_scripts_dir / "entry_module.py").write_text("from middle_module import thing\n")
    (synthetic_scripts_dir / "middle_module.py").write_text("import forbidden_module\nthing = 1\n")
    (synthetic_scripts_dir / "forbidden_module.py").write_text("x = 1\n")

    tib = sys.modules[__name__]
    monkeypatch.setattr(tib, "_SCRIPTS_DIR", synthetic_scripts_dir)

    transitive = tib._transitive_imports("entry_module")
    assert "forbidden_module" in transitive


def test_checker_correctly_resolves_from_package_import_submodule(tmp_path, monkeypatch):
    """Round-3 review's exact reported bug: `from X import Y` where Y is a
    real submodule of X must resolve to `X.Y`, not truncate to `X` alone
    and silently lose which submodule was actually reached."""
    synthetic_scripts_dir = tmp_path / "scripts"
    package_dir = synthetic_scripts_dir / "pkg"
    package_dir.mkdir(parents=True)
    (package_dir / "__init__.py").write_text("")
    (package_dir / "sub.py").write_text("import forbidden_module\n")
    (synthetic_scripts_dir / "forbidden_module.py").write_text("x = 1\n")
    (synthetic_scripts_dir / "entry_module.py").write_text("from pkg import sub\n")

    tib = sys.modules[__name__]
    monkeypatch.setattr(tib, "_SCRIPTS_DIR", synthetic_scripts_dir)

    direct = tib._direct_imports(synthetic_scripts_dir / "entry_module.py")
    assert "pkg.sub" in direct  # not truncated to just "pkg"
    transitive = tib._transitive_imports("entry_module")
    assert "forbidden_module" in transitive
