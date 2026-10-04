"""
webpart_code_analysis.py

Purpose:
    Groups and classifies the code payloads carried by classic Content Editor / Script
    Editor web parts, so that N deployed instances collapse into a small number of
    distinct functional groups, each with a modernization recommendation.

    Read-only: reads an already-collected web part content export from the local
    filesystem and writes report artifacts to a caller-specified output directory. No
    SharePoint tenant I/O.

Layer: plugins/sharepoint-site-assessment -- analysis

Key Input Dependencies:
    - A web part content export: JSON array of
      { PageUrl, WebPartId, WebPartTitle, Content }.
    - Optional: a site knowledge base JSON file (see `KnowledgeBase`). The shipped
      default is deliberately EMPTY -- all site-specific helper-script meanings and
      business-logic interpretations are caller-supplied data, never built in. Each
      `inlineLogicRules` entry may also carry `businessIntent`/`spfxAssessment`
      strings; without them, those two output fields honestly report "requires
      manual review" rather than guessing.

Narrative assessment fields (per group, in addition to summary/modernEquivalent/
effort): `businessIntent`, `enforcementLevel`, `spfxAssessment`. Categories with a
structurally unambiguous answer (Empty/TextOnly) get a fixed generic value since
that's genuinely true regardless of site; everything else is computed from
caller-supplied rules or reported as an honest gap -- never asserted as a fixed
conclusion the way a prior source implementation's report generator did (see
`generate-sharepoint-discovery-report-set.ps1`'s own header for that precedent).

Provenance:
    Extracted from the originating SharePoint migration repository's web-part code
    analysis script at the pinned source commit. The source's
    hardcoded ~30-entry helper-script table and its named business-rule heuristics were
    site-specific knowledge; they are removed here and replaced by the caller-supplied
    `KnowledgeBase`. See
    docs/reports/phase-9-reusable-sharepoint-plugin-extraction/provenance.md.
"""

from __future__ import annotations

import csv
import io
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from discovery_inputs import DiscoveryOutcome, DiscoveryStatus, load_json_input, require_output_dir

DOMAIN = "web-parts"

# -- Content extraction patterns ----------------------------------------------

SCRIPT_SRC_RE = re.compile(r'<script[^>]*\bsrc\s*=\s*"([^"]+)"[^>]*>', re.IGNORECASE)
STYLE_RE = re.compile(r"(?s)<style[^>]*>(.*?)</style(?:\s+[^>]*)?\s*>", re.IGNORECASE)
INLINE_SCRIPT_RE = re.compile(
    r"(?s)<script(?![^>]*\bsrc\s*=)[^>]*>(.*?)</script(?:\s+[^>]*)?\s*>", re.IGNORECASE
)
# Some classic web parts stash their real logic inside a hidden (display:none)
# <textarea> rather than a literal <script> tag, to survive the rich text editor's
# script stripping. Without this, that logic is invisible to classification and the web
# part is misread as a trivial static banner.
HIDDEN_TEXTAREA_RE = re.compile(
    r'(?s)<textarea[^>]*\bstyle\s*=\s*"[^"]*display\s*:\s*none[^"]*"[^>]*>(.*?)'
    r"</textarea(?:\s+[^>]*)?\s*>",
    re.IGNORECASE,
)
TEXT_STRIP_RE = re.compile(r"<[^>]+>")
NBSP_RE = re.compile(r"&#160;|&nbsp;|​")


# -- Caller-supplied site knowledge -------------------------------------------


@dataclass(frozen=True)
class InlineLogicRule:
    """Maps a recognisable inline-script fingerprint to a reviewed interpretation."""

    match: tuple[str, ...]
    summary: str
    modern_equivalent: str
    effort: str
    business_intent: str = "Unknown -- requires manual review to confirm business purpose."
    spfx_assessment: str = "Unknown -- requires manual review to confirm whether SPFx is needed."

    def matches(self, script: str) -> bool:
        return all(token in script for token in self.match)


