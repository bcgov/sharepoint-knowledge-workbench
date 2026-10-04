#!/usr/bin/env python
"""
pandoc/validate.py
=========================

Hard-fail validator for cleaned pandoc markdown output. Run after the
sibling attrs/images/toc/tables/footnotes cleanup modules in this same
pandoc/ package (attrs -> images -> toc -> tables -> footnotes ->
legacy image conversion, per spec Section 7.2) to catch regressions the
pipeline should have already fixed:

  (a) unresolved image links: a relative image path that does not exist
      under the given base directory.
  (b) leftover pandoc attribute artifacts: `{width=...}`, `{.underline}`,
      `{.mark}`-style syntax still present, which means attrs.py either
      didn't run or missed something.
  (c) images still embedded directly in heading lines, which means
      images.py either didn't run or missed something.

Key Input Dependencies:
    - `base_dir` (Path): directory relative image paths are resolved
      against, to check the images actually exist on disk.

Function Index:
    - validate_cleaned_markdown(markdown_text: str, base_dir: Path) -> dict
        Returns {"status": "PASS" | "FAIL", "errors": list[str]}.

Usage:
    from pandoc.validate import validate_cleaned_markdown
    result = validate_cleaned_markdown(cleaned_text, Path("output/my-doc"))
    if result["status"] == "FAIL":
        raise RuntimeError("\\n".join(result["errors"]))
"""

import re
from pathlib import Path

# Alt text uses `(?:[^\]\\]|\\.)*` rather than a naive `[^\]]*` -- see
# scripts/package.py's _IMAGE_REF docstring: a markdown-escaped `]` in alt
# text (pandoc emits `\]` for a literal `]` byte) otherwise terminates the
# character class early and the whole reference is silently missed.
_IMAGE_LINK = re.compile(r'!\[(?:[^\]\\]|\\.)*\]\(([^)]+)\)')
# Each attribute starts with a different character class (`.`, `#`, word) and an unquoted value cannot contain quotes, braces or
# whitespace, so every `{...}` has exactly one tokenization: no ambiguity, no catastrophic backtracking.
_ATTR_ITEM = r'(?:\.[\w-]+|#[\w-]+|[\w-]+=(?:"[^"]*"|[^\s"}][^\s}]*))'
_ATTR_ARTIFACT = re.compile(
    r'\{\s*' + _ATTR_ITEM + r'(?:(?:\s+|(?=[.#]))' + _ATTR_ITEM + r')*\s*\}'
)
_HEADING_WITH_IMAGE = re.compile(r'^#{1,6} .*!\[(?:[^\]\\]|\\.)*\]\([^)]*\).*$', re.MULTILINE)


def validate_cleaned_markdown(markdown_text: str, base_dir: Path) -> dict:
    """Validate cleaned markdown text, hard-failing on known cleanup gaps.

    Returns a dict with `status` ("PASS"/"FAIL") and `errors` (list[str]).
    An empty `errors` list always corresponds to `status == "PASS"`.
    """
    base_dir = Path(base_dir)
    errors: list[str] = []

    for match in _IMAGE_LINK.finditer(markdown_text):
        image_path = match.group(1).strip()
        if image_path.startswith(("http://", "https://")):
            continue
        resolved = base_dir / image_path
        if not resolved.exists():
            errors.append(f"Unresolved image link: {image_path!r} does not exist under {base_dir}")

    if _ATTR_ARTIFACT.search(markdown_text):
        errors.append("Leftover pandoc attribute artifact found (e.g. {width=...}, {.underline}, {.mark}); attrs.py cleanup did not fully run")

    for match in _HEADING_WITH_IMAGE.finditer(markdown_text):
        errors.append(f"Image embedded directly in heading line: {match.group(0)!r}")

    status = "FAIL" if errors else "PASS"
    return {"status": status, "errors": errors}
