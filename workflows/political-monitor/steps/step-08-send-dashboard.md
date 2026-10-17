---
status: not-started
started-at: ~
completed-at: ~
model: sonnet
---

<!-- system:start -->
# Step 08: Send Dashboard to Susie

## MANDATORY EXECUTION RULES

1. Pre-flight: verify that david@davidohara.net is a verified sender in your Superhuman account and that Susie's email address is susie@everydayentries.com before sending.
2. Send only via Superhuman MCP, from david@davidohara.net, with `acting_email: david@davidohara.net`.
3. Always update the pinned Cowork artifact after sending the email (see YOUR TASK below).

---

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** The validated `dashboard.html` from step-07
**Output:** The dashboard emailed to Susie + pinned Cowork artifact updated

---

## YOUR TASK

**Pre-flight:** Verify that david@davidohara.net is a verified sender in your Superhuman account and that Susie's email address is susie@everydayentries.com.

Read the `dashboard.html` file. The dashboard uses light-friendly colors (white background, dark text, blue/red accents for left/right), so no conversion is needed. Send via Superhuman MCP from david@davidohara.net to susie@everydayentries.com with subject "Political Monitor — <date>" and the full HTML dashboard as the email body. Use the `mcp__1f6e0bda-36e0-456c-956f-abc8f14b8b8c__create_or_update_draft` and `mcp__1f6e0bda-36e0-456c-956f-abc8f14b8b8c__send_draft` tools with `acting_email: david@davidohara.net`.

**Update the pinned Cowork artifact:** After sending the email, republish the dashboard to the existing pinned artifact using the Artifact tool:
```
Artifact(
  action="publish",
  url="https://claude.ai/artifact/Thq2jTmASnX9XvPqFvbBMV",
  file_path="systems/political-monitor/dashboard.html"
)
```
This is an update to an existing artifact (not a first publish) and does not require an approval card. If the Artifact tool is unavailable in the session, skip silently — the dashboard is already on disk and emailed.

## NEXT STEP

Read fully and follow: `step-09-cleanup-commit.md`
<!-- system:end -->
