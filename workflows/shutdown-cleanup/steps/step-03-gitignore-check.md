---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 03: Gitignore Check

## MANDATORY EXECUTION RULES

1. You MUST read the current `.gitignore` before proposing changes.
2. You MUST NOT remove existing gitignore entries.
3. Only add patterns if a new temp artifact type was discovered during the session that isn't already covered.

---

## EXECUTION PROTOCOL

**Agent:** Master
**Mode:** Automated — no controller interaction needed
**Input:** Current `.gitignore`, purge results from step 01
**Output:** Updated `.gitignore` (if needed), list of patterns added

---

## YOUR TASK

### Sequence

1. **Read `.gitignore`** from the project root

2. **Cross-reference** against the known temp patterns from step 01:

   | Pattern | Should Be Gitignored |
   |---------|---------------------|
   | `.DS_Store` | Yes |
   | `.fuse_hidden*` | Yes |
   | `__pycache__/` | Yes |
   | `*.tmp` | Yes |
   | `meetings/**/*.html` | Yes |
   | `*.pyc` | Yes |

3. **Check step 01 results** — were any new artifact types discovered that aren't in the list above? If so, add their pattern.

4. **If changes needed**, update `.gitignore`:
   - Add missing patterns
   - Group by category with comments
   - Do not reorder or modify existing entries

5. **Store results** in working memory:
   ```
   gitignore_results:
     patterns_added:
       - pattern: ...
         reason: ...
     already_covered: N
     no_changes_needed: true/false
   ```

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `.gitignore` doesn't exist | Create one with the standard patterns |
| Pattern already exists but in different format | Leave existing. Do not duplicate. |

---

## NEXT STEP

Read fully and follow: `step-04-commit.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
