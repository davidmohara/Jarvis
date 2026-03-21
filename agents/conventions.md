# Agent Conventions

<!-- system:start -->
Shared protocols that apply to every IES agent. Read this file at the start of every task, immediately after reading your own agent file.

---

## Error Reporting Protocol

All agents are responsible for surfacing self-detected errors back to Master so they can be logged to `systems/error-tracking/error-log.json`. Master owns the log write — agents report, Master records.

### When to Report

Report an error when you:
- Catch yourself mid-execution having used the wrong tool, wrong source, or wrong approach
- Realize output you already produced was incorrect (wrong data, wrong format, bad assumption)
- Skip a required step and then catch it before or after the fact
- Detect a routing mistake — you handled something that should have gone to a different agent

### Explicit Corrections from the Executive

When David corrects any behavior — routing, data, process, tone, anything — **Master must log the correction to `systems/error-tracking/error-log.json` immediately in that same response.** This is not optional and does not require a second prompt. Use `"source": "explicit"` in the entry. The correction is logged first, then the conversation continues. This rule applies regardless of which agent was active when the correction occurred.

Do **not** report minor self-corrections that are trivially part of normal reasoning (e.g., rewriting a sentence). Report errors that would matter if they had shipped uncorrected.

### How to Report

At the end of your response or handoff, include a `## Self-Corrections` block if any errors occurred. Omit the block entirely if there are nothing to report — don't add it just to say "none."

```
## Self-Corrections

- **Category**: [data-accuracy | tool-misuse | routing-error | format-violation | missed-context | assumption-error | process-skip | hallucination | over-engineering | under-delivery]
- **Failure mode**: [lazy-search | stale-cache | wrong-assumption | sloppy-read | bad-conversion | tool-ignorance | context-blindness | pattern-mismatch | scope-creep | protocol-skip]
- **Severity**: [minor | moderate | major]
- **What happened**: [one sentence — what went wrong]
- **Corrected to**: [one sentence — what the right answer was]
```

Multiple errors get multiple bullet groups under the same `## Self-Corrections` heading.

Master will pick up this block, log each entry to the error tracking system, and strip the block before delivering output to the controller. The controller never sees raw error reports unless patterns are surfaced during reviews.

### Severity Guide

| Level | Use when |
|-------|----------|
| `minor` | Caught immediately, no impact on output quality |
| `moderate` | Required real correction effort; output would have been wrong |
| `major` | Could have led to a bad decision, missed commitment, or external impact |

---

*Additional shared conventions will be added here as they are established. This file is the single source of truth for cross-agent behavioral standards.*
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
