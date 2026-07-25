---
name: azure-assess
description: Produce a topic-scoped assessment document for questions that fall outside inventory, design, IaC, or runbook — egress/ingress audits, secret-zero strategy, cost tradeoff analysis, IP allowlist references, stakeholder dependency questionnaires, as-is topology diagrams. Every live-state claim is backed by an Azure MCP call; every best-practice claim cites Microsoft Learn.
---

## When to invoke

Use this skill when the operator asks for an audit, an analysis, a reference table, a questionnaire, or an as-is picture — a question that needs an evidence-backed answer but is not an inventory scan, a target-state design, a Terraform module, or a cutover sequence.

Required input: a **topic** — a kebab-case name for the question being assessed. Topics are open-ended, not an enum. Examples seen in real modernizations: `egress-ingress-audit`, `secret-zero-strategy`, `cost-tradeoff-analysis`, `ip-allowlist-reference`, `stakeholder-dependency-questionnaire`, `as-is-topology`. If the operator gives no topic, ask. Do not default — an unscoped assessment is a survey, not an answer.

If the request is really inventory, design, IaC, or a runbook, say so and route the operator to `azure-inventory`, `azure-design`, `azure-iac-author`, or `azure-migrate-runbook` instead.

## Inputs

- `.azure-modernizer/config.yaml`.
- Operator-provided topic, plus any scoping the topic needs (resource groups, environments, cost window, stakeholder list).
- Optional: existing inventory snapshots under `{docs.spec_dir}/1.x-inventory/` and design docs under `{docs.spec_dir}/3.x-design/`. Use them as a baseline — never as a substitute for a live check.

## MCPs

- **Azure MCP** — live state for every factual claim about the estate (resources, network rules, identities, public IPs, SKUs, costs).
- **Microsoft Learn MCP** — citations for every best-practice, threshold, limit, or recommendation claim. Live-fetch in this turn.

If the Azure MCP is unbound, a read-only `az` CLI fallback is acceptable (`az ... --output json`, list/show/query verbs only — never create, update, or delete). When the fallback is used, record the degradation in the document's **Method** section: which MCP was missing, which commands substituted for it, and that the operator's local `az` context supplied the credentials.

If the Microsoft Learn MCP is unavailable: stop. Per Ground Rule 2, best-practice claims without a live citation do not ship.

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
       print("Config validated successfully")
   except Exception as e:
       print(f"Validation error: {e}", file=sys.stderr)
       sys.exit(1)
   VALIDATE
   ```

2. Restate the topic as an answerable question and confirm it with the operator before querying. Name what is in scope and what is explicitly out.

3. Determine the evidence set the question needs — the specific resources, properties, cost dimensions, or stakeholders that would change the answer. Write that list down before querying; it becomes the Method section.

4. Collect live evidence via the Azure MCP (or the documented `az` read-only fallback). Every number, name, IP, SKU, and rule in the output must trace to a call made in this turn. Per Ground Rule 1, nothing is inferred from memory or from an older snapshot.

5. Fetch the Microsoft Learn references the topic needs via the Microsoft Learn MCP. Record every URL and the section quoted.

6. If the topic is topology-shaped (traffic paths, egress/ingress, connectivity, dependency graphs), include an **as-is** Mermaid diagram of current state. Label it as-is, not target — target-state diagrams belong to `azure-design`.

7. Produce a single markdown document with these sections:
   - **Question** — the topic restated as the question this document answers, plus scope and out-of-scope.
   - **Method** — what was queried, via which MCP, on which date. Note any MCP degradation and the fallback used.
   - **Findings** — the evidence, organized for the topic (table, matrix, diagram, or questionnaire as fits). Each finding cites the resource(s) it came from.
   - **Assessment** — what the findings mean: risks, gaps, tradeoffs, or the recommendation. Distinguish observed fact from architectural judgement.
   - **Open questions** — what could not be determined and who or what would resolve it.
   - **References** — every Microsoft Learn URL cited.

8. Save to `{docs.spec_dir}/2.x-assessments/{topic}.md`. If `work_tracker` is configured, prefix the filename with the work item identifier (`{work-item-id}-{topic}.md`) so the doc and the tracker stay legible to each other.

9. If `work_tracker` is configured, update the corresponding work item with the assessment path and a one-line summary of the assessment.

10. Emit the closing line. Suggested next skill: usually `azure-design` for the topic the assessment motivates — or `azure-inventory` first if the assessment exposed a scope that was never mapped.

## Outputs

- One markdown assessment at `{docs.spec_dir}/2.x-assessments/{topic}.md` (or `{work-item-id}-{topic}.md` when a work tracker is configured).
- Optionally, a work-item update.

An assessment is an input to design, not a design. It states what is true and what it costs — the target state belongs to `azure-design`.
