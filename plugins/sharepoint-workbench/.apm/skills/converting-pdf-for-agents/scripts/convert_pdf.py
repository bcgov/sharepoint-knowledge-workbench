#!/usr/bin/env python3
"""convert_pdf.py: convert a text-layer PDF into agent-optimized Markdown or a formatted HTML site, one page per topic.

Modes:
  check                         read-only probe of the libraries and folders this script needs
  plan  PDF --work DIR          extract, detect topics, write topics.xlsx (or .csv) + pages-digest.md
  build PDF --topics FILE --out DIR --format agent-md|html [--title T]
                                write the index, one page per topic, manifest.json, validation.json
                                (--format is required: the user chooses it before any build)

Deterministic path: topics come from PDF bookmarks or heading font sizes and are written to an
editable topics file. AI path: when structure is weak, the agent reads pages-digest.md and fills
the same topics file. Build always reads the topics file, so both paths produce the same output.
Images: embedded pictures are extracted into images/ (see extract_images); --vector-figures also rasterizes drawn figures.
Requires pdfplumber (with Pillow and pypdfium2, which it installs). Optional: pypdf (bookmarks), openpyxl (.xlsx; .csv is the fallback).
"""
import argparse
import csv
import json
import os
import re
import shutil
import sys
import unicodedata
from collections import Counter
from urllib.parse import quote, unquote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_links  # noqa: E402
import render_outputs  # noqa: E402  (sibling module: agent-md and html writers)

TOPIC_COLS = ["topic_no", "title", "level", "start_page", "start_heading", "source", "notes"]
BAD_NAME_CHARS = re.compile(r'[#%*:<>?/\\|"~&{}]')
BULLET = re.compile("^([•▪●◦·\\-–*]|\\d{1,2}[.)]|[a-z][.)])\\s+")


# ----------------------------------------------------------------------------- helpers
def slugify(text, limit=60):
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    t = BAD_NAME_CHARS.sub(" ", t.lower())
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return (t[:limit].strip("-")) or "topic"


def norm(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", text.lower())).strip()


def unique_dir(path):
    if not os.path.exists(path):
        return path
    n = 2
    while os.path.exists(f"{path}-{n}"):
        n += 1
    return f"{path}-{n}"


def pdf_ref(pdf_name, page):
    """Relative link to a page of the copied PDF (works in browsers and most viewers)."""
    return f"{quote(pdf_name)}#page={page}"


def pages_md(pdf_name, start, end):
    """Markdown link to the first page of a range, labelled with the whole range."""
    label = f"p. {start}" if start == end else f"pp. {start}-{end}"
    return f"[{label}]({pdf_ref(pdf_name, start)})"


def need_pdfplumber():
    try:
        import pdfplumber
        return pdfplumber
    except Exception as e:  # noqa: BLE001
        sys.exit(f"ERROR: pdfplumber is not available ({type(e).__name__}). Run: convert_pdf.py check")


# ----------------------------------------------------------------------------- extraction
def clean_cell(c):
    return re.sub(r"\s+", " ", str(c or "")).strip()


def find_tables(page):
    """Ruled tables on a page as [(bbox, rows)]; tables with fewer than 2 rows or 2 columns are ignored."""
    out = []
    try:
        for t in page.find_tables():
            rows = [[clean_cell(c) for c in r] for r in t.extract() if r and any(clean_cell(c) for c in r)]
            if len(rows) >= 2 and max(len(r) for r in rows) >= 2:
                width = max(len(r) for r in rows)
                out.append((t.bbox, [r + [""] * (width - len(r)) for r in rows]))
    except Exception:  # noqa: BLE001  (a table the library cannot parse stays as plain text lines)
        return []
    return out


def table_to_md(rows):
    """GitHub-style pipe table; the first row is the header."""
    esc = lambda c: c.replace("|", "\\|")
    out = ["| " + " | ".join(esc(c) for c in rows[0]) + " |", "|" + "---|" * len(rows[0])]
    out += ["| " + " | ".join(esc(c) for c in r) + " |" for r in rows[1:]]
    return "\n".join(out)


def chars_of(l):
    """Characters a line contributes to the coverage check: text lines, tables, and image captions."""
    if l.get("image"):
        return len(l.get("caption") or "")
    if l.get("synthetic"):
        return len(l["text"]) if l.get("table") else 0
    return len(l["text"])


# ----------------------------------------------------------------------------- images
CAPTION = re.compile(r"^(figure|fig\.?|image|chart|diagram|photo|screenshot|illustration)\s*\d+[a-z]?\s*[.:\-–—)]?\s*\S", re.I)
IMG_EXT_KEEP = {".jpg", ".jpeg"}


def _clamp(bbox, page):
    x0, t, x1, b = bbox
    return (max(0, x0), max(0, t), min(float(page.width), x1), min(float(page.height), b))


def _png_bytes(img):
    import io
    if img.mode in ("CMYK", "P", "LA", "I;16", "1"):
        img = img.convert("RGBA" if img.mode in ("P", "LA") else "RGB")
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=False)
    return buf.getvalue(), img.size


def _render_region(page, bbox, dpi):
    """Rasterize a page region (used for vector figures and as the fallback for undecodable images)."""
    crop = page.crop(_clamp(bbox, page))
    return _png_bytes(crop.to_image(resolution=dpi).original)


def _cluster(boxes, gap):
    """Merge boxes (x0, top, x1, bottom) that touch or lie within `gap` points; returns [(bbox, count)]."""
    groups = [[list(b), 1] for b in boxes]
    merged = True
    while merged:
        merged = False
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                a, b = groups[i][0], groups[j][0]
                if a[0] - gap <= b[2] and b[0] - gap <= a[2] and a[1] - gap <= b[3] and b[1] - gap <= a[3]:
                    groups[i][0] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]
                    groups[i][1] += groups[j][1]
                    del groups[j]
                    merged = True
                    break
            if merged:
                break
    return [(tuple(g[0]), g[1]) for g in groups]


