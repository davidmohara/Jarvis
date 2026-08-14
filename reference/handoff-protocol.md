# Handoff Protocol

When a sub-agent discovers work that crosses into another agent's domain, it initiates a handoff. Master coordinates all handoffs — sub-agents do not spawn each other directly.

---

## How Handoffs Work

1. The originating agent notes the handoff need in its output, including what it has completed and what the receiving agent should do.
2. Master constructs a handoff payload per the Handoff Payload Schema in `shared-definitions.md#Handoff Payload Schema`. Fields: `from`, `to`, `reason`, `original-request`, `work-completed`, `context`, `required-action`.
3. Master notifies the controller: "[From] is handing this to [To] because [reason]"
4. Master spawns the receiving agent using the spawning protocol, passing the handoff payload as context.
5. The receiving agent continues without re-asking the controller for information already gathered.
6. Output returns to Master, which synthesizes the combined result if needed.

**Handoff patterns:** Each agent defines its handoff triggers in its own Handoff Behavior section (`agents/{name}.md`). Common patterns are in `shared-definitions.md#Defined Handoff Patterns`.

## Circular Loop Detection

Master tracks the handoff chain for each task. If a handoff would create a circular loop (e.g., A hands to B, B hands back to A), Master blocks the handoff and handles the remaining work directly using both agents' output.

## Chain Depth Limit

A handoff chain may not exceed 3 hops (A → B → C → D). If a fourth handoff is attempted, Master stops the chain and escalates to cross-domain synthesis. Three hops is the maximum.

## When the Receiving Agent Is Unavailable

If the target agent is disabled in `config/agents.json` or fails to spawn: report failure using the standard error response format (`shared-definitions.md#Error Response Format`) and return the originating agent's partial result to the controller.
