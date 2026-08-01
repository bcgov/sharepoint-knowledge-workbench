# tools/phase-4-5-core-plugin-refactoring/isolated_install_check.py
"""Builds a plugin's wheel, installs it (plus the contracts distribution and
declared dependencies only) into a clean virtual environment, and proves the
package works from that installation — not from the monorepo checkout."""
from __future__ import annotations
import argparse
import subprocess
import sys
import tempfile
import venv
from pathlib import Path


def check_declares_dependency(project_dir: Path, dependency_distribution_name: str) -> bool:
    """Static metadata check (Revision 3 changelog item 4's "plus a metadata-inspection
    harness"): does this plugin's own pyproject.toml [project].dependencies list declare
    the given dependency? The runtime check_isolated_install() below always installs the
    contracts distribution alongside every plugin (by design — every plugin needs it), so
    it cannot by itself catch a plugin that imports the contracts distribution without
    declaring it as a dependency; this static check is what actually catches that."""
    import tomllib

    pyproject = project_dir / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    dependencies = data.get("project", {}).get("dependencies", [])
    return any(dep.split("=")[0].split(">")[0].split("<")[0].strip() == dependency_distribution_name for dep in dependencies)


def build_wheel(project_dir: Path, dist_dir: Path) -> Path:
    subprocess.run([sys.executable, "-m", "build", "--wheel", "--outdir", str(dist_dir), str(project_dir)], check=True)
    wheels = sorted(dist_dir.glob("*.whl"))
    if not wheels:
        raise RuntimeError(f"No wheel produced for {project_dir}")
    return wheels[-1]


def check_isolated_install(
    plugin_dir: Path, contracts_dir: Path, repo_root: Path, import_package: str
) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        venv_dir = tmp_path / "venv"
        venv.EnvBuilder(with_pip=True).create(venv_dir)
        pip = venv_dir / "bin" / "pip"
        python = venv_dir / "bin" / "python"

        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()
        contracts_wheel = build_wheel(contracts_dir, dist_dir)
        plugin_wheel = build_wheel(plugin_dir, dist_dir)

        subprocess.run([str(pip), "install", str(contracts_wheel), str(plugin_wheel), "pytest"], check=True, capture_output=True)

        # Confirm NO upstream plugin distribution is installed (undeclared-dependency negative control)
        freeze = subprocess.run([str(pip), "freeze"], capture_output=True, text=True, check=True).stdout
        for other in ["source-document-extraction", "knowledge-analysis", "canonical-knowledge", "knowledge-publication"]:
            if other in freeze and other != plugin_dir.name:
                raise AssertionError(f"Undeclared upstream plugin {other} found installed: {freeze}")

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
    result = check_isolated_install(
        repo_root / "plugins" / args.plugin,
        repo_root / "contracts" / "python",
        repo_root,
        args.import_package,
    )
    print(result.stdout)
    print(result.stderr)
    sys.exit(result.returncode)
