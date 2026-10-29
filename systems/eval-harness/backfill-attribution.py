#!/usr/bin/env python3
"""Correct eval records whose agent attribution came from a bare name mention.

Background (2026-10-29): resolve_spawn_agent_from_prompt used to fall back to
resolve_agent_from_text, which counts ANY whole-word mention of an unambiguous
agent name (knox, rigby, quinn, ...) in a spawn prompt. A boot-token-analysis
agent whose prompt merely said "... and Knox plaud-ingest runs spawned from
boot step-01 ..." was therefore stamped `agent: knox, owning_agent: knox`.

The resolver now requires an attribution-grade signal — a "You are <Agent>"
opener, a leading direct address ("Knox — ..."), exactly one agents/<name>.md
persona file actually read, a single skill-owner path, or a spawn-cue-anchored
mention — and returns None for a bare mention.

This script finds records already stamped by the old heuristic and reverses
the stamp. It is deliberately conservative: a record is only touched when ALL
of the following hold, which proves the stored label came from a mention:

  * the stored `owning_agent` (or canonical `agent`) is a manifest agent
  * strong (attribution-grade) resolution now returns None
  * the OLD mention-count resolver, run on the transcript's first user
    message, returns exactly the stored agent
  * no workflow owner and no persona/skill/opener evidence exists

In that case `owning_agent` is cleared and `agent` is restored to the raw
Claude Code subagent type (`subagent_type`, else "unknown").

Records where strong resolution returns a DIFFERENT agent are reported, never
rewritten: those are pre-existing workflow-owner disagreements outside this
bug class and need a human decision.

Usage:
    python3 backfill-attribution.py --since 2026-10-29            # dry run
    python3 backfill-attribution.py --since 2026-10-29 --apply    # write
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IES_ROOT = HERE.parents[1]
RUNS_DIR = HERE / "runs"

sys.path.insert(0, str(HERE))

from hook_utils import (  # noqa: E402
    _read_first_user_message_text,
    resolve_agent_from_text,
    resolve_spawn_agent_from_prompt,
)
from step_audit import (  # noqa: E402
    normalize_agent_label,
    resolve_record_agent,
    workflow_owner_agent,
)


def stored_owner(record: dict):
    return (normalize_agent_label(record.get("owning_agent"))
            or normalize_agent_label(record.get("agent")))


def strong_owner(record: dict):
    """Attribution-grade owner only (workflow owner / persona read / opener /
    leading address / skill path / spawn cue). Ignores stored labels."""
    return resolve_record_agent(record, trust_stored=False)


def is_mention_artifact(record: dict, stored: str) -> bool:
    """True when the stored label is provably a bare-mention artifact."""
    tpath = record.get("agent_transcript_path")
    text = _read_first_user_message_text(tpath)
    if not text:
        return False
    # An explicit workflow owner would be legitimate evidence, not a mention.
    for wf in (record.get("workflow"), record.get("name")):
        if normalize_agent_label(workflow_owner_agent(wf)):
            return False
    # The prompt itself must not carry an attribution-grade signal.
    if resolve_spawn_agent_from_prompt(text):
        return False
    # And the old mention-count resolver must reproduce the stored label.
    return resolve_agent_from_text(text) == stored


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--since", required=True,
                    help="only records whose started date (YYYY-MM-DD) is >= this")
    ap.add_argument("--apply", action="store_true",
                    help="write corrections (default: dry run)")
    ap.add_argument("--runs-dir", default=str(RUNS_DIR))
    args = ap.parse_args()

    corrected, conflicts = [], []
    for path in sorted(Path(args.runs_dir).glob("eval-*.json")):
        try:
            record = json.loads(path.read_bytes())
        except Exception:
            continue
        if str(record.get("started") or "")[:10] < args.since:
            continue
        stored = stored_owner(record)
        if not stored:
            continue
        strong = strong_owner(record)
        if strong == stored:
            continue
        if strong:
            conflicts.append((path.name, stored, strong,
                              record.get("name"), record.get("workflow")))
            continue
        if not is_mention_artifact(record, stored):
            continue
        raw = normalize_agent_label(record.get("subagent_type"))
        new_agent = record.get("subagent_type") or "unknown"
        if raw:  # subagent_type was itself a manifest agent: keep it
            new_agent = raw
        corrected.append({
            "file": path.name,
            "id": record.get("id"),
            "started": record.get("started"),
            "from_owning_agent": record.get("owning_agent"),
            "from_agent": record.get("agent"),
            "to_agent": new_agent,
        })
        if args.apply:
            record["owning_agent"] = None
            record["agent"] = new_agent
            with open(path, "w") as f:
                json.dump(record, f, indent=2)

    verb = "Corrected" if args.apply else "Would correct"
    print(f"{verb} {len(corrected)} bare-mention attribution(s) since {args.since}:")
    for c in corrected:
        print(f"  {c['id']}  {c['from_owning_agent']}/{c['from_agent']} "
              f"-> {c['to_agent']} (agent), owning_agent=None")
    if conflicts:
        print(f"\nSkipped {len(conflicts)} record(s) whose strong evidence names a "
              f"DIFFERENT agent (not this bug class; review by hand):")
        for name, stored, strong, rec_name, wf in conflicts:
            print(f"  {name}  stored={stored} strong={strong} "
                  f"name={rec_name} workflow={wf}")
    if not args.apply and corrected:
        print("\nDry run. Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
