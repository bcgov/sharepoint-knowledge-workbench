# tools/phase-4-5-core-plugin-refactoring/combined_install_check.py
"""Installs all four domain-plugin wheels (no shared contracts/runtime
wheel -- each plugin materializes its own contract/runtime code, per spec
Section 13d) into ONE clean virtual environment, proving zero namespace/
dependency collisions and that every plugin's own test suite still
passes in the shared environment.

Under the materialized-contract model each plugin is self-contained, so
the combined-install proof is "these four independently-standalone
plugins also don't collide when co-installed," not "these plugins plus a
shared distribution work together." See
docs/superpowers/plans/phase-4-5-evidence/wave-2-contract-materialization-correction.md.
"""
from __future__ import annotations
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from isolated_install_check import build_wheel, check_no_workbench_family_dependency

PLUGINS = (
    "source-document-extraction",
    "knowledge-analysis",
    "canonical-knowledge",
    "knowledge-publication",
)


def check_combined_install(repo_root: Path) -> dict:
    for p in PLUGINS:
        if check_no_workbench_family_dependency(repo_root / "plugins" / p):
            raise AssertionError(f"{p} declares a prohibited workbench-family dependency")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        venv_dir = tmp_path / "venv"
        venv.EnvBuilder(with_pip=True).create(venv_dir)
        pip, python = venv_dir / "bin" / "pip", venv_dir / "bin" / "python"
        # Each plugin builds into its OWN subdirectory, never a shared
        # dist_dir: build_wheel() picks the alphabetically-last *.whl in
        # whatever directory it's given, so building four wheels into one
        # shared directory makes every call after the first silently
        # return the same (alphabetically-last) wheel instead of the one
        # just built -- a real bug this combined-install harness caught.
        wheels = []
        for p in PLUGINS:
            plugin_dist_dir = tmp_path / "dist" / p
            plugin_dist_dir.mkdir(parents=True)
            wheels.append(build_wheel(repo_root / "plugins" / p, plugin_dist_dir))
        subprocess.run(
            [str(pip), "install", *[str(w) for w in wheels], "pytest"],
            check=True, capture_output=True,
        )
        results = {}
        for p in PLUGINS:
            r = subprocess.run(
                [str(python), "-m", "pytest", str(repo_root / "plugins" / p / "tests"), "-v"],
                capture_output=True, text=True,
            )
            results[p] = r.returncode
            if r.returncode != 0:
                print(r.stdout)
                print(r.stderr)
        return results


if __name__ == "__main__":
    repo_root = Path(
        subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).decode().strip()
    )
    results = check_combined_install(repo_root)
    print("Combined install results:", results)
    sys.exit(0 if all(rc == 0 for rc in results.values()) else 1)
