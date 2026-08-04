"""
compare_rendered_output.py
============================

Phase 6 Task 0.16 -- the `compare-rendered-output` skill. Packages the
golden-master comparison pattern used at Phase 2 Subphase 2.5.4 (proving
a fresh render is byte-identical to a recorded baseline) as a standalone,
reusable primitive -- usable against either a Markdown
(`render-multipage-markdown`) or ASPX (`render-sharepoint-aspx`)
rendered-output tree, since both are just a directory of files.

Two files are excluded from comparison by default (matching the
precedent this plugin's Phase 4.5 Wave 6 golden-master proof already
established -- see `docs/superpowers/plans/phase-4-5-evidence/
wave-6-golden-master-manifest.json`'s own `excluded_from_hash` list):

    generator-info.json  -- `run_timestamp` is deliberately run-specific
                             (`atomic_output.write_generator_info`'s own
                             documented exclusion rule).
    render-result.json   -- `output_files` entries are absolute,
                             run-location-specific paths.

Unlike Wave 6's one-off manual hash script (which excluded only the
run-specific *fields* within those two files), this module excludes the
*entire file* from comparison -- a deliberately simpler, more
conservative policy for a reusable primitive: it never risks silently
comparing a field it doesn't know is run-specific, at the cost of not
catching a real regression that happens to live only in one of those
two files' otherwise-stable fields. Any caller needing field-level
comparison of those two files can still read and compare them directly.
"""

from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_EXCLUDED_FILENAMES = frozenset({"generator-info.json", "render-result.json"})


@dataclass
class ComparisonIssue:
    severity: str
    code: str
    message: str


@dataclass
class ComparisonReport:
    status: str
    issues: list = field(default_factory=list)


def _error(code: str, message: str) -> "ComparisonIssue":
    return ComparisonIssue(severity="error", code=code, message=message)


def _relative_files(root: Path, excluded_filenames: frozenset) -> dict:
    """Return `{relative_posix_path: absolute_path}` for every file under
    `root`, skipping any file whose bare name is in `excluded_filenames`."""
    result = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name in excluded_filenames:
            continue
        result[path.relative_to(root).as_posix()] = path
    return result


def compare_rendered_trees(
    dir_a: "Path | str",
    dir_b: "Path | str",
    *,
    excluded_filenames: frozenset = DEFAULT_EXCLUDED_FILENAMES,
) -> "ComparisonReport":
    """Compare every file under `dir_a` against `dir_b` (both typically
    rendered-output directories -- a freshly-produced render and a
    recorded golden-master baseline), skipping any file whose bare name
    is in `excluded_filenames`. Detects: files present in `dir_a` but
    missing from `dir_b`, files present in `dir_b` but not `dir_a`, and
    byte-content mismatches for files present in both. Returns
    `ComparisonReport(status="MATCH"|"MISMATCH", issues=[...])`."""
    dir_a, dir_b = Path(dir_a), Path(dir_b)
    files_a = _relative_files(dir_a, excluded_filenames)
    files_b = _relative_files(dir_b, excluded_filenames)

    issues = []

    for rel_path in sorted(set(files_a) - set(files_b)):
        issues.append(_error(
            "missing_in_b",
            f"{rel_path!r} exists under {dir_a} but not under {dir_b}",
        ))

    for rel_path in sorted(set(files_b) - set(files_a)):
        issues.append(_error(
            "extra_in_b",
            f"{rel_path!r} exists under {dir_b} but not under {dir_a}",
        ))

    for rel_path in sorted(set(files_a) & set(files_b)):
        if files_a[rel_path].read_bytes() != files_b[rel_path].read_bytes():
            issues.append(_error(
                "content_mismatch",
                f"{rel_path!r} differs in content between {dir_a} and {dir_b}",
            ))

    status = "MISMATCH" if issues else "MATCH"
    return ComparisonReport(status=status, issues=issues)
