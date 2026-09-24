#!/usr/bin/env python3
"""Adopt lightweight project governance without replacing an existing project.

Python 3.10+ and the standard library are sufficient. Git is used read-only when
available. No command in this tool downloads files, executes task commands,
changes remotes, commits changes, or contacts an agent service.
"""

# MIT License
#
# Copyright (c) 2026 furenzhong
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import subprocess
import sys
from typing import Any
from urllib.parse import urlsplit


VERSION = "1.1.0"
SCHEMA_VERSION = 1
MANIFEST = "project-os.json"
KIT_ORIGIN = "github.com/furenzhong/ai_codex_project_os_starter_kit"
SOURCE_KEYS = ("rules", "status", "handoff", "decisions")
DEFAULT_SOURCES = {key: f"project-os/{key.upper()}.md" for key in SOURCE_KEYS}
BEGIN = b"<!-- project-os:begin -->"
END = b"<!-- project-os:end -->"
TASK_STATUSES = {"planned", "running", "submitted", "accepted", "returned", "blocked"}
LIMITS = (
    "Checks validate local structure, Git object references, declared results, and evidence paths. "
    "They do not execute acceptance commands, establish reviewer identity, or prove product correctness."
)


class ProjectOSError(Exception):
    """A concise, actionable validation failure."""


