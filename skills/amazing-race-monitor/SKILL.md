---
name: amazing-race-monitor
owning_agent: knox
description: >
  Monitor the Amazing Race Photos Teams channel during the event: poll for new team
  photo/video posts via Microsoft Graph, vision-review each post against the quest
  rules, flag suspected non-compliance for David's ruling, surface creative posts as
  Bonus Point Review Candidates for Dawn, and maintain a live scoreboard dashboard.
  All output is private to David — nothing is ever posted back to the Teams channel.
model: sonnet
trigger_keywords: [amazing race, race channel, race monitor, race sweep, bonus review candidate, race ruling, race standings]
trigger_agents: [knox, chief, master]
---

# Amazing Race Teams Channel Monitor

Monitor the "Vegas Teams / Photos" Teams channel for the 2026 Amazing Race, review
each posted photo/video against the quest rules, score base points, and keep David
in command of every ruling.

<!-- system:start -->

## Ground rules (non-negotiable)

1. **Read-only toward Teams.** The Graph app has read permissions only. This skill
   NEVER posts, replies, or reacts in the Teams channel. All output goes to David
   (dashboard + Slack) and Dawn (via David).
2. **Base points only.** Score fixed quest points and per-item counts per
   `references/quests.json`. Never score Power, Fortune, or Dawn's creativity
   bonuses. Bonus candidates are surfaced, never scored.
3. **Judge only what is visible.** Vision review compares what is actually in the
   frame against the verified item lists in `references/quests.json`. Never assert
   venue or location facts that are not both (a) in the quest reference and (b)
   visible in the image.
4. **Deterministic first.** The poll is a script, not a model. If nothing new was
   posted, the sweep does zero model work and sends nothing.
5. **All Slack goes through the master-slack skill path** —
   `python3 systems/slack-bot/post.py <channel> "<message>"` as the Jarvis bot.
   No other Slack mechanism.

## Architecture

```
Skill:      skills/amazing-race-monitor/SKILL.md (+ .claude/skills wrapper)
Scripts:    skills/amazing-race-monitor/scripts/
  poll_channel.py    — Graph fetch, parse, media download, ffmpeg frames
  scoring.py         — standings + flag state model (shared by dashboard)
  apply_ruling.py    — David's ok/override/reject rulings
  dashboard_server.py — live localhost scoreboard (auto-refresh)
References: skills/amazing-race-monitor/references/
  quests.json          — quest specs, points, verified item lists
  config.example.json  — config template
Data:       data/amazing-race/ (gitignored) — config.json, auth.json, state.json,
            posts.jsonl, flags.json, confirmations.json, new-items.json, media/
```

## One-time setup

1. **Entra app** (David, in Azure portal → Microsoft Entra ID → App registrations
   → New registration; "Amazing Race Monitor", public client, no secret):
   - Authentication → Allow public client flows: Yes
   - API permissions (Delegated): `ChannelMessage.Read.All`, `Files.Read.All`,
     `Team.ReadBasic.All`, `User.Read`
   - If admin consent is required and David cannot grant it: copy the
     admin-consent URL into a short IT request. Meanwhile continue setup — the
     full pipeline rehearses against a test team/channel in any tenant David
     controls.
2. **Config** — copy `references/config.example.json` to `data/amazing-race/config.json`
   and fill tenant_id + client_id.
3. **Authenticate** — `python3 skills/amazing-race-monitor/scripts/poll_channel.py --setup`
   (device-code flow; follow the printed URL + code).
4. **Resolve the channel** — `--list-teams`, then `--list-channels <TEAM_ID>`;
   write team_id + channel_id into config.json. The channel is the event's
   Photos channel (rules docs call it "Vegas Teams / Photos channel").
5. **Rehearse** — see the Rehearsal section below. Do not skip this.

## The sweep (run every ~4 minutes during the event)

### 1. Poll + review in PARALLEL (event-night mode)

