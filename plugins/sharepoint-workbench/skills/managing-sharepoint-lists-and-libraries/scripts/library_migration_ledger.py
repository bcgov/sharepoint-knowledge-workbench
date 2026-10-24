"""Resumable per-file ledger for uploading one SharePoint library to a new site.

Purpose: turn an inventory CSV (files.csv from sharepoint-collect-site-inventory) into a ledger
that routes each file (static-html -> sp-static-aspx-file-migration, upload -> generic upload,
skip), maps source paths to target library/folder, recorders status, and emits a
spo-upload-file.ps1 plan for downloaded generic files. No tenant I/O.

Key Input Dependencies: inventory files.csv (LibraryTitle, LibraryRelativePath, FileName,
FileExtension, FileUrl, SizeBytes); downloads.csv from download-sharepoint-inventory-files.ps1
(FileUrl, LocalPath, Status).

Usage:
  python library_migration_ledger.py find-inventory --search-dir inventory --source-library "Administration Documents" \
      --source-web-url https://source-tenant.example.com/Operations   (exit 3 = none covers it; crawl first)
  python library_migration_ledger.py export-inventory --inventory files.csv --source-library "..." \
      --source-web-url URL --output library-inventory.csv   (prints the downloader's extension list)
  python library_migration_ledger.py plan --inventory files.csv --source-library "Administration Documents" \
      --target-library Operations --target-root "Administration Documents" --ledger ledger.csv
  python library_migration_ledger.py stage --ledger ledger.csv --downloads downloads.csv
  python library_migration_ledger.py upload-plan --ledger ledger.csv --output upload-plan.json       [--limit 20] [--extensions pdf,jpg]   (batch the plan; only DOWNLOADED upload rows with a local file)
  python library_migration_ledger.py upload-next --ledger ledger.csv --uploader <path>/spo-upload-file.ps1       --config config-spo-dev.psd1 [--count 1] [--extensions pdf] [--execute]
      (picks the next DOWNLOADED upload row(s), runs the uploader, recorders UPLOADED/FAILED itself;
      without --execute it is a dry run and the ledger is unchanged; refuses a non-DEV config;
      --route static-html uploads CONVERTED pages instead)
  python library_migration_ledger.py mark-converted --ledger ledger.csv --file-url URL --html page.html
      (after a page is converted and validated: points the row at the HTML, sets CONVERTED)
  python library_migration_ledger.py reconcile --ledger ledger.csv --listing target-listing.csv
      (listing columns: ServerRelativeUrl [or FileRef], optional SizeBytes; sets UPLOADED for files
      present on the target, reverts UPLOADED rows missing there, FAILED on size mismatch)
  python library_migration_ledger.py verify --ledger ledger.csv --listing target-listing.csv
      (end-of-library check: every UPLOADED row must be on the target, size-matched for plain uploads -> VERIFIED;
      prints missing / size_mismatch / outstanding; exit 4 when anything is not confirmed)
  python library_migration_ledger.py record --ledger ledger.csv --file-url URL --status UPLOADED --message ok
  python library_migration_ledger.py summary --ledger ledger.csv
  Any mutating command (plan, stage, upload-next --execute, mark-converted, reconcile, record) also accepts
  --tracker inventory/portal-workspace-documents/migration-status.csv [--environment DEV] to write the ledger through
  to the overall file-level tracker (see migration_status_tracker.py).

Index: LedgerError, find_inventory, export_inventory, build_plan, stage, upload_plan, upload_next, reconcile, verify,
record, mark_converted, summarize, format_batch, main (helpers: ledger_location_warning, _sync_tracker, _read, _write, _clean_error, _run_uploader, _check_site_marker,
_uploader_command, _upload_results, _match_results, _record_upload_results, _index_listing, _reconcile_row, _verify_row, _csv_set,
_build_parser, _cmd_find_inventory, _cmd_export_inventory, _cmd_upload_next, _cmd_verify)
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

FIELDS = ["FileUrl", "SourceRelativePath", "Extension", "SizeBytes", "Route", "TargetLibrary",
          "TargetFolder", "TargetFilename", "LocalPath", "Sha256", "Status", "Message"]
STATUSES = {"PLANNED", "DOWNLOADED", "CONVERTED", "UPLOADED", "VERIFIED", "FAILED", "BLOCKED", "SKIPPED", "EXCLUDED"}
HTML_EXT = {"aspx": "html", "html": "html", "htm": "html"}
# Status a row must have before upload-plan/upload-next will pick it, by route.
PENDING_STATUS = {"upload": "DOWNLOADED", "static-html": "CONVERTED"}
OFFICE_EXTENSIONS = {"doc", "docx", "xls", "xlsx", "ppt", "pptx"}


class LedgerError(Exception):
    """Raised for invalid input or ledger state."""


def _read(path: Path) -> list[dict[str, str]]:
    """Read a CSV (UTF-8, BOM tolerated) into row dicts; LedgerError if the file is missing."""
    if not path.exists():
        raise LedgerError(f"File not found: {path}")
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def _write(path: Path, rows: list[dict[str, str]]) -> None:
    """Write ledger rows with the FIELDS header, creating the parent folder if missing."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def _library_rows(rows: list[dict[str, str]], source_library: str, source_web_url: str) -> list[dict[str, str]]:
    """Rows of one library, scoped to one web when source_web_url is given.

    With a web URL the library is matched by its URL folder (e.g. PublishingImages), which can differ
    from the display title (Images); without one it is matched by title.
    """
    if source_web_url:
        prefix = f"{source_web_url.rstrip('/')}/{source_library}/".lower()
        return [r for r in rows if r.get("FileUrl", "").lower().startswith(prefix)]
    return [r for r in rows if r.get("LibraryTitle", "").lower() == source_library.lower()]


