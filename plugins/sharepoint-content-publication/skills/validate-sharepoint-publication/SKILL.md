---
name: validate-sharepoint-publication
description: Offline pre-upload schema validation of an UploadPackage against the target library schema. Post-deployment validation (files/pages/metadata/links/media actually present after upload) is not yet built.
---

# validate-sharepoint-publication

## Purpose

**Pre-upload validation (existing, real):** `sharepoint_dry_run.py`'s `validate_upload_package`
runs entirely offline — zero tenant I/O — checking an `UploadPackage`'s fields against the
target library schema (e.g. title length) before any human upload happens.

**Post-deployment validation (not yet built):** verifying files, pages, metadata, links, and
media are actually present and correct *after* a deployment, against observed tenant state. This
is a genuinely separate capability from the pre-upload check and has not been extended yet —
recorded here honestly rather than claimed complete.

## Input boundaries

- Pre-upload: an `UploadPackage`, checked entirely offline.
- Zero tenant I/O in the existing implementation.

## Scripts

- `../../scripts/sharepoint_dry_run.py` (existing, pre-upload only).

## Tests

- `../../tests/unit/test_sharepoint_dry_run.py` (existing).

## Outstanding work

Post-deployment validation (comparing actual tenant state after upload against the package) is
not implemented. `reconcile-sharepoint-publication` partially covers this from a different angle
(reconciling *identity* fields against a CSV export), but does not check file/page/media
*presence* specifically. This gap is real and not silently claimed complete.
