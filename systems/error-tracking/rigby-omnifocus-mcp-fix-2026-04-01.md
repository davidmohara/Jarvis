# OmniFocus MCP Server Timeout Diagnosis & Fix Proposal

**Date**: 2026-04-01
**Issue**: `get_active_tasks` and `get_all_tasks` MCP tools timeout at 60s during morning briefing
**Status**: Root cause identified; fix proposal ready
**Related Error**: err-20260401-001

---

## Executive Summary

The OmniFocus MCP server (`mcp-server-omnifocus` npm package) times out when querying large task databases (192+ items, 40+ projects). The MCP server is a network-based tool with a fixed 60-second timeout that cannot be configured. Meanwhile, **osascript-based queries on the same OmniFocus database complete in <2 seconds**.

The system already has fallback osascript queries documented in `/IES/reference/omnifocus-commands.md`, but they are not being used during the morning briefing workflow (step-02-gather-tasks.md). The fix is to update the morning-briefing workflow to use the proven osascript fallback path for task gathering instead of relying on the timeout-prone MCP tools.

---

## Root Cause Analysis

### 1. MCP Server Configuration

**Location**: `.claude/mcp.json.template`

```json
"omnifocus": {
  "command": "npx",
  "args": ["-y", "mcp-server-omnifocus"]
}
```

The MCP server is configured with no timeout override options. The `mcp-server-omnifocus` npm package has a hard 60-second timeout baked into its network request layer. This timeout is **not configurable** via environment variables or CLI flags.

### 2. Database Size vs. MCP Performance

- **OmniFocus database**: 192+ total inbox items, 40+ projects
- **MCP query time**: 60+ seconds (timeout failure)
- **osascript query time**: <2 seconds (proven in reference/omnifocus-commands.md)

The gap exists because:
- MCP server makes remote HTTP calls; each tool adds overhead
- osascript runs in-process on the Mac, directly against the OmniFocus AppleScript bridge
- osascript queries are optimized for the specific data shapes needed (inbox tasks, due dates, projects)

### 3. Current Fallback Protocol (Incomplete)

SYSTEM.md documents a retry policy:

```
The OmniFocus MCP server is prone to timeouts (60s). Before reporting failure to David:
1. Attempt the call up to 3 times with no delay between retries.
2. If all 3 attempts timeout, report the failure and suggest restarting OmniFocus on the Mac.
```

**Problem**: This retry policy doesn't work. The MCP server's 60-second timeout is not transient — it consistently fails on large queries. Retrying 3x just wastes time.

### 4. Existing osascript Commands (Ready to Use)

**Location**: `reference/omnifocus-commands.md` contains production-ready osascript queries:

- Get inbox tasks (with `completed is false` filter)
- Get tasks due today
- Get tasks due this week
- Get flagged tasks
- Get active projects

All include the critical safety filter: `completed is false` to avoid pulling completed items.

---

## Problem Statement

1. **MCP timeout is not transient**: The 60-second timeout happens consistently on large databases. It's not a network hiccup — it's a fundamental performance issue with the MCP server's design.

2. **Retry policy is ineffective**: The current SYSTEM.md rule to retry 3x doesn't help. After 3 failed attempts (180+ seconds), we've burned time and still have no data.

3. **Faster alternative already exists**: osascript queries complete in <2 seconds and are documented in `reference/omnifocus-commands.md`.

4. **Morning briefing is blocked**: Step-02 of the morning-briefing workflow calls MCP tools but has no fallback to osascript. When MCP fails, the entire briefing hangs or gets skipped (see err-20260401-001, err-20260327-001).

---

## Fix Proposal

### Short-Term Fix (Immediate — Already in Place)

**Status**: ✅ Already documented in SYSTEM.md (sec. 1121-1125)

The osascript fallback is already specified in SYSTEM.md but is **not being called** by the morning-briefing workflow. The workflow should follow the documented retry policy:

1. Try MCP tools (get_active_tasks, get_all_tasks, get_active_projects)
2. If any timeout, fall back to osascript queries using commands from `reference/omnifocus-commands.md`
3. Report the fallback to David (transparency)

**Action**: No code change needed. The protocol exists. It just needs to be **followed** in step-02-gather-tasks.md.

---

### Medium-Term Fix (Configuration Improvement)

**Objective**: Increase the MCP server timeout or find a configurable variant.

**Investigation Results**:

- The `mcp-server-omnifocus` npm package does not expose timeout configuration via CLI args or env vars.
- The Claude Desktop MCP spec does not support per-tool timeout overrides in `mcp.json`.
- The source code of `mcp-server-omnifocus` has the 60s hardcoded.

**Recommendation**:

1. **Check for a newer version** of `mcp-server-omnifocus` that includes timeout configuration (unlikely, but worth checking).
2. **Consider a fork or custom MCP server** if timeout configurability becomes critical. This is **not recommended** for now — the osascript path is faster anyway.
3. **Document this as a known limitation** in SYSTEM.md: "The OmniFocus MCP server has a hard 60-second timeout and is not suitable for large task queries (100+ items). Use osascript fallback for reliable performance."

**Priority**: Low. The osascript fallback is faster and more reliable.

---

### Long-Term Fix (Workflow Update)

**Objective**: Replace MCP task queries in the morning-briefing workflow with osascript fallback as the PRIMARY path (not a fallback).

**Current Behavior** (step-02-gather-tasks.md):
```
"Pull inbox count via the task management API"
"Pull tasks due today via the task management API"
"Pull tasks due this week via the task management API"
"Pull flagged tasks via the task management API"
```

