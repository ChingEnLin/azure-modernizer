---
name: azure-iac-author
description: Author Terraform modules realizing an azure-design output. Delegates IaC discipline to an installed Terraform skill (terrashark, antonbabenko/terraform-skill) when present. Focuses on Azure-module patterns. Never runs plan or apply — pipelines own those.
---

## Trigger

`/azure-iac <module>` where module is a kebab-case name matching a module type, e.g. `hub-vnet`, `spoke-vnet`, `private-endpoint`, `private-dns-zone`, `workload-identity-federation`.

If the operator gives no module name, ask. Do not default.

## Inputs

- `.azure-modernizer/config.yaml`.
- The design doc(s) under `{docs.spec_dir}/3.x-design/` whose target state requires this module. If no relevant design exists, stop and prompt the operator to run `/azure-design <topic>` first.
- Operator's chosen environment(s) to compose the module into (e.g., dev, staging, prod).

## MCPs

- Terraform MCP — provider/registry lookups for Azure resource types and module signatures.
- `mcp_microsoft_azu_*` — for PR creation at the end (only with operator confirmation).

## Procedure

1. Load and validate config.
2. Load the relevant design doc(s). Cross-check that the module being authored is one the design called for.
3. **Delegate to Terraform skill if installed:**
   - Detect whether `terrashark` or `antonbabenko/terraform-skill` is installed in the host.
   - If yes, invoke the relevant guidance for module structure, testing, provider pinning, formatting. Do not duplicate that discipline here.
   - If no, apply built-in minimal discipline:
     - Pin `azurerm` provider version (`~> 4.0` at time of writing — verify current latest via Terraform MCP).
     - Pin Terraform version (`>= 1.9`).
     - Add `variable "..."` validation blocks for required inputs.
     - Use `for_each` for multi-instance resources, not `count`, where ordering matters.
4. Look up the Azure resource types involved via Terraform MCP. Verify the chosen resource versions exist.
5. Author the module under `terraform/modules/{module}/` with:
   - `main.tf` — resource declarations.
   - `variables.tf` — typed inputs with descriptions and validation.
   - `outputs.tf` — typed outputs documented.
   - `versions.tf` — required_providers and required_version.
   - `README.md` — purpose, inputs, outputs, example usage, references to the design doc.
   Use naming conventions from `config.yaml::naming.resource_group_pattern` and `config.yaml::naming.tag_required`.
6. Compose the module into the requested environment stack(s) under `terraform/environments/{env}/`, referencing the module via relative path.
7. Run `terraform fmt -recursive terraform/` and `terraform validate` (in each environment dir). Report results.
   - Do NOT run `terraform plan` or `terraform apply`. Stop after `validate`.
8. **Offer to open a PR via Azure DevOps MCP** with the design doc and ADR linked. Operator confirms before the PR is opened — never automatic.
9. If `work_tracker` is configured, update the corresponding work item if `work_tracker` is configured.
10. Emit the closing line. Suggested next skill: `azure-migrate-runbook` if the design's migration sequencing has not yet been written.

## Outputs

- Terraform module at `terraform/modules/{module}/` with the five files above.
- Environment composition under `terraform/environments/{env}/`.
- `terraform fmt`/`validate` output reported in chat.
- Optionally, a PR (after operator confirmation).
- Optionally, a work-item update.
