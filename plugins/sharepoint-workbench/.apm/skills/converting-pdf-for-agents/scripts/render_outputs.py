#!/usr/bin/env python3
"""render_outputs.py: deterministic writers for the two output formats of converting-pdf-for-agents.

Imported by convert_pdf.py (not run directly). Standard library only.

  agent-md : topic pages with YAML front matter (source, title, page range, summary, keywords, neighbours),
             one stable H1 per page, an index with descriptions and links, and chunks.jsonl for retrieval.
  html     : a small semantic HTML5 site (index.html + one page per topic + style.css) with a sidebar table of
             contents, breadcrumbs, previous/next links, styled tables and print/dark-mode CSS.

Every function is a pure function of its inputs: no clocks, no randomness, no network. Same PDF and topics file
give byte-identical output.
"""
import html as _html
import json
import os
import re
from collections import Counter
from urllib.parse import quote

STOP = set("""a about above after again all also an and any are as at be because been before being below between both but by
can could did do does doing down during each few for from further had has have having he her here hers him his how i if in
into is it its itself just me more most my no nor not now of off on once only or other our out over own same she should so
some such than that the their them then there these they this those through to too under until up very was we were what
when where which while who whom why will with would you your page pages see per may must shall""".split())


# ----------------------------------------------------------------------------- shared helpers
def yq(value):
    """YAML-safe scalar: JSON strings and numbers are valid YAML."""
    return json.dumps(value, ensure_ascii=False)


def topic_id(entry):
    return os.path.splitext(entry["file"])[0]


def page_range(e):
    return str(e["start_page"]) if e["start_page"] == e["end_page"] else f"{e['start_page']}-{e['end_page']}"


def pages_label(e):
    return f"PDF page {e['start_page']}" if e["start_page"] == e["end_page"] else f"PDF pages {e['start_page']}-{e['end_page']}"


LISTISH = re.compile(r"^([•▪●◦·\-–*]|\d{1,2}[.)]|[a-z][.)])\s+")


def plain_text(seg):
    """Prose of a topic (no headings, list items, tables, markers), used for summary and keywords."""
    return " ".join(l["text"] for l in seg if not l.get("synthetic") and not l.get("level") and not l.get("toc_title")
                    and not LISTISH.match(l["text"]))


def summarize(e, limit=280):
    """First sentences of the topic's own prose, at most `limit` characters; tables and lists as fallbacks."""
    text = re.sub(r"\s+", " ", plain_text(e["seg"])).strip()
    if not text:
        tab = next((l for l in e["seg"] if l.get("table")), None)
        if tab:
            return f"Table with columns: {', '.join(c for c in tab['rows'][0] if c)}."[:limit]
        items = [LISTISH.sub("", l["text"]) for l in e["seg"] if not l.get("synthetic") and LISTISH.match(l["text"])]
        return ("; ".join(items[:3]) or e["title"])[:limit]
    out = ""
    for sent in re.split(r"(?<=[a-z)\"'][.!?])\s+(?=[A-Z])", text):
        if out and len(out) + len(sent) + 1 > limit:
            break
        out = f"{out} {sent}".strip()
        if len(out) >= 120:
            break
    if len(out) > limit:
        out = out[:limit].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return out


def keywords(e, k=8):
    words = re.findall(r"[a-zA-Z][a-zA-Z\-]{3,}", plain_text(e["seg"]) + " " + e["title"])
    counts = Counter(w.lower() for w in words if w.lower() not in STOP)
    return [w for w, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:k]]


def pdf_link(pdf_name, page):
    return f"{quote(pdf_name)}#page={page}"