A busy first poll takes 15+ minutes (media downloads for ~60 teams). Never
serialize the vision review behind the poll — posts are appended to
`posts.jsonl` as each is processed, so the reviewer can work captured posts
while the poll continues. Each sweep does BOTH:

1. **Poll:** if no poll process is already running
   (`ps aux | grep "[p]oll_channel.py --poll"`), launch it in the background
   (unbuffered, output to a log — never wrap in a short timeout; a busy channel
   takes minutes). Two polls at once would double-process messages — always
   check first and ride an in-flight poll instead of launching another.
2. **Vision review — sharded:** gather posts in `posts.jsonl` with media and
   no flag for their post_id in `flags.json`. Split the backlog into chunks of
   ~7 posts and launch ONE sub-agent PER CHUNK (see §2), each with an
   EXPLICIT post_id list so agents never overlap. Each shard agent writes its
   own file `data/amazing-race/flags-shard-{n}.json` (JSON array) — never
   flags.json directly. The controller (single writer) merges shards into
   `flags.json` with `scripts/merge_shards.py` (dedupes by post_id, keeps the
   first flag per post, guarantees unique flag_ids, deletes consumed shards).
   Poll stays single; review scales with as many shard agents as needed.

Only when both the poll and the reviewer are quiet (no new posts, no unflagged
captured posts) is the sweep a no-op. Otherwise: update scoring, check for
rulings David has given conversationally, send/re-send only unnotified flags
and bonus candidates, confirm the dashboard daemon is alive, report one
compact line.

- Errors mentioning 401/consent → auth/consent problem, surface to David immediately.
- Attachment download warnings → note them in the sweep report; the affected posts
  still get flagged for manual review rather than silently dropped.
- ffmpeg frame-extraction failures → the reviewer returns verdict "review" with
  reason "video frames unavailable" — the post goes to David's manual queue, never
  silently dropped.

### 2. Vision review (sub-agent — keep images out of this context)

The review sub-agent is a **general-purpose sub-agent with `model: sonnet`**
(a vision-capable model). **Do NOT use a fork for this step:** a fork
inherits the controller's model, and the controller model may not accept image
inputs. The sub-agent:

1. Selects posts to review: every post in `data/amazing-race/posts.jsonl` with
   media attached that has no flag for its `post_id` in `data/amazing-race/flags.json`
   (event-night mode — the poller appends posts live, review runs in parallel;
   `new-items.json` lists the latest batch but is only written when a poll finishes).
   For each post, opens the media files (images directly; for videos, the extracted
   frames in `media/frames/`) with the Read tool. Videos with no extracted frames
   (ffmpeg failure) → verdict "review", reason "video frames unavailable — manual
   review needed", suggested_points 0.
2. Judges each post against `references/quests.json` for that quest.
3. Writes/merges verdicts into `data/amazing-race/flags.json` (schema below).
4. Returns only a compact text summary — no images in the parent context.

**Fork prompt template** (adapt the details per sweep):

