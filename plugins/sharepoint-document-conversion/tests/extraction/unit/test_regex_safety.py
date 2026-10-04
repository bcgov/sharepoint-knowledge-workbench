"""Regression tests for regular-expression safety (CodeQL: inefficient regular expression).

The grid-table separator and the leftover pandoc-attribute patterns must match exactly what they always matched, and must stay
linear-time on adversarial input (long runs of `=`/`-`/`!`) that previously allowed exponential backtracking.
"""

import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "extraction"))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "extraction" / "pandoc"))

import heading_parsing  # noqa: E402
import validate  # noqa: E402

GRID = heading_parsing._GRID_TABLE_HEADER_SEPARATOR
ATTR = validate._ATTR_ARTIFACT
BUDGET_SECONDS = 1.0


@pytest.mark.parametrize("line, expected", [
    ("+===+", True), ("+=+=+", True), ("+:=:+---+", False), ("+:=:+:=:+", True), ("  +===+===+  ", True),
    ("+---+", False), ("+--+==+", False), ("+=", False), ("=+", False), ("+++", False),
])
def test_grid_table_header_separator_matches_only_rows_with_an_equals_in_every_segment(line, expected):
    assert bool(GRID.match(line)) is expected


@pytest.mark.parametrize("text, expected", [
    ("{.class}", ["{.class}"]), ("{#id}", ["{#id}"]), ("{.a .b}", ["{.a .b}"]), ("{.a.b}", ["{.a.b}"]), ("{key=val}", ["{key=val}"]),
    ('{key="a b"}', ['{key="a b"}']), ('{.a key="x y" #z}', ['{.a key="x y" #z}']), ("{width=50% height=3}", ["{width=50% height=3}"]),
    ("{}", []), ("{-=}", []), ("{.a}{.b}", ["{.a}", "{.b}"]), ("text {.x} text", ["{.x}"]),
])
def test_attribute_artifact_pattern_matches_what_it_always_matched(text, expected):
    assert [m.group(0) for m in ATTR.finditer(text)] == expected


@pytest.mark.parametrize("pattern, text", [
    (GRID, "+=" + "==" * 50000 + "x"),
    (ATTR, "{" + "-=!" * 50000),
    (ATTR, "{." + "---=!." * 30000),
    (ATTR, "{#" + "---=!#" * 30000),
    (ATTR, '{-=' + '!-=' * 50000),
])
def test_adversarial_input_is_handled_in_linear_time(pattern, text):
    start = time.perf_counter()
    pattern.search(text)
    assert time.perf_counter() - start < BUDGET_SECONDS