# ----------------------------------------------------------------------------- agent-optimized Markdown
def write_agent_md_pages(stage, pages_list, title, pdf_name, n_pages, body_to_md):
    total = len(pages_list)
    for k, e in enumerate(pages_list):
        prev_e = pages_list[k - 1] if k else None
        next_e = pages_list[k + 1] if k < total - 1 else None
        body = body_to_md(e["seg"], e["title"], e["level"], pdf_name)
        e["body_md"], e["summary"], e["keywords"] = body, summarize(e), keywords(e)
        par = e["parent"]["title"] if e.get("parent") else None
        fm = ["---",
              "type: pdf-topic",
              f"topic_id: {yq(topic_id(e))}",
              f"title: {yq(e['title'])}",
              f"source_file: {yq(pdf_name)}",
              f"source_title: {yq(title)}",
              f"page_start: {e['start_page']}",
              f"page_end: {e['end_page']}",
              f"topic_number: {k + 1}",
              f"topic_count: {total}",
              f"parent_topic: {yq(par)}",
              f"previous: {yq(prev_e['file'] if prev_e else None)}",
              f"next: {yq(next_e['file'] if next_e else None)}",
              f"summary: {yq(e['summary'])}",
              f"keywords: {yq(e['keywords'])}",
              f"tables: {e['tables']}",
              "images: " + json.dumps([{"file": r["file"], "page": r["page"], "alt": r["alt"]} for r in e["image_list"]],
                                      ensure_ascii=False),
              f"images_not_extracted: {e['images_missing']}",
              f"topic_source: {yq(e['source'])}",
              "---"]
        nav = ["[Index](index.md)"]
        if prev_e:
            nav.insert(0, f"[Previous: {prev_e['title']}]({prev_e['file']})")
        if next_e:
            nav.append(f"[Next: {next_e['title']}]({next_e['file']})")
        head = (f"# {e['title']}\n\n"
                f"> **Source:** {pdf_name}, {pages_label(e)} · Topic {k + 1} of {total}\n"
                f"> **Summary:** {e['summary']}\n\n")
        with open(os.path.join(stage, e["file"]), "w", encoding="utf-8") as f:
            f.write("\n".join(fm) + "\n\n" + head + body + "\n---\n" + " | ".join(nav) + "\n")


IMG_MD = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")


def chunk_body(body, max_chars=1800):
    """Split a topic body at headings first, then at paragraph/list/table boundaries, never inside a table."""
    sections, cur, path = [], [], []
    for block in re.split(r"\n{2,}", body.strip()):
        m = re.match(r"^(#{2,6}) (.*)", block)
        if m:
            if cur:
                sections.append((list(path), cur))
            level = len(m.group(1))
            path = path[:level - 2] + [m.group(2).strip()]
            cur = [block]
        else:
            cur.append(block)
    if cur:
        sections.append((list(path), cur))
    chunks = []
    for hp, blocks in sections:
        buf = ""
        for b in blocks:
            if buf and len(buf) + len(b) + 2 > max_chars:
                chunks.append((hp, buf))
                buf = ""
            buf = f"{buf}\n\n{b}" if buf else b
        if buf:
            chunks.append((hp, buf))
    return chunks


