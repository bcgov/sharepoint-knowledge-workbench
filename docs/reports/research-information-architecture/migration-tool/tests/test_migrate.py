#!/usr/bin/env python3
"""
Tests for migrate.py, run against a temporary fixture repository -- never the real corpus.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import migrate  # noqa: E402


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


class FixtureRepo:
    """Creates a throwaway git repo with a few files to migrate."""

    def __enter__(self):
        self.tmp = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q"], cwd=self.tmp, check=True)
        subprocess.run(["git", "config", "user.email", "test@test"], cwd=self.tmp, check=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=self.tmp, check=True)
        (self.tmp / "docs" / "research").mkdir(parents=True)
        (self.tmp / "docs" / "superpowers").mkdir(parents=True)
        (self.tmp / "docs" / "reports" / "phase-4-native-sharepoint-skills").mkdir(parents=True)
        self.file_a = self.tmp / "docs" / "research" / "a.md"
        self.file_a.write_text("# A\ncontent a\n")
        self.file_excluded = self.tmp / "docs" / "superpowers" / "excluded.md"
        self.file_excluded.write_text("# excluded\n")
        subprocess.run(["git", "add", "-A"], cwd=self.tmp, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=self.tmp, check=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.tmp, ignore_errors=True)


def base_entry(repo, dest_status="approved", operation="move", dest="docs/research/subject", fname="a-renamed.md"):
    return {
        "id": "test-001",
        "source_path": "docs/research/a.md",
        "source_hash": sha256(repo.file_a),
        "current_filename": "a.md",
        "proposed_operation": operation,
        "proposed_destination": dest,
        "proposed_filename": fname,
        "destination_status": dest_status,
        "inbound_references": [],
    }


def base_manifest(repo, **kw):
    return {"manifest_id": "test", "entries": [base_entry(repo, **kw)]}


# --------------------------------------------------------------------------
# Preflight / collisions / hashes
# --------------------------------------------------------------------------

class TestPreflight(unittest.TestCase):
    def test_missing_source_stops_processing(self):
        with FixtureRepo() as repo:
            m = base_manifest(repo)
            m["entries"][0]["source_path"] = "docs/research/does-not-exist.md"
            with self.assertRaises(migrate.MigrationError):
                migrate.preflight(m, repo.tmp)

    def test_hash_mismatch_stops_processing(self):
        with FixtureRepo() as repo:
            m = base_manifest(repo)
            m["entries"][0]["source_hash"] = "0" * 64
            with self.assertRaises(migrate.MigrationError):
                migrate.preflight(m, repo.tmp)

    def test_destination_collision_stops_processing(self):
        with FixtureRepo() as repo:
            other = repo.tmp / "docs" / "research" / "b.md"
            other.write_text("# B\n")
            subprocess.run(["git", "add", "-A"], cwd=repo.tmp, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "add b"], cwd=repo.tmp, check=True)
            m = base_manifest(repo)
            m["entries"].append({
                **base_entry(repo, fname="A-RENAMED.md"),  # case-insensitive collision
                "id": "test-002", "source_path": "docs/research/b.md", "source_hash": sha256(other),
            })
            with self.assertRaises(migrate.MigrationError):
                migrate.preflight(m, repo.tmp)

    def test_hash_pass_and_no_collision_succeeds(self):
        with FixtureRepo() as repo:
            self.assertTrue(migrate.preflight(base_manifest(repo), repo.tmp))


# --------------------------------------------------------------------------
# Approval gate
# --------------------------------------------------------------------------

class TestApprovalGate(unittest.TestCase):
    def test_recommended_entries_excluded_from_execution_set(self):
        with FixtureRepo() as repo:
            plan = migrate.build_plan(base_manifest(repo, dest_status="recommended"), repo.tmp, require_approved=True)
            self.assertEqual(len(plan), 0, "unapproved entries must never enter the execution set")

    def test_tentative_entries_excluded_from_execution_set(self):
        with FixtureRepo() as repo:
            plan = migrate.build_plan(base_manifest(repo, dest_status="tentative"), repo.tmp, require_approved=True)
            self.assertEqual(len(plan), 0)

    def test_approved_entries_included(self):
        with FixtureRepo() as repo:
            plan = migrate.build_plan(base_manifest(repo), repo.tmp, require_approved=True)
            self.assertEqual(len(plan), 1)
            self.assertEqual(plan[0]["operation"], "move")

    def test_incomplete_approved_entry_rejected(self):
        with FixtureRepo() as repo:
            m = base_manifest(repo)
            del m["entries"][0]["proposed_destination"]
            with self.assertRaises(migrate.MigrationError):
                migrate.build_plan(m, repo.tmp, require_approved=True)


# --------------------------------------------------------------------------
# Tree policy: prohibited vs. restricted-with-exception
# --------------------------------------------------------------------------

class TestTreePolicy(unittest.TestCase):
    def test_prohibited_tree_source_rejected_even_if_approved(self):
        with FixtureRepo() as repo:
            m = {"manifest_id": "test", "entries": [{
                "id": "test-003", "source_path": "docs/superpowers/excluded.md",
                "source_hash": sha256(repo.file_excluded), "current_filename": "excluded.md",
                "proposed_operation": "move", "proposed_destination": "docs/research/subject",
                "proposed_filename": "excluded.md", "destination_status": "approved",
            }]}
            plan = migrate.build_plan(m, repo.tmp, require_approved=True)
            manifest_by_id = {e["id"]: e for e in m["entries"]}
            with self.assertRaises(migrate.MigrationError):
                migrate.assert_no_excluded_tree_touched(plan, repo.tmp, manifest_by_id)

    def test_plugins_tree_remains_protected(self):
        entry = {"id": "x", "destination_exception_approved": True}
        with self.assertRaises(migrate.MigrationError):
            migrate.check_tree_policy("plugins/foo/skill/SKILL.md", entry)

    def test_unauthorized_docs_reports_write_rejected(self):
        # docs/reports/ is restricted -- no destination_exception_approved -> reject.
        entry = {"id": "res-015"}
        with self.assertRaises(migrate.MigrationError):
            migrate.check_tree_policy("docs/reports/phase-4-native-sharepoint-skills/evidence.md", entry)

    def test_exact_approved_archive_destination_accepted(self):
        # res-015-style entry: docs/reports/ write IS allowed when the entry explicitly
        # carries destination_exception_approved: true.
        entry = {"id": "res-015", "destination_exception_approved": True}
        self.assertTrue(
            migrate.check_tree_policy("docs/reports/phase-4-native-sharepoint-skills/evidence.md", entry)
        )

    def test_docs_superpowers_remains_protected_even_with_exception_flag(self):
        # destination_exception_approved does NOT override PROHIBITED_MODIFICATION_TREES --
        # only RESTRICTED_DESTINATION_TREES. superpowers/ and plugins/ have no escape hatch.
        entry = {"id": "x", "destination_exception_approved": True}
        with self.assertRaises(migrate.MigrationError):
            migrate.check_tree_policy("docs/superpowers/plans/foo.md", entry)


# --------------------------------------------------------------------------
# Idempotency -- the corrected version. A second run must detect
# already-applied state and succeed with ZERO changes, not merely fail closed.
# --------------------------------------------------------------------------

class TestIdempotency(unittest.TestCase):
    def test_pending_state_when_only_source_exists(self):
        with FixtureRepo() as repo:
            entry = base_entry(repo)
            state = migrate.determine_operation_state(entry, repo.tmp)
            self.assertEqual(state, "pending")

    def test_already_applied_when_dest_exists_with_matching_hash(self):
        with FixtureRepo() as repo:
            entry = base_entry(repo)
            # Simulate a completed prior move: dest exists with matching content, source gone.
            dest = repo.tmp / "docs" / "research" / "subject" / "a-renamed.md"
            dest.parent.mkdir(parents=True)
            dest.write_text(repo.file_a.read_text())
            repo.file_a.unlink()
            state = migrate.determine_operation_state(entry, repo.tmp)
            self.assertEqual(state, "already-applied")

    def test_fails_closed_when_dest_hash_differs(self):
        with FixtureRepo() as repo:
            entry = base_entry(repo)
            dest = repo.tmp / "docs" / "research" / "subject" / "a-renamed.md"
            dest.parent.mkdir(parents=True)
            dest.write_text("DIFFERENT CONTENT")  # not the same file
            repo.file_a.unlink()
            with self.assertRaises(migrate.MigrationError):
                migrate.determine_operation_state(entry, repo.tmp)

    def test_fails_closed_when_both_source_and_dest_exist(self):
        with FixtureRepo() as repo:
            entry = base_entry(repo)
            dest = repo.tmp / "docs" / "research" / "subject" / "a-renamed.md"
            dest.parent.mkdir(parents=True)
            dest.write_text("duplicate")
            # source (repo.file_a) still exists too -- inconsistent state
            with self.assertRaises(migrate.MigrationError):
                migrate.determine_operation_state(entry, repo.tmp)

    def test_fails_closed_when_neither_exists(self):
        with FixtureRepo() as repo:
            entry = base_entry(repo)
            repo.file_a.unlink()
            with self.assertRaises(migrate.MigrationError):
                migrate.determine_operation_state(entry, repo.tmp)

    def test_second_execute_run_returns_success_with_zero_changes(self):
        """THE CORRECTED IDEMPOTENCY TEST. A successful second run must:
        - exit 0
        - report the entry as skipped_already_applied, not executed again
        - perform zero filesystem changes on the second run
        """
        with FixtureRepo() as repo:
            m = base_manifest(repo)
            manifest_path = repo.tmp.parent / "manifest.json"
            manifest_path.write_text(json.dumps(m))
            report1 = repo.tmp.parent / "report1.json"
            args1 = argparse.Namespace(manifest=str(manifest_path), repo_root=str(repo.tmp), report=str(report1))
            rc1 = migrate.cmd_execute(args1)
            self.assertEqual(rc1, 0)

            status_before_second_run = subprocess.run(
                ["git", "status", "--short"], cwd=repo.tmp, capture_output=True, text=True
            ).stdout

            report2 = repo.tmp.parent / "report2.json"
            args2 = argparse.Namespace(manifest=str(manifest_path), repo_root=str(repo.tmp), report=str(report2))
            rc2 = migrate.cmd_execute(args2)
            self.assertEqual(rc2, 0, "second run of an already-completed move must succeed, not error")

            status_after_second_run = subprocess.run(
                ["git", "status", "--short"], cwd=repo.tmp, capture_output=True, text=True
            ).stdout
            self.assertEqual(status_before_second_run, status_after_second_run,
                              "second run must perform zero additional changes")

            report2_data = json.loads(report2.read_text())
            self.assertEqual(len(report2_data["executed"]), 0)
            self.assertEqual(len(report2_data["skipped_already_applied"]), 1)
            self.assertEqual(report2_data["skipped_already_applied"][0]["id"], "test-001")


# --------------------------------------------------------------------------
# Reference rewriting -- real positive/negative tests, not a documented gap.
# --------------------------------------------------------------------------

class TestReferenceRewriting(unittest.TestCase):
    def test_markdown_link_rewritten_to_new_relative_path(self):
        with FixtureRepo() as repo:
            (repo.tmp / "docs" / "vision").mkdir(parents=True)
            ref = repo.tmp / "docs" / "vision" / "ref.md"
            ref.write_text("See [the doc](../research/a.md) for detail.")
            subprocess.run(["git", "add", "-A"], cwd=repo.tmp, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "add ref"], cwd=repo.tmp, check=True)

            entry = base_entry(repo, dest="docs/research/subject")
            changes = migrate.rewrite_references(entry, ["docs/vision/ref.md"], repo.tmp, dry_run=True)
            self.assertEqual(len(changes), 1)
            self.assertEqual(len(changes[0]["edits"]), 1)
            self.assertIn("subject/a-renamed.md", changes[0]["edits"][0]["new"])

    def test_markdown_link_actually_written_on_execute(self):
        with FixtureRepo() as repo:
            (repo.tmp / "docs" / "vision").mkdir(parents=True)
            ref = repo.tmp / "docs" / "vision" / "ref.md"
            ref.write_text("See [the doc](../research/a.md) for detail.")
            subprocess.run(["git", "add", "-A"], cwd=repo.tmp, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "add ref"], cwd=repo.tmp, check=True)

            entry = base_entry(repo, dest="docs/research/subject")
            entry["inbound_references"] = ["docs/vision/ref.md"]
            m = {"manifest_id": "test", "entries": [entry]}
            manifest_path = repo.tmp.parent / "manifest.json"
            manifest_path.write_text(json.dumps(m))
            args = argparse.Namespace(manifest=str(manifest_path), repo_root=str(repo.tmp), report=None)
            rc = migrate.cmd_execute(args)
            self.assertEqual(rc, 0)

            new_text = ref.read_text()
            self.assertNotIn("../research/a.md", new_text)
            self.assertIn("subject/a-renamed.md", new_text)

    def test_anchor_preserved_across_rewrite(self):
        with FixtureRepo() as repo:
            (repo.tmp / "docs" / "vision").mkdir(parents=True)
            ref = repo.tmp / "docs" / "vision" / "ref.md"
            ref.write_text("See [section](../research/a.md#key-finding) for detail.")
            subprocess.run(["git", "add", "-A"], cwd=repo.tmp, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "add ref"], cwd=repo.tmp, check=True)

            entry = base_entry(repo, dest="docs/research/subject")
            changes = migrate.rewrite_references(entry, ["docs/vision/ref.md"], repo.tmp, dry_run=True)
            self.assertIn("#key-finding", changes[0]["edits"][0]["new"])

    def test_plain_backtick_path_rewritten(self):
        with FixtureRepo() as repo:
            (repo.tmp / "docs" / "vision").mkdir(parents=True)
            ref = repo.tmp / "docs" / "vision" / "ref.md"
            ref.write_text("Cited in `docs/research/a.md` directly.")
            subprocess.run(["git", "add", "-A"], cwd=repo.tmp, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "add ref"], cwd=repo.tmp, check=True)

            entry = base_entry(repo, dest="docs/research/subject")
            changes = migrate.rewrite_references(entry, ["docs/vision/ref.md"], repo.tmp, dry_run=True)
            self.assertEqual(changes[0]["edits"][0]["new"], "`docs/research/subject/a-renamed.md`")

    def test_relative_path_correctness_from_deeper_referencing_file(self):
        with FixtureRepo() as repo:
            deep = repo.tmp / "docs" / "vision" / "sub" / "deep.md"
            deep.parent.mkdir(parents=True)
            deep.write_text("See [x](../../research/a.md).")
            subprocess.run(["git", "add", "-A"], cwd=repo.tmp, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "add deep ref"], cwd=repo.tmp, check=True)

            entry = base_entry(repo, dest="docs/research/subject")
            changes = migrate.rewrite_references(entry, ["docs/vision/sub/deep.md"], repo.tmp, dry_run=True)
            new_link = changes[0]["edits"][0]["new"]
            # Verify the computed relative link actually resolves back to the real new path.
            resolved = (deep.parent / new_link.split("](")[1].rstrip(")")).resolve()
            expected = (repo.tmp / "docs" / "research" / "subject" / "a-renamed.md").resolve()
            self.assertEqual(resolved, expected)

    def test_no_hit_returns_no_changes(self):
        with FixtureRepo() as repo:
            (repo.tmp / "docs" / "vision").mkdir(parents=True)
            ref = repo.tmp / "docs" / "vision" / "ref.md"
            ref.write_text("Unrelated content, no reference here.")
            subprocess.run(["git", "add", "-A"], cwd=repo.tmp, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "add ref"], cwd=repo.tmp, check=True)

            entry = base_entry(repo, dest="docs/research/subject")
            changes = migrate.rewrite_references(entry, ["docs/vision/ref.md"], repo.tmp, dry_run=True)
            self.assertEqual(changes, [])

    def test_post_execution_verify_finds_stale_reference(self):
        with FixtureRepo() as repo:
            (repo.tmp / "docs" / "vision").mkdir(parents=True)
            # A file that still mentions the OLD path via a form the rewriter doesn't
            # touch (plain prose, not a markdown link or backtick path) -- simulates
            # a stale reference surviving execution.
            ref = repo.tmp / "docs" / "vision" / "prose.md"
            ref.write_text("The file docs/research/a.md contains important detail.")
            subprocess.run(["git", "add", "-A"], cwd=repo.tmp, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "add prose ref"], cwd=repo.tmp, check=True)

            entry = base_entry(repo, dest="docs/research/subject")
            stale = migrate.verify_no_stale_references([entry], repo.tmp)
            self.assertEqual(len(stale), 1)
            self.assertEqual(stale[0]["file"], "docs/vision/prose.md")

    def test_retained_historical_literal_excluded_from_stale_check(self):
        with FixtureRepo() as repo:
            (repo.tmp / "docs" / "vision").mkdir(parents=True)
            ref = repo.tmp / "docs" / "vision" / "prose.md"
            ref.write_text("Historically, docs/research/a.md was the record.")
            subprocess.run(["git", "add", "-A"], cwd=repo.tmp, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "add prose ref"], cwd=repo.tmp, check=True)

            entry = base_entry(repo, dest="docs/research/subject")
            stale = migrate.verify_no_stale_references(
                [entry], repo.tmp,
                retained_historical_literals=[("docs/vision/prose.md", "docs/research/a.md")]
            )
            self.assertEqual(stale, [])


# --------------------------------------------------------------------------
# Execution-plan generation and its strict schema
# --------------------------------------------------------------------------

class TestOperationalFilenameIsSourceOfTruth(unittest.TestCase):
    """Regression test for a real bug found in review: an entry can carry an
    advisory-only 'proposedFilename' (camelCase, human-readable title-proposal
    field) that disagrees with the operational 'proposed_filename' (snake_case,
    consumed by build_plan/execute). Every generated artifact -- the plan, the
    dry-run/execute paths, disposition reporting -- must use proposed_filename
    ONLY. This proves it structurally, not just by convention."""

    def test_build_plan_uses_operational_filename_not_advisory_duplicate(self):
        with FixtureRepo() as repo:
            entry = base_entry(repo, fname="operational-name.md")
            entry["proposedFilename"] = "ADVISORY-NAME-SHOULD-BE-IGNORED.md"
            m = {"manifest_id": "test", "entries": [entry]}
            plan = migrate.build_plan(m, repo.tmp, require_approved=True)
            self.assertIn("operational-name.md", plan[0]["dest_path"])
            self.assertNotIn("ADVISORY-NAME-SHOULD-BE-IGNORED", plan[0]["dest_path"])

    def test_gen_exec_plan_uses_operational_filename_not_advisory_duplicate(self):
        with FixtureRepo() as repo:
            entry = base_entry(repo, fname="operational-name.md")
            entry["proposedFilename"] = "ADVISORY-NAME-SHOULD-BE-IGNORED.md"
            m = {"manifest_id": "test", "entries": [entry]}
            plan = migrate.generate_execution_plan(m)
            self.assertEqual(plan["entries"][0]["proposed_filename"], "operational-name.md")

    def test_execute_writes_to_operational_filename_not_advisory(self):
        with FixtureRepo() as repo:
            entry = base_entry(repo, fname="operational-name.md")
            entry["proposedFilename"] = "ADVISORY-NAME-SHOULD-BE-IGNORED.md"
            m = {"manifest_id": "test", "entries": [entry]}
            manifest_path = repo.tmp.parent / "manifest.json"
            manifest_path.write_text(json.dumps(m))
            args = argparse.Namespace(manifest=str(manifest_path), repo_root=str(repo.tmp), report=None)
            migrate.cmd_execute(args)
            dest = repo.tmp / "docs" / "research" / "subject" / "operational-name.md"
            self.assertTrue(dest.exists())
            advisory_dest = repo.tmp / "docs" / "research" / "subject" / "ADVISORY-NAME-SHOULD-BE-IGNORED.md"
            self.assertFalse(advisory_dest.exists())


class TestExecutionPlan(unittest.TestCase):
    def test_gen_exec_plan_excludes_non_approved(self):
        with FixtureRepo() as repo:
            m = {"manifest_id": "test", "entries": [
                base_entry(repo, dest_status="approved"),
                {**base_entry(repo, dest_status="recommended"), "id": "test-002", "source_path": "docs/research/a.md"},
            ]}
            plan = migrate.generate_execution_plan(m)
            self.assertEqual(len(plan["entries"]), 1)
            self.assertEqual(plan["entries"][0]["id"], "test-001")

    def test_validate_execution_plan_rejects_missing_hash(self):
        with FixtureRepo() as repo:
            m = base_manifest(repo)
            plan = migrate.generate_execution_plan(m)
            del plan["entries"][0]["source_hash"]
            manifest_by_id = {e["id"]: e for e in m["entries"]}
            with self.assertRaises(migrate.MigrationError):
                migrate.validate_execution_plan(plan, manifest_by_id)

    def test_validate_execution_plan_rejects_prohibited_destination(self):
        with FixtureRepo() as repo:
            entry = base_entry(repo, dest="plugins/foo")
            m = {"manifest_id": "test", "entries": [entry]}
            plan = migrate.generate_execution_plan(m)
            manifest_by_id = {e["id"]: e for e in m["entries"]}
            with self.assertRaises(migrate.MigrationError):
                migrate.validate_execution_plan(plan, manifest_by_id)

    def test_validate_execution_plan_accepts_approved_reports_exception(self):
        with FixtureRepo() as repo:
            entry = base_entry(repo, dest="docs/reports/phase-4-native-sharepoint-skills")
            entry["destination_exception_approved"] = True
            m = {"manifest_id": "test", "entries": [entry]}
            plan = migrate.generate_execution_plan(m)
            manifest_by_id = {e["id"]: e for e in m["entries"]}
            self.assertTrue(migrate.validate_execution_plan(plan, manifest_by_id))

    def test_validate_execution_plan_rejects_duplicate_case_insensitive_destination(self):
        with FixtureRepo() as repo:
            other = repo.tmp / "docs" / "research" / "b.md"
            other.write_text("# B\n")
            m = {"manifest_id": "test", "entries": [
                base_entry(repo, fname="X.md"),
                {**base_entry(repo, fname="x.md"), "id": "test-002", "source_path": "docs/research/b.md", "source_hash": sha256(other)},
            ]}
            plan = migrate.generate_execution_plan(m)
            manifest_by_id = {e["id"]: e for e in m["entries"]}
            with self.assertRaises(migrate.MigrationError):
                migrate.validate_execution_plan(plan, manifest_by_id)


# --------------------------------------------------------------------------
# Dry-run / execute / verify / rollback end-to-end
# --------------------------------------------------------------------------

class TestDryRunAndExecute(unittest.TestCase):
    def test_dry_run_causes_no_repository_changes(self):
        with FixtureRepo() as repo:
            m = base_manifest(repo)
            manifest_path = repo.tmp.parent / "manifest.json"
            manifest_path.write_text(json.dumps(m))
            status_before = subprocess.run(["git", "status", "--short"], cwd=repo.tmp, capture_output=True, text=True).stdout
            self.assertEqual(status_before, "")

            args = argparse.Namespace(manifest=str(manifest_path), repo_root=str(repo.tmp), report=None)
            rc = migrate.cmd_dry_run(args)
            self.assertEqual(rc, 0)

            status_after = subprocess.run(["git", "status", "--short"], cwd=repo.tmp, capture_output=True, text=True).stdout
            self.assertEqual(status_after, "", "dry-run must leave the working tree untouched")
            self.assertTrue(repo.file_a.exists())

    def test_successful_move_preserves_content_and_hash(self):
        with FixtureRepo() as repo:
            m = base_manifest(repo)
            manifest_path = repo.tmp.parent / "manifest.json"
            manifest_path.write_text(json.dumps(m))
            report_path = repo.tmp.parent / "report.json"

            args = argparse.Namespace(manifest=str(manifest_path), repo_root=str(repo.tmp), report=str(report_path))
            rc = migrate.cmd_execute(args)
            self.assertEqual(rc, 0)

            dest = repo.tmp / "docs" / "research" / "subject" / "a-renamed.md"
            self.assertTrue(dest.exists())
            self.assertFalse(repo.file_a.exists())
            self.assertEqual(dest.read_text(), "# A\ncontent a\n")


class TestVerifyAndRollback(unittest.TestCase):
    def test_execution_report_matches_manifest_operations(self):
        with FixtureRepo() as repo:
            m = base_manifest(repo)
            manifest_path = repo.tmp.parent / "manifest.json"
            manifest_path.write_text(json.dumps(m))
            report_path = repo.tmp.parent / "report.json"
            args = argparse.Namespace(manifest=str(manifest_path), repo_root=str(repo.tmp), report=str(report_path))
            migrate.cmd_execute(args)

            report = json.loads(report_path.read_text())
            self.assertEqual(len(report["executed"]), 1)
            self.assertEqual(report["executed"][0]["id"], "test-001")
            self.assertEqual(report["executed"][0]["pre_hash"], report["executed"][0]["post_hash"])

    def test_verify_passes_after_successful_execute(self):
        with FixtureRepo() as repo:
            m = base_manifest(repo)
            manifest_path = repo.tmp.parent / "manifest.json"
            manifest_path.write_text(json.dumps(m))
            report_path = repo.tmp.parent / "report.json"
            exec_args = argparse.Namespace(manifest=str(manifest_path), repo_root=str(repo.tmp), report=str(report_path))
            migrate.cmd_execute(exec_args)

            verify_args = argparse.Namespace(manifest=str(manifest_path), repo_root=str(repo.tmp), report=str(report_path))
            rc = migrate.cmd_verify(verify_args)
            self.assertEqual(rc, 0)

    def test_rollback_restores_original_location(self):
        with FixtureRepo() as repo:
            m = base_manifest(repo)
            manifest_path = repo.tmp.parent / "manifest.json"
            manifest_path.write_text(json.dumps(m))
            report_path = repo.tmp.parent / "report.json"
            exec_args = argparse.Namespace(manifest=str(manifest_path), repo_root=str(repo.tmp), report=str(report_path))
            migrate.cmd_execute(exec_args)

            rollback_args = argparse.Namespace(report=str(report_path), repo_root=str(repo.tmp))
            migrate.cmd_rollback(rollback_args)

            self.assertTrue(repo.file_a.exists())
            self.assertEqual(sha256(repo.file_a), m["entries"][0]["source_hash"])


if __name__ == "__main__":
    unittest.main()
