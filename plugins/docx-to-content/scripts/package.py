"""
package.py
==========

Builds a STAGED canonical-content package (spec Section 6.3) from a
confirmed `ConversionPlan` and a `chunking.SlicedDocument` (already
reconciled/sliced by Task 8's `chunking.py` against cleaned markdown).

    canonical-content/
      manifest.json
      validation.json   <- placeholder here; Task 10 writes real content
      chunks/
        <chunk-id>.md
        <chunk-id>.meta.json
      media/
        <asset files>

This module does NOT invoke pandoc, cleanup, or chunk reconciliation
itself (that is `convert.py`'s job) — it only takes already-sliced chunk
content plus a raw media directory (pandoc's `--extract-media` output,
post legacy-image conversion) and turns them into the on-disk canonical
package: one sidecar per chunk, deduplicated/rewritten media, content
hashes, and a deterministically-ordered manifest.

Chunk IDs are never recomputed independently here: each chunk's ID is the
`stable_key` already carried on its `StructuralAnchor` (originally computed
via `identity.make_chunk_id` during analysis/Task 6, unchanged since).

Manifest/chunk ordering is deterministic: built by iterating
`sliced_document.chunks` in the order chunking.py produced them (itself
the confirmed plan's original `chunk_anchors` order), and `source_order`
is assigned from that same enumerate() index — never from directory
listing order.

Media handling (see individual docstrings below for full detail):
    - Copied once: identical content (by sha256) copied to media/ exactly
      once, regardless of how many chunks/refs point at it.
    - Duplicate names, different content: disambiguated with a
      `-<shorthash>` suffix so one file is never silently overwritten by
      another of the same name.
    - Relative path rewriting: `media/<file>` (relative to the raw
      extraction dir) -> `../media/<file>` (relative to `chunks/<id>.md`).
    - URL-encoded refs / spaces: decoded once via `urllib.parse.unquote`
      before resolving on disk, then re-encoded once via
      `urllib.parse.quote` when rewriting -- never double-encoded.
    - Absolute paths / `..` traversal: rejected via `MediaPathViolation`
      (a security/integrity boundary -- this is content that would let a
      malicious or corrupted document read/write outside the package).
    - Unsupported legacy media remaining after conversion: any media
      reference that still resolves to a `.emf`/`.wmf` file, or to a path
      that doesn't exist on disk at all, raises `UnsupportedLegacyMediaError`
      HERE, at packaging time -- not deferred to Task 10's validator.
      Rationale: packaging is the last point before writing files to
      staging; a package known to reference dead/unconverted media should
      never be written in the first place, rather than being written now
      and only caught by a later validation pass that runs against
      already-staged (but broken) output.
"""

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import quote, unquote

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import contracts  # noqa: E402
import dispositions  # noqa: E402
import hashing  # noqa: E402
import publication_map  # noqa: E402
import topic_grouping  # noqa: E402

_LEGACY_MEDIA_EXTENSIONS = {".emf", ".wmf"}

# Matches `![alt](ref)` markdown image syntax; group(2) is the raw
# (possibly URL-encoded) reference exactly as written in the source text.
# Alt text is matched with `(?:[^\]\\]|\\.)*` rather than a naive `[^\]]*`:
# alt text containing a markdown-escaped `]` (pandoc emits `\]` for a
# literal `]` byte, e.g. captions quoting "[Order Terminating a Protection
# Order]") otherwise terminates the character class early, so the image
# reference is never recognized at all -- never copied, never rewritten,
# and invisible to every downstream validator (a real defect found running
# the CEIS pilot; content-loss checks stayed green because the raw text
# survived untouched, just never parsed as a media reference).
_IMAGE_REF = re.compile(r"(!\[(?:[^\]\\]|\\.)*\]\()([^)]+)(\))")


class MediaError(Exception):
    """Base class for media-handling failures during canonical package
    building."""


