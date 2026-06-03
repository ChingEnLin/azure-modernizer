---
name: azure-inventory
description: Map live Azure state, scoped by capability (networking, identity, data-services, all). Produces a structured snapshot with gaps-vs-target-topology callouts. Use this before designing any modernization — designs without inventory are guesses.
---

## When to invoke

Use this skill when the operator asks to inventory, map, audit, or scan their Azure estate — or when they ask about modernization but no inventory snapshot exists yet under `{docs.spec_dir}/1.x-inventory/`.

Required input: a **scope** — one of `networking`, `identity`, `data-services`, `all`. If the operator gives no scope, ask which one. Do not default — they may not realize the cost of `all`.

## Inputs

- `.azure-modernizer/config.yaml` (subscription, tenant, regions).
- Operator-provided scope.
- Optional: list of resource group names to limit the scan to. Default: all RGs in the subscription.

## MCPs

- **Azure MCP** — Resource Graph queries, networking config, AKS config, Key Vault network rules, Storage firewall rules, Cosmos DB IP allowlists.

If the Azure MCP is unavailable: stop, report which call failed, ask the operator to start the MCP. Per Ground Rule 4.

## Procedure

1. **Load and validate config schema using bash+python3:**
   ```bash
   # Resolve schema path relative to skill location
   SCHEMA_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/schema/config.schema.json"
   echo "Validating config against: $SCHEMA_PATH"
   
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
   except FileNotFoundError as e:
       print(f"✗ File not found: {e}", file=sys.stderr)
       sys.exit(1)
   except Exception as e:
       print(f"✗ Validation error: {e}", file=sys.stderr)
       sys.exit(1)
   VALIDATE
   ```

2. **Verify Azure MCP availability:**
   ```bash
   echo "Checking Azure MCP availability..."
   # The agent will report if Azure MCP tools are unavailable
   ```

3. Determine query set from scope:
   - **networking** — VNets, subnets, peerings, NSGs, route tables, public IPs, LBs, NAT gateways, Private Endpoints, Private DNS Zones, Azure Firewalls.
   - **identity** — Managed identities (system + user-assigned), federated credentials, RBAC role assignments at subscription and RG scope, Key Vault access policies and RBAC.
   - **data-services** — Storage accounts (network rules), Key Vaults (network rules), Cosmos DB (IP rules + Private Endpoints), Azure SQL, Service Bus, Event Hubs.
   - **all** — union of the above. Warn the operator about runtime if the subscription has > 200 resource groups.

4. Run the Resource Graph queries via the Azure MCP. Page through results.

5. For scopes touching AKS: enumerate AKS networking config (CNI mode, network plugin, network policy, pod CIDR, service CIDR, outbound type, authorized IP ranges).

6. For scopes touching data services: cross-reference each resource against subnets/VNets to identify exposure.

7. Produce a structured snapshot with these sections:
   - **Summary** — resource counts by type.
   - **Resource table** — name, type, region, RG, key network config, tags.
   - **Gaps vs. target topology** — bullet list of CAF/WAF deviations (e.g., "no Private Endpoints found", "Key Vault public access enabled", "single LB egress — SNAT exhaustion risk"). Each gap cites the relevant Azure resource(s).
   - **Suggested designs** — list of `azure-design` topics this inventory motivates (e.g., `private-link-dns`, `aks-outbound-redesign`).

8. Save to `{docs.spec_dir}/1.x-inventory/{YYYY-MM-DD}-{scope}.md`.

9. If `work_tracker` is configured, update the corresponding work item to reflect the inventory snapshot's existence (add a comment with the snapshot path).

10. Emit the closing line.

## Outputs

- One markdown snapshot per scope, at `{docs.spec_dir}/1.x-inventory/{YYYY-MM-DD}-{scope}.md`.
- Optionally, a work-item update.

The "Gaps" section is the primary input to `azure-design`. The "Suggested designs" section tells the operator which design topic to run next.
