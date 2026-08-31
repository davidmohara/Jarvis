---
name: plaud-speaker-id
owning_agent: knox
model: sonnet
description: >
  Identify generic speaker labels (Speaker 1, Speaker 2, etc.) in Plaud recordings
  by cross-referencing recording timestamps against calendar attendees. Auto-resolves
  when confidence is high; surfaces a consolidated question to the controller when it
  cannot. Use during the plaud-ingest workflow step-03, or standalone when a recording
  has unidentified speakers. Also triggered by "who is Speaker 1", "identify the
  speakers in this recording", or "I need to label the speakers".
trigger_keywords: [speaker id, identify speaker, who was on the call]
trigger_agents: [knox, chief]
---

# Plaud Speaker Identification

Resolve generic speaker labels in Plaud recordings to real names, using calendar
data as the primary signal and controller input as the fallback.

## ⛔ HARD GATE — READ BEFORE ANYTHING ELSE

**You MUST scan the transcript for self-identification, then query the calendar, before
asking the controller. No exceptions, and in that order.**

This is a two-part gate, both parts confirmed failing independently on 2026-08-31
(`err-20260831T145747-LDPD1Q`, `err-20260831T145748-3SVX4A`):

1. **Self-ID scan first.** Most speakers in Plaud recordings state their own name aloud,
   typically near the end of the recording (sign-offs, "this is X", introductions).
   Section "0" below runs a full-transcript self-identification scan for every
   unresolved speaker *before* calendar-attendee matching is even attempted. Skipping
   straight to calendar heuristics when the transcript itself already answers the
   question is a protocol violation.
2. **Calendar before controller.** The calendar resolves most of what self-ID doesn't.
   Asking the controller before checking the calendar is a protocol violation (logged
   as err-20260522T191304-TO2VXV). A calendar subject-line not matching the transcript's
   apparent topic is **not**, by itself, grounds to give up on the calendar — see the
   Search Discipline requirement in section 2a below (minimum 3 strategies: matched
   event, attendees on that event, adjacent/nearby events) before treating the calendar
   as unhelpful for a given recording.

Do not surface any speaker question to the controller until:
1. The full transcript has been scanned for self-identification for every recording
   with unresolved speakers (section 0)
2. The M365 calendar has been searched for every recording with speakers still
   unresolved after the self-ID scan — including attendees and adjacent events, not
   just the single best-matching event by subject line (section 2a)
3. All auto-resolution heuristics have been applied
4. One or more speakers genuinely cannot be resolved from self-ID + calendar + heuristics

If self-ID and/or the calendar resolve all speakers: proceed silently. No user interaction at all —
**unless step 3's off-invite validation gate flags something.** A resolved name that
isn't on the attendee list, or a name mentioned/addressed in the transcript that was
never assigned to any speaker, breaks silence even on an otherwise fully auto-resolved
recording. This is deliberate: those are exactly the cases most likely to be a wrong
resolution, and "proceed silently" was never meant to hide a mis-tag from the
controller, only to skip bothering them when nothing looks wrong.

---

## How this works

The Plaud fetch script detects when a transcript contains generic speaker labels
("Speaker 1", "Speaker 2", etc.) and writes a `_speakers.json` file to staging
alongside the transcript markdown. This skill reads those files, attempts to match
speakers to calendar attendees automatically, and surfaces any that can't be
auto-resolved to the controller as a single consolidated prompt. Every resolution —
whether it came from a heuristic or from the controller — is also checked against the
calendar's own attendee list before being finalized (step 3 below); a resolved name
that isn't actually on the invite gets surfaced, even on an otherwise fully
auto-resolved recording. This is not optional and not folded into the heuristics —
it's a validation gate on the *output* of resolution, run every time.

## Prerequisites

- `_speakers.json` file(s) in `~/Downloads/transcript-staging/`
- M365 calendar access (via MCP) for the recording's date
- (Optional) Clay contact data for additional name context

## Input: Speaker mapping file structure

```json
{
  "file_id": "abc123",
  "recording_name": "Meeting with Todd Wynne",
  "all_speakers": [
    {"name": "Speaker 1", "segments_count": 42, "sample_text": "I think we should look at the AI maturity..."},
    {"name": "Speaker 2", "segments_count": 31, "sample_text": "The timeline for the POC is..."}
  ],
  "untagged_speakers": ["Speaker 1", "Speaker 2"],
  "known_speakers": [
    {"speaker_id": "...", "speaker_name": "David O'Hara", "speaker_type": 1, ...}
  ],
  "status": "needs_mapping"
}
```

