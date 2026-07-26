"""
cli.py
======

Command-line entry point for the docx-to-content plugin pipeline
(spec section 12):

    python -m scripts.cli analyze --source <docx> --output <analysis-dir>
    python -m scripts.cli confirm --draft-plan <path> --output <confirmed-plan>
    python -m scripts.cli convert --source <docx> --plan <confirmed-plan> --output <run-dir>
    python -m scripts.cli render --canonical <canonical-dir> --renderer multipage-markdown --output <render-dir>
    python -m scripts.cli run --source <docx> --confirmed-plan <path> --output <run-dir>

This module is the CLI *skeleton*: real argument parsing, exit-code
plumbing, and dependency preconditions. The analyze/convert/render business
logic itself does not exist yet (Tasks 6, 9, 13) — those subcommands stub
out with NotImplementedError once their preconditions pass.

Exit codes:
    0 - PASS
    2 - validation or contract FAIL
    3 - dependency/precondition failure (missing source file, missing
        pandoc/soffice)
    4 - user input or unsupported schema/renderer error (unknown
        subcommand, missing required argument, unsupported renderer name,
        or a plan that is not yet confirmed)
    1 - unexpected/unclassified error (still non-zero; a diagnostic is
        always printed, never a bare traceback)

Must be run with `plugins/docx-to-content/` as the working directory (or
with that directory on PYTHONPATH) so `python -m scripts.cli` resolves the
`scripts` package. This file also inserts its own directory onto
sys.path at import time so its plain top-level imports (`import
dependencies`, `import contracts`) work the same way whether it is loaded
as `scripts.cli` (via `-m`) or as a bare `cli` module (as tests do, via
tests/conftest.py's sys.path setup) — matching the import convention
already used by contracts.py/hashing.py/identity.py in this package.
"""

import argparse
import json
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import analyze_structure  # noqa: E402
import contracts  # noqa: E402
import convert  # noqa: E402
import dependencies  # noqa: E402
import package  # noqa: E402
import plans  # noqa: E402


EXIT_PASS = 0
EXIT_VALIDATION_FAIL = 2
EXIT_DEPENDENCY_FAIL = 3
EXIT_USAGE_ERROR = 4
EXIT_UNEXPECTED = 1

SUPPORTED_RENDERERS = {"multipage-markdown"}


# ---------------------------------------------------------------------------
# Typed errors -> exit codes
# ---------------------------------------------------------------------------

class CLIError(Exception):
    """Base class for CLI errors that map to a specific exit code."""

    exit_code = EXIT_UNEXPECTED


class UsageError(CLIError):
    """Unsupported command, missing required argument, unsupported
    renderer, or an unconfirmed plan passed to `run`."""

    exit_code = EXIT_USAGE_ERROR


class PreconditionError(CLIError):
    """Missing source file or missing required external tool."""

    exit_code = EXIT_DEPENDENCY_FAIL


class ValidationFailError(CLIError):
    """Malformed/unsupported-schema plan or contract data."""

    exit_code = EXIT_VALIDATION_FAIL


class _StrictArgumentParser(argparse.ArgumentParser):
    """argparse's default `error()` prints usage and calls `sys.exit(2)`.
    This repo's exit-code contract reserves 2 for validation/contract FAIL,
    so unknown subcommands and missing required arguments (both "user
    input" problems) must map to 4 instead. Raising here lets main()
    apply that mapping uniformly.
    """

    def error(self, message):
        raise UsageError(f"{self.prog}: {message}")


# ---------------------------------------------------------------------------
# Shared preconditions
# ---------------------------------------------------------------------------

def _require_source(source: str) -> Path:
    path = Path(source)
    if not path.exists():
        raise PreconditionError(f"source file not found: {source}")
    return path


def _require_pandoc() -> dependencies.DependencyStatus:
    status = dependencies.probe_pandoc()
    if not status.available:
        raise PreconditionError("pandoc is required but was not found on PATH")
    return status


def _load_plan_from_file(plan_path: Path) -> contracts.ConversionPlan:
    if not plan_path.exists():
        raise PreconditionError(f"plan file not found: {plan_path}")
    try:
        data = json.loads(plan_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationFailError(f"could not read plan file {plan_path}: {exc}") from exc
    try:
        return contracts.ConversionPlan.from_dict(data)
    except ValueError as exc:
        raise ValidationFailError(f"invalid plan contract in {plan_path}: {exc}") from exc


def _require_confirmed_plan(plan_path: Path) -> contracts.ConversionPlan:
    """Load a plan file and reject it with exit code 4 (UsageError) if it is
    not already confirmed. This is the sole enforcement point for the
    "no all-in-one command may bypass plan confirmation" rule: `run` never
    performs the confirm step itself and never silently promotes a draft.

    Delegates the actual "is this plan confirmed" check to
    `plans.require_confirmed` so there is exactly one implementation of
    that rule; this wrapper's only job is mapping the plans.py-level
    PlanVerificationError to the CLI's exit-code-4 UsageError.
    """
    plan = _load_plan_from_file(plan_path)
    try:
        plans.require_confirmed(plan)
    except plans.PlanVerificationError as exc:
        raise UsageError(
            f"plan {plan_path} is not confirmed: {exc} -- `run`/`convert` "
            "never auto-confirm a draft plan"
        ) from exc
    return plan


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

def cmd_analyze(args):
    source_path = _require_source(args.source)
    _require_pandoc()
    analyze_structure.analyze_document(source_path, Path(args.output))
    return EXIT_PASS


def cmd_confirm(args):
    draft_plan_path = Path(args.draft_plan)
    draft_plan = _load_plan_from_file(draft_plan_path)  # exit 3 missing / 2 malformed
    if draft_plan.confirmation.status == "confirmed":
        # Double-confirming is rejected rather than allowed idempotently:
        # confirming is a deliberate, one-way action tied to reviewing a
        # specific draft. Silently "allowing" it again would re-stamp
        # confirmed_by/confirmed_at over an existing confirmed plan for no
        # reason -- if the caller wants a fresh confirmation they should
        # confirm the *draft* it came from, not an already-confirmed file.
        raise UsageError(
            f"{draft_plan_path} is already confirmed "
            f"(confirmation.status={draft_plan.confirmation.status!r}); "
            "confirm expects a draft plan, not an already-confirmed one"
        )
    confirmed_plan = plans.confirm_plan(draft_plan)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(confirmed_plan.to_dict(), indent=2))
    return EXIT_PASS


