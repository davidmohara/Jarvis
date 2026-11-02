# Briefing Subagent Optimization Plan (boot steps 05-08)

**Author:** Rigby
**Date:** 2026-11-02
**Status:** PLAN ONLY. Nothing under `workflows/`, `skills/`, `agents/`, or `systems/` was modified.

---

## 1. Diagnosis: where the 3.37M actually goes

### 1.1 Method

Parsed the briefing subagent's own transcript (`agent-ae0ad97657bd4e88f.jsonl`), deduplicated by
assistant message id to get 46 real API calls (the 92 assistant records collapse to 46 because
parallel tool calls each write a record with identical usage). Summed usage per call, mapped each
call to a step window, and cross-checked against `eval-20261102T161939-82ACO1.json`. Corroborated
against the 2026-10-30 boot and against the other six boot subagents from the same run.

### 1.2 Headline finding

The 3,369,767 input tokens are **not** spent on synthesis. They are spent re-sending a growing
conversation across 46 API calls:

| Metric | Value |
|---|---:|
| Real API calls (turns) | 46 |
| Input at first call | 31,685 |
| Input at last call | 88,733 |
| Average prompt per call | 73,255 |
| Total input | 3,369,767 |
| Cache-read share of input | 95.3% |
| Total output | 25,679 |
| Duration | 197.7s |

The cost is essentially `turns x average prompt size`. Every boot subagent pays the same
~31.2k to 31.7k baseline on its first call. The briefing subagent is expensive because it takes
46 turns, not because any single read is large.

Today's comparison, same boot, same model:

| Subagent | Turns | Input | Output | Avg prompt |
|---|---:|---:|---:|---:|
| Knox / plaud-ingest | 3 | 97,719 | 834 | 32,573 |
| 03 verify phase 2 | 9 | 354,651 | 2,710 | 39,406 |
| 01.2 data pull | 15 | 1,011,763 | 13,550 | 67,451 |
| 04 meeting context | 17 | 1,035,541 | 17,476 | 60,914 |
| 02 gather data | 20 | 1,115,018 | 19,483 | 55,751 |
| 01.5 calendar | 22 | 1,724,267 | 27,229 | 78,376 |
| **05-08 briefing** | **46** | **3,369,767** | **25,679** | **73,255** |
| Chief nested inside 05 | 3 | 123,931 | 6,038 | 41,310 |

Turn count explains the ranking almost completely. Input per turn is a secondary, roughly flat
multiplier across the whole boot chain.

### 1.3 Where the 46 turns go

| Category (call numbers) | Calls | Input | Output |
|---|---:|---:|---:|
| Orientation reads (1-7) | 7 | 334,300 | 1,838 |
| Chief synthesis spawn (8) | 1 | 55,344 | 4,581 |
| Investigation: verify source, eval records, greps (9-17) | 9 | 579,832 | 4,545 |
| Step-05 close: working memory, stamps, state (18-22) | 5 | 381,404 | 5,575 |
| Step-06 close: frontmatter + state ping-pong (23-31) | 9 | 732,718 | 1,967 |
| Step-07 verify + guardrail + stamps (32-39) | 8 | 675,204 | 2,137 |
| Step-08 knox + close + handback (40-46) | 7 | 610,965 | 5,036 |
| **Total** | **46** | **3,369,767** | **25,679** |

Counted a different way: **13 calls are nothing but a single Edit or Write, and they cost
1,065,962 input (31.6% of the run)**. About 30 of the 46 calls touch `state.yaml`, a step
frontmatter block, or the clock, for 2.34M input (69.5%).

### 1.4 Five root causes, in order of leverage

**1. Bookkeeping is one API call per file operation.** The subagent never batches a state write
with a frontmatter stamp. It greps for a line, reads one line, edits, then edits again. Example
tail from the transcript: `Edit state.yaml` (16:21:43), `grep briefing_delivered` (16:21:44),
`Read state.yaml offset 185 limit 1` (16:21:45), `Edit state.yaml` (16:21:48). Four calls, about
324k input, to write one key. The reason is structural: `accumulated-context` values are long prose
(500 to 900 characters each), and the subagent cannot construct an exact `old_string` without
looking it up. Every lookup is a fresh 80k-token round trip.

