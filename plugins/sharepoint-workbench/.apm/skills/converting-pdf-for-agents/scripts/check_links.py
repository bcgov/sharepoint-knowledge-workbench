#!/usr/bin/env python3
"""check_links.py: mandatory link + heading check for a generated output folder (agent-md, html, markdown-basic).

Usage: python check_links.py <output_folder> [--no-pdf-copy] [--json]   (exit 0 = clean, 1 = problems)
Also imported by convert_pdf.py (build fails when problems are found) and build_html_fallback.py.
Standard library only. Checks, over every .html and .md file in the folder (recursively):
  1. every href / src (HTML) and every [text](target) / ![alt](target) (Markdown, outside code) that is not
     http(s)/mailto/data resolves: the file named by the path part exists (percent-decoding applied);
  2. every #anchor: the target file (or the same page) has that id (HTML id= / name=) or heading slug (Markdown);
     `file.pdf#page=N` is not an anchor: the PDF must exist and N must be within 1..page count when `pdf_pages` is given;
  3. each page has exactly one h1 (Markdown: one `# ` after the front matter) and no skipped heading levels;
  4. chunks.jsonl: every images[].file exists; manifest.json: every listed file exists; front matter
     previous / next / images[].file in Markdown topic pages point at existing files.
With pdf_copied=False, links to a missing PDF are warnings (the PDF must then be placed beside the pages), not errors.
"""
import json
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote

SKIP = re.compile(r"^(https?:|mailto:|tel:|data:|javascript:)", re.I)


class _Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.heads = [], set(), []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        for k in ("id", "name"):
            if d.get(k):
                self.ids.add(d[k])
        for k in ("href", "src"):
            if d.get(k):
                self.links.append(d[k])
        if re.fullmatch(r"h[1-6]", tag):
            self.heads.append(int(tag[1]))


def md_slug(text):
    t = re.sub(r"[`*_\[\]()]", "", text.strip().lower())
    t = re.sub(r"[^\w\s-]", "", t)
    return re.sub(r"\s", "-", t)


def _strip_md(text):
    """Return (front_matter_text, body) with fenced and inline code removed from the body."""
    fm = ""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if m:
        fm, text = m.group(1), text[m.end():]
    text = re.sub(r"^(```|~~~).*?^\1.*?$", "", text, flags=re.S | re.M)
    text = re.sub(r"`[^`\n]*`", "", text)
    return fm, text


def _fm_links(fm):
    out = []
    for key in ("previous", "next"):
        m = re.search(rf'^{key}:\s*"([^"]+)"', fm, re.M)
        if m:
            out.append(m.group(1))
    m = re.search(r"^images:\s*(\[.*\])\s*$", fm, re.M)
    if m:
        try:
            out += [i["file"] for i in json.loads(m.group(1))]
        except (ValueError, KeyError, TypeError):
            pass
    return out


def check_output(folder, pdf_copied=True, pdf_pages=None):
    """Return {"ok", "files", "links", "broken": [...], "heading_problems": [...], "warnings": [...]}."""
    broken, hprob, warns = [], [], []
    pages = {}          # relpath -> {"ids": set, "links": [...], "heads": [...]}
    for root, _, files in os.walk(folder):
        for fn in sorted(files):
            rel = os.path.relpath(os.path.join(root, fn), folder).replace(os.sep, "/")
            path = os.path.join(root, fn)
            if fn.endswith(".html"):
                p = _Page()
                with open(path, encoding="utf-8") as f:
                    p.feed(f.read())
                pages[rel] = {"ids": p.ids, "links": p.links, "heads": p.heads}
            elif fn.endswith(".md"):
                with open(path, encoding="utf-8") as f:
                    fm, body = _strip_md(f.read())
                heads = [len(m.group(1)) for m in re.finditer(r"^(#{1,6})\s+\S", body, re.M)]
                ids = {md_slug(m.group(2)) for m in re.finditer(r"^(#{1,6})\s+(.*)$", body, re.M)}
                links = [m.group(1) for m in re.finditer(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", body)]
                pages[rel] = {"ids": ids, "links": links + _fm_links(fm), "heads": heads}
    nlinks = 0
    for rel, pg in sorted(pages.items()):
        base = os.path.dirname(os.path.join(folder, rel))
        hs = pg["heads"]
        if hs.count(1) != 1:
            hprob.append(f"{rel}: {hs.count(1)} h1 headings (exactly 1 required)")
        for a, b in zip(hs, hs[1:]):
            if b > a + 1:
                hprob.append(f"{rel}: heading level jumps from h{a} to h{b}")
                break
        if hs and hs[0] != 1:
            hprob.append(f"{rel}: first heading is h{hs[0]}, not h1")
        for link in pg["links"]:
            if not link or SKIP.match(link):
                continue
            nlinks += 1
            target, _, frag = link.partition("#")
            if not target:                                   # same-page anchor
                if frag and frag not in pg["ids"] and unquote(frag) not in pg["ids"]:
                    broken.append(f"{rel}: anchor #{frag} not found on the page")
                continue
            target = unquote(target)
            tpath = os.path.normpath(os.path.join(base, target))
            if not os.path.exists(tpath):
                msg = f"{rel}: link target missing: {link}"
                if target.lower().endswith(".pdf") and not pdf_copied:
                    warns.append(msg + " (PDF not copied; place it beside the pages)")
                else:
                    broken.append(msg)
                continue
            if frag and target.lower().endswith(".pdf"):
                m = re.fullmatch(r"page=(\d+)", frag)
                if frag.startswith("page=") and not (m and int(m.group(1)) >= 1 and (not pdf_pages or int(m.group(1)) <= pdf_pages)):
                    broken.append(f"{rel}: bad PDF page reference {link} (physical pages 1-{pdf_pages or '?'})")
            elif frag:
                tr = os.path.relpath(tpath, folder).replace(os.sep, "/")
                ids = pages.get(tr, {}).get("ids")
                if ids is not None and frag not in ids and unquote(frag) not in ids:
                    broken.append(f"{rel}: anchor {link} not found in {tr}")
    cj = os.path.join(folder, "chunks.jsonl")
    if os.path.exists(cj):
        with open(cj, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                rec = json.loads(line)
                for im in rec.get("images", []):
                    nlinks += 1
                    if not os.path.exists(os.path.join(folder, unquote(im["file"]))):
                        broken.append(f"chunks.jsonl line {n}: image missing: {im['file']}")
                if rec.get("file") and not os.path.exists(os.path.join(folder, rec["file"])):
                    broken.append(f"chunks.jsonl line {n}: topic file missing: {rec['file']}")
    mj = os.path.join(folder, "manifest.json")
    if os.path.exists(mj):
        with open(mj, encoding="utf-8") as f:
            for ent in json.load(f).get("files", []):
                nlinks += 1
                if not os.path.exists(os.path.join(folder, ent["file"])):
                    broken.append(f"manifest.json: listed file missing: {ent['file']}")
    return {"ok": not broken and not hprob, "files": len(pages), "links": nlinks,
            "broken": broken, "heading_problems": hprob, "warnings": warns}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    rep = check_output(args[0], pdf_copied="--no-pdf-copy" not in sys.argv)
    if "--json" in sys.argv:
        print(json.dumps(rep, indent=2))
    else:
        print(f"Link check: {'PASS' if rep['ok'] else 'FAIL'} - {rep['files']} pages, {rep['links']} links/references")
        for x in rep["broken"] + rep["heading_problems"]:
            print("  BROKEN:", x)
        for x in rep["warnings"]:
            print("  warning:", x)
    sys.exit(0 if rep["ok"] else 1)


if __name__ == "__main__":
    main()