@dataclass(frozen=True)
class KnowledgeBase:
    """
    Optional, caller-supplied interpretation data for one specific site.

    This plugin ships an EMPTY knowledge base on purpose: which helper script does what,
    and what a given inline script means for a business process, is site knowledge, not
    generic SharePoint knowledge. With an empty knowledge base the analyser still
    classifies and groups every web part -- it simply reports unrecognised code as
    requiring manual review instead of guessing.
    """

    helper_summaries: dict[str, str] = field(default_factory=dict)
    inline_logic_rules: tuple[InlineLogicRule, ...] = ()

    @classmethod
    def from_file(cls, path: str | Path) -> "KnowledgeBase":
        """Load a knowledge base JSON file. Raises FileNotFoundError if absent."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeBase":
        rules = tuple(
            InlineLogicRule(
                match=tuple(entry["match"]),
                summary=entry["summary"],
                modern_equivalent=entry.get("modernEquivalent", "Manual review required"),
                effort=entry.get("effort", "Unknown"),
                business_intent=entry.get(
                    "businessIntent",
                    "Unknown -- requires manual review to confirm business purpose.",
                ),
                spfx_assessment=entry.get(
                    "spfxAssessment",
                    "Unknown -- requires manual review to confirm whether SPFx is needed.",
                ),
            )
            for entry in data.get("inlineLogicRules", [])
        )
        return cls(helper_summaries=dict(data.get("helperSummaries", {})), inline_logic_rules=rules)


DEFAULT_KNOWLEDGE_BASE = KnowledgeBase()


# -- Content decomposition ----------------------------------------------------


def extract_script_srcs(content: str) -> list[str]:
    """Return the filenames (not full paths) referenced by `<script src="...">`."""
    return [m.group(1).rsplit("/", 1)[-1] for m in SCRIPT_SRC_RE.finditer(content or "")]


def extract_inline_script(content: str) -> str:
    """Concatenate inline `<script>` bodies plus logic hidden in display:none textareas."""
    parts = [m.group(1).strip() for m in INLINE_SCRIPT_RE.finditer(content or "") if m.group(1).strip()]
    parts += [m.group(1).strip() for m in HIDDEN_TEXTAREA_RE.finditer(content or "") if m.group(1).strip()]
    return "\n".join(parts)


def extract_style(content: str) -> str:
    return "\n".join(m.group(1).strip() for m in STYLE_RE.finditer(content or "") if m.group(1).strip())


def strip_to_text(content: str) -> str:
    """Strip code and markup to see whether anything but whitespace remains."""
    stripped = INLINE_SCRIPT_RE.sub("", content or "")
    stripped = HIDDEN_TEXTAREA_RE.sub("", stripped)
    stripped = SCRIPT_SRC_RE.sub("", stripped)
    stripped = STYLE_RE.sub("", stripped)
    return NBSP_RE.sub("", TEXT_STRIP_RE.sub("", stripped)).strip()


def _is_library(filename: str) -> bool:
    """A third-party library reference is a dependency, not functional intent."""
    return filename.lower().startswith("jquery")


# -- Classification -----------------------------------------------------------


def classify(entry: dict, knowledge: KnowledgeBase = DEFAULT_KNOWLEDGE_BASE) -> dict:
    """
    Classify a single web part instance.

    Returns `signature` (used to group instances that do the same thing), `category`
    (Empty | TextOnly | ExternalHelpersOnly | InlineLogic | ScriptEditorMissing), and
    the decomposed content parts.
    """
    content = entry.get("Content") or ""
    title = entry.get("WebPartTitle", "")

    if not content.strip():
        if "script editor" in title.strip().lower():
            return {
                "category": "ScriptEditorMissing",
                "signature": "SCRIPT_EDITOR_MISSING",
                "external_srcs": [],
                "inline_script": "",
                "style": "",
                "text_content": "",
            }
        return {
            "category": "Empty",
            "signature": "EMPTY",
            "external_srcs": [],
            "inline_script": "",
            "style": "",
            "text_content": "",
        }

    external_srcs = sorted(set(extract_script_srcs(content)))
    inline_script = extract_inline_script(content)
    style = extract_style(content)
    text_content = strip_to_text(content)
    custom_srcs = [s for s in external_srcs if not _is_library(s)]

    if inline_script:
        category = "InlineLogic"
        # Normalise before signing: the same logic is often mangled differently by the
        # rich text editor across page saves.
        norm = re.sub(r'<span[^>]*class="ms-rtegenerate-skip"[^>]*>|</span(?:\s+[^>]*)?\s*>', "", inline_script)
        norm = re.sub(r'<a[^>]*class="ms-rtegenerate-skip"[^>]*>.*?</a(?:\s+[^>]*)?\s*>', "", norm, flags=re.DOTALL)
        norm = re.sub(r"\s+", " ", norm).strip()
        # A content hash, not Python's salted hash(), so signatures are reproducible
        # across processes (see test_grouping_signatures_are_stable_across_runs).
        import hashlib

        signature = "INLINE::" + hashlib.sha256(norm.encode("utf-8")).hexdigest()[:8]
    elif custom_srcs:
        category = "ExternalHelpersOnly"
        signature = "HELPERS::" + "+".join(custom_srcs)
    else:
        category = "TextOnly"
        signature = _text_pattern_signature(content.lower())

    return {
        "category": category,
        "signature": signature,
        "external_srcs": external_srcs,
        "inline_script": inline_script,
        "style": style,
        "text_content": text_content,
    }


def _text_pattern_signature(content_lower: str) -> str:
    """
    Cluster code-free web parts by structural markup pattern, so that visually similar
    content collapses into one reviewable group. Purely structural -- no site vocabulary.
    """
    accordions = len(re.findall(r'class=["\']panel-group["\']|id=["\']accordion', content_lower))
    if accordions > 1 or ("panel-group" in content_lower and content_lower.count("panel-heading") > 3):
        return "PATTERN::MultiAccordionPanels"
    if accordions == 1 or "panel-collapse" in content_lower or 'data-toggle="collapse"' in content_lower:
        return "PATTERN::SingleAccordionPanel"
    if "<table" in content_lower and "<img" in content_lower:
        return "PATTERN::TableWithImages"
    if "<img" in content_lower and "<table" not in content_lower:
        return "PATTERN::ImageBanner"
    if re.search(r"\.(pdf|docx?|xlsx?|pptx?)\b", content_lower) and (
        "<ul" in content_lower or "<table" in content_lower
    ):
        return "PATTERN::DocumentLinkList"
    if "mailto:" in content_lower:
        return "PATTERN::ContactBox"
    return "PATTERN::RichTextBanner"


# -- Group interpretation -----------------------------------------------------


def summarize_group(members: list[dict], knowledge: KnowledgeBase) -> str:
    """One-paragraph, plain-English description of what a group's code does."""
    classification = members[0]["classification"]
    category = classification["category"]

    if category == "ScriptEditorMissing":
        return (
            "Script Editor web part whose content could not be retrieved -- the web part id no "
            "longer resolves on the page. Re-run the collector to obtain the current id, then "
            "re-extract, before this can be classified."
        )
    if category == "Empty":
        return "Empty or hidden placeholder web part -- no content, no functional impact."
    if category == "TextOnly":
        sample = classification["text_content"][:200]
        return f'Static rich-text content or banner. Sample: "{sample}"'

    custom_srcs = [s for s in classification["external_srcs"] if not _is_library(s)]

    if category == "ExternalHelpersOnly":
        parts = [
            f"**{s}** -- {knowledge.helper_summaries.get(s, 'unrecognised helper; inspect the source file directly')}"
            for s in custom_srcs
        ]
        return "Loads external helper script(s), no additional inline logic: " + "; ".join(parts)

    if category == "InlineLogic":
        script = classification["inline_script"]
        helper_note = ""
        if custom_srcs:
            helper_note = " Also loads: " + ", ".join(
                f"{s} ({knowledge.helper_summaries.get(s, 'unrecognised')})" for s in custom_srcs
            )
        for rule in knowledge.inline_logic_rules:
            if rule.matches(script):
                return rule.summary + helper_note
        return (
            f"Custom inline JavaScript ({len(script)} chars) with unrecognised intent -- read the "
            "extracted source directly to confirm what it does." + helper_note
        )

    return "Unclassified."


