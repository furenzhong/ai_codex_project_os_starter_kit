---
name: api-contract-check
description: Check an actual API or data contract change against its callers, behavior and versioned verification evidence.
---

# api-contract-check

Use this only when an API or data contract is part of the task; projects without one do not need an API document.

Compare the intended contract, actual implementation and affected callers. Identify concrete mismatches and their observable impact, including compatibility with existing data when relevant. The document being labeled active does not establish the running service's behavior.

Run appropriate local checks and authorized integration checks. Record the code revision and, when relevant, which version the running process loaded. Report contract coverage and gaps. Update the canonical contract only when the intended behavior was actually changed, not to make a faulty implementation appear compliant.