**2. The whole 25,603-byte state.yaml is `cat`-ed at turn 1.** Call 1 is
`date -u ... && echo "---STATE---" && cat workflows/boot/state.yaml`. That is ~6.4k tokens injected
before any work and carried through 45 more turns, roughly 288k input on its own. Note the
measurement file confirms accumulated-context is 21,078 bytes / 5,269 tokens at step-05 entry. The
size is not catastrophic; the multiplier is.

**3. Investigative detours.** The subagent read `boot-verify.py` source in four slices (calls 13,
14, 15, 16) to learn what a script it was told to invoke would do. It then ran `boot-verify.py
completion` twice (call 32 and again at call 44, after the gate had already passed). That detour is
about 5 calls and roughly 350k input, and it changes no output.

**4. Clock reads are their own turns.** Four calls (18, 20, 27, 34) are pure
`date -u +%Y-%m-%dT%H:%M:%SZ`, costing 317,239 input combined. Each could ride along with the edit
that consumes it.

**5. 25.2% of the run is invisible to attribution.** Ten calls, 850,518 input, land outside every
step window because `completed-at` is stamped *before* the state writes finish. Step-05's
frontmatter edit happens at 16:21:28 with `completed-at: 16:21:27`, then two more writes follow
outside the window. Steps 05-08 are recorded as 2.52M; the true subagent cost is 3.37M. Any
optimization must also fix this, or the win will be half-invisible in the eval records.

### 1.5 Hypotheses tested and rejected

- **accumulated-context is too big.** It is 21KB / 5,269 tokens. Even reading it in full once is
  cheap. It only matters because it is re-sent 46 times. Slimming it is worth ~200k, not 2M.
- **The nested Chief spawn is the problem.** It is 123,931 input, 3.7% of the chain, and produces
  the actual deliverable. It is the cheapest high-value component in the run. Leave it alone.
- **The model or effort setting.** Identical to every other boot subagent.
- **One pathological file read.** The largest single tool result is the 25.5KB state.yaml (6.4k
  tokens). Nothing else exceeds 4k.

### 1.6 The 2026-10-30 run has the same shape

| Step | 10-30 input | Turns | Today input | Turns |
|---|---:|---:|---:|---:|
| step-05 | 1,211,818 | 21 | 1,196,026 | 20 |
| step-06 | 157,071 | 2 | 481,821 | 6 |
| step-07 | 858,150 | 10 | 415,244 | 5 |
| step-08 | 269,791 | 3 | 426,158 | 5 |
| Gaps | n/a | n/a | 850,518 | 10 |

Same disease, different distribution. On 10-30 the detour landed in step-07; today it landed in
step-06 and step-08. Any fix that only targets one step will not hold.

---

## 2. Options, ranked

### Option A (recommended): slim the single spawn, keep the structure

Change the brief and the four step files so the same one-spawn architecture runs in roughly 20 to
24 turns instead of 36 to 46, and so the writes land inside the attribution windows.

**What changes**
- Turn budget and read restrictions added to the steps 05-08 brief in `workflow.md`.
- A shared WRITE PROTOCOL block inlined into all four step files (one clock read, one state edit,
  one frontmatter edit, batch them into the same turn, stamp last).
- One deterministic command per mechanical step: step-06's index plus consistency check in a single
  call, step-08's Knox record lookup in a single call.
- Explicit "do not read the verifier source" and "do not re-run a passing gate" rules.
- `morning-briefing/state.yaml` becomes a targeted Edit instead of a full 2,725-token Write.

**Estimated savings**

| Scenario | Turns | Peak prompt | Input | Cut | Cost | Duration |
|---|---:|---:|---:|---:|---:|---:|
| Today | 46 | 88.7k | 3.37M | n/a | $0.175 | 198s |
| Conservative | 28 | 60k | ~1.55M | 54% | ~$0.085 | ~130s |
| Base case | 22 | 55k | ~1.10M | 67% | ~$0.062 | ~100s |
| Stretch | 18 | 50k | ~0.85M | 75% | ~$0.050 | ~85s |

**Risk: low to medium.** No structural change, no new spawn, no schema change. The main risk is
that a turn budget causes the subagent to skip the guardrail or truncate the briefing. Mitigate by
scoping the budget to reads and bookkeeping, and by leaving the verbatim handback requirement and
step-07 content judgment untouched.