def assess_group(category: str, inline_script: str, knowledge: KnowledgeBase) -> dict:
    """
    Return the narrative assessment dimensions for a group: business intent, actual
    enforcement level, and an SPFx-needed assessment. Only categories with a
    structurally unambiguous answer (Empty/TextOnly -- display-only content, no
    logic) get a fixed generic answer; everything else is genuinely computed from
    caller-supplied rules or reported as an honest "requires manual review" gap,
    never asserted regardless of the underlying content.
    """
    if category == "Empty":
        return {
            "businessIntent": "None -- no content or functional impact.",
            "enforcementLevel": "None.",
            "spfxAssessment": "Not required -- nothing to migrate.",
        }
    if category == "ScriptEditorMissing":
        return {
            "businessIntent": "Unknown -- content not retrievable (stale web part id).",
            "enforcementLevel": "Unknown.",
            "spfxAssessment": "Unknown -- re-extract before assessing.",
        }
    if category == "TextOnly":
        return {
            "businessIntent": "Provide information, guidance, or links to site visitors.",
            "enforcementLevel": "Informational / display only -- no logic executes.",
            "spfxAssessment": "Not required -- a modern Text web part is a 100% native OOB replacement.",
        }
    if category == "ExternalHelpersOnly":
        return {
            "businessIntent": (
                "Unknown -- requires manual review of the referenced helper script(s) "
                "to confirm business purpose."
            ),
            "enforcementLevel": "Client-side DOM manipulation (hide/show/rename UI elements).",
            "spfxAssessment": (
                "Conditional -- often replaceable with modern list view column/row "
                "formatting (JSON, no code); an SPFx application customizer is only "
                "needed if the effect genuinely can't be expressed that way."
            ),
        }
    if category == "InlineLogic":
        for rule in knowledge.inline_logic_rules:
            if rule.matches(inline_script):
                return {
                    "businessIntent": rule.business_intent,
                    "enforcementLevel": "Client-side script execution on page load.",
                    "spfxAssessment": rule.spfx_assessment,
                }
        return {
            "businessIntent": "Unknown -- requires manual review to confirm business purpose.",
            "enforcementLevel": "Client-side script execution on page load.",
            "spfxAssessment": "Unknown -- requires manual review to confirm whether SPFx is needed.",
        }
    return {
        "businessIntent": "Unknown.",
        "enforcementLevel": "Unknown.",
        "spfxAssessment": "Unknown.",
    }


