"""test_golden_master_aspx.py
============================

Purpose:
    Phase 6 Task 0.16's ASPX golden-master fidelity proof, mirroring the Phase 2 Subphase 2.5.4 pattern already established for `render-markdown-pages` (see `docs/superpowers/plans/ phase-4-5-evidence/wave-6-golden-master-manifest.json`): render the REAL sample manual canonical package through `render-sharepoint-pages` and prove the fresh render is byte-identical to a recorded baseline, established once and committed at `runs/sample-manual/render-aspx/ rendered-output/`.

Key Input Dependencies:
    - pytest and the plugin-local tests in this namespace
    - shutil
    - pathlib
    - pytest
    - canonical_package
    - compare_rendered_output
    - renderers.validate_rendered

Phase 6 Task 0.16's ASPX golden-master fidelity proof, mirroring the
Phase 2 Subphase 2.5.4 pattern already established for
`render-markdown-pages` (see `docs/superpowers/plans/
phase-4-5-evidence/wave-6-golden-master-manifest.json`): render the
REAL sample manual canonical package through `render-sharepoint-pages` and
prove the fresh render is byte-identical to a recorded baseline,
established once and committed at `runs/sample-manual/render-aspx/
rendered-output/`.

This is a real end-to-end proof, not a synthetic-fixture test -- it
loads the actual 25-chunk, 319-media-file, grouped-strategy sample
canonical package (`runs/sample-manual/canonical-content/`, the same
package `render-markdown-pages`'s own golden master was built from)
and runs it through the full `render_and_promote_aspx` stage -> validate
-> promote pipeline.

Key Functions Index:
    - test_real_sample_package_renders_and_validates_pass()
    - test_fresh_render_matches_committed_golden_baseline()"""

import shutil
from pathlib import Path

import pytest

import canonical_package
import compare_rendered_output as cro
from renderers.validate_rendered import render_and_promote_aspx

PANDOC_AVAILABLE = shutil.which("pandoc") is not None
requires_pandoc = pytest.mark.skipif(not PANDOC_AVAILABLE, reason="pandoc not on PATH")

_REPO_ROOT = Path(__file__).resolve().parents[5]
_sample_CANONICAL_CONTENT = _REPO_ROOT / "runs" / "sample-manual" / "canonical-content"
_GOLDEN_BASELINE = _REPO_ROOT / "runs" / "sample-manual" / "render-aspx" / "rendered-output"

requires_sample_evidence = pytest.mark.skipif(
    not _sample_CANONICAL_CONTENT.exists(),
    reason="runs/sample-manual/canonical-content/ evidence not present in this checkout",
)


# Verify real sample package renders and validates pass.
@requires_pandoc
@requires_sample_evidence
def test_real_sample_package_renders_and_validates_pass(tmp_path):
    """Verify real sample package renders and validates pass."""
    package = canonical_package.CanonicalPackage.load(_sample_CANONICAL_CONTENT)
    assert len(package.chunks) == 25
    assert len(list(package.media_dir.glob("*"))) == 319

    result, report, promoted, final_dir = render_and_promote_aspx(package, tmp_path / "out")

    assert report.status == "PASS", report.issues
    assert promoted is True
    assert result.renderer_name == "sharepoint-aspx"
    assert len(list((final_dir / "pages").glob("*.html"))) == 25
    assert len(list((final_dir / "media").glob("*"))) == 319


# Verify fresh render matches committed golden baseline.
@requires_pandoc
@requires_sample_evidence
@pytest.mark.skipif(
    not (Path(__file__).resolve().parents[5] / "runs" / "sample-manual" / "render-aspx").exists(),
    reason="golden-master baseline not yet recorded at runs/sample-manual/render-aspx/",
)
def test_fresh_render_matches_committed_golden_baseline(tmp_path):
    """Verify fresh render matches committed golden baseline."""
    package = canonical_package.CanonicalPackage.load(_sample_CANONICAL_CONTENT)
    _, report, promoted, final_dir = render_and_promote_aspx(package, tmp_path / "out")
    assert report.status == "PASS", report.issues
    assert promoted is True

    comparison = cro.compare_rendered_trees(final_dir, _GOLDEN_BASELINE)
    assert comparison.status == "MATCH", comparison.issues
