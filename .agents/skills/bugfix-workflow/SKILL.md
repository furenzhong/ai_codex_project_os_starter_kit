---
name: bugfix-workflow
description: Use a reported failure to guide a bounded fix, verification and factual status update in an existing project.
---

# bugfix-workflow

Identify expected behavior from the current contract and observed behavior from reproducible evidence. Record what version and environment each observation covers. If the failure cannot yet be reproduced, keep the explanation as a hypothesis.

Fix the smallest responsible scope and run checks proportionate to its effect. An unrelated refactor or broad test expansion needs a concrete reason. Report remaining uncertainty rather than turning an unrun check into a pass.

Update the existing issue and authoritative status when their facts change. A code fix, a passed check and acceptance are separate conclusions. Do not create duplicate issue registers or overwrite historical evidence.
