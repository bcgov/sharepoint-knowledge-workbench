#!/usr/bin/env python
"""pdf_extraction.py
===================

Purpose:
    Extracts a text-layer PDF into the same `normalized-source-document` v1 contract that
    `extract_and_normalize` produces for DOCX, so structure analysis and assembly can run unchanged.

Key Input Dependencies:
    - PyMuPDF (`fitz`)
    - heading_parsing, schema.normalized_source_document

Headings come from the PDF outline (bookmarks) when present, otherwise from a font-size/bold
heuristic (`heading_source: "inferred"`, which a human must review). Running headers/footers
(lines repeated on many pages) are dropped, images are written to `raw/media/`, and the page each
heading starts on is returned as `heading_pages` so later stages can cite source pages.

Scope: text, headings, images. Tables, hyperlinks and image text are separate extraction steps.
Scanned PDFs (no text layer) are reported via `defect_signals.no_text_layer`; they need OCR first.

Function Index:
    - extract_pdf_and_normalize(source, output_dir) -> dict

Key Functions Index:
    - _noise_lines()
    - _page_lines()
    - _paragraphs()
    - _extract_images()
    - _infer_outline()
    - _outline()
    - _build_markdown()
    - extract_pdf_and_normalize()"""

import hashlib
import re
import sys
from collections import Counter
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import dependencies  # noqa: E402
from heading_parsing import (  # noqa: E402
    _counts_by_level,
    _image_stats,
    _repeated_heading_texts,
    _repeated_paths,
    compute_statistics,
    detect_defect_signals,
    detect_raw_toc,
    parse_headings,
)
from schema.normalized_source_document import validate as validate_normalized_source_document  # noqa: E402

_BULLET = re.compile(r"^\s*[\u2022\u00b7\u25aa\u25cf]\s*")
_NUMBERED = re.compile(r"^\s*(\d+|[a-z])[.)]\s+")
_WEB_IMAGE_EXT = {"png", "jpg", "jpeg", "gif", "webp", "bmp"}


def _fitz():
    try:
        import fitz
    except ImportError as exc:
        raise dependencies.MissingDependencyError(
            "pymupdf", "PyMuPDF is required for PDF extraction: pip install pymupdf"
        ) from exc
    return fitz


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _noise_lines(doc) -> set:
    """Lines (digits masked) that recur on at least half the pages: running headers/footers."""
    counts = Counter()
    for page in doc:
        counts.update({re.sub(r"\d+", "#", ln.strip()) for ln in page.get_text().splitlines() if ln.strip()})
    threshold = max(3, int(len(doc) * 0.5))
    return {k for k, v in counts.items() if v >= threshold and len(k) < 120}


def _page_lines(page, noise: set) -> list:
    out = []
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block["lines"]:
            text = "".join(s["text"] for s in line["spans"]).strip()
            if text and re.sub(r"\d+", "#", text) not in noise:
                out.append((text, line["bbox"][0], line["bbox"][1]))
    return out


