"""dependencies.py
================

Purpose:
    Dependency probing for this plugin's two external system tools: `pandoc` (always required) and `soffice`/LibreOffice (required only when a document contains legacy `.emf`/`.wmf` media that needs conversion).

Key Input Dependencies:
    - shutil
    - subprocess
    - dataclasses
    - typing

Dependency probing for this plugin's two external system tools: `pandoc`
(always required) and `soffice`/LibreOffice (required only when a document
contains legacy `.emf`/`.wmf` media that needs conversion).

Uses `shutil.which()` to locate an executable on PATH and
`subprocess.run([exe, "--version"])` to report its version — no
third-party dependency-detection libraries.

Key Functions Index:
    - MissingDependencyError.__init__()
    - _probe()
    - probe_pandoc()
    - probe_soffice()
    - require_soffice_if_needed()"""

import shutil
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class DependencyStatus:
    name: str
    available: bool
    path: Optional[str] = None
    version: Optional[str] = None


class MissingDependencyError(RuntimeError):
    """Raised when a required external tool is not available on PATH."""

    # Initialize the MissingDependencyError instance with its configured dependencies.
    def __init__(self, dependency_name: str, message: Optional[str] = None):
        """Initialize the MissingDependencyError instance with its configured dependencies."""
        self.dependency_name = dependency_name
        super().__init__(
            message
            or f"required dependency {dependency_name!r} is not available on PATH"
        )


# Run a dependency version probe and return its availability, version, and diagnostic details.
def _probe(name: str, version_flag: str = "--version") -> DependencyStatus:
    """Run a dependency version probe and return its availability, version, and diagnostic details."""
    path = shutil.which(name)
    if path is None:
        return DependencyStatus(name=name, available=False, path=None, version=None)

    version: Optional[str] = None
    try:
        result = subprocess.run(
            [path, version_flag],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        output = (result.stdout or result.stderr or "").strip()
        version = output.splitlines()[0] if output else None
    except (OSError, subprocess.SubprocessError):
        version = None

    return DependencyStatus(name=name, available=True, path=path, version=version)


# Check that Pandoc is installed and meets the configured minimum version for DOCX extraction.
def probe_pandoc() -> DependencyStatus:
    """Check that Pandoc is installed and meets the configured minimum version for DOCX extraction."""
    return _probe("pandoc")


# Check that LibreOffice is available for the configured document-conversion fallback.
def probe_soffice() -> DependencyStatus:
    """Check that LibreOffice is available for the configured document-conversion fallback."""
    return _probe("soffice")


def require_soffice_if_needed(needs_legacy_conversion: bool) -> None:
    """Raise MissingDependencyError if legacy media conversion is needed and
    soffice is not available. A no-op when needs_legacy_conversion is False.

    Document-level legacy-media detection (deciding whether
    `needs_legacy_conversion` is True for a given source) is not built yet —
    that lands in Task 6 (analyze) alongside real pandoc invocation. This
    function is the stable seam later tasks call into once that detection
    exists.
    """
    if not needs_legacy_conversion:
        return
    status = probe_soffice()
    if not status.available:
        raise MissingDependencyError(
            "soffice",
            "soffice (LibreOffice) is required to convert legacy .emf/.wmf "
            "media but was not found on PATH",
        )
