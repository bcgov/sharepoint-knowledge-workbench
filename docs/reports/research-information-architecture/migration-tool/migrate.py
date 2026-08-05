#!/usr/bin/env python3
"""
Research IA migration tool. Consumes an approved research-migration-manifest.json
and (in --execute mode only) performs git-aware moves/archives for entries whose
destination_status == 'approved', plus rewrites the inbound references recorded
against each moved entry. Dry-run is the default and only mode until --execute
is explicitly passed. Retain entries are validated but never touched.

Usage:
    python3 migrate.py validate       --manifest M.json --schema S.json
    python3 migrate.py gen-exec-plan  --manifest M.json --out PLAN.json
    python3 migrate.py validate-exec  --plan PLAN.json --schema EXEC_S.json
    python3 migrate.py dry-run        --manifest M.json --repo-root R
    python3 migrate.py execute        --manifest M.json --repo-root R
    python3 migrate.py verify         --manifest M.json --repo-root R --report REPORT.json
    python3 migrate.py rollback       --report REPORT.json --repo-root R

See README.md in this directory for full usage and design notes.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


class MigrationError(Exception):
    pass


def load_json(path):
    with open(path) as f:
        return json.load(f)


def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def approved_entries(manifest):
    """Only entries explicitly approved for execution. This is the hard boundary --
    'recommended' and 'tentative' entries are validated for shape but never acted on."""
    return [e for e in manifest["entries"] if e.get("destination_status") == "approved"]


# --------------------------------------------------------------------------
# Tree policy: three distinct concepts, not one blanket exclusion list.
# --------------------------------------------------------------------------

# Trees the migration tool must NEVER write into, period -- no manifest entry
# can override this. These are owned by other lifecycles (phase specs/plans,
# plugin code) entirely outside this IA effort's authority.
PROHIBITED_MODIFICATION_TREES = ["docs/superpowers/", "plugins/"]

# Trees that are prohibited as a DESTINATION by default, but may receive a
# write if -- and only if -- the specific manifest entry explicitly names that
# exact destination AND carries destination_exception_approved: true. This is
# how res-015 (archive into docs/reports/phase-4-native-sharepoint-skills/)
# is handled: docs/reports/ is not a corpus tree and is not a free-for-all
# destination, but this one named exception is real and repo-consistent
# (evidence belongs beside its 26 sibling files).
RESTRICTED_DESTINATION_TREES = ["docs/reports/"]


def check_tree_policy(dest_rel_path, entry):
    """Raises MigrationError if dest_rel_path violates tree policy for this entry."""
    for prohibited in PROHIBITED_MODIFICATION_TREES:
        if dest_rel_path.startswith(prohibited):
            raise MigrationError(
                f"{entry.get('id','?')}: destination '{dest_rel_path}' is under a permanently "
                f"prohibited tree '{prohibited}' -- no exception is possible."
            )
    for restricted in RESTRICTED_DESTINATION_TREES:
        if dest_rel_path.startswith(restricted):
            if not entry.get("destination_exception_approved"):
                raise MigrationError(
                    f"{entry.get('id','?')}: destination '{dest_rel_path}' is under a restricted "
                    f"tree '{restricted}'. This requires the entry to carry "
                    f"destination_exception_approved: true. It does not."
                )
    return True


def assert_no_excluded_tree_touched(operations, repo_root, manifest_by_id):
    """Applies check_tree_policy to every planned destination, plus refuses to
    ever touch a PROHIBITED source path regardless of entry approval."""
    for op in operations:
        entry = manifest_by_id.get(op["id"], {})
        src_rel = op.get("source_path")
        if src_rel:
            for prohibited in PROHIBITED_MODIFICATION_TREES:
                if src_rel.startswith(prohibited):
                    raise MigrationError(
                        f"{op['id']}: source '{src_rel}' is under a permanently "
                        f"prohibited tree '{prohibited}'."
                    )
        dest_rel = op.get("dest_path")
        if dest_rel:
            check_tree_policy(dest_rel, entry)


# --------------------------------------------------------------------------
# Preflight
# --------------------------------------------------------------------------

def preflight(manifest, repo_root):
    """Checks that must pass before any plan is built, approved or not.
    Raises MigrationError on the first failure -- no partial continuation."""
    repo_root = Path(repo_root)
    seen_destinations = {}
    for e in manifest["entries"]:
        src = repo_root / e["source_path"]
        dest_dir = e.get("proposed_destination")
        fname = e.get("proposed_filename") or e.get("current_filename")
        dest = repo_root / dest_dir / fname if dest_dir else None
        recorded_hash = e.get("source_hash")

        # Idempotency-aware existence check: if the source is gone but the
        # destination already matches, treat as "already applied" and don't
        # fail preflight for it -- see determine_operation_state() below for
        # the authoritative classification used at execute time. Preflight
        # here only needs to reject truly broken states.
        source_exists = src.exists()
        dest_exists = dest.exists() if dest else False

        if not source_exists and not dest_exists:
            raise MigrationError(
                f"{e['id']}: neither source ({src}) nor destination ({dest}) exists. "
                f"Cannot determine state."
            )

        if source_exists:
            if recorded_hash and len(recorded_hash) == 64:
                actual = file_hash(src)
                if actual != recorded_hash:
                    raise MigrationError(
                        f"{e['id']}: hash mismatch. Source file changed since cataloging. "
                        f"recorded={recorded_hash} actual={actual}"
                    )

        if dest_dir and fname:
            key = (dest_dir.lower(), fname.lower())
            if key in seen_destinations and seen_destinations[key] != e["id"]:
                raise MigrationError(
                    f"{e['id']}: destination collision with {seen_destinations[key]} "
                    f"at {dest_dir}/{fname} (case-insensitive match)"
                )
            seen_destinations[key] = e["id"]
    return True


def determine_operation_state(entry, repo_root):
    """Classifies the real-world state of one approved move/rename/archive entry.
    Returns one of: 'pending' (do the move), 'already-applied' (skip, success),
    or raises MigrationError for any inconsistent state.
    """
    repo_root = Path(repo_root)
    src = repo_root / entry["source_path"]
    dest_dir = entry.get("proposed_destination")
    fname = entry.get("proposed_filename") or entry.get("current_filename")
    dest = repo_root / dest_dir / fname
    recorded_hash = entry.get("source_hash")

    source_exists = src.exists()
    dest_exists = dest.exists()

    if source_exists and dest_exists:
        raise MigrationError(
            f"{entry['id']}: BOTH source ({src}) and destination ({dest}) exist -- "
            f"inconsistent state, cannot determine whether this is pre-move, "
            f"post-move, or a duplication. Refusing to guess."
        )

    if not source_exists and not dest_exists:
        raise MigrationError(
            f"{entry['id']}: neither source ({src}) nor destination ({dest}) exists."
        )

    if source_exists and not dest_exists:
        return "pending"

    # not source_exists and dest_exists: either already applied, or a hash mismatch
    if recorded_hash and len(recorded_hash) == 64:
        dest_hash = file_hash(dest)
        if dest_hash == recorded_hash:
            return "already-applied"
        raise MigrationError(
            f"{entry['id']}: source is absent and destination exists at {dest}, "
            f"but destination hash ({dest_hash}) does not match the manifest's "
            f"recorded source hash ({recorded_hash}). This is not a clean "
            f"already-applied state -- refusing to proceed."
        )
    raise MigrationError(
        f"{entry['id']}: source is absent and destination exists at {dest}, but no "
        f"source_hash is recorded to confirm this is the same content. Refusing to "
        f"classify as already-applied without that proof."
    )


# --------------------------------------------------------------------------
# Reference rewriting
# --------------------------------------------------------------------------

MARKDOWN_LINK_RE = re.compile(r'(!?\[[^\]]*\])\(([^)\s]+)(\s+"[^"]*")?\)')


def resolve_relative(referencing_file_dir: Path, link_target: str, repo_root: Path):
    """Resolves a possibly-relative link target to a repo-relative POSIX path,
    stripping any anchor fragment. Returns (resolved_repo_relative_path, anchor)."""
    anchor = ""
    target = link_target
    if "#" in target:
        target, anchor = target.split("#", 1)
        anchor = "#" + anchor
    if not target:
        return None, anchor  # pure anchor link, e.g. "#section" -- no path to resolve
    if target.startswith(("http://", "https://", "mailto:")):
        return None, anchor  # external link, not a repo-relative reference
    if target.startswith("/"):
        resolved = (repo_root / target.lstrip("/")).resolve()
    else:
        resolved = (referencing_file_dir / target).resolve()
    try:
        rel = resolved.relative_to(repo_root.resolve())
    except ValueError:
        return None, anchor  # resolves outside the repo -- leave alone
    return rel.as_posix(), anchor


def compute_new_relative_link(referencing_file_dir: Path, new_target_repo_rel: str, anchor: str, repo_root: Path):
    """Computes the correct relative link from a referencing file to a new target path."""
    import os
    new_target_abs = (repo_root / new_target_repo_rel).resolve()
    try:
        rel = Path(os.path.relpath(new_target_abs, start=referencing_file_dir.resolve()))
    except ValueError:
        rel = new_target_abs
    return rel.as_posix() + anchor


def find_references_in_file(referencing_path: Path, repo_root: Path, old_target_repo_rel: str):
    """Scans one Markdown file for links/plain-text paths resolving to old_target_repo_rel.
    Returns (hits, text). Both Markdown-link syntax and bare backtick-quoted repo-relative
    path mentions are detected; anything else is left alone as ambiguous.
    """
    text = referencing_path.read_text()
    hits = []
    ref_dir = referencing_path.parent

    for m in MARKDOWN_LINK_RE.finditer(text):
        link_text, target, _title = m.group(1), m.group(2), m.group(3)
        resolved, anchor = resolve_relative(ref_dir, target, repo_root)
        if resolved == old_target_repo_rel:
            hits.append({"kind": "markdown-link", "span": m.span(), "raw": m.group(0),
                         "link_text": link_text, "anchor": anchor})

    for m in re.finditer(r"`([^`]+)`", text):
        candidate = m.group(1)
        if candidate == old_target_repo_rel:
            hits.append({"kind": "plain-path", "span": m.span(), "raw": m.group(0),
                         "link_text": None, "anchor": ""})

    return hits, text


def rewrite_references(entry, referencing_paths, repo_root: Path, dry_run=True):
    """For one moved/renamed entry, rewrites all its recorded inbound references.
    Returns a list of per-file change records. Raises MigrationError if a hit's
    kind is not recognized, rather than guessing at a replacement.
    """
    old_target = entry["source_path"]
    new_dir = entry["proposed_destination"]
    new_fname = entry.get("proposed_filename") or entry["current_filename"]
    new_target = f"{new_dir.rstrip('/')}/{new_fname}"

    changes = []
    for ref_rel in referencing_paths:
        ref_path = repo_root / ref_rel
        if not ref_path.exists():
            continue
        hits, text = find_references_in_file(ref_path, repo_root, old_target)
        if not hits:
            continue

        new_text = text
        offset = 0
        applied = []
        for h in sorted(hits, key=lambda x: x["span"][0]):
            start, end = h["span"]
            start += offset
            end += offset
            if h["kind"] == "markdown-link":
                new_link = compute_new_relative_link(ref_path.parent, new_target, h["anchor"], repo_root)
                replacement = f'{h["link_text"]}({new_link})'
            elif h["kind"] == "plain-path":
                replacement = f"`{new_target}`"
            else:
                raise MigrationError(f"{entry['id']}: unrecognized reference kind in {ref_rel}, refusing to guess")
            new_text = new_text[:start] + replacement + new_text[end:]
            offset += len(replacement) - (end - start)
            applied.append({"old": h["raw"], "new": replacement})

        changes.append({"file": ref_rel, "edits": applied})
        if not dry_run:
            ref_path.write_text(new_text)

    return changes


def verify_no_stale_references(entries_moved, repo_root: Path, retained_historical_literals=None):
    """Post-execution check: scans committed Markdown for any remaining reference
    to an old_path that was moved, excluding paths explicitly approved for
    retention as historical literals."""
    retained = set(retained_historical_literals or [])
    stale = []
    old_paths = {e["source_path"] for e in entries_moved}
    for md_file in repo_root.rglob("*.md"):
        rel = md_file.relative_to(repo_root).as_posix()
        if any(rel.startswith(t) for t in PROHIBITED_MODIFICATION_TREES):
            continue
        try:
            text = md_file.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        for old in old_paths:
            if old in text and (rel, old) not in retained:
                stale.append({"file": rel, "stale_reference": old})
    return stale


# --------------------------------------------------------------------------
# Execution plan generation + strict validation
# --------------------------------------------------------------------------

REQUIRED_EXEC_FIELDS = ["id", "source_path", "source_hash", "proposed_operation", "destination_status"]


def generate_execution_plan(manifest):
    """Extracts ONLY approved entries into a standalone execution-plan document.
    This is what gets validated against the strict execution schema -- not the
    full proposal manifest, which legitimately contains recommended/tentative
    entries that are not execution-ready by design."""
    keep_keys = [
        "id", "source_path", "source_hash", "current_filename",
        "proposed_operation", "proposed_destination", "proposed_filename",
        "destination_status", "destination_exception_approved",
        "inbound_references",
    ]
    plan_entries = []
    for e in approved_entries(manifest):
        plan_entries.append({k: e[k] for k in keep_keys if k in e})
    return {"generated_from": manifest.get("manifest_id"), "entries": plan_entries}


def validate_execution_plan(plan, manifest_by_id):
    """Strict, hand-written validation beyond what JSON Schema alone can express --
    duplicate-destination and tree-policy checks need real code, not just types."""
    seen = {}
    for e in plan["entries"]:
        for field in REQUIRED_EXEC_FIELDS:
            if not e.get(field):
                raise MigrationError(f"{e.get('id','?')}: execution plan missing required field '{field}'")
        if e["destination_status"] != "approved":
            raise MigrationError(f"{e['id']}: execution plan contains a non-approved entry")
        op = e["proposed_operation"]
        if op in ("move", "rename", "archive"):
            if not e.get("proposed_destination") or not e.get("proposed_filename"):
                raise MigrationError(f"{e['id']}: {op} missing destination/filename")
            key = (e["proposed_destination"].lower(), e["proposed_filename"].lower())
            if key in seen:
                raise MigrationError(f"{e['id']}: duplicate case-insensitive destination with {seen[key]}")
            seen[key] = e["id"]
            full_entry = manifest_by_id.get(e["id"], {})
            check_tree_policy(f"{e['proposed_destination'].rstrip('/')}/{e['proposed_filename']}", full_entry)
    return True


# --------------------------------------------------------------------------
# Plan building (dry-run / execute)
# --------------------------------------------------------------------------

def build_plan(manifest, repo_root, require_approved=True):
    entries = approved_entries(manifest) if require_approved else manifest["entries"]
    plan = []
    for e in entries:
        op = e.get("proposed_operation")
        if op in (None, "retain", "exclude"):
            plan.append({
                "id": e["id"], "operation": op or "unspecified", "source_path": e["source_path"],
                "dest_path": None, "note": "no filesystem action" if op in ("retain", "exclude") else "MISSING OPERATION"
            })
            continue
        if op in ("move", "rename", "archive"):
            dest_dir = e.get("proposed_destination")
            fname = e.get("proposed_filename") or e.get("current_filename")
            if not dest_dir or not fname:
                raise MigrationError(f"{e['id']}: operation={op} but destination/filename incomplete")
            dest_path = f"{dest_dir.rstrip('/')}/{fname}"
            plan.append({
                "id": e["id"], "operation": op, "source_path": e["source_path"],
                "dest_path": dest_path, "note": f"git mv {e['source_path']} -> {dest_path}"
            })
        elif op == "synthesize":
            plan.append({"id": e["id"], "operation": op, "source_path": e["source_path"], "dest_path": None,
                         "note": "synthesis requires separate approval -- not auto-executed"})
        else:
            raise MigrationError(f"{e['id']}: unrecognized operation '{op}'")
    return plan


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------

def cmd_validate(args):
    manifest = load_json(args.manifest)
    schema = load_json(args.schema)
    import jsonschema
    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors(manifest))
    if errors:
        for e in errors:
            print(f"SCHEMA ERROR: {'/'.join(str(p) for p in e.path)}: {e.message}", file=sys.stderr)
        return 1
    print(f"Schema valid: {len(manifest['entries'])} entries.")
    return 0


def cmd_gen_exec_plan(args):
    manifest = load_json(args.manifest)
    plan = generate_execution_plan(manifest)
    manifest_by_id = {e["id"]: e for e in manifest["entries"]}
    validate_execution_plan(plan, manifest_by_id)
    with open(args.out, "w") as f:
        json.dump(plan, f, indent=2)
    print(f"Execution plan generated: {len(plan['entries'])} approved entries -> {args.out}")
    return 0


def cmd_validate_exec(args):
    plan = load_json(args.plan)
    schema = load_json(args.schema)
    import jsonschema
    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors(plan))
    if errors:
        for e in errors:
            print(f"EXEC SCHEMA ERROR: {'/'.join(str(p) for p in e.path)}: {e.message}", file=sys.stderr)
        return 1
    print(f"Execution plan schema valid: {len(plan['entries'])} entries.")
    return 0


def cmd_dry_run(args):
    manifest = load_json(args.manifest)
    preflight(manifest, args.repo_root)
    manifest_by_id = {e["id"]: e for e in manifest["entries"]}
    plan_approved = build_plan(manifest, args.repo_root, require_approved=True)
    assert_no_excluded_tree_touched(plan_approved, Path(args.repo_root), manifest_by_id)

    print("=== DRY RUN (no changes made) ===")
    print(f"Total entries in manifest: {len(manifest['entries'])}")
    print(f"Entries with destination_status='approved' (execution set): {len(plan_approved)}")
    print()

    ref_changes_all = []
    for op in plan_approved:
        print(f"  [{op['operation']:8s}] {op['id']}: {op['note']}")
        if op["operation"] in ("move", "rename", "archive"):
            entry = manifest_by_id[op["id"]]
            state = determine_operation_state(entry, args.repo_root)
            print(f"      state: {state}")
            refs = entry.get("inbound_references", [])
            referencing_paths = [r.split(" ")[0].strip("`") for r in refs if "/" in r.split(" ")[0]]
            changes = rewrite_references(entry, referencing_paths, Path(args.repo_root), dry_run=True)
            if changes:
                print(f"      would update {len(changes)} referencing file(s):")
                for c in changes:
                    print(f"        {c['file']}: {len(c['edits'])} edit(s)")
            ref_changes_all.extend([{"entry": op["id"], **c} for c in changes])

    by_status = {}
    for e in manifest["entries"]:
        s = e.get("destination_status", "MISSING")
        by_status[s] = by_status.get(s, 0) + 1
    print()
    print("Full manifest destination_status breakdown (informational, not executed):")
    for s, c in by_status.items():
        print(f"  {s}: {c}")

    report = {
        "mode": "dry-run",
        "manifest_id": manifest.get("manifest_id"),
        "total_entries": len(manifest["entries"]),
        "execution_set_size": len(plan_approved),
        "execution_set": plan_approved,
        "reference_changes": ref_changes_all,
        "destination_status_breakdown": by_status,
    }
    if args.report:
        with open(args.report, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nDry-run report written to {args.report}")
    return 0


def cmd_execute(args):
    manifest = load_json(args.manifest)
    preflight(manifest, args.repo_root)
    manifest_by_id = {e["id"]: e for e in manifest["entries"]}
    plan = build_plan(manifest, args.repo_root, require_approved=True)
    assert_no_excluded_tree_touched(plan, Path(args.repo_root), manifest_by_id)

    actionable = [op for op in plan if op["operation"] in ("move", "rename", "archive")]
    if not actionable:
        print("No approved move/rename/archive operations to execute. "
              "(This is expected if only 'retain' entries are currently approved.)")
        return 0

    repo_root = Path(args.repo_root)
    executed = []
    skipped_already_applied = []
    rollback_map = []
    reference_changes = []
    try:
        for op in actionable:
            entry = manifest_by_id[op["id"]]
            state = determine_operation_state(entry, repo_root)

            if state == "already-applied":
                skipped_already_applied.append({"id": op["id"], "dest_path": op["dest_path"]})
                continue

            src = repo_root / op["source_path"]
            dest = repo_root / op["dest_path"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            pre_hash = file_hash(src)
            subprocess.run(["git", "mv", str(src), str(dest)], cwd=repo_root, check=True)
            post_hash = file_hash(dest)
            if pre_hash != post_hash:
                raise MigrationError(f"{op['id']}: hash changed across move -- not move-only, aborting")
            executed.append({**op, "pre_hash": pre_hash, "post_hash": post_hash})
            rollback_map.append({"from": op["dest_path"], "to": op["source_path"]})

            refs = entry.get("inbound_references", [])
            referencing_paths = [r.split(" ")[0].strip("`") for r in refs if "/" in r.split(" ")[0]]
            changes = rewrite_references(entry, referencing_paths, repo_root, dry_run=False)
            reference_changes.extend([{"entry": op["id"], **c} for c in changes])

    except Exception as ex:
        print(f"EXECUTION FAILED, no partial continuation: {ex}", file=sys.stderr)
        print(f"Operations completed before failure: {len(executed)}", file=sys.stderr)
        if executed:
            print("Rollback map for completed operations (not auto-applied):", file=sys.stderr)
            print(json.dumps(rollback_map, indent=2), file=sys.stderr)
        return 1

    moved_entries = [manifest_by_id[op["id"]] for op in executed]
    stale = verify_no_stale_references(moved_entries, repo_root)
    if stale:
        print("WARNING: stale references remain after execution:", file=sys.stderr)
        for s in stale:
            print(f"  {s['file']}: still references {s['stale_reference']}", file=sys.stderr)

    report = {
        "mode": "execute",
        "executed": executed,
        "skipped_already_applied": skipped_already_applied,
        "reference_changes": reference_changes,
        "stale_references_remaining": stale,
        "rollback_map": rollback_map,
    }
    if args.report:
        with open(args.report, "w") as f:
            json.dump(report, f, indent=2)
    print(f"Executed {len(executed)} operations, skipped {len(skipped_already_applied)} already-applied. "
          f"Rewrote references in {len(reference_changes)} file-entry pairs. Report: {args.report}")
    return 0


def cmd_verify(args):
    report = load_json(args.report)
    repo_root = Path(args.repo_root)
    ok = True
    for op in report.get("executed", []):
        dest = repo_root / op["dest_path"]
        if not dest.exists():
            print(f"MISSING: {op['id']} expected at {dest}", file=sys.stderr)
            ok = False
            continue
        actual = file_hash(dest)
        if actual != op["post_hash"]:
            print(f"HASH MISMATCH after move: {op['id']}", file=sys.stderr)
            ok = False
        src = repo_root / op["source_path"]
        if src.exists():
            print(f"SOURCE STILL PRESENT (should be gone after move): {op['id']} at {src}", file=sys.stderr)
            ok = False
    if report.get("stale_references_remaining"):
        print(f"STALE REFERENCES REMAIN: {len(report['stale_references_remaining'])}", file=sys.stderr)
        ok = False
    print("VERIFY: PASS" if ok else "VERIFY: FAIL")
    return 0 if ok else 1


def cmd_rollback(args):
    report = load_json(args.report)
    repo_root = Path(args.repo_root)
    for entry in reversed(report.get("rollback_map", [])):
        src = repo_root / entry["from"]
        dest = repo_root / entry["to"]
        if src.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "mv", str(src), str(dest)], cwd=repo_root, check=True)
            print(f"Rolled back: {entry['from']} -> {entry['to']}")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate")
    p.add_argument("--manifest", required=True)
    p.add_argument("--schema", required=True)
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("gen-exec-plan")
    p.add_argument("--manifest", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_gen_exec_plan)

    p = sub.add_parser("validate-exec")
    p.add_argument("--plan", required=True)
    p.add_argument("--schema", required=True)
    p.set_defaults(func=cmd_validate_exec)

    p = sub.add_parser("dry-run")
    p.add_argument("--manifest", required=True)
    p.add_argument("--repo-root", required=True)
    p.add_argument("--report", default=None)
    p.set_defaults(func=cmd_dry_run)

    p = sub.add_parser("execute")
    p.add_argument("--manifest", required=True)
    p.add_argument("--repo-root", required=True)
    p.add_argument("--report", default=None)
    p.set_defaults(func=cmd_execute)

    p = sub.add_parser("verify")
    p.add_argument("--manifest", required=True)
    p.add_argument("--repo-root", required=True)
    p.add_argument("--report", required=True)
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("rollback")
    p.add_argument("--report", required=True)
    p.add_argument("--repo-root", required=True)
    p.set_defaults(func=cmd_rollback)

    args = parser.parse_args()
    try:
        return args.func(args)
    except MigrationError as e:
        print(f"MIGRATION ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
