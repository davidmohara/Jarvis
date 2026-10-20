<!-- system:start -->
# Output Templates (evolution-deployment)

Used by step-07 tasks 7 and 9. Formats are exact.


Present the evolution's changelog from manifest:

```
🎉 Evolution Applied: {evolution_name}

What's New:
{for each changelog entry:}
• {entry}
{end for}
```

If manifest includes `training_prompts`, mention them:

```
New capabilities unlocked! Try these:
{for each prompt:}
• {prompt.agent}: {prompt.prompt}
{end for}
```

### 9. Output Final Summary

**If deployment fully successful:**

```
✅ Evolution deployment complete

Evolution: {evolution_name} ({evolution_version})
Applied: {timestamp}
Files changed: {count}
Personal blocks preserved: {count}
Snapshot: {snapshot_id}
Rollback available: yes

History logged to: evolutions/history.md

{display changelog}
```

**If deployment had warnings/errors:**

```
⚠️  Evolution deployment completed with warnings

Evolution: {evolution_name} ({evolution_version})
Applied: {timestamp}
Files changed: {success_count}/{total_count}
Errors: {error_count}
Personal blocks preserved: {count}
Snapshot: {snapshot_id}

Issues encountered:
{list errors}

Recommendations:
- Review errors above
- Verify system functionality
- Rollback available if needed: rigby rollback {snapshot_id}

History logged to: evolutions/history.md
```
<!-- system:end -->