def write_agent_md_index(stage, entries, pages_list, title, pdf_name, n_pages, status, notes):
    first = pages_list[0]["summary"] if pages_list else title
    fm = ["---", "type: pdf-index", f"title: {yq(title)}", f"source_file: {yq(pdf_name)}",
          f"source_pages: {n_pages}", f"topic_count: {len(pages_list)}",
          f"summary: {yq(first)}", f"conversion_status: {yq(status)}",
          'chunks_file: "chunks.jsonl"', "---"]
    out = ["\n".join(fm), "", f"# {title}", "",
           f"> Converted from {pdf_name} ({n_pages} pages) into {len(pages_list)} topic pages. "
           "Page text is copied from the PDF unchanged.", "",
           "## How to use this knowledge", "",
           "- Read this index first; each entry has a one-line description and a link.",
           "- Every topic file starts with YAML front matter (`topic_id`, `page_start`, `page_end`, `summary`, "
           "`keywords`, `previous`, `next`). Cite as `source_file` + page range.",
           "- `chunks.jsonl` holds the same text split into retrieval-sized chunks with their heading path and pages.",
           "- Tables are kept as Markdown pipe tables. Images are extracted to `images/` and embedded with alt text; "
           "pictures that could not be extracted are marked in the page.", "",
           "## Topics", ""]
    for e in entries:
        pad = "  " * (max(e["level"], 1) - 1)
        if e["group"]:
            out.append(f"{pad}- **{e['title']}** (group, {pages_label(e)})")
        else:
            out.append(f"{pad}- [{e['title']}]({e['file']}) ({pages_label(e)}): {e['summary']}")
    if any(e["source"] == "ai" for e in entries):
        out += ["", "> Some topic boundaries were proposed by AI and confirmed by a person."]
    if notes:
        out += ["", "## Not converted", ""] + [f"- {x}" for x in notes]
    out += ["", f"Conversion check: **{status}** (see [validation.md](validation.md))."]
    with open(os.path.join(stage, "index.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    with open(os.path.join(stage, "chunks.jsonl"), "w", encoding="utf-8") as f:
        for e in pages_list:
            for i, (hp, text) in enumerate(chunk_body(e["body_md"]), 1):
                rec = {"chunk_id": f"{topic_id(e)}#c{i:02d}", "topic_id": topic_id(e), "title": e["title"],
                       "heading_path": [e["title"]] + hp, "source_file": pdf_name,
                       "page_start": e["start_page"], "page_end": e["end_page"], "file": e["file"],
                       "images": [{"file": m.group(2), "alt": m.group(1)} for m in IMG_MD.finditer(text)], "text": text}
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ----------------------------------------------------------------------------- Markdown subset -> HTML
def inline(text):
    t = _html.escape(text, quote=False)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{_html.escape(_html.unescape(m.group(2)), quote=True)}">{m.group(1)}</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", t)
    return t.replace("\\|", "|")


def slug(text, seen):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"
    base, n = s, 2
    while s in seen:
        s, n = f"{base}-{n}", n + 1
    seen.add(s)
    return s


LIST_RE = re.compile(r"^(\s*)(-|\d{1,2}[.)]|[a-z][.)])\s+(.*)$")


def md_to_html(md):
    """Convert the Markdown subset convert_pdf.py writes. Returns (html, headings[(level, id, text)])."""
    out, heads, seen = [], [], {"main"}   # "main" is the skip-link target id
    lines = md.split("\n")
    i, para, stack = 0, [], []        # stack of (indent, closing tag)

    def flush_para():
        nonlocal para
        if para:
            text = " ".join(para)
            cls = ' class="source"' if text.startswith("*Source:") else ""
            out.append(f"<p{cls}>{inline(text)}</p>")
        para = []

    def close_lists(to=0):
        while len(stack) > to:
            out.append(stack.pop()[1])

    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            flush_para()
            close_lists()
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            flush_para()
            close_lists()
            lv, text = len(m.group(1)), m.group(2).strip()
            hid = slug(text, seen)
            heads.append((lv, hid, text))
            out.append(f'<h{lv} id="{hid}">{inline(text)}</h{lv}>')
            i += 1
            continue
        if ln.lstrip().startswith("|"):
            flush_para()
            close_lists()
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                cells = re.split(r"(?<!\\)\|", lines[i].strip())[1:-1]
                rows.append([c.strip() for c in cells])
                i += 1
            rows = [r for r in rows if not all(re.fullmatch(r":?-{3,}:?", c or "---") for c in r)]
            th = "".join(f'<th scope="col">{inline(c)}</th>' for c in rows[0])
            tb = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
            out.append(f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>')
            continue
        im = IMG_MD.match(ln.strip())
        if im and ln.strip().startswith("!["):
            flush_para()
            close_lists()
            alt, src = im.group(1), im.group(2)
            i += 1
            cap = []
            while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(("![", "#", "|")):
                cap.append(lines[i].strip())
                i += 1
            text = " ".join(cap)
            text = re.sub(r"^\*(.*)\*$", r"\1", text) if text else alt
            out.append(f'<figure><img src="{_html.escape(src, quote=True)}" alt="{_html.escape(alt, quote=True)}" '
                       f'loading="lazy"><figcaption>{inline(text)}</figcaption></figure>')
            continue
        if ln.strip() == "---":
            flush_para()
            close_lists()
            i += 1
            continue
        m = LIST_RE.match(ln)
        if m:
            flush_para()
            indent, marker, text = len(m.group(1)), m.group(2), m.group(3)
            while stack and stack[-1][0] > indent:
                out.append(stack.pop()[1])
            if not stack or stack[-1][0] < indent:
                if marker == "-":
                    out.append("<ul>")
                    stack.append((indent, "</ul>"))
                else:
                    kind = 'type="a" ' if marker[0].isalpha() else ""
                    start = f'start="{marker[:-1]}" ' if marker[0].isdigit() and marker[:-1] != "1" else ""
                    out.append(f"<ol {kind}{start}>".replace(" >", ">"))
                    stack.append((indent, "</ol>"))
            out.append(f"<li>{inline(text)}</li>")
            i += 1
            continue
        close_lists()
        para.append(ln.strip())
        i += 1
    flush_para()
    close_lists()
    return "\n".join(out), heads


# ----------------------------------------------------------------------------- HTML site (B.C. Design System)
# Look and feel: B.C. Design System (design tokens v5.1.0, component library 0.9.0 as of Nov 2026).
# Tokens live in ../assets/bc_tokens.css (the one place to update); component styles in ../assets/bc_components.css.
# The generated style.css is tokens + components, so a built site is self-contained and works offline.
_HERE = os.path.dirname(os.path.abspath(__file__))
# header logo (used when a shared design system supplies one at publish time)
LOGO_CSS = ("\n/* shared-manual additions */\n"
            "header.bc .bc-logo{height:2.5rem;width:auto;margin-right:1rem;vertical-align:middle}\n"
            "header.bc .in{display:flex;align-items:center;flex-wrap:wrap;gap:.5rem}\n"
            "header.bc .org{margin-left:auto}\n")
SITE = {"org": "", "date": ""}      # optional header/footer text, set with configure()


def configure(org="", date=""):
    SITE["org"], SITE["date"] = org or "", date or ""


def _read_asset(name):
    for d in (os.path.join(_HERE, "..", "assets"), os.path.join(_HERE, "assets"), _HERE):
        path = os.path.join(d, name)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                return f.read()
    raise SystemExit(f"ERROR: {name} not found next to the scripts (looked in ../assets, ./assets and ./). "
                     "Copy the skill's assets/ folder together with scripts/.")


def build_css():
    return _read_asset("bc_tokens.css").rstrip() + "\n" + _read_asset("bc_components.css")


def _nav_groups(entries):
    """Accordion sections: each top-level entry with the entries below it (a group heading has no page of its own)."""
    sections, top = [], min((e["level"] for e in entries), default=1)
    for e in entries:
        if not sections or e["level"] <= top:
            sections.append((e, []))
        else:
            sections[-1][1].append(e)
    return sections


def _link(e, current):
    cur = ' aria-current="page"' if e["file"] == current else ""
    lv = min(max(e["level"], 1), 4)
    cls = f' class="l{lv}"' if lv >= 3 else ""
    return f'<a href="{e["file"]}"{cls}{cur}>{_html.escape(e["title"])}</a>'


def _sidebar(title, entries, current):
    cur = ' aria-current="page"' if current == "index.html" else ""
    parts = [f'<a href="index.html"{cur}>Home</a>']
    for head, kids in _nav_groups(entries):
        if not kids and not head["group"]:
            parts.append(_link(head, current))
            continue
        files = {k["file"] for k in kids if not k["group"]} | ({head["file"]} if not head["group"] else set())
        op = " open" if current in files else ""
        inner = "" if head["group"] else _link(head, current)
        inner += "".join(_link(k, current) if not k["group"] else
                         f'<span class="meta" style="display:block;padding:.35rem .5rem">{_html.escape(k["title"])}</span>' for k in kids)
        parts.append(f'<details{op}><summary>{_html.escape(head["title"])}</summary>{inner}</details>')
    return f'<nav class="toc" aria-label="Contents">{"".join(parts)}</nav>'


def _shell(doc_title, page_title, sidebar, main, pdf_name, description="", crumbs=""):
    desc = f'<meta name="description" content="{_html.escape(description, quote=True)}">' if description else ""
    org = f'<span class="org">{_html.escape(SITE["org"])}</span>' if SITE["org"] else ""
    when = f" ({_html.escape(SITE['date'])})" if SITE["date"] else ""
    foot_org = f"{_html.escape(SITE['org'])}. " if SITE["org"] else ""
    return (f'<!DOCTYPE html>\n<html lang="en-CA">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">\n{desc}\n'
            f'<title>{_html.escape(page_title)} - {_html.escape(doc_title)}</title>\n'
            f'<link rel="stylesheet" href="style.css">\n</head>\n<body>\n'
            f'<a class="skip" href="#main">Skip to main content</a>\n'
            f'<header class="bc"><div class="in"><a href="index.html">{_html.escape(doc_title)}</a>{org}</div></header>\n'
            f'<div class="subheader"><div class="in"><a href="index.html">Home</a>'
            f'<a href="{quote(pdf_name)}">Original PDF</a></div></div>\n'
            f'<div class="layout">\n{sidebar}\n<main id="main">\n{crumbs}\n{main}\n</main>\n</div>\n'
            f'<footer class="bc"><div class="in">{foot_org}{_html.escape(doc_title)}{when}. '
            f'The PDF is the source of record.</div></footer>\n'
            f'</body>\n</html>\n')


def _crumbs(title, trail, last):
    items = [f'<li><a href="index.html">Home</a></li>'] + [f"<li>{t}</li>" for t in trail]
    items.append(f'<li aria-current="page">{_html.escape(last)}</li>')
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(items)}</ol></nav>'


def write_html_pages(stage, entries, pages_list, title, pdf_name, n_pages, body_to_md):
    with open(os.path.join(stage, "style.css"), "w", encoding="utf-8") as f:
        f.write(build_css())
    total = len(pages_list)
    for k, e in enumerate(pages_list):
        prev_e = pages_list[k - 1] if k else None
        next_e = pages_list[k + 1] if k < total - 1 else None
        e["body_md"], e["summary"] = body_to_md(e["seg"], e["title"], e["level"], pdf_name), summarize(e)
        body_html, heads = md_to_html(e["body_md"])
        trail = []
        if e.get("parent"):
            par = e["parent"]
            trail.append(_html.escape(par["title"]) if par["group"] else
                         f'<a href="{par["file"]}">{_html.escape(par["title"])}</a>')
        tags = [f'<span class="tag">{pages_label(e)}</span>', f'<span class="tag">Topic {k + 1} of {total}</span>']
        if e["tables"]:
            tags.append(f'<span class="tag">{e["tables"]} table{"s" if e["tables"] != 1 else ""}</span>')
        if e["images"]:
            tags.append(f'<span class="tag">{e["images"]} figure{"s" if e["images"] != 1 else ""}</span>')
        if e["images_missing"]:
            tags.append('<span class="tag bad">some images not extracted</span>')
        sub = [h for h in heads if h[0] in (2, 3)]
        toc = ""
        if len(sub) >= 3:
            toc = ('<nav class="onpage" aria-label="On this page"><strong>On this page</strong><ul>' +
                   "".join(f'<li><a href="#{hid}">{_html.escape(t)}</a></li>' for _, hid, t in sub) + "</ul></nav>")
        pager = '<nav class="pn" aria-label="Previous and next topic">'
        pager += (f'<a class="btn sec" href="{prev_e["file"]}" rel="prev">&larr; {_html.escape(prev_e["title"])}</a>' if prev_e else "<span></span>")
        pager += (f'<a class="btn" href="{next_e["file"]}" rel="next">{_html.escape(next_e["title"])} &rarr;</a>' if next_e else "<span></span>")
        pager += "</nav>"
        main = (f'<article>\n<h1>{_html.escape(e["title"])}</h1>\n'
                f'<p class="meta">{"".join(tags)}</p>\n<div class="callout">{_html.escape(e["summary"])}</div>\n'
                f'{toc}\n{body_html}\n</article>\n{pager}\n'
                f'<p class="source">Source: <a href="{pdf_link(pdf_name, e["start_page"])}">{_html.escape(pdf_name)}</a>, '
                f'{pages_label(e)}.</p>')
        with open(os.path.join(stage, e["file"]), "w", encoding="utf-8") as f:
            f.write(_shell(title, e["title"], _sidebar(title, entries, e["file"]), main, pdf_name, e["summary"],
                           _crumbs(title, trail, e["title"])))


def write_html_index(stage, entries, pages_list, title, pdf_name, n_pages, status, notes, args):
    cards = "".join(
        f'<li class="card"><a href="{e["file"]}">{_html.escape(e["title"])}</a>'
        f'<p>{_html.escape(e["summary"])}</p><p class="meta">{pages_label(e)}</p></li>'
        for e in pages_list)
    tables = sum(e["tables"] for e in pages_list)
    figs = sum(e["images"] for e in pages_list)
    tags = (f'<span class="tag">{n_pages} PDF pages</span><span class="tag">{len(pages_list)} topics</span>'
            f'<span class="tag">{tables} tables</span><span class="tag">{figs} figures</span>')
    ai = ('<div class="callout warn">Some topic boundaries were proposed by AI and confirmed by a person.</div>'
          if any(e["source"] == "ai" for e in entries) else "")
    first = (f'<a class="btn" href="{pages_list[0]["file"]}">Start reading</a> ' if pages_list else "")
    main = (f'<article>\n<h1>{_html.escape(title)}</h1>\n<p class="meta">{tags}</p>\n'
            f'<p>Browse the topics below or <a href="{pdf_link(pdf_name, 1)}">open the original PDF</a>.</p>\n{ai}\n'
            f'<p>{first}<a class="btn sec" href="{quote(pdf_name)}">Open the original PDF</a></p>\n<h2>Topics</h2>\n'
            f'<ul class="grid">{cards}</ul>\n</article>')
    desc = pages_list[0]["summary"] if pages_list else title
    with open(os.path.join(stage, "index.html"), "w", encoding="utf-8") as f:
        f.write(_shell(title, "Contents", _sidebar(title, entries, "index.html"), main, pdf_name, desc))


def write_html_validation(stage, title, entries, pages_list, val_md, pdf_name):
    """Render the validation report as HTML. Rewritten on every emit, so it can carry the final status."""
    with open(os.path.join(stage, "style.css"), "w", encoding="utf-8") as f:
        f.write(build_css())
    body, _ = md_to_html(val_md)
    main = f'<article>\n{body}\n</article>'
    with open(os.path.join(stage, "validation.html"), "w", encoding="utf-8") as f:
        f.write(_shell(title, "Conversion report", _sidebar(title, entries, "validation.html"), main, pdf_name,
                       crumbs=_crumbs(title, [], "Conversion report")))