def find_inventory(search_dirs: list[Path], source_library: str, source_web_url: str = "") -> Path | None:
    """Newest files.csv under search_dirs that already covers the library, else None."""
    hits = []
    for d in search_dirs:
        for f in (d.rglob("files.csv") if d.is_dir() else []):
            if _library_rows(_read(f), source_library, source_web_url):
                hits.append(f)
    return max(hits, key=lambda f: f.stat().st_mtime) if hits else None


def export_inventory(inventory: Path, source_library: str, source_web_url: str, output: Path,
                     done: dict[str, str] | None = None) -> list[str]:
    """Write the library-scoped inventory the bulk downloader needs; return its sorted extensions.

    done (FileUrl -> status from the tracker) drops files already migrated so they are never re-downloaded.
    """
    rows = _library_rows(_read(inventory), source_library, source_web_url)
    if not rows:
        raise LedgerError(f"No inventory rows for source library '{source_library}'")
    if done:
        rows = [r for r in rows if r["FileUrl"] not in done]
        if not rows:
            raise LedgerError(f"All files in '{source_library}' are already done in the tracker; nothing to download")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return sorted({(r.get("FileExtension") or "").lower().lstrip(".") for r in rows} - {""})


def build_plan(inventory: Path, source_library: str, target_library: str, target_root: str,
               ledger: Path, skip_extensions: set[str] | None = None,
               source_web_url: str = "", done: dict[str, str] | None = None) -> list[dict[str, str]]:
    """Create or refresh the ledger; rows already recorded keep their status.

    done (FileUrl -> status from the tracker) seeds new rows as already migrated, so work done through
    an older wrapper or another ledger is not planned or downloaded again.

    source_web_url scopes the library to one web, since several webs can share a library title.
    """
    skip_extensions = {e.lower().lstrip(".") for e in (skip_extensions or set())}
    inv = _library_rows(_read(inventory), source_library, source_web_url)
    if not inv:
        raise LedgerError(f"No inventory rows for source library '{source_library}'")
    existing = {r["FileUrl"]: r for r in _read(ledger)} if ledger.exists() else {}
    rows, seen = [], Counter()
    for r in inv:
        rel = (r.get("LibraryRelativePath") or r["FileName"]).replace("\\", "/").strip("/")
        folder, _, name = rel.rpartition("/")
        ext = (r.get("FileExtension") or "").lower()
        route = "skip" if ext in skip_extensions else ("static-html" if ext in HTML_EXT else "upload")
        target_name = f"{name.rsplit('.', 1)[0]}.html" if route == "static-html" else name
        tfolder = "/".join(p for p in (target_root.strip("/"), folder) if p)
        row = {"FileUrl": r["FileUrl"], "SourceRelativePath": rel, "Extension": ext,
               "SizeBytes": r.get("SizeBytes", ""), "Route": route, "TargetLibrary": target_library,
               "TargetFolder": tfolder, "TargetFilename": target_name, "LocalPath": "", "Sha256": "",
               "Status": "EXCLUDED" if route == "skip" else "PLANNED", "Message": ""}
        prior = existing.get(r["FileUrl"])
        if prior:
            row.update({k: prior[k] for k in ("LocalPath", "Sha256", "Status", "Message")})
            if route == "skip" and row["Status"] == "SKIPPED":
                row["Status"] = "EXCLUDED"
        elif done and r["FileUrl"] in done and route != "skip":
            row.update(Status=done[r["FileUrl"]], Message="Already done per tracker")
        seen[(tfolder.lower(), target_name.lower())] += 1
        rows.append(row)
    for row in rows:
        if seen[(row["TargetFolder"].lower(), row["TargetFilename"].lower())] > 1 and row["Status"] == "PLANNED":
            row["Status"], row["Message"] = "BLOCKED", "Target path collision"
    _write(ledger, rows)
    return rows


