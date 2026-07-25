# azure-modernizer

A Claude Code plugin that acts as an Azure solution architect / network engineer for **modernizing existing Azure estates**.

It inventories live state, designs CAF/WAF-aligned target topologies, authors Terraform modules, and produces executable cutover runbooks. It does not deploy — pipelines own that.

## When to use this

- You have an existing Azure estate and need to harden its network topology (hub-and-spoke, Private Link, Private DNS).
- You're migrating off public PaaS endpoints to Private Endpoints.
- You're moving AKS workloads from credentials to Workload Identity federation.
- You're aligning to CAF/WAF and need a documented decision trail (ADRs, design docs, runbooks).

## When NOT to use this

- **Greenfield Azure deployments** — use `microsoft/azure-skills` instead. It's better at the deploy-direction work.
- **Generic Terraform discipline** — use [terrashark](https://github.com/LukasNiessen/terrashark) or [antonbabenko/terraform-skill](https://github.com/antonbabenko/terraform-skill). This plugin composes with them.
- **Multi-cloud** — Azure only.

## Prerequisites

| Plugin | Why | Install |
|---|---|---|
| `microsoft/azure-skills` | Provides Azure MCP (200+ tools across 40+ services). This plugin reuses it instead of bundling. | `/plugin install microsoft/azure-skills` |
| MS Learn MCP server | Required by Ground Rule 2 (cite docs, never guess). | See your host's MCP configuration. |
| Azure DevOps MCP (optional) | Required only if you configure `work_tracker.type: azure_devops`. | See Microsoft's Azure DevOps MCP docs. |
| Terraform MCP | Provider/registry lookups during IaC authoring. | See HashiCorp's Terraform MCP. |
| Kubernetes MCP (optional) | Required for AKS-touching runbooks. | See your host's MCP configuration. |

## Install

### Claude Code

Add this repo as a plugin marketplace, then install:

```text
/plugin marketplace add ChingEnLin/azure-modernizer
/plugin install azure-modernizer@azure-modernizer
```

Run from inside Claude Code (these are slash commands, not shell). The marketplace lives at `.claude-plugin/marketplace.json`; the plugin manifest is `.claude-plugin/plugin.json`.

To update later:

```text
/plugin marketplace update azure-modernizer
/plugin update azure-modernizer@azure-modernizer
```

To uninstall:

```text
/plugin uninstall azure-modernizer@azure-modernizer
```

### GitHub Copilot CLI

A separate Copilot CLI build of the same plugin lives at [`copilot-cli/`](./copilot-cli/). See [`copilot-cli/README.md`](./copilot-cli/README.md) for prerequisites and install steps. Short version:

```bash
copilot plugin marketplace add https://github.com/ChingEnLin/azure-modernizer
copilot plugin install azure-modernizer@azure-modernizer
```

## Per-project setup

1. Copy `examples/config.example.yaml` to `.azure-modernizer/config.yaml` in your repo root.
2. Fill in `subscription_id`, `tenant_id`, `primary_region`, `docs.spec_dir`, `docs.decision_record_dir`. These are required.
3. Optionally configure `data_regions`, `naming`, `aks`, `work_tracker`. Omit `work_tracker` entirely if you don't use one — the plugin won't nag.
4. Run `/azure-inventory networking` to verify the plugin can reach your subscription.

## Commands

| Command | What it does | Output location |
|---|---|---|
| `/azure-inventory <scope>` | Maps live Azure state for a scope (networking, identity, data-services, all). | `{docs.spec_dir}/1.x-inventory/` |
| `/azure-design <topic>` | Designs a target-state topology for a topic, with MS Learn citations and an ADR. | `{docs.spec_dir}/3.x-design/` + `{docs.decision_record_dir}/` |
| `/azure-assess <topic>` | Produces a topic-scoped assessment (egress audit, secret-zero strategy, cost tradeoffs, as-is diagrams, ...) with live evidence and citations. | `{docs.spec_dir}/2.x-assessments/` |
| `/azure-iac <module>` | Authors a Terraform module realizing a design, extending the repo's existing Terraform layout in place. Runs `terraform fmt`/`validate`. Never `plan`/`apply`. | the repo's existing module/stack dirs |
| `/azure-runbook <topic>` | Produces a cutover runbook with phases, gates, verification, rollback. Re-queries live state at authoring time. Registers the runbook in the progress ledger. | `{docs.spec_dir}/4.x-runbooks/` |

Typical workflow:

```
/azure-inventory networking         # 1. see current state
/azure-design hub-and-spoke         # 2. decide target state
/azure-iac hub-vnet                 # 3. write the modules
/azure-iac spoke-vnet
/azure-runbook hub-and-spoke        # 4. plan the cutover
# 5. a human executes the runbook — or a project-local implementation
#    agent bound by templates/infra-implementer.md, under human approval
#    gates, updating {docs.spec_dir}/progress-ledger.md after every step
```

## Templates

The plugin never deploys, but implementation has to happen somewhere. `templates/` ships two starting points for that phase:

- `templates/infra-implementer.md` — a contract for a project-local implementation agent (copy into your repo's `.claude/agents/`): approval brief before any mutation, `terraform plan` before apply with a hard stop on `replace`/`destroy`, expand-cutover-contract, staging first, cold-resumable checkpoints.
- `templates/progress-ledger.md` — a cross-session progress ledger (current checkpoint, applied changes, open items, session log). The runbook skill creates it automatically; whoever executes keeps it current.

## Ground rules

The `azure-modernizer` subagent operates under five non-negotiable rules:

1. Never hallucinate Azure state — every claim has a live MCP call backing it.
2. Never guess best practices — every design recommendation has an MS Learn citation.
3. Cite the live source for IaC — Terraform registry lookups via Terraform MCP.
4. Surface MCP gaps loudly — if an MCP is down, stop and ask.
5. Track work-item state when a tracker is configured — silent skip if not.

See `agents/azure-modernizer.md` for the full subagent prompt.

## Development

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

Tests validate the config schema and the skill markdown structure. They do NOT call Azure — that's dogfood territory (see "Smoke test" below).

## Smoke test

The honest test for this plugin is dogfooding against a real Azure subscription. Run:

```
/azure-inventory networking
```

against your subscription with `.azure-modernizer/config.yaml` set up. Verify the output snapshot matches what you'd get from manually clicking through the portal. If it matches, the plugin works.

## License

MIT.
