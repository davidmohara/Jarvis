#!/usr/bin/env python3
"""Ground-truth verifier for watchtower/weekly-step-02b-draft-tweets.

Tweet-generation check. The step claims it generated exactly 10 tweets. This
verifier re-derives the claim from the real state file and the step's own hard
constraints rather than trusting the frontmatter self-report:

  * state.yaml accumulated-context.weekly_tweets must contain exactly
    `tweets_generated` entries, and `tweets_generated` must be 10 (the step's
    hard rule) unless the week had zero themes;
  * every tweet's text must satisfy the length rule: <= 280 chars, and
    <= 240 chars when a supporting_url is attached;
  * the `angle_types` counts must sum to `tweets_generated`.

Verdict: retry on any violation; pass otherwise.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

STEP_REL = Path("workflows") / "watchtower" / "steps" / "weekly-step-02b-draft-tweets.md"
STATE_REL = Path("workflows") / "watchtower" / "state.yaml"


def extract_frontmatter(content: str) -> dict:
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    fm_lines = []
    in_fm = False
    for line in lines:
        if line.strip() == "---":
            in_fm = not in_fm
            if not in_fm:
                break
            continue
        if in_fm:
            fm_lines.append(line)
    try:
        return yaml.safe_load("\n".join(fm_lines)) or {}
    except Exception:
        return {}


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    step_path = ies_root / STEP_REL
    state_path = ies_root / STATE_REL
    if yaml is None or not step_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "weekly-step-02b-draft-tweets.md not found or YAML parser unavailable",
            "fields": {"tweets_verified": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/watchtower/steps/weekly-step-02b-draft-tweets.md exists.",
        }))
        return

    outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "weekly-step-02b outputs block is empty - no tweet counts recorded",
            "fields": {"tweets_verified": False},
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-02b and record tweets_generated/tweets_with_links/angle_types in the step frontmatter outputs.",
        }))
        return

    state = {}
    if state_path.is_file():
        try:
            state = yaml.safe_load(state_path.read_text()) or {}
        except Exception:
            state = {}
    ctx = state.get("accumulated-context") or {}
    tweets = ctx.get("weekly_tweets") if isinstance(ctx, dict) else None
    tweets = tweets if isinstance(tweets, list) else []

    tweets_generated = outputs.get("tweets_generated")
    angle_types = outputs.get("angle_types") or {}

    over_limit = []
    for t in tweets:
        if not isinstance(t, dict):
            continue
        text = t.get("text") or ""
        limit = 240 if t.get("supporting_url") else 280
        if len(text) > limit:
            over_limit.append({"text": text[:40], "len": len(text), "limit": limit})

    angle_sum = None
    if isinstance(angle_types, dict):
        try:
            angle_sum = sum(int(v) for v in angle_types.values())
        except Exception:
            angle_sum = None

    fields = {
        "tweets_generated_reported": tweets_generated,
        "weekly_tweets_in_state": len(tweets),
        "over_length_tweets": over_limit,
        "angle_types_sum": angle_sum,
    }

    if not isinstance(tweets_generated, int):
        print(json.dumps({
            "result": "retry",
            "reason": "tweets_generated is missing or not an integer",
            "fields": fields,
            "validation_errors": ["invalid_tweets_generated"],
            "retry_instruction": "Record an integer tweets_generated in step-02b outputs.",
        }))
        return

    if tweets_generated != len(tweets):
        print(json.dumps({
            "result": "retry",
            "reason": f"tweets_generated ({tweets_generated}) != len(weekly_tweets) in state.yaml ({len(tweets)})",
            "fields": fields,
            "validation_errors": ["tweet_count_mismatch"],
            "retry_instruction": "Reconcile tweets_generated with the weekly_tweets array in state.yaml.",
        }))
        return

    if tweets_generated not in (0, 10):
        print(json.dumps({
            "result": "retry",
            "reason": f"tweets_generated is {tweets_generated}; the step requires exactly 10 (or 0 on a zero-theme week)",
            "fields": fields,
            "validation_errors": ["wrong_tweet_count"],
            "retry_instruction": "Generate exactly 10 tweets (or 0 only when weekly_themes is empty).",
        }))
        return

    if over_limit:
        print(json.dumps({
            "result": "retry",
            "reason": f"{len(over_limit)} tweet(s) exceed their character limit: {over_limit[:3]}",
            "fields": fields,
            "validation_errors": ["tweet_over_length"],
            "retry_instruction": "Trim over-length tweets (<=240 chars with a link, <=280 without).",
        }))
        return

    if angle_sum is not None and tweets_generated > 0 and angle_sum != tweets_generated:
        print(json.dumps({
            "result": "retry",
            "reason": f"angle_types sum ({angle_sum}) != tweets_generated ({tweets_generated})",
            "fields": fields,
            "validation_errors": ["angle_types_mismatch"],
            "retry_instruction": "Reconcile the angle_types counts with the number of tweets generated.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-02b tweets verified: {tweets_generated} tweet(s) in state.yaml, all within character limits",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()
