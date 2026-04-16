---
name: account-strategy
description: Account strategy deep-dive — history, contacts, open opportunities, competitive landscape, relationship map, and recommended playbook
agent: chase
model: sonnet
---

<!-- system:start -->
# Account Strategy Workflow

**Goal:** Give the executive a complete strategic picture of any account — who they know, what's open, who the competition is, and exactly what to do next. Know the account better than the client knows themselves.

**Agent:** Chase — Revenue & Pipeline

**Architecture:** Sequential 3-step workflow. Aggregate all CRM and knowledge layer account data, research competitive intelligence via web search, then generate the strategy brief and recommended playbook. No user interaction required until the brief is delivered.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| CRM (CRM) | Account history, contacts, open opportunities, engagement history, revenue | CRM via Chrome/M365 auth |
| Knowledge layer | Past meeting notes, relationship history, deal context, notes | Knowledge base API |
| Web Search | Company news (last 90 days), competitive landscape, LinkedIn profiles | Web search MCP |

### Input

This workflow requires an account name to begin. One of:
- A specific company name
- A CRM account ID or domain
- A direct request: "Deep-dive on [company]"

If triggered from the pipeline-review workflow, the account will be pre-identified.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-account-data.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
