# Ghost Review — 2026-07-01

## Summary

Reviewed Ghost blog posts against pending-drafts.json to sync scheduled post details.

## Findings

### Updated in pending-drafts.json

**Post: "The Pocket Barrier Is Disappearing"** (ID: 6a42529d1e7721029086b543)
- **Status change**: "pending" → "scheduled"
- **Title correction**: "The Pocket Barrier Is Gone" → "The Pocket Barrier Is Disappearing"
- **Added field**: `scheduled_at: 2026-07-06T14:20:06.000Z`
- **Created_at sync**: Updated to Ghost's actual creation date (2026-06-29T11:10:21.000Z)
- **Ghost status**: Confirmed as "scheduled" for publication on 2026-07-06 at 14:20 UTC

### Posts status verified (no changes needed)

**Post: "The Consulting Middle Is Disappearing. Which Side Are You On?"** (ID: 6a3bbc1d1e7721029086b4c8)
- Ghost status: draft
- Pending-drafts status: pending ✓
- No changes needed

**Post: "Fulfillment Is Not a Benefit. It's a Business Model."** (ID: 6a3bbc211e7721029086b4e0)
- Ghost status: draft
- Pending-drafts status: pending ✓
- No changes needed

### Discrepancy found (not in pending-drafts.json)

**Post: "Dallas Just Topped D.C. Here's What That Actually Means"** (ID: 6a3bbc201e7721029086b4d0)
- Ghost status: **scheduled**
- Scheduled for: 2026-07-02T16:36:49.000Z (upcoming)
- Created at: 2026-06-24T11:14:40.000Z
- **Status**: Not in pending-drafts.json — appears to be a separate post (possibly created outside Harper workflow)

## Action Taken

- Updated pending-drafts.json with correct details for post 3
- Pending approval step should now correctly identify post 3 as "scheduled" and skip it (per cleanup rules in step-02-approve.md)
- Dallas post remains external to this workflow's tracking

## Next Steps

- When Harper next runs approval step, it will clean up the scheduled post (post 3) per step-02-approve.md rules
- The Dallas post is not a Harper-managed draft and should be handled separately if needed