def cmd_convert(args):
    source_path = _require_source(args.source)
    _require_pandoc()
    plan = _require_confirmed_plan(Path(args.plan))
    try:
        convert.convert_document(source_path, plan, Path(args.output))
    except plans.PlanVerificationError as exc:
        # verify_plan_against_source / verify_plan_integrity failures:
        # a stale or tampered plan, surfaced as exit 4 (usage error) --
        # matching _require_confirmed_plan's mapping for the same class
        # of "this plan cannot be trusted as-is" problem.
        raise UsageError(str(exc)) from exc
    except (
        convert.chunking.AnchorReconciliationError,
        package.MediaError,
    ) as exc:
        # Malformed/unsupported content discovered while building the
        # canonical package (missing anchors, ambiguous anchors, illegal
        # media references, unconverted legacy media, ...) is a contract/
        # validation failure, not a dependency or usage problem.
        raise ValidationFailError(str(exc)) from exc
    return EXIT_PASS


def cmd_render(args):
    if args.renderer not in SUPPORTED_RENDERERS:
        raise UsageError(
            f"unsupported renderer: {args.renderer!r} "
            f"(supported: {sorted(SUPPORTED_RENDERERS)})"
        )
    canonical_path = Path(args.canonical)
    if not canonical_path.exists():
        raise PreconditionError(f"canonical directory not found: {args.canonical}")
    raise NotImplementedError(
        "render business logic (multipage-markdown renderer) is "
        "implemented in Task 13"
    )


def cmd_run(args):
    _require_source(args.source)
    _require_pandoc()
    # Enforces "no all-in-one command may bypass plan confirmation": the
    # plan file at --confirmed-plan must already exist and already have
    # confirmation.status == "confirmed"; run rejects a draft with exit 4.
    _require_confirmed_plan(Path(args.confirmed_plan))
    raise NotImplementedError(
        "run orchestration (convert+render using an already-confirmed "
        "plan) is implemented across Tasks 9 and 13"
    )


# ---------------------------------------------------------------------------
# Parser construction
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = _StrictArgumentParser(
        prog="python -m scripts.cli",
        description="docx-to-content: convert Word manuals into versioned "
                     "canonical content and rendered output.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_analyze = subparsers.add_parser(
        "analyze", help="Analyze a source .docx and produce a draft conversion plan"
    )
    p_analyze.add_argument("--source", required=True, help="Path to the source .docx file")
    p_analyze.add_argument("--output", required=True, help="Directory to write analysis output to")
    p_analyze.set_defaults(func=cmd_analyze)

    p_confirm = subparsers.add_parser(
        "confirm", help="Promote a draft plan to an explicitly confirmed plan"
    )
    p_confirm.add_argument(
        "--draft-plan", required=True, dest="draft_plan", help="Path to the draft plan file"
    )
    p_confirm.add_argument("--output", required=True, help="Path to write the confirmed plan to")
    p_confirm.set_defaults(func=cmd_confirm)

    p_convert = subparsers.add_parser(
        "convert",
        help="Convert a source .docx into a canonical content package using a confirmed plan",
    )
    p_convert.add_argument("--source", required=True, help="Path to the source .docx file")
    p_convert.add_argument("--plan", required=True, help="Path to the confirmed plan file")
    p_convert.add_argument("--output", required=True, help="Directory to write run output to")
    p_convert.set_defaults(func=cmd_convert)

    p_render = subparsers.add_parser(
        "render", help="Render a canonical content package with a named renderer"
    )
    p_render.add_argument("--canonical", required=True, help="Path to the canonical content directory")
    p_render.add_argument("--renderer", required=True, help="Renderer name (e.g. multipage-markdown)")
    p_render.add_argument("--output", required=True, help="Directory to write rendered output to")
    p_render.set_defaults(func=cmd_render)

    p_run = subparsers.add_parser(
        "run",
        help="Orchestrate convert+render end to end using an already-confirmed plan",
    )
    p_run.add_argument("--source", required=True, help="Path to the source .docx file")
    p_run.add_argument(
        "--confirmed-plan",
        required=True,
        dest="confirmed_plan",
        help="Path to an ALREADY-CONFIRMED plan file (run never confirms a draft itself)",
    )
    p_run.add_argument("--output", required=True, help="Directory to write run output to")
    p_run.set_defaults(func=cmd_run)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        result = args.func(args)
        return result if isinstance(result, int) else EXIT_PASS
    except CLIError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code
    except dependencies.MissingDependencyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_DEPENDENCY_FAIL
    except NotImplementedError as exc:
        print(f"not implemented: {exc}", file=sys.stderr)
        return EXIT_UNEXPECTED
    except Exception as exc:  # top-level catch-all: never a bare traceback
        print(f"unexpected error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_UNEXPECTED


if __name__ == "__main__":
    sys.exit(main())
