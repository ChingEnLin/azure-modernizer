---
name: azure-iac-author
description: Author Terraform modules realizing an azure-design output. Delegates IaC discipline to an installed Terraform skill when present. Focuses on Azure-module patterns. Never runs plan or apply — pipelines own those.
---

## When to invoke

Use this skill when the operator asks to author, scaffold, or generate Terraform for a target module — and a relevant design doc already exists under `{docs.spec_dir}/3.x-design/`.

Required input: a **module name** — kebab-case, matching a module type, e.g. `hub-vnet`, `spoke-vnet`, `private-endpoint`, `private-dns-zone`, `workload-identity-federation`. If the operator gives no module name, ask. Do not default.

## Inputs

- `.azure-modernizer/config.yaml`.
- The design doc(s) under `{docs.spec_dir}/3.x-design/` whose target state requires this module. If no relevant design exists, stop and prompt the operator to run `azure-design <topic>` first.
- Operator's chosen environment(s) to compose the module into (e.g., dev, staging, prod).

## MCPs

- **Terraform MCP** — provider/registry lookups for Azure resource types and module signatures.
- **Azure DevOps MCP** (optional) — for PR creation at the end (only with operator confirmation).

## Procedure

1. **Load and validate config using bash+python3:**
   ```bash
   SCHEMA_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/schema/config.schema.json"
   python3 << 'VALIDATE'
   import json, yaml, sys
   try:
       with open('.azure-modernizer/config.yaml') as f:
           config = yaml.safe_load(f)
       with open('$SCHEMA_PATH') as f:
           schema = json.load(f)
       from jsonschema import validate
       validate(instance=config, schema=schema)
       print("✓ Config validated successfully")
   except Exception as e:
       print(f"✗ Validation error: {e}", file=sys.stderr)
       sys.exit(1)
   VALIDATE
   ```

2. Load the relevant design doc(s). Cross-check that the module being authored is one the design called for.

3. **Delegate to a Terraform skill if installed:**
   - Detect whether a Terraform skill (e.g. `terrashark`, `antonbabenko/terraform-skill`) is installed in the host.
   - If yes, invoke the relevant guidance for module structure, testing, provider pinning, formatting. Do not duplicate that discipline here.
   - If no, apply built-in minimal discipline:
     - Pin `azurerm` provider version (`~> 4.0` at time of writing — verify current latest via the Terraform MCP).
     - Pin Terraform version (`>= 1.9`).
     - Add `variable "..."` validation blocks for required inputs.
     - Use `for_each` for multi-instance resources, not `count`, where ordering matters.

4. Look up the Azure resource types involved via the Terraform MCP. Verify the chosen resource versions exist.

5. **Brownfield first — detect the repo's existing Terraform layout before writing anything.** Find the existing module directory (`terraform_modules/`, `modules/`, `terraform/modules/`, ...), root/environment stacks, state backend, and provider pins, and follow them. Default to extending the existing stack in place — a new module directory beside its siblings, wired into the existing root or environment composition, deliverable as one reviewable PR against the existing workspace. Only scaffold a parallel stack (separate state/workspace) if the operator explicitly asks for state separation; name the tradeoff (parallel stacks drift and get abandoned when implementation lands incrementally in the original workspace).
   The canonical layout below applies only when the repo has no Terraform at all. Author the module under the repo's module directory (canonical default `terraform/modules/{module}/`) with:
   - `main.tf` — resource declarations.
   - `variables.tf` — typed inputs with descriptions and validation.
   - `outputs.tf` — typed outputs documented.
   - `versions.tf` — required_providers and required_version.
   - `README.md` — purpose, inputs, outputs, example usage, references to the design doc.
   Use naming conventions from `config.yaml::naming.resource_group_pattern` and `config.yaml::naming.tag_required`.

6. Compose the module into the requested environment stack(s) — the repo's existing root module or environment dirs, or `terraform/environments/{env}/` when scaffolding fresh — referencing the module via relative path.

7. Run `terraform fmt -recursive` and `terraform validate` (in each touched stack dir). Report results.
   - Do NOT run `terraform plan` or `terraform apply`. Stop after `validate`.

8. **Offer to open a PR via the Azure DevOps MCP** with the design doc and ADR linked. Operator confirms before the PR is opened — never automatic.

9. If `work_tracker` is configured, update the corresponding work item.

10. Emit the closing line. Suggested next skill: `azure-migrate-runbook` if the design's migration sequencing has not yet been written.

## Outputs

- Terraform module in the repo's existing module directory (or `terraform/modules/{module}/` when scaffolding fresh) with the five files above.
- Composition into the repo's existing root/environment stack(s).
- `terraform fmt`/`validate` output reported in chat.
- Optionally, a PR (after operator confirmation).
- Optionally, a work-item update.