def stage(ledger: Path, downloads: Path) -> None:
    """Attach downloaded local paths and hashes; mark missing files FAILED."""
    dl = {r["FileUrl"]: r for r in _read(downloads)}
    rows = _read(ledger)
    for row in rows:
        d = dl.get(row["FileUrl"])
        if not d or row["Status"] not in {"PLANNED", "FAILED"}:
            continue
        local = Path(d.get("LocalPath", ""))
        if d.get("Status", "").upper() in {"SUCCESS", "DOWNLOADED"} and local.is_file():
            row.update(LocalPath=str(local), Sha256=hashlib.sha256(local.read_bytes()).hexdigest(),
                       Status="DOWNLOADED", Message="")
        else:
            row.update(Status="FAILED", Message=d.get("Message") or "Downloaded file missing")
    _write(ledger, rows)


def upload_plan(ledger: Path, output: Path, limit: int | None = None,
                extensions: set[str] | None = None, route: str = "upload") -> dict:
    """Write a spo-upload-file.ps1 plan for pending rows of one route.

    route "upload" takes DOWNLOADED files; route "static-html" takes CONVERTED pages (see mark_converted).

    limit caps the batch size; extensions restricts it to those file types. Rows whose local
    file no longer exists are left out so the plan never points at a missing source.
    """
    wanted = {e.lower().lstrip(".") for e in extensions} if extensions else None
    actions = []
    for r in _read(ledger):
        if r["Route"] != route or r["Status"] != PENDING_STATUS[route] or not Path(r["LocalPath"]).is_file():
            continue
        if wanted is not None and r["Extension"].lower().lstrip(".") not in wanted:
            continue
        actions.append({"source_path": r["LocalPath"], "target_library": r["TargetLibrary"],
                        "target_folder": r["TargetFolder"], "target_filename": r["TargetFilename"]})
        if limit is not None and len(actions) >= limit:
            break
    plan = {"document_id": "library-upload", "action_count": len(actions), "actions": actions}
    output.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    return plan


ANSI_RE = r"\x1b\[[0-9;]*m"  # PowerShell colour codes in captured errors
UPLOAD_TOKEN = "PUBLISH-SPO-MARKDOWN"  # must match spo-upload-file.ps1's -ConfirmToken


CREATE_LIBRARY_TOKEN = "PROVISION-SPO-LIST"


def _clean_error(text: str, limit: int = 600) -> str:
    """Strip ANSI colour codes, collapse whitespace, and keep the 'Details:' tail of PowerShell errors."""
    text = re.sub(ANSI_RE, "", text or "")
    text = " ".join(text.split())
    if "Details:" in text:
        text = text[text.index("Details:"):]
    return text[:limit]