def _paragraphs(lines: list) -> list:
    """Join wrapped lines into paragraphs (split on larger-than-typical y gaps); bullets and numbered lines stay separate."""
    base = min((x for _, x, _ in lines), default=0)
    gaps = sorted(b[2] - a[2] for a, b in zip(lines, lines[1:]) if b[2] > a[2])
    typical = gaps[len(gaps) // 2] if gaps else 0
    parts, prev_y = [], None
    for text, x, y in lines:
        bullet = _BULLET.match(text)
        if bullet or _NUMBERED.match(text):
            indent = "  " * max(0, int((x - base) // 18))
            parts.append(("li", f"{indent}- {text[bullet.end():]}" if bullet else f"{indent}{text}"))
        elif parts and not (prev_y is not None and typical and parts[-1][0] == "p" and typical * 1.4 < y - prev_y < 5000):
            kind, prev = parts[-1]
            parts[-1] = (kind, prev + ("" if prev.endswith("-") else " ") + text)
        else:
            parts.append(("p", text))
        prev_y = y
    return parts


def _extract_images(doc, media_dir: Path, warnings: list) -> dict:
    """Write meaningful images to media_dir; skip icons and decorations repeated on many pages. Returns {page: [(name, y)]}."""
    fitz = _fitz()
    placements = Counter()
    for page in doc:
        for info in page.get_images(full=True):
            placements[info[0]] += 1
    repeat_limit = max(4, int(len(doc) * 0.3))
    result = {}
    for pno, page in enumerate(doc, 1):
        for i, info in enumerate(page.get_images(full=True), 1):
            xref = info[0]
            rects = page.get_image_rects(xref)
            if not rects or rects[0].width < 20 or rects[0].height < 20 or placements[xref] >= repeat_limit:
                continue
            try:
                data = doc.extract_image(xref)
                ext, blob = data["ext"].lower(), data["image"]
                if ext not in _WEB_IMAGE_EXT:
                    pix = fitz.Pixmap(doc, xref)
                    if pix.n - pix.alpha >= 4:
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    ext, blob = "png", pix.tobytes("png")
                name = f"page{pno:03d}_img{i:03d}.{ext}"
                media_dir.mkdir(parents=True, exist_ok=True)
                (media_dir / name).write_bytes(blob)
                result.setdefault(pno, []).append((name, rects[0].y0))
            except Exception as exc:  # one bad image must not fail the document
                warnings.append(f"image page {pno} xref {xref} not extracted: {str(exc)[:60]}")
    return result


def _infer_outline(doc, noise: set) -> list:
    """Heading outline [(level, title, page)] from font size/bold; [] when unconvincing. Levels capped at 3."""
    sizes, lines = Counter(), []
    for pno, page in enumerate(doc, 1):
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue
            for line in block["lines"]:
                spans = [s for s in line["spans"] if s["text"].strip()]
                text = "".join(s["text"] for s in line["spans"]).strip()
                if not spans or re.sub(r"\d+", "#", text) in noise:
                    continue
                size = round(max(s["size"] for s in spans) * 2) / 2
                bold = all((s["flags"] & 16) or "bold" in s["font"].lower() for s in spans)
                sizes[size] += len(text)
                lines.append((pno, text, size, bold, line["bbox"][1]))
    if not sizes:
        return []
    body = sizes.most_common(1)[0][0]
    cands = []
    for pno, text, size, bold, y in lines:
        if not 3 <= len(text) <= 100 or _BULLET.match(text) or _NUMBERED.match(text) or text.endswith((".", ",", ";", ":")):
            continue
        if size >= body + 1 or (bold and size >= body and len(text) <= 80):
            key = (size, 0) if size >= body + 1 else (body, -1)
            if cands and cands[-1]["pno"] == pno and cands[-1]["key"] == key and 0 < y - cands[-1]["y"] < size * 1.8:
                cands[-1]["text"] += " " + text
                cands[-1]["y"] = y
            else:
                cands.append({"pno": pno, "text": text, "key": key, "y": y})
    keys = sorted({c["key"] for c in cands}, key=lambda k: (-k[0], -k[1]))
    level = {k: min(3, i + 1) for i, k in enumerate(keys)}
    outline = [(level[c["key"]], c["text"], c["pno"]) for c in cands]
    if sum(1 for lv, _, _ in outline if lv == min(level.values())) < 2 or len(outline) > 150:
        return []
    return outline


def _outline(doc, noise: set):
    """(outline, heading_source) where heading_source is 'outline', 'inferred' or 'none'."""
    toc = [(lv, t.strip(), max(1, pg)) for lv, t, pg in doc.get_toc() if t.strip()]
    if toc:
        return toc, "outline"
    inferred = _infer_outline(doc, noise)
    return (inferred, "inferred") if inferred else ([], "none")


def _toc_like(page) -> bool:
    """True for a contents listing page: many ending-in-page-number lines."""
    lines = [ln.strip() for ln in page.get_text().splitlines() if ln.strip()]
    return len(lines) >= 8 and sum(1 for ln in lines if re.search(r"\s\d+$|\.{3,}", ln)) >= 0.4 * len(lines)


def _build_markdown(doc, outline: list, noise: set, images: dict, warnings: list):
    """Return (markdown_text, heading_pages). Outline headings are matched to page lines in order."""
    out, heading_pages, cursor, skipped, pending = [], [], 0, [], []

    def flush():
        nonlocal pending
        out.extend(text for _, text in _paragraphs(pending))
        pending = []

    for pno in range(1, len(doc) + 1):
        page = doc[pno - 1]
        if outline and pno < outline[0][2] and _toc_like(page):
            skipped.append(pno)
            continue
        while cursor < len(outline) and outline[cursor][2] < pno:
            warnings.append(f"outline heading not found on page {outline[cursor][2]}: {outline[cursor][1][:50]}")
            cursor += 1
        # y is offset per page so paragraph-gap logic never spans a page break
        entries = [("line", t, x, y + pno * 10000) for t, x, y in _page_lines(page, noise)]
        entries += [("img", n, 0, y + pno * 10000) for n, y in images.get(pno, [])]
        entries.sort(key=lambda e: e[3])
        i = 0
        while i < len(entries):
            kind, text, x, y = entries[i]
            if kind == "img":
                flush()
                out.append(f"![{Path(text).stem}](media/{text})")
                i += 1
                continue
            matched = None
            if cursor < len(outline) and outline[cursor][2] == pno:
                target, acc = _norm(outline[cursor][1]), ""
                for j in range(i, min(i + 4, len(entries))):
                    if entries[j][0] != "line":
                        break
                    acc = (acc + " " + entries[j][1]).strip()
                    if _norm(acc) == target:
                        matched = j
                        break
            if matched is not None:
                flush()
                level, title, _ = outline[cursor]
                out.append("#" * min(6, level) + " " + title)
                heading_pages.append(pno)
                cursor += 1
                i = matched + 1
                continue
            pending.append((text, x, y))
            i += 1
    flush()
    if skipped:
        warnings.append(f"contents pages not converted: {skipped}")
    for _, title, page in outline[cursor:]:
        warnings.append(f"outline heading not found on page {page}: {title[:50]}")
    return "\n\n".join(out) + "\n", heading_pages


def extract_pdf_and_normalize(source: Path, output_dir: Path) -> dict:
    """Extract a text-layer `source` PDF into `output_dir/raw/` (`extracted.md` + `media/`) and return a
    `normalized-source-document` v1 dict, plus PDF-only fields: `source_format`, `page_count`,
    `heading_source`, `heading_pages` (parallel to `headings`, omitted if the counts disagree) and `warnings`.

    Raises FileNotFoundError if `source` does not exist and `dependencies.MissingDependencyError`
    if PyMuPDF is not installed.
    """
    source, output_dir = Path(source), Path(output_dir)
    if not source.is_file():
        raise FileNotFoundError(f"source file not found: {source}")
    fitz = _fitz()

    raw_dir = output_dir / "raw"
    media_dir = raw_dir / "media"
    media_dir.mkdir(parents=True, exist_ok=True)
    warnings = []

    with fitz.open(source) as doc:
        page_count = len(doc)
        noise = _noise_lines(doc)
        outline, heading_source = _outline(doc, noise)
        images = _extract_images(doc, media_dir, warnings)
        markdown_text, heading_pages = _build_markdown(doc, outline, noise, images, warnings)
        no_text_layer = not any(page.get_text().strip() for page in doc)

    (raw_dir / "extracted.md").write_text(markdown_text, encoding="utf-8")
    media_files = sorted(str(p.relative_to(media_dir).as_posix()) for p in media_dir.rglob("*") if p.is_file())
    headings = parse_headings(markdown_text)

    defects = detect_defect_signals(markdown_text)
    defects["no_text_layer"] = no_text_layer
    normalized = {
        "schema_version": "v1",
        "source_content_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "markdown_text": markdown_text,
        "media_files": media_files,
        "source_path": str(source),
        "source_size_bytes": source.stat().st_size,
        "dependencies": {"pymupdf": {"available": True, "version": fitz.__doc__.split(":")[0], "path": None}},
        "headings": headings,
        "heading_counts_by_level": _counts_by_level(headings),
        "repeated_heading_texts": _repeated_heading_texts(headings),
        "repeated_heading_paths": [list(p) for p in _repeated_paths(headings).keys()],
        "images": _image_stats(media_dir),
        "raw_toc_detected": detect_raw_toc(markdown_text),
        "defect_signals": defects,
        "statistics": compute_statistics(markdown_text),
        "source_format": "pdf",
        "page_count": page_count,
        "heading_source": heading_source,
        "warnings": warnings,
    }
    if len(heading_pages) == len(headings):
        normalized["heading_pages"] = heading_pages
    validate_normalized_source_document(normalized)
    return normalized
