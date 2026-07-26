#!/usr/bin/env python
"""
tables.py
=========

Fixes malformed markdown tables that pandoc can emit: a missing header
separator row, or a separator row whose column count does not match the
header row's column count. Standard markdown table renderers (GitHub,
VS Code) require a `---|---` style separator row immediately below the
header, with the same number of columns as the header — without it (or
with a mismatched count) the block renders as plain text instead of a
table.

Key Input Dependencies: none (pure string transform, no filesystem/network access).

Function Index:
    - fix_malformed_tables(markdown_text: str) -> str
        Scans for pipe-delimited table blocks, inserts a missing header
        separator row, or corrects one whose column count does not match
        the header.

Usage:
    from pandoc_fixes.tables import fix_malformed_tables
    cleaned = fix_malformed_tables(raw_markdown_text)
"""

import re

_PIPE_ROW = re.compile(r'^\s*\|.*\|\s*$')
_SEPARATOR_CELL = re.compile(r'^\s*:?-{1,}:?\s*$')


def _count_columns(row: str) -> int:
    """Count table columns in a pipe-delimited row, ignoring leading/
    trailing empty cells produced by outer pipes."""
    cells = row.strip().split("|")
    if cells and cells[0].strip() == "":
        cells = cells[1:]
    if cells and cells[-1].strip() == "":
        cells = cells[:-1]
    return len(cells)


def _is_separator_row(row: str) -> bool:
    cells = row.strip().strip("|").split("|")
    return all(_SEPARATOR_CELL.match(cell) for cell in cells) and len(cells) > 0


def _make_separator_row(column_count: int) -> str:
    return "| " + " | ".join(["---"] * column_count) + " |"


def fix_malformed_tables(markdown_text: str) -> str:
    """Ensure every pipe-delimited table has a correctly-sized header
    separator row.

    Leaves non-table text untouched. A well-formed table (separator row
    present, column count matching the header) is returned unchanged.
    """
    lines = markdown_text.splitlines(keepends=True)
    output = []
    i = 0
    n = len(lines)
    in_table = False  # True once we're past a table's header+separator rows

    while i < n:
        line = lines[i]
        stripped = line.rstrip("\n")

        if not _PIPE_ROW.match(stripped):
            in_table = False
            output.append(line)
            i += 1
            continue

        if in_table:
            # A data row within an already-established table: pass through.
            output.append(line)
            i += 1
            continue

        if not _is_separator_row(stripped):
            # Candidate table header row.
            header_col_count = _count_columns(stripped)
            next_stripped = lines[i + 1].rstrip("\n") if i + 1 < n else ""
            ending = line[len(stripped):] or "\n"

            if _is_separator_row(next_stripped):
                sep_col_count = _count_columns(next_stripped)
                if sep_col_count == header_col_count:
                    # Well-formed already; pass through both rows.
                    output.append(line)
                    output.append(lines[i + 1])
                    i += 2
                    in_table = True
                    continue
                # Malformed column count: replace the separator row.
                sep_ending = lines[i + 1][len(next_stripped):] or "\n"
                output.append(line)
                output.append(_make_separator_row(header_col_count) + sep_ending)
                i += 2
                in_table = True
                continue

            # No separator row at all: insert one.
            output.append(line)
            output.append(_make_separator_row(header_col_count) + ending)
            i += 1
            in_table = True
            continue

        # A standalone separator-shaped row with no preceding header in this
        # pass (already consumed as part of a header above in normal flow);
        # treat as an established table boundary to avoid re-processing.
        output.append(line)
        i += 1
        in_table = True
        continue

        output.append(line)
        i += 1

    return "".join(output)
