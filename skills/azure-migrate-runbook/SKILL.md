---
name: azure-migrate-runbook
description: Produce an executable cutover runbook for a designed Azure migration. Re-queries live state at runbook-authoring time (not snapshot time) because state drifts. Decomposes into ordered phases with explicit gates, verification, rollback, and stakeholder coordination. Never auto-executes.
---

## Trigger

`/azure-runbook <topic>` where topic matches an existing design doc under `{docs.spec_dir}/3.x-design/`.

If the operator gives no topic, ask. Do not default.

## Inputs

- `.azure-modernizer/config.yaml`.
- The design doc at `{docs.spec_dir}/3.x-design/{topic}.md` and its ADR. If either is missing, stop and prompt the operator to run `/azure-design <topic>` first.
- The relevant inventory snapshot under `{docs.spec_dir}/1.x-inventory/` for cross-reference.

## MCPs

- `mcp_azure_*` — **live re-query** at runbook-authoring time. The runbook is written against current state, not the inventory snapshot, because state drifts between inventory and migration.
- `mcp_kubernetes_*` — for AKS-touching migrations: verify cluster state, identify in-flight workloads, surface pod disruption budgets.

## Procedure

1. Load and validate config.
2. Load the design doc + ADR for the topic. If missing, stop.
3. **Re-query live state** via Azure MCP for every resource the design touches. Compare to the inventory snapshot.
   - If drift is detected (resource removed, added, or materially changed), surface the drift to the operator. Ask whether to refresh the inventory first or proceed with current state.
4. Decompose the migration into ordered phases. Standard phase shape:
   - **Pre-checks** — explicit preconditions that must be true before the phase starts. Each is a verification command (Azure MCP call or shell command) with the expected result.
   - **Phase steps** — each step has:
     - **Action** — what to do (Terraform apply of module X, Azure CLI command, kubectl manifest, portal step).
     - **Expected result** — what should be true after.
     - **Verification command** — how to confirm (typically `mcp_azure_*` or `kubectl`).
     - **Rollback procedure** — how to revert if the step fails.
     - **Blast radius** — what's affected.
     - **Estimated duration** — minutes/hours, with confidence note.
   - **Cutover gate** — explicit point of no easy return. Names what triggers it (e.g., "disabling Key Vault public network access"). Lists the approval the operator should have before crossing.
   - **Post-checks** — completion criteria (e.g., "private DNS resolves the PaaS hostname", "public endpoints disabled on all in-scope resources", "AKS health probes green for 15 minutes").
5. Identify **stakeholder coordination points**:
   - Who needs to be notified before/during/after each phase.
   - Which change windows are required (and where they live in your change-management system).
   - Comms templates for "starting", "cutover imminent", "complete", "rolled back".
6. Save to `{docs.spec_dir}/4.x-runbooks/{topic}-runbook.md`. Link from the design doc and ADR (edit those files to add a "Runbook: <path>" line near the top).
7. If `work_tracker` is configured, update the corresponding work item with the runbook path.
8. Emit the closing line. Suggested next skill: none — the runbook is for human execution.

## Outputs

- Runbook at `{docs.spec_dir}/4.x-runbooks/{topic}-runbook.md`.
- Updated design doc and ADR with a runbook back-link.
- Optionally, a work-item update.

**The runbook is for human execution. This skill never runs migration commands itself.**
