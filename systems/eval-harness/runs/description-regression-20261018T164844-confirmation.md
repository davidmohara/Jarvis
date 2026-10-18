# Description regression — confirmation pass (2026-10-18)

Follow-up to `description-regression-20261018T164844.json`: re-ran all 23
queries flagged (LOST / BROADENED) in the single-repetition full pass,
3 repetitions per variant, same isolated judge root.

## Result

- **confirmed lost triggers: 0**
- **confirmed broadenings: 0**
- noise / partial (judge flakiness): 23/23

Most flagged "losses" were noise in the *original* pass (old fired 0-1/3 on
re-run), i.e. judge triggering is stochastic run-to-run and the full pass's
single old=True was the outlier, not the new description.

## Marginal cases (partial — old fires more than new, but new still fires)

- `.claude/skills/quinn-strategy` — "what should we do about our declining
  enterprise bookings?" — old 3/3, new 1/3. New text retains the quoted
  trigger phrase ("asks 'what should we do about X' in a business context"),
  so this reads as judge variance, not lost surface; watch it in live use.
- `skills/account-targeting` — "who should we go after based on this audience
  profile? give me accounts with sourced fields" — old 2/3, new 1/3.
- `skills/episode-transcript-intake` — "get a clean transcript for this
  Improving Edge episode from Obsidian" — old 2/3, new 1/3.
- `skills/rigby-skill-reflect` — "analyze eval records for galen-morning and
  suggest edits to the skill document" — old 2/3, new 1/3.

## Verdict

The meaning-sensitive rewrite batch **passes**: no trigger phrase needs
restoring. Suggest treating single-repetition LOST/BROADENED flags from the
description-regression driver as review candidates only — always confirm
with a 3-rep pass before editing a description.
