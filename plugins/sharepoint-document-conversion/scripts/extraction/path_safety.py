"""path_safety.py
================

Purpose:
    Shared path-safety primitive for resolving a (possibly URL-encoded, possibly relative-with-'..') reference found in generated markdown content against a `base_dir` while enforcing that the resolved path never escapes a `root_dir` security boundary.

Key Input Dependencies:
    - pathlib
    - urllib.parse

Shared path-safety primitive for resolving a (possibly URL-encoded, possibly
relative-with-'..') reference found in generated markdown content against a
`base_dir` while enforcing that the resolved path never escapes a
`root_dir` security boundary.

This is the THIRD place in the plugin that needs this exact policy:
    1. `package.py`'s `_decode_and_validate` (conversion-time, RAW pre-rewrite
       references -- rejects ANY '..' segment outright, a stricter policy
       correct for its own narrower scope).
    2. `validate_canonical.py`'s `_check_media_references` (validation-time,
       FINAL already-rewritten `../media/<file>` references -- a '..'
       segment is expected and only a violation if it resolves outside the
       package dir entirely). That module's docstring explains why it does
       NOT reuse (1) unmodified: the two call sites enforce the same
       underlying boundary at different scopes.
    3. `renderers/validate_rendered.py` (Task 14) needs the exact same
       "final, already-rewritten reference" policy as (2), against the
       rendered-output directory's `pages/` + `media/` layout instead of
       canonical-content's `chunks/` + `media/`.

Rather than writing a third copy of the same resolve-and-classify logic,
this module factors out the one piece that (2) and (3) both need verbatim:
"decode a raw reference, classify it as external/absolute/traversal-outside-
root/resolvable, and return the resolved path when resolvable." `package.py`
is deliberately left as-is (different scope, different call site, already
covered by its own tests) -- only `validate_rendered.py` is wired to this
shared helper for now; retrofitting `validate_canonical.py` onto it is a
clean, in-scope follow-up but out of scope for this task's surgical-change
budget.

Key Functions Index:
    - classify_reference()"""

from pathlib import Path, PurePosixPath
from urllib.parse import unquote

EXTERNAL_PREFIXES = ("http://", "https://", "#", "mailto:")

VIOLATION_ABSOLUTE = "absolute"
VIOLATION_TRAVERSAL = "traversal"


def classify_reference(raw_ref: str, base_dir: Path, root_dir: Path):
    """Decode and classify `raw_ref` (as found literally in markdown
    content), resolved relative to `base_dir`, against the `root_dir`
    security boundary.

    Returns one of:
        ("external", None)             -- http(s)/#/mailto, not resolved at all
        ("violation", VIOLATION_ABSOLUTE)   -- absolute path / UNC / drive-letter root
        ("violation", VIOLATION_TRAVERSAL)  -- resolves outside root_dir via '..'
        ("resolved", Path)             -- safe, decoded, resolved absolute Path
                                           (caller decides existence/location)
    """
    if raw_ref.startswith(EXTERNAL_PREFIXES):
        return "external", None

    decoded = unquote(raw_ref)
    posix = PurePosixPath(decoded)
    is_windows_style = (
        len(decoded) >= 2 and decoded[1] == ":" and decoded[0].isalpha()
    ) or decoded.startswith("\\\\")
    if posix.is_absolute() or is_windows_style:
        return "violation", VIOLATION_ABSOLUTE

    root_resolved = Path(root_dir).resolve()
    candidate = (Path(base_dir) / decoded).resolve()
    if candidate != root_resolved and root_resolved not in candidate.parents:
        return "violation", VIOLATION_TRAVERSAL

    return "resolved", candidate
