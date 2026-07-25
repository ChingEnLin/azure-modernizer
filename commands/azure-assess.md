---
name: azure-assess
description: Produce a topic-scoped assessment document (egress audit, secret-zero strategy, cost tradeoffs, IP allowlist reference, stakeholder questionnaire, as-is diagram). Spawns the azure-modernizer subagent against the azure-assess skill.
argument-hint: <topic: kebab-case, e.g. egress-ingress-audit>
---

Spawn the `azure-modernizer` subagent and instruct it to run the `azure-assess` skill with the topic argument `$ARGUMENTS`.

If `$ARGUMENTS` is empty, the subagent will ask which topic to assess. Do not infer.

Topics are open-ended — anything that needs an evidence-backed answer but is not an inventory scan, a target-state design, a Terraform module, or a cutover runbook. The skill output will be saved under `{docs.spec_dir}/2.x-assessments/` per the per-project config.
