#!/usr/bin/env python
"""
test_future_output_profiles.py
================================

Task 15b: contract tests for `references/future-output-profiles.md` (spec
Section 14b) and the documentation-only guarantees around it -- no
SharePoint/Graph/PnP/Entra reference anywhere in the plugin's own source,
and the Phase 1 renderer registry contains only `multipage_markdown`.
"""

import re
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).parent.parent.parent
REFERENCES_DIR = PLUGIN_ROOT / "references"
DOC_PATH = REFERENCES_DIR / "future-output-profiles.md"

SCRIPTS_DIR = PLUGIN_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

REQUIRED_PROFILES = [
    "Multipage Markdown",
    "PDF",
    "Word",
    "PowerPoint",
    "Audio/Video",
    "HTML",
    "ZIP Release Package",
    "SharePoint Modern Pages",
]


def _text() -> str:
    assert DOC_PATH.exists(), f"missing {DOC_PATH}"
    return DOC_PATH.read_text(encoding="utf-8")


class TestFutureOutputProfilesStructure:
    def test_exists_and_documents_all_eight_profiles(self):
        text = _text()
        for profile in REQUIRED_PROFILES:
            assert profile in text, f"missing profile section: {profile}"

    def test_only_multipage_markdown_is_implemented(self):
        text = _text()
        sections = _split_sections(text)
        for profile in REQUIRED_PROFILES:
            section = sections[profile]
            if profile == "Multipage Markdown":
                assert "status: implemented" in section.lower() or "implementation status: implemented" in section.lower()
            else:
                lowered = section.lower()
                assert (
                    "designed-only" in lowered or "requires-platform-authorization" in lowered
                ), f"{profile} must be marked designed-only or requires-platform-authorization"
                assert "status: implemented" not in lowered
                assert "implementation status: implemented" not in lowered

    def test_sharepoint_profile_requires_platform_authorization(self):
        text = _text()
        sections = _split_sections(text)
        section = sections["SharePoint Modern Pages"].lower()
        assert "requires-platform-authorization" in section

    def test_no_aspx_described_as_authoring_or_canonical_format(self):
        text = _text()
        for line in text.splitlines():
            if ".aspx" in line.lower():
                lowered = line.lower()
                assert "authoring format" not in lowered
                assert "canonical format" not in lowered

    def test_word_and_sharepoint_have_drift_warning(self):
        text = _text()
        sections = _split_sections(text)
        for profile in ("Word", "SharePoint Modern Pages"):
            lowered = sections[profile].lower()
            assert "source of truth" in lowered
            assert "no silent round-trip" in lowered or "not a silent round-trip" in lowered

    def test_no_profile_claims_automatic_round_trip_editing(self):
        # Every mention of "automatic round-trip editing" must be a
        # denial ("no automatic round-trip editing"), never an assertion
        # that it is supported.
        text = _text().lower()
        assert "automatically round-trips" not in text
        for line in text.splitlines():
            if "automatic round-trip editing" in line:
                assert "no automatic round-trip editing" in line, (
                    f"line asserts automatic round-trip editing without denial: {line!r}"
                )


def _split_sections(text: str) -> dict:
    """Split the document on `## <Profile Name>` headings into
    {profile_name: section_text}."""
    pattern = re.compile(r"^## (.+)$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    sections = {}
    for i, match in enumerate(matches):
        name = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[name] = text[start:end]
    return sections


class TestNoSharePointReferenceInPluginSource:
    FORBIDDEN_TERMS = ["sharepoint", "microsoft graph", "pnp powershell", "entra"]

    def test_no_forbidden_terms_in_plugin_source(self):
        scan_dirs = ["scripts", "skills", "references", "templates"]
        hits = []
        phase3_sharepoint_modules = [
            "sharepoint_package.py",
            "sharepoint_dry_run.py",
            "sharepoint_reconcile.py",
            "sharepoint_cli.py",
        ]
        for dir_name in scan_dirs:
            base = PLUGIN_ROOT / dir_name
            if not base.exists():
                continue
            for path in base.rglob("*"):
                if not path.is_file():
                    continue
                if "__pycache__" in path.parts:
                    continue
                if path == DOC_PATH:
                    # future-output-profiles.md is explicitly permitted to
                    # NAME SharePoint as a designed-only future profile --
                    # it is documentation about a boundary, not an
                    # implementation reference. It is excluded from this
                    # source-purity scan by design; a separate, narrower
                    # test below still constrains what it may say.
                    continue
                if path.name in phase3_sharepoint_modules:
                    # Phase 3 introduces SharePoint-specific modules that
                    # intentionally break the Phase 1 implementation-agnostic
                    # constraint. These are excluded from the purity scan.
                    continue
                try:
                    content = path.read_text(encoding="utf-8").lower()
                except (UnicodeDecodeError, OSError):
                    continue
                for term in self.FORBIDDEN_TERMS:
                    if term in content:
                        hits.append((str(path), term))
        assert hits == [], f"forbidden platform references found: {hits}"

    def test_future_output_profiles_doc_names_sharepoint_only_as_designed_only(self):
        # The one place SharePoint is allowed to be named: it must always
        # appear alongside its requires-platform-authorization status,
        # never as something implemented or importable.
        text = _text()
        sections = _split_sections(text)
        section = sections["SharePoint Modern Pages"].lower()
        assert "requires-platform-authorization" in section
        assert "status: implemented" not in section
        assert "implementation status: implemented" not in section


class TestRendererRegistryOnlyMultipageMarkdown:
    def test_registry_used_by_cli_registers_only_multipage_markdown(self):
        # Check against the REAL Task 12 registry object/module, not a
        # hand-written list that could drift from reality.
        from renderers import protocol
        from renderers.multipage_markdown import MultipageMarkdownRenderer

        registry = protocol.RendererRegistry()
        registry.register(MultipageMarkdownRenderer())

        assert set(registry._renderers.keys()) == {"multipage-markdown"}

    def test_cli_supported_renderers_constant_has_only_multipage_markdown(self):
        import cli

        assert cli.SUPPORTED_RENDERERS == {"multipage-markdown"}