class MediaPathViolation(MediaError):
    """A markdown image reference used an absolute path or contained a
    `..` path-traversal segment. Rejected outright -- media references
    are only ever resolved relative to the raw extraction directory, so
    an absolute path or a `..` segment is either a corrupted document or
    an attempt to read/write outside the package; either way this is not
    something to silently "handle", it must fail loudly."""


class UnsupportedLegacyMediaError(MediaError):
    """A media reference could not be copied into the canonical package:
    either it still resolves to a `.emf`/`.wmf` file (legacy conversion
    did not run, failed, or missed it), or it does not resolve to any
    file on disk at all. See module docstring for why this is raised here
    rather than deferred to Task 10's validator."""


# ---------------------------------------------------------------------------
# Media copy / dedupe / rewrite
# ---------------------------------------------------------------------------

_WINDOWS_DRIVE_ROOT_RE = re.compile(r"^[A-Za-z]:[\\/]")


def _decode_and_validate(raw_ref: str) -> str:
    decoded = unquote(raw_ref)
    posix = PurePosixPath(decoded)
    is_windows_style = (
        _WINDOWS_DRIVE_ROOT_RE.match(decoded) is not None
        or decoded.startswith("\\\\")
    )
    # Windows-style traversal (`..\..\secret`) is not caught by PurePosixPath,
    # which only splits on '/'. Normalize backslashes to forward slashes for
    # the '..' segment check so backslash-separated traversal is caught too.
    has_backslash_traversal = ".." in decoded.replace("\\", "/").split("/")
    if posix.is_absolute() or ".." in posix.parts or is_windows_style or has_backslash_traversal:
        raise MediaPathViolation(
            f"rejected media reference {raw_ref!r}: absolute paths (including "
            "Windows drive-letter roots and UNC paths) and '..' traversal "
            "segments (POSIX or backslash-separated) are not allowed in "
            "media references"
        )
    return decoded


def rewrite_media_and_copy(chunk_items: list, raw_base_dir: Path, media_out_dir: Path):
    """Copy every media file referenced by `chunk_items` into
    `media_out_dir` (deduplicated by content hash) and return
    `(rewritten_by_chunk_id, media_filenames)`.

    `chunk_items` is a list of `(chunk_id, content)` tuples, in the exact
    order the caller wants processed (does not affect correctness, only
    which duplicate-named file "wins" the un-suffixed name -- first one
    seen keeps the plain name, subsequent different-content collisions
    get a `-<shorthash>` suffix).
    """
    raw_base_dir = Path(raw_base_dir)
    media_out_dir.mkdir(parents=True, exist_ok=True)

    hash_to_name: dict = {}
    names_taken: set = set()
    media_filenames: list = []

    def _copy_once(decoded_ref: str) -> str:
        source_path = raw_base_dir / decoded_ref
        if (
            not source_path.exists()
            or not source_path.is_file()
            or source_path.suffix.lower() in _LEGACY_MEDIA_EXTENSIONS
        ):
            raise UnsupportedLegacyMediaError(
                f"media reference {decoded_ref!r} resolves to {source_path}, "
                "which is missing or is still an unconverted legacy "
                "(.emf/.wmf) file after legacy-media conversion ran"
            )
        data = source_path.read_bytes()
        sha256 = hashing.content_hash(data)
        if sha256 in hash_to_name:
            return hash_to_name[sha256]

        basename = source_path.name
        candidate = basename
        if candidate in names_taken:
            candidate = f"{source_path.stem}-{sha256[:8]}{source_path.suffix}"
        names_taken.add(candidate)
        hash_to_name[sha256] = candidate
        (media_out_dir / candidate).write_bytes(data)
        media_filenames.append(candidate)
        return candidate

    def _replace(match: "re.Match") -> str:
        prefix, raw_ref, suffix = match.group(1), match.group(2), match.group(3)
        if raw_ref.startswith(("http://", "https://")):
            return match.group(0)
        decoded = _decode_and_validate(raw_ref)
        out_name = _copy_once(decoded)
        new_ref = f"../media/{quote(out_name)}"
        return f"{prefix}{new_ref}{suffix}"

    rewritten_by_chunk_id = {}
    for chunk_id, content in chunk_items:
        rewritten_by_chunk_id[chunk_id] = _IMAGE_REF.sub(_replace, content)

    return rewritten_by_chunk_id, sorted(media_filenames)


