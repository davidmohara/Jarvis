#!/usr/bin/env python3
"""Shared scoring + standings model for the Amazing Race monitor.

Reads:
  data/amazing-race/posts.jsonl        — posts captured by poll_channel.py
  data/amazing-race/flags.json         — vision-fork verdicts (pass/fail/review)
  data/amazing-race/confirmations.json — David's rulings (ok / override / reject)
  skills/amazing-race-monitor/references/quests.json — quest specs

Produces a single state dict used by the live dashboard and the skill's
reporting: standings per team, flag queue with ruling status, bonus candidates.

Scoring rules (base points only, never Dawn's bonuses):
  - fixed quests: quest points once the verdict passes
  - per-item quests (4/8/9/14/15): pts x items_matched, capped by base_item_cap
    (default: full item list length; quest 14 caps at 2)
  - verdict fail/review scores 0 unless a ruling promotes it
  - split posts on a one_post quest: items still counted, flag surfaced
  - duplicate posts by the same team for the same quest: first post counts;
    later posts are flagged, never double-scored
"""

import json
import os
from collections import defaultdict

IES_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DATA_DIR = os.path.join(IES_ROOT, "data", "amazing-race")
QUESTS_PATH = os.path.join(IES_ROOT, "skills", "amazing-race-monitor", "references", "quests.json")
POSTS_PATH = os.path.join(DATA_DIR, "posts.jsonl")
FLAGS_PATH = os.path.join(DATA_DIR, "flags.json")
CONFIRMATIONS_PATH = os.path.join(DATA_DIR, "confirmations.json")


def _load(path, default):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)


def _load_posts():
    posts = []
    if os.path.exists(POSTS_PATH):
        with open(POSTS_PATH) as f:
            for line in f:
                try:
                    posts.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return posts


def effective_points(flag, quest_spec):
    """Points for one post after verdict + any ruling. Ruling beats vision."""
    verdict = flag.get("verdict", "review")
    ruling = flag.get("ruling")
    if ruling == "reject":
        return 0
    if ruling == "override":
        return flag.get("ruled_points", 0)
    if ruling == "ok":
        return flag.get("ruled_points", flag.get("suggested_points", 0))
    if verdict == "pass":
        return flag.get("suggested_points", 0)
    if verdict == "ignore":
        return 0  # station post — host-scored elsewhere, never channel-scored
    return 0  # fail or unresolved review


import apply_ruling  # full_quest_points — what an Approve ruling awards


def _enrich(flags, post_by_id):
    """Join flags with their posts: caption, author, thumbnail, Teams deep link."""
    cfg = _load(os.path.join(DATA_DIR, "config.json"), {})
    team_id, channel_id, tenant_id = cfg.get("team_id"), cfg.get("channel_id"), cfg.get("tenant_id")
    for f in flags:
        p = post_by_id.get(f.get("post_id"))
        if not p:
            continue
        f["author"] = p.get("author")
        f["text"] = (p.get("text") or "")[:140]
        if f.get("team") is None:
            f["assumed_team"] = apply_ruling.lookup_team(f["author"])
        if f.get("quest") is None:
            f["assumed_quest"] = apply_ruling.guess_quest(f["text"])
        f["approve_points"] = apply_ruling.full_quest_points(
            {"quest": f.get("quest") or f.get("assumed_quest"),
             "items_matched": f.get("items_matched")})
        thumb = None
        for a in p.get("attachments", []):
            if a.get("type") == "image" and a.get("path"):
                thumb = a["path"]
                break
            if a.get("type") == "video" and a.get("frames"):
                thumb = a["frames"][0]
                break
        f["thumb"] = thumb
        if team_id and channel_id and tenant_id and p.get("id"):
            f["link"] = ("https://teams.microsoft.com/l/message/%s/%s?groupId=%s&tenantId=%s"
                         % (channel_id, p["id"], team_id, tenant_id))
    return flags


