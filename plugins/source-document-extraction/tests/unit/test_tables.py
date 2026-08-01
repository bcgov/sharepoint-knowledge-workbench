#!/usr/bin/env python
"""
test_tables.py
==============

TDD-first: failing tests for pandoc/tables.py.
Covers detecting/fixing malformed pandoc-emitted markdown tables: missing or
malformed header separator rows (must exist and match the header column
count).

Usage:
    pytest plugins/docx-to-content/tests/unit/test_tables.py -v
"""

from pandoc.tables import fix_malformed_tables


class TestFixMalformedTables:
    def test_inserts_missing_separator_row(self):
        text = (
            "| Name | Value |\n"
            "| Alpha | 1 |\n"
            "| Beta | 2 |\n"
        )
        expected = (
            "| Name | Value |\n"
            "| --- | --- |\n"
            "| Alpha | 1 |\n"
            "| Beta | 2 |\n"
        )
        assert fix_malformed_tables(text) == expected

    def test_fixes_separator_row_with_wrong_column_count(self):
        text = (
            "| Name | Value | Note |\n"
            "| --- | --- |\n"
            "| Alpha | 1 | ok |\n"
        )
        expected = (
            "| Name | Value | Note |\n"
            "| --- | --- | --- |\n"
            "| Alpha | 1 | ok |\n"
        )
        assert fix_malformed_tables(text) == expected

    def test_leaves_well_formed_table_untouched(self):
        text = (
            "| Name | Value |\n"
            "| --- | --- |\n"
            "| Alpha | 1 |\n"
        )
        assert fix_malformed_tables(text) == text

    def test_leaves_non_table_text_untouched(self):
        text = "Section One\n\nThis is a normal paragraph, no pipes at all.\n"
        assert fix_malformed_tables(text) == text

    def test_leaves_grid_table_untouched(self):
        # Pandoc emits grid tables (bounded by +---+/+===+ lines) for complex/
        # merged-cell Word tables. Grid tables already carry their own valid
        # header-separator convention (the +===+ boundary) and must not be
        # mistaken for headerless pipe tables -- each `| ... |` content row
        # sits between `+---+` boundary lines, and naively applying pipe-table
        # separator-insertion logic to it injects a spurious `| --- | --- |`
        # row after every single data row, corrupting an already-valid table.
        text = (
            "+------+------+\n"
            "| A    | B    |\n"
            "+======+======+\n"
            "| val1 | val2 |\n"
            "+------+------+\n"
            "| val3 | val4 |\n"
            "+------+------+\n"
        )
        assert fix_malformed_tables(text) == text
