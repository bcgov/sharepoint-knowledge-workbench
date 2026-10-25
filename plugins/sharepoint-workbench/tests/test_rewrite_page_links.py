"""Tests for rewrite_page_links.py (real ledger CSV file I/O and a real CLI subprocess).

Key Input Dependencies: publishing-sharepoint-pages/scripts/rewrite_page_links.py.
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
SKILLS_DIR = PLUGIN / ".apm" / "skills" if (PLUGIN / ".apm" / "skills").exists() else PLUGIN / "skills"
SKILL = SKILLS_DIR / "publishing-sharepoint-pages"
SCRIPT = SKILL / "scripts" / "rewrite_page_links.py"
sys.path.insert(0, str(SCRIPT.parent))
import rewrite_page_links as r  # noqa: E402

HOST = "https://csb.jag.gov.bc.ca"
BASE = f"{HOST}/Sheriff/Administration Documents"
PAGE = f"{BASE}/ohs/compliance_reviews/index.aspx"


def row(url, folder, name, status="UPLOADED"):
    return {"FileUrl": url, "TargetLibrary": "Sheriff", "TargetFolder": folder,
            "TargetFilename": name, "Status": status}


ROWS = [
    row(PAGE, "Administration Documents/ohs/compliance_reviews", "index.html", "CONVERTED"),
    row(f"{BASE}/ohs/compliance_reviews/abbotsford.pdf", "Administration Documents/ohs/compliance_reviews", "abbotsford.pdf"),
    row(f"{BASE}/awards/criteria_processes.aspx", "Administration Documents/awards", "criteria_processes.html"),
    row(f"{BASE}/ohs/compliance_reviews/pending.pdf", "Administration Documents/ohs/compliance_reviews", "pending.pdf", "DOWNLOADED"),
]


def rewrite(html):
    return r.rewrite_links(html, PAGE, ROWS, HOST)


def test_absolute_source_url_becomes_same_folder_relative_link():
    html, report = rewrite(f'<a href="{HOST}/Sheriff/Administration%20Documents/ohs/compliance_reviews/abbotsford.pdf">A</a>')
    assert 'href="abbotsford.pdf"' in html
    assert report[0]["status"] == "rewritten"


def test_already_relative_link_is_unchanged_and_reported_resolved():
    html, report = rewrite('<a href="abbotsford.pdf">A</a>')
    assert 'href="abbotsford.pdf"' in html
    assert report[0]["status"] == "unchanged"


def test_cross_folder_link_rewritten_relative_to_page():
    html, report = rewrite(f'<a href="{HOST}/Sheriff/Administration%20Documents/awards/criteria_processes.aspx">B</a>')
    assert 'href="../../awards/criteria_processes.html"' in html
    assert report[0]["status"] == "rewritten"


def test_unresolved_link_left_unchanged_and_reported():
    html, report = rewrite(f'<a href="{HOST}/Sheriff/Administration%20Documents/ohs/compliance_reviews/missing.pdf">C</a>')
    assert 'href="https://csb.jag.gov.bc.ca/Sheriff/Administration%20Documents/ohs/compliance_reviews/missing.pdf"' in html
    assert report[0]["status"] == "unresolved"
    assert report[0]["reason"] == "not in ledger"


def test_link_to_file_not_yet_uploaded_is_unresolved():
    html, report = rewrite(f'<a href="{HOST}/Sheriff/Administration%20Documents/ohs/compliance_reviews/pending.pdf">D</a>')
    assert report[0]["status"] == "unresolved"
    assert "DOWNLOADED" in report[0]["reason"]


def test_external_link_is_ignored():
    html, report = rewrite('<a href="https://example.com/x.pdf">E</a>')
    assert 'href="https://example.com/x.pdf"' in html
    assert report == []


def test_anchor_only_link_is_ignored():
    html, report = rewrite('<a href="#section">F</a>')
    assert 'href="#section"' in html
    assert report == []


def test_preserves_query_and_fragment_on_rewritten_link():
    html, report = rewrite(f'<a href="{HOST}/Sheriff/Administration%20Documents/awards/criteria_processes.aspx?view=1#top">G</a>')
    assert 'href="../../awards/criteria_processes.html?view=1#top"' in html


def test_img_src_is_rewritten():
    html, report = rewrite(f'<img src="{HOST}/Sheriff/Administration%20Documents/ohs/compliance_reviews/abbotsford.pdf">')
    assert 'src="abbotsford.pdf"' in html
    assert report[0]["status"] == "rewritten"


def test_target_site_chrome_paths_are_ignored():
    original = '<img src="/sites/AG-CSB-INTRANET-DEV/SiteAssets/x.png"><a href="/sites/AG-CSB-INTRANET-DEV">Home</a>'
    html, report = rewrite(original)
    assert html == original
    assert report == []


def test_cli_writes_output_and_report_and_exits_nonzero_on_unresolved(tmp_path):
    ledger = tmp_path / "ledger.csv"
    with ledger.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(ROWS[0]))
        w.writeheader()
        w.writerows(ROWS)
    src = tmp_path / "in.html"
    src.write_text(f'<a href="{BASE}/ohs/compliance_reviews/abbotsford.pdf">A</a><img src="../x.jpg">', encoding="utf-8")
    out, rep = tmp_path / "out.html", tmp_path / "report.json"
    done = subprocess.run([sys.executable, str(SCRIPT), str(src), "--ledger", str(ledger), "--page-url", PAGE,
                           "--source-host", HOST, "--output", str(out), "--report", str(rep)],
                          capture_output=True, text=True)
    assert done.returncode == 1
    assert 'href="abbotsford.pdf"' in out.read_text(encoding="utf-8")
    assert {e["status"] for e in json.loads(rep.read_text(encoding="utf-8"))} == {"rewritten", "unresolved"}