def _run_uploader(cmd: list[str]) -> subprocess.CompletedProcess:
    """Run the PowerShell uploader; stdin stays attached so interactive sign-in works."""
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def _check_site_marker(config: Path, site_marker: str) -> None:
    """Refuse to continue unless the config's SiteUrl contains site_marker (for example DEV)."""
    site = re.search(r"SiteUrl\s*=\s*['\"]([^'\"]+)", config.read_text(encoding="utf-8"))
    if not site or site_marker.lower() not in site.group(1).lower():
        raise LedgerError(f"Config {config} SiteUrl does not contain '{site_marker}'; refusing to upload")


def _uploader_command(uploader: Path, plan_path: Path, config: Path, execute: bool) -> list[str]:
    """Build the PowerShell command line for spo-upload-file.ps1 (dry run unless execute)."""
    shell = shutil.which("pwsh") or shutil.which("powershell") or "pwsh"
    cmd = [shell, "-NoProfile", "-File", str(uploader), "-PlanPath", str(plan_path), "-ConfigPath", str(config)]
    return cmd + ["-Execute", "-ConfirmToken", UPLOAD_TOKEN] if execute else cmd


def _upload_results(done: subprocess.CompletedProcess) -> list[dict]:
    """Parse the uploader's JSON stdout into result dicts (empty when the uploader failed)."""
    if done.returncode != 0:
        return []
    out = json.loads(done.stdout or "[]")
    return out if isinstance(out, list) else [out]


def _match_results(plan: dict, results: list[dict]) -> list[dict | None]:
    """Pair each planned action with its uploader result.

    The uploader returns results in plan order, so when the counts agree match by position: the echoed
    source_path can be mangled by the console code page (for example an en dash in a filename). Otherwise
    fall back to matching on source_path.
    """
    if len(results) == len(plan["actions"]):
        return list(results)
    by_path = {r.get("source_path"): r for r in results}
    return [by_path.get(a["source_path"]) for a in plan["actions"]]


def _record_upload_results(ledger: Path, plan: dict, done: subprocess.CompletedProcess) -> tuple[int, list[dict]]:
    """Set UPLOADED or FAILED on each planned row from the uploader result.

    Returns the success count and one outcome dict (file, status, message) per planned file.
    """
    rows = _read(ledger)
    by_source = {r["LocalPath"]: r for r in rows}
    error = _clean_error(done.stderr or done.stdout)
    uploaded = 0
    outcomes: list[dict] = []
    for action, result in zip(plan["actions"], _match_results(plan, _upload_results(done))):
        row = by_source[action["source_path"]]
        if result and result.get("success"):
            row.update(Status="UPLOADED", Message=f"Uploaded to {result.get('target_url', '')}")
            uploaded += 1
        elif result:
            row.update(Status="FAILED", Message="Uploader reported success=false for this file")
        else:
            row.update(Status="FAILED", Message=(error if done.returncode != 0 and error
                                                 else f"No matching result from uploader for {row['TargetFilename']}"))
        outcomes.append({"file": f"{row['TargetFolder']}/{row['TargetFilename']}".lstrip("/"),
                         "status": row["Status"], "message": row["Message"]})
    _write(ledger, rows)
    return uploaded, outcomes


def _missing_library(plan: dict, done: subprocess.CompletedProcess) -> str | None:
    """Return the target library the uploader reported as non-existent, else None."""
    text = _clean_error((done.stderr or "") + " " + (done.stdout or ""))
    for lib in dict.fromkeys(a["target_library"] for a in plan["actions"]):
        if f"List '{lib}' does not exist" in text:
            return lib
    return None


def _default_library_creator(uploader: Path) -> Path:
    """Sibling skill's spo-provision-list.ps1, located relative to the installed uploader script."""
    return uploader.resolve().parents[2] / "sharepoint-create-document-library" / "scripts" / "spo-provision-list.ps1"


