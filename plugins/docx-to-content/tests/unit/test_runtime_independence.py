"""
test_runtime_independence.py
===============================

Phase 2, spec Section 5.4: proves rendering works when the real source
.docx, intake/, and temp/ analysis artifacts are physically absent -- not
merely unused. Complements test_import_boundaries.py's static proof with
a behavioral one.
"""

from pathlib import Path
import sys

# Ensure the tests/unit directory is on sys.path so local test helper modules
# (like test_independent_fixture.py) can be imported when running a single
# test file directly.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from canonical_package import CanonicalPackage
from renderers.multipage_markdown import MultipageMarkdownRenderer
from test_independent_fixture import _build_independent_fixture


def test_render_succeeds_with_no_docx_intake_or_temp_directory_present(tmp_path, monkeypatch):
    # Build the fixture in an isolated tmp_path that has no intake/ or
    # temp/ sibling directories at all -- there is nothing to accidentally
    # fall back to.
    package_dir = _build_independent_fixture(tmp_path)
    assert not (tmp_path / "intake").exists()
    assert not (tmp_path / "temp").exists()
    assert not any(tmp_path.rglob("*.docx"))

    package = CanonicalPackage.load(package_dir)
    result = MultipageMarkdownRenderer().render(package, tmp_path / "rendered-output")
    assert result.status == "PASS"
