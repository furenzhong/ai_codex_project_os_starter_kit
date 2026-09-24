---
name: handoff-update
description: Update a project handoff after substantial work or before a new AI session continues unfinished work.
---

# handoff-update

Resolve the canonical sources from project-os.json when present; otherwise follow the existing project index. Put mutable facts in the status source once. Keep the handoff limited to the unfinished work scene, recovery information, outstanding decisions and links to current facts.

For delegated work, preserve the task ID, baseline, session locator, current write owner, delivered revision and verification references. Do not copy its lifecycle state into another file. On interruption, inspect the existing execution before redispatching.

Bind completion claims to actual revision and evidence. Mark unknowns and unrun checks explicitly. Retire resolved temporary instructions from the current handoff; retain useful history in dated records. Routine small changes do not require a new long session summary.
