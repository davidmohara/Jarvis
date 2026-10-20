<!-- system:start -->
# Evolution History Entry Template (evolution-deployment)

Used by step-07 task 5 when appending to `evolutions/history.md`. The format is exact.

## {evolution_name} ({evolution_version}) — Applied {date}

**Evolution ID:** {evolution_id}
**Applied:** {ISO timestamp}
**Snapshot:** {snapshot_id}
**Applied by:** {user or system}

### Files Changed

{for each file in file_list:}
- `{file.path}` — {action}{if merged: " ({personal_blocks_count} personal blocks preserved)"}
{end for}

### Conflicts

{if conflicts encountered:}
{list each conflict and resolution}
{else:}
None.
{end if}

### Personal Blocks Preserved

{if personal blocks:}
{for each file with personal blocks:}
- `{file.path}`: {list sections where blocks preserved}
{end for}
{else:}
No personal blocks in target files.
{end if}

### Status

{if no errors:}
✓ Deployment successful
{else:}
⚠️  Deployment completed with warnings (see errors below)
{list errors}
{end if}

### Eval Comparison (if benchmark snapshot exists)

{if eval_comparison was performed:}
**Trend:** {trend} (success rate: {success_rate_delta}, composite score: {avg_composite_score_delta})
**Baseline:** {baseline_metrics}
**Post-deployment:** {post_deployment_metrics}
{else:}
Eval comparison skipped (no baseline available)
{end if}

---

```
<!-- system:end -->
