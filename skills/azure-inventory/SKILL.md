---
name: azure-inventory
description: Map live Azure state, scoped by capability (networking, identity, data-services, all). Produces a structured snapshot with gaps-vs-target-topology callouts. Use this before designing any modernization — designs without inventory are guesses.
---

## Trigger

`/azure-inventory <scope>` where `scope ∈ {networking, identity, data-services, all}`.

If the operator gives no scope, ask which one. Do not default — they may not realize the cost of `all`.

## Inputs

- `.azure-modernizer/config.yaml` (subscription, tenant, regions).
- Operator-provided scope.
- Optional: list of resource group names to limit the scan to. Default: all RGs in the subscription.

## MCPs

- `mcp_azure_*` — Resource Graph queries, networking config, AKS config, Key Vault network rules, Storage firewall rules, Cosmos DB IP allowlists.

If `mcp_azure_*` is unavailable: name the gap, then fall back to read-only `az` CLI commands (`az graph query`, `az network ...`, `az aks show`, etc.) and note the CLI fallback in the snapshot header. Per Ground Rule 4.

## Procedure

1. Load and validate `.azure-modernizer/config.yaml` against the schema. Stop on failure.
2. Determine query set from scope:
   - **networking** — VNets, subnets, peerings, NSGs, route tables, public IPs, LBs, NAT gateways, Private Endpoints, Private DNS Zones, Azure Firewalls.
   - **identity** — Managed identities (system + user-assigned), federated credentials, RBAC role assignments at subscription and RG scope, Key Vault access policies and RBAC.
   - **data-services** — Storage accounts (network rules), Key Vaults (network rules), Cosmos DB (IP rules + Private Endpoints), Azure SQL, Service Bus, Event Hubs.
   - **all** — union of the above. Warn the operator about runtime if the subscription has > 200 resource groups.
3. Run the Resource Graph queries via `mcp_azure_*`. Page through results.
4. For scopes touching AKS: enumerate AKS networking config (CNI mode, network plugin, network policy, pod CIDR, service CIDR, outbound type, authorized IP ranges).
5. For scopes touching data services: cross-reference each resource against subnets/VNets to identify exposure.
6. Produce a structured snapshot with these sections:
   - **Summary** — resource counts by type.
   - **Resource table** — name, type, region, RG, key network config, tags.
   - **Gaps vs. target topology** — bullet list of CAF/WAF deviations (e.g., "no Private Endpoints found", "Key Vault public access enabled", "single LB egress — SNAT exhaustion risk"). Each gap cites the relevant Azure resource(s).
   - **Suggested designs** — list of `azure-design` topics this inventory motivates (e.g., `private-link-dns`, `aks-outbound-redesign`).
7. **Refresh mode:** if a previous snapshot for the same scope exists under `{docs.spec_dir}`, this run is a refresh. Diff the new state against the most recent snapshot and prepend a `## Delta vs {previous-snapshot-date}` section listing resources added, removed, or materially changed (network config, SKU, access posture). Do not overwrite the old snapshot.
8. Save to `{docs.spec_dir}/1.x-inventory/{YYYY-MM-DD}-{scope}.md`, and update the `verified` date comment in `.azure-modernizer/config.yaml` if one exists.
9. If `work_tracker` is configured, update the corresponding work item to reflect the inventory snapshot's existence (add a comment with the snapshot path).
10. Emit the closing line.

## Outputs

- One markdown snapshot per scope, at `{docs.spec_dir}/1.x-inventory/{YYYY-MM-DD}-{scope}.md`.
- Optionally, a work-item update.

The "Gaps" section is the primary input to `azure-design`. The "Suggested designs" section tells the operator which `/azure-design <topic>` to run next.
