---
name: azure-inventory
description: Map live Azure state, scoped by capability (networking, identity, data-services, all). Spawns the azure-modernizer subagent against the azure-inventory skill.
argument-hint: <scope: networking|identity|data-services|all>
---

Spawn the `azure-modernizer` subagent and instruct it to run the `azure-inventory` skill with the scope argument `$ARGUMENTS`.

If `$ARGUMENTS` is empty, the subagent will ask which scope to use. Do not infer.

The skill output will be saved under `{docs.spec_dir}/1.x-inventory/` per the per-project config.
