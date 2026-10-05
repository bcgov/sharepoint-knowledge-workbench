"""Purpose: Integration tests for the local legacy ASPX-to-HTML PowerShell converter.

Key input dependencies: PowerShell 7, pytest, and the canonical converter script in
plugins/sharepoint-site-migration/scripts/.

Functions:
- run_converter: Execute the real converter process against temporary source/output files.
- test_rejects_active_markup_without_writing_output: Reject common active markup.
- test_protects_existing_output_unless_overwrite_is_explicit: Require explicit overwrite.
- test_refuses_output_path_that_resolves_to_source: Preserve the ASPX source on collision.
- test_removes_known_legacy_artifacts_and_preserves_content: Preserve conversion behavior.
- test_uses_sibling_html_output_by_default: Preserve default output-path behavior.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

import pytest

CONVERTER = Path(__file__).resolve().parents[2] / "scripts" / "convert-aspx-to-html.ps1"


def run_converter(
    source_path: Path,
    output_path: Optional[Path],
    *options: str,
) -> subprocess.CompletedProcess[str]:
    """Run the canonical PowerShell converter with real filesystem inputs."""
    command = [
        "pwsh",
        "-NoLogo",
        "-NoProfile",
        "-File",
        str(CONVERTER),
        "-SourcePath",
        str(source_path),
    ]
    if output_path is not None:
        command.extend(["-OutputPath", str(output_path)])
    command.extend(options)
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


@pytest.mark.parametrize(
    "active_markup",
    [
        "<script>alert(1)</script>",
        '<img src="x" onerror="alert(1)">',
        '<iframe src="https://example.invalid"></iframe>',
        '<div srcdoc="<script>alert(1)</script>"></div>',
        '<a href="javascript:alert(1)">open</a>',
    ],
)
def test_rejects_active_markup_without_writing_output(
    tmp_path: Path,
    active_markup: str,
) -> None:
    """Reject common active markup before creating any output file."""
    source_path = tmp_path / "source.aspx"
    output_path = tmp_path / "converted.html"
    source_path.write_text(f"<html><body>{active_markup}</body></html>", encoding="utf-8")

    result = run_converter(source_path, output_path)

    assert result.returncode != 0
    assert "active" in result.stderr.lower() or "active" in result.stdout.lower()
    assert not output_path.exists()
    assert source_path.read_text(encoding="utf-8") == (
        f"<html><body>{active_markup}</body></html>"
    )


def test_protects_existing_output_unless_overwrite_is_explicit(tmp_path: Path) -> None:
    """Keep existing output unchanged unless the caller passes -Overwrite."""
    source_path = tmp_path / "source.aspx"
    output_path = tmp_path / "converted.html"
    source_path.write_text("<html><body>new content</body></html>", encoding="utf-8")
    output_path.write_text("existing content", encoding="utf-8")

    protected_result = run_converter(source_path, output_path)

    assert protected_result.returncode != 0
    assert output_path.read_text(encoding="utf-8") == "existing content"

    overwrite_result = run_converter(source_path, output_path, "-Overwrite")

    assert overwrite_result.returncode == 0, overwrite_result.stderr
    assert "new content" in output_path.read_text(encoding="utf-8")


def test_refuses_output_path_that_resolves_to_source(tmp_path: Path) -> None:
    """Reject source/output collisions without changing the source file."""
    source_path = tmp_path / "source.aspx"
    source_content = "<html><body>keep original</body></html>"
    source_path.write_text(source_content, encoding="utf-8")

    result = run_converter(source_path, source_path)

    assert result.returncode != 0
    assert source_path.read_text(encoding="utf-8") == source_content


def test_removes_known_legacy_artifacts_and_preserves_content(tmp_path: Path) -> None:
    """Retain useful content while removing known legacy-only markup."""
    source_path = tmp_path / "source.aspx"
    output_path = tmp_path / "converted.html"
    source_path.write_text(
        """<%@ Page %><html><head><title>Sample</title></head><body>
<script src="WebResource.axd"></script>
<img src="spacer.gif"><table><tr><td><p>Useful text</p></td></tr></table>
<table><tr><th>Column</th></tr><tr><td>Value</td></tr></table>
</body></html>""",
        encoding="utf-8",
    )

    result = run_converter(source_path, output_path)

    assert result.returncode == 0, result.stderr
    converted = output_path.read_text(encoding="utf-8")
    assert "<title>Sample</title>" in converted
    assert "Useful text" in converted
    assert "<th>Column</th>" in converted
    assert "WebResource.axd" not in converted
    assert "spacer.gif" not in converted


def test_uses_sibling_html_output_by_default(tmp_path: Path) -> None:
    """Write the default output beside the source and keep the source intact."""
    source_path = tmp_path / "source.aspx"
    output_path = tmp_path / "source.html"
    source_content = "<html><body>default output</body></html>"
    source_path.write_text(source_content, encoding="utf-8")

    result = run_converter(source_path, None)

    assert result.returncode == 0, result.stderr
    assert output_path.exists()
    assert "default output" in output_path.read_text(encoding="utf-8")
    assert source_path.read_text(encoding="utf-8") == source_content