def extract_media_refs(content: str) -> list:
    """Return the list of (already-rewritten) media reference paths found
    in a chunk's final content, for `ChunkMetadata.media_refs`."""
    refs = []
    for match in _IMAGE_REF.finditer(content):
        ref = match.group(2)
        if not ref.startswith(("http://", "https://")):
            refs.append(ref)
    return refs


# ---------------------------------------------------------------------------
# Canonical package assembly
# ---------------------------------------------------------------------------

def build_canonical_package(
    plan: "contracts.ConversionPlan",
    sliced_document,
    raw_media_dir: Path,
    output_dir: Path,
) -> "contracts.Manifest":
    """Build the staged canonical-content package under `output_dir` from
    `plan` and an already-reconciled/sliced `chunking.SlicedDocument`.

    Ordering is taken directly from `sliced_document.chunks` (itself in
    the confirmed plan's original `chunk_anchors` order) via `enumerate`;
    `source_order` and manifest ordering are both derived from that index,
    never from `os.listdir()`/`glob()`.

    `validation.json` is written as an explicit PENDING placeholder here,
    not a real validation report -- Task 10 owns writing real validation
    content into this same path; the manifest's `validation_report` field
    already points at "validation.json" so Task 10 does not need to change
    the manifest shape, only replace this placeholder's content.
    """
    output_dir = Path(output_dir)
    chunks_dir = output_dir / "chunks"
    media_dir = output_dir / "media"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    ordered = list(enumerate(sliced_document.chunks))

    chunk_items = [
        (chunk_slice.anchor.stable_key, chunk_slice.content)
        for chunk_slice in sliced_document.chunks
    ]
    rewritten_by_chunk_id, media_filenames = rewrite_media_and_copy(
        chunk_items, raw_media_dir, media_dir
    )

    source_sha256 = plan.source.sha256
    manifest_chunks = []
    for idx, chunk_slice in ordered:
        anchor = chunk_slice.anchor
        chunk_id = anchor.stable_key
        content = rewritten_by_chunk_id[chunk_id]
        content_file = f"chunks/{chunk_id}.md"
        metadata_file = f"chunks/{chunk_id}.meta.json"

        (chunks_dir / f"{chunk_id}.md").write_text(content)

        content_sha256 = hashing.content_hash(content.encode("utf-8"))
        meta = contracts.ChunkMetadata(
            schema_version=contracts.CHUNK_METADATA_SCHEMA_VERSION,
            chunk_id=chunk_id,
            source_order=idx,
            source_heading_path=list(anchor.source_heading_path),
            topic=anchor.heading_text,
            content_type=plan.content_type,
            template_profile=plan.template_profile,
            source_sha256=source_sha256,
            plan_id=plan.plan_id,
            content_file=content_file,
            content_sha256=content_sha256,
            local_links=[],
            media_refs=extract_media_refs(content),
        )
        (chunks_dir / f"{chunk_id}.meta.json").write_text(
            json.dumps(meta.to_dict(), indent=2, sort_keys=True)
        )

        manifest_chunks.append(
            contracts.ManifestChunk(
                chunk_id=chunk_id,
                content_file=content_file,
                metadata_file=metadata_file,
                source_order=idx,
                source_heading_path=list(anchor.source_heading_path),
            )
        )

    manifest = contracts.Manifest(
        schema_version=contracts.MANIFEST_SCHEMA_VERSION,
        generator=contracts.ManifestGenerator(
            plugin="docx-to-content", plugin_version="0.1.0"
        ),
        source=contracts.ManifestSourceFingerprint(
            path=plan.source.path, sha256=source_sha256
        ),
        plan_id=plan.plan_id,
        content_type=plan.content_type,
        template_profile=plan.template_profile,
        strategy=plan.strategy,
        chunk_count=len(manifest_chunks),
        chunks=manifest_chunks,
        media=media_filenames,
        validation_report="validation.json",
    )

    (output_dir / "manifest.json").write_text(
        json.dumps(manifest.to_dict(), indent=2, sort_keys=True)
    )
    (output_dir / "validation.json").write_text(
        json.dumps(
            {
                "status": "PENDING",
                "issues": [],
                "note": "placeholder written by Task 9's package builder; "
                        "Task 10 implements real canonical validation and "
                        "overwrites this file with an actual ValidationReport.",
            },
            indent=2,
        )
    )

    return manifest


