# handoff-export · ctx-002 · fictional corrected dispatch

Goal: add a JSON status export for unfinished work, preserving its existing fields.
Sources: project-os/DECISIONS.md, DEC-001 and DEC-002.
User constraint (DEC-002): document inventory, consolidation, archive, and deletion require an explicit user request. Handoff, context compaction, or task closure neither starts cleanup nor prompts for cleanup. The first packet omitted this existing requirement.
Rejected options: prose-only output breaks JSON consumers; automatic archival on export violates DEC-002.
Assumption, not verified: consumers accept extra JSON fields. Check existing consumers before adding any.
Non-goals: storage redesign, scheduler, cleanup, or exporting all chat history.
Acceptance basis: preserve existing output fields, review compatibility and absence of cleanup side effects, and independently inspect the actual diff and a representative output. Preserve useful export changes; inspect and remove only the unauthorized archival behavior from the proposed implementation.