def compute_state():
    quests = _load(QUESTS_PATH, {}).get("quests", {})
    posts = _load_posts()
    flags = _load(FLAGS_PATH, [])
    # confirmations.json is the durable record of rulings; flags.json entries
    # carry the ruling inline once applied — merge defensively
    confirmations = _load(CONFIRMATIONS_PATH, [])
    by_post = {c.get("post_id"): c for c in confirmations if c.get("post_id")}
    for fl in flags:
        pid = fl.get("post_id")
        if pid in by_post and not fl.get("ruling"):
            fl["ruling"] = by_post[pid].get("ruling")
            fl["ruled_points"] = by_post[pid].get("ruled_points")

    post_by_id = {p["id"]: p for p in posts}
    flags = _enrich(flags, post_by_id)  # author/text/assumed team+quest before grouping
    # station-game posts are host-scored, never channel-scored: auto-ignored
    flags = [f for f in flags if f.get("verdict") != "ignore"]
    team_flags = defaultdict(list)  # (team, quest) -> [flags]
    for fl in flags:
        team = fl.get("team") if fl.get("team") is not None else fl.get("assumed_team")
        quest = fl.get("quest") if fl.get("quest") is not None else fl.get("assumed_quest")
        team_flags[(team, quest)].append(fl)

    standings = defaultdict(lambda: {"quests": {}, "total": 0, "pending_flags": 0})

    for (team, quest), flist in team_flags.items():
        if team is None or quest is None:
            continue
        spec = quests.get(str(quest))
        if not spec:
            continue
        # sort by post first_seen so the earliest post counts first;
        # later posts for the same (team, quest) are duplicates and never add points
        flist = sorted(flist, key=lambda f: post_by_id.get(f.get("post_id"), {}).get("first_seen", ""))
        primary = flist[0]
        pts = effective_points(primary, spec)
        standings[team]["quests"][str(quest)] = {
            "points": pts,
            "posts": len(flist),
            "status": "passed" if pts else ("rejected" if primary.get("ruling") == "reject" else "pending"),
        }
        standings[team]["total"] += pts

    pending = [f for f in flags if f.get("verdict") != "pass" or f.get("bonus_candidate")]
    pending_rulings = [f for f in flags
                        if f.get("verdict") in ("fail", "review") and not f.get("ruling")]
    for f in flags:
        if f.get("verdict") in ("fail", "review") and not f.get("ruling") and f.get("team"):
            standings[f["team"]]["pending_flags"] += 1

    bonus_candidates = [f for f in flags if f.get("bonus_candidate")]

    # unidentified posts (no team or quest parse) surface for the controller
    # truly unclassified only: no flag at all (a flagged post — pending or
    # ruled — is covered by its flag card, never here), not roster-resolvable,
    # and not ignored via the dashboard Ignore button
    flagged_ids = {f.get("post_id") for f in flags}
    unidentified = [p for p in posts
                    if not p.get("ignored")
                    and (p.get("team") is None
                         and apply_ruling.lookup_team(p.get("author")) is None
                         or p.get("quest") is None)
                    and p.get("id") not in flagged_ids]

    return {
        "generated_at": __import__("time").strftime("%Y-%m-%dT%H:%M:%S"),
        "standings": {str(t): s for t, s in sorted(standings.items(), key=lambda kv: -kv[1]["total"])},
        "flags": _enrich(flags, post_by_id),
        "pending_rulings": _enrich(pending_rulings, post_by_id),
        "bonus_candidates": _enrich(bonus_candidates, post_by_id),
        "unidentified": _enrich([{"flag_id": "UNK", "post_id": p["id"],
                                  "team": p.get("team") or apply_ruling.lookup_team(p.get("author")),
                                  "quest": p.get("quest"), "verdict": "unidentified"}
                                 for p in unidentified], post_by_id),
        "counts": {
            "posts": len(posts),
            "flags": len(flags),
            "pending_rulings": len(pending_rulings),
            "bonus_candidates": len(bonus_candidates),
        },
    }


if __name__ == "__main__":
    print(json.dumps(compute_state(), indent=2))