def build_grouped_canonical_package(
    plan: "contracts.ConversionPlan",
    sliced_document,
    raw_media_dir: Path,
    output_dir: Path,
) -> "contracts.Manifest":
    """Build a staged canonical-content package under `output_dir` using
    the "grouped" strategy (Task 17-topic-grouping): every level-1 heading
    in `sliced_document.chunks` becomes one topic chunk file, with all of
    its descendant structural anchors' content concatenated (in source
    order) into that single file, and their lineage preserved as
    `ChunkMetadata.anchors`. A `publication-map.json` sidecar is written
    alongside the manifest, giving explicit, directory-order-independent
    topic ordering for rendering.

    Reuses `rewrite_media_and_copy`/`extract_media_refs` unchanged from the
    ungrouped path -- media handling does not change with strategy.
    """
    output_dir = Path(output_dir)
    chunks_dir = output_dir / "chunks"
    media_dir = output_dir / "media"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    headings = [
        {
            "level": chunk_slice.anchor.heading_level,
            "text": chunk_slice.anchor.heading_text,
            "path": list(chunk_slice.anchor.source_heading_path),
            "occurrence": chunk_slice.anchor.occurrence,
        }
        for chunk_slice in sliced_document.chunks
    ]
    if plan.confirmed_topic_roots:
        root_keys = {
            (tuple(r["source_heading_path"]), r["occurrence"])
            for r in plan.confirmed_topic_roots
        }
        boundaries = topic_grouping.compute_topic_boundaries_from_roots(headings, root_keys)
    else:
        # No confirmed root set on this plan (e.g. a plan predating Task 18,
        # or the "grouped" strategy chosen without a prior analyze pass) --
        # fall back to recomputing the default heuristic.
        boundaries = topic_grouping.compute_topic_boundaries(headings)

    slices_by_path_occurrence = {
        (tuple(chunk_slice.anchor.source_heading_path), chunk_slice.anchor.occurrence): chunk_slice
        for chunk_slice in sliced_document.chunks
    }

    def _slice_for_member(member):
        return slices_by_path_occurrence[(tuple(member.path), member.occurrence)]

    chunk_items = [
        (
            boundary.topic_id,
            "\n\n".join(_slice_for_member(m).content for m in boundary.members),
        )
        for boundary in boundaries
    ]
    rewritten_by_topic_id, media_filenames = rewrite_media_and_copy(
        chunk_items, raw_media_dir, media_dir
    )

    source_sha256 = plan.source.sha256
    manifest_chunks = []
    topic_chunk_ids = {}
    for source_order, boundary in enumerate(boundaries):
        content = rewritten_by_topic_id[boundary.topic_id]
        content_file = f"chunks/{boundary.topic_id}.md"
        metadata_file = f"chunks/{boundary.topic_id}.meta.json"
        topic_chunk_ids[boundary.topic_id] = boundary.topic_id

        (chunks_dir / f"{boundary.topic_id}.md").write_text(content)

        anchors_meta = [
            {
                "stable_key": _slice_for_member(m).anchor.stable_key,
                "source_heading_path": list(m.path),
                "occurrence": m.occurrence,
                "heading_level": m.level,
            }
            for m in boundary.members
        ]
        meta = contracts.ChunkMetadata(
            schema_version=contracts.CHUNK_METADATA_SCHEMA_VERSION,
            chunk_id=boundary.topic_id,
            source_order=source_order,
            source_heading_path=[boundary.title],
            topic=boundary.title,
            content_type=plan.content_type,
            template_profile=plan.template_profile,
            source_sha256=source_sha256,
            plan_id=plan.plan_id,
            content_file=content_file,
            content_sha256=hashing.content_hash(content.encode("utf-8")),
            local_links=[],
            media_refs=extract_media_refs(content),
            anchors=anchors_meta,
        )
        (chunks_dir / f"{boundary.topic_id}.meta.json").write_text(
            json.dumps(meta.to_dict(), indent=2, sort_keys=True)
        )

        manifest_chunks.append(
            contracts.ManifestChunk(
                chunk_id=boundary.topic_id,
                content_file=content_file,
                metadata_file=metadata_file,
                source_order=source_order,
                source_heading_path=[boundary.title],
            )
        )

    manifest = contracts.Manifest(
        schema_version=contracts.MANIFEST_SCHEMA_VERSION,
        generator=contracts.ManifestGenerator(
            plugin="docx-to-content", plugin_version="0.1.0"
        ),
        source=contracts.ManifestSourceFingerprint(
            path=plan.source.path, sha256=source_sha256
        ),
        plan_id=plan.plan_id,
        content_type=plan.content_type,
        template_profile=plan.template_profile,
        strategy="grouped",
        chunk_count=len(manifest_chunks),
        chunks=manifest_chunks,
        media=media_filenames,
        validation_report="validation.json",
    )

    (output_dir / "manifest.json").write_text(
        json.dumps(manifest.to_dict(), indent=2, sort_keys=True)
    )
    (output_dir / "validation.json").write_text(
        json.dumps(
            {
                "status": "PENDING",
                "issues": [],
                "note": "placeholder written by the grouped package builder; "
                        "validate_canonical.py overwrites this file with an "
                        "actual ValidationReport.",
            },
            indent=2,
        )
    )

    pub_map = publication_map.build_publication_map(
        boundaries, topic_chunk_ids, package_identity=manifest.plan_id
    )
    publication_map.write_publication_map(pub_map, output_dir)

    return manifest