def create_library(ledger: Path, creator: Path, config: Path, library: str, runner=None) -> None:
    """Create a document library (template 101) via the canonical provisioning script.

    The script can raise a harmless 'Count' error after the library is created, so the exit code is
    not trusted: the caller retries the upload, which proves whether the library now exists.
    """
    plan_path = ledger.with_name("create-library-plan.json")
    plan = {"outcome": "OBSERVED", "confirmation_token": f"APPLY-1-{library}", "field_actions": [],
            "content_type_actions": [], "blocking_findings": [], "list_deletions": [],
            "list_creations": [{"title": library, "template": 101, "detail": f"create '{library}' (template 101)"}]}
    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    shell = shutil.which("pwsh") or shutil.which("powershell") or "pwsh"
    cmd = [shell, "-NoProfile", "-File", str(creator), "-PlanPath", str(plan_path), "-ConfigPath", str(config),
           "-Execute", "-ConfirmToken", CREATE_LIBRARY_TOKEN]
    (runner or _run_uploader)(cmd)


def upload_next(ledger: Path, uploader: Path, config: Path, count: int = 1,
                extensions: set[str] | None = None, execute: bool = False,
                site_marker: str = "DEV", runner=None, route: str = "upload",
                library_creator: Path | None = None, allow_create: bool = True) -> dict:
    """Upload the next `count` pending files and record each outcome in the ledger.

    Dry run (execute=False) prints the uploader's plan and leaves the ledger untouched. The
    config SiteUrl must contain site_marker so a TEST/PROD config can never be used by accident.
    On execute, a target library that does not exist yet is created once, then the upload is retried.
    allow_create=False never creates (use it when the library should already exist, for example a default
    library whose title differs from its URL folder), so a failed lookup cannot produce a duplicate library.
    """
    _check_site_marker(config, site_marker)
    plan_path = ledger.with_name("next-upload-plan.json")
    plan = upload_plan(ledger, plan_path, limit=count, extensions=extensions, route=route)
    if not plan["actions"]:
        raise LedgerError(f"No {PENDING_STATUS[route]} rows pending for route {route}")
    run = runner or _run_uploader
    done = run(_uploader_command(uploader, plan_path, config, execute))
    if not execute:
        return {"dry_run": True, "returncode": done.returncode, "output": done.stdout, "error": done.stderr}
    created = _missing_library(plan, done) if allow_create else None
    if created:
        create_library(ledger, library_creator or _default_library_creator(uploader), config, created, run)
        done = run(_uploader_command(uploader, plan_path, config, execute))
    uploaded, outcomes = _record_upload_results(ledger, plan, done)
    return {"dry_run": False, "uploaded": uploaded, "failed": len(plan["actions"]) - uploaded, "files": outcomes,
            "created_library": created}

def format_batch(files: list[dict]) -> list[str]:
    """One console line per file: status, target path and message, so a run names what it changed."""
    return [f"{f['status']:<9} {f['file']}  ({f['message']})" for f in files]


def _index_listing(listing: Path) -> dict[str, str]:
    """Map lower-cased server-relative URL -> size from a target library listing CSV."""
    found = {}
    for r in _read(listing):
        url = (r.get("ServerRelativeUrl") or r.get("FileRef") or "").replace("\\", "/").lower()
        found[url] = (r.get("SizeBytes") or r.get("Length") or "").strip()
    return found


def _reconcile_row(row: dict[str, str], found: dict[str, str]) -> None:
    """Update one upload-route row from the target listing (see reconcile)."""
    suffix = "/" + "/".join(p for p in (row["TargetLibrary"], row["TargetFolder"], row["TargetFilename"]) if p).lower()
    match = [size for url, size in found.items() if url.endswith(suffix)]
    if not match:
        if row["Status"] == "UPLOADED":
            row.update(Status="DOWNLOADED", Message="Missing on target at reconcile")
    elif match[0] and row["SizeBytes"] and match[0] != row["SizeBytes"]:
        row.update(Status="FAILED", Message=f"Target size {match[0]} differs from source {row['SizeBytes']}")
    else:
        row.update(Status="UPLOADED", Message=row["Message"] or "Found on target at reconcile")


def reconcile(ledger: Path, listing: Path) -> None:
    """Align upload-route rows with a target library listing (spo-upload-file cannot overwrite).

    Present on target -> UPLOADED (FAILED on a size mismatch); UPLOADED but absent -> DOWNLOADED.
    """
    found = _index_listing(listing)
    rows = _read(ledger)
    for row in rows:
        if row["Route"] == "upload" and row["Status"] in {"DOWNLOADED", "FAILED", "UPLOADED"}:
            _reconcile_row(row, found)
    _write(ledger, rows)


