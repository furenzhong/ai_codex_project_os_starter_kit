# Contributing / 参与维护

A useful change prevents a concrete failure or makes a real project easier to continue. Explain the trigger, the intended behavior, and how you checked it. Preserve the kit's ability to integrate into existing projects.

有用的改动应解决具体失误或接续障碍。请说明触发条件、预期行为和验证方式。不要仅因为某个新模型发布而新增大套规则。

## Development

Python 3.10+ and Git are sufficient; no model credentials are required.

```text
python -m unittest discover -s tests -v
python scripts/project_os.py check --target .
```

Tests must use temporary repositories. Do not point destructive or fault-injection tests at a user's real workspace. Record what a check cannot prove.

For onboarding, handoff or delegation changes, follow [the governance trial](docs/03_DELIVERY/GOVERNANCE_TRIAL.md). A static pass is not an AI behavior evaluation.

## Documentation

Keep README.md and README.en.md equivalent in capabilities, commands and limitations. Formal contract changes update the mapped source, document catalog and decision log. Other entries should link to current facts instead of repeating them.

Examples must be fictional or deliberately sanitized. Do not contribute project archives, credentials, user logs, machine-specific absolute paths or proprietary Skill bundles. Include provenance for third-party material and retain its license.

Issues are most useful with: the user's request, source-kit revision, the relevant sanitized target structure, observed vs expected behavior, and evidence. Do not require a user to share their entire project.

By contributing, you agree that your contribution can be distributed under this repository's MIT license.
