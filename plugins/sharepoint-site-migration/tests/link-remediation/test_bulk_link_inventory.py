"""Bulk local extraction preserves source identity and reports format coverage."""
import csv
import importlib.util
import json
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/link-remediation/export_link_inventory.py"


def load_exporter():
    assert SCRIPT.exists(), "bulk link CSV exporter is missing"
    spec = importlib.util.spec_from_file_location("bulk_links", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_static_office_and_modern_sources(tmp_path):
    exporter = load_exporter()
    source = tmp_path / "source"
    (source / "a").mkdir(parents=True)
    (source / "b").mkdir()
    for folder in ("a", "b"):
        (source / folder / "default.aspx").write_text('<a href="../doc.pdf?a=1&amp;b=2">Doc</a><img src="/images/x.png">', encoding="utf-8")
    with zipfile.ZipFile(source / "book.docx", "w") as archive:
        archive.writestr("word/_rels/document.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="r1" TargetMode="External" Target="https://example.test/reference" Type="hyperlink"/></Relationships>')
    (source / "modern.page.json").write_text(json.dumps({
        "SourceUrl": "https://example.test/SitePages/news.aspx", "WebUrl": "https://example.test", "LibraryTitle": "Site Pages",
        "Fields": {"CanvasContent1": '<a href="/docs/guide.pdf">Guide</a>', "LayoutWebpartsContent": '[{"properties":{"imageUrl":"/images/banner.png"}}]'},
    }), encoding="utf-8")
    (source / "scan.pdf").write_bytes(b"%PDF test")
    report = exporter.run(source_dir=source, output_dir=tmp_path / "out", base_url="https://example.test/pages/")
    assert report["Status"] == "PARTIAL"  # PDF coverage is explicit
    with (tmp_path / "out/links.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len({row["SourceUrl"] for row in rows if row["LocalPath"].endswith("default.aspx")}) == 2
    assert any(row["RawUrl"] == "../doc.pdf?a=1&b=2" for row in rows)
    assert any(row["ResolvedUrl"] == "https://example.test/pages/doc.pdf?a=1&b=2" for row in rows)
    assert any(row["SourcePart"].endswith(".rels") for row in rows)
    assert any(row["RawUrl"] == "/images/banner.png" and row["SourcePart"] == "LayoutWebpartsContent" for row in rows)
    assert "NOT_SUPPORTED" in (tmp_path / "out/sources.csv").read_text(encoding="utf-8-sig")


def test_manifest_keeps_remote_url_and_download_failures(tmp_path):
    exporter = load_exporter()
    page = tmp_path / "local.html"
    page.write_text('<a href="relative.aspx">Next</a>', encoding="utf-8")
    manifest = tmp_path / "downloads.csv"
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["FileUrl", "LocalPath", "Status", "WebUrl", "LibraryTitle"])
        writer.writeheader()
        writer.writerow({"FileUrl": "https://example.test/sub/pages/start.html", "LocalPath": str(page), "Status": "DOWNLOADED", "LibraryTitle": "Docs"})
        writer.writerow({"FileUrl": "https://example.test/sub/pages/missing.html", "Status": "FAILED"})
    report = exporter.run(manifest_csv=manifest, output_dir=tmp_path / "out")
    assert report["Status"] == "PARTIAL"
    assert report["SourceCount"] == 2
    text = (tmp_path / "out/links.csv").read_text(encoding="utf-8-sig")
    assert "https://example.test/sub/pages/relative.aspx" in text
    assert "Docs" in text


def test_empty_and_unreadable_are_distinct(tmp_path):
    exporter = load_exporter()
    page = tmp_path / "empty.htm"
    page.write_text("<p>No links</p>", encoding="utf-8")
    assert exporter.run(source_dir=tmp_path, output_dir=tmp_path / "out")["Status"] == "EMPTY"
    bad = tmp_path / "bad.docx"
    bad.write_text("not a zip", encoding="utf-8")
    assert exporter.run(source_dir=tmp_path, output_dir=tmp_path / "other")["Status"] == "PARTIAL"