def git(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=15,
            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def normalize_origin(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip().replace("\\", "/")
    if "://" in value:
        try:
            parsed = urlsplit(value)
        except ValueError:
            return None
        value = (parsed.hostname or "") + parsed.path
    else:
        value = re.sub(r"^[^/@]+@", "", value)
        value = re.sub(r"^([^/]+):(?=[^/])", r"\1/", value)
        value = re.split(r"[?#]", value, maxsplit=1)[0]
    value = value.rstrip("/")
    if value.lower().endswith(".git"):
        value = value[:-4]
    return value.lower()


def identity(root: Path) -> dict[str, Any]:
    top = git(root, "rev-parse", "--show-toplevel")
    common = git(root, "rev-parse", "--git-common-dir") if top else None
    common_path = (root / common).resolve() if common else None
    return {
        "root": root,
        "git_root": Path(top).resolve() if top else None,
        "common_dir": common_path,
        "origin": normalize_origin(git(root, "remote", "get-url", "origin")) if top else None,
    }


def fingerprint(path: Path | None) -> str | None:
    return hashlib.sha256(os.path.normcase(str(path)).encode("utf-8")).hexdigest() if path else None


def target_root(value: str) -> Path:
    root = Path(value).expanduser().resolve()
    if not root.is_dir():
        raise ProjectOSError(f"Target must be an existing project directory: {value}")
    info = identity(root)
    if info["git_root"] and info["git_root"] != root:
        raise ProjectOSError("--target must name the Git working tree root, not one of its subdirectories.")
    return root


def safe_path(root: Path, relative: Any) -> Path:
    root = root.resolve()
    if not isinstance(relative, str) or not relative.strip():
        raise ProjectOSError("Managed paths must be nonempty relative strings.")
    windows = PureWindowsPath(relative)
    parts = PurePosixPath(relative.replace("\\", "/")).parts
    if windows.drive or windows.is_absolute() or relative.startswith("/"):
        raise ProjectOSError(f"Absolute paths are not allowed: {relative}")
    if not parts or any(p.casefold() in {"..", ".git"} for p in parts):
        raise ProjectOSError(f"Path traversal and .git paths are not allowed: {relative}")
    if any(":" in p for p in parts):
        raise ProjectOSError(f"Drive and alternate-stream paths are not allowed: {relative}")
    if any(p.endswith((" ", ".")) or re.fullmatch(r"(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", p) for p in parts):
        raise ProjectOSError(f"Ambiguous or reserved filesystem names are not allowed: {relative}")
    path = root.joinpath(*parts)
    cursor = root
    for part in parts:
        cursor = cursor / part
        if cursor.is_symlink() or (hasattr(cursor, "is_junction") and cursor.is_junction()):
            raise ProjectOSError(f"Symlink or junction paths are not managed: {relative}")
    if not path.resolve().is_relative_to(root):
        raise ProjectOSError(f"Path escapes the project: {relative}")
    return path


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise ProjectOSError(f"Cannot read JSON from {path.name}: {exc}") from exc
    if not isinstance(data, dict):
        raise ProjectOSError(f"{path.name} must contain a JSON object.")
    return data


def json_bytes(data: dict[str, Any]) -> bytes:
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def manifest_shape(root: Path, data: dict[str, Any]) -> None:
    if type(data.get("schema_version")) is not int or data["schema_version"] != SCHEMA_VERSION:
        raise ProjectOSError(f"Unsupported schema_version; expected {SCHEMA_VERSION}.")
    if data.get("role") not in ("starter-kit", "project"):
        raise ProjectOSError("Manifest role must be starter-kit or project.")
    if not isinstance(data.get("kit_version"), str) or not data["kit_version"]:
        raise ProjectOSError("Manifest requires kit_version.")
    sources = data.get("sources")
    if not isinstance(sources, dict) or set(sources) != set(SOURCE_KEYS):
        raise ProjectOSError("sources must map exactly rules, status, handoff, and decisions.")
    names = list(sources.values()) + [data.get("tasks_dir"), data.get("evidence_dir")]
    paths = [safe_path(root, name) for name in names]
    reserved = {root / MANIFEST, root / "AGENTS.md", root / "CLAUDE.md", root / "scripts/project_os.py"}
    for index, path in enumerate(paths):
        rules_entry = names[index] == sources["rules"] and path == root / "AGENTS.md"
        if path in reserved and not rules_entry:
            raise ProjectOSError("Governance paths must not replace the manifest, agent entries, or tool.")
    for i, path in enumerate(paths):
        for other in paths[i + 1:]:
            if path == other or path.is_relative_to(other) or other.is_relative_to(path):
                raise ProjectOSError("Source files, tasks_dir, and evidence_dir must be distinct, non-nested paths.")
    source_identity = data.get("source_identity")
    if source_identity is not None:
        if not isinstance(source_identity, dict):
            raise ProjectOSError("source_identity must be an object.")
        for key in ("origin", "revision", "kit_version", "common_dir_fingerprint"):
            if source_identity.get(key) is not None and not isinstance(source_identity[key], str):
                raise ProjectOSError(f"source_identity.{key} must be a string or null.")


def install_identity(source: Path, target: Path, current: dict[str, Any] | None) -> dict[str, Any]:
    if source == target or source.is_relative_to(target) or target.is_relative_to(source):
        raise ProjectOSError("Source and target must be separate, non-overlapping directories.")
    source_manifest = safe_path(source, MANIFEST)
    if source_manifest.exists() and read_json(source_manifest).get("role") != "starter-kit":
        raise ProjectOSError("Install from a starter-kit checkout; an installed copy is for check and snapshot.")
    if current and current.get("role") != "project":
        raise ProjectOSError("Target identifies as starter-kit. Choose the existing child project instead.")
    src, dst = identity(source), identity(target)
    if src["common_dir"] and src["common_dir"] == dst["common_dir"]:
        raise ProjectOSError("Target shares the starter kit's Git common directory (including worktrees).")
    if dst["origin"] and dst["origin"] in {KIT_ORIGIN, src["origin"]}:
        raise ProjectOSError("Target origin identifies the starter kit. Do not deploy into a clone of the mother repository.")
    origin = src["origin"]
    # Local remotes are useful for the live identity comparison but should not
    # publish machine-specific paths in a committed child-project manifest.
    public_origin = origin if origin and "." in origin.split("/", 1)[0] else None
    return {
        "origin": public_origin,
        "revision": git(source, "rev-parse", "HEAD"),
        "kit_version": VERSION,
        "dirty_source": bool(git(source, "status", "--porcelain=v1")),
        "common_dir_fingerprint": fingerprint(src["common_dir"]),
    }


def default_document(key: str) -> bytes:
    documents = {
        "rules": """# 项目规则 / Project rules

Record the project's goal, scope boundaries, and lasting constraints here.
Use existing code, tests, and observed behavior to check claims about reality.
Keep one authoritative source for each fact; link to task evidence instead of
copying task state into multiple documents. Add detail only when it prevents a
specific recurring mistake.

## 当前约束 / Current constraints

- Not yet recorded. The project owner or agent must reconcile these rules with
  the existing project before treating adoption as operational validation.
""",
        "status": """# 当前项目状态 / Current project status

Governance files have been installed. The project's implementation and product
behavior have not been inspected or validated by this installer.

## 当前目标 / Current objective

- Not yet recorded.

## 已验证事实 / Verified state

- No implementation claims yet. Link each material completion claim to its
  revision, verification command, and evidence.

## 正在进行 / Active work

- Link to task records instead of maintaining a second task lifecycle here.
""",
        "handoff": """# 当前交接 / Current handoff

## 接续位置 / Resume point

- Reconcile the current project state with code and existing documentation.

## 下一步 / Next useful action

- Record the immediate objective and the smallest check that demonstrates it.

## 中断的工作 / Interrupted work

- No execution sessions have been recorded by this installer. Before resuming
  an interrupted delegated task, inspect its executor, worktree, and session.
  Silence or a timeout does not establish that its previous writer has stopped.
""",
        "decisions": """# 项目决策 / Project decisions

Record consequential decisions with their reason, scope, assumptions, and the
condition that would reopen them. Link to the affected contract or source.
Routine edits do not require a decision entry.

No project-specific decisions have been recorded by this installer.
""",
    }
    return documents[key].encode("utf-8")


def entry_block(data: dict[str, Any], claude: bool = False) -> bytes:
    if claude:
        body = "@AGENTS.md"
    else:
        lines = ["Project governance index: `project-os.json`."]
        lines.extend(f"- {key}: `{data['sources'][key]}`" for key in SOURCE_KEYS)
        lines.extend([
            f"- Task state: `{data['tasks_dir']}`; evidence: `{data['evidence_dir']}`.",
            "Read the relevant sources before substantial work. Preserve existing project rules.",
            "Installer checks are structural; project claims still require verification.",
        ])
        body = "\n".join(lines)
    return BEGIN + b"\n" + body.encode("utf-8") + b"\n" + END


def append_entry(original: bytes, block: bytes, name: str) -> bytes:
    if BEGIN in original or END in original:
        if original.count(BEGIN) != 1 or original.count(END) != 1:
            raise ProjectOSError(f"{name} has malformed or duplicate managed blocks; reconcile it manually.")
        actual = original.split(BEGIN, 1)[1].split(END, 1)[0]
        expected = block.split(BEGIN, 1)[1].split(END, 1)[0]
        if actual.replace(b"\r\n", b"\n") != expected:
            raise ProjectOSError(f"{name} has a different managed block; existing content will not be overwritten.")
        return original
    separator = b"\r\n" if b"\r\n" in original else b"\n"
    suffix = block.replace(b"\n", separator) + separator
    return original + (separator * 2 if original else b"") + suffix


def build_plan(source: Path, target: Path, mapping_file: str | None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    source, target = source.resolve(), target.resolve()
    manifest_path = safe_path(target, MANIFEST)
    current = read_json(manifest_path) if manifest_path.exists() else None
    source_identity = install_identity(source, target, current)
    mapping = read_json(Path(mapping_file).expanduser().resolve()) if mapping_file else {}
    if set(mapping) - {"sources", "tasks_dir", "evidence_dir"}:
        raise ProjectOSError("Mapping accepts only sources, tasks_dir, and evidence_dir.")
    mapped_sources = mapping.get("sources", {})
    if not isinstance(mapped_sources, dict) or set(mapped_sources) - set(SOURCE_KEYS):
        raise ProjectOSError("Mapping sources accepts only rules, status, handoff, and decisions.")
    if current:
        manifest_shape(target, current)
        data = current
        for key, value in mapping.items():
            if key == "sources":
                if any(current["sources"][k] != v for k, v in value.items()):
                    raise ProjectOSError("Mapping differs from installed sources. Reconcile the manifest manually; no files changed.")
            elif current[key] != value:
                raise ProjectOSError("Mapping differs from the installed manifest; no files changed.")
    else:
        data = {
            "schema_version": SCHEMA_VERSION, "kit_version": VERSION, "role": "project",
            "sources": {**DEFAULT_SOURCES, **mapped_sources},
            "tasks_dir": mapping.get("tasks_dir", "project-os/tasks"),
            "evidence_dir": mapping.get("evidence_dir", "project-os/evidence"),
            "source_identity": source_identity,
        }
        manifest_shape(target, data)
    operations: list[dict[str, Any]] = []

    def add_file(relative: str, content: bytes | None, purpose: str, adopt: bool = False) -> None:
        path = safe_path(target, relative)
        if path.exists() and not path.is_file():
            raise ProjectOSError(f"Expected a file, found another path type: {relative}")
        for parent in path.parents:
            if parent == target:
                break
            if parent.exists() and not parent.is_dir():
                raise ProjectOSError(f"A parent directory is occupied by a file: {relative}")
        before = path.read_bytes() if path.exists() else None
        if before is not None and adopt:
            after, action = before, "reuse"
        elif before is not None and before != content:
            raise ProjectOSError(f"Path conflict: {relative}. Use --mapping to adopt existing governance documents or choose unused paths; files are never overwritten.")
        else:
            after, action = content, "reuse" if before is not None else "create"
        operations.append({"path": relative, "action": action, "purpose": purpose, "before": before, "after": after})

    for key, relative in data["sources"].items():
        existing = safe_path(target, relative).exists()
        if current and not existing:
            raise ProjectOSError(f"Installed source is missing: {relative}. Restore it explicitly; apply will not recreate user documents.")
        if key == "rules" and safe_path(target, relative) == target / "AGENTS.md":
            continue  # The single entry operation below preserves and indexes it.
        add_file(relative, default_document(key), key, adopt=bool(current) or key in mapped_sources)
    for key in ("tasks_dir", "evidence_dir"):
        relative = data[key]
        path = safe_path(target, relative)
        if path.exists() and not path.is_dir():
            raise ProjectOSError(f"Directory conflicts with an existing file: {relative}")
        for parent in path.parents:
            if parent == target:
                break
            if parent.exists() and not parent.is_dir():
                raise ProjectOSError(f"A parent directory is occupied by a file: {relative}")
        operations.append({"path": relative, "action": "reuse" if path.exists() else "mkdir", "purpose": key, "directory": True})
    for name in ("AGENTS.md", "CLAUDE.md"):
        path = safe_path(target, name)
        if path.exists() and not path.is_file():
            raise ProjectOSError(f"Expected a file: {name}")
        before = path.read_bytes() if path.exists() else b""
        initial = before
        if name == "AGENTS.md" and not path.exists() and safe_path(target, data["sources"]["rules"]) == path:
            initial = default_document("rules")
        after = append_entry(initial, entry_block(data, name == "CLAUDE.md"), name)
        if path.exists() and path.stat().st_nlink > 1 and before != after:
            raise ProjectOSError(f"Cannot append to hardlinked agent entry: {name}")
        operations.append({"path": name, "action": "reuse" if before == after else ("append" if path.exists() else "create"), "purpose": "agent entry", "before": before if path.exists() else None, "after": after})
    add_file("scripts/project_os.py", Path(__file__).read_bytes(), "offline checker", adopt=bool(current))
    add_file(MANIFEST, json_bytes(data), "governance mapping", adopt=bool(current))
    report = {
        "command": "plan", "ok": True, "target": str(target), "kit_version": VERSION,
        "operations": [{k: v for k, v in op.items() if k not in {"before", "after", "directory"}} for op in operations],
        "changes": sum(op["action"] != "reuse" for op in operations),
        "limits": LIMITS,
        "notes": ["Existing project files and Git metadata are preserved.", "Adopted documents require semantic review; installation does not verify their contents."],
    }
    if current and current["kit_version"] != VERSION:
        report["notes"].append("An older installed version was retained. Automatic content migration is not supported; review an explicit upgrade diff.")
    tool_path = safe_path(target, "scripts/project_os.py")
    if current and tool_path.is_file() and tool_path.read_bytes() != Path(__file__).read_bytes():
        report["notes"].append("Installed scripts/project_os.py differs from this kit and was retained. Apply is adoption, not an upgrade; reconcile the tool with an explicit reviewed diff.")
    return report, operations


def apply_plan(target: Path, operations: list[dict[str, Any]]) -> None:
    target = target.resolve()
    # Recheck the whole write set before starting. This protects against ordinary
    # concurrent edits; it is not a filesystem transaction or a hostile-race lock.
    for op in operations:
        path = safe_path(target, op["path"])
        if op.get("directory"):
            if path.exists() and not path.is_dir():
                raise ProjectOSError(f"Target directory changed after planning: {op['path']}; retry plan.")
        else:
            before = path.read_bytes() if path.exists() else None
            if before != op["before"]:
                raise ProjectOSError(f"Target changed after planning: {op['path']}; retry plan.")
    for op in operations:
        if op["action"] == "reuse":
            continue
        path = safe_path(target, op["path"])
        if op.get("directory"):
            path.mkdir(parents=True, exist_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            if op["action"] == "create":
                with path.open("xb") as stream:
                    stream.write(op["after"])
            else:
                # Append only the governed suffix; do not rewrite original bytes.
                with path.open("ab") as stream:
                    stream.write(op["after"][len(op["before"]):])


def check_project(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    def issue(code: str, message: str, path: str = "", warning: bool = False) -> None:
        (warnings if warning else errors).append({"code": code, "path": path, "message": message})

    report: dict[str, Any] = {"command": "check", "ok": False, "target": str(root), "errors": errors, "warnings": warnings, "harness": {"tasks": 0, "accepted": 0, "state": "not_exercised"}, "limits": LIMITS}
    try:
        data = read_json(safe_path(root, MANIFEST))
        manifest_shape(root, data)
    except ProjectOSError as exc:
        issue("manifest", str(exc), MANIFEST)
        return report
    report["role"] = data["role"]
    report["kit_version"] = data["kit_version"]
    if data["kit_version"] != VERSION:
        issue("version", f"Installed manifest is {data['kit_version']}; checker is {VERSION}. No migration was performed.", MANIFEST, True)
    info = identity(root)
    if data["role"] == "project":
        src = data.get("source_identity", {})
        if not isinstance(src, dict):
            issue("identity", "source_identity must be an object.", MANIFEST)
            src = {}
        same_origin = info["origin"] and info["origin"] in {KIT_ORIGIN, src.get("origin")}
        same_common = fingerprint(info["common_dir"]) and fingerprint(info["common_dir"]) == src.get("common_dir_fingerprint")
        if same_origin or same_common:
            issue("identity", "Project manifest is installed in a repository identifying as its starter kit.", MANIFEST)
    if not info["git_root"]:
        issue("git_unavailable", "No Git working tree was found; revision evidence cannot be verified.", warning=True)
    for key, relative in data["sources"].items():
        path = safe_path(root, relative)
        if not path.is_file():
            issue("missing_source", f"Missing {key} source.", relative)
    try:
        if not safe_path(root, "scripts/project_os.py").is_file():
            issue("missing_checker", "Offline project checker is missing.", "scripts/project_os.py")
    except ProjectOSError as exc:
        issue("checker", str(exc), "scripts/project_os.py")
    for name in ("AGENTS.md", "CLAUDE.md"):
        try:
            path = safe_path(root, name)
            if not path.is_file():
                if data["role"] == "project" or name == "AGENTS.md":
                    issue("missing_entry", "Agent entry is missing.", name)
                continue
            content = path.read_bytes()
            if len(content) > 24_000:
                issue("large_entry", "Entry exceeds 24 KB; move detailed material behind focused links.", name, True)
            if data["role"] == "project":
                if BEGIN not in content:
                    issue("entry_index", "Managed governance index is missing.", name)
                else:
                    append_entry(content, entry_block(data, name == "CLAUDE.md"), name)
        except (ProjectOSError, OSError) as exc:
            issue("entry_index", str(exc), name)
    task_dir = safe_path(root, data["tasks_dir"])
    evidence_dir = safe_path(root, data["evidence_dir"])
    for path in (task_dir, evidence_dir):
        if not path.is_dir():
            issue("missing_directory", "Governance directory is missing.", path.relative_to(root).as_posix())
    task_files = sorted(task_dir.glob("*.json")) if task_dir.is_dir() else []
    report["harness"]["tasks"] = len(task_files)

    def evidence_file(relative: Any, label: str) -> bool:
        try:
            path = safe_path(root, relative)
            if not path.is_file() or path.stat().st_size == 0:
                raise ProjectOSError("Evidence must name an existing, nonempty file.")
        except (ProjectOSError, OSError) as exc:
            issue("evidence", f"{label}: {exc}", str(relative))
            return False
        return True

    def revision(value: Any, label: str, relative: str) -> str | None:
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}", value):
            issue("revision", f"{label} must be a full commit ID, not a moving branch name.", relative)
            return None
        resolved = git(root, "rev-parse", "--verify", f"{value}^{{commit}}")
        if not resolved:
            issue("revision", f"{label} is not a locally available Git commit.", relative)
        return resolved

    seen: set[str] = set()
    for task_path in task_files:
        relative = task_path.relative_to(root).as_posix()
        try:
            safe_path(root, relative)
            task = read_json(task_path)
            for field in ("id", "objective", "base_revision", "status"):
                if not isinstance(task.get(field), str) or not task[field].strip():
                    raise ProjectOSError(f"Task requires nonempty {field}.")
            if task["id"] in seen:
                raise ProjectOSError(f"Duplicate task id: {task['id']}")
            seen.add(task["id"])
            if task["status"] not in TASK_STATUSES:
                raise ProjectOSError("Unknown task status.")
            for field in ("writable_paths", "acceptance_commands"):
                if not isinstance(task.get(field), list) or not task[field] or not all(isinstance(x, str) and x.strip() for x in task[field]):
                    raise ProjectOSError(f"Task requires a nonempty {field} list.")
            scopes = [safe_path(root, value) for value in task["writable_paths"]]
            base = revision(task["base_revision"], "Task base_revision", relative)
            if task["status"] == "running":
                for field in ("executor", "worktree", "session_id"):
                    if not isinstance(task.get(field), str) or not task[field].strip():
                        issue("resume_locator", f"Running task lacks {field}; inspect the existing writer before reassigning it.", relative, True)
            if task["status"] == "accepted":
                report["harness"]["accepted"] += 1
            receipt_ref = task.get("receipt")
            if not receipt_ref:
                if task["status"] in {"submitted", "accepted"}:
                    raise ProjectOSError("Submitted or accepted task requires a receipt path.")
                continue
            receipt_path = safe_path(root, receipt_ref)
            receipt = read_json(receipt_path)
            if receipt.get("task_id") != task["id"]:
                raise ProjectOSError("Receipt task_id does not match the task.")
            receipt_base = revision(receipt.get("base_revision"), "Receipt base_revision", receipt_ref)
            result = revision(receipt.get("result_revision"), "Receipt result_revision", receipt_ref)
            if receipt_base != base or not isinstance(receipt.get("base_revision"), str) or receipt["base_revision"].lower() != task["base_revision"].lower():
                issue("receipt_baseline", "Receipt was produced for a different task baseline.", receipt_ref)
            if base and result and git(root, "merge-base", "--is-ancestor", base, result) is None:
                issue("receipt_ancestry", "Result revision is not a descendant of the task baseline.", receipt_ref)
            changed = receipt.get("changed_files")
            if not isinstance(changed, list) or not all(isinstance(x, str) for x in changed):
                raise ProjectOSError("Receipt requires changed_files as a list of project-relative paths.")
            for changed_file in changed:
                path = safe_path(root, changed_file)
                if not any(path == scope or path.is_relative_to(scope) for scope in scopes):
                    issue("write_scope", "Receipt declares a change outside writable_paths.", changed_file)
            if base and result:
                actual = git(root, "-c", "core.quotePath=false", "diff", "--name-only", "--no-renames", base, result)
                if actual is None:
                    issue("receipt_diff_unavailable", "Git could not compare the base and result revisions; changed_files could not be verified.", receipt_ref)
                elif set(actual.splitlines()) != set(changed):
                    issue("receipt_diff", "changed_files does not match the committed diff between base and result.", receipt_ref)
            checks = receipt.get("checks")
            if not isinstance(checks, list) or not checks:
                raise ProjectOSError("Receipt requires a nonempty checks list.")
            declared_commands: set[str] = set()
            for check in checks:
                if not isinstance(check, dict) or not isinstance(check.get("command"), str) or not check["command"].strip():
                    raise ProjectOSError("Each receipt check requires command, exit_code, and evidence.")
                declared_commands.add(check["command"])
                if type(check.get("exit_code")) is not int:
                    raise ProjectOSError("Receipt check exit_code must be an integer.")
                if task["status"] == "accepted" and check["exit_code"] != 0:
                    issue("failed_check", "Accepted task declares a failed check.", receipt_ref)
                evidence_file(check.get("evidence"), "Check output")
            if not set(task["acceptance_commands"]).issubset(declared_commands):
                issue("missing_check", "Receipt does not include all acceptance_commands.", receipt_ref)
            evidence = receipt.get("evidence")
            if not isinstance(evidence, list):
                raise ProjectOSError("Receipt requires an evidence list; use [] when checks contain all delivery evidence.")
            for reference in evidence:
                evidence_file(reference, "Delivery evidence")
            if task["status"] == "accepted":
                if not isinstance(receipt.get("verified_by"), str) or not receipt["verified_by"].strip():
                    issue("verification", "Accepted task requires verified_by; execution success alone is not acceptance.", receipt_ref)
                verification = receipt.get("verification_evidence")
                if not isinstance(verification, list) or not verification:
                    issue("verification", "Accepted task requires nonempty verification_evidence.", receipt_ref)
                else:
                    for reference in verification:
                        evidence_file(reference, "Acceptance verification")
        except (ProjectOSError, OSError) as exc:
            issue("task", str(exc), relative)
    if task_files:
        report["harness"]["state"] = "records_invalid" if errors else ("accepted_records_checked" if report["harness"]["accepted"] else "records_checked_no_acceptance")
    report["ok"] = not errors
    return report


def snapshot(root: Path) -> dict[str, Any]:
    root = root.resolve()
    report = check_project(root)
    report["command"] = "snapshot"
    report["git"] = {"head": git(root, "rev-parse", "HEAD"), "branch": git(root, "branch", "--show-current"), "status": git(root, "status", "--porcelain=v1")}
    try:
        data = read_json(safe_path(root, MANIFEST))
        report["sources"] = {key: {"path": relative, "sha256": hashlib.sha256(safe_path(root, relative).read_bytes()).hexdigest() if safe_path(root, relative).is_file() else None} for key, relative in data["sources"].items()}
    except (ProjectOSError, OSError, KeyError, TypeError):
        pass
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("plan", "apply", "check", "snapshot"))
    parser.add_argument("--target", required=True, help="Existing project root; never a destination to clone or overwrite.")
    parser.add_argument("--mapping", help="JSON file relative to the current working directory. Its sources/tasks_dir/evidence_dir paths are relative to --target; existing mapped documents are adopted.")
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable report.")
    args = parser.parse_args(argv)
    try:
        target = target_root(args.target)
        if args.mapping and args.command not in {"plan", "apply"}:
            raise ProjectOSError("--mapping is only valid for plan and apply.")
        if args.command in {"plan", "apply"}:
            source = Path(__file__).resolve().parents[1]
            report, operations = build_plan(source, target, args.mapping)
            if args.command == "apply":
                apply_plan(target, operations)
                report["command"] = "apply"
        else:
            report = check_project(target) if args.command == "check" else snapshot(target)
    except (ProjectOSError, OSError) as exc:
        report = {"command": args.command, "ok": False, "errors": [{"code": "preflight", "message": str(exc)}], "limits": LIMITS}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"{args.command}: {'PASS' if report['ok'] else 'FAIL'} (structural checks only)")
        if "changes" in report:
            print(f"Planned changes: {report['changes']}")
        for operation in report.get("operations", []):
            print(f"  {operation['action']}: {operation['path']}")
        for note in report.get("notes", []):
            print(f"  note: {note}")
        for kind in ("errors", "warnings"):
            for item in report.get(kind, []):
                print(f"  {kind[:-1]}: {item.get('path', '')} {item['message']}")
        if "harness" in report:
            print(f"Harness: {report['harness']['state']}")
        print(LIMITS)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