def _verify_row(row: dict[str, str], found: dict[str, str]) -> str:
    """Check one UPLOADED/VERIFIED row against the listing; returns 'ok', 'missing' or 'size'."""
    suffix = "/" + "/".join(p for p in (row["TargetLibrary"], row["TargetFolder"], row["TargetFilename"]) if p).lower()
    match = [size for url, size in found.items() if url.endswith(suffix)]
    if not match:
        row.update(Status=PENDING_STATUS.get(row["Route"], "DOWNLOADED"), Message="Missing on target at verify")
        return "missing"
    # Converted pages differ from the source in size by design, and SharePoint rewrites Office document
    # properties on upload, so only other plain uploads are size-checked.
    sized = row["Route"] == "upload" and row["Extension"].lower().lstrip(".") not in OFFICE_EXTENSIONS
    if sized and match[0] and row["SizeBytes"] and match[0] != row["SizeBytes"]:
        row.update(Status="FAILED", Message=f"Target size {match[0]} differs from source {row['SizeBytes']}")
        return "size"
    row.update(Status="VERIFIED", Message="Present on target at verify")
    return "ok"


def verify(ledger: Path, listing: Path) -> dict:
    """Confirm every ledger file is on the target library (read-only against the tenant).

    UPLOADED/VERIFIED rows found on the target (size-checked for plain uploads) become VERIFIED; rows missing or
    mismatched are reverted/FAILED. Every row that is not VERIFIED, SKIPPED or EXCLUDED is reported as outstanding.
    """
    found = _index_listing(listing)
    rows = _read(ledger)
    out: dict = {"missing": [], "size_mismatch": [], "outstanding": []}
    for row in rows:
        earlier_size_failure = row["Status"] == "FAILED" and row["Message"].startswith("Target size")
        if row["Route"] in PENDING_STATUS and (row["Status"] in {"UPLOADED", "VERIFIED"} or earlier_size_failure):
            problem = _verify_row(row, found)
            if problem != "ok":
                out["missing" if problem == "missing" else "size_mismatch"].append(
                    {"file": row["SourceRelativePath"], "message": row["Message"]})
    _write(ledger, rows)
    out["outstanding"] = [{"file": r["SourceRelativePath"], "route": r["Route"], "status": r["Status"]}
                          for r in rows if r["Status"] not in {"VERIFIED", "SKIPPED", "EXCLUDED"}]
    out["verified"] = sum(r["Status"] == "VERIFIED" for r in rows)
    out["skipped"] = sum(r["Status"] == "SKIPPED" for r in rows)
    out["excluded"] = sum(r["Status"] == "EXCLUDED" for r in rows)
    out["total"] = len(rows)
    out["ok"] = not out["outstanding"]
    return out


def record(ledger: Path, file_url: str, status: str, message: str) -> None:
    """Record the outcome for one file."""
    if status not in STATUSES:
        raise LedgerError(f"Invalid status '{status}'; use one of {sorted(STATUSES)}")
    rows = _read(ledger)
    hit = [r for r in rows if r["FileUrl"] == file_url]
    if not hit:
        raise LedgerError(f"FileUrl not in ledger: {file_url}")
    hit[0].update(Status=status, Message=message)
    _write(ledger, rows)


def mark_converted(ledger: Path, file_url: str, html: Path) -> None:
    """Point a static-html row at its converted, validated HTML file and mark it CONVERTED."""
    if not html.is_file():
        raise LedgerError(f"Converted file not found: {html}")
    rows = _read(ledger)
    hit = [r for r in rows if r["FileUrl"] == file_url]
    if not hit:
        raise LedgerError(f"FileUrl not in ledger: {file_url}")
    if hit[0]["Route"] != "static-html":
        raise LedgerError(f"Not a static-html page row: {file_url}")
    hit[0].update(LocalPath=str(html.resolve()), Sha256=hashlib.sha256(html.read_bytes()).hexdigest(),
                  Status="CONVERTED", Message="Converted and validated; ready to upload")
    _write(ledger, rows)


