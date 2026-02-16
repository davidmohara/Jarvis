# Step 01: Wins and Misses

## MANDATORY EXECUTION RULES

1. You MUST pull this week's daily review files before asking the controller anything. Context first, then conversation.
2. You MUST ask "What were this week's wins?" and wait for a response before proceeding to misses.
3. You MUST ask "What didn't go well?" and wait for a response before proceeding.
4. Do NOT rush this step. The controller needs space to reflect. This sets the tone for the entire review.
5. Do NOT proceed to step 02 until wins, misses, and themes are captured.

---

## EXECUTION PROTOCOL

**Agent:** Master
**Input:** Daily review files from this week, controller's verbal input
**Output:** Wins list, misses list, and themes summary stored in working memory for step 06

---

## CONTEXT BOUNDARIES

- Look back exactly one week: Monday through today (or Friday if running on Saturday/Sunday).
- Pull daily reviews from `reviews/daily/` for each day this week.
- If daily reviews are missing for some days, note which days have no review. This is itself a signal.
- Do not pull calendar or task data here. That comes in later steps. This step is reflective, not operational.

---

## YOUR TASK

### Sequence

1. **Gather daily reviews** for this week.
   - Read all files in `reviews/daily/` matching this week's dates (YYYY-MM-DD format).
   - Extract: accomplishments, incomplete items, blockers, and any patterns across the week.
   - Note which days have reviews and which are missing.

2. **Present a brief week summary** from the daily reviews:
   - "Here's what I see from your daily reviews this week..."
   - List key accomplishments and carryover items.
   - Note any recurring themes (same blocker appearing multiple days, same task deferred repeatedly).
   - Flag missing review days: "No daily review for [day]. Worth noting."

3. **Ask: "What were this week's wins?"**
   - Let the controller respond. Capture everything.
   - Probe if needed: "Anything else? Even small ones count."
   - Cross-reference against daily reviews. If the controller mentions something not in the reviews, note it.

4. **Ask: "What didn't go well this week?"**
   - Let the controller respond. Capture everything.
   - Probe specifically: "Anything you committed to that didn't happen?"
   - Cross-reference against incomplete items from daily reviews.

5. **Synthesize themes:**
   - Group wins and misses into 2-3 themes (e.g., "strong client engagement but internal follow-through lagging").
   - Present themes back to the controller for validation.
   - Store in working memory for use in step 06 (priorities).

---

## SUCCESS METRICS

- All available daily reviews for the week have been read
- Controller has articulated wins and misses
- Themes are identified and validated by the controller
- Missing review days are flagged

## FAILURE MODES

| Failure | Action |
|---------|--------|
| No daily reviews exist for this week | Note it directly: "No daily reviews this week. That's a gap worth closing. Let's work from memory." Proceed with controller input only. |
| Controller gives one-word answers | Probe with specifics from calendar or tasks: "You had that meeting with [person] on Tuesday. How did that go?" |
| Controller wants to skip this step | Push back gently: "This takes 3 minutes and it sets up the whole review. What's one win?" |

---

## NEXT STEP

Read fully and follow: `step-02-rocks-review.md`
