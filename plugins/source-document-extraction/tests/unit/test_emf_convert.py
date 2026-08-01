#!/usr/bin/env python
"""
test_emf_convert.py
====================

TDD-first: failing tests for emf_convert.py.
Covers converting legacy Enhanced Metafile (.emf) / Windows Metafile (.wmf)
media to .png via the LibreOffice `soffice` CLI, and returning an
old-filename -> new-filename mapping for markdown reference rewriting.

Real conversion tests are skipped with a clear reason when `soffice` is not
on PATH in the current environment (a sandboxed test runner should not fail
the whole suite over a missing system dependency), but non-conversion
behavior (empty dir, no legacy media present) is always exercised.

Usage:
    pytest plugins/docx-to-content/tests/unit/test_emf_convert.py -v
"""

import shutil
import struct
from pathlib import Path

import pytest

from emf_convert import convert_legacy_media

SOFFICE_AVAILABLE = shutil.which("soffice") is not None


def _write_minimal_emf(path: Path) -> None:
    """Write a minimal but structurally valid, real .emf file (a bare
    EMR_HEADER + EMR_EOF record, no drawing primitives) so the real-
    conversion test exercises actual `soffice` conversion rather than a
    synthetic stub soffice would just reject."""
    header_size = 88
    eof_size = 20
    total = header_size + eof_size

    header = struct.pack("<II", 1, header_size)  # iType=EMR_HEADER, nSize
    header += struct.pack("<4i", 0, 0, 99, 99)  # rclBounds
    header += struct.pack("<4i", 0, 0, 2540, 2540)  # rclFrame (.01mm)
    header += struct.pack("<I", 0x464D4520)  # dSignature ('EMF ' as DWORD)
    header += struct.pack("<I", 0x00010000)  # nVersion
    header += struct.pack("<I", total)  # nBytes
    header += struct.pack("<I", 2)  # nRecords (header + eof)
    header += struct.pack("<HH", 1, 0)  # nHandles, sReserved
    header += struct.pack("<I", 0)  # nDescription
    header += struct.pack("<I", 0)  # offDescription
    header += struct.pack("<I", 0)  # nPalEntries
    header += struct.pack("<2i", 320, 240)  # szlDevice
    header += struct.pack("<2i", 96, 72)  # szlMillimeters

    eof = struct.pack("<II", 14, eof_size)  # iType=EMR_EOF, nSize
    eof += struct.pack("<III", 0, 0, eof_size)  # nPalEntries, offPalEntries, nSizeLast

    path.write_bytes(header + eof)


class TestConvertLegacyMedia:
    def test_empty_directory_returns_empty_mapping(self, tmp_path: Path):
        result = convert_legacy_media(tmp_path)
        assert result == {}

    def test_directory_with_no_legacy_media_returns_empty_mapping(self, tmp_path: Path):
        (tmp_path / "image1.png").write_bytes(b"not a real png, just a stub")
        result = convert_legacy_media(tmp_path)
        assert result == {}
        # Non-legacy files must be left untouched.
        assert (tmp_path / "image1.png").exists()

    @pytest.mark.skipif(not SOFFICE_AVAILABLE, reason="soffice not found on PATH in this environment")
    def test_converts_emf_to_png_and_returns_mapping(self, tmp_path: Path):
        emf_path = tmp_path / "image1.emf"
        _write_minimal_emf(emf_path)

        result = convert_legacy_media(tmp_path)

        assert "image1.emf" in result
        assert result["image1.emf"] == "image1.png"
        assert (tmp_path / "image1.png").exists()