def recommend(category: str, inline_script: str, knowledge: KnowledgeBase) -> tuple[str, str]:
    """Return (modern_equivalent, effort) for a group."""
    if category == "Empty":
        return "None needed -- do not migrate.", "None"
    if category == "ScriptEditorMissing":
        return "Unknown -- re-extract with the current web part id before assessing.", "Unknown"
    if category == "TextOnly":
        return "Modern Text web part -- direct copy-paste, no code.", "Trivial"
    if category == "ExternalHelpersOnly":
        return (
            "No direct modern web part equivalent for arbitrary DOM manipulation. Recreate the "
            "effect with modern list view column/row formatting (JSON, no script) where possible; "
            "otherwise a small SPFx application customizer.",
            "Low-Medium",
        )
    if category == "InlineLogic":
        for rule in knowledge.inline_logic_rules:
            if rule.matches(inline_script):
                return rule.modern_equivalent, rule.effort
        return (
            "Custom inline JavaScript with unrecognised intent -- read the source and decide "
            "between list view column/row formatting (JSON, no code) and an SPFx application "
            "customizer or command set.",
            "Medium-High",
        )
    return "Review manually.", "Unknown"


CATEGORY_LABELS = {
    "Empty": "Empty / hidden placeholder",
    "TextOnly": "Static rich-text content (no code)",
    "ExternalHelpersOnly": "External helper script(s), no additional inline logic",
    "InlineLogic": "Custom inline JavaScript logic",
    "ScriptEditorMissing": "Script Editor -- content not retrievable (stale web part id)",
}


# -- Analysis -----------------------------------------------------------------


