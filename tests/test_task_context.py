"""Task-context regressions: preserve provenance without claiming live coordination."""

import copy
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

import test_project_os as fixtures


project_os = fixtures.project_os


@unittest.skipUnless(shutil.which("git"), "Git is required for context receipt regressions")
class TaskContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="task-context-tests-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "kit"
        self.target = self.root / "project"
        for path, origin in ((self.source, "https://github.com/furenzhong/awoo-vibe-coding-governance.git"),
                             (self.target, "https://example.invalid/team/product.git")):
            path.mkdir()
            fixtures.run_git(path, "init", "-q")
            fixtures.run_git(path, "remote", "add", "origin", origin)
            (path / "app.txt").write_text("original\n", encoding="utf-8")
            fixtures.run_git(path, "add", "app.txt")
            fixtures.run_git(path, "commit", "-qm", "Initial fixture")

    def install(self):
        report, operations = project_os.build_plan(self.source, self.target, None)
        project_os.apply_plan(self.target, operations)
        return report

    def check(self):
        return project_os.check_project(self.target)

    def valid_task(self):
        # Reuse fixture construction, not its TestCase class or test methods.
        return fixtures.ProjectOSRegressionTests.valid_task(self)

    def save_task(self, task, receipt):
        fixtures.write_json(self.target / "project-os/tasks/task-001.json", task)
        fixtures.write_json(self.target / task["receipt"], receipt)

    def tracked_task(self):
        task, receipt = self.valid_task()
        snapshot_ref = "project-os/evidence/task-001/ctx-001.md"
        snapshot = self.target / snapshot_ref
        snapshot.parent.mkdir()
        snapshot.write_bytes(b"# Dispatch\nUser: preserve the public API.\nAssumption: this fix is local.\n")
        checkpoint_ref = "project-os/evidence/task-001/executor.json"
        checkpoint = {
            "task_id": task["id"], "actor": "worker", "role": "executor",
            "session_id": task["session_id"], "context_revision": "ctx-001",
            "observed_at": "2026-09-27T10:30:00+08:00",
            "last_action": "Committed the bounded change and ran the fixture checks.",
            "next_action": "Await coordinator acceptance.", "unresolved": [], "operations": [],
            "evidence": ["project-os/evidence/check.txt"],
        }
        fixtures.write_json(self.target / checkpoint_ref, checkpoint)
        coordinator_ref = "project-os/evidence/task-001/coordinator.json"
        coordinator = {**checkpoint, "actor": "coordinator", "role": "coordinator",
                       "session_id": "coordinator-session", "last_action": "Reviewed the returned change.",
                       "next_action": "Report the accepted result."}
        fixtures.write_json(self.target / coordinator_ref, coordinator)
        task["context"] = {
            "schema_version": 1, "current_revision": "ctx-001",
            "snapshots": [{"revision": "ctx-001", "path": snapshot_ref,
                           "sha256": project_os.context_snapshot_sha256(snapshot)}],
            "checkpoints": [checkpoint_ref, coordinator_ref], "corrections": [],
        }
        receipt.update(context_revision="ctx-001", checkpoint=checkpoint_ref)
        self.save_task(task, receipt)
        return task, receipt, checkpoint

    def second_revision(self, task, receipt, checkpoint, delivery="adopted"):
        snapshot_ref = "project-os/evidence/task-001/ctx-002.md"
        snapshot = self.target / snapshot_ref
        snapshot.write_text("# Corrected dispatch\nPreserve the API and the caller's timeout.\n", encoding="utf-8")
        task["context"]["snapshots"].append({"revision": "ctx-002", "path": snapshot_ref,
                                                "sha256": project_os.context_snapshot_sha256(snapshot)})
        task["context"]["current_revision"] = "ctx-002"
        correction_ref = "project-os/evidence/task-001/correction-001.json"
        correction = {
            "id": "correction-001", "task_id": task["id"], "from_revision": "ctx-001",
            "to_revision": "ctx-002", "cause": "handoff_omission",
            "reason": "The first dispatch omitted the user's timeout constraint.",
            "impact": "Review timeout behavior before acceptance.",
            "target_session_id": task["session_id"], "delivery": delivery,
            "delivery_evidence": ["project-os/evidence/check.txt"] if delivery != "recorded" else [],
            "adoption_evidence": ["project-os/evidence/review.txt"] if delivery == "adopted" else [],
        }
        fixtures.write_json(self.target / correction_ref, correction)
        task["context"]["corrections"].append(correction_ref)
        checkpoint["context_revision"] = "ctx-002"
        fixtures.write_json(self.target / receipt["checkpoint"], checkpoint)
        coordinator_ref = "project-os/evidence/task-001/coordinator.json"
        coordinator = project_os.read_json(self.target / coordinator_ref)
        coordinator["context_revision"] = "ctx-002"
        fixtures.write_json(self.target / coordinator_ref, coordinator)
        receipt["context_revision"] = "ctx-002"
        self.save_task(task, receipt)
        return correction, correction_ref

    def assert_context_error(self, code=None):
        report = self.check()
        self.assertFalse(report["ok"], report)
        self.assertEqual(report["context"]["state"], "records_invalid", report)
        self.assertTrue(any(item["code"].startswith("context_") and (not code or item["code"] == code)
                            for item in report["errors"]), report)
        return report

    def test_legacy_tasks_remain_compatible_and_coverage_is_explicit(self):
        task, receipt = self.valid_task()
        report = self.check()
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["context"], {"tracked": 0, "legacy": 1, "state": "legacy_only"})
        self.assertEqual(report["harness"]["state"], "accepted_records_checked")
        task["context"] = None  # Presence is opt-in; malformed context cannot silently become legacy.
        self.save_task(task, receipt)
        self.assert_context_error("context_schema")

    def test_valid_acceptance_line_endings_and_mixed_coverage_are_read_only(self):
        task, receipt, _ = self.tracked_task()
        snapshot = self.target / task["context"]["snapshots"][0]["path"]
        snapshot.write_bytes(snapshot.read_bytes().replace(b"\n", b"\r\n"))
        before = fixtures.file_bytes(self.target)
        before_git = fixtures.run_git(self.target, "status", "--porcelain=v1")
        report = self.check()
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["context"], {"tracked": 1, "legacy": 0, "state": "tracked_records_checked"})
        self.assertEqual(before, fixtures.file_bytes(self.target))
        self.assertEqual(before_git, fixtures.run_git(self.target, "status", "--porcelain=v1"))
        legacy = {key: value for key, value in task.items() if key not in {"context", "receipt"}}
        legacy.update(id="legacy-002", status="planned")
        fixtures.write_json(self.target / "project-os/tasks/legacy-002.json", legacy)
        report = self.check()
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["context"], {"tracked": 1, "legacy": 1, "state": "partially_covered"})

    def test_snapshot_integrity_includes_historical_revisions(self):
        task, receipt, checkpoint = self.tracked_task()
        self.second_revision(task, receipt, checkpoint)
        old_snapshot = self.target / task["context"]["snapshots"][0]["path"]
        original = old_snapshot.read_bytes()
        for contents in (b"silently rewritten old dispatch", b"", b"  \n", b"\xff"):
            with self.subTest(contents=contents):
                old_snapshot.write_bytes(contents)
                self.assert_context_error("context_snapshot")
        old_snapshot.write_bytes(original)
        for mutate in (
            lambda context: context["snapshots"][0].update(path="missing.md"),
            lambda context: context["snapshots"][0].update(sha256="not-a-digest"),
            lambda context: context.update(current_revision="ctx-001"),
            lambda context: context["snapshots"][1].update(revision="ctx-001"),
            lambda context: context["snapshots"][1].update(path=context["snapshots"][0]["path"]),
        ):
            changed = copy.deepcopy(task)
            mutate(changed["context"])
            self.save_task(changed, receipt)
            self.assert_context_error()

    def test_old_delivery_can_be_submitted_but_not_accepted(self):
        task, receipt, checkpoint = self.tracked_task()
        self.second_revision(task, receipt, checkpoint)
        checkpoint["context_revision"] = receipt["context_revision"] = "ctx-001"
        fixtures.write_json(self.target / receipt["checkpoint"], checkpoint)
        task["status"] = "submitted"
        self.save_task(task, receipt)
        report = self.check()
        self.assertTrue(report["ok"], report)
        self.assertIn("context_stale_receipt", {item["code"] for item in report["warnings"]})
        task["status"] = "accepted"
        self.save_task(task, receipt)
        self.assert_context_error("context_stale_receipt")

    def test_correction_delivery_adoption_and_evidence_are_distinct(self):
        task, receipt, checkpoint = self.tracked_task()
        correction, ref = self.second_revision(task, receipt, checkpoint, "recorded")
        task["status"] = "submitted"
        self.save_task(task, receipt)
        report = self.check()
        self.assertTrue(report["ok"], report)
        self.assertIn("context_pending_correction", {item["code"] for item in report["warnings"]})
        task["status"] = "accepted"
        self.save_task(task, receipt)
        self.assert_context_error("context_pending_correction")
        correction["delivery"] = "delivered"
        fixtures.write_json(self.target / ref, correction)
        self.assert_context_error("context_correction")
        correction["delivery_evidence"] = ["project-os/evidence/check.txt"]
        fixtures.write_json(self.target / ref, correction)
        self.assert_context_error("context_pending_correction")
        correction["delivery"] = "adopted"
        for invalid in ([], ["missing.txt"], [receipt["checkpoint"]]):
            with self.subTest(adoption=invalid):
                correction["adoption_evidence"] = invalid
                fixtures.write_json(self.target / ref, correction)
                self.assert_context_error("context_correction")
        correction["adoption_evidence"] = ["project-os/evidence/review.txt"]
        fixtures.write_json(self.target / ref, correction)
        self.assertTrue(self.check()["ok"], self.check())
        correction.update(target_session_id="previous-worker-session", delivery="recorded", delivery_evidence=[], adoption_evidence=[])
        fixtures.write_json(self.target / ref, correction)
        report = self.check()
        self.assertTrue(report["ok"], report)
        self.assertIn("context_pending_correction", {item["code"] for item in report["warnings"]})

    def test_revision_changes_require_valid_correction_history(self):
        task, receipt, checkpoint = self.tracked_task()
        correction, ref = self.second_revision(task, receipt, checkpoint)
        mutations = [
            {"from_revision": "unknown"}, {"from_revision": "ctx-002", "to_revision": "ctx-001"},
            {"task_id": "other-task"}, {"cause": []}, {"delivery": True}, {"reason": ""},
            {"delivery_evidence": {}}, {"adoption_evidence": [False]},
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                fixtures.write_json(self.target / ref, {**correction, **mutation})
                self.assert_context_error("context_correction")
        fixtures.write_json(self.target / ref, correction)
        duplicate_ref = "project-os/evidence/task-001/correction-duplicate.json"
        fixtures.write_json(self.target / duplicate_ref, correction)
        task["context"]["corrections"].append(duplicate_ref)
        self.save_task(task, receipt)
        self.assert_context_error("context_correction")
        task["context"]["corrections"] = []
        self.save_task(task, receipt)
        self.assert_context_error("context_missing_correction")

    def test_receipt_binds_task_executor_session_and_revision(self):
        task, receipt, checkpoint = self.tracked_task()
        for mutation in ({"task_id": "other-task"}, {"session_id": "old-session"},
                         {"role": "coordinator"}, {"context_revision": "unknown"}):
            with self.subTest(mutation=mutation):
                fixtures.write_json(self.target / receipt["checkpoint"], {**checkpoint, **mutation})
                self.assert_context_error()
        fixtures.write_json(self.target / receipt["checkpoint"], checkpoint)
        unlisted = "project-os/evidence/task-001/unlisted-checkpoint.json"
        fixtures.write_json(self.target / unlisted, checkpoint)
        for mutation in ({"checkpoint": unlisted}, {"context_revision": "unknown"},
                         {"context_revision": False}, {"checkpoint": []}):
            with self.subTest(receipt=mutation):
                self.save_task(task, {**receipt, **mutation})
                self.assert_context_error("context_receipt")
        self.save_task(task, receipt)
        self.second_revision(task, receipt, checkpoint)
        receipt["context_revision"] = "ctx-001"
        self.save_task(task, receipt)
        self.assert_context_error("context_receipt")

    def test_coordinator_history_does_not_replace_current_executor_checkpoint(self):
        task, receipt, checkpoint = self.tracked_task()
        self.second_revision(task, receipt, checkpoint)
        coordinator = {**checkpoint, "actor": "coordinator", "role": "coordinator",
                       "session_id": "coordinator-session", "context_revision": "ctx-001"}
        coordinator_ref = "project-os/evidence/task-001/coordinator.json"
        fixtures.write_json(self.target / coordinator_ref, coordinator)
        self.save_task(task, receipt)
        report = self.check()
        self.assertTrue(report["ok"], report)
        self.assertIn("context_stale_checkpoint", {item["code"] for item in report["warnings"]})
        task["status"] = "running"
        task.pop("receipt")
        task["context"]["checkpoints"] = [coordinator_ref]
        fixtures.write_json(self.target / "project-os/tasks/task-001.json", task)
        report = self.check()
        self.assertTrue(report["ok"], report)
        self.assertIn("context_missing_checkpoint", {item["code"] for item in report["warnings"]})
        task["status"] = "planned"
        task["context"]["checkpoints"] = []
        fixtures.write_json(self.target / "project-os/tasks/task-001.json", task)
        self.assertNotIn("context_missing_checkpoint", {item["code"] for item in self.check()["warnings"]})

    def test_checkpoint_types_uniqueness_and_timestamps_are_validated(self):
        task, receipt, checkpoint = self.tracked_task()
        for mutation in ({"actor": []}, {"last_action": ""}, {"role": {}}, {"unresolved": "none"},
                         {"unresolved": [False]}, {"evidence": None}, {"operations": {}},
                         {"operations": [False]}, {"operations": [{"description": "job", "locator": "id", "state": []}]},
                         {"observed_at": "2026-09-27T10:30:00"}, {"observed_at": "2026-02-30T10:30:00Z"}):
            with self.subTest(mutation=mutation):
                fixtures.write_json(self.target / receipt["checkpoint"], {**checkpoint, **mutation})
                self.assert_context_error("context_checkpoint")
        fixtures.write_json(self.target / receipt["checkpoint"], checkpoint)
        second_ref = "project-os/evidence/task-001/duplicate-session.json"
        fixtures.write_json(self.target / second_ref, checkpoint)
        for ref in (receipt["checkpoint"], second_ref):
            task["context"]["checkpoints"] = [receipt["checkpoint"], ref]
            self.save_task(task, receipt)
            self.assert_context_error("context_checkpoint")

    def test_coordinator_checkpoint_absence_warns_only_after_planning(self):
        task, receipt, _ = self.tracked_task()
        report = self.check()
        self.assertTrue(report["ok"], report)
        self.assertNotIn("context_missing_coordinator", {item["code"] for item in report["warnings"]})
        task["context"]["checkpoints"] = [receipt["checkpoint"]]
        for status in ("running", "submitted", "accepted", "planned"):
            with self.subTest(status=status):
                task["status"] = status
                self.save_task(task, receipt)
                report = self.check()
                self.assertTrue(report["ok"], report)
                self.assertEqual(status != "planned", "context_missing_coordinator" in
                                 {item["code"] for item in report["warnings"]})

    def test_hardlink_aliases_cannot_duplicate_records_or_supply_adoption_evidence(self):
        task, receipt, checkpoint = self.tracked_task()
        correction, ref = self.second_revision(task, receipt, checkpoint)
        checkpoint_alias = "project-os/evidence/task-001/checkpoint-alias.json"
        snapshot_alias = "project-os/evidence/task-001/snapshot-alias.md"
        try:
            os.link(self.target / receipt["checkpoint"], self.target / checkpoint_alias)
            os.link(self.target / task["context"]["snapshots"][0]["path"], self.target / snapshot_alias)
        except OSError:
            self.skipTest("Host does not allow hardlinks")
        correction["adoption_evidence"] = [checkpoint_alias]
        fixtures.write_json(self.target / ref, correction)
        report = self.assert_context_error("context_correction")
        self.assertTrue(any("mutable active checkpoint" in item["message"] for item in report["errors"]))
        correction["adoption_evidence"] = ["project-os/evidence/review.txt"]
        fixtures.write_json(self.target / ref, correction)
        task["context"]["snapshots"][1].update(
            path=snapshot_alias, sha256=task["context"]["snapshots"][0]["sha256"])
        self.save_task(task, receipt)
        report = self.assert_context_error("context_snapshot")
        self.assertTrue(any("unique files" in item["message"] for item in report["errors"]))

    def test_bad_context_schema_and_collection_types_do_not_crash(self):
        task, receipt, _ = self.tracked_task()
        original = copy.deepcopy(task["context"])
        for bad in (None, [], True, {**original, "schema_version": True}, {**original, "schema_version": 2},
                    {**original, "current_revision": []}, {**original, "snapshots": {}},
                    {**original, "snapshots": []}, {**original, "snapshots": [True]},
                    {**original, "checkpoints": None}, {**original, "checkpoints": [False]},
                    {**original, "corrections": {}}, {**original, "corrections": [{}]}):
            with self.subTest(context=bad):
                task["context"] = bad
                self.save_task(task, receipt)
                self.assert_context_error()

    def test_paths_cannot_escape_or_read_links(self):
        task, receipt, checkpoint = self.tracked_task()
        original = copy.deepcopy(task["context"])
        for bad in ("../outside.md", ".git/config", "C:relative.md", "docs/item:stream", "docs/NUL.txt",
                    "bad\x00.md", str(self.root / "outside.md")):
            with self.subTest(path=bad):
                task["context"] = copy.deepcopy(original)
                task["context"]["snapshots"][0]["path"] = bad
                self.save_task(task, receipt)
                self.assert_context_error("context_snapshot")
        outside = self.root / "outside.md"
        outside.write_text("This external content must not be read.", encoding="utf-8")
        link = self.target / "external.md"
        try:
            link.symlink_to(outside)
        except OSError:
            self.skipTest("Host does not allow symlinks; lexical escape cases were exercised")
        self.addCleanup(link.unlink)
        task["context"] = copy.deepcopy(original)
        task["context"]["snapshots"][0]["path"] = "external.md"
        self.save_task(task, receipt)
        original_read = Path.read_bytes

        def guarded_read(path):
            if path.resolve() == outside:
                self.fail("Checker tried to read content outside the project through a link")
            return original_read(path)

        with mock.patch.object(Path, "read_bytes", guarded_read):
            self.assert_context_error("context_snapshot")
        task["context"] = original
        checkpoint["evidence"] = ["external.md"]
        fixtures.write_json(self.target / receipt["checkpoint"], checkpoint)
        self.save_task(task, receipt)
        self.assert_context_error("context_checkpoint")

    def test_recorded_operations_are_not_executed_or_treated_as_live_facts(self):
        task, receipt, checkpoint = self.tracked_task()
        checkpoint["operations"] = [
            {"description": "External worker", "locator": "claude-session:do-not-execute", "state": "running"},
            {"description": "Unknown job", "locator": "https://example.invalid/operation/123", "state": "unknown"},
        ]
        fixtures.write_json(self.target / receipt["checkpoint"], checkpoint)
        original_run = project_os.subprocess.run
        commands = []

        def git_only(command, **kwargs):
            commands.append(command)
            self.assertEqual(command[0], "git")
            return original_run(command, **kwargs)

        before = fixtures.file_bytes(self.target)
        with mock.patch.object(project_os.subprocess, "run", side_effect=git_only):
            report = self.check()
        self.assertTrue(report["ok"], report)
        self.assertTrue(commands)
        self.assertEqual(2, sum(item["code"] == "context_operation" for item in report["warnings"]))
        self.assertEqual(before, fixtures.file_bytes(self.target))


if __name__ == "__main__":
    unittest.main()