# ---------------------------------------------------------------------------
# Task 12 — CanonicalPackage: renderer-side loader
# ---------------------------------------------------------------------------
#
# Renderers (Task 13+) never touch a canonical package's files directly and
# never see a source .docx path, an analysis directory, or a ConversionPlan
# -- `CanonicalPackage.load()` takes only a directory path and hands back an
# already-fully-vetted in-memory object. See spec Section 7.3 (renderer
# preconditions) and Section 8 (Renderer Protocol).
#
# This is a *second*, independent integrity check at load time, on top of
# whatever `validate_canonical.py` already recorded in `validation.json` at
# convert time -- defense against the promoted package having been
# tampered with or corrupted on disk since promotion. Nothing here
# reimplements schema validation (`contracts.Manifest.from_dict` /
# `contracts.ChunkMetadata.from_dict`) or disposition-completeness checking
# (`dispositions.apply_disposition`); both are reused as-is.


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
    """Reverse `rewrite_media_and_copy`'s `../media/<quoted-name>` rewrite
    back to the plain on-disk filename under `media/`."""
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
    publication_map: "object" = None  # contracts.PublicationMap | None; populated by load() for strategy="grouped"

    @classmethod
    def load(cls, package_dir: Path) -> "CanonicalPackage":
        """Load and fully re-validate an ACCEPTED canonical package at
        `package_dir`. Raises `CanonicalPackageError` (or a subclass) if
        any of the following fail -- never returns a partially-valid
        package:

        1. `manifest.json` schema-validates via `contracts.Manifest.from_dict`.
        2. `validation.json` schema-validates via
           `contracts.ValidationReport.from_dict`, and its status is
           either PASS, or WARN with every warning accounted for by a
           co-located `warning-disposition.json`
           (`dispositions.apply_disposition`) -- FAIL always rejects.
        3. Every chunk's on-disk content hash (`hashing.content_hash`)
           matches its sidecar's `content_sha256` (fresh integrity check,
           not trusting convert-time validation).
        4. Every chunk's media references resolve to a real file under
           `media/`.
        5. Only if all of the above pass, returns the loaded
           `CanonicalPackage`.
        """
        package_dir = Path(package_dir)

        manifest_path = package_dir / "manifest.json"
        if not manifest_path.exists():
            raise CanonicalPackageValidationError(
                f"{manifest_path} does not exist"
            )
        try:
            manifest = contracts.Manifest.from_dict(
                json.loads(manifest_path.read_text())
            )
        except (ValueError, json.JSONDecodeError) as exc:
            raise CanonicalPackageValidationError(
                f"manifest.json failed schema validation: {exc}"
            ) from exc

        validation_path = package_dir / "validation.json"
        if not validation_path.exists():
            raise CanonicalPackageValidationError(
                f"{validation_path} does not exist"
            )
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
                undispositioned = [
                    dispositions.disposition_key(w) for w in check.undispositioned
                ]
                raise CanonicalPackageValidationError(
                    f"{package_dir} has validation status WARN with "
                    f"undispositioned warnings: {undispositioned}"
                )

        loaded_chunks = []
        for manifest_chunk in manifest.chunks:
            content_path = package_dir / manifest_chunk.content_file
            metadata_path = package_dir / manifest_chunk.metadata_file
            if not content_path.exists():
                raise CanonicalPackageIntegrityError(
                    f"chunk {manifest_chunk.chunk_id!r}: missing content "
                    f"file {content_path}"
                )
            if not metadata_path.exists():
                raise CanonicalPackageIntegrityError(
                    f"chunk {manifest_chunk.chunk_id!r}: missing metadata "
                    f"file {metadata_path}"
                )

            content = content_path.read_text()
            try:
                metadata = contracts.ChunkMetadata.from_dict(
                    json.loads(metadata_path.read_text())
                )
            except (ValueError, json.JSONDecodeError) as exc:
                raise CanonicalPackageValidationError(
                    f"chunk {manifest_chunk.chunk_id!r}: metadata failed "
                    f"schema validation: {exc}"
                ) from exc

            recomputed_hash = hashing.content_hash(content.encode("utf-8"))
            if recomputed_hash != metadata.content_sha256:
                raise CanonicalPackageIntegrityError(
                    f"chunk {manifest_chunk.chunk_id!r}: content hash "
                    f"mismatch (sidecar says {metadata.content_sha256}, "
                    f"on-disk content hashes to {recomputed_hash}) -- "
                    "package may have been tampered with or corrupted "
                    "since promotion"
                )

            for ref in metadata.media_refs:
                media_path = package_dir / "media" / _media_ref_to_filename(ref)
                if not media_path.exists():
                    raise CanonicalPackageIntegrityError(
                        f"chunk {manifest_chunk.chunk_id!r}: media "
                        f"reference {ref!r} does not resolve to a file "
                        f"under {package_dir / 'media'}"
                    )

            loaded_chunks.append(LoadedChunk(metadata=metadata, content=content))

        pub_map = None
        if manifest.strategy == "grouped":
            pub_map = publication_map.load_publication_map(package_dir)

        return cls(
            manifest=manifest,
            validation_report=validation_report,
            chunks=loaded_chunks,
            media_dir=package_dir / "media",
            package_dir=package_dir,
            publication_map=pub_map,
        )
