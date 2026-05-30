---
name: azure-design
description: Produce a CAF/WAF-aligned target-state design for an Azure modernization topic. Spawns the azure-modernizer subagent against the azure-design skill.
argument-hint: <topic: kebab-case, e.g. hub-and-spoke>
---

Spawn the `azure-modernizer` subagent and instruct it to run the `azure-design` skill with the topic argument `$ARGUMENTS`.

If `$ARGUMENTS` is empty, the subagent will ask which topic to design. Do not infer.

The skill output will be saved under `{docs.spec_dir}/3.x-design/` and `{docs.decision_record_dir}/` per the per-project config.
