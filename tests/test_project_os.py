"""Regression tests for failures that can damage an existing project or its memory.

Run with: python -m unittest discover -s tests -v
All repositories and evidence files are created in temporary directories.
"""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


TOOL = Path(__file__).resolve().parents[1] / "scripts/project_os.py"
SPEC = importlib.util.spec_from_file_location("project_os", TOOL)
project_os = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(project_os)


def run_git(root, *args):
    return subprocess.check_output(
        ["git", "-C", str(root), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", *args],
        text=True, encoding="utf-8", stderr=subprocess.PIPE,
    ).strip()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def file_bytes(root):
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in root.rglob("*") if p.is_file() and ".git" not in p.relative_to(root).parts
    }


@unittest.skipUnless(shutil.which("git"), "Git is required for repository identity and receipt regressions")
class ProjectOSRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="project-os-tests-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "kit"
        self.target = self.root / "project"
        for path, origin in ((self.source, "https://github.com/furenzhong/ai_codex_project_os_starter_kit.git"), (self.target, "https://example.invalid/team/product.git")):
            path.mkdir()
            run_git(path, "init", "-q")
            run_git(path, "remote", "add", "origin", origin)
            (path / "app.txt").write_text("original\n", encoding="utf-8")
            run_git(path, "add", "app.txt")
            run_git(path, "commit", "-qm", "Initial fixture")

    def plan(self, mapping=None):
        mapping_file = None
        if mapping is not None:
            mapping_file = self.root / "mapping.json"
            write_json(mapping_file, mapping)
        return project_os.build_plan(self.source, self.target, str(mapping_file) if mapping_file else None)

    def install(self, mapping=None):
        report, operations = self.plan(mapping)
        project_os.apply_plan(self.target, operations)
        return report

    def check(self):
        return project_os.check_project(self.target)

    def valid_task(self):
        self.install()
        base = run_git(self.target, "rev-parse", "HEAD")
        (self.target / "app.txt").write_text("fixed\n", encoding="utf-8")
        run_git(self.target, "add", "app.txt")
        run_git(self.target, "commit", "-qm", "Implement bounded change")
        result = run_git(self.target, "rev-parse", "HEAD")
        evidence = self.target / "project-os/evidence"
        (evidence / "check.txt").write_text("Fixture acceptance command completed successfully.\n", encoding="utf-8")
        (evidence / "review.txt").write_text("Fixture reviewer inspected app.txt and the recorded result.\n", encoding="utf-8")
        task = {
            "id": "task-001", "objective": "Update the bounded fixture",
            "status": "accepted", "base_revision": base,
            "writable_paths": ["app.txt"], "acceptance_commands": ["python -m unittest"],
            "executor": "worker", "worktree": str(self.target), "session_id": "fixture-session",
            "receipt": "project-os/evidence/task-001.json",
        }
        receipt = {
            "task_id": "task-001", "base_revision": base, "result_revision": result,
            "changed_files": ["app.txt"],
            "checks": [{"command": "python -m unittest", "exit_code": 0, "evidence": "project-os/evidence/check.txt"}],
            "evidence": ["project-os/evidence/check.txt"], "verified_by": "fixture-reviewer",
            "verification_evidence": ["project-os/evidence/review.txt"],
        }
        write_json(self.target / "project-os/tasks/task-001.json", task)
        write_json(self.target / task["receipt"], receipt)
        return task, receipt

    def save_task(self, task, receipt):
        write_json(self.target / "project-os/tasks/task-001.json", task)
        write_json(self.target / task["receipt"], receipt)

    def test_plan_is_read_only_even_when_existing_project_is_dirty(self):
        (self.target / "app.txt").write_bytes(b"dirty business work\x00\r\n")
        (self.target / "untracked.bin").write_bytes(bytes(range(256)))
        before, source_before = file_bytes(self.target), file_bytes(self.source)
        status = run_git(self.target, "status", "--porcelain=v1")
        report, _ = self.plan()
        self.assertTrue(report["ok"])
        self.assertEqual(before, file_bytes(self.target))
        self.assertEqual(source_before, file_bytes(self.source))
        self.assertEqual(status, run_git(self.target, "status", "--porcelain=v1"))

    def test_apply_preserves_dirty_files_entries_remote_and_is_idempotent(self):
        agents = "# 自有规则\r\n先验证代码\r\n".encode("utf-8")
        claude = b"# Existing Claude guidance\nDo not rewrite this."
        (self.target / "AGENTS.md").write_bytes(agents)
        (self.target / "CLAUDE.md").write_bytes(claude)
        (self.target / "app.txt").write_bytes(b"uncommitted business work\r\n")
        before = file_bytes(self.target)
        git_config = (self.target / ".git/config").read_bytes()
        self.install()
        self.assertTrue((self.target / "AGENTS.md").read_bytes().startswith(agents))
        self.assertTrue((self.target / "CLAUDE.md").read_bytes().startswith(claude))
        self.assertEqual((self.target / "CLAUDE.md").read_bytes().count(b"@AGENTS.md"), 1)
        self.assertEqual(before["app.txt"], (self.target / "app.txt").read_bytes())
        self.assertEqual(git_config, (self.target / ".git/config").read_bytes())
        installed = file_bytes(self.target)
        report = self.install()
        self.assertEqual(report["changes"], 0)
        self.assertEqual(installed, file_bytes(self.target))
        self.assertTrue(self.check()["ok"])

    def test_adoption_mapping_preserves_existing_document_bytes(self):
        sources = {key: f"existing/{key}.md" for key in project_os.SOURCE_KEYS}
        for key, relative in sources.items():
            path = self.target / relative
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(("既有事实:" + key).encode("utf-8") + b"\r\n")
        before = file_bytes(self.target)
        self.install({"sources": sources, "tasks_dir": "tasks", "evidence_dir": "evidence"})
        for relative in sources.values():
            self.assertEqual(before[relative], (self.target / relative).read_bytes())
        manifest = project_os.read_json(self.target / "project-os.json")
        self.assertEqual(manifest["sources"], sources)
        self.assertFalse((self.target / "project-os/STATUS.md").exists())
        self.assertTrue(self.check()["ok"])

    def test_existing_agents_can_be_the_canonical_rules_source(self):
        original = b"# Canonical existing project rules\r\n"
        (self.target / "AGENTS.md").write_bytes(original)
        self.install({"sources": {"rules": "AGENTS.md"}})
        self.assertTrue((self.target / "AGENTS.md").read_bytes().startswith(original))
        self.assertTrue(self.check()["ok"], self.check()["errors"])
        installed = file_bytes(self.target)
        self.assertEqual(self.install()["changes"], 0)
        self.assertEqual(installed, file_bytes(self.target))

    def test_new_agents_can_be_the_canonical_rules_source(self):
        self.install({"sources": {"rules": "AGENTS.md"}})
        self.assertIn(b"Project rules", (self.target / "AGENTS.md").read_bytes())
        self.assertTrue(self.check()["ok"])

    def test_hardlinked_entry_is_not_appended_outside_target(self):
        outside = self.root / "outside.md"
        outside.write_bytes(b"Original external file")
        try:
            os.link(outside, self.target / "AGENTS.md")
        except OSError:
            self.skipTest("Hardlinks unavailable")
        with self.assertRaisesRegex(project_os.ProjectOSError, "hardlinked"):
            self.install()
        self.assertEqual(outside.read_bytes(), b"Original external file")
        self.assertFalse((self.target / "project-os.json").exists())

    def test_different_installed_tool_is_retained_with_explicit_upgrade_note(self):
        self.install()
        custom = b"# Local customized checker\n"
        (self.target / "scripts/project_os.py").write_bytes(custom)
        report = self.install()
        self.assertEqual((self.target / "scripts/project_os.py").read_bytes(), custom)
        self.assertTrue(any("not an upgrade" in note for note in report["notes"]))

    def test_conflict_preflight_writes_nothing(self):
        (self.target / "project-os").mkdir()
        (self.target / "project-os/STATUS.md").write_text("Existing status", encoding="utf-8")
        before = file_bytes(self.target)
        with self.assertRaisesRegex(project_os.ProjectOSError, "Path conflict"):
            self.install()
        self.assertEqual(before, file_bytes(self.target))

    def test_tool_name_conflict_is_not_overwritten(self):
        (self.target / "scripts").mkdir()
        (self.target / "scripts/project_os.py").write_text("# custom unrelated tool", encoding="utf-8")
        before = file_bytes(self.target)
        with self.assertRaisesRegex(project_os.ProjectOSError, "Path conflict"):
            self.install()
        self.assertEqual(before, file_bytes(self.target))

    def test_path_traversal_absolute_git_and_stream_paths_are_rejected(self):
        for bad in ("../outside.md", str(self.root / "outside.md"), ".git/config", ".GIT/config", "docs/../../escape.md", "C:relative.md", "docs/item:stream", "AGENTS.md", "docs/NUL.txt"):
            with self.subTest(path=bad):
                before = file_bytes(self.target)
                with self.assertRaises(project_os.ProjectOSError):
                    self.install({"sources": {"status": bad}})
                self.assertEqual(before, file_bytes(self.target))

    def test_symlink_escape_is_rejected_before_writes(self):
        external = self.root / "external"
        external.mkdir()
        try:
            (self.target / "outside-link").symlink_to(external, target_is_directory=True)
        except OSError:
            self.skipTest("Host does not allow directory symlinks")
        with self.assertRaisesRegex(project_os.ProjectOSError, "Symlink"):
            self.install({"sources": {"status": "outside-link/status.md"}})
        self.assertEqual(list(external.iterdir()), [])
        self.assertFalse((self.target / "project-os.json").exists())

    def test_source_same_directory_and_alias_are_rejected(self):
        with self.assertRaisesRegex(project_os.ProjectOSError, "non-overlapping"):
            project_os.build_plan(self.source, self.source, None)
        alias = self.root / "alias"
        try:
            alias.symlink_to(self.source, target_is_directory=True)
        except OSError:
            self.skipTest("Host does not allow directory symlinks")
        self.addCleanup(alias.unlink)
        with self.assertRaisesRegex(project_os.ProjectOSError, "non-overlapping"):
            project_os.build_plan(self.source, project_os.target_root(str(alias)), None)

    def test_clone_origin_is_rejected_across_https_and_ssh(self):
        for origin in ("git@github.com:furenzhong/ai_codex_project_os_starter_kit.git", "ssh://git@github.com/furenzhong/ai_codex_project_os_starter_kit.git", "https://user:secret@github.com/furenzhong/ai_codex_project_os_starter_kit.git?token=secret"):
            with self.subTest(origin=origin):
                run_git(self.target, "remote", "set-url", "origin", origin)
                with self.assertRaisesRegex(project_os.ProjectOSError, "origin identifies") as error:
                    self.install()
                self.assertNotIn("secret", str(error.exception))
                self.assertFalse((self.target / "project-os.json").exists())

    def test_shared_git_worktree_is_rejected(self):
        worktree = self.root / "kit-worktree"
        run_git(self.source, "worktree", "add", "--detach", str(worktree), "HEAD")
        with self.assertRaisesRegex(project_os.ProjectOSError, "common directory"):
            project_os.build_plan(self.source, project_os.target_root(str(worktree)), None)

    def test_manifest_starter_identity_is_rejected_even_without_matching_remote(self):
        write_json(self.target / "project-os.json", {"role": "starter-kit"})
        with self.assertRaisesRegex(project_os.ProjectOSError, "identifies as starter-kit"):
            self.install()

    def test_git_subdirectory_cannot_be_used_as_project_root(self):
        nested = self.target / "nested"
        nested.mkdir()
        with self.assertRaisesRegex(project_os.ProjectOSError, "working tree root"):
            project_os.target_root(str(nested))

    def test_install_manifest_redacts_source_credentials_and_has_provenance(self):
        run_git(self.source, "remote", "set-url", "origin", "https://user:secret@github.com/furenzhong/ai_codex_project_os_starter_kit.git?token=hidden")
        self.install()
        manifest = project_os.read_json(self.target / "project-os.json")
        source = manifest["source_identity"]
        self.assertEqual(source["origin"], project_os.KIT_ORIGIN)
        self.assertEqual(source["revision"], run_git(self.source, "rev-parse", "HEAD"))
        self.assertNotIn("secret", json.dumps(manifest))
        self.assertNotIn("hidden", json.dumps(manifest))
        self.assertNotIn(str(self.source), json.dumps(manifest))

    def test_no_tasks_does_not_claim_harness_was_exercised(self):
        self.install()
        report = self.check()
        self.assertTrue(report["ok"])
        self.assertEqual(report["harness"], {"tasks": 0, "accepted": 0, "state": "not_exercised"})

    def test_accepted_result_can_be_an_older_commit_than_current_head(self):
        task, receipt = self.valid_task()
        (self.target / "later.txt").write_text("Unrelated later commit", encoding="utf-8")
        run_git(self.target, "add", "later.txt")
        run_git(self.target, "commit", "-qm", "Later independent work")
        self.assertNotEqual(receipt["result_revision"], run_git(self.target, "rev-parse", "HEAD"))
        report = self.check()
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(report["harness"]["state"], "accepted_records_checked")

    def test_wrong_baseline_receipt_is_rejected(self):
        task, receipt = self.valid_task()
        receipt["base_revision"] = receipt["result_revision"]
        self.save_task(task, receipt)
        self.assertIn("receipt_baseline", {e["code"] for e in self.check()["errors"]})

    def test_missing_evidence_failed_checks_and_no_review_cannot_be_accepted(self):
        task, receipt = self.valid_task()
        receipt["checks"][0]["exit_code"] = 1
        receipt["evidence"] = ["project-os/evidence/missing.txt"]
        receipt.pop("verified_by")
        receipt.pop("verification_evidence")
        self.save_task(task, receipt)
        codes = {e["code"] for e in self.check()["errors"]}
        self.assertTrue({"failed_check", "evidence", "verification"}.issubset(codes), codes)

    def test_other_evidence_can_be_empty_when_checks_and_verification_have_evidence(self):
        task, receipt = self.valid_task()
        receipt["evidence"] = []
        self.save_task(task, receipt)
        report = self.check()
        self.assertTrue(report["ok"], report["errors"])

    def test_malformed_receipt_revision_reports_error_without_traceback(self):
        task, receipt = self.valid_task()
        receipt["base_revision"] = {"unexpected": "object"}
        self.save_task(task, receipt)
        report = self.check()
        self.assertFalse(report["ok"])
        self.assertIn("revision", {e["code"] for e in report["errors"]})

    def test_malformed_manifest_types_and_schema_report_errors_without_traceback(self):
        self.install()
        path = self.target / "project-os.json"
        original = project_os.read_json(path)
        for changes in ({"role": []}, {"schema_version": 99}, {"schema_version": True}, {"sources": []}, {"source_identity": {"origin": []}}):
            with self.subTest(changes=changes):
                write_json(path, {**original, **changes})
                report = self.check()
                self.assertFalse(report["ok"])
                self.assertEqual(report["errors"][0]["code"], "manifest")

    def test_reapply_does_not_recreate_a_missing_adopted_source(self):
        self.install()
        (self.target / "project-os/STATUS.md").unlink()
        before = file_bytes(self.target)
        with self.assertRaisesRegex(project_os.ProjectOSError, "Installed source is missing"):
            self.install()
        self.assertEqual(before, file_bytes(self.target))

    def test_unrun_acceptance_command_is_not_satisfied_by_other_success(self):
        task, receipt = self.valid_task()
        receipt["checks"][0]["command"] = "echo unrelated success"
        self.save_task(task, receipt)
        self.assertIn("missing_check", {e["code"] for e in self.check()["errors"]})

    def test_wrong_commit_unknown_object_and_scope_are_rejected(self):
        task, receipt = self.valid_task()
        receipt["result_revision"] = "f" * 40
        receipt["changed_files"] = ["outside.txt"]
        self.save_task(task, receipt)
        codes = {e["code"] for e in self.check()["errors"]}
        self.assertIn("revision", codes)
        self.assertIn("write_scope", codes)

    def test_receipt_file_list_must_match_committed_changes(self):
        task, receipt = self.valid_task()
        receipt["changed_files"] = []
        self.save_task(task, receipt)
        self.assertIn("receipt_diff", {e["code"] for e in self.check()["errors"]})

    def test_unavailable_git_diff_cannot_accept_an_unverified_file_list(self):
        task, receipt = self.valid_task()
        receipt["changed_files"] = []
        self.save_task(task, receipt)
        run_git(self.target, "config", "diff.orderFile", str(self.root / "missing-diff-order-file"))
        report = self.check()
        self.assertFalse(report["ok"])
        self.assertEqual(report["harness"]["state"], "records_invalid")
        self.assertIn("receipt_diff_unavailable", {e["code"] for e in report["errors"]})

    def test_running_without_locator_warns_and_does_not_reassign(self):
        self.install()
        task = {"id": "running-task", "objective": "Inspect a paused writer", "status": "running", "base_revision": run_git(self.target, "rev-parse", "HEAD"), "writable_paths": ["app.txt"], "acceptance_commands": ["test app"]}
        path = self.target / "project-os/tasks/running.json"
        write_json(path, task)
        before = path.read_bytes()
        report = self.check()
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(sum(w["code"] == "resume_locator" for w in report["warnings"]), 3)
        self.assertEqual(before, path.read_bytes())

    def test_post_plan_edit_is_detected_before_any_installation_write(self):
        _, operations = self.plan()
        (self.target / "AGENTS.md").write_text("Concurrent user edit", encoding="utf-8")
        before = file_bytes(self.target)
        with self.assertRaisesRegex(project_os.ProjectOSError, "changed after planning"):
            project_os.apply_plan(self.target, operations)
        self.assertEqual(before, file_bytes(self.target))

    def test_installed_checker_runs_offline_and_snapshot_is_read_only(self):
        self.install()
        before = file_bytes(self.target)
        result = subprocess.run([sys.executable, str(self.target / "scripts/project_os.py"), "snapshot", "--target", str(self.target), "--json"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        report = json.loads(result.stdout)
        self.assertEqual(report["harness"]["state"], "not_exercised")
        self.assertEqual(report["git"]["head"], run_git(self.target, "rev-parse", "HEAD"))
        self.assertEqual(before, file_bytes(self.target))


if __name__ == "__main__":
    unittest.main()
