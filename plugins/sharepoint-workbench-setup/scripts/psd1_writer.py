"""Purpose:
    Render Python values as PowerShell data-file hashtables.

Key Input Dependencies:
    - Caller-provided Python dict/list/scalar values; no filesystem or SharePoint access.

psd1_writer.py
================

Minimal PowerShell hashtable (`.psd1`) text writer, shared by
`config_setup.py` (Layer 1 root connection config) and
`document_workflow.py` (Layer 1b/2 workflow and publication profiles) --
all three of this plugin's written artifacts are PowerShell hashtables,
so this is the one place that knows how to turn a Python dict into
valid `.psd1` text. Deliberately one-directional (Python -> `.psd1`
text only) -- this module never parses `.psd1` back into Python; see
`workflow_validation.py`'s own docstring for why that boundary is out
of scope for this first version.

Function Index:
    - Psd1WriteError
    - render_value
    - render_hashtable
    - render_document
"""

from typing import Any


class Psd1WriteError(Exception):
    """Raised when a value cannot be represented as `.psd1` text."""


# Render one supported Python value as its PowerShell data-file literal.
def render_value(value: Any, indent: int) -> str:
    """Render one supported Python value as its PowerShell data-file literal."""
    if isinstance(value, bool):
        return "$true" if value else "$false"
    if isinstance(value, str):
        escaped = value.replace('"', '`"')
        return f'"{escaped}"'
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, dict):
        return render_hashtable(value, indent)
    if isinstance(value, list):
        if not value:
            return "@()"
        items = ", ".join(render_value(item, indent) for item in value)
        return f"@({items})"
    if value is None:
        return '""'
    raise Psd1WriteError(f"unsupported .psd1 value type: {type(value)!r}")


# Render mapping entries as a consistently indented PowerShell hashtable.
def render_hashtable(data: dict, indent: int) -> str:
    """Render mapping entries as a consistently indented PowerShell hashtable."""
    pad = "    " * indent
    inner_pad = "    " * (indent + 1)
    lines = ["@{"]
    for key, value in data.items():
        lines.append(f"{inner_pad}{key} = {render_value(value, indent + 1)}")
    lines.append(f"{pad}}}")
    return "\n".join(lines)


def render_document(data: dict) -> str:
    """Render `data` as a complete `.psd1` file's contents (a top-level
    hashtable followed by a trailing newline)."""
    return render_hashtable(data, 0) + "\n"
