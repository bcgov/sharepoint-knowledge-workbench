# tools/phase-4-5-core-plugin-refactoring/isolated_install_check.py
"""Builds a plugin's wheel and installs ONLY that wheel (plus third-party
PyPI dependencies) into a clean virtual environment, proving the plugin
works standalone -- no other workbench distribution (no sibling plugin, no
`knowledge-workbench-contracts`, no `knowledge-workbench-runtime`) is
installed, and no repository-root path is on sys.path. This is the Wave 2
correction to the original harness, which used to co-install the contracts
distribution alongside every plugin -- that made "isolated" installs
secretly depend on a sibling distribution nobody would know to install.
See docs/superpowers/plans/phase-4-5-evidence/wave-2-contract-materialization-correction.md.
"""
from __future__ import annotations
import argparse
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

_WORKBENCH_FAMILY_PREFIXES = ("knowledge-workbench-", "knowledge-")
_WORKBENCH_DISTRIBUTIONS = (
    "knowledge-workbench-contracts",
    "knowledge-workbench-runtime",
    "source-document-extraction",
    "document-structure-analysis",
    "structured-content-assembly",
    "structured-content-rendering",
)


def check_no_workbench_family_dependency(project_dir: Path) -> bool:
    """Static metadata check: does this plugin's pyproject.toml declare a
    pip dependency on ANY workbench-family distribution (the contracts
    distribution, the runtime distribution, or a sibling plugin)? Under the
    Wave 2 correction, this must always be False for a compliant plugin --
    every plugin carries its own contract/runtime code rather than
    depending on a shared distribution. Returns True if a violation is
    found (i.e. "has a prohibited dependency"), False if clean."""
    import tomllib

    pyproject = project_dir / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    dependencies = data.get("project", {}).get("dependencies", [])
    for dep in dependencies:
        dep_name = dep.split("=")[0].split(">")[0].split("<")[0].strip()
        if dep_name in _WORKBENCH_DISTRIBUTIONS or dep_name.startswith(_WORKBENCH_FAMILY_PREFIXES):
            return True
    return False


def build_wheel(project_dir: Path, dist_dir: Path) -> Path:
    subprocess.run([sys.executable, "-m", "build", "--wheel", "--outdir", str(dist_dir), str(project_dir)], check=True)
    wheels = sorted(dist_dir.glob("*.whl"))
    if not wheels:
        raise RuntimeError(f"No wheel produced for {project_dir}")
    return wheels[-1]


def check_isolated_install(plugin_dir: Path, import_package: str) -> subprocess.CompletedProcess:
    """Build and install ONLY `plugin_dir`'s own wheel (plus pytest) into a
    fresh venv -- no contracts distribution, no runtime distribution, no
    sibling plugin, no repository checkout on sys.path at all. Proves the
    plugin is genuinely standalone-installable."""
    if check_no_workbench_family_dependency(plugin_dir):
        raise AssertionError(
            f"{plugin_dir.name}'s pyproject.toml declares a prohibited "
            "workbench-family dependency -- every plugin must carry its own "
            "contract/runtime code, not depend on a shared distribution."
        )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        venv_dir = tmp_path / "venv"
        venv.EnvBuilder(with_pip=True).create(venv_dir)
        pip = venv_dir / "bin" / "pip"
        python = venv_dir / "bin" / "python"

        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()
        plugin_wheel = build_wheel(plugin_dir, dist_dir)

        subprocess.run([str(pip), "install", str(plugin_wheel), "pytest"], check=True, capture_output=True)

        # Confirm NO other workbench distribution is installed at all --
        # not a sibling plugin, not contracts, not runtime.
        freeze = subprocess.run([str(pip), "freeze"], capture_output=True, text=True, check=True).stdout
        for other in _WORKBENCH_DISTRIBUTIONS:
            if other == plugin_dir.name:
                continue
            if other in freeze:
                raise AssertionError(f"Undeclared workbench distribution {other} found installed: {freeze}")

        # Import the package outside pytest, from the installed distribution only
        import_check = subprocess.run(
            [str(python), "-c", f"import {import_package}; print({import_package}.__file__)"],
            capture_output=True, text=True,
        )
        if import_check.returncode != 0 or "site-packages" not in import_check.stdout:
            raise AssertionError(f"Import did not resolve from installed site-packages: {import_check.stdout} {import_check.stderr}")

        # Run this plugin's own tests using the installed distribution
        test_result = subprocess.run(
            [str(python), "-m", "pytest", str(plugin_dir / "tests"), "-v"],
            capture_output=True, text=True,
        )
        return test_result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--plugin", required=True)
    parser.add_argument("--import-package", required=True)
    args = parser.parse_args()
    repo_root = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).decode().strip())
    result = check_isolated_install(repo_root / "plugins" / args.plugin, args.import_package)
    print(result.stdout)
    print(result.stderr)
    sys.exit(result.returncode)
