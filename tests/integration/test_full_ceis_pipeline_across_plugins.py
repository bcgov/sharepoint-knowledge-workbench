"""
test_full_ceis_pipeline_across_plugins.py
============================================

Phase 4.5 Wave 6, repository-wide reconciliation (plugin/skill names
updated for the post-Wave-9 naming refactor -- see
docs/reports/phase-4-5-core-plugin-refactoring/plugin-skill-name-migration.md):
proves the CEIS manual converts byte-identically (modulo documented
run-specific fields) when run through the four independently-installed
domain plugins (source-document-extraction, document-structure-analysis,
structured-content-assembly, structured-content-rendering) chained via
their real public interfaces -- `structured_content_assembly.
build_canonical_package` then `structured_content_rendering.render` --
compared against the pre-Phase-4.5 combined docx-to-content pipeline's
own recorded baseline (`runs/ceis-manual-v2/`).

Each stage runs in its OWN subprocess with only that plugin's scripts/
directory on sys.path. This is not a workaround: structured-content-
assembly and structured-content-rendering both share several identically-
named bare modules via managed cross-plugin symlinks (canonical_schema,
atomic_output, hashing, dispositions, publication_map, canonical_package
-- see wave-9-duplication-remediation-report.md), so importing both by
bare name in ONE long-lived interpreter causes a real namespace collision
(only one plugin's copy of each shared name survives on sys.path).
Running each stage in its own process is how these plugins are actually
meant to be invoked -- each as its own independently installed
skill/CLI -- and mirrors combined_install_check.py's own choice to run
each plugin's test suite in an isolated subprocess.

Per the Wave 6 plan: the `pytest.skip` branch below (missing gitignored
confirmed plan, missing intake docx, or pandoc unavailable) is retained
for ordinary development runs only. At Wave 6's closure, this test was
executed with zero skips and its computed hashes were recorded in
docs/superpowers/plans/phase-4-5-evidence/wave-6-golden-master-manifest.json
(and the copy at tests/golden-master/ceis/manifest.json).
"""

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GOLDEN_MASTER_MANIFEST = REPO_ROOT / "tests" / "golden-master" / "ceis" / "manifest.json"
SOURCE_DOCX = REPO_ROOT / "intake" / "CEIS MANUAL - working version.docx"
CONFIRMED_PLAN = REPO_ROOT / "temp" / "ceis-manual-analysis" / "conversion-plan.confirmed.json"

PANDOC_AVAILABLE = shutil.which("pandoc") is not None
SOFFICE_AVAILABLE = shutil.which("soffice") is not None


def _tree_hash(root: Path, exclude: set) -> str:
    files = sorted(p for p in root.rglob("*") if p.is_file() and p.name not in exclude)
    h = hashlib.sha256()
    for f in files:
        h.update(str(f.relative_to(root)).encode())
        h.update(f.read_bytes())
    return h.hexdigest()


def _run_canonical_stage(plan: dict, source_path: Path, output_dir: Path) -> dict:
    """Subprocess 1: only structured-content-assembly's scripts/ on sys.path."""
    script = f"""
import sys, json
sys.path.insert(0, {str(REPO_ROOT / "plugins" / "structured-content-assembly" / "scripts")!r})
import structured_content_assembly
plan = json.loads({json.dumps(json.dumps(plan))})
result = structured_content_assembly.build_canonical_package(
    plan, {str(source_path)!r}, {str(output_dir)!r}
)
print(json.dumps(result))
"""
    proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip().splitlines()[-1])


def _run_render_stage(package_dir: str, output_dir: Path) -> dict:
    """Subprocess 2: only structured-content-rendering's scripts/ on sys.path."""
    script = f"""
import sys, json
sys.path.insert(0, {str(REPO_ROOT / "plugins" / "structured-content-rendering" / "scripts")!r})
import structured_content_rendering
result = structured_content_rendering.render({package_dir!r}, {str(output_dir)!r})
print(json.dumps(result))
"""
    proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip().splitlines()[-1])


@pytest.mark.skipif(
    not (PANDOC_AVAILABLE and SOFFICE_AVAILABLE and SOURCE_DOCX.exists() and CONFIRMED_PLAN.exists()),
    reason=(
        "requires pandoc, soffice, the intake CEIS docx, and a real confirmed "
        "plan at temp/ceis-manual-analysis/conversion-plan.confirmed.json "
        "(gitignored -- produced by a real `analyze`+`confirm` run per "
        "start-here.md). This skip is for ordinary development runs only; "
        "Wave 6's own gate was closed only after running this assertion "
        "path with zero skips -- see wave-6-golden-master-manifest.json."
    ),
)
def test_ceis_pipeline_across_four_plugins_matches_golden_master(tmp_path):
    manifest = json.loads(GOLDEN_MASTER_MANIFEST.read_text())

    source_sha256 = hashlib.sha256(SOURCE_DOCX.read_bytes()).hexdigest()
    assert source_sha256 == manifest["source_docx_sha256"], (
        "intake docx changed since the golden master was recorded -- "
        "re-run analyze+confirm and update the golden-master manifest"
    )

    plan = json.loads(CONFIRMED_PLAN.read_text())
    assert plan["source"]["sha256"] == source_sha256, (
        "confirmed plan's recorded source fingerprint no longer matches "
        "the current intake docx"
    )

    canonical_out = tmp_path / "canonical"
    canonical_result = _run_canonical_stage(plan, SOURCE_DOCX, canonical_out)
    assert canonical_result["promoted"] is True
    assert canonical_result["validation_report"]["status"] == "PASS"

    render_out = tmp_path / "rendered"
    render_result = _run_render_stage(canonical_result["package_dir"], render_out)
    assert render_result["promoted"] is True
    assert render_result["validation_report"]["status"] == "PASS"

    canonical_hash = _tree_hash(
        Path(canonical_result["package_dir"]), exclude={"generator-info.json"}
    )
    rendered_hash = _tree_hash(
        Path(render_result["output_dir"]),
        exclude={"generator-info.json", "render-result.json"},
    )

    assert canonical_hash == manifest["canonical_content_tree_hash_excl_generator_info"]
    assert rendered_hash == manifest["rendered_output_tree_hash_excl_generator_info_and_render_result"]