def summarize(ledger: Path) -> dict:
    """Count rows by route/status."""
    rows = _read(ledger)
    return {"total": len(rows), "by_route_status": dict(Counter(f"{r['Route']}/{r['Status']}" for r in rows))}


def _csv_set(text: str) -> set[str]:
    """Split a comma-separated CLI value into a set, ignoring empty items."""
    return {e for e in text.split(",") if e}


# (flag, kwargs) pairs per subcommand, so the parser is declarative data
_LEDGER = ("--ledger", {"type": Path, "required": True})
# Optional write-through to the overall tracker (migration_status_tracker.py) after a mutating command.
_TRACK = [("--tracker", {"type": Path, "default": None}), ("--environment", {"default": "DEV"})]
_MUTATING = {"plan", "stage", "upload-next", "mark-converted", "reconcile", "record", "verify"}
_COMMANDS: dict[str, list[tuple[str, dict]]] = {
    "plan": [("--inventory", {"type": Path, "required": True}), ("--source-library", {"required": True}),
             ("--source-web-url", {"default": ""}), ("--target-library", {"required": True}),
             ("--target-root", {"default": ""}), ("--skip-extensions", {"default": ""}), _LEDGER, *_TRACK],
    "find-inventory": [("--search-dir", {"type": Path, "action": "append", "required": True}),
                       ("--source-library", {"required": True}), ("--source-web-url", {"default": ""})],
    "export-inventory": [("--inventory", {"type": Path, "required": True}), ("--source-library", {"required": True}),
                         ("--source-web-url", {"default": ""}), ("--output", {"type": Path, "required": True}),
                         *_TRACK],
    "stage": [_LEDGER, ("--downloads", {"type": Path, "required": True}), *_TRACK],
    "upload-plan": [_LEDGER, ("--output", {"type": Path, "required": True}),
                    ("--limit", {"type": int, "default": None}), ("--extensions", {"default": ""})],
    "upload-next": [_LEDGER, ("--uploader", {"type": Path, "required": True}),
                    ("--config", {"type": Path, "required": True}), ("--count", {"type": int, "default": 1}),
                    ("--extensions", {"default": ""}), ("--execute", {"action": "store_true"}),
                    ("--route", {"choices": sorted(PENDING_STATUS), "default": "upload"}),
                    ("--library-creator", {"type": Path, "default": None}),
                    ("--no-create-library", {"action": "store_true"}), *_TRACK],
    "mark-converted": [_LEDGER, ("--file-url", {"required": True}), ("--html", {"type": Path, "required": True}), *_TRACK],
    "reconcile": [_LEDGER, ("--listing", {"type": Path, "required": True}), *_TRACK],
    "verify": [_LEDGER, ("--listing", {"type": Path, "required": True}), *_TRACK],
    "record": [_LEDGER, ("--file-url", {"required": True}), ("--status", {"required": True}),
               ("--message", {"default": ""}), *_TRACK],
    "summary": [_LEDGER],
}


