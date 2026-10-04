"""
templates.py
=============

Shared module backing the `create-markdown-rendering-template` and
`create-sharepoint-rendering-template` skills.

These are rendering templates: Markdown document/page structure, ASPX
page structure, navigation, headings/sections, metadata placement, media
placement, links, and human-facing layout under
`assets/templates/{generic,solutions/standard-manual}/{markdown,aspx}/`.

A template is a small placeholder-driven text file plus a JSON sidecar
recording its `profile`/`format`/`schema_version` (the sidecar is what
lets `load_rendering_template` recover those without re-parsing the
template body, and what `validate-rendering-template` checks against).
Placeholders are literal `{{name}}` tokens with zero templating engine
dependencies beyond the Python standard library.

Starter templates are authored at the plugin root and packaged within
`scripts/rendering/assets/templates/...`:

    assets/templates/generic/markdown/page.template.md
    assets/templates/solutions/standard-manual/markdown/page.template.md
    assets/templates/generic/aspx/page.template.html
    assets/templates/solutions/standard-manual/aspx/page.template.html
"""

import json
from dataclasses import dataclass
from pathlib import Path

TEMPLATE_SCHEMA_VERSION = "1.0"

_THIS_DIR = Path(__file__).resolve().parent
_TEMPLATES_ROOT = _THIS_DIR / "assets" / "templates"

_PROFILE_DIRS = {
    "generic": _TEMPLATES_ROOT / "generic",
    "standard-manual": _TEMPLATES_ROOT / "solutions" / "standard-manual",
}

_FORMAT_EXTENSIONS = {
    "markdown": ("markdown", "page.template.md"),
    "aspx": ("aspx", "page.template.html"),
}

REQUIRED_PLACEHOLDERS = frozenset({"{{title}}", "{{body}}"})

# Public aliases for `template_validation.py` (or any other consumer) to
# check known profiles/formats without reaching into this module's
# internal `_PROFILE_DIRS`/`_FORMAT_EXTENSIONS` mappings.
KNOWN_PROFILES = frozenset(_PROFILE_DIRS)
KNOWN_FORMATS = frozenset(_FORMAT_EXTENSIONS)


class UnknownTemplateProfileError(Exception):
    """Raised when `profile` is not one of the plugin's known template
    profiles (`generic`, `standard-manual`)."""


class UnknownTemplateFormatError(Exception):
    """Raised when `fmt` is not one of the plugin's known rendering
    formats (`markdown`, `aspx`)."""


class MissingTemplateMetadataError(Exception):
    """Raised by `load_rendering_template` when a template file has no
    `<name>.meta.json` sidecar -- it cannot have been created by
    `create_rendering_template`, or its sidecar was deleted."""


@dataclass
class RenderingTemplate:
    schema_version: str
    profile: str
    format: str
    content: str
    path: Path

    def to_metadata_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "profile": self.profile,
            "format": self.format,
        }


def _sidecar_path(output_path: Path) -> Path:
    return output_path.with_suffix(output_path.suffix + ".meta.json")


def _starter_path(profile: str, fmt: str) -> Path:
    if profile not in _PROFILE_DIRS:
        raise UnknownTemplateProfileError(
            f"unknown template profile: {profile!r} (known: {sorted(_PROFILE_DIRS)})"
        )
    if fmt not in _FORMAT_EXTENSIONS:
        raise UnknownTemplateFormatError(
            f"unknown template format: {fmt!r} (known: {sorted(_FORMAT_EXTENSIONS)})"
        )
    subdir, filename = _FORMAT_EXTENSIONS[fmt]
    return _PROFILE_DIRS[profile] / subdir / filename


def create_rendering_template(profile: str, fmt: str, output_path: "Path | str") -> RenderingTemplate:
    """Instantiate a new rendering template file at `output_path`,
    seeded verbatim from this plugin's canonical starter for
    `(profile, fmt)`. Writes a `<output_path>.meta.json` sidecar
    alongside it recording `schema_version`/`profile`/`format`. Raises
    `UnknownTemplateProfileError`/`UnknownTemplateFormatError` for an
    unrecognized `profile`/`fmt` before touching disk."""
    output_path = Path(output_path)
    starter_path = _starter_path(profile, fmt)
    content = starter_path.read_text(encoding="utf-8")

    template = RenderingTemplate(
        schema_version=TEMPLATE_SCHEMA_VERSION,
        profile=profile,
        format=fmt,
        content=content,
        path=output_path,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)
    _sidecar_path(output_path).write_text(
        json.dumps(template.to_metadata_dict(), indent=2, sort_keys=True)
    )
    return template


def load_rendering_template(path: "Path | str") -> RenderingTemplate:
    """Load an already-created rendering template file and its
    `.meta.json` sidecar. Raises `MissingTemplateMetadataError` if the
    sidecar does not exist -- a template file without one was never
    created by `create_rendering_template` (or its sidecar was
    deleted/lost)."""
    path = Path(path)
    sidecar_path = _sidecar_path(path)
    if not sidecar_path.exists():
        raise MissingTemplateMetadataError(
            f"{path} has no metadata sidecar ({sidecar_path}) -- "
            "cannot determine its profile/format"
        )
    metadata = json.loads(sidecar_path.read_text(encoding="utf-8"))
    return RenderingTemplate(
        schema_version=metadata["schema_version"],
        profile=metadata["profile"],
        format=metadata["format"],
        content=path.read_text(encoding="utf-8"),
        path=path,
    )