def extract_images(pdf_path, n_pages, min_px=64, dpi=150, vector=False):
    """Deterministic image extraction. Returns (images, stats).

    Embedded raster images: original JPEG bytes when the PDF holds a JPEG, otherwise decoded with pdfminer and saved
    as PNG, otherwise the page region is rasterized. Images smaller than `min_px` (source pixels, either side) or
    smaller than 24 pt on the page are skipped as decorative; so is any picture that repeats on many pages (logos).
    With vector=True, drawn figures (clusters of at least 6 lines, rectangles or curves outside tables) are
    rasterized from the page region. Each image: page, top, bottom, x0, h, data (bytes), ext, sha, width, height, kind.
    """
    import hashlib
    import tempfile
    pdfplumber = need_pdfplumber()
    stats = Counter()
    found, failed_pages = [], Counter()
    with pdfplumber.open(pdf_path) as pdf, tempfile.TemporaryDirectory() as tmp:
        try:
            from pdfminer.image import ImageWriter
            from pdfminer.layout import LTImage
            writer = ImageWriter(tmp)
        except Exception:  # noqa: BLE001
            writer = None
        for pno, page in enumerate(pdf.pages, 1):
            tabs = [b for b, _ in find_tables(page)]
            page_area = float(page.width) * float(page.height)
            claimed = []
            for k, im in enumerate(page.images):
                bbox = (im["x0"], im["top"], im["x1"], im["bottom"])
                sw, sh = im.get("srcsize") or (0, 0)
                wpt, hpt = bbox[2] - bbox[0], bbox[3] - bbox[1]
                if min(sw or 0, sh or 0) < min_px or min(wpt, hpt) < 24:
                    stats["skipped_small"] += 1
                    continue
                data = ext = size = None
                kind = "embedded"
                try:
                    if writer is None:
                        raise RuntimeError("pdfminer image writer unavailable")
                    lt = LTImage(f"p{pno}i{k}", im["stream"], (im["x0"], im["y0"], im["x1"], im["y1"]))
                    fname = writer.export_image(lt)
                    path = os.path.join(tmp, fname)
                    if os.path.splitext(fname)[1].lower() in IMG_EXT_KEEP:
                        from PIL import Image
                        with open(path, "rb") as fh:
                            data = fh.read()
                        ext = ".jpg"
                        with Image.open(path) as pim:
                            size = pim.size
                    else:
                        from PIL import Image
                        with Image.open(path) as pim:
                            pim.load()
                            data, size = _png_bytes(pim)
                        ext = ".png"
                except Exception:  # noqa: BLE001  (undecodable stream: fall back to rendering the region)
                    try:
                        data, size = _render_region(page, bbox, dpi)
                        ext, kind = ".png", "rendered"
                    except Exception:  # noqa: BLE001
                        failed_pages[pno] += 1
                        stats["failed"] += 1
                        continue
                claimed.append(bbox)
                found.append({"page": pno, "top": bbox[1], "bottom": bbox[3], "x0": bbox[0], "h": float(page.height),
                              "data": data, "ext": ext, "width": size[0], "height": size[1], "kind": kind,
                              "sha": hashlib.sha256(data).hexdigest()})
            if vector:
                boxes = []
                for o in list(page.rects) + list(page.curves) + list(page.lines):
                    b = (o["x0"], o["top"], o["x1"], o["bottom"])
                    if (b[2] - b[0]) * (b[3] - b[1]) > 0.8 * page_area:
                        continue                      # page background / border
                    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
                    if any(t[0] <= cx <= t[2] and t[1] <= cy <= t[3] for t in tabs):
                        continue                      # table ruling
                    boxes.append(b)
                for bbox, count in _cluster(boxes, 8):
                    wpt, hpt = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    if count < 6 or wpt < 80 or hpt < 60:
                        continue
                    if any(c[0] < bbox[2] and bbox[0] < c[2] and c[1] < bbox[3] and bbox[1] < c[3] for c in claimed):
                        continue
                    pad = (bbox[0] - 6, bbox[1] - 6, bbox[2] + 6, bbox[3] + 6)
                    try:
                        data, size = _render_region(page, pad, dpi)
                    except Exception:  # noqa: BLE001
                        failed_pages[pno] += 1
                        stats["failed"] += 1
                        continue
                    found.append({"page": pno, "top": bbox[1], "bottom": bbox[3], "x0": bbox[0], "h": float(page.height),
                                  "data": data, "ext": ".png", "width": size[0], "height": size[1], "kind": "vector",
                                  "sha": hashlib.sha256(data).hexdigest()})
    # pictures repeated on many pages (logos, watermarks) are decoration
    pages_of = {}
    for im in found:
        pages_of.setdefault(im["sha"], set()).add(im["page"])
    limit = max(3, -(-2 * n_pages // 5))
    keep = []
    for im in found:
        if len(pages_of[im["sha"]]) >= limit:
            stats["skipped_repeated"] += 1
        else:
            keep.append(im)
    keep.sort(key=lambda im: (im["page"], im["top"], im["x0"]))
    stats["found"] = len(keep)
    return keep, stats, dict(failed_pages)


def attach_images(lines, images):
    """Insert image lines at their vertical position and take a caption from a nearby text line (consumed)."""
    by_page = {}
    for im in images:
        by_page.setdefault(im["page"], []).append(im)
    for pno, ims in by_page.items():
        page_lines = [l for l in lines if l["page"] == pno]
        rest = [l for l in lines if l["page"] != pno]
        for im in ims:
            cap = None
            for l in page_lines:
                if l.get("synthetic") or l.get("image") or not CAPTION.match(l["text"]):
                    continue
                below = 0 <= l["top"] - im["bottom"] <= 40
                above = 0 <= im["top"] - l["bottom"] <= 24
                if below or above:
                    cap = l
                    break
            caption = cap["text"] if cap else None
            if cap:
                page_lines.remove(cap)
            page_lines.append({"page": pno, "text": "", "size": 0, "bold": False, "top": im["top"], "bottom": im["bottom"],
                               "x0": im["x0"], "h": im["h"], "level": 0, "synthetic": True, "image": True,
                               "img": im, "caption": caption})
        page_lines.sort(key=lambda l: l["top"])
        lines[:] = rest + page_lines
    lines.sort(key=lambda l: l["page"])      # stable: keeps the vertical order inside each page


def extract_lines(pdf_path):
    """Return (lines, page_count, page_chars, page_images). Each line: page, text, size, bold, top, bottom, h."""
    pdfplumber = need_pdfplumber()
    lines, page_chars, page_images = [], {}, {}
    with pdfplumber.open(pdf_path) as pdf:
        n = len(pdf.pages)
        for pno, page in enumerate(pdf.pages, 1):
            words = page.extract_words(extra_attrs=["size", "fontname"], keep_blank_chars=False)
            tables = find_tables(page)
            if tables:
                words = [w for w in words if not any(
                    b[0] - 1 <= (w["x0"] + w["x1"]) / 2 <= b[2] + 1 and b[1] - 1 <= (w["top"] + w["bottom"]) / 2 <= b[3] + 1
                    for b, _ in tables)]
            rows = []
            for w in sorted(words, key=lambda w: (round(w["top"]), w["x0"])):
                if rows and abs(rows[-1][-1]["top"] - w["top"]) <= 3:
                    rows[-1].append(w)
                else:
                    rows.append([w])
            count = 0
            for row in rows:
                row.sort(key=lambda w: w["x0"])
                text = " ".join(w["text"] for w in row).strip()
                if not text:
                    continue
                size = round(max(w["size"] for w in row) * 2) / 2
                bold = sum(("bold" in w["fontname"].lower()) or ("black" in w["fontname"].lower())
                           for w in row) > len(row) / 2
                lines.append({"page": pno, "text": text, "size": size, "bold": bold,
                              "top": min(w["top"] for w in row), "bottom": max(w["bottom"] for w in row),
                              "x0": min(w["x0"] for w in row), "h": float(page.height)})
                count += len(text)
            for bbox, trows in tables:
                lines.append({"page": pno, "text": table_to_md(trows), "size": 0, "bold": False, "top": bbox[1],
                              "bottom": bbox[3], "x0": bbox[0], "h": float(page.height), "level": 0,
                              "synthetic": True, "table": True, "rows": trows})
            page_lines = [l for l in lines if l["page"] == pno]
            page_lines.sort(key=lambda l: l["top"])
            lines[:] = [l for l in lines if l["page"] != pno] + page_lines
            page_chars[pno] = count
            page_images[pno] = len(page.images)
    return lines, n, page_chars, page_images


def strip_furniture(lines, page_count):
    """Drop running headers/footers and bare page numbers (top/bottom 8% of the page)."""
    def key(line):
        return re.sub(r"\d+", "#", norm(line["text"]))

    def at_edge(line):
        return line["top"] < 0.08 * line["h"] or line["bottom"] > 0.92 * line["h"]

    counts = Counter(key(l) for l in lines if at_edge(l))
    limit = max(3, int(0.4 * page_count))
    drop = {k for k, c in counts.items() if c >= limit}
    out = []
    for l in lines:
        if at_edge(l) and (key(l) in drop or re.fullmatch(
                r"(page\s*)?\d{1,4}(\s*(of|/)\s*\d{1,4})?", l["text"].strip(), re.I)):
            continue
        out.append(l)
    return out


def mark_headings(lines):
    """Set line['level'] (1-3, or 0 for body) from font size and weight; merge wrapped titles."""
    if not lines:
        return 0
    weight = Counter()
    for l in lines:
        if not l.get("synthetic"):
            weight[l["size"]] += len(l["text"])
    body_size = weight.most_common(1)[0][0]
    keys = []
    for l in lines:
        if l.get("synthetic"):
            l["_cand"], l["_key"] = False, body_size
            continue
        words = len(l["text"].split())
        big = l["size"] >= body_size + 1.0 and l["size"] >= body_size * 1.12 and words <= 18
        boldline = (l["bold"] and l["size"] >= body_size - 0.5 and words <= 12 and len(l["text"]) <= 90
                    and not l["text"].rstrip().endswith((".", ",", ";")))
        l["_cand"] = big or boldline
        l["_key"] = l["size"] if big else body_size
        if l["_cand"]:
            keys.append(l["_key"])
    sizes = sorted(set(keys), reverse=True)[:3]
    for l in lines:
        l["level"] = 0
        if l["_cand"]:
            l["level"] = sizes.index(l["_key"]) + 1 if l["_key"] in sizes else (len(sizes) or 1)
    merged = []
    for l in lines:
        p = merged[-1] if merged else None
        if (p and l["level"] and p["level"] == l["level"] and p["page"] == l["page"]
                and p["size"] == l["size"] and 0 <= l["top"] - p["bottom"] < p["size"] * 0.9):
            p["text"] += " " + l["text"]
            p["bottom"] = l["bottom"]
        else:
            merged.append(l)
    lines[:] = merged
    return body_size


def no_text_pages(lines, page_count):
    """Pages with almost no body text once headers and footers are removed."""
    chars = Counter()
    for l in lines:
        chars[l["page"]] += chars_of(l)
    return [p for p in range(1, page_count + 1) if chars[p] < 20]


def image_only_pages(lines, page_images, page_count, limit=80):
    """Pages that hold images but almost no text (typically screenshot-only pages)."""
    chars = Counter()
    for l in lines:
        chars[l["page"]] += chars_of(l)
    return [p for p in range(1, page_count + 1) if page_images.get(p) and chars[p] < limit]


def add_image_markers(lines, page_images):
    """Insert one marker line at the end of every page with images that were NOT extracted (page_images: page -> count)."""
    out, by_page = [], {}
    for l in lines:
        by_page.setdefault(l["page"], []).append(l)
    for p in sorted(set(by_page) | {p for p, k in page_images.items() if k}):
        out.extend(by_page.get(p, []))
        k = page_images.get(p, 0)
        if k:
            ref = by_page[p][-1] if p in by_page else {"h": 0.0, "bottom": 0.0}
            out.append({"page": p, "text": f"*[{k} image{'s' if k != 1 else ''} on this page not extracted]*", "size": 0, "bold": False,
                        "top": ref["bottom"], "bottom": ref["bottom"], "h": ref["h"], "level": 0, "synthetic": True})
    return out


def read_outline(pdf_path):
    """Level 1-2 bookmarks as [(title, page, level)], or [] when none exist or pypdf is missing."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        found = []

        def walk(items, level):
            for it in items:
                if isinstance(it, list):
                    walk(it, level + 1)
                else:
                    try:
                        found.append((str(it.title).strip(),
                                      reader.get_destination_page_number(it) + 1, level))
                    except Exception:  # noqa: BLE001
                        pass
        walk(reader.outline, 1)
        return [f for f in found if f[2] <= 2 and f[0]]
    except Exception:  # noqa: BLE001
        return []


# ----------------------------------------------------------------------------- topics file
def write_topics(path_base, rows):
    """Write topics.xlsx if openpyxl exists, else topics.csv. Return the path written."""
    try:
        from openpyxl import Workbook
    except ImportError:
        p = path_base + ".csv"
        with open(p, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=TOPIC_COLS)
            w.writeheader()
            w.writerows([{c: r.get(c, "") for c in TOPIC_COLS} for r in rows])
        return p
    wb = Workbook()
    ws = wb.active
    ws.title = "topics"
    ws.append(TOPIC_COLS)
    for r in rows:
        ws.append([r.get(c, "") for c in TOPIC_COLS])
    for col, width in zip("ABCDEFG", (9, 50, 7, 11, 40, 10, 40)):
        ws.column_dimensions[col].width = width
    p = path_base + ".xlsx"
    wb.save(p)
    return p


def read_topics(path):
    if path.lower().endswith(".xlsx"):
        from openpyxl import load_workbook
        ws = load_workbook(path, read_only=True, data_only=True).worksheets[0]
        data = [list(r) for r in ws.iter_rows(values_only=True)]
    else:
        with open(path, newline="", encoding="utf-8-sig") as f:
            data = list(csv.reader(f))
    if not data:
        sys.exit("ERROR: topics file is empty")
    head = [str(h or "").strip().lower() for h in data[0]]
    for need in ("title", "start_page"):
        if need not in head:
            sys.exit(f"ERROR: topics file needs a '{need}' column; found {head}")
    topics = []
    for i, row in enumerate(data[1:], 2):
        d = {h: (row[j] if j < len(row) else None) for j, h in enumerate(head)}
        if not (d.get("title") and d.get("start_page")):
            continue
        try:
            d["start_page"] = int(float(d["start_page"]))
            d["level"] = int(float(d.get("level") or 1))
        except (TypeError, ValueError):
            sys.exit(f"ERROR: row {i} has a non-numeric start_page or level")
        d["title"] = str(d["title"]).strip()
        d["start_heading"] = str(d.get("start_heading") or "").strip()
        d["source"] = str(d.get("source") or "").strip().lower()
        topics.append(d)
    return topics


# ----------------------------------------------------------------------------- modes
def cmd_check(_a):
    import importlib.util
    res = {m: importlib.util.find_spec(m) is not None for m in ("pdfplumber", "pypdf", "openpyxl", "pdfminer", "PIL", "pypdfium2")}
    for t in ("pdftotext", "tesseract"):
        res[t] = shutil.which(t) is not None
    res["cwd_writable"] = os.access(".", os.W_OK)
    note = {"pdfplumber": "REQUIRED: PDF text and fonts", "pypdf": "optional: PDF bookmarks as topics",
            "openpyxl": "optional: topics.xlsx (otherwise topics.csv)",
            "PIL": "images: saving PNGs (installed with pdfplumber)", "pypdfium2": "images: rasterizing figures (installed with pdfplumber)", "tesseract": "optional: OCR, not used by default"}
    for k, v in res.items():
        print(f"{k:<14}{'OK' if v else 'missing':<8}{note.get(k, '')}")
    sys.exit(0 if res["pdfplumber"] else 1)


def cmd_plan(a):
    lines, n, page_chars, page_images = extract_lines(a.pdf)
    lines = strip_furniture(lines, n)
    body = mark_headings(lines)
    scanned = no_text_pages(lines, n)
    os.makedirs(a.work, exist_ok=True)
    title = a.title or os.path.splitext(os.path.basename(a.pdf))[0]
    rows, source = [], "none"
    outline = read_outline(a.pdf)
    if len([o for o in outline if o[2] == 1]) >= 2:
        source = "outline"
        rows = [{"title": t, "level": lv, "start_page": pg, "start_heading": t, "source": "outline"}
                for t, pg, lv in outline]
    else:
        heads = [l for l in lines if l["level"]]
        for maxlv in (2, 1):
            sel = [l for l in heads if l["level"] <= maxlv]
            if 2 <= len(sel) <= a.max_topics:
                source = "font"
                rows = [{"title": l["text"], "level": l["level"], "start_page": l["page"],
                         "start_heading": l["text"], "source": "font"} for l in sel]
                break
    rows.sort(key=lambda r: r["start_page"])
    for i, r in enumerate(rows, 1):
        r["topic_no"] = i
    structured = len(rows) >= 2
    if not structured:
        rows = []
    tpath = write_topics(os.path.join(a.work, "topics"), rows)
    digest = os.path.join(a.work, "pages-digest.md")
    with open(digest, "w", encoding="utf-8") as f:
        f.write(f"# Page digest: {title}\n\nPages: {n}. Body font size: {body}. "
                f"Pages with no text: {scanned or 'none'}.\n\n")
        per = 700 if n <= 40 else 350
        for p in range(1, n + 1):
            pl = [l for l in lines if l["page"] == p]
            hl = [l["text"] for l in pl if l["level"]]
            f.write(f"## Page {p}\nDetected headings: {hl or 'none'}\n\n"
                    f"{' '.join(l['text'] for l in pl)[:per]}\n\n")
    summary = {"pdf": a.pdf, "pages": n, "title": title, "structure": "strong" if structured else "weak",
               "topic_source": source, "topics_found": len(rows), "topics_file": tpath,
               "digest": digest, "pages_without_text": scanned,
               "image_only_pages": image_only_pages(lines, page_images, n)}
    summary["next"] = (
        "Show the topic list to the user for confirmation, then run build." if structured else
        "Structure is weak: read pages-digest.md, propose topics (set source to ai), write them to the "
        "topics file, get the user's confirmation, then run build.")
    with open(os.path.join(a.work, "plan.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


IMAGE_LABEL = re.compile(r"^Image\s+\d+(\s*[-–:].*)?$", re.I)
FRONT_TITLE = "About this manual"
# a contents line: "Title ____ 6" / "Title ...... 6" (underscore, dot or ellipsis leaders, then a page number)
TOC_LINE = re.compile(r"^(.*?\S)\s*[._…·]{3,}\s*(\d+|[ivxlcdm]+)$", re.I)
TOC_LEADER = re.compile(r"^(.*?)\s*[.…· ]{3,}\s*(\d+|[ivxlcdm]+)$", re.I)


def is_toc_title(title):
    return norm(title) in ("contents", "table of contents")


def toc_to_md(lines, own_title, pdf_name):
    """Contents pages become an indented list; dot leaders turn into '(p. N)'."""
    body = [l for l in lines if not l.get("synthetic") and norm(l["text"]) != norm(own_title)]
    cols = sorted({round(l.get("x0", 0) / 8) for l in body})
    out, cur_page = [], lines[0]["page"] if lines else None
    for l in lines:
        if l["page"] != cur_page:
            cur_page = l["page"]
            out.extend(["", f"*Source: [PDF page {cur_page}]({pdf_ref(pdf_name, cur_page)})*", ""])
        if l.get("synthetic"):
            out.extend(["", l["text"], ""])
            continue
        if norm(l["text"]) == norm(own_title):
            continue
        m = TOC_LEADER.match(l["text"])
        text = f"{m.group(1).strip()} (p. {m.group(2)})" if m else l["text"]
        out.append("   " * cols.index(round(l.get("x0", 0) / 8)) + "- " + text)
    return "\n".join(out).strip() + "\n"


def body_to_md(lines, own_title, topic_level, pdf_name):
    """Convert the lines of one topic to Markdown: paragraphs, nested lists, sub-headings, page links."""
    if is_toc_title(own_title):
        return toc_to_md(lines, own_title, pdf_name)
    out, cur, stack, prev = [], None, [], None   # cur: {"kind": "para"|"item", "text": [...], "prefix": str}

    def blank():
        if out and out[-1] != "":
            out.append("")

    def flush():
        nonlocal cur
        if cur:
            if cur["kind"] == "para":
                blank()
                out.append(" ".join(cur["text"]))
                out.append("")
            else:
                out.append(cur["prefix"] + " ".join(cur["text"]))
        cur = None

    def add_text(parts, t):
        if parts and parts[-1].endswith("-") and t[:1].islower():
            parts[-1] = parts[-1][:-1] + t
        else:
            parts.append(t)

    cur_page = lines[0]["page"] if lines else None
    last_h = 1                                    # level of the previous heading; the topic title is the H1
    for l in lines:
        t = l["text"]
        if l["page"] != cur_page:
            flush()
            blank()
            cur_page = l["page"]
            out.extend([f"*Source: [PDF page {cur_page}]({pdf_ref(pdf_name, cur_page)})*", ""])
            prev, stack = None, []
        if l.get("toc_title"):
            flush()
            if out and out[-1] and not out[-1].startswith("- "):
                blank()
            out.append(f"- [{l['toc_title']}]({l['toc_link']})" if l.get("toc_link") else f"- {l['toc_title']}")
            prev, stack = None, []
            continue
        if l.get("synthetic") or IMAGE_LABEL.match(t):
            flush()
            blank()
            out.extend([t if l.get("synthetic") else f"*{t}*", ""])
            prev, stack = None, []
            continue
        if l["level"]:
            if norm(t) == norm(own_title):
                prev = l
                continue
            flush()
            blank()
            last_h = min(6, max(2, 1 + l["level"] - topic_level), last_h + 1)   # never skip a level
            out.extend(["#" * last_h + " " + t, ""])
            stack = []
        elif BULLET.match(t):
            flush()
            x = l.get("x0", 0)
            while stack and stack[-1] >= x - 2:
                stack.pop()
            indent = len(stack)
            stack.append(x)
            m = re.match(r"^(\d{1,2}[.)]|[a-z][.)])\s+(.*)", t)
            marker, text = (m.group(1), m.group(2)) if m else ("-", BULLET.sub("", t))
            cur = {"kind": "item", "text": [text], "prefix": "   " * indent + marker + " "}
        else:
            gap = (l["top"] - prev["bottom"]) if prev and prev["page"] == l["page"] else 0
            if cur and gap <= l["size"] * 0.9:
                add_text(cur["text"], t)          # wrapped line of the current paragraph or list item
            else:
                flush()
                stack = []
                cur = {"kind": "para", "text": [t], "prefix": ""}
        prev = l
    flush()
    return "\n".join(out).strip() + "\n"


def cmd_build(a):
    lines, n, page_chars, page_images = extract_lines(a.pdf)
    lines = strip_furniture(lines, n)
    mark_headings(lines)
    img_only = image_only_pages(lines, page_images, n)
    images, img_stats, img_failed = ([], Counter(), {}) if a.no_images else extract_images(
        a.pdf, n, a.min_image_px, a.image_dpi, a.vector_figures)
    attach_images(lines, images)
    missing = dict(page_images) if a.no_images else img_failed
    lines = add_image_markers(lines, missing)
    topics = read_topics(a.topics)
    topics.sort(key=lambda t: t["start_page"])
    if not topics:
        sys.exit("ERROR: no topics found in the topics file")
    bad = [f"'{t['title']}': start_page {t['start_page']} is outside 1-{n}"
           for t in topics if not 1 <= t["start_page"] <= n]
    if bad:
        sys.exit("ERROR: " + "; ".join(bad))
    warnings, starts = [], []
    for t in topics:
        lo = starts[-1] + 1 if starts else 0
        idx = next((i for i, l in enumerate(lines) if i >= lo and l["page"] == t["start_page"] and (
            not t["start_heading"] or norm(l["text"]).startswith(norm(t["start_heading"])[:40]))), None)
        if idx is None:
            idx = next((i for i, l in enumerate(lines) if l["page"] >= t["start_page"]), len(lines))
            if t["start_heading"]:
                warnings.append(f"heading '{t['start_heading']}' not found on page {t['start_page']}; "
                                "split at the page start")
        starts.append(max(idx, starts[-1] if starts else 0))
    title = a.title or os.path.splitext(os.path.basename(a.pdf))[0]
    pdf_name = BAD_NAME_CHARS.sub("-", os.path.basename(a.pdf))
    out_root = unique_dir(os.path.join(a.out, slugify(title)))
    stage = out_root + ".staging"
    shutil.rmtree(stage, ignore_errors=True)
    os.makedirs(stage)
    front = lines[:starts[0]]
    if sum(chars_of(l) for l in front) > 200:
        topics.insert(0, {"title": FRONT_TITLE, "level": 1, "start_page": front[0]["page"],
                          "start_heading": "", "source": "auto"})
        starts.insert(0, 0)
    bounds = starts + [len(lines)]
    entries = []
    for i, t in enumerate(topics):
        seg = lines[bounds[i]:bounds[i + 1]]
        pages = sorted({l["page"] for l in seg}) or [t["start_page"]]
        entries.append({"title": t["title"], "level": t["level"], "source": t["source"] or "unspecified",
                        "start_page": pages[0], "end_page": pages[-1],
                        "chars": sum(chars_of(l) for l in seg),
                        "images": sum(1 for l in seg if l.get("image")),
                        "images_missing": sum(1 for l in seg if l.get("synthetic") and not l.get("table") and not l.get("image")),
                        "tables": sum(1 for l in seg if l.get("table")), "seg": seg, "file": None})
    # a heading with no text of its own, directly followed by a deeper topic, is a group heading in the index
    for i, e in enumerate(entries[:-1]):
        e["group"] = e["chars"] < 40 + len(e["title"]) and not e["images"] and entries[i + 1]["level"] > e["level"]
    entries[-1]["group"] = False
    pages_list = [e for e in entries if not e["group"]]
    fmt = a.format
    render_outputs.configure(a.org, a.doc_date)
    ext = ".html" if fmt == "html" else ".md"
    for k, e in enumerate(pages_list, 1):
        e["file"] = f"{k:02d}-{slugify(e['title'])}{ext}"
    # contents lines in the front matter become links to the topic pages (no leader lines or printed page numbers)
    target, nxt = {}, None
    for e in reversed(entries):
        nxt = e["file"] or nxt                      # a group heading links to the first page under it
        if nxt:
            target.setdefault(norm(e["title"]), nxt)
    if entries and entries[0]["title"] == FRONT_TITLE:
        for l in entries[0]["seg"]:
            m = None if l.get("synthetic") or l.get("table") else TOC_LINE.match(l["text"])
            if m:
                l["toc_title"], l["toc_link"] = m.group(1).strip(), target.get(norm(m.group(1)))
    stack = []
    for e in entries:
        while stack and stack[-1]["level"] >= e["level"]:
            stack.pop()
        e["parent"] = stack[-1] if stack else None
        stack.append(e)
    if not a.no_pdf_copy:
        shutil.copy(a.pdf, os.path.join(stage, pdf_name))
    # images: stable names <topic-slug>-p<page>-<n>.<ext>; identical pictures (same hash) share one file
    image_files, by_hash, image_index = {}, {}, []
    for e in pages_list:
        stem, counter = os.path.splitext(e["file"])[0], Counter()
        e["image_list"] = []
        for l in e["seg"]:
            if not l.get("image"):
                continue
            im = l["img"]
            if im["sha"] in by_hash:
                name = by_hash[im["sha"]]
            else:
                counter[im["page"]] += 1
                name = f"images/{stem}-p{im['page']:02d}-{counter[im['page']]:02d}{im['ext']}"
                by_hash[im["sha"]] = name
                image_files[name] = im["data"]
            alt = re.sub(r"[\[\]]", "", l["caption"] or f"Figure on page {im['page']}").strip()
            l["text"] = f"![{alt}]({name})" + (f"\n*{re.sub(r'[*]', '', l['caption'])}*" if l["caption"] else "")
            rec = {"file": name, "page": im["page"], "alt": alt, "caption": l["caption"], "width": im["width"],
                   "height": im["height"], "kind": im["kind"], "sha256": im["sha"], "topic": e["file"]}
            e["image_list"].append(rec)
            image_index.append(rec)
    if image_files:
        os.makedirs(os.path.join(stage, "images"))
        for name, data in image_files.items():
            with open(os.path.join(stage, name), "wb") as f:
                f.write(data)
    if fmt == "markdown-basic":
        for k, e in enumerate(pages_list):
            crumb = [f"[{title}](index.md)"]
            if e["parent"]:
                par = e["parent"]
                crumb.append(par["title"] if par["group"] else f"[{par['title']}]({par['file']})")
            crumb.append(e["title"])
            crumb_md = " › ".join(crumb)
            nav = []
            if k > 0:
                nav.append(f"[Previous: {pages_list[k - 1]['title']}]({pages_list[k - 1]['file']})")
            nav.append("[Index](index.md)")
            if k < len(pages_list) - 1:
                nav.append(f"[Next: {pages_list[k + 1]['title']}]({pages_list[k + 1]['file']})")
            meta = (f"**Source:** {pdf_name}, {pages_md(pdf_name, e['start_page'], e['end_page'])}"
                    f" \u00b7 Topic {k + 1} of {len(pages_list)}")
            md = (f"> {crumb_md}\n\n# {e['title']}\n\n{meta}\n\n"
                  f"{body_to_md(e['seg'], e['title'], e['level'], pdf_name)}\n---\n{' | '.join(nav)}\n")
            with open(os.path.join(stage, e["file"]), "w", encoding="utf-8") as f:
                f.write(md)
    elif fmt == "agent-md":
        render_outputs.write_agent_md_pages(stage, pages_list, title, pdf_name, n, body_to_md)
    else:
        render_outputs.write_html_pages(stage, entries, pages_list, title, pdf_name, n, body_to_md)
    total_in = sum(chars_of(l) for l in lines)
    total_out = sum(e["chars"] for e in entries)
    empty = [e["title"] for e in pages_list if e["chars"] < 20 and not e["images"]]
    if empty:
        warnings.append(f"topics with almost no text: {empty}")
    scanned = [p for p in no_text_pages(lines, n) if p not in img_only]
    if scanned:
        warnings.append(f"pages with no body text (blank, or scanned images that need OCR): {scanned}")
    if img_only:
        warnings.append(f"pages that are only images (their text is inside the picture; OCR was not run): {img_only}")
    covered = {p for e in entries for p in range(e["start_page"], e["end_page"] + 1)}
    gaps = [p for p in range(1, n + 1) if p not in covered and p not in scanned]
    if gaps:
        warnings.append(f"pages not covered by any topic: {gaps}")
    text_ok = bool(total_in) and total_out >= 0.98 * total_in
    pictures_only = not total_in and bool(image_index)      # scanned document: all pages extracted as pictures, no text to check
    status = "PASS" if (not empty and (text_ok or pictures_only)) else "FAIL"
    def emit(status, lc):
        """Write validation, index, manifest and validation.json; returns the report. Called twice so the
        final files carry the link-check result (and FAIL if it failed)."""
        labels = {}
        for l in lines:
            if not l.get("synthetic") and IMAGE_LABEL.match(l["text"]):
                labels.setdefault(l["page"], []).append(l["text"])
        img_pages = [p for p, k in sorted(page_images.items()) if k]
        mixed = [p for p in img_pages if p not in img_only]
        pdflink = lambda p: f"[{p}]({pdf_ref(pdf_name, p)})"
        val = [f"# Validation: {title}", "", "## Summary", "",
               f"- Result: **{status}**",
               f"- PDF pages: {n}; topic pages: {len(pages_list)}; group headings: {len(entries) - len(pages_list)}",
               f"- Characters read from the PDF: {total_in}; written to the pages: {total_out}"
               f" ({(100.0 * total_out / total_in) if total_in else 0:.2f}%)",
               "- Running headers, footers and bare page numbers were removed.", ""]
        val += ["## Pages that are only images", ""]
        if img_only:
            val += ["The text inside screenshots is not read (no OCR was run); the pictures themselves are extracted. Image labels in the text layer are kept.", "",
                    "| PDF page | Image labels on the page |", "|---|---|"]
            val += [f"| {pdflink(p)} | {', '.join(labels.get(p, [])) or 'none'} |" for p in img_only]
        else:
            val += ["None."]
        val += ["", "## Images", ""]
        if a.no_images:
            val += [f"Image extraction was switched off (--no-images). {sum(page_images.values())} embedded images on "
                    f"{len(img_pages)} pages were not extracted.", ""]
        elif image_index:
            val += [f"{len(image_index)} images placed in the pages, {len(image_files)} unique files in `images/` "
                    "(identical pictures share one file). Text inside pictures is not read (no OCR).", "",
                    "| PDF page | File | Kind | Size (px) | Caption |", "|---|---|---|---|---|"]
            val += [f"| {pdflink(r['page'])} | `{r['file']}` | {r['kind']} | {r['width']}x{r['height']} | {r['caption'] or 'none'} |"
                    for r in image_index]
            val += [""]
        else:
            val += ["No images were extracted." if img_pages or img_stats.get("skipped_small") or img_stats.get("skipped_repeated")
                    else "No embedded images found.", ""]
        if not a.no_images and (img_stats.get("skipped_small") or img_stats.get("skipped_repeated") or img_failed):
            val += [f"Skipped as decorative: {img_stats.get('skipped_small', 0)} small (under {a.min_image_px} px or 24 pt), "
                    f"{img_stats.get('skipped_repeated', 0)} repeated on many pages. Could not extract: {img_stats.get('failed', 0)}.", ""]
        val += ["## Pages where reading order should be checked", ""]
        if mixed:
            val += ["Text and images share these pages. Text follows top-to-bottom order around the images.", "",
                    "| PDF page | Images |", "|---|---|"]
            val += [f"| {pdflink(p)} | {page_images[p]} |" for p in mixed]
        else:
            val += ["None."]
        val += ["", "## Link check", ""]
        if lc is None:
            val += ["Not run yet."]
        else:
            val += [f"- Result: **{'PASS' if lc['ok'] else 'FAIL'}**: {lc['files']} pages, {lc['links']} links and references checked "
                    "(files, anchors, PDF page numbers, one h1 per page, no skipped heading levels)."]
            val += [f"- Broken: {x}" for x in lc["broken"] + lc["heading_problems"]]
        val += ["", "## Warnings", ""] + ([f"- {w}" for w in warnings] or ["None."])
        val_md = "\n".join(val) + "\n"
        if fmt == "html":
            render_outputs.write_html_validation(stage, title, entries, pages_list, val_md, pdf_name)
        else:
            with open(os.path.join(stage, "validation.md"), "w", encoding="utf-8") as f:
                f.write(val_md)
        idx = [f"# {title}", "",
               f"> Converted from [{os.path.basename(a.pdf)}]({pdf_ref(pdf_name, 1)}) · {n} pages · "
               f"{len(pages_list)} topic pages · Conversion check: {status} (see [validation.md](validation.md))", "",
               "Each page links back to the PDF page it came from. Page text is copied from the PDF unchanged.", ""]
        if any(e["source"] == "ai" for e in entries):
            idx += ["> Some topic boundaries were proposed by AI and confirmed by a person.", ""]
        idx += ["## Topics", ""]
        for e in entries:
            pad = "  " * (max(e["level"], 1) - 1)
            rng = pages_md(pdf_name, e["start_page"], e["end_page"])
            idx.append(f"{pad}- **{e['title']}** — {rng}" if e["group"] else
                       f"{pad}- [{e['title']}]({e['file']}) — {rng}")
        notes = []
        if img_only and a.no_images:
            notes.append("Pages that are only images (skipped because --no-images was set): "
                         + ", ".join(f"[{p}]({pdf_ref(pdf_name, p)})" for p in img_only))
        truly_empty = [p for p in scanned if p not in img_only]
        if truly_empty:
            notes.append("Pages with no text or extractable images (blank, or scanned images that need OCR): "
                         + ", ".join(f"[{p}]({pdf_ref(pdf_name, p)})" for p in truly_empty))
        if notes:
            idx += ["", "## Not converted", ""] + [f"- {x}" for x in notes]
        if fmt == "markdown-basic":
            with open(os.path.join(stage, "index.md"), "w", encoding="utf-8") as f:
                f.write("\n".join(idx) + "\n")
        elif fmt == "agent-md":
            render_outputs.write_agent_md_index(stage, entries, pages_list, title, pdf_name, n, status, notes)
        else:
            render_outputs.write_html_index(stage, entries, pages_list, title, pdf_name, n, status, notes, a)
        report = {"status": status, "pages": n, "topics": len(pages_list), "groups": len(entries) - len(pages_list), "text_chars_in": total_in,
                  "text_chars_out": total_out, "image_only_pages": img_only,
                  "images": {"placed": len(image_index), "unique_files": len(image_files),
                             "skipped_small": img_stats.get("skipped_small", 0),
                             "skipped_repeated": img_stats.get("skipped_repeated", 0),
                             "failed": img_stats.get("failed", 0), "extraction_off": bool(a.no_images),
                             "vector_figures": bool(a.vector_figures), "min_image_px": a.min_image_px},
                  "pdf_copied": not a.no_pdf_copy, "warnings": warnings,
                  "link_check": None if lc is None else {"status": "PASS" if lc["ok"] else "FAIL", "pages": lc["files"], "links": lc["links"],
                                                         "broken": lc["broken"], "heading_problems": lc["heading_problems"]}}
        with open(os.path.join(stage, "validation.json"), "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        shutil.copy(a.topics, os.path.join(stage, "topics" + os.path.splitext(a.topics)[1]))
        topic_files = {e["file"] for e in pages_list}
        kinds = {"index.md": "index", "index.html": "index", "validation.md": "report", "validation.html": "report",
                 "validation.json": "report", "style.css": "stylesheet", "chunks.jsonl": "chunks", pdf_name: "source-pdf"}
        others = [{"file": f, "kind": kinds.get(f, "other")} for f in sorted(os.listdir(stage))
                  if f not in topic_files and f != "manifest.json" and f != "images"]
        seen_img = set()
        for r in sorted(image_index, key=lambda r: r["file"]):
            if r["file"] in seen_img:
                continue
            seen_img.add(r["file"])
            same = [x for x in image_index if x["file"] == r["file"]]
            others.append({"file": r["file"], "kind": "image", "sha256": r["sha256"], "size_px": f"{r['width']}x{r['height']}",
                           "extracted_as": r["kind"], "alt": r["alt"], "used_on_pages": sorted({x["page"] for x in same}),
                           "topics": sorted({x["topic"] for x in same})})
        manifest = {"source": os.path.basename(a.pdf), "title": title, "format": fmt, "status": status,
                    "files": others + [{"file": e["file"], "kind": "topic", "title": e["title"],
                                        "pages": f"{e['start_page']}-{e['end_page']}", "topic_source": e["source"]}
                                       for e in pages_list]}
        report["format"] = fmt
        report["tables"] = sum(e["tables"] for e in entries)
        for name, obj in (("validation.json", report), ("manifest.json", manifest)):  # rewrite validation.json with format/tables
            with open(os.path.join(stage, name), "w", encoding="utf-8") as f:
                json.dump(obj, f, indent=2)
        return report

    report = emit(status, None)
    lc = check_links.check_output(stage, pdf_copied=not a.no_pdf_copy, pdf_pages=n)
    warnings.extend(f"link check: {x}" for x in lc["warnings"])
    if not lc["ok"]:
        status = "FAIL"
        warnings.append(f"link check FAILED: {len(lc['broken'])} broken links, {len(lc['heading_problems'])} heading problems (see Link check)")
    report = emit(status, lc)
    lc2 = check_links.check_output(stage, pdf_copied=not a.no_pdf_copy, pdf_pages=n)   # the final files must pass too
    if status == "PASS" and not lc2["ok"]:
        status = "FAIL"
        warnings.append("link check FAILED on the final files (see Link check)")
        report = emit(status, lc2)
    if status == "PASS":
        import time
        for _attempt in range(5):
            try:
                os.rename(stage, out_root)
                break
            except PermissionError:
                if _attempt == 4:
                    raise
                time.sleep(0.15)
        report["output_dir"] = out_root
    else:
        report["output_dir"] = stage + " (kept for diagnosis, not accepted)"
    print(json.dumps(report, indent=2))
    sys.exit(0 if status == "PASS" else 2)


# ---------------------------------------------------------------- publish (SharePoint split layout)
def cmd_publish(a):
    """Split a finished HTML build into the SharePoint layout and rewrite every link to match.

    SharePoint only serves .html pages from Site Pages; everything else (style.css, images/, reports, topics file)
    must live in Site Assets. The result is a local mirror of the site under --site-root:
        <site-root>/<pages-path>/*.html          -> upload to the Site Pages library (e.g. SitePages/Manuals/CEIS)
        <site-root>/<assets-path>/...            -> upload to the Site Assets library (e.g. SiteAssets/CEIS, images/ kept)
    Links are page-relative (e.g. ../../../SiteAssets/CEIS/style.css), so they work on any host name.
    --pdf-path names a PDF that is ALREADY on the site (site-relative, e.g. Manuals/ceis-manual.pdf): pages link to it
    and it is not uploaded again (a reference copy is placed in the mirror only so the link check can count pages;
    it is listed under reference_only in publish-plan.json). Without --pdf-path the PDF goes to the assets folder.
    Writes publish-plan.json (every file to upload, with library and folder) and runs the link check on the mirror."""
    src = a.build.rstrip("/\\")
    with open(os.path.join(src, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    if manifest.get("format") != "html":
        sys.exit("ERROR: publish supports --format html builds only")
    val = {}
    if os.path.exists(os.path.join(src, "validation.json")):
        with open(os.path.join(src, "validation.json"), encoding="utf-8") as f:
            val = json.load(f)
    if val.get("status") != "PASS":
        sys.exit("ERROR: the build did not PASS; fix it before publishing")
    n_pages = val.get("pages")
    pdf_name = next((e["file"] for e in manifest["files"] if e.get("kind") == "source-pdf"), None) \
        or BAD_NAME_CHARS.sub("-", manifest["source"])
    posix = lambda x: x.replace("\\", "/").strip("/")
    if a.pdf_path.lower().startswith("http"):           # a full URL was given: keep the path after the site
        a.pdf_path = re.sub(r"^https?://[^/]+/(sites|teams)/[^/]+/", "", unquote(a.pdf_path))
    missing = []
    if not (a.folder or (a.pages_path and a.assets_path)):
        missing.append("Destination folder (used in both Site Pages and Site Assets), e.g. Manuals/CEIS")
    if not (a.pdf_path or a.no_site_pdf):
        missing.append("Is the source PDF already on the SharePoint site? If yes, its path or URL "
                       "(e.g. Manuals/ceis-manual.pdf); if no, the PDF is published to the assets folder")
    if not (a.design_system or a.no_design_system):
        missing.append("Is there a shared design system or CSS on the site to reuse (fonts, colours, logo)? "
                       "If yes, its folder (e.g. SiteAssets/bc-gov-design-system) -> --design-system; if no -> --no-design-system")
    if missing and sys.stdin.isatty():
        if not (a.folder or (a.pages_path and a.assets_path)):
            a.folder = input("Destination folder for Site Pages and Site Assets (e.g. Manuals/CEIS): ").strip()
        if not (a.pdf_path or a.no_site_pdf):
            ans = input("Path or URL of the source PDF already on the site (blank = not on the site): ").strip()
            a.pdf_path = re.sub(r"^https?://[^/]+/(sites|teams)/[^/]+/", "", unquote(ans)) if ans else ""
            a.no_site_pdf = not ans
        missing = [] if (a.folder or (a.pages_path and a.assets_path)) else missing
    if missing:
        sys.exit("ASK THE USER before publishing:\n- " + "\n- ".join(missing))
    folder = posix(a.folder)
    pages_rel = posix(a.pages_path) or f"{posix(a.pages_library)}/{folder}"
    assets_rel = posix(a.assets_path) or f"{posix(a.assets_library)}/{folder}"
    pdf_rel = posix(a.pdf_path) if a.pdf_path else f"{assets_rel}/{pdf_name}"
    root = unique_dir(a.site_root) if os.path.exists(a.site_root) and os.listdir(a.site_root) else a.site_root
    pages_dir, assets_dir = os.path.join(root, pages_rel), os.path.join(root, assets_rel)
    os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)
    html_files = {f for f in os.listdir(src) if f.endswith(".html")}
    rel_from_pages = lambda target: os.path.relpath(os.path.join(root, target), pages_dir).replace(os.sep, "/")
    pdf_href = quote(rel_from_pages(pdf_rel), safe="/.")
    skip = re.compile(r"^(https?:|mailto:|tel:|data:|javascript:|#)", re.I)

    def rewrite(m):
        attr, link = m.group(1), m.group(2)
        if skip.match(link):
            return m.group(0)
        target, sep, frag = link.partition("#")
        t = unquote(target)
        if t in html_files:
            new = target                                   # page to page: same folder
        elif t == pdf_name:
            new = pdf_href
        else:
            new = quote(rel_from_pages(f"{assets_rel}/{t}"), safe="/.-_~")
        return f'{attr}="{new}{sep}{frag}"'

    ds = posix(a.design_system) if a.design_system else ""
    shared_refs = []
    head_css = None
    if ds:
        # shared B.C. Design System folder on the site: fonts, tokens and logo are reused, and the manual styling is
        # published ONCE as <ds>/manuals.css for every manual (not copied per manual)
        os.makedirs(os.path.join(root, ds), exist_ok=True)
        with open(os.path.join(src, "style.css"), encoding="utf-8") as f:
            manuals_css = f.read() + render_outputs.LOGO_CSS
        with open(os.path.join(root, ds, "manuals.css"), "w", encoding="utf-8") as f:
            f.write(manuals_css)
        for ref in [x for x in (a.ds_tokens, a.ds_logo) if x]:
            dest = os.path.join(root, ds, ref)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            open(dest, "a").close()               # placeholder so the link check can resolve it; NOT uploaded
            shared_refs.append(f"{ds}/{ref}")
        links = ([f'<link rel="stylesheet" href="{rel_from_pages(ds + "/" + a.ds_tokens)}">'] if a.ds_tokens else []) \
            + [f'<link rel="stylesheet" href="{rel_from_pages(ds + "/manuals.css")}">']
        head_css = "\n".join(links)
        logo = (f'<img class="bc-logo" src="{rel_from_pages(ds + "/" + a.ds_logo)}" alt="Government of British Columbia">'
                if a.ds_logo else "")
    css_text = ""
    if not ds and not a.link_css and os.path.exists(os.path.join(src, "style.css")):
        with open(os.path.join(src, "style.css"), encoding="utf-8") as f:
            css_text = f.read()
    link_re = re.compile(r'<link rel="stylesheet" href="[^"]*style\.css">')

    def _parse_nav(spec):
        lbl, _, path = spec.partition("|")
        lbl, path = lbl.strip(), posix(path)
        if not lbl or not path:
            sys.exit(f"ERROR: nav target must be 'Label|SiteRelativePath', got: {spec!r}")
        return lbl, path

    nav_ancestors = []
    if getattr(a, "site_home", ""):
        nav_ancestors.append(_parse_nav(a.site_home))
    for p_spec in getattr(a, "parent", []) or []:
        nav_ancestors.append(_parse_nav(p_spec))
    ancestor_links = []
    for lbl, target_rel in nav_ancestors:
        dest = os.path.join(root, target_rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if not os.path.exists(dest):
            with open(dest, "w", encoding="utf-8") as pf:
                if target_rel.lower().endswith((".html", ".htm")):
                    pf.write(f"<!DOCTYPE html><html><body><h1>{render_outputs._html.escape(lbl)}</h1></body></html>\n")
        shared_refs.append(target_rel)
        ancestor_links.append((lbl, quote(rel_from_pages(target_rel), safe="/.-_~")))

    doc_title = manifest.get("title") or os.path.basename(src)
    sub_prefix = "".join(f'<a href="{href}">{render_outputs._html.escape(lbl)}</a>' for lbl, href in ancestor_links)
    crumb_prefix = "".join(f'<li><a href="{href}">{render_outputs._html.escape(lbl)}</a></li>' for lbl, href in ancestor_links)

    toc_re = re.compile(r'<nav class="toc" aria-label="Contents">(.*?)</nav>', re.S)
    toc_js_rel = quote(rel_from_pages(f"{assets_rel}/toc.js"), safe="/.-_~")
    toc_template = None
    if not getattr(a, "inline_toc", False) and "index.html" in html_files:
        with open(os.path.join(src, "index.html"), encoding="utf-8") as f:
            m_toc = toc_re.search(f.read())
        if m_toc:
            toc_template = m_toc.group(1).replace(' aria-current="page"', "").replace("<details open>", "<details>")
            toc_js_code = (
                "(function(){\n"
                "  var nav=document.querySelector('nav.toc');if(!nav)return;\n"
                f"  nav.innerHTML={json.dumps(toc_template)};\n"
                "  var cur=nav.getAttribute('data-current')||(location.pathname.split('/').pop()||'index.html');\n"
                "  var links=nav.querySelectorAll('a[href]');\n"
                "  for(var i=0;i<links.length;i++){\n"
                "    if(links[i].getAttribute('href').split('#')[0]===cur){\n"
                "      links[i].setAttribute('aria-current','page');\n"
                "      var d=links[i].closest('details');\n"
                "      while(d){d.setAttribute('open','');d=d.parentElement?d.parentElement.closest('details'):null;}\n"
                "    }\n"
                "  }\n"
                "})();\n"
            )
            with open(os.path.join(assets_dir, "toc.js"), "w", encoding="utf-8") as tf:
                tf.write(toc_js_code)

    plan, reference_only = [], []
    if toc_template is not None:
        plan.append({"local": f"{assets_rel}/toc.js", "library": assets_rel.split("/")[0],
                     "folder": "/".join(assets_rel.split("/")[1:]), "file": "toc.js"})
    for dirpath, _, files in os.walk(src):
        for fn in sorted(files):
            rel = os.path.relpath(os.path.join(dirpath, fn), src).replace(os.sep, "/")
            if not getattr(a, "include_report", False) and rel in ("validation.html", "validation.json"):
                continue                                   # internal QA artifacts stay local unless --include-report is set
            if rel in html_files:
                with open(os.path.join(src, rel), encoding="utf-8") as f:
                    text = f.read()
                if head_css:
                    text = link_re.sub(lambda m: head_css, text, count=1)
                    if logo:
                        text = text.replace('<header class="bc"><div class="in">', '<header class="bc"><div class="in">' + logo, 1)
                    text = re.sub(r'\b(href|src)="([^"]*)"', lambda m: m.group(0) if "/" in m.group(2) and
                                  (ds in unquote(m.group(2))) else rewrite(m), text)
                elif css_text:   # SharePoint's file viewer renders pages from another address, so a linked stylesheet does not load: embed it
                    text = link_re.sub(lambda m: "<style>\n" + css_text + "\n</style>", text, count=1)
                if not head_css:
                    text = re.sub(r'\b(href|src)="([^"]*)"', rewrite, text)
                if ancestor_links:
                    text = text.replace(
                        '<div class="subheader"><div class="in"><a href="index.html">Home</a>',
                        f'<div class="subheader"><div class="in">{sub_prefix}<a href="index.html">Guide Home</a>',
                        1,
                    )
                    text = text.replace(
                        '<nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="index.html">Home</a></li>',
                        f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{crumb_prefix}<li><a href="index.html">{render_outputs._html.escape(doc_title)}</a></li>',
                        1,
                    )
                if toc_template is not None:
                    text = toc_re.sub(
                        lambda _m: f'<nav class="toc" aria-label="Contents" data-current="{render_outputs._html.escape(rel, quote=True)}"></nav><script src="{toc_js_rel}"></script>',
                        text,
                        count=1,
                    )
                with open(os.path.join(pages_dir, rel), "w", encoding="utf-8") as f:
                    f.write(text)
                plan.append({"local": f"{pages_rel}/{rel}", "library": pages_rel.split("/")[0],
                             "folder": "/".join(pages_rel.split("/")[1:]), "file": rel})
            elif rel == "style.css" and ds:
                continue                                   # replaced by the shared <ds>/manuals.css
            elif rel == pdf_name and a.pdf_path:
                dest = os.path.join(root, pdf_rel)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy(os.path.join(src, rel), dest)
                reference_only.append(pdf_rel)
            else:
                dest = os.path.join(assets_dir, rel)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy(os.path.join(src, rel), dest)
                sub = os.path.dirname(rel)
                plan.append({"local": f"{assets_rel}/{rel}", "library": assets_rel.split("/")[0],
                             "folder": "/".join(assets_rel.split("/")[1:] + ([sub] if sub else [])),
                             "file": os.path.basename(rel)})
    if ds:
        plan.append({"local": f"{ds}/manuals.css", "library": ds.split("/")[0], "folder": "/".join(ds.split("/")[1:]),
                     "file": "manuals.css", "shared": True})
    lc = check_links.check_output(root, pdf_copied=True, pdf_pages=n_pages)
    out = {"design_system": ds or None, "shared_refs": shared_refs, "status": "PASS" if lc["ok"] else "FAIL", "site_root": root, "pages_path": pages_rel,
           "assets_path": assets_rel, "pdf_link": pdf_rel, "pdf_already_on_site": bool(a.pdf_path),
           "upload": plan, "reference_only": reference_only,
           "counts": {"pages": sum(1 for p in plan if p["local"].startswith(pages_rel + "/")),
                      "assets": sum(1 for p in plan if p["local"].startswith(assets_rel + "/"))},
           "link_check": {"status": "PASS" if lc["ok"] else "FAIL", "pages": lc["files"], "links": lc["links"],
                          "broken": lc["broken"][:50], "heading_problems": lc["heading_problems"][:50]}}
    with open(os.path.join(root, "publish-plan.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    summary = {k: v for k, v in out.items() if k != "upload"}
    print(json.dumps(summary, indent=2))
    sys.exit(0 if lc["ok"] else 2)


def cmd_verify(a):
    """Check a SharePoint publish against its publish-plan.json (run AFTER uploading; a publish is not done until this PASSes).

    --online is a JSON file the agent writes from the live libraries: {"<library>/<folder>": [{"name", "size", "level"}, ...], ...},
    where level is the item's publication.level from Graph ("published", "checkout", ...). Site Pages files are uploaded
    CHECKED OUT; any file not "published" fails the check (other users cannot see it until it is checked in).
    one key per destination folder in the plan (e.g. SitePages/Manuals/CEIS, SiteAssets/Manuals/CEIS,
    SiteAssets/Manuals/CEIS/images) plus the folder of a --pdf-path PDF (e.g. "Manuals": [{"name": "ceis-manual.pdf", ...}]).
    Confirms every planned file is online with the same byte size, the linked PDF exists on the site with the same size
    as the source, and reports extra online files (left from an earlier publish) as warnings."""
    root = a.site_root
    with open(os.path.join(root, "publish-plan.json"), encoding="utf-8") as f:
        plan = json.load(f)
    with open(a.online, encoding="utf-8") as f:
        raw = json.load(f)
    online = {k.strip("/"): {i["name"]: i.get("size") for i in v} for k, v in raw.items()}
    level = {f"{k.strip('/')}/{i['name']}": i.get("level") for k, v in raw.items() for i in v}
    missing, size_diff, warns, checked, not_published = [], [], [], 0, []
    planned = {}
    for e in plan["upload"]:
        key = "/".join(x for x in (e["library"], e["folder"]) if x)
        planned.setdefault(key, set()).add(e["file"])
        checked += 1
        here = online.get(key)
        if here is None:
            missing.append(f"{key}: folder not in the online listing")
            continue
        if e["file"] not in here:
            missing.append(f"{key}/{e['file']}")
            continue
        lvl = level.get(f"{key}/{e['file']}")
        if lvl is not None and lvl != "published":         # still checked out (or a draft): invisible to other users
            not_published.append(f"{key}/{e['file']} ({lvl})")
        local = os.path.getsize(os.path.join(root, e["local"]))
        if here[e["file"]] is not None and here[e["file"]] != local:
            if e["file"].lower().endswith((".xlsx", ".docx", ".pptx")):   # SharePoint writes its own properties into Office files
                warns.append(f"{key}/{e['file']}: size changed on upload ({local} -> {here[e['file']]} bytes); normal for Office files")
                continue
            size_diff.append(f"{key}/{e['file']}: online {here[e['file']]} bytes, local {local}")
    for key, names in planned.items():
        extra = sorted(set(online.get(key, {})) - names)
        if extra:
            warns.append(f"{key}: {len(extra)} extra file(s) online not in this publish: {extra[:10]}")
    for ref in plan.get("reference_only", []):
        folder, name = os.path.dirname(ref), os.path.basename(ref)
        checked += 1
        here = online.get(folder, {})
        if name not in here:
            missing.append(f"{ref}: linked PDF not found on the site (pages link to it)")
        elif here[name] is not None and here[name] != os.path.getsize(os.path.join(root, ref)):
            warns.append(f"{ref}: the site copy differs in size from the PDF that was converted (page links may point at different content)")
    if not any(v is not None for v in level.values()):
        warns.append("the online listing has no 'level' values, so check-in was NOT verified: list with $select=name,size,file,publication")
    ok = not missing and not size_diff and not not_published
    rep = {"status": "PASS" if ok else "FAIL", "checked": checked, "missing": missing, "size_mismatch": size_diff,
           "not_checked_in": not_published[:50], "not_checked_in_count": len(not_published), "warnings": warns}
    with open(os.path.join(root, "publish-verify.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2)
    print(json.dumps(rep, indent=2))
    sys.exit(0 if ok else 2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check").set_defaults(fn=cmd_check)
    p = sub.add_parser("plan")
    p.add_argument("pdf")
    p.add_argument("--work", required=True)
    p.add_argument("--title")
    p.add_argument("--max-topics", type=int, default=40, help="finest topic level is used only if it gives at most this many topics")
    p.set_defaults(fn=cmd_plan)
    b = sub.add_parser("build")
    b.add_argument("pdf")
    b.add_argument("--topics", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--title")
    b.add_argument("--format", required=True, choices=["agent-md", "html", "markdown-basic"],
                   help="agent-md = agent-optimized Markdown; html = formatted HTML site; "
                        "markdown-basic = legacy linked Markdown pages without front matter (kept for compatibility)")
    b.add_argument("--no-images", action="store_true", help="do not extract images (pages with images then get a 'not extracted' marker)")
    b.add_argument("--min-image-px", type=int, default=64, help="skip images smaller than this many source pixels on either side (default 64); also skips anything under 24 pt on the page")
    b.add_argument("--image-dpi", type=int, default=150, help="resolution for rasterized regions: vector figures and undecodable images (default 150)")
    b.add_argument("--vector-figures", action="store_true", help="also rasterize drawn (vector) figures: clusters of 6+ lines, rectangles or curves outside tables")
    b.add_argument("--no-pdf-copy", action="store_true", help="do not copy the PDF into the output folder (page links then need the PDF placed beside the pages)")
    b.add_argument("--org", default="", help="html only: organization or branch name shown in the header and footer (optional)")
    b.add_argument("--doc-date", default="", help="html only: document date shown in the footer, e.g. 'September 2026' (optional)")
    b.set_defaults(fn=cmd_build)
    u = sub.add_parser("publish", help="split an HTML build into the SharePoint layout: .html to Site Pages, everything else to Site Assets")
    u.add_argument("build", help="finished html build folder (status PASS)")
    u.add_argument("--site-root", required=True, help="local folder for the site mirror (created; a numeric suffix is added if it is not empty)")
    u.add_argument("--folder", default="", help="ASK THE USER. Folder used in BOTH libraries, e.g. Manuals/CEIS -> SitePages/Manuals/CEIS and SiteAssets/Manuals/CEIS")
    u.add_argument("--pages-library", default="SitePages", help="library for the .html pages (default SitePages)")
    u.add_argument("--assets-library", default="SiteAssets", help="library for css, images and reports (default SiteAssets)")
    u.add_argument("--pages-path", default="", help="advanced: full site-relative pages folder; overrides --pages-library/--folder")
    u.add_argument("--assets-path", default="", help="advanced: full site-relative assets folder; overrides --assets-library/--folder")
    u.add_argument("--design-system", default="", help="ASK THE USER. Site-relative folder of a shared design system to reuse, e.g. SiteAssets/bc-gov-design-system: pages link its tokens css, fonts and logo, and the manual styling is published once there as manuals.css")
    u.add_argument("--no-design-system", action="store_true", help="no shared design system: styles are embedded in every page")
    u.add_argument("--ds-tokens", default="colors_and_type.css", help="tokens/fonts stylesheet inside --design-system (default colors_and_type.css; '' to skip)")
    u.add_argument("--ds-logo", default="icons/bc-logo.png", help="logo inside --design-system shown in the header (default icons/bc-logo.png; '' for none)")
    u.add_argument("--link-css", action="store_true", help="link style.css from Site Assets instead of embedding it in every page (embedding is the default: SharePoint's file viewer does not load linked stylesheets)")
    u.add_argument("--site-home", default="", help="optional site home link for subheader and breadcrumbs: 'Label|SitePages/TopicHome.aspx'")
    u.add_argument("--parent", action="append", default=[], help="optional parent manual link(s) for subheader and breadcrumbs (repeatable): 'Label|SitePages/Manuals/CEIS/index.html'")
    u.add_argument("--inline-toc", action="store_true", help="keep static per-page <nav class=\"toc\"> HTML instead of extracting a shared SiteAssets/<folder>/toc.js")
    u.add_argument("--include-report", action="store_true", help="also publish internal validation.html and validation.json to SharePoint (omitted by default)")
    g = u.add_mutually_exclusive_group()
    g.add_argument("--pdf-path", default="", help="ASK THE USER. Site-relative path of the source PDF ALREADY on the site, e.g. Manuals/ceis-manual.pdf (linked, not uploaded again)")
    g.add_argument("--no-site-pdf", action="store_true", help="the PDF is not on the site yet: publish the copy into the assets folder")
    u.set_defaults(fn=cmd_publish)
    v = sub.add_parser("verify", help="after uploading: check the published files against publish-plan.json")
    v.add_argument("site_root", help="the --site-root folder written by publish")
    v.add_argument("--online", required=True, help='JSON listing of the live folders: {"<library>/<folder>": [{"name","size","level"}]} (level = publication.level)')
    v.set_defaults(fn=cmd_verify)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
