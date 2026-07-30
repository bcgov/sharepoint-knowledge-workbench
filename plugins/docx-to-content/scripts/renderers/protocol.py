"""
protocol.py
============

The renderer side of the docx-to-content pipeline (Task 12; spec Section
8, "Renderer Protocol", and Section 7.3, "Renderer preconditions").

    class Renderer(Protocol):
        name: str
        supported_manifest_versions: frozenset[str]

        def render(self, package: CanonicalPackage, output_dir: Path) -> RenderResult:
            ...

`Renderer` is `typing.Protocol` (structural typing, stdlib) rather than an
ABC -- any object with the right attribute/method shape satisfies it, no
inheritance required, matching the spec's literal declaration.

This module defines only the protocol + registry + dispatch gate. It does
NOT define any concrete renderer (Task 13's `multipage_markdown.py` job);
the test suite for this module builds its own minimal fake renderer purely
to prove the protocol shape works end to end.

Structural guarantee -- "renderer code has no DOCX/raw-analysis input":
`Renderer.render`'s signature is `(self, package: CanonicalPackage,
output_dir: Path)` -- there is no parameter through which a source .docx
path, an analysis directory, or a ConversionPlan could be passed. A
renderer can only ever read what `CanonicalPackage.load()` (scripts/package.py)
already loaded and vetted. This is enforced at the signature level, not
just by convention -- see tests/unit/test_renderer_protocol.py's
`inspect.signature` assertions.

Renderer registry: a simple name -> Renderer instance mapping. The CLI's
`render` subcommand (still `NotImplementedError`-stubbed as of Task 5; to
be wired up in Task 13) will use `get_renderer(name)` to resolve the
`--renderer` argument, catching `UnknownRendererError` and mapping it to
the CLI's exit-code-4 `UsageError`.
"""

from pathlib import Path
from typing import Protocol, runtime_checkable

from contracts import RenderResult
from canonical_package import CanonicalPackage


@runtime_checkable
class Renderer(Protocol):
    """Structural protocol every renderer satisfies (spec Section 8).
    `runtime_checkable` allows `isinstance(obj, Renderer)` checks, but
    (per `typing.Protocol` semantics) only verifies the *names* of
    `name`, `supported_manifest_versions`, and `render` exist -- not their
    types or signatures. Signature conformance is proven separately via
    `inspect.signature` in the test suite."""

    name: str
    supported_manifest_versions: frozenset

    def render(self, package: CanonicalPackage, output_dir: Path) -> RenderResult:
        ...


class UnknownRendererError(Exception):
    """Raised by `RendererRegistry.get_renderer()` for a name that was
    never registered. Task 13's CLI wiring catches this and maps it to the
    CLI's exit-code-4 `UsageError`."""


class UnsupportedManifestVersionError(Exception):
    """Raised by `dispatch_render()` when the loaded package's manifest
    `schema_version` is not in the renderer's own
    `supported_manifest_versions` -- e.g. a renderer built for schema 1.0
    must not silently attempt to render a hypothetical future schema 2.0
    package."""


class RendererRegistry:
    """Name -> `Renderer` instance registry. Instantiable (rather than a
    single module-level singleton) so tests can register fake renderers
    without polluting global state shared across the test suite."""

    def __init__(self):
        self._renderers: dict = {}

    def register(self, renderer: "Renderer") -> None:
        self._renderers[renderer.name] = renderer

    def get_renderer(self, name: str) -> "Renderer":
        try:
            return self._renderers[name]
        except KeyError:
            raise UnknownRendererError(
                f"unknown renderer: {name!r} "
                f"(registered: {sorted(self._renderers)})"
            ) from None


def dispatch_render(
    renderer: "Renderer", package: "CanonicalPackage", output_dir: Path
) -> "RenderResult":
    """Check the loaded package's manifest `schema_version` against
    `renderer.supported_manifest_versions` (spec Section 8) before calling
    `renderer.render()`. Raises `UnsupportedManifestVersionError` if the
    version is not supported; never silently attempts to render it."""
    manifest_version = package.manifest.schema_version
    if manifest_version not in renderer.supported_manifest_versions:
        raise UnsupportedManifestVersionError(
            f"renderer {renderer.name!r} does not support manifest "
            f"schema_version {manifest_version!r} "
            f"(supported: {sorted(renderer.supported_manifest_versions)})"
        )
    return renderer.render(package, Path(output_dir))
