"""
canonical_package.py
=====================

The read-only, renderer-side consumer of a promoted canonical-content
package (moved out of package.py during Phase 2's contract hardening).
Renderers (and anything else that only needs to READ an already-promoted
package) import from HERE, never from package.py -- package.py retains
only the producer/builder functions (build_canonical_package,
build_grouped_canonical_package), which depend on topic_grouping and other
analysis-side modules. This module depends on none of that: keeping the
two responsibilities in separate files is what makes the import-boundary
test in tests/unit/test_import_boundaries.py actually mean something --
see that test's docstring for the full rationale (a renderer that
imported `package.CanonicalPackage` transitively pulled in
`topic_grouping`, a producer/analysis concern, even though the renderer
code itself never referenced it directly).

CanonicalPackage.load() is a SECOND, independent integrity check at load
time, on top of whatever validate_canonical.py already recorded in
validation.json at convert time -- defense against the promoted package
having been tampered with or corrupted on disk since promotion.
"""

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import contracts  # noqa: E402
import dispositions  # noqa: E402
import hashing  # noqa: E402
import publication_map  # noqa: E402

# Round-3 review (GPT 5.6 blocking #4/#5, confirmed independently by Opus):
# an earlier draft of this module trusted validation.json's status without
# cross-checking its OWN lineage fields against the manifest it claims to
# describe, and loaded publication-map.json without re-enforcing any of
# the same-invariants validate_canonical.py already checked at convert
# time. Both are real post-promotion tamper surfaces: a PASS report copied
# from a different package, or a publication-map.json edited/deleted after
# promotion, would otherwise silently authorize a package that never
# actually passed those checks. load() now re-derives both, independent of
# whatever validate_canonical.py recorded -- this is the whole point of
# Layer 2 existing as a SEPARATE check from Layer 1.


class CanonicalPackageError(Exception):
    """Base class for `CanonicalPackage.load()` failures. Raised, never
    swallowed into a null/error field -- a renderer receiving a
    `CanonicalPackage` instance can assume it has already been fully
    vetted."""


class CanonicalPackageValidationError(CanonicalPackageError):
    """The package's manifest/validation.json failed schema validation, or
    its validation status is FAIL, or WARN without a disposition file that
    accounts for every warning."""


class CanonicalPackageIntegrityError(CanonicalPackageError):
    """A chunk's on-disk content no longer matches its sidecar's recorded
    `content_sha256`, or a chunk's media reference does not resolve to a
    file under `media/` -- i.e. the package was tampered with or corrupted
    on disk after promotion."""


def _media_ref_to_filename(ref: str) -> str:
    """Reverse `package.rewrite_media_and_copy`'s `../media/<quoted-name>`
    rewrite back to the plain on-disk filename under `media/`."""
    prefix = "../media/"
    name = ref[len(prefix):] if ref.startswith(prefix) else ref
    return unquote(name)


@dataclass(frozen=True)
class LoadedChunk:
    """One chunk's metadata and content, already loaded into memory and
    hash-verified by `CanonicalPackage.load()`."""

    metadata: "contracts.ChunkMetadata"
    content: str


