---
name: azure-iac
description: Author a Terraform module realizing an azure-design output. Spawns the azure-modernizer subagent against the azure-iac-author skill. Never runs plan or apply.
argument-hint: <module: kebab-case, e.g. hub-vnet>
---

Spawn the `azure-modernizer` subagent and instruct it to run the `azure-iac-author` skill with the module argument `$ARGUMENTS`.

If `$ARGUMENTS` is empty, the subagent will ask which module to author. Do not infer.

The skill will write modules under `terraform/modules/` and compose them into `terraform/environments/`. It runs `terraform fmt`/`validate` but never `plan` or `apply`.
