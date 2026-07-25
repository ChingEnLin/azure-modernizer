<!--
  TEMPLATE — cross-session implementation progress ledger.

  How to install: copy to your docs dir (e.g. <docs-dir>/progress-ledger.md), point
  templates/infra-implementer.md at that path, delete this comment block, and start
  filling it in. Keep the guidance italics until each section has real content.
-->
# Implementation Progress Ledger

> **The source of truth for resumable implementation state.** The task tracker shows
> *state*; this ledger shows *what actually happened, what changed, what's next, and how to
> undo what's in flight*. The implementation agent updates it after every meaningful step so
> any session can resume cold.
>
> **How to read this on resume:** check **§1 Current checkpoint** first (where we are and how
> to undo anything in flight), then **§2 Change log** (what has been applied), then pick up
> from the next unchecked step in **§3**.

Related: `<docs-dir>/README.md` · `<docs-dir>/INSTRUCTIONS.md` ·
agent: `.claude/agents/infra-implementer.md`

---

## 1. Current checkpoint

*One table, overwritten in place each time the position moves. This is the first thing a
cold session reads — if it is stale, everything below is untrustworthy. Update it before
ending any session, and immediately after any apply.*

| Field | Value |
|-------|-------|
| **Checkpoint** | *Where the work stands in one sentence.* |
| **Immediate next** | *The next task to pick up, with its work-item id and any precondition.* |
| **Applied so far** | *One line naming what is already live. Detail belongs in §2.* |
| **Pending / not yet applied** | *What remains in the current phase.* |
| **In-flight state** | *Any half-finished apply, partial cutover, or uncommitted Terraform state. "None" is a valid and important answer.* |
| **Rollback position** | *What a session would have to undo right now, and where the procedure is written.* |
| **Blocked on** | *Approvals, credentials, change windows, or upstream decisions holding work up.* |
| **Last updated** | *Date + what changed since the previous checkpoint.* |

**Decisions taken:**
- *Durable decisions that constrain later steps (state placement, naming, target resource
  group). Link the ADR where one exists.*

**Live-state corrections vs design docs:**
- *Where live Azure differs from what a design doc assumed, with the verification date.
  Ground Rule 1: live state wins over the doc.*

## 2. Change log (applied changes)

*Append-only. One entry per applied change, newest last, never edited after the fact — this
is what a rollback is reconstructed from. Add the entry immediately after the apply
succeeds, not at the end of the session.*

| Date | Task / work item | Change | Env | Rollback | Verified by |
|------|------------------|--------|-----|----------|-------------|
| *YYYY-MM-DD* | *id + short name* | *concrete resources created/modified/destroyed* | *dev / staging / prod* | *exact command or procedure to revert, or "irreversible"* | *the check that confirmed success, and its result* |

## 3. Per-task execution status

*One subsection per task in the current phase, each with its ordered steps as checkboxes.
Tick a step only after its verification passed. A cold session resumes at the first
unchecked box, so unchecked must mean genuinely not done.*

### <task-id> — <task name>

Status: *not started / in progress / applied / verified / rolled back*

- [ ] *Step 1 — action, then the verification that proves it worked.*
- [ ] *Step 2 — …*

Notes: *anything a resuming session needs that the step list does not carry — surprises,
deviations from the runbook, timing constraints.*

## 4. Open items / decisions needed

*Questions blocking or shaping upcoming work, each with an owner. Move an item into §1
"Decisions taken" once resolved, with the resolution — do not silently delete it.*

- **<item>** — *what is undecided, who decides, what it blocks, and by when it is needed.*

## 5. Session log

*One short entry per working session: date, what was attempted, what landed, what did not,
and where the next session should start. Keeps the narrative that the tables above flatten
away. Terse is fine; absent is not.*

### YYYY-MM-DD

- *What was done.*
- *What was learned or corrected.*
- *Where to resume.*