@dataclass(frozen=True)
class CanonicalPackage:
    """A fully vetted, in-memory view of an ACCEPTED canonical-content
    package. Only ever constructed via `CanonicalPackage.load()` -- never
    built by a renderer directly."""

    manifest: "contracts.Manifest"
    validation_report: "contracts.ValidationReport"
    chunks: list  # list[LoadedChunk], in manifest order
    media_dir: Path
    package_dir: Path
    publication_map: "object" = None

    @classmethod
    def load(cls, package_dir: Path) -> "CanonicalPackage":
        """Load and fully re-validate an ACCEPTED canonical package at
        `package_dir`. Raises `CanonicalPackageError` (or a subclass) on
        any failure -- never returns a partially-valid package."""
        package_dir = Path(package_dir)

        manifest_path = package_dir / "manifest.json"
        if not manifest_path.exists():
            raise CanonicalPackageValidationError(f"{manifest_path} does not exist")
        try:
            manifest = contracts.Manifest.from_dict(json.loads(manifest_path.read_text()))
        except (ValueError, json.JSONDecodeError) as exc:
            raise CanonicalPackageValidationError(
                f"manifest.json failed schema validation: {exc}"
            ) from exc

        validation_path = package_dir / "validation.json"
        if not validation_path.exists():
            raise CanonicalPackageValidationError(f"{validation_path} does not exist")
        try:
            validation_report = contracts.ValidationReport.from_dict(
                json.loads(validation_path.read_text())
            )
        except (ValueError, json.JSONDecodeError) as exc:
            raise CanonicalPackageValidationError(
                f"validation.json failed schema validation: {exc}"
            ) from exc

        if validation_report.status == "FAIL":
            raise CanonicalPackageValidationError(
                f"{package_dir} has validation status FAIL -- not renderable"
            )
        if validation_report.status == "WARN":
            disposition_path = package_dir / "warning-disposition.json"
            check = dispositions.apply_disposition(validation_report, disposition_path)
            if not check.promotable:
                undispositioned = [dispositions.disposition_key(w) for w in check.undispositioned]
                raise CanonicalPackageValidationError(
                    f"{package_dir} has validation status WARN with "
                    f"undispositioned warnings: {undispositioned}"
                )

        # Lineage cross-check: validation.json must actually describe THIS
        # manifest, not merely have a PASS/WARN status -- a validation
        # report copied or left over from a different package must not
        # silently authorize this one.
        if validation_report.plan_id != manifest.plan_id:
            raise CanonicalPackageIntegrityError(
                f"validation.json plan_id={validation_report.plan_id!r} does "
                f"not match manifest.json plan_id={manifest.plan_id!r} -- "
                "the validation report does not describe this package"
            )
        if validation_report.source_sha256 != manifest.source.sha256:
            raise CanonicalPackageIntegrityError(
                f"validation.json source_sha256={validation_report.source_sha256!r} "
                f"does not match manifest.json source.sha256="
                f"{manifest.source.sha256!r} -- the validation report does "
                "not describe this package"
            )

        loaded_chunks = []
        for manifest_chunk in manifest.chunks:
            content_path = package_dir / manifest_chunk.content_file
            metadata_path = package_dir / manifest_chunk.metadata_file
            if not content_path.exists():
                raise CanonicalPackageIntegrityError(
                    f"chunk {manifest_chunk.chunk_id!r}: missing content file {content_path}"
                )
            if not metadata_path.exists():
                raise CanonicalPackageIntegrityError(
                    f"chunk {manifest_chunk.chunk_id!r}: missing metadata file {metadata_path}"
                )

            content = content_path.read_text()
            try:
                metadata = contracts.ChunkMetadata.from_dict(json.loads(metadata_path.read_text()))
            except (ValueError, json.JSONDecodeError) as exc:
                raise CanonicalPackageValidationError(
                    f"chunk {manifest_chunk.chunk_id!r}: metadata failed schema validation: {exc}"
                ) from exc

            recomputed_hash = hashing.content_hash(content.encode("utf-8"))
            if recomputed_hash != metadata.content_sha256:
                raise CanonicalPackageIntegrityError(
                    f"chunk {manifest_chunk.chunk_id!r}: content hash mismatch "
                    f"(sidecar says {metadata.content_sha256}, on-disk content "
                    f"hashes to {recomputed_hash}) -- package may have been "
                    "tampered with or corrupted since promotion"
                )

            for ref in metadata.media_refs:
                media_path = package_dir / "media" / _media_ref_to_filename(ref)
                if not media_path.exists():
                    raise CanonicalPackageIntegrityError(
                        f"chunk {manifest_chunk.chunk_id!r}: media reference "
                        f"{ref!r} does not resolve to a file under "
                        f"{package_dir / 'media'}"
                    )

            loaded_chunks.append(LoadedChunk(metadata=metadata, content=content))

        pub_map = None
        if manifest.strategy == "grouped":
            try:
                pub_map = publication_map.load_publication_map(package_dir)
            except publication_map.MalformedPublicationMapError as exc:
                raise CanonicalPackageValidationError(
                    f"publication-map.json is malformed: {exc}"
                ) from exc

            if pub_map is None:
                raise CanonicalPackageValidationError(
                    f"{package_dir} has strategy='grouped' but "
                    "publication-map.json is missing -- required at load "
                    "time, not only at convert time"
                )

            if pub_map.package_identity != manifest.plan_id:
                raise CanonicalPackageIntegrityError(
                    f"publication-map.json package_identity="
                    f"{pub_map.package_identity!r} does not match "
                    f"manifest.json plan_id={manifest.plan_id!r} -- the "
                    "publication map does not describe this package"
                )

            manifest_chunk_ids = {c.chunk_id for c in manifest.chunks}
            entry_chunk_ids = [e.chunk_id for e in pub_map.entries]
            if len(set(entry_chunk_ids)) != len(entry_chunk_ids):
                raise CanonicalPackageIntegrityError(
                    "publication-map.json has a duplicate chunk_id across entries"
                )
            if set(entry_chunk_ids) != manifest_chunk_ids:
                raise CanonicalPackageIntegrityError(
                    "publication-map.json entries' chunk_id values do not "
                    "match manifest chunk ids -- may have been edited or "
                    "corrupted after promotion"
                )
            orders = sorted(e.order for e in pub_map.entries)
            if orders != list(range(len(orders))):
                raise CanonicalPackageIntegrityError(
                    "publication-map.json entry order is not a contiguous "
                    "0..N-1 sequence -- may have been edited or corrupted "
                    "after promotion"
                )
        elif publication_map.load_publication_map(package_dir) is not None:
            # Non-grouped package with an unexpected publication-map.json
            # present -- validate_canonical.py already rejects this at
            # convert time (Task 6), but load() re-checks independently
            # since the file could have been added after promotion.
            raise CanonicalPackageValidationError(
                f"{package_dir} has strategy={manifest.strategy!r} but an "
                "unexpected publication-map.json is present"
            )

        return cls(
            manifest=manifest,
            validation_report=validation_report,
            chunks=loaded_chunks,
            media_dir=package_dir / "media",
            package_dir=package_dir,
            publication_map=pub_map,
        )
