# Post-Step Completion Protocol

Standard wrap-up sequence for workflow step files. Apply after the step's primary work is done.

---

## 1. Working Memory Write

Write a working memory file to `memory/working/` using this filename pattern:

```
{workflow-name}-YYYY-MM-DD-HHmmss.md
```

Use the session start time from `state.yaml` if available; otherwise use current local time.

Required YAML frontmatter:

```yaml
---
type: working
task_id: "session"
session_id: "{agent}-{YYYY-MM-DD}-{HHmmss}"
agent-source: {agent that executed}
created: {YYYY-MM-DD}T{HH:MM:SS}
expires: {created + 2 days, same time}
status: active
context: "{What the workflow did} — {YYYY-MM-DD}"
---
```

Field rules:
- `session_id`: `{agent}-` prefix + timestamp matching the filename (e.g., `chief-2026-05-25-071532`)
- `created`: ISO 8601 local time, no Z suffix
- `expires`: `created` + exactly 2 days, same time
- `status`: always `active` when first written

Body content (compose from the step's output):
- What was requested and what was produced
- Key data points, findings, or decisions
- Data sources used and any that were unavailable
- Action items or follow-ups surfaced

---

## 2. Eval Record Close

Run this command to close the eval record for this workflow execution:

```bash
python3 systems/eval-harness/close-eval-record.py \
  --name {workflow-name} \
  --type workflow \
  --agent {agent} \
  --status {success|partial|failure} \
  --trigger {boot|manual|scheduled} \
  --started "{session_started from state.yaml}" \
  --steps "{comma-separated step names}"
```

Status logic:
- `success` — workflow delivered with all required outputs
- `partial` — workflow delivered but one or more data sources failed
- `failure` — workflow could not deliver its primary output

---

## 3. State Write

Write `state.yaml` in the workflow directory with `status: complete` and `current-step` matching the final step name:

```yaml
workflow: {workflow-name}
agent: {agent}
status: complete
current-step: {final-step-name}
```

---

## 4. Git Commit

After the workflow completes, commit all changes using the git skill:

```bash
git add -A
git commit -m "chore({agent}): {workflow-name} run — working memory capture and state update"
git push origin main
```

Execute each git command as a separate, atomic call. Never chain with `&&` or `;`. Wait for each to return before issuing the next. See `skills/git/SKILL.md` for the atomic command rule.