def analyse(entries: list[dict], knowledge: KnowledgeBase = DEFAULT_KNOWLEDGE_BASE) -> dict:
    """Classify every web part instance and collapse them into functional groups."""
    for entry in entries:
        entry["classification"] = classify(entry, knowledge)

    grouped: dict[str, list[dict]] = defaultdict(list)
    for entry in entries:
        grouped[entry["classification"]["signature"]].append(entry)

    groups = []
    for signature, members in grouped.items():
        category = members[0]["classification"]["category"]
        custom_srcs = sorted(
            {
                s
                for m in members
                for s in m["classification"]["external_srcs"]
                if not _is_library(s)
            }
        )
        inline_script = members[0]["classification"].get("inline_script", "")
        modern_equivalent, effort = recommend(category, inline_script, knowledge)
        assessment = assess_group(category, inline_script, knowledge)
        groups.append(
            {
                "signature": signature,
                "category": category,
                "instanceCount": len(members),
                "sampleContent": members[0].get("Content", ""),
                "pages": sorted({m.get("PageUrl", "") for m in members}),
                "pagePartPairs": [[m.get("PageUrl", ""), m.get("WebPartId", "")] for m in members],
                "webPartTitles": sorted({m.get("WebPartTitle", "") for m in members}),
                "externalScripts": custom_srcs,
                "usesLibrary": any(
                    _is_library(s) for m in members for s in m["classification"]["external_srcs"]
                ),
                "summary": summarize_group(members, knowledge),
                "modernEquivalent": modern_equivalent,
                "effort": effort,
                "businessIntent": assessment["businessIntent"],
                "enforcementLevel": assessment["enforcementLevel"],
                "spfxAssessment": assessment["spfxAssessment"],
            }
        )

    groups.sort(key=lambda g: (-g["instanceCount"], g["category"], g["signature"]))

    by_category: dict[str, int] = defaultdict(int)
    for group in groups:
        by_category[group["category"]] += group["instanceCount"]

    return {
        "generated": str(date.today()),
        "groups": groups,
        "stats": {
            "totalWebParts": len(entries),
            "uniqueGroups": len(groups),
            "byCategory": dict(by_category),
        },
    }


def generate_instance_csv(entries: list[dict], plan: dict) -> str:
    """One row per web part instance -- the per-instance audit trail, no deduplication."""
    groups_by_signature = {g["signature"]: g for g in plan["groups"]}
    # lineterminator='\n': csv's default '\r\n' combined with Path.write_text()'s own
    # newline translation on Windows doubles up to '\r\r\n' and corrupts row boundaries.
    buf = io.StringIO(newline="")
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(
        [
            "PageUrl", "WebPartId", "WebPartTitle", "Category", "GroupSignature",
            "ExternalScripts", "UsesLibrary", "Summary", "ModernEquivalent", "Effort",
        ]
    )
    for entry in entries:
        classification = entry["classification"]
        group = groups_by_signature.get(classification["signature"], {})
        writer.writerow(
            [
                entry.get("PageUrl", ""),
                entry.get("WebPartId", ""),
                entry.get("WebPartTitle", ""),
                classification["category"],
                classification["signature"],
                ", ".join(classification.get("external_srcs", [])),
                any(_is_library(s) for s in classification.get("external_srcs", [])),
                group.get("summary", ""),
                group.get("modernEquivalent", ""),
                group.get("effort", ""),
            ]
        )
    return buf.getvalue()


