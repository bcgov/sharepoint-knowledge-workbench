"""Trust metadata, the AI-generated notice, and provenance/staleness validation for the optional enrichment layer.

Purpose: keep deterministic extraction (authoritative) and AI-generated navigation aids (discovery only) visibly and
machine-readably distinct, and check that every generated artifact traces back to extracted source pages.

Key Input Dependencies: `raw/extracted.md` text and `page_map` from `pdf_extraction`; no model calls happen here.

Key Functions Index:
    - deterministic_metadata()
    - ai_metadata()
    - render_front_matter()
    - ai_artifact_header()
    - parse_front_matter()
    - validate_ai_artifact()
    - is_stale()
"""

import re
from pathlib import Path

AI_NOTICE_TITLE = "AI-GENERATED NAVIGATION AID"
AI_NOTICE_BODY = (
    "This content was generated to support knowledge discovery and may contain omissions, interpretation errors, "
    "or inaccurate summaries. Do not treat it as authoritative. Verify factual answers against the deterministic "
    "extracted content and the original source document."
)

# Highest to lowest authority; AI layers never override a level above them.
TRUST_HIERARCHY = (
    "original_source",
    "deterministic_extraction",
    "ai_topic_restructuring",
    "ai_indexes_and_summaries",
)

_REQUIRED_AI_KEYS = (
    "content_type", "trust_level", "authoritative", "generated_from", "source_document", "extracted_content",
    "source_sha256", "generation_model", "prompt_version", "generation_timestamp", "source_pages",
)
_LINK = re.compile(r"\]\((?!https?:|mailto:|#)([^)#\s]+)")


def deterministic_metadata(source_document: str, source_sha256: str) -> dict:
    """Metadata for authoritative extracted files."""
    return {
        "content_type": "deterministic_extraction",
        "trust_level": "authoritative_extraction",
        "authoritative": True,
        "source_document": source_document,
        "source_sha256": source_sha256,
    }


def ai_metadata(*, source_document: str, extracted_content: str, source_sha256: str, model: str,
                prompt_version: str, timestamp: str, source_pages: list, kind: str = "navigation",
                uncertain: bool = False) -> dict:
    """Metadata every AI-generated artifact must carry. `source_pages` is [first, last] (1-based, inclusive)."""
    return {
        "content_type": "ai_generated_navigation",
        "trust_level": "discovery_only",
        "authoritative": False,
        "generated_from": "deterministic_extraction",
        "artifact_kind": kind,
        "source_document": source_document,
        "extracted_content": extracted_content,
        "source_sha256": source_sha256,
        "generation_model": model,
        "prompt_version": prompt_version,
        "generation_timestamp": timestamp,
        "source_pages": list(source_pages),
        "uncertain_boundary": uncertain,
    }


def _scalar(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return "[" + ", ".join(_scalar(v) for v in value) + "]"
    if isinstance(value, (int, float)):
        return str(value)
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_front_matter(meta: dict) -> str:
    """YAML front matter limited to scalars and flat lists, so `parse_front_matter` can read it without a YAML library."""
    return "---\n" + "".join(f"{k}: {_scalar(v)}\n" for k, v in meta.items()) + "---\n"


def ai_artifact_header(meta: dict) -> str:
    """Front matter plus the visible notice; place at the top of every AI-generated file."""
    notice = f"> **{AI_NOTICE_TITLE}**\n> {AI_NOTICE_BODY}\n"
    if meta.get("uncertain_boundary"):
        notice += "> The title and boundaries of this section were inferred and are marked uncertain.\n"
    return render_front_matter(meta) + "\n" + notice + "\n"


def _parse_value(raw: str):
    raw = raw.strip()
    if raw in ("true", "false"):
        return raw == "true"
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        return [_parse_value(p) for p in re.split(r",\s*(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)", inner)] if inner else []
    if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
        return raw[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    try:
        return int(raw)
    except ValueError:
        return raw


def parse_front_matter(text: str):
    """(meta dict, body) for text written by `render_front_matter`; ({}, text) when there is none."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    meta = {}
    for line in text[4:end].splitlines():
        key, sep, value = line.partition(":")
        if sep:
            meta[key.strip()] = _parse_value(value)
    return meta, text[end + 5:]


def validate_ai_artifact(path: Path, extracted_text: str, page_count: int, current_source_sha256: str = None,
                         link_roots=()) -> list:
    """Problems found in one AI-generated file, as [{code, message}]; empty means it passes.

    Checks: front matter present and required keys set; trust flags (`discovery_only`, `authoritative: false`);
    visible notice; `source_pages` inside 1..page_count; relative links resolve; and, when
    `current_source_sha256` is given, that the artifact is not stale. `link_roots` are extra directories to resolve
    relative links against (verbatim slices keep the extraction's `media/...` links, which live beside `extracted.md`)."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    meta, body = parse_front_matter(text)
    problems = []

    def bad(code, message):
        problems.append({"code": code, "message": f"{path.name}: {message}"})

    if not meta:
        bad("missing_metadata", "no front matter")
        return problems
    for key in _REQUIRED_AI_KEYS:
        if key not in meta or meta[key] in ("", None):
            bad("missing_key", f"metadata key {key!r} is missing")
    if meta.get("content_type") != "ai_generated_navigation":
        bad("wrong_content_type", f"content_type is {meta.get('content_type')!r}")
    if meta.get("trust_level") != "discovery_only" or meta.get("authoritative") is not False:
        bad("wrong_trust", "must be trust_level discovery_only and authoritative false")
    if AI_NOTICE_TITLE not in body or AI_NOTICE_BODY not in body:
        bad("missing_notice", "the visible AI-generated notice is absent or altered")
    pages = meta.get("source_pages")
    if not (isinstance(pages, list) and len(pages) == 2 and all(isinstance(p, int) for p in pages)
            and 1 <= pages[0] <= pages[1] <= page_count):
        bad("bad_source_pages", f"source_pages {pages!r} is not [first, last] within 1..{page_count}")
    for target in _LINK.findall(body):
        if not any((root / target).exists() for root in (path.parent, *map(Path, link_roots))):
            bad("broken_link", f"link target does not exist: {target}")
    if current_source_sha256 and meta.get("source_sha256") != current_source_sha256:
        bad("stale", "generated from a different source version than the current one")
    return problems


def is_stale(generation_meta: dict, current_source_sha256: str) -> bool:
    """True when artifacts were generated from a different source version than `current_source_sha256`."""
    return generation_meta.get("source_sha256") != current_source_sha256


def is_verbatim_slice(slice_text: str, extracted_text: str, start: int, end: int) -> bool:
    """True when `slice_text` is exactly `extracted_text[start:end]`: AI-chosen topic files may only cut, never rewrite."""
    return 0 <= start < end <= len(extracted_text) and extracted_text[start:end] == slice_text
