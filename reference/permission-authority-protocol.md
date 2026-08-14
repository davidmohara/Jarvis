# Permission Authority Protocol

Master manages a three-tier permission model:
1. **Standing permissions** — pre-delegated at boot from `identity/AUTOMATION.md`
2. **Runtime elevation** — requested by a sub-agent during execution, evaluated by Master
3. **Controller boundaries** — absolute restrictions from `identity/SECURITY.md`; no bypass path

---

## Standing Permissions at Boot

Master reads `identity/AUTOMATION.md` at boot and pre-delegates trust tier assignments per agent domain. Chief gets standing permissions for calendar and inbox; Chase for CRM and pipeline; etc. These are passed in the spawning protocol so agents operate without runtime interruption for their normal task portfolio.

Standing permissions are checked first on any permissioned action. If the action falls within the agent's trust tier, it proceeds immediately. If not, the agent requests elevation.

## Runtime Elevation

When a sub-agent exceeds its standing permissions, it includes in its output:

```yaml
elevation-request:
  agent: agent-name
  permission: "description of the permission needed"
  justification: "why this action is needed for the current task"
  scope: "what specific action will be taken"
```

Master evaluates the request against `identity/AUTOMATION.md` and current task context. Grants are temporary and session-scoped — they expire when the sub-agent terminates unless the controller explicitly makes them standing. Master notifies the controller either way:

> "[Agent] requested permission to [action]. [Granted/Denied] because [reason]."

If the elevation would cross a controller boundary, Master denies it unconditionally.

## Controller Boundary Enforcement

`identity/SECURITY.md` defines hard rules that override all configuration. No agent can violate them regardless of trust tier or elevation. When any agent attempts a boundary violation, Master halts immediately:

> "[Agent] attempted to [action] which violates a security boundary: [rule]. Action blocked. Awaiting your instructions."

The Incident Response protocol in `identity/SECURITY.md` governs what happens next. Controller boundaries apply to all agents uniformly — no exceptions.

## Permission Logging

Every permission decision is logged to `logs/permissions/`:

```yaml
timestamp: ISO-8601
agent: agent-name
action: "what was attempted"
tier: standing | elevation | boundary
result: granted | denied | blocked
reason: "why the decision was made"
```

Grants, denials, escalations, and boundary enforcement events are all logged. The audit trail is queryable by agent, action type, result, and date. Retention and review cadence governed by `identity/AUTOMATION.md` (Audit & Logging) and `identity/SECURITY.md` (Audit Trail).
