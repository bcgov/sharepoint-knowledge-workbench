#!/usr/bin/env python3
"""selftest.py: end-to-end check of both output formats on a PDF (default: examples/sample-handbook.pdf).

Usage: python scripts/selftest.py [PDF] [--work DIR] [--expect-images N]
Runs plan + build for agent-md and html, then verifies: PASS status, front matter keys, tables kept (pipe tables /
<table>), every relative link resolves, HTML tags balance, two builds are byte-identical, and images: extracted
files exist, are valid images, are listed in the manifest and referenced by both formats (Markdown image links with
alt text; HTML <figure><img><figcaption>), decorative ones are skipped, identical ones are shared.
With no PDF argument it also runs the extra cases: the no-image sample (nothing extracted, nothing broken),
--vector-figures (one more figure), --no-images and --min-image-px. Exit 0 = all passed.
"""
import argparse
import filecmp
import json
import os
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_links  # noqa: E402
CONVERT = os.path.join(HERE, "convert_pdf.py")
VOID = {"meta", "link", "br", "hr", "img", "input"}
results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}{(' - ' + detail) if detail and not ok else ''}")


def run(*args):
    p = subprocess.run([sys.executable, CONVERT, *args], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


class Balance(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.errors, self.hrefs, self.ids = [], [], [], set()

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "id" in d:
            self.ids.add(d["id"])
        if tag == "a" and d.get("href"):
            self.hrefs.append(d["href"])
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unexpected </{tag}> (open: {self.stack[-1:] })")
        else:
            self.stack.pop()


def tree(d):
    return sorted(os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/") for r, _, fs in os.walk(d) for f in fs)


def valid_image(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            im.load()
            return im.size[0] > 0 and im.size[1] > 0
    except Exception:  # noqa: BLE001
        return False


def build(pdf, topics, out, fmt, *extra):
    rc, so, se = run("build", pdf, "--topics", topics, "--out", out, "--format", fmt, "--title", "Selftest", *extra)
    return rc, (json.loads(so) if so.strip().startswith("{") else {}), se


def check_images(d, fmt, topic_files, expect_total, expect_unique):
    """Images in output dir d: files exist and are valid, manifest lists them, pages reference them."""
    manifest = json.load(open(os.path.join(d, "manifest.json")))
    imgs = [f for f in manifest["files"] if f["kind"] == "image"]
    check(f"{fmt}: manifest lists {expect_unique} unique image files", len(imgs) == expect_unique, str(len(imgs)))
    for f in imgs:
        path = os.path.join(d, f["file"])
        check(f"{fmt}: image exists and opens: {f['file']}", os.path.isfile(path) and valid_image(path))
        check(f"{fmt}: image name is stable (topic-p##-##): {f['file']}",
              bool(re.fullmatch(r"images/\d\d-[a-z0-9-]+-p\d\d-\d\d\.(png|jpg)", f["file"])))
    on_disk = {t for t in tree(d) if t.startswith("images/")}
    check(f"{fmt}: images/ holds exactly the manifest images", on_disk == {f["file"] for f in imgs})
    refs = []
    for tf in topic_files:
        t = open(os.path.join(d, tf), encoding="utf-8").read()
        if fmt == "agent-md":
            refs += re.findall(r"^!\[([^\]]+)\]\((images/[^)]+)\)$", t, re.M)
        else:
            figs = re.findall(r'<figure><img src="(images/[^"]+)" alt="([^"]+)" loading="lazy"><figcaption>(.+?)</figcaption></figure>', t)
            check(f"{fmt}: {tf} figures have a non-empty figcaption", all(c.strip() for _, _, c in figs))
            refs += [(alt, src) for src, alt, _ in figs]
    check(f"{fmt}: {expect_total} image references in pages", len(refs) == expect_total, str(len(refs)))
    check(f"{fmt}: every reference has alt text and points to an existing file",
          all(alt.strip() and os.path.isfile(os.path.join(d, src)) for alt, src in refs))
    check(f"{fmt}: every manifest image is referenced", {src for _, src in refs} == {f["file"] for f in imgs})
    return refs


def extra_cases(work, topics_for):
    """No-image PDF, --no-images, --vector-figures, --min-image-px (only for the bundled sample)."""
    ex = os.path.join(HERE, "..", "examples")
    noimg = os.path.join(ex, "sample-no-images.pdf")
    t = topics_for(noimg, "noimg")
    for fmt in ("agent-md", "html"):
        rc, rep, se = build(noimg, t, os.path.join(work, f"noimg-{fmt}"), fmt)
        check(f"no-image PDF ({fmt}): PASS and zero images", rc == 0 and rep.get("images", {}).get("placed") == 0, se or str(rep.get("images")))
        d = rep.get("output_dir", "")
        check(f"no-image PDF ({fmt}): no images/ folder and no image entries", not os.path.exists(os.path.join(d, "images"))
              and not [f for f in json.load(open(os.path.join(d, "manifest.json")))["files"] if f["kind"] == "image"])
        pages = "".join(open(os.path.join(d, f), encoding="utf-8").read() for f in os.listdir(d) if f[:2].isdigit())
        check(f"no-image PDF ({fmt}): no image references or 'not extracted' markers", "![" not in pages and "<img" not in pages and "not extracted" not in pages)
    sample = os.path.join(ex, "sample-handbook.pdf")
    t = topics_for(sample, "sample")
    rc, rep, se = build(sample, t, os.path.join(work, "vec"), "agent-md", "--vector-figures")
    check("--vector-figures adds the drawn chart (4 placed, 3 unique files)", rep.get("images", {}).get("placed") == 4 and rep["images"]["unique_files"] == 3, str(rep.get("images")))
    if rep.get("output_dir"):
        vm = json.load(open(os.path.join(rep["output_dir"], "manifest.json")))
        check("--vector-figures: the vector figure is a rendered PNG with its Figure 2 caption",
              any(f.get("extracted_as") == "vector" and f["alt"].startswith("Figure 2") for f in vm["files"] if f["kind"] == "image"))
    rc, rep, se = build(sample, t, os.path.join(work, "noext"), "html", "--no-images")
    od = rep.get("output_dir", "")
    pages = "".join(open(os.path.join(od, f), encoding="utf-8").read() for f in sorted(os.listdir(od)) if f[:2].isdigit()) if od else ""
    check("--no-images: nothing extracted, no images/ folder, pages say 'not extracted'",
          rc == 0 and rep["images"]["placed"] == 0 and rep["images"]["extraction_off"]
          and not os.path.exists(os.path.join(od, "images")) and "not extracted" in pages and "<img" not in pages, str(rep.get("images")))
    rc, rep, se = build(sample, t, os.path.join(work, "bigmin"), "agent-md", "--min-image-px", "280")
    check("--min-image-px 280 skips the 260 px-high photo, keeps the 300 px-high chart (2 placed)",
          rep.get("images", {}).get("placed") == 2 and rep["images"]["unique_files"] == 1, str(rep.get("images")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", nargs="?")
    ap.add_argument("--work")
    ap.add_argument("--expect-images", type=int, help="expected number of image references per format (default: 3 for the bundled sample)")
    a = ap.parse_args()
    bundled = a.pdf is None
    if bundled:
        a.pdf = os.path.join(HERE, "..", "examples", "sample-handbook.pdf")
    work = a.work or tempfile.mkdtemp(prefix="cpfa-")
    rc, so, se = run("plan", a.pdf, "--work", os.path.join(work, "work"))
    check("plan runs", rc == 0, se)
    plan = json.loads(so)
    if plan["structure"] != "strong":
        print("NOTE: weak structure; supply a topics file to test build. Stopping.")
        return 1
    topics = plan["topics_file"]
    for fmt in ("agent-md", "html"):
        outs = []
        for run_no in (1, 2):
            rc, rep, se = build(a.pdf, topics, os.path.join(work, f"{fmt}-{run_no}"), fmt)
            check(f"{fmt} build #{run_no} status PASS", rc == 0 and rep.get("status") == "PASS", se or str(rep))
            outs.append(rep.get("output_dir"))
        d = outs[0]
        if not d or not os.path.isdir(d):
            continue
        files = tree(d)
        manifest = json.load(open(os.path.join(d, "manifest.json")))
        check(f"{fmt}: manifest lists every file", {f["file"] for f in manifest["files"]} | {"manifest.json"} == set(files))
        same = files == tree(outs[1]) and all(filecmp.cmp(os.path.join(d, f), os.path.join(outs[1], f), shallow=False)
                                              for f in files if f != "validation.json")
        check(f"{fmt}: deterministic (two builds identical)", same)
        topic_files = [f["file"] for f in manifest["files"] if f["kind"] == "topic"]
        n_img = a.expect_images if a.expect_images is not None else (3 if bundled else None)
        if n_img is not None:
            uniq = 2 if bundled else n_img
            check_images(d, fmt, topic_files, n_img, uniq)
        if fmt == "agent-md":
            for tf in topic_files:
                t = open(os.path.join(d, tf), encoding="utf-8").read()
                fm = re.match(r"^---\n(.*?)\n---\n", t, re.S)
                keys = set(re.findall(r"^(\w+):", fm.group(1), re.M)) if fm else set()
                need = {"title", "source_file", "page_start", "page_end", "summary", "topic_id", "previous", "next"}
                check(f"agent-md: {tf} front matter", need <= keys, f"missing {need - keys}")
                check(f"agent-md: {tf} has one H1", len(re.findall(r"^# ", t, re.M)) == 1)
            idx = open(os.path.join(d, "index.md"), encoding="utf-8").read()
            check("agent-md: index links every topic with a description",
                  all(re.search(rf"\]\({re.escape(tf)}\) \(PDF pages? [\d-]+\): \S", idx) for tf in topic_files))
            tables = sum(len(re.findall(r"^\|---", open(os.path.join(d, f), encoding="utf-8").read(), re.M)) for f in topic_files)
            check("agent-md: tables preserved", tables == manifest.get("tables", tables) or tables >= 1)
            chunks = [json.loads(l) for l in open(os.path.join(d, "chunks.jsonl"), encoding="utf-8")]
            check("agent-md: chunks.jsonl valid and non-empty", bool(chunks) and all({"chunk_id", "text", "page_start"} <= set(c) for c in chunks))
            links = [m for f in topic_files + ["index.md"] for m in re.findall(r"\]\(([^)#:]+\.(?:md|pdf))\)", open(os.path.join(d, f), encoding="utf-8").read())]
        else:
            links, ntables = [], 0
            for hf in topic_files + ["index.html", "validation.html"]:
                t = open(os.path.join(d, hf), encoding="utf-8").read()
                b = Balance()
                b.feed(t)
                check(f"html: {hf} tags balanced", not b.errors and not b.stack, f"{b.errors[:2]} open={b.stack}")
                check(f"html: {hf} semantic landmarks", all(x in t for x in ("<nav", "<main", "<h1", 'lang="en-CA"')))
                check(f"html: {hf} has no raw markdown", not re.search(r"^\s*#{1,6} |\]\(", re.sub(r"<[^>]+>", "", t), re.M))
                ntables += t.count("<table>")
                links += [h for h in b.hrefs if not re.match(r"^(#|https?:|mailto:)", h)]
            check("html: tables rendered as <table>", ntables == manifest.get("tables", ntables) or ntables >= 1)
            css = open(os.path.join(d, "style.css"), encoding="utf-8").read()
            check("html: style.css carries the B.C. Design System tokens and BC Sans stack",
                  all(x in css for x in ("--blue:#013366", "--gold:#FCBA19", '"BC Sans","Noto Sans",Verdana,Arial,sans-serif', "--focus:#2E5DD7")))
            allhtml = "".join(open(os.path.join(d, hf), encoding="utf-8").read() for hf in topic_files + ["index.html"])
            check("html: header, subheader, footer, skip link and breadcrumb present",
                  all(x in allhtml for x in ('<header class="bc">', 'class="subheader"', '<footer class="bc">', 'class="skip"', 'aria-label="Breadcrumb"', 'aria-current="page"')))
        lc = check_links.check_output(d)
        check(f"{fmt}: check_links.py passes (files, anchors, PDF pages, one h1, no skipped levels)", lc["ok"], str(lc["broken"][:2] + lc["heading_problems"][:2]))
        check(f"{fmt}: validation.json records the link check", json.load(open(os.path.join(d, "validation.json")))["link_check"]["status"] == "PASS")
        missing = [l for l in links if not os.path.exists(os.path.join(d, l.split("#")[0].replace("%20", " ")))]
        check(f"{fmt}: all relative links resolve", not missing, str(missing[:3]))
    # the checker itself must fail on a broken link, a missing anchor and a skipped heading level
    bad = os.path.join(work, "bad-links")
    os.makedirs(bad, exist_ok=True)
    with open(os.path.join(bad, "a.html"), "w", encoding="utf-8") as f:
        f.write('<h1 id="x">T</h1><h3>skip</h3><a href="nope.html">x</a><img src="images/nope.png"><a href="#zzz">z</a>')
    lcb = check_links.check_output(bad)
    check("check_links flags broken file, image, anchor and heading skip",
          not lcb["ok"] and len(lcb["broken"]) == 3 and len(lcb["heading_problems"]) == 1, str(lcb))
    if bundled:
        def topics_for(pdf, tag):
            rc, so, se = run("plan", pdf, "--work", os.path.join(work, "work-" + tag))
            return json.loads(so)["topics_file"]
        extra_cases(work, topics_for)
    ok = all(results)
    print(f"\n{sum(results)}/{len(results)} checks passed. Output kept in {work}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