def generate_report(plan: dict) -> str:
    """Render the grouped analysis as a reviewer-facing Markdown report."""
    stats = plan["stats"]
    lines = [
        "# Web Part Code Analysis -- Unique Groups & Modernization Recommendations",
        "",
        f"> **Generated:** {plan['generated']}  ",
        f"> **Total web part instances analysed:** {stats['totalWebParts']}  ",
        f"> **Unique functional groups found:** {stats['uniqueGroups']}",
        "",
        "---",
        "",
        "## 1. Summary by Category",
        "",
        "| Category | Instances |",
        "|:---|---:|",
    ]
    for category, label in CATEGORY_LABELS.items():
        count = stats["byCategory"].get(category, 0)
        if count:
            lines.append(f"| {label} | {count} |")

    lines += [
        "",
        "---",
        "",
        "## 2. Unique Groups (most common first)",
        "",
        "Each group represents one distinct piece of functionality -- every instance in the group",
        "does the same thing, just deployed on different pages.",
        "",
    ]

    for index, group in enumerate(plan["groups"], 1):
        first_pair = (group.get("pagePartPairs") or [["", ""]])[0]
        plural = "s" if group["instanceCount"] != 1 else ""
        lines += [
            f"### Group {index}: {CATEGORY_LABELS.get(group['category'], group['category'])} "
            f"({group['instanceCount']} instance{plural})",
            "",
            f"**Representative:** `{first_pair[0]}` (web part id `{first_pair[1]}`)",
            "",
            "#### Content snippet",
            "```html",
            group.get("sampleContent", "").strip(),
            "```",
            "",
            "#### Modernization assessment",
            f"- **Observed behaviour:** {group['summary']}",
            f"- **Business intent:** {group['businessIntent']}",
            f"- **Actual enforcement level:** {group['enforcementLevel']}",
            f"- **Recommended modern replacement:** {group['modernEquivalent']}",
            f"- **SPFx assessment:** {group['spfxAssessment']}",
            f"- **Estimated effort:** {group['effort']}",
            f"- **External scripts:** {', '.join(group['externalScripts']) or 'none'}",
            "",
            "**Instances in this group:**",
            "",
            "| Page | Web Part Id |",
            "|:---|:---|",
        ]
        lines += [f"| `{pair[0]}` | `{pair[1]}` |" for pair in group.get("pagePartPairs", [])]
        lines += ["", "---", ""]

    lines += [
        "## 3. Notes",
        "",
        "- Text-only groups need no engineering -- copy the content into a modern Text web part.",
        "- External-helper-only groups usually hide or rename UI elements; most of those effects are "
        "achievable with modern list view column/row formatting rather than a script port.",
        "- Inline-logic groups need the most engineering judgement. Where this report says the intent "
        "is unrecognised, that is an honest gap: supply a knowledge base file describing the site's "
        "own scripts rather than assuming a default interpretation.",
        "",
        "*Full structured data: `webpart-code-groups.json`; per-instance audit trail: "
        "`webpart-instance-review.csv`.*",
    ]
    return "\n".join(lines)


def run(
    *,
    extract_path: str | Path,
    output_dir: str | Path,
    knowledge_base_path: str | Path | None = None,
) -> DiscoveryOutcome:
    """
    Analyse a web part content export and write the groups JSON, Markdown report, and
    per-instance CSV. Returns an honest `DiscoveryOutcome`.
    """
    loaded = load_json_input(extract_path, domain=DOMAIN)
    if not loaded.ok:
        return loaded
    if not isinstance(loaded.data, list):
        return DiscoveryOutcome.failed(
            DOMAIN,
            f"Expected a JSON array of web part records in {extract_path}, "
            f"got {type(loaded.data).__name__}.",
        )

    knowledge = DEFAULT_KNOWLEDGE_BASE
    if knowledge_base_path is not None:
        kb_loaded = load_json_input(knowledge_base_path, domain=DOMAIN)
        if not kb_loaded.ok:
            return DiscoveryOutcome.unavailable(
                DOMAIN, f"Knowledge base unavailable: {kb_loaded.detail}"
            )
        knowledge = KnowledgeBase.from_dict(kb_loaded.data)

    out_dir = require_output_dir(output_dir)
    entries = loaded.data
    plan = analyse(entries, knowledge)

    json_path = out_dir / "webpart-code-groups.json"
    json_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    md_path = out_dir / "webpart-code-analysis.md"
    md_path.write_text(generate_report(plan), encoding="utf-8")
    csv_path = out_dir / "webpart-instance-review.csv"
    csv_path.write_text(generate_instance_csv(entries, plan), encoding="utf-8", newline="")

    artifacts = (str(json_path), str(md_path), str(csv_path))
    if loaded.status is DiscoveryStatus.EMPTY:
        return DiscoveryOutcome.empty(DOMAIN, "No web parts in the export.", plan, artifacts)

    unresolved = sum(1 for g in plan["groups"] if g["category"] == "ScriptEditorMissing")
    detail = (
        f"{plan['stats']['totalWebParts']} instance(s) collapsed into "
        f"{plan['stats']['uniqueGroups']} functional group(s)."
    )
    if unresolved:
        return DiscoveryOutcome.partial(
            DOMAIN,
            detail + f" {unresolved} group(s) could not be retrieved (stale web part id).",
            plan,
            artifacts,
        )
    return DiscoveryOutcome.observed(DOMAIN, detail, plan, artifacts)
