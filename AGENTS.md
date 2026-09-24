# Awoo Vibe Coding Governance — repository instructions

This is the reusable governance **source kit**, not a business project. It helps people keep intent, evidence and unfinished work usable across AI sessions and execution tools.

## Read only what the task needs

- Current work: `docs/00_PROJECT_CONTROL/PROJECT_CURRENT_STATUS.md`.
- Continuation point: `docs/05_HANDOFF/HANDOFF_CURRENT.md`.
- Governance rules: `docs/00_PROJECT_CONTROL/DOCUMENT_GOVERNANCE_SYSTEM.md`.
- Applying this kit elsewhere: `docs/03_DELIVERY/DELIVERY_PROJECT_INSTANTIATION_GUIDE_v1.md`.
- Delegating work: `docs/02_TECH/HARNESS_CONTRACT.md`.
- Testing whether governance helps: `docs/03_DELIVERY/GOVERNANCE_TRIAL.md`.
- Structure and document ownership: `docs/00_PROJECT_CONTROL/PROJECT_STRUCTURE_AND_NAMING_SPEC.md` and `DOCUMENT_CATALOG.md` in that directory.

## Interpret the user's destination correctly

“Apply / deploy this repository's governance to my current project” means integrate the kit into that existing target. Treat this checkout as source material. Determine the target from the user's workspace, not from the directory in which the source was downloaded.

Use `scripts/project_os.py plan --target <target>` before `apply`. Inspect the plan and resolve routine choices within the existing request. Do not add an approval round for an already authorized, additive installation. Ask only if the target or a substantive conflict cannot be determined.

Preserve the target's product, code, Git history, remote, existing rules and uncommitted work. Reuse its authoritative documents through a mapping. Do not copy the source kit's project status into the target, replace its README, repoint origin, or push its business content to the source remote. New empty projects are supported too; they do not require a frontend, backend or a particular stack.

## Maintain facts once

`project-os.json` maps each authoritative source. Stable instructions live here; mutable project state lives in the status document. Handoff preserves unfinished context and points to state. Briefs and indexes link to those sources rather than maintaining another progress list. Historical observations belong in dated evidence or session records.

Distinguish user requirements, working assumptions, observed facts and acceptance decisions. Evidence must identify the version and checks it covers. Code, running processes and documentation may disagree: investigate the discrepancy and correct the current summary; do not declare a document true merely because it is marked active. Preserve historical evidence.

## Work in bounded, verifiable steps

- Test the most consequential uncertainty with the smallest useful experiment. Mock data is useful when it answers that question; model quality or provider behavior may require authorized real samples.
- Define the desired behavior and acceptance basis before implementation. Use relevant tests; do not invent tests that only restate a document edit.
- Delegate independent tasks when useful. Assign write ownership and a baseline; collect an identifiable result and verification evidence before accepting it. An isolated worktree does not isolate databases, ports, processes or external accounts.
- Recover an interrupted task by inspecting its recorded session, files and external operation IDs before redispatching. Carry forward the user's existing authorization and constraints.
- Keep model choices and tool-specific invocation details outside durable product rules. Shared instructions have one canonical source; `CLAUDE.md` is an import entry.

## Change and validation discipline

Keep Chinese and English README behavior and limitations in sync. Update the relevant source of truth, document catalog and decision log when their contracts change; do not copy the same update into every entry file.

Required checks for installer/checker changes:

```text
python -m unittest discover -s tests -v
python scripts/project_os.py check --target .
```

Machine checks cover declared structure and evidence consistency, not product correctness or actual AI adherence. For changes to onboarding or recovery behavior, also run the independent trial in `GOVERNANCE_TRIAL.md`. Record skipped checks as untested.

Finish with what changed, what was verified, remaining limitations, and only decisions that actually need the user. Do not keep crucial state solely in the conversation.
