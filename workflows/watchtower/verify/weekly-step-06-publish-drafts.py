#!/usr/bin/env python3
"""Ground-truth verifier for watchtower/weekly-step-06-publish-drafts.

Publish check. This is the highest-stakes step (it sends drafts to an
external Slack channel). The step claims it either skipped (`step_skipped`)
or sent `drafts_sent`. This verifier re-derives the claim from the real eval
record and the step's own contract rather than trusting the frontmatter
self-report:

  * the destination channel must be the authorized `C0B160MA3EK`;
  * when the step ran (not skipped), a `pre-publish-review` guardrail
    checkpoint entry must exist on a watchtower eval record (the automated
    leakage/attribution/tone review is mandatory before presenting);
  * when the step ran, `drafts_sent` must be a non-empty list; when skipped,
    `drafts_sent` must be empty.

Verdict: retry on a wrong channel, a missing guardrail on a send, or a
sent/skip contradiction; pass otherwise.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

STEP_REL = Path("workflows") / "watchtower" / "steps" / "weekly-step-06-publish-drafts.md"
AUTHORIZED_CHANNEL = "C0B160MA3EK"
CHECKPOINT_NAME = "pre-publish-review"


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
    if yaml is None or not step_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "weekly-step-06-publish-drafts.md not found or YAML parser unavailable",
            "fields": {"publish_verified": False},
            "validation_errors": ["step_file_missing"],
            "retry_instruction": "Confirm workflows/watchtower/steps/weekly-step-06-publish-drafts.md exists.",
        }))
        return

    outputs = extract_frontmatter(step_path.read_text()).get("outputs") or {}
    if not isinstance(outputs, dict) or not outputs:
        print(json.dumps({
            "result": "retry",
            "reason": "weekly-step-06 outputs block is empty - no publish results recorded",
            "fields": {"publish_verified": False},
            "validation_errors": ["no_outputs"],
            "retry_instruction": "Re-execute step-06 and record drafts_sent/drafts_skipped/channel/step_skipped in the step frontmatter outputs.",
        }))
        return

    drafts_sent = outputs.get("drafts_sent") or []
    drafts_sent = drafts_sent if isinstance(drafts_sent, list) else []
    step_skipped = outputs.get("step_skipped")
    channel = outputs.get("channel")

    guardrail_present = False
    runs_dir = ies_root / "systems" / "eval-harness" / "runs"
    if runs_dir.is_dir():
        for f in runs_dir.glob("eval-*.json"):
            try:
                data = json.loads(f.read_text())
            except Exception:
                continue
            if data.get("name") != "watchtower":
                continue
            for g in data.get("guardrails", []) or []:
                if g.get("name") == CHECKPOINT_NAME:
                    guardrail_present = True
                    break
            if guardrail_present:
                break

    fields = {
        "drafts_sent_count": len(drafts_sent),
        "step_skipped": step_skipped,
        "channel": channel,
        "pre_publish_guardrail_present": guardrail_present,
    }

    if channel != AUTHORIZED_CHANNEL:
        print(json.dumps({
            "result": "retry",
            "reason": f"channel is '{channel}', not the authorized {AUTHORIZED_CHANNEL}",
            "fields": fields,
            "validation_errors": ["wrong_channel"],
            "retry_instruction": f"Send only to the authorized #content channel ({AUTHORIZED_CHANNEL}).",
        }))
        return

    if step_skipped is True:
        if drafts_sent:
            print(json.dumps({
                "result": "retry",
                "reason": f"step_skipped is true but {len(drafts_sent)} draft(s) are listed as sent",
                "fields": fields,
                "validation_errors": ["skip_but_sent"],
                "retry_instruction": "Reconcile step_skipped with the drafts_sent list.",
            }))
            return
        print(json.dumps({
            "result": "pass",
            "reason": "step-06 cleanly skipped (David opted out); nothing sent",
            "fields": fields,
            "validation_errors": [],
        }))
        return

    if not drafts_sent:
        print(json.dumps({
            "result": "retry",
            "reason": "step_skipped is false but no drafts are listed as sent",
            "fields": fields,
            "validation_errors": ["no_drafts_sent"],
            "retry_instruction": "Record the drafts actually delivered in drafts_sent, or set step_skipped: true if nothing was sent.",
        }))
        return

    if not guardrail_present:
        print(json.dumps({
            "result": "retry",
            "reason": "drafts were sent but no 'pre-publish-review' guardrail checkpoint is recorded on a watchtower eval record - the mandatory pre-publish review was skipped",
            "fields": fields,
            "validation_errors": ["pre_publish_review_skipped"],
            "retry_instruction": "Run the step-06 guardrail checkpoint (leakage/attribution/tone review) before sending, and record it via guardrail-checkpoint.py.",
        }))
        return

    print(json.dumps({
        "result": "pass",
        "reason": f"step-06 publish verified: {len(drafts_sent)} draft(s) sent to {channel} after a recorded pre-publish review",
        "fields": fields,
        "validation_errors": [],
    }))


if __name__ == "__main__":
    main()
