# Content Pipeline — Rigby Review
Date: 2026-05-04

## Verdict: PASS WITH CONDITIONS

The workflow is architecturally sound and well-specified, with clear separation of concerns between discovery and approval. The Ghost integration is correct, Python scripts are robust, and state tracking is viable. However, there are three moderate-to-critical issues that must be resolved before first run: thread tracking is broken, Unsplash image sourcing is underspecified, and the read.py thread filtering has a logic error that will cause missed approvals.

---

## Summary

The `content-pipeline` workflow implements a two-stage automated blog publishing system (discovery + approval) with correct Ghost API integration, solid Slack read/write via custom Python scripts, and a JSON-based state file to coordinate between agents. The architecture avoids using the Slack MCP connector (which would post as David) and correctly uses bot-token-based read/write scripts. However, the thread timestamp plumbing is incomplete — step-01 writes a null `slack_thread_ts` and claims to update it after posting, but provides no instruction for capturing the response timestamp. Step-02 relies on this field to read thread replies. Additionally, Unsplash image sourcing is vague about the actual search/selection process, and read.py's thread filtering condition has a subtle error that will cause it to include the original message and potentially miss approvals.

---

## Findings

### Critical (must fix before first run)

**1. Missing thread_ts capture in step-01**

Step-01, section 9 says:
> "Capture the `ts` (timestamp) of this Slack message. Update `pending-drafts.json` — set `slack_thread_ts` to this value for the entry you just created."

But post.py returns `{"ok": true, "channel": result["channel"], "ts": result["ts"]}`. The step file provides **no instruction** for how to extract this ts from the response and update the JSON. This leaves `slack_thread_ts` as null, which breaks step-02's thread reading entirely.

**Required fix:** Step-01, section 9 must include explicit pseudo-code or example showing how to parse the post.py response JSON and update the pending-drafts.json entry:
```
response = {"ok": true, "ts": "1234567890.123456"}
pending_draft["slack_thread_ts"] = response["ts"]
```

**File:** `/sessions/eager-hopeful-volta/mnt/IES/workflows/content-pipeline/steps/step-01-discover.md` (section 9)

---

**2. read.py thread filtering is incorrect**

read.py, line 65:
```python
top_level = [m for m in messages if not m.get("thread_ts") or m.get("thread_ts") == m.get("ts")]
```

This condition filters for messages where `thread_ts` is absent OR `thread_ts == ts`. This is correct for *channel history* (you want top-level messages only). But in `read_thread()`, line 80:
```python
replies = messages[1:] if len(messages) > 1 else []
```

The function assumes the first message in `conversations.replies` is the original post, and slices it away. This is correct — Slack's `conversations.replies` returns the original message plus all replies.

**However**, the approval loop in step-02 will read those replies and look for from David (line 52):
> "Look for replies from David (user ID: U0ANHV5UXEW) that arrived after the original bot message."

