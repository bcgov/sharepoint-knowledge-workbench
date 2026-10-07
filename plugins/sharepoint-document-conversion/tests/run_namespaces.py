#!/usr/bin/env python3
"""Purpose:
    Run every test namespace of this package in its own pytest process.

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - subprocess
    - sys
    - pathlib

Run every test namespace of this package in its own pytest process.

Same-named flat modules exist in more than one namespace, so a single interpreter would import the
first namespace's module for every later one. Exit code is non-zero if any namespace fails.
usage: python3 tests/run_namespaces.py [-- extra pytest args]

Key Functions Index:
    - main()"""
import subprocess
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
TESTS = PACKAGE / "tests"


# Run each plugin test namespace in an isolated pytest process and report failing namespaces.
def main(extra):
    """Run each plugin test namespace in an isolated pytest process and report failing namespaces."""
    failed = []
    for namespace in sorted(p.name for p in TESTS.iterdir() if p.is_dir() and p.name not in ("__pycache__", "fixtures")):
        code = subprocess.call([sys.executable, "-m", "pytest", f"tests/{namespace}", "-q", *extra], cwd=PACKAGE)
        if code not in (0, 5):
            failed.append(namespace)
    if failed:
        print("FAILED namespaces:", ", ".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    sys.exit(main(args[1:] if args[:1] == ["--"] else args))
