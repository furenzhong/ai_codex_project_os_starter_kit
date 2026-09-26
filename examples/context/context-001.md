# handoff-export · ctx-001 · fictional dispatch

Goal: add a JSON status export for unfinished work, preserving its existing fields.
Source: project-os/DECISIONS.md, DEC-001 (status export only).
Constraint delivered: exported data must remain JSON; no business-code refactor.
Rejected option: replacing JSON with a prose summary, because callers parse it.
Assumption, not verified: current consumers accept additional fields. Verify before adding fields.
Non-goal: redesigning project storage or building a scheduler.
Acceptance basis: exported fields remain compatible; the coordinator reviews the actual diff and a representative output.

This is the original packet. A later-discovered omission must not be patched into this historical version.
