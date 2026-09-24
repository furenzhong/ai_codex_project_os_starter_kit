# Project OS · Documentation governance for AI-assisted projects

English · [简体中文](README.md)

Keep the same project moving correctly when you switch conversations, models, or execution tools.

Project OS is a lightweight governance kit that integrates into **existing projects**. It helps an AI find effective requirements, current facts, unfinished work, and acceptance evidence. It includes additive installation and local checking tools. You can give this repository link directly to the AI already working on your project.

It is intended for ongoing development with tools such as Codex and Claude Code. For a one-off task, borrowing a few principles may be enough. It does not build your application automatically or require a specific model, technology stack, or multiple agents.

## The simplest way to use it

Send this prompt to the AI in your existing project:

```text
Integrate the documentation governance from
https://github.com/furenzhong/ai_codex_project_os_starter_kit
into the project I am currently developing.

Follow the kit's integration guide. Identify the source kit and the target
project, reuse my existing rules and authoritative documents, and add only
what is missing. Preserve application code, existing documents, uncommitted
work, Git history, and remotes. Do not copy the kit's own product identity
or project status into my project facts.

Run the machine checks and an independent handoff exercise. Tell me what
the checks found, what was actually verified, what remains untested, and
whether a specific decision needs my input. Do not make me fill in a set
of governance forms.
```

The AI's operational entry is the [integration guide](docs/03_DELIVERY/DELIVERY_PROJECT_INSTANTIATION_GUIDE_v1.md). When the project already contains the necessary information, the AI should extract it rather than ask you to enter it again or approve routine implementation choices.

## What it addresses

| Common failure | Mechanism |
|---|---|
| A new conversation reopens settled decisions | Explicit sources for current facts and decisions; read context on demand |
| Multiple “current status” documents disagree | Maintain each fact once; handoffs and briefs reference it |
| An AI says “done” without a clear basis | Bind results to a revision, checks, and evidence; record acceptance separately |
| Work delegated from Codex to Claude Code is difficult to reclaim | Define the baseline, write ownership, session, delivery, and recovery contract |
| Installing a kit replaces the project's identity | Check source and target identities; preserve the target's Git and business content |
| Documentation grows without visible benefit | Run AI handoff and failure exercises; report outcomes and maintenance effort |

Start with the smallest experiment that tests the most consequential uncertainty. Mock data may validate a UI flow; model quality, provider behavior, and generated output need relevant empirical evidence. Templates do not require every project to build a frontend, backend, or rules engine first.

## What integration adds

By default, four small documents are added. Existing equivalents can be mapped directly instead of creating another set.

```text
your-project/
  project-os.json             # Authoritative paths and kit provenance
  AGENTS.md                   # Original content preserved; index appended
  CLAUDE.md                   # Original content preserved; shared-rule import appended
  scripts/project_os.py       # Local checking tool
  project-os/
    RULES.md                  # Stable rules
    STATUS.md                 # Current facts, assumptions, and goals
    HANDOFF.md                # Unfinished work and recovery context
    DECISIONS.md              # Significant choices and their rationale
```

Task and evidence directories are used when work calls for them. Heavier PRD, API, and risk templates remain optional resources in the kit; **they are not copied into every project**. The AI must populate the initial documents from your actual project. File existence alone does not constitute successful integration.

## Manual commands

Requires Python 3.10+ and Git, with no model API key or third-party Python packages. The same Python entry works in Windows PowerShell, macOS, and Linux. Run these commands from the **target project's root**, with the source kit beside it:

```text
git clone https://github.com/furenzhong/ai_codex_project_os_starter_kit.git ../project-os-kit
python ../project-os-kit/scripts/project_os.py plan --target .
python ../project-os-kit/scripts/project_os.py apply --target .
python scripts/project_os.py check --target .
python scripts/project_os.py snapshot --target . --json
```

- `plan` reads the project and lists proposed changes and conflicts. After inspecting it, the AI can `apply` within the user's existing authorization.
- `apply` creates or appends incrementally. Repeated use preserves user content. Conflicts are reported rather than resolved by replacing the project.
- `check` checks declared paths, entrypoints, tasks, and evidence consistency. It calls no model, application service, or network endpoint.
- `snapshot` reports observable state without rewriting project status.

Use `--mapping` to adopt existing documents; see the [mapping example](examples/adoption-mapping.json) and [integration guide](docs/03_DELIVERY/DELIVERY_PROJECT_INSTANTIATION_GUIDE_v1.md). Replace example paths with real target paths. First adoption and upgrading an existing installation are different operations: compare changes and preserve project-owned content when upgrading.

## How to tell whether it helps when the AI uses it

Ask the AI for a short result receipt instead of reviewing every template yourself:

```text
Machine checks: pass / issues found; actual report attached
Independent handoff: pass / fail / untested; correct goal, work state, next step?
Failure exercises: what was detected, and what was missed?
Observed use: recorded repeated work, user corrections, and maintenance effort
Your decision: none, or one specific question
```

At first adoption and after substantial changes to reading or collaboration behavior, follow the [governance trial](docs/03_DELIVERY/GOVERNANCE_TRIAL.md) in an isolated copy: fresh-session recovery, stale statements, missing acceptance evidence, and interrupted work. Day-to-day work checks only relevant changes. It does not rerun the entire trial on every edit or automatically create monitoring or paid calls.

**A machine pass establishes only the checked structural and declaration rules.** It does not establish product quality, the truth of every document, or actual agent adherence. Mark exercises that were not run as untested. Report evidence and a minimal correction when something fails. See the [validation record](docs/05_HANDOFF/evidence/2026-09-25-v1.1-validation.md) for the current version's measured coverage.

## Collaboration such as Codex → Claude Code

The [harness contract](docs/02_TECH/HARNESS_CONTRACT.md) defines tool-independent dispatch and return: goal and baseline → bounded execution → inspectable delivery → acceptance → update the authoritative state.

The current implementation provides contracts, examples, and local receipt checks. **It is not a cross-model orchestrator.** A project chooses its executors, models, and CLI adapters. Separate worktrees do not isolate databases, ports, or external accounts. After interruption, inspect the existing task and session before resuming to avoid repeating effects that already occurred.

## Reading and contributing

- [Governance principles](docs/00_PROJECT_CONTROL/DOCUMENT_GOVERNANCE_SYSTEM.md): ownership of requirements, facts, assumptions, and acceptance.
- [Implementation and limitations](docs/00_PROJECT_CONTROL/PROJECT_CURRENT_STATUS.md): grounded in actual records.
- [Contributing](CONTRIBUTING.md): improve the kit through concrete failures and verification.
- [MIT License](LICENSE): copy, modify, use commercially, and redistribute while retaining the license notice.

Shared rules live in `AGENTS.md`; `CLAUDE.md` is a compatibility entry. Optional `.agents/skills/` provide workflow guidance. Integration does not automatically modify global skills or model configuration. Detailed operational documents are currently primarily in Chinese; this English README covers the complete public quick-start and capability boundaries.
