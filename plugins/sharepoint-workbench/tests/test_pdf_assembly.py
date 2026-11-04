"""End-to-end test: a text-layer PDF flows through extraction, analysis, assembly and Markdown render.

Purpose: verify assembly accepts a PDF source and the rendered pages carry the breadcrumb.

Key Input Dependencies: scripts/extraction, structure-analysis, assembly, rendering; PyMuPDF.
"""
import sys
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")

_plugin_dir = Path(__file__).resolve().parents[1]
_skills_dir = _plugin_dir / ".apm" / "skills" if (_plugin_dir / ".apm" / "skills").exists() else _plugin_dir / "skills"
_SCRIPTS = _skills_dir / "converting-sharepoint-documents" / "scripts"
for sub in ("assembly", "rendering", "structure-analysis", "extraction", ""):
    sys.path.insert(0, str(_SCRIPTS / sub) if sub else str(_SCRIPTS))

import pdf_extraction  # noqa: E402
import document_structure_analysis as dsa  # noqa: E402
import plans  # noqa: E402
import structured_content_assembly as sca  # noqa: E402
import structured_content_rendering as scr  # noqa: E402
from plan_schema import analysis_plan as plan_contracts  # noqa: E402


def test_pdf_assembles_and_renders_with_breadcrumb(tmp_path):
    pdf = tmp_path / "Crown_Manual.pdf"
    doc = fitz.open()
    for title, body in (("Bail", "Bail rules caf\u00e9 text."), ("Appeals", "Appeal rules text.")):
        page = doc.new_page()
        page.insert_text((72, 72), title, fontsize=18)
        page.insert_text((72, 110), body, fontsize=11)
    doc.set_toc([[1, "Bail", 1], [1, "Appeals", 2]])
    doc.save(pdf)
    doc.close()

    normalized = pdf_extraction.extract_pdf_and_normalize(pdf, tmp_path / "analysis")
    draft = plan_contracts.ConversionPlan.from_dict(dsa.recommend_from_normalized(normalized))
    confirmed = plans.confirm_plan(draft)

    built = sca.build_canonical_package(confirmed.to_dict(), pdf, tmp_path / "pkg")
    assert built["promoted"], built["validation_report"]

    rendered = scr.render(Path(built["package_dir"]), tmp_path / "out")
    assert rendered["promoted"], rendered["validation_report"]
    pages = list((Path(rendered["output_dir"]) / "pages").glob("*.md"))
    text = "\n".join(p.read_text(encoding="utf-8") for p in pages)
    assert "> Document: Crown Manual | Section: Bail" in text
    assert "caf\u00e9" in text
