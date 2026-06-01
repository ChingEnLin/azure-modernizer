# azure-modernizer (GitHub Copilot CLI plugin)

Azure solution architect / network engineer for modernizing **existing** Azure estates.

This is the **GitHub Copilot CLI** port of the [`azure-modernizer` Claude Code plugin](../README.md). It ships the same agent + four skills (inventory, design, IaC authoring, runbook) in the Copilot CLI plugin format.

> Slash commands (`/azure-inventory`, `/azure-design`, …) are **Claude Code only** — Copilot CLI does not have a slash-command surface. Invoke the agent in natural language instead, e.g. *"inventory my networking"*, *"design hub-and-spoke"*, *"author the hub-vnet module"*, *"write the cutover runbook for private-link-dns"*.

## What you get

- **1 agent** — `azure-modernizer` (umbrella architect that delegates to the four skills below).
- **4 skills**:
  - `azure-inventory` — map live Azure state by capability.
  - `azure-design` — produce a CAF/WAF-aligned target-state design + ADR.
  - `azure-iac-author` — author Terraform modules realizing a design.
  - `azure-migrate-runbook` — produce an executable cutover runbook.

## Prerequisites

Configure these MCP servers in your Copilot CLI host before installing:

| MCP | Why | Required |
|-----|-----|----------|
| Azure MCP | Resource Graph, ARM, AKS, Key Vault, Storage, Cosmos, … | Yes |
| Microsoft Learn MCP | `microsoft_docs_search`/`fetch` for citation-backed design | Yes |
| Terraform MCP | provider/registry lookups during IaC authoring | Yes (for `azure-iac-author`) |
| Azure DevOps MCP | PR creation at the end of IaC authoring | Optional |
| Kubernetes MCP | AKS-touching runbooks | Optional |

If a required MCP is missing, the agent stops and tells you which one to start (Ground Rule 4).

## Install

### From this marketplace

```shell
# Add this repo as a marketplace (Copilot CLI looks at .github/plugin/ or .claude-plugin/)
copilot plugin marketplace add https://github.com/ChingEnLin/azure-modernizer

# Install the plugin
copilot plugin install azure-modernizer
```

### Local install (development)

```shell
# From the repo root
copilot plugin install ./copilot-cli
```

### Uninstall

```shell
copilot plugin uninstall azure-modernizer
```

## Configuration

Each project that uses the plugin needs a `.azure-modernizer/config.yaml`. Copy the template:

```shell
mkdir -p .azure-modernizer
cp /path/to/azure-modernizer/copilot-cli/examples/config.example.yaml .azure-modernizer/config.yaml
$EDITOR .azure-modernizer/config.yaml
```

The schema lives at `schema/config.schema.json`. The agent validates the config on every invocation and refuses to proceed if it's missing or invalid — no defaults, no inference.

## Plugin layout

```text
copilot-cli/
├── plugin.json                       # Copilot CLI manifest
├── .github/plugin/marketplace.json   # Marketplace entry
├── agents/
│   └── azure-modernizer.agent.md     # Umbrella agent
├── skills/
│   ├── azure-inventory/SKILL.md
│   ├── azure-design/SKILL.md
│   ├── azure-iac-author/SKILL.md
│   └── azure-migrate-runbook/SKILL.md
├── schema/config.schema.json         # JSON Schema for per-project config
└── examples/config.example.yaml      # Template to copy into .azure-modernizer/config.yaml
```

## Differences from the Claude Code version

| | Claude Code | Copilot CLI |
|---|---|---|
| Manifest location | `.claude-plugin/plugin.json` | `plugin.json` (repo root of plugin dir) |
| Agent file name | `agents/<name>.md` | `agents/<name>.agent.md` |
| Skill file name | `skills/<name>/SKILL.md` | `skills/<name>/SKILL.md` (same) |
| Slash commands | `/azure-inventory`, `/azure-design`, … | **Not supported** — use natural language |
| Tool list field | `tools: Read, Write, Edit, Bash, Glob, Grep` | `tools: ["bash", "edit", "view"]` |
| Marketplace location | `.claude-plugin/marketplace.json` | `.github/plugin/marketplace.json` |

Both versions live in the same repo so a single source of truth feeds both ecosystems. See [the parent README](../README.md) for the Claude Code edition.

## License

MIT — see the repo root.
