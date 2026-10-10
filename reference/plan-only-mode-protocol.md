# Plan-Only Mode Protocol

Canonical dry-run gate for the Podcast-to-Pipeline skill family (and any other skill that points here). Each skill's own Plan-Only Mode section names only what is specific to that skill; the shared protocol lives here.

Pointer form used by each skill:

> Plan-Only Mode: follow `reference/plan-only-mode-protocol.md`.

---

## What Plan-Only Mode means

Plan-Only Mode is a dry-run gate on a skill's live side effects. When it is active, the skill must not perform any live side-effect action: no browser automation, no CRM write, no backend API call, no send, no create. Instead it produces a markdown plan that describes, in order, the actions it would take, with the exact inputs, targets, and rationale for each, saves that plan to the output path the caller requested, and stops.

## How it is toggled

Plan-Only Mode is active when the prompt contains either:

- the phrase "do not execute", or
- the token `eval-mode: plan-only`.

## What it never overrides

Plan-Only Mode is one control among several. It does not replace or weaken any other gate, and no other gate replaces it:

- **Read-only operations are not gated.** They may still run normally, against whatever backend or source the caller specified, to support planning. Each skill states which of its operations are read-only.
- **A separate live per-action confirmation still applies on non-plan-only runs.** Where a skill carries its own live confirmation requirement (for example campaign-send's per-contact send confirmation), that requirement applies on any run that is NOT in Plan-Only Mode. The two controls are independent: Plan-Only Mode governs whether a skill's real side effects can happen at all in an invocation, while the live confirmation governs whether, in a real run, an individual action proceeds without a human saying yes to that specific item. A live run must never act on a batch-level or pre-approved go-ahead alone.
- **No gated tool or API may be called under any circumstances while Plan-Only Mode is active.**