**Constraints touched:** the step-file write instructions, the workflow brief. Not touched: the
Edit-only rule, the real-clock rule, the punch-out protocol, the no-step-walking rule, the verbatim
final message.

### Option B: split into two spawns (05-06 and 07-08)

Spawn A produces the briefing and the scan, ends with the briefing verbatim. Spawn B starts fresh at
the 31.7k baseline, reads steps 07 and 08, runs the gate, and closes.

**Estimated savings:** Spawn A 14 to 16 turns at ~44k average is ~0.65M. Spawn B 8 to 10 turns at
~38k average is ~0.35M. Total ~1.0M, a 70% cut. Marginally better than Option A's base case.

**Why it is not first**
- It touches the "steps 05 through 08, exactly one briefing subagent" structural rule and changes
  the shape of Master's relay from one message to two.
- The briefing has to cross the spawn boundary. Spawn B needs it for step-07's content judgment, so
  it would read the working-memory file Spawn A wrote. That is workable but adds a dependency.
- It doubles the fixed baseline and adds a second handback.
- It does not fix the bookkeeping ping-pong, it only bounds it per spawn. If both spawns still
  ping-pong, the win shrinks.

**Verdict:** the right fallback if Option A cannot hold the turn budget, not the first move.

### Option C: script the close (steps 07-08 as one deterministic script)

Rejected. `step-complete.py` is invoked from `post-tool-use.py` on the `Edit|Write` matcher
(`.claude/settings.json`). A Python script that writes the step frontmatter through Bash never
fires that hook, so the step record is never created and per-step attribution silently vanishes.
That is the exact failure mode of the 2026-10-22 executor (42 Bash calls, zero per-step records).
This option only becomes viable if the harness gains a Bash-aware step-completion trigger, which is
a bigger change than the problem it solves.

### Option D (outside this pass): a restricted briefing agent definition

Almost 20k of the 31.7k per-turn baseline is harness scaffolding: a 30k-character skill listing,
a 396-name deferred-tool list, MCP instruction blocks, and tool schemas the briefing subagent never
uses. A dedicated `agents/briefing.md` with a narrow tool allowlist could plausibly cut the baseline
to 18k to 22k. At 22 turns that is another 220k to 300k. Worth investigating after Option A, but it
adds an agent definition in a gated directory and it is not yet verified that the harness lets an
agent type suppress the skill listing.

---

## 3. Recommended option: implementation sketch

### 3.1 `workflows/boot/workflow.md`, steps 05-08 brief

Keep verbatim: the literal `` `workflows/boot/workflow.md` `` string (eval attribution) and the
"do not read or execute any other step file" line (the 57-turn / 6.27M defense). Add:

```
TURN BUDGET: target 22 assistant turns or fewer for all four steps. The 10-30 and 11-02 runs took
36 and 46. Turns are the cost: every turn re-sends the whole conversation, so one extra turn at this
point in boot costs about 80,000 tokens. Batch independent tool calls into one turn. Do not spend a
turn on anything you can fold into another turn.

READ RESTRICTIONS:
- Read the four step files in ONE turn, not four.
- Read `workflows/boot/state.yaml` ONCE, targeted at the `accumulated-context:` block. Never
  `cat` the whole file. Do not grep before an edit; the step file names the anchor.
- Do NOT read `workflows/boot/verify/boot-verify.py` source. Invoke it. It is the authority.
- Do NOT read `systems/eval-harness/**` or any `.jsonl`.
- Do NOT re-run a gate that already exited 0.

WRITE ORDER: do the step's work, write the state key, then stamp the step frontmatter LAST as the
final action of the step. `completed-at` is the clock reading taken immediately before the writes.
Stamping before the state writes is why 25% of the 11-02 run fell outside every attribution window.
```

### 3.2 Shared WRITE PROTOCOL block, inlined in each of steps 05-08

Inlined rather than a new reference file, because a new file costs a read turn.

```
## WRITE PROTOCOL (this block is the entire bookkeeping cost for this step)

1. One clock read: `date -u +%Y-%m-%dT%H:%M:%SZ`. Reuse that exact value for both writes below.
2. One Edit to `workflows/boot/state.yaml`, anchored on the line named in this step. No grep, no
   re-read. If the named anchor is absent, read only the `accumulated-context:` block once, then
   edit.
3. One Edit to this step file's frontmatter. Do it last, in the same turn as the state edit.
4. Issue 1 and 2 as parallel tool calls in one turn.
5. Never `cat` state.yaml. Never Write state.yaml.
```

### 3.3 Per-step changes

**step-05-synthesize-briefing.md**
- Keep the Chief spawn exactly as is.
- Replace the state-write instruction with the WRITE PROTOCOL block.
- `briefing_delivered` value becomes one line, 200 characters max, with a fixed prefix so the
  anchor is predictable: `briefing_delivered: "yes: 3 paragraphs + N-row calendar + M reminders; WM: <path>"`.
- `workflows/morning-briefing/state.yaml`: targeted Edit on `current-step:` and `completed:`,
  never a full-file Write (today that Write alone was 2,725 output tokens).
- Fold the `data/reminders.json` inspection into the same turn that builds the Chief digest.

**step-06-scan-workflows.md**
- Keep rule 1 (read `_active.yaml` first).
- Replace the open-ended consistency sweep with one command that returns both the index and the
  ground truth:

```
python3 -I -c "
import glob,re
print('--- _active.yaml ---')
print(open('workflows/_active.yaml').read())
print('--- in-progress on disk ---')
for p in glob.glob('workflows/*/state.yaml'):
    t=open(p).read()
    if re.search(r'^status:\s*in-progress',t,re.M): print(p)
