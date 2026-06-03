---
name: azure-design
description: Produce a CAF/WAF-aligned target-state design for an Azure modernization topic. Loads relevant inventory snapshots, presents 2-3 design options with tradeoffs, captures the choice as an ADR, and writes the design doc. Use after azure-inventory for the same topic.
---

## When to invoke

Use this skill when the operator asks to design, architect, or plan a target-state for an Azure modernization topic — and at least one inventory snapshot exists.

Required input: a **topic** — kebab-case name like `hub-and-spoke`, `private-link-dns`, `aks-workload-identity-migration`, `aks-outbound-redesign`. If the operator gives no topic, ask. Do not default.

## Inputs

- `.azure-modernizer/config.yaml`.
- The latest inventory snapshot(s) under `{docs.spec_dir}/1.x-inventory/` relevant to the topic. If none exist, instruct the operator to run `azure-inventory <scope>` first and stop.
- Operator's chosen option (collected during the procedure).

## MCPs

- **Microsoft Learn MCP** — fetch CAF/WAF references, reference architectures, Private Link/DNS/Workload Identity docs. Every citation must be live-fetched in this turn.
- **Azure MCP** — residual live checks where the design depends on current state (e.g., available regions for a paired-region hub, current AKS networking mode).

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

2. Locate the relevant inventory snapshot(s). If missing, stop and prompt the operator to run `azure-inventory` first.

3. Fetch MS Learn references for the topic via the Microsoft Learn MCP. Record every URL fetched and the section quoted.

4. Present 2–3 target-state options to the operator, each with: architecture sketch, pros, cons, cost implications, migration complexity (low/med/high), and the MS Learn citations supporting it. Wait for the operator to pick.

5. Produce a design doc with these sections:
   - **Topic** — kebab name + one-line summary.
   - **Current state** — relevant excerpt from the inventory snapshot.
   - **Target state** — chosen option, with a Mermaid diagram showing the topology.
   - **Decision rationale** — why this option vs. the alternatives.
   - **Migration impact** — downtime expectation, sequencing dependencies on other designs, blast radius.
   - **References** — every MS Learn URL cited.

6. Produce an ADR at `{docs.decision_record_dir}/ADR-NNNN-<topic>.md` capturing the decision in standard ADR form (Context, Decision, Consequences, Status: Accepted).

7. Save the design doc to `{docs.spec_dir}/3.x-design/{topic}.md`.

8. If `work_tracker` is configured, update the corresponding work item with the design + ADR paths.

9. Emit the closing line. Suggested next skill: `azure-iac-author` for the modules realizing the design, or `azure-migrate-runbook` for the cutover.

## Outputs

- Design doc at `{docs.spec_dir}/3.x-design/{topic}.md`.
- ADR at `{docs.decision_record_dir}/ADR-NNNN-<topic>.md` where NNNN is the next sequential number across existing ADRs.
- Optionally, a work-item update.
