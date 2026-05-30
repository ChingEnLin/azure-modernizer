---
name: azure-runbook
description: Produce an executable cutover runbook for a designed Azure migration. Spawns the azure-modernizer subagent against the azure-migrate-runbook skill. Never auto-executes the migration.
argument-hint: <topic: matches a design doc, e.g. private-link-dns>
---

Spawn the `azure-modernizer` subagent and instruct it to run the `azure-migrate-runbook` skill with the topic argument `$ARGUMENTS`.

If `$ARGUMENTS` is empty, the subagent will ask which topic to write a runbook for. Do not infer.

The runbook will be saved under `{docs.spec_dir}/4.x-runbooks/`. The skill re-queries live Azure state before authoring the runbook — it does not trust the inventory snapshot. **It does not execute the migration.** The runbook is for human operators to follow.
