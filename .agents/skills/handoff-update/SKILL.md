---
name: handoff-update
description: Update a project handoff after substantial work or before a new AI session continues unfinished work.
---

# handoff-update

Resolve the canonical sources from project-os.json when present; otherwise follow the existing project index. Put mutable facts in the status source once. Keep the handoff limited to the unfinished work scene, recovery information, outstanding decisions and links to current facts.

For work spanning conversations or delegated to an executor, follow `docs/02_TECH/TASK_CONTEXT.md` in the source kit, or the equivalent rules adopted by the target project. Preserve the task ID, baseline, exact session locator, current write owner, dispatched context revision, delivered revision, and verification references. Keep the task as the sole lifecycle source. Link to its context records from the handoff rather than duplicating them.

The coordinator and each execution identity maintain separate recovery checkpoints. Record actions actually completed and observed results, unresolved assumptions, ongoing operations with locators, and the next action. Distinguish completed, planned, and unknown. A checkpoint records the last observation; inspect the actual session, worktree, pending output, and external operations before resuming or redispatching. Do not overwrite another participant's checkpoint or treat a missing final answer as proof that execution stopped.

Preserve versioned dispatch snapshots, including constraint sources, rejected options and reasons, assumptions, non-goals, and acceptance criteria. Ensure the receiver can read the actual snapshot in its execution environment. Record corrections as recorded, delivered, or adopted only when the corresponding evidence exists. A shared-file edit is not delivery. Target a resumable session explicitly and retain adoption evidence. For an invocation that cannot receive updates while running, retain pending corrections and reconcile the affected scope when its output returns. Do not accept a stale-context delivery before reconciliation.

Bind completion claims to actual revision and evidence. Mark unknowns and unrun checks explicitly. Update the current recovery pointer when a task advances while preserving historical evidence. Existing tasks without context records remain usable; do not fabricate prior dispatch, delivery, or adoption history.

Maintain necessary records at dispatch, consequential choices, corrections, and handoff as part of authorized work. Routine small changes need no long session summary or new approval round. Do not depend on a pre-compaction hook, access to internal tool summaries, or lossless conversation recovery. Ask only about unresolved substantive intent or authority; preserve disputed material and continue independent work while awaiting an answer.

Handoff maintenance does not initiate or suggest document inventory, cleanup, consolidation, or archiving. Those activities still require an explicit user request. Do not add per-turn summaries or scheduled jobs.