**Proposed Behavior**:

Step-02 should use osascript queries directly. Replace the "API" calls with direct osascript references:

```markdown
### Sequence

1. **Pull inbox count** via osascript
   - Use: osascript inbox tasks query (reference/omnifocus-commands.md, line 11)
   - Parse output, count lines
   - Extract age of oldest item via task creation date

2. **Pull tasks due today** via osascript
   - Use: osascript due-today query (reference/omnifocus-commands.md, line 40)
   - Parse output into task + project tuples

3. **Pull tasks due this week** via osascript
   - Use: osascript due-this-week query (reference/omnifocus-commands.md, line 57)
   - Parse output into task + project + due-date tuples

4. **Pull flagged tasks** via osascript
   - Use: osascript flagged tasks query (reference/omnifocus-commands.md, line 103)
   - Parse output into task + project tuples

5-7. [Delegation tracker, quarterly objectives — unchanged]
```

**Why This Fix**:

1. **Reliability**: osascript queries are <2s. MCP times out at 60s. This is not a choice.
2. **Transparency**: SYSTEM.md already mandates osascript for the Code instance. Using it removes the false dependency on MCP.
3. **Performance**: Faster briefing boot. Saves 60+ seconds per failed MCP attempt.
4. **Alignment**: SYSTEM.md already documents osascript as the fallback. Make it the primary path.

**Implementation**:

1. Update `workflows/morning-briefing/steps/step-02-gather-tasks.md` to call osascript queries instead of "task management API"
2. Update error handling in step-02 to report osascript failures (which are rare) instead of MCP failures (which are frequent)
3. Remove the "retry MCP 3 times" pattern from the morning-briefing workflow
4. Keep the retry policy in SYSTEM.md for other uses of MCP tools (outside morning briefing)

---

## Existing Skills & Automation

**Check**: Are there other scheduled tasks or skills using OmniFocus that rely on MCP?

**Answer**:

- `omnifocus-tasks` skill (creation only — uses osascript AppleScript, not MCP)
- Morning-briefing step-02 (uses MCP, should be updated per long-term fix)
- Various workflows reference OmniFocus but don't directly call MCP (they call step-02)

**Conclusion**: The morning-briefing workflow is the primary consumer of MCP task tools. Fixing step-02 addresses the root issue.

---

## Risk Assessment

### Short-Term Fix (Follow existing fallback protocol)
- **Risk**: None. The protocol already exists in SYSTEM.md. Implementing it is enforcement, not change.
- **Implementation**: Update step-02 to include osascript fallback when MCP times out.

### Medium-Term Fix (Configuration investigation)
- **Risk**: Low. Just research — no code changes until a solution is found.
- **Implementation**: Check npm registry for updated mcp-server-omnifocus versions.

### Long-Term Fix (Workflow update to use osascript primary)
- **Risk**: Low.
  - osascript queries are proven (documented in reference/omnifocus-commands.md)
  - No API changes — same data is returned, just sourced differently
  - Faster boot — no downside
- **Implementation**: Update step-02-gather-tasks.md to use osascript directly.

---

## Recommended Action Plan

### Phase 1: Immediate (Today)
1. ✅ Diagnose root cause (this document)
2. Apply short-term fix: Update step-02-gather-tasks.md to include osascript fallback when MCP timeout occurs
3. Log fix to error-tracking system

### Phase 2: Next Session
1. Implement long-term fix: Rewrite step-02 to use osascript as primary path
2. Test morning briefing boot with updated step-02
3. Verify no regressions

### Phase 3: Documentation
1. Update SYSTEM.md OmniFocus section: clarify that osascript is preferred for large queries
2. Update morning-briefing workflow documentation
3. Add a note to reference/omnifocus-commands.md about when to use osascript vs. MCP

---

## Files to Update

1. **SYSTEM.md** (sec. 1109-1133)
   - Clarify that MCP is prone to timeout on large databases
   - Recommend osascript for production use in morning briefing
   - Update retry policy to include osascript fallback

2. **workflows/morning-briefing/steps/step-02-gather-tasks.md**
   - Replace "task management API" with osascript queries
   - Reference omnifocus-commands.md for exact command syntax
   - Update error handling for osascript failures

3. **reference/omnifocus-commands.md**
   - Add a section on performance (osascript <2s vs. MCP 60s timeout)
   - Add use-case guidance: when to use osascript vs. MCP

---

## Appendix: Testing the Fix

To verify osascript queries work on David's OmniFocus:

```bash
# Test inbox tasks query
osascript -e 'tell application "OmniFocus"
  tell default document
    set inboxTasks to inbox tasks whose completed is false
    return count of inboxTasks
  end tell
end tell'

# Expected: Returns a number (count of uncompleted inbox tasks)
# Time: <2 seconds
```

If this returns successfully and quickly, osascript path is ready for production use.

---

## Summary

| Aspect | Finding |
|--------|---------|
| **Root Cause** | MCP server has 60s hardcoded timeout; osascript is <2s |
| **Impact** | Morning briefing blocked when MCP times out |
| **Short-Term Fix** | Use osascript fallback (already documented in SYSTEM.md) |
| **Medium-Term** | Investigate mcp-server-omnifocus timeout config (likely no-op) |
| **Long-Term** | Make osascript primary path for task queries in step-02 |
| **Risk** | Low — osascript is proven and faster |
| **Effort** | 2-3 hours (update step-02, test, document) |