This is contradictory. If step-01's post message carries the bot's own user ID (not David's), and read_thread returns only replies (excluding the original), then the logic is fine. But the step file doesn't clarify whether David is expected to reply to his own post or to the bot's message, and doesn't verify that read.py is correctly excluding the original.

**Risk:** If the Slack bot's own reply is included in the replies list, step-02 could pick up its own notification message and re-trigger approval logic.

**Required fix:** Verify that `conversations.replies` excludes the original message at index 0. The code looks correct (`replies = messages[1:]`), but add a safety check: if the first reply has `user == BOT_USER_ID`, reject it. Or, add a comment to step-02 clarifying this assumption.

**File:** `/sessions/eager-hopeful-volta/mnt/IES/systems/slack-bot/read.py` (line 80) and `/sessions/eager-hopeful-volta/mnt/IES/workflows/content-pipeline/steps/step-02-approve.md` (section 2)

---

**3. Unsplash image sourcing is underspecified**

Step-01, section 6 says:
> "Search Unsplash for a thematic image matching the post's core concept (not the source article's topic literally — the *feeling* or *theme* of David's post)."

This is intentionally vague guidance (good for voice), but it doesn't explain **how Harper actually finds and selects an Unsplash image**. The instruction says "Construct the Unsplash URL" with a template, but it never explains:
- How to search Unsplash (web UI? API? Which API endpoint?)
- How to extract the PHOTO_ID and IXID from a search result
- How to select "the right" image from multiple results
- Fallback if Unsplash search returns nothing

The workflow assumes Harper can independently figure this out. For a human, it's reasonable. For an agent, it's ambiguous.

**Required fix:** Add one of the following:
- **Option A:** "Use web search to find an Unsplash image matching [theme]. Copy the Unsplash photo URL and extract PHOTO_ID from it."
- **Option B:** "Call Unsplash API (unsplash.com/napi/search/photos) with query [theme], select the top result, and construct the URL."
- **Option C:** Provide a concrete example URL and dissect it to show where PHOTO_ID and IXID come from.

Harper is Sonnet, which is smart enough to figure it out, but explicit instructions reduce error risk.

**File:** `/sessions/eager-hopeful-volta/mnt/IES/workflows/content-pipeline/steps/step-01-discover.md` (section 6)

---

### Moderate (fix soon)

**4. Race condition if content-discovery and content-approval overlap**

Both agents read and write `pending-drafts.json`. If content-discovery is running (writing a new draft) and content-approval is running (updating an existing draft) at the same time, there's a risk of file corruption if writes aren't atomic.

Python's `json.dump()` is not atomic. If one agent is writing and another reads mid-write, the file could be corrupted.

**Mitigation options:**
- Add a `.lock` file pattern (read-before-write, write-to-temp-then-rename)
- Or, accept the risk and add a recovery instruction: "If pending-drafts.json is malformed, reset to `[]` and log." (This is already in both step files, so *risk is mitigated but not eliminated*.)

**Recommended fix:** Use write-to-temp-then-rename pattern in both steps. Add a helper function in each step's pseudo-code:
```python
def write_pending_drafts(data):
    with open("pending-drafts.json.tmp", "w") as f:
        json.dump(data, f)
    os.rename("pending-drafts.json.tmp", "pending-drafts.json")
```

**File:** `/sessions/eager-hopeful-volta/mnt/IES/workflows/content-pipeline/steps/step-01-discover.md` (section 8) and `/sessions/eager-hopeful-volta/mnt/IES/workflows/content-pipeline/steps/step-02-approve.md` (section 4a-4c)

---

**5. No deduplication between pending and published drafts**

Step-01, section 3 checks for duplicates against:
- `reference/blog-ideas.md` Published section
- Ghost published posts via `get_posts`

But it does **not** check against **pending-drafts.json** (drafts awaiting approval). If two URLs are dropped in #content simultaneously (before the daily agent runs again), they could both pass dedup checks and create duplicate drafts with different Ghost post IDs.

**Required fix:** Step-01, section 3 should also filter out source URLs already in pending-drafts.json:
```
if source_url in [d["source_url"] for d in pending_drafts]:
    skip with note "This URL is already pending approval..."
```

**File:** `/sessions/eager-hopeful-volta/mnt/IES/workflows/content-pipeline/steps/step-01-discover.md` (section 3)

---

**6. Cleanup policy is vague**

Step-02 says:
> "Periodically (when running): remove entries from pending-drafts.json that are older than 30 days with status "rejected" or "published"."

"Periodically (when running)" is informal. The approval agent runs hourly — should cleanup happen every hour? Every 10th hour? This should be explicit.

**Required fix:** Specify exactly when cleanup runs:
```
Every time content-approval runs, check for and remove entries > 30 days old with status published or rejected. If > 10 entries are removed, log the action.
```

Or move cleanup to a separate scheduled task (weekly or monthly).

**File:** `/sessions/eager-hopeful-volta/mnt/IES/workflows/content-pipeline/steps/step-02-approve.md` (CLEANUP section)

---

### Minor (nice to have)

**7. No handling for URLs that fetch as "blocked" or minimal content**

Step-01, section 2 says:
> "If fetch fails or returns minimal content: Run a web search for the article title or topic to gather context. The model should self-recover — don't halt on a blocked URL."

This is good, but it doesn't define "minimal content" (how many characters? words? A check? ). For consistency, add a threshold:
```
If the fetched content is < 500 characters, run a web search instead.
```

**File:** `/sessions/eager-hopeful-volta/mnt/IES/workflows/content-pipeline/steps/step-01-discover.md` (section 2)

---

**8. Ghost author ID is hardcoded**

Step-01, section 7 and step-02, section 4c both hardcode author ID `68a3465b9e3561027e745c51` for David. This is correct and expected, but there's no note about what happens if this ID is invalid or if David's Ghost author record is deleted. Minor, but worth a comment: "This ID was verified in Ghost as of 2026-05. If it becomes invalid, update workflow.md."

**File:** `/sessions/eager-hopeful-volta/mnt/IES/workflows/content-pipeline/workflow.md` (line 74) and step files

---

**9. No explicit confirmation of channel ID**

workflow.md says:
> "If the channel ID above is wrong or the channel doesn't exist yet, the agent should search for it: Use `slack_search_channels`..."

But no Slack MCP connector is being used — all reads/writes go through post.py and read.py, which only take a channel ID as a string argument. There is no "search for channel" capability in the current design. This note should be removed or updated to clarify the limitation.

**File:** `/sessions/eager-hopeful-volta/mnt/IES/workflows/content-pipeline/workflow.md` (line 35-36)

---

**10. Missing fallback for read.py script location**

Both step files use:
```bash
python3 "$(mdfind -name 'read.py' | grep 'systems/slack-bot/read.py' | head -1)" channel C08UZMA7EGV 24
```

If `mdfind` is slow or the path is wrong, there's no fallback. The SKILL.md for master-slack documents an alternative (find SYSTEM.md), but the step files don't. Minor, but for robustness, add a note: "If mdfind times out, hardcode the path or use the SYSTEM.md fallback from master-slack/SKILL.md."

**File:** `/sessions/eager-hopeful-volta/mnt/IES/workflows/content-pipeline/steps/step-01-discover.md` and `step-02-approve.md`

---

## Specific File Notes

**workflow.md**
- ✅ Ghost conventions are locked and clear
- ✅ Tag list is comprehensive (38 tags, all IDs present)
- ✅ Voice rules are good (short, personal, direct)
- ❌ Channel ID note is misleading (no search capability with current design)
- ❌ Image sourcing doesn't explain *how* to find Unsplash images

**step-01-discover.md**
- ✅ Deduplication logic is sound
- ✅ Failure modes are documented
- ✅ Image upload and Ghost API calls are correct
- ❌ **CRITICAL:** No instruction for capturing thread_ts from post.py response
- ❌ Does not check for duplicates in pending-drafts.json
- ❌ Unsplash image sourcing is vague

**step-02-approve.md**
- ✅ Approval classification is clear
- ✅ Failure modes are documented
- ✅ Regeneration flow is defined
- ❌ **CRITICAL:** Assumes thread_ts is set by step-01, but step-01 doesn't explain how
- ❌ Cleanup policy is informal ("periodically")
- ❌ No validation that step-01 correctly set slack_thread_ts before attempting thread reads

**pending-drafts.json**
- ✅ Currently empty (correct initial state)
- ✅ Schema is well-defined in workflow.md
- ❌ No validation schema or migration notes

**read.py**
- ✅ Token handling is secure (reads from .env, not hardcoded)
- ✅ API calls are correct (`conversations.history` and `conversations.replies`)
- ✅ Top-level filtering is correct for channel reads
- ✅ Thread reply slicing is correct
- ⚠️ **MODERATE:** Thread filtering comment could clarify assumptions for step-02

**post.py**
- ✅ Token handling is secure
- ✅ Message and thread_ts arguments are correct
- ✅ Response JSON format matches what step-01 expects

**master-slack/SKILL.md**
- ✅ Read.py and post.py are documented
- ✅ Channel IDs are listed
- ✅ Usage examples are clear
- ⚠️ Minor: Could reference the specific response fields that scripts return

---

## Recommended Fixes

### Before First Run (CRITICAL)

1. **Step-01, section 9:** Add explicit instruction for parsing post.py response and updating pending-drafts.json with slack_thread_ts:
   ```
   Parse the response JSON. Extract ts from "ts" field.
   Update the pending draft entry: pending_draft["slack_thread_ts"] = response["ts"]
   Write the updated pending-drafts.json.
   ```

2. **Step-01, section 6:** Add explicit Unsplash image sourcing workflow:
   ```
   Use Unsplash API endpoint: /search/photos?query={theme}
   Extract photo ID and ixid from the top result's URLs.
   Construct the feature image URL as shown.
   ```
   Or specify: "Use web search to find a suitable Unsplash image. Copy its URL and extract PHOTO_ID from the path."

3. **Step-01, section 3:** Add pending-drafts.json to dedup check:
   ```
   If source_url in pending_drafts[*].source_url: skip with note
   ```

4. **Step-02, section 2:** Add clarification that thread_ts must be non-null:
   ```
   Only read thread if slack_thread_ts is set (not null).
   If null, skip (draft notification was not posted to Slack).
   ```

### After First Run (MODERATE)

5. **Pending-drafts.json I/O:** Implement atomic writes (write-to-temp, rename) in both steps to prevent corruption on overlapping runs.

6. **Step-02 cleanup:** Clarify exact cleanup timing: "On every run, remove entries > 30 days old."

7. **Fallback for mdfind:** Add note in both steps about SYSTEM.md fallback if mdfind is slow.

### Nice to Have (MINOR)

8. Remove or clarify the channel-search note in workflow.md (no search capability with current design).

9. Add "minimal content threshold" definition in step-01, section 2.

10. Add author ID verification note in workflow.md.

---

## Verdict Summary

**PASS WITH CONDITIONS.** The workflow is sound architecturally. The three critical issues (thread_ts capture, Unsplash sourcing, and read.py clarity) must be resolved before first run. The moderate issues (race conditions, cleanup timing, missing dedup) should be fixed soon after first run to reduce operational risk. Minor issues are polish.

The agents (Harper) are Sonnet — capable enough to infer some of the missing details, but explicit instructions will make execution more reliable and debuggable if something fails.

Once the critical fixes are in place, this is ready for pilot.