"
```

- Cap the response: if the two agree, one line. If they disagree, surface it and move on.
- `workflows_scanned` value: one line, 200 characters max.

**step-07-verify-completion.md**
- Add: "Do not read `boot-verify.py` source. Invoke it once."
- Add: "If it exits 0, do not run it again at the end of boot."
- One `guardrail-checkpoint.py` call.
- One Edit to `state.yaml` carrying `status: complete`, `current-step: null`, `completed-at`, and
  `state_status` in a single edit rather than three.
- `state_status` value: one line, 200 characters max.

**step-08-knox-completion-check.md**
- Replace the free-form search with one command that prints the newest plaud-ingest record's
  fields, for example a small Python one-liner over `systems/eval-harness/runs/*.json` filtered by
  `workflow == "plaud-ingest"` and a `started` date of today, printing name, status, started,
  completed, duration.
- One Edit to `state.yaml` for `knox_status` / `knox_reason` / `knox_eval_id` /
  `knox_duration_seconds`. `knox_reason` capped at 200 characters.
- One Edit to the step frontmatter. Stamp last.

### 3.4 What the eval harness needs

Nothing structural. `step-complete.py` derives each step's tokens from the step frontmatter window
and fires on the `Edit|Write` that writes `status: complete`. As long as each step keeps one
frontmatter Edit, per-step attribution survives and actually improves, because the stamp-last order
pulls the bookkeeping inside the window.

Optional, and outside this edit pass: have `eval-agent-stop.py` record `turns_total` and
`peak_prompt_tokens` on the subagent record. Both are already computable from the transcript it
reads. That makes the win directly measurable per boot instead of requiring a manual parse.

### 3.5 Phase 2 (separate, only if Phase 1 lands)

Cap `accumulated-context` values at one line / 200 characters as a convention. Today the block is
21,078 bytes because values are 500 to 900 character prose paragraphs. Slimming it to structured
one-liners cuts state.yaml to roughly 8KB, which saves about 4k tokens per turn for *every*
subagent that reads it, not just the briefing one. Medium risk because steps 01 through 04 write
those values, so it is a convention change across the boot chain. Do not bundle it with Phase 1.

---

## 4. How to verify the win

Compare the next three boots against today's baseline. The numbers to pull, from the briefing
subagent record and its transcript:

| Metric | Today | Target | Hard fail |
|---|---:|---:|---:|
| `total_tokens_input` | 3,369,767 | < 1.3M | > 2.1M |
| Assistant turns | 46 | <= 24 | > 32 |
| Peak prompt size | 88,733 | <= 58k | > 70k |
| `duration_seconds` | 197.7 | <= 110 | > 150 |
| Attributed share of calls | 74.8% | >= 90% | < 80% |
| Briefing integrity | pass | pass | any regression |

Briefing integrity check, unchanged from today's standard: three narrative paragraphs before the
calendar table, calendar table present with 1-line context, reminders rendered or omitted per the
rule, ends with exactly "What do you want to tackle first?", working memory written at
`memory/working/morning-briefing-YYYY-MM-DD-HHmmss.md`, and the subagent's final message contains
the full briefing verbatim.

Regression trigger: if any of the next three boots exceeds 32 turns or 2.1M input, the brief is not
binding and Option B becomes the next move.

One caution on the dollar figure. At $0.05/M input, 2.27M saved tokens is about $0.11 per boot, or
roughly $40 a year at one boot a day. The real wins here are wall clock (about 100 seconds per
boot), context headroom on a 1M window, and per-step attribution that reflects reality. Do not sell
this as a cost program.

---

## 5. What NOT to touch, and why

1. **The nested Chief spawn.** 123,931 input, 3.7% of the chain, and it produces the deliverable.
   Inlining the synthesis into the briefing subagent would run a 3-paragraph persona task inside an
   80k-token bookkeeping context and would lose the persona isolation. This is the best-value
   component in the run.
2. **The Edit/Write-only write rule.** `step-complete.py` is a PostToolUse hook on `Edit|Write`. A
   Bash-written frontmatter silently drops the step record. This is the 2026-10-22 failure.
3. **The real-clock stamp rule and the timestamp-integrity gate.** `boot-verify.py completion`
   treats a stamp ahead of the file write as a hard error. Keep it. The fix is write order, not
   relaxed stamps.
4. **The guardrail punch-out and `SendMessage` resume protocol.** It is what makes an escalated
   boot recoverable without losing `current-step` or `accumulated-context`.
5. **The literal `workflows/boot/workflow.md` string in the spawn prompt.** Without it
   `eval-agent-start.py` tags the spawn `general-purpose` and drops per-step attribution.
6. **The "do not read or execute any other step file" line.** That line is the standing defense
   against the 57-turn / 6.27M walk.
7. **The verbatim-final-message requirement.** Master relays it unmodified. It is the primary
   output of boot.
8. **The semantics of either `boot-verify.py` gate.** Remove the duplicate invocation, not the
   gate. The freshness, leakage, and briefing-currency checks are the point of step-07.
9. **The `state.yaml` schema in Phase 1.** Do the value-shape change as a separate pass, after the
   turn-count win is proven.
10. **Steps 01 through 04.** They are not the outlier and they just stabilized. This plan is scoped
    to 05-08.

---

## 6. Adjacent finding worth a separate fix

`.claude/hooks/post-tool-use.py` line 175 raises
`AttributeError: 'str' object has no attribute 'get'` in `update_session_index` whenever a
`current_topic` is set, because the `topics` list can contain a plain string. The hook is
configured non-blocking, so it does not stop the tool call, but it does two harmful things:

- It aborts the session-index update, so `memory/sessions/index.json` files/loops tracking is not
  being maintained on Write/Edit.
- It injects a ~700-character traceback into every subagent transcript that writes a file. Today
  that fired 13 times in the briefing subagent (2,236 tokens, re-sent for the rest of the run) and
  3 to 6 times in every other boot subagent.

Fix is a one-line guard (`if isinstance(t, dict) and (...)`), or normalizing `topics` before the
loop. Out of scope for this plan because it lives in `.claude/hooks/`, but it should be fixed before
the next token comparison so the measurement is clean.

---

## 7. Risks and open questions

1. **Turn budget versus completeness.** A hard number could tempt the subagent to skip the step-07
   content judgment or shorten the briefing. Mitigation: state that the budget applies to reads and
   bookkeeping only, and keep the briefing integrity checks in step-07 and the handback rule.
2. **Anchor predictability.** The WRITE PROTOCOL block assumes the named anchor exists. The bounded
   fallback (read only the `accumulated-context:` block once, then edit) keeps that to one extra
   call in the worst case.
3. **Parallel writes in one turn.** Issuing the state Edit and the frontmatter Edit in the same turn
   means the frontmatter write may be processed second. That is fine, because the clock value was
   read before either, but it should be checked on the first run.
4. **Open question: can an agent type suppress the skill listing?** If yes, Option D is a larger
   win than Option A's tail. Needs a harness answer, not a workflow change.
5. **Open question: should the briefing subagent read `workflow.md` at all?** Today it reads the
   full 16KB file (about 4k tokens, carried 45 turns). The brief plus the four step files may be
   sufficient. Worth testing in the first run after Option A lands, not worth changing blind.
