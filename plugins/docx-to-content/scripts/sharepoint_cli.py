"""
sharepoint_cli.py
=================

Human-facing CLI for the Phase 3 package-only SharePoint pilot tooling:
build an UploadPackage, dry-run validate it, and reconcile it against
actual-library-state CSV evidence after a human uploads it. No
SharePoint tenant I/O happens in this module or anything it calls. Phase
3 plan Task 3.3.6.
"""

import argparse
import json
import sys
from pathlib import Path

import sharepoint_dry_run as dry_run
import sharepoint_package as pkg_mod
import sharepoint_reconcile as reconcile_mod


def _cmd_package(args) -> int:
    pkg = pkg_mod.build_upload_package(
        Path(args.canonical_dir), Path(args.render_dir), Path(args.output_dir),
    )
    print(f"entries={len(pkg.entries)}")
    return 0


def _cmd_dry_run(args) -> int:
    pkg = pkg_mod.UploadPackage.load(Path(args.package_dir))
    report = dry_run.validate_upload_package(pkg)
    print(json.dumps(report.to_dict(), indent=2))
    return 0 if report.status == "PASS" else 1


def _cmd_reconcile(args) -> int:
    pkg = pkg_mod.UploadPackage.load(Path(args.package_dir))
    actual_items = reconcile_mod.load_actual_state_from_csv(Path(args.actual_state))
    report = reconcile_mod.reconcile(pkg, actual_items)
    print(json.dumps(report.to_dict(), indent=2))
    return 0 if report.status == "MATCH" else 1


def main(argv: list) -> int:
    parser = argparse.ArgumentParser(prog="sharepoint_cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    package_parser = subparsers.add_parser("package")
    package_parser.add_argument("--canonical-dir", required=True)
    package_parser.add_argument("--render-dir", required=True)
    package_parser.add_argument("--output-dir", required=True)
    package_parser.set_defaults(func=_cmd_package)

    dry_run_parser = subparsers.add_parser("dry-run")
    dry_run_parser.add_argument("--package-dir", required=True)
    dry_run_parser.set_defaults(func=_cmd_dry_run)

    reconcile_parser = subparsers.add_parser("reconcile")
    reconcile_parser.add_argument("--package-dir", required=True)
    reconcile_parser.add_argument("--actual-state", required=True)
    reconcile_parser.set_defaults(func=_cmd_reconcile)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