> You are reviewing Amazing Race quest posts. Read
> `skills/amazing-race-monitor/references/quests.json` and
> `data/amazing-race/new-items.json`. For each post: open each media file with the
> Read tool (videos: use the extracted frames listed in the post's attachments).
> Judge ONLY what is visible against that quest's vision_criteria and item list. When the post's quest number is missing, INFER the quest from visible content (group cheers with drinks → Quest 2; food-review video → Quest 6) matching only the verified quest criteria. STATION-GAME content (Chubby Bunny marshmallow mouths, Elephant Walk trunk/cups, Trash Can Free Throw, Snort/Raspberry/Whistle circle, Trivia Blitz cards) → verdict "ignore", reason "station game (host-scored) — auto-ignored", 0 points, no bonus: stations assign their own points host-side and are never channel-scored.
> from quests.json. Never assert venue facts you cannot see in the frame. For each
> post append a flag object to `data/amazing-race/flags.json` (load, append, save —
> flag_id format `T{team}-Q{quest}-{n}` continuing the existing numbering, or
> `UNK-{n}` if team/quest unknown):
> `{flag_id, post_id, team, quest, verdict: pass|fail|review, reasons: [],
> items_matched: [<exact item strings from quests.json>], suggested_points,
> bonus_candidate: bool, ruled_at: null}`
> - pass: requirements visibly met → compute suggested_points from the quest spec
>   (fixed points; per-item quests: points × len(items_matched), capped at the
>   spec's base_item_cap or the item list length; quest 14 caps at 2).
> - fail: requirement clearly violated (wrong media type, required item not
>   visible, no media) — state the reason.
> - review: you cannot tell (blurry, dark, ambiguous) — say what is unclear.
> - ignore: STATION-GAME content (Chubby Bunny marshmallow mouths, Elephant
>   Walk trunk/cups, Trash Can Free Throw, Snort/Raspberry/Whistle circle,
>   Trivia Blitz cards) — host-scored, never channel-scored; suggested_points 0,
>   no bonus.
> - bonus_candidate: true when the post is notably creative or original —
>   standout staging, clever execution, above-and-beyond effort. Never affects
>   suggested_points. Bonus-eligible quests (1, 6, 10, 11, 13, 16) are natural
>   candidates, but any quest can produce one.
> Multiple posts by the same team for the same quest: flag later ones with
> reason "duplicate post — earlier post already counts". A per-item quest split
> across multiple posts: still match items, add reason "split post (one-post rule)".
> Return a one-line summary per post. Do not post anything anywhere.

### 3. Notify David (master-slack skill)

Send via `python3 systems/slack-bot/post.py <channel> "<message>"` — use the DM
channel ID from config (`slack_dm_channel`, default U0ANHV5UXEW) for rulings and
`#jarvis` (`slack_jarvis_channel`, default C0AN2PQNXBR) for standing summaries.
Real newlines in the message string, never literal `\n`. Max 5000 chars per send.

**Compliance flags (one message per sweep, only when there are pending rulings):**

```
*Amazing Race — rulings needed (N)*
T12-Q4-1 · Team 12 Quest 4 · review — item not clearly visible: "vintage casino carpet"
T03-Q1-2 · Team 3 Quest 1 · fail — photo posted but quest requires video
Reply or run: ok | override <points> | reject
```

**Bonus candidates (SEPARATE messages, one per candidate, titled exactly
"Bonus Point Review Candidate"):**

```
*Bonus Point Review Candidate*
Team 12 · Quest 1 · creative group photo
Why: 4-shot story sequence staged under the Viva Vision canopy, full commit to the western tableau
For Dawn's review — bonus points are hers to assign (0–10).
```

Send bonus-candidate messages when the candidate is first flagged — do not batch
them across sweeps, and do not resend ones already sent (check the flag's
`bonus_notified` field; the fork sets `bonus_candidate`, the sweep sets
`bonus_notified: true` after sending).

**Also DM immediately:** any unidentified posts (no parseable team or quest number)
with the author name + message text so David can classify them.

### 4. Rulings

David rules in-session or via the command; both land in the same place:

```bash
python3 skills/amazing-race-monitor/scripts/apply_ruling.py T12-Q4-1 ok
python3 skills/amazing-race-monitor/scripts/apply_ruling.py T12-Q4-1 override 15
python3 skills/amazing-race-monitor/scripts/apply_ruling.py T12-Q4-1 reject
python3 skills/amazing-race-monitor/scripts/apply_ruling.py --list
```

When David types a ruling conversationally ("T12-Q4-1 override 15", "that one's
fine"), run the script for him — never just remember it.

### 5. Dashboard

Start once at the beginning of the event evening:

```bash
python3 skills/amazing-race-monitor/scripts/dashboard_server.py &   # http://localhost:7430
# later: --status / --stop
```

It reads state live on every request — standings, pending rulings, bonus
candidates, unidentified posts, and the posted media. Confirm it is running
during each sweep and give David the URL in the first sweep's Slack message.

## Scoring rules (scoring.py — do not reimplement ad hoc)

- Fixed quests: points once the primary post passes (or a ruling promotes it).
- Per-item quests (4/8/9: 5 pts/item; 7: 20 pts/item; 14: 10 pts/item capped at 2):
  points × items_matched, capped by `base_item_cap` or the item list length.
- `fail`/`review` score 0 until ruled. `ok` → suggested points; `override N` → N;
  `reject` → 0. Ruling always beats the vision verdict.
- First post for a (team, quest) counts; later posts are duplicates, never
  double-scored.

## Event-night runbook

1. Pre-flight (earlier in the day): `poll_channel.py --setup` re-auth if tokens
   expired; `--poll` smoke run against the real channel; dashboard started;
   Mac caffeinated (`caffeinate -di &`); test Slack send confirmed.
2. During: sweep every ~4 minutes (scheduled task or loop invoking this skill).
   Each sweep: poll → fork if new media → Slack flags + bonus messages →
   confirm dashboard alive.
3. After: stop the dashboard or leave it for the wrap-up; produce a final
   standings summary for David (Slack + markdown file in `data/amazing-race/`).

## Rehearsal (before the event — mandatory)

In a private test team/channel (any tenant David controls), post and verify:

| Scenario | Expected |
|---|---|
| Normal photo post, "Team 5 Quest 16" + image | pass, 10 pts, flag recorded |
| Video quest (e.g., Quest 5) with a photo posted | fail — wrong media type |
| Post with video attached | frames extracted, judged from frames |
| Missing team number | unidentified → DM David, no score |
| Missing quest number | unidentified → DM David |
| Per-item quest (Quest 9) with 3 items in one post | pass, 15 pts |
| Same quest split across two posts | items counted, "split post" reason |
| Duplicate quest post by same team | duplicate flag, no double score |
| Creative post | bonus_candidate → separate Slack "Bonus Point Review Candidate" |
| Ruling override | standings update live on the dashboard |

Confirm: parsing, media download (inline + attached), ffmpeg frames, verdicts,
scoring math, dashboard live refresh, Slack delivery (flags + bonus), ruling
round-trip.

## Error handling

- Auth/consent failure → surface to David immediately with the exact portal step
  or the IT handoff; keep rehearsing offline fixtures in the meantime.
- Attachment download fails → flag for manual review; never drop the post silently.
- Dashboard dies → restart it in the next sweep; keep Slack as the fallback channel.
- Slack send fails → follow the master-slack skill's no-duplicate rule; include
  the flag list in the session output so David still sees it.

## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so
the eval harness captures this execution:

```
systems/eval-harness/skill-runs/amazing-race-monitor-latest.json
```

Content:
```json
{
  "skill": "amazing-race-monitor",
  "agent": "knox",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if called
from a scheduled task or event loop, `"manual"` otherwise. Set `status` to
`"partial"` if the sweep completed with degraded output (e.g. Slack failed but
dashboard worked), `"failure"` if it could not run at all. Use the actual start
time of this skill execution for `started`. This write is always the final action.

## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic
grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill amazing-race-monitor
```

This prints a compact block: a structure/content/quality assertion breakdown, a
deterministic % score, and a pass/fail gate status, computed from
`systems/eval-harness/assertions/amazing-race-monitor.json` (Tier 2 — 100%
deterministic, no model judgment). It always exits 0, even when no assertion file
exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing
summary's style) in your final response to the operator — the deterministic grade
must always reach the person reading the output, not just the eval record on disk.
A qualitative (Tier 3) grade is added separately later via the end-of-day
`rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade
yourself here.

<!-- system:end -->

<!-- personal:start -->
## Personal configuration (this IES instance)

- IES root: `/Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES`
- Event: 2026 Improving Amazing Race, corporate retreat (Fremont Street, Las Vegas)
- Rules documents: `Corporate/Retreat/2026/Amazing Race/*.docx`
- Slack: DM David `U0ANHV5UXEW` (rulings, unidentified posts), `#jarvis`
  `C0AN2PQNXBR` (bonus candidates, standings summaries)
- Channel identity: David provides the event Team + Photos channel at setup
<!-- personal:end -->
