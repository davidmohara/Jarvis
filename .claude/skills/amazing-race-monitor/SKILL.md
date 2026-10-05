---
name: amazing-race-monitor
description: "Monitor the Amazing Race Photos Teams channel during the event — poll via Graph, vision-review team photo/video posts against quest rules, flag non-compliance for David's ruling, surface creative posts as Bonus Point Review Candidates for Dawn, maintain a live scoreboard. Trigger on 'amazing race', 'race sweep', 'race monitor', 'race standings', 'race ruling', 'bonus review candidate'."
context: fork
agent: general-purpose
model: sonnet
---

<!-- system:start -->
# Amazing Race Channel Monitor (wrapper)

Delegate to the canonical skill for the full procedure:

**Read and follow `skills/amazing-race-monitor/SKILL.md` (canonical) in full.**

Quick reference for dispatch decisions:

- Sweep: `python3 skills/amazing-race-monitor/scripts/poll_channel.py --poll`
  → if new items, spawn a **general-purpose sub-agent with `model: sonnet`** for
  vision review (never a fork — the controller model may reject image inputs)
  → Slack via `systems/slack-bot/post.py` → rulings via `apply_ruling.py`
  → dashboard at http://localhost:7430
- Setup/one-time: Entra app registration + config + `--setup` auth + channel
  resolution — all detailed in the canonical skill.
- Hard rules: read-only toward Teams (never post to the channel); base points
  only; judge only what is visible against `references/quests.json` (no venue
  claims from memory); all Slack through the master-slack path; Bonus Review
  Candidates go as separate Slack messages titled exactly "Bonus Point Review
  Candidate".
<!-- system:end -->
