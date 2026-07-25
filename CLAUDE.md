# CLAUDE.md

One-line purpose: A Claude Code plugin that acts as an Azure solution architect for modernizing existing Azure estates — inventory, CAF/WAF design, Terraform authoring, cutover runbooks. It does not deploy.

## Tech stack
- Plugin content is markdown: agents, skills, commands (no application runtime).
- Tooling/tests: Python >=3.11, pytest, jsonschema, pyyaml.
- Config schema: JSON Schema (`schema/config.schema.json`). User config is YAML at `.azure-modernizer/config.yaml`.
- Relies on external MCP servers at runtime (Azure MCP via `microsoft/azure-skills`, MS Learn, Terraform, optional Azure DevOps / Kubernetes). This repo bundles none of them.

## Build / test
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```
Tests validate the config schema, plugin manifest, and skill markdown structure only. They do NOT call Azure. Real verification is dogfooding `/azure-inventory networking` against a live subscription.

## Architecture / key directories
- `agents/azure-modernizer.md` — the subagent prompt; the behavioral core. Five non-negotiable ground rules (no hallucinated state, cite MS Learn, cite Terraform registry, surface MCP gaps, track work items).
- `skills/{azure-inventory,azure-assess,azure-design,azure-iac-author,azure-migrate-runbook}/SKILL.md` — the five capability skills.
- `commands/*.md` — slash commands (`/azure-inventory`, `/azure-assess`, `/azure-design`, `/azure-iac`, `/azure-runbook`) that drive the skills.
- `templates/` — copy-into-project starting points: `infra-implementer.md` (implementation-agent contract with human approval gates) and `progress-ledger.md` (cross-session execution ledger). The plugin itself still never deploys.
- `schema/config.schema.json` — config contract. `examples/config.example.yaml` — template.
- `.claude-plugin/{plugin.json,marketplace.json}` — Claude Code plugin + marketplace manifests (these are what the host reads).
- `plugin.json` (root) — duplicate/legacy manifest; the authoritative one for Claude Code is under `.claude-plugin/`.
- `copilot-cli/` — a separate GitHub Copilot CLI port of the same plugin. Self-contained with its own README, skills, schema, scripts. Changes to core behavior must be mirrored here.
- `tests/` — pytest suite (schema + markdown-structure validation).

## Conventions / gotchas
- Workflow is ordered: inventory → (assess) → design → iac → runbook. The plugin never deploys, never runs terraform `plan`/`apply` (only `fmt`/`validate`). Runbook execution belongs to a human or to a project-local agent bound by `templates/infra-implementer.md`, tracked in the progress ledger.
- Manifest lives in two places (`plugin.json` and `.claude-plugin/plugin.json`); the skills/commands/agents lists are auto-discovered from default dirs, so keep declarations consistent if you edit them.
- Two parallel builds: root (Claude Code) and `copilot-cli/` (Copilot CLI). Keep them in sync.
- Not for greenfield Azure (defer to `microsoft/azure-skills`), generic Terraform discipline, or multi-cloud.
- No emojis in docs.