## Execution

### 1. Load all `_speakers.json` files from staging

Enumerate `~/Downloads/transcript-staging/plaud_*_speakers.json`. Load each.
Group by recording (one JSON file per recording that has generic speakers).

### 2. For each recording: scan for self-identification, then attempt calendar auto-resolution

**0. Self-identification scan (MANDATORY, runs before any calendar lookup)**

For every speaker still labeled generically (`Speaker N`), scan that speaker's **full**
set of transcript segments — not just the `sample_text` snippet in `_speakers.json` — for
self-identification. If the staged markdown/full transcript isn't already loaded, fetch
it before skipping this step; a truncated sample is not a substitute for the real scan.

Look specifically at:
- **The end of the recording** — most people sign off by name ("Alright, this is Todd,
  talk soon", "Thanks everyone, Robbie out"). Check the last several segments for each
  unresolved speaker first, since this is the highest-yield location.
- **The beginning of the recording** — round-the-table introductions ("Hey, it's Sarah
  here").
- **Anywhere else in the transcript** — direct self-reference ("As I mentioned, this is
  [Name] from [Company]...", "[Name] here, I think...").

If a speaker's own segments contain a first-person self-identification that names them,
resolve that speaker directly from the transcript. This is independent of and does not
require calendar confirmation — a person naming themselves is a stronger signal than a
calendar attendee-count inference. Still run this resolution through the step 3
attendee-list validation gate below (a self-identified name should also be a plausible
attendee, but the validation gate is informational/flagging here, not blocking, since
self-ID is direct evidence — see step 3a's exemption note).

Only speakers who produce no self-identification anywhere in their segments proceed to
the calendar-based heuristics in steps 1-7 below.

**a. Extract recording time window**

The recording's date AND time are in the `_speakers.json` metadata. Use the precise timestamp for matching:

```
mcp__b8c41a14-7a9b-4ea5-ab12-933ee04bc52f__outlook_calendar_search(
  query="",
  start: "<recording-date>T00:00:00",
  end: "<recording-date>T23:59:59"
)
```

> **TIMESTAMP MATCHING — MANDATORY:** Match the recording to the calendar event whose time window **contains or closely overlaps the recording's start timestamp** (converted to local time). Do NOT pick the largest or most prominent event on the day. A recording at 14:32 CDT must match against the event scheduled for that time window — not a morning standup or an unrelated afternoon block. Recordings start when David presses record, which may be a few minutes before or after the scheduled start. Use a ±15 minute window for the start time match, expanding to ±45 minutes only when no event is found in the tighter window (see edge case 3 below).

Find calendar events that overlap the recording's time window with the precision rules above.

> **SUBJECT-LINE MISMATCH IS NOT GROUNDS TO GIVE UP ON THE CALENDAR.** A matched event's
> subject/title not obviously fitting the transcript's apparent topic (e.g. a business
> meeting title on a recording that sounds personal/casual) is common — meeting titles are
> often stale, generic ("AI Leaders Weekly"), or set up for a different original purpose
> than how the time slot actually got used. This happened concretely on 2026-08-31
> (`err-20260831T145747-LDPD1Q`): a "AI Leaders Weekly" event was matched to a recording
> that sounded like a personal catch-up, and that mismatch alone was treated as a dead end
> instead of being investigated further. Per the Search Discipline rule in SYSTEM.md
> (minimum 3 search strategies before reporting not-found), a subject-line mismatch
> requires you to try, in order, before concluding the calendar can't help:
> 1. **Check the matched event's attendee list anyway** — the topic discussed on a call
>    frequently drifts from the meeting's original title; the attendee list is still valid
>    signal even if the subject reads oddly.
> 2. **Check adjacent events** — the 30-60 minutes before/after the matched event on
>    David's calendar, in case the recording actually spans a different (possibly
>    untitled, personal, or informally-added) block than the one that technically overlaps.
> 3. **Check for recurring 1:1 patterns** — if a first-name-only or partial match appears
>    in the transcript (e.g. "Robbie"), search calendar history for recurring meetings with
>    an attendee matching that name, even outside the exact recording date, to confirm the
>    relationship and correct spelling.
> Only after all three come up empty does "calendar had no matching event" become a valid
> basis to fall through to controller escalation for that speaker.

**b. Get attendee list from matching calendar event**

From the matched event, extract all attendee display names **and their email domains**
(the part after `@`). Domain is a relationship/seniority signal, not just a name lookup
key — see heuristic 7 and the controller-prompt template below. Do not discard it after
extraction the way earlier versions of this skill did.

Remove David O'Hara from the attendee list — he is always present, his voice is
registered as `speaker_type: 1` in the known_speakers list.

**c. Auto-resolve using heuristics (apply in order)**

1. **Known speakers match**: If a speaker in `known_speakers` (already registered in Plaud)
   maps to a generic label via the recording's `embeddingKey`, use that name directly.

2. **David is the owner**: David (`speaker_type: 1`) is always the highest-segment-count
   speaker in internal meetings. In external meetings (David as the only Improving person),
   David is still typically highest segment count. Assign David to highest `segments_count`.

3. **Single external attendee**: If calendar shows exactly 2 attendees (David + one other),
   and transcript has 2 speakers, the assignment is unambiguous regardless of segment counts.

4. **Sample text name drops**: Scan `sample_text` for name mentions. If Speaker 1's sample
   says "...as Todd mentioned..." then Speaker 1 is likely David talking about Todd, not Todd.

5. **Title self-identification matching**: Scan `sample_text` (and other segments for that
   speaker, if the sample alone is inconclusive) for self-identifying role/title language —
   "I'm HR", "I'm the [title]", "as [title] I...", or a bare title fragment like "Chief
   Commercial Officer." This requires actually knowing each attendee's real title, not just
   their name — see heuristic 7 for where that comes from (Clay, falling back to a web
   search). Cross-reference the spoken title against attendee titles:
   - Treat it as a strong, auto-resolvable match if the spoken title clearly maps to exactly
     one attendee's real title, including near-misses from transcription error (Plaud
     mis-hears titles constantly — "Chief County Officer" is almost certainly "Chief
     **Commercial** Officer" mangled by the transcriber, not a real title. If a spoken
     fragment is phonetically/structurally close to exactly one attendee's actual title and
     no other attendee's, treat it as a match).
   - Treat it as inconclusive (not an auto-resolve) if the spoken title is generic enough to
     fit more than one attendee (e.g., "I'm on the leadership team") or doesn't map clearly
     to any fetched title.
   - This heuristic is on par with heuristic 6 for auto-resolve confidence (see confidence
     threshold below) — a clean title match is as strong a signal as a name appearing in the
     recording title.

6. **Recording title contains attendee name**: If the recording is named "Meeting with
   Sarah Chen" and there is a Sarah Chen in the attendee list, she is the non-David speaker.

7. **Attendee title lookup — Clay first, web search fallback**: If attendee names from
   calendar are ambiguous, or heuristic 5 needs real titles to compare against, look them up
   in Clay for role/company context ("VP of Sales" vs "Principal Consultant"). **Clay is
   frequently empty or stale for people who changed roles recently** (a title change,
   promotion, or new hire within roughly the last quarter often hasn't been captured yet).
   When Clay returns no title/role data for an attendee, do not stop there — fall back to a
   web search for that person's current title at their employer. The employer is derivable
   from their email domain (captured back in step 2b): search `"[attendee
   name]" [company from domain] title`, or similar. A newly-appointed leadership team is
   exactly the case Clay is least likely to have — don't let an empty Clay result end the
   lookup.

**d. Confidence threshold**

Mark a resolution as auto-confirmed if:
- It came from the step 0 self-identification scan (highest confidence — the person
  named themselves)
- OR it satisfies heuristic 1, 2, or 3 (deterministic)
- OR it satisfies heuristic 4, 5 (title self-identification), or 6 with calendar
  confirmation (attendee in list)

Mark as needing controller input only if, after the step 0 self-ID scan AND the full
3-strategy calendar search in step 2a (matched event attendees, adjacent events,
recurring 1:1 pattern check) have all been exhausted:
- 3+ unresolved speakers remain after all heuristics
- Calendar had no matching event **and** adjacent-event and recurring-pattern checks
  (step 2a) also came up empty — a subject-line mismatch alone is never sufficient, see
  step 2a
- Attendee count doesn't match speaker count
- Heuristics produce conflicting signals

A speaker is only escalated to the controller if self-ID (step 0), the full calendar
search discipline (step 2a), and the heuristics above all failed to produce a resolution.
Escalating because a plausible name existed but wasn't checked against the transcript's
own self-identification or the calendar's attendees/adjacent events first is the exact
failure pattern from `err-20260831T145747-LDPD1Q` and `err-20260831T145748-3SVX4A` — do
not repeat it.

### 3. Validate every resolution against the attendee list

Run this after resolution (step 2) and before any prompt is built or `state.yaml` is
written — on every recording, including ones where every speaker auto-resolved. This is
a validation gate on the *output* of resolution, not another resolution heuristic, and
it applies equally to auto-resolved and controller-confirmed mappings (a controller can
mis-hear or mis-type a name too).

This exists because of a real, already-observed failure class: Plaud auto-tagged a
segment as "Robyn Fuentes" in the Jack Claeys "Bifurcated Engagement Strategy" recording
even though Robyn was never an attendee on that call — Knox caught it that time and
flagged it as non-blocking, but the skill itself had no systematic check for this. In
the same session, the "08-25 Meeting: AI Strategy..." recording has Speaker 5 (resolved
to Keith Oltchick) saying "Randy, do we have anyone doing that now?" — addressing a
"Randy" who never appears on the calendar invite at all. Nothing mis-happened with Randy
this time, but a future name-drop heuristic (4) matching an off-invite name exactly the
same way would produce exactly the Robyn Fuentes failure again, silently.

**a. Check every resolved `{Speaker N: Name}` pair**

For each speaker now mapped to a name (from any heuristic, or from a parsed controller
response in step 5), check whether `Name` appears in the matched calendar event's
attendee list from step 2b — by display name or email, with reasonable fuzzy matching
(e.g. "Robyn Fuentes" vs. an invite entry of "Robyn M. Fuentes" or an email-derived
"rfuentes" should still count as a match; don't demand exact string equality). Known
speakers already registered in Plaud (heuristic 1) and David himself are exempt — they
aren't expected to be a fresh invite match every time. Speakers resolved via the step 0
self-identification scan are not exempt from this check, but a mismatch there is
downgraded to the informational ⚠️ flag (not a block) — the transcript naming itself is
strong direct evidence, so a resolved self-ID name absent from the invite most likely
means an uninvited/late-added attendee, not a mis-tag; still surface it so the controller
can confirm.

If `Name` is **not** found among attendees (even fuzzily): do not silently accept the
resolution, regardless of which heuristic produced it or how high its confidence was.
Flag it for the controller prompt in step 4 — see the message format addition below.
This overrides "proceed silently" per the HARD GATE note above. Exception: if the
resolution came from the step 0 self-identification scan, still include the ⚠️
informational flag in the prompt, but do not hold `speaker-mappings` as pending for it —
the transcript is direct first-person evidence and the mapping can be finalized while
the flag is surfaced for awareness.

**b. Check for off-invite names mentioned but never assigned**

Separately, scan the transcript/sample text across all speakers for names that are
addressed or referenced (e.g. "Randy, do we have anyone doing that now?") but were never
themselves assigned to a speaker label. If such a name is not on the attendee list
either, note it as a distinct "mentioned but unidentified, off-invite" item — this is
not a speaker resolution error (nobody was mis-tagged as this person), just a fact worth
surfacing: it may be an uninvited attendee, a misheard name, or someone real who simply
wasn't on the calendar and doesn't need a speaker slot. Do not hold up ingestion for
this — it's informational, not a blocker.

**c. What this changes downstream**

- If step 3a found nothing wrong and step 3b found nothing to note: proceed exactly as
  before (silently, if step 2 also fully auto-resolved everything).
- If step 3a or 3b found something: that recording no longer qualifies for silent
  auto-resolution even if every speaker technically got a name. Include it in the
  consolidated controller prompt (step 4) with the flag(s) below, alongside any
  genuinely-unresolved recordings. Do not write `accumulated-context.speaker-mappings`
  as final for a flagged recording until the controller has had a chance to confirm or
  correct it.

### 4. Compile unresolved and flagged speakers for controller prompt

If any recordings have unresolved speakers, **or step 3 flagged an off-invite
resolution or mention**, build a single consolidated message. All recordings in one
message — never send multiple separate prompts.

**Message format:**
```
I need your help identifying speakers in [N] recording(s) before I can finish ingesting them.

---

**"[Recording Name]"** — [Date, HH:MM]
Calendar attendees: [Name] ([title from Clay/web if found]), [Name], [Name — email domain,
  flagged if different from the rest, e.g. "R Jones — ashfordinc.com, different domain
  than the rest — likely from [company inferred from domain], not [primary org]"]

  Speaker 1 ([N] segments): "[sample text]"
  Speaker 2 ([N] segments): "[sample text]"

Who is Speaker 1 and Speaker 2?
*(e.g., "Speaker 1 = David, Speaker 2 = Todd")*

⚠️ [Name] resolved for Speaker N is not on the calendar invite for this event.
Attendees were: [list]. Confirm this is correct, or flag if it's a mis-tag.

ℹ️ "[Off-invite name]" is mentioned/addressed in this recording but never assigned to a
speaker and isn't on the invite either — just flagging in case it's useful context, no
action needed.

---

**"[Another Recording]"** — [Date, HH:MM]
...
```

**Domain-mismatch line is conditional, not decorative.** Only include the "different domain
than the rest" callout when at least one attendee's domain actually differs from the
majority — don't pad every prompt with it. When present, it exists to give the controller
disambiguating context the raw transcript quotes don't carry (a different domain usually
means a different company — an asset manager, a client's client, a vendor — not just a
typo), even for recordings the skill still can't fully auto-resolve. Include a title next
to a name whenever heuristic 7 found one (Clay or web), regardless of whether that
attendee's speaker mapping itself was auto-resolved — it's useful context either way.

Likewise, the ⚠️/ℹ️ lines from step 3 are conditional — only appear when step 3 actually
found something. A recording with zero step-3 findings and zero unresolved speakers
never enters this prompt at all (still fully silent, per the HARD GATE).

Update `state.yaml status: awaiting-input` before surfacing the prompt.
Do not surface recordings with no unresolved speakers and no step-3 findings in this
prompt — silent auto-resolution is still the default outcome for the common case; step 3
is a check that most recordings will simply pass.

### 5. Parse controller response

When the controller responds, parse the speaker assignments. Accept flexible formats:
- `"Speaker 1 = David, Speaker 2 = Todd"`
- `"1 is me, 2 is Todd"`
- `"top one is David, second is Todd Wynne"`

Normalize to: `{"Speaker 1": "David O'Hara", "Speaker 2": "Todd Wynne"}`

Merge with auto-resolved mappings. Update `state.yaml`:
- `accumulated-context.speaker-mappings` = full resolved set
- `accumulated-context.pending-speaker-mappings: []`
- `status: in-progress`

### 6. Return final mappings

```yaml
speaker_mappings:
  abc123:
    Speaker 1: "David O'Hara"
    Speaker 2: "Todd Wynne"
  def456:
    Speaker 1: "David O'Hara"
    Speaker 2: "Sarah Chen"

resolution_method:
  abc123: auto (self-identification)
  def456: auto (calendar + segment count)
  ghi789: controller-confirmed
```

## Standalone invocation

This skill can be invoked directly (outside the plaud-ingest workflow) when the
controller asks about speaker identification for a specific recording. In that case:
1. Load the relevant `_speakers.json` from staging (or reconstruct from the staged markdown)
2. Run steps 2-6 above (including the step-3 validation gate — standalone invocation is
   not an exemption from it)
3. Apply the mappings via `fetch_plaud.py --rename` immediately (no workflow state to update)

## Error handling

| Error | Action |
|-------|--------|
| Calendar unavailable | Self-ID scan (step 0) still runs and resolves what it can. For everything else, skip calendar auto-resolution and put remaining recordings in `pending-speaker-mappings`. |
| Self-ID scan finds no self-identification for a speaker | Not an error — fall through to calendar-based heuristics (steps 1-7) per the normal order. |
| No `_speakers.json` found | No generic speakers in this recording — mark all speakers as resolved. |
| Controller response is ambiguous | Ask for clarification on only the ambiguous recording, not the whole set. |
| More speakers in transcript than attendees | Include all unknown speakers in the prompt with a note: "There are more speakers than calendar attendees — this may have been a group call." |
| Step 3 finds a resolved name not on the invite | Do not silently accept it, even if the recording is otherwise fully auto-resolved. Flag it in the consolidated prompt (step 4) and hold `accumulated-context.speaker-mappings` as pending for that recording until confirmed. |
| Step 3 finds an off-invite name mentioned but never assigned to a speaker | Note it as informational in the consolidated prompt. Does not block ingestion or require a speaker-mapping answer — it's context, not an error. |

## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/plaud-speaker-id-latest.json
```

Content:
```json
{
  "skill": "plaud-speaker-id",
  "agent": "knox",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from the morning briefing or a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action.