def _build_parser() -> argparse.ArgumentParser:
    """Build the argparse parser with one subcommand per _COMMANDS entry."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, args in _COMMANDS.items():
        q = sub.add_parser(name)
        for flag, kwargs in args:
            q.add_argument(flag, **kwargs)
    return ap


def ledger_location_warning(ledger: Path) -> str | None:
    """Warn when a ledger lives in the git-ignored repo-level temp/ folder, where other devs cannot see it."""
    try:
        first = Path(ledger).resolve().relative_to(Path.cwd().resolve()).parts[0]
    except (ValueError, IndexError):
        return None
    if first.lower() == "temp":
        return ("WARNING: ledger is under git-ignored temp/; keep ledgers in "
                "inventory/ledgers/<Web>-<Library>/ledger.csv so other developers can see them")
    return None


def _sync_tracker(tracker: Path, ledger: Path, environment: str) -> None:
    """Write the whole ledger through to the overall tracker (idempotent); reports untracked rows."""
    import migration_status_tracker as trk
    try:
        res = trk.sync_from_ledger(tracker, ledger, environment)
    except trk.TrackerError as exc:
        raise LedgerError(str(exc)) from exc
    print(f"tracker {environment}: {res['updated']} updated, {res['untracked']} not in inventory", file=sys.stderr)


def _cmd_find_inventory(a: argparse.Namespace) -> int | None:
    """Print the newest covering inventory; exit 3 when none exists."""
    hit = find_inventory(a.search_dir, a.source_library, a.source_web_url)
    if hit is None:
        print("NOT FOUND: run collect-sharepoint-content-inventory.ps1 (user-run)", file=sys.stderr)
        return 3
    print(hit)
    return 0


def _cmd_export_inventory(a: argparse.Namespace) -> int | None:
    """Write the library-scoped inventory and print its extension list."""
    exts = export_inventory(a.inventory, a.source_library, a.source_web_url, a.output,
                            _tracker_done(a.tracker, a.environment))
    print(json.dumps({"output": str(a.output), "extensions": ",".join(exts)}))
    return 0


def _tracker_done(tracker: Path | None, environment: str) -> dict[str, str]:
    """Files the overall tracker already marks DONE, so planning and downloads skip them."""
    import migration_status_tracker as trk
    return trk.done_status_by_url(tracker, environment)


def _cmd_upload_next(a: argparse.Namespace) -> int | None:
    """Run upload-next; a dry run prints the uploader plan instead of the ledger summary."""
    res = upload_next(a.ledger, a.uploader, a.config, a.count, _csv_set(a.extensions) or None, a.execute,
                      route=a.route, library_creator=a.library_creator, allow_create=not a.no_create_library)
    if res["dry_run"]:
        print(res["output"] or res["error"])
        return 0 if res["returncode"] == 0 else 2
    print("\n".join(format_batch(res["files"])), file=sys.stderr)
    return None


def _cmd_verify(a: argparse.Namespace) -> int | None:
    """Print the verification report as JSON; exit 4 when any file is not confirmed on the target."""
    res = verify(a.ledger, a.listing)
    print(json.dumps(res, indent=2))
    return 0 if res["ok"] else 4


# Handlers returning None fall through to printing the ledger summary.
_HANDLERS = {
    "verify": _cmd_verify,
    "find-inventory": _cmd_find_inventory,
    "export-inventory": _cmd_export_inventory,
    "plan": lambda a: build_plan(a.inventory, a.source_library, a.target_library, a.target_root, a.ledger,
                                 _csv_set(a.skip_extensions), a.source_web_url,
                                 _tracker_done(a.tracker, a.environment)) and None,
    "stage": lambda a: stage(a.ledger, a.downloads),
    "upload-plan": lambda a: upload_plan(a.ledger, a.output, a.limit, _csv_set(a.extensions) or None) and None,
    "upload-next": _cmd_upload_next,
    "reconcile": lambda a: reconcile(a.ledger, a.listing),
    "record": lambda a: record(a.ledger, a.file_url, a.status, a.message),
    "mark-converted": lambda a: mark_converted(a.ledger, a.file_url, a.html),
    "summary": lambda a: None,
}


def default_tracker() -> Path | None:
    """Return the tracker named in migration-paths.json (cwd or a parent) if that file exists, else None."""
    for d in [Path.cwd(), *Path.cwd().parents]:
        f = d / "migration-paths.json"
        if f.exists():
            rel = json.loads(f.read_text(encoding="utf-8")).get("tracker")
            tracker = d / rel if rel else None
            return tracker if tracker and tracker.is_file() else None
    return None


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: 0 ok, 2 error, 3 no covering inventory (find-inventory)."""
    a = _build_parser().parse_args(argv)
    if hasattr(a, "tracker") and a.tracker is None:
        a.tracker = default_tracker()
    warning = ledger_location_warning(a.ledger) if getattr(a, "ledger", None) else None
    if warning:
        print(warning, file=sys.stderr)
    try:
        rc = _HANDLERS[a.cmd](a)
        if getattr(a, "tracker", None) and a.cmd in _MUTATING and not (a.cmd == "upload-next" and not a.execute):
            _sync_tracker(a.tracker, a.ledger, a.environment)
        if rc is None:
            print(json.dumps(summarize(a.ledger)))
            return 0
        return rc
    except LedgerError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
