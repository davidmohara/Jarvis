#!/usr/bin/env python3
"""Apply David's ruling to a flag from the Amazing Race monitor.

Usage:
  apply_ruling.py FLAG_ID ok                  # accept the vision verdict/suggested points
  apply_ruling.py FLAG_ID override POINTS     # accept the post but set points manually
  apply_ruling.py FLAG_ID reject              # reject the post, no points
  apply_ruling.py --list                      # list flags needing a ruling

Writes the ruling into data/amazing-race/flags.json (inline) and appends the
durable record to data/amazing-race/confirmations.json. The live dashboard
picks it up on its next auto-refresh.
"""

import json
import os
import sys
import time

IES_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DATA_DIR = os.path.join(IES_ROOT, "data", "amazing-race")
FLAGS_PATH = os.path.join(DATA_DIR, "flags.json")
CONFIRMATIONS_PATH = os.path.join(DATA_DIR, "confirmations.json")
QUESTS_PATH = os.path.join(IES_ROOT, "skills", "amazing-race-monitor", "references", "quests.json")
ROSTER_PATH = os.path.join(DATA_DIR, "roster.json")


def _norm_tokens(name):
    import re as _re
    import unicodedata as _u
    t = _u.normalize("NFKD", name or "").encode("ascii", "ignore").decode("ascii")
    return set(_re.sub(r"[^a-z0-9 ]+", " ", t.lower()).split())


def lookup_team(author):
    """Correlate a post author to their Racing Team via the roster.

    Exact name, then diacritic-normalized, then token-subset (Teams display
    names often carry extra middle/last tokens: 'Jessica Gonzalez Cueva' ->
    roster 'Jessica Gonzalez'). Subset match must be unique and share >= 2
    tokens. Returns team int or None.
    """
    if not author or not os.path.exists(ROSTER_PATH):
        return None
    roster = load(ROSTER_PATH, {})
    by_name, by_norm = roster.get("by_name", {}), roster.get("by_norm", {})
    if author in by_name:
        return by_name[author]
    import re as _re
    import unicodedata as _u
    key = _re.sub(r"\s+", " ", _re.sub(r"[^a-z0-9 ]+", " ", _u.normalize(
        "NFKD", author).encode("ascii", "ignore").decode("ascii").lower())).strip()
    if key in by_norm:
        return by_norm[key]
    tokens = _norm_tokens(author)
    if len(tokens) < 2:
        return None
    candidates = {t for n, t in by_name.items() if len(_norm_tokens(n) & tokens) >= 2
                  and _norm_tokens(n) <= tokens}
    return candidates.pop() if len(candidates) == 1 else None


def ignore_post(post_id):
    """Mark a post as ignored (dashboard Ignore button) — drops it from the
    unidentified queue; chatter and non-race posts never need classification."""
    posts_path = os.path.join(DATA_DIR, "posts.jsonl")
    if not os.path.exists(posts_path):
        return {"ok": False, "error": "posts.jsonl missing"}
    out, found = [], False
    for line in open(posts_path).read().splitlines():
        try:
            p = json.loads(line)
        except json.JSONDecodeError:
            out.append(line)
            continue
        if p.get("id") == post_id:
            p["ignored"] = True
            found = True
        out.append(json.dumps(p))
    if not found:
        return {"ok": False, "error": "post %s not found" % post_id}
    tmp = posts_path + ".tmp"
    with open(tmp, "w") as f:
        f.write("\n".join(out) + "\n")
    os.replace(tmp, posts_path)
    return {"ok": True, "post_id": post_id, "ignored": True}


# Keyword → quest inference from the post's own words (quest titles/vocab from
# references/quests.json — David's rule: never offer Approve at 0; assume the
# challenge from the caption when the quest number is missing)
QUEST_KEYWORDS = [
    (1, ["creative", "group photo", "story", "sequence"]),
    (3, ["performer", "acting it out", "routine"]),
    (4, ["golden nugget", "hand of faith", "go for the gold"]),
    (5, ["slomo", "slow motion", "runway", "synchronized walk"]),
    (6, ["food", "eat", "critic", "shrimp", "fried"]),
    (7, ["landmark", "reenact"]),
    (8, ["binion", "horseshoe", "million", "wsop"]),
    (9, ["vintage vegas", "vegas vickie", "mega bar", "first telephone", "oldest casino"]),
    (10, ["slot machine", "human slot", "reel"]),
    (11, ["high five", "highfive"]),
    (12, ["confession", "craziest", "meeting"]),
    (13, ["zip", "zipline", "zip bomber", "slotzilla"]),
    (14, ["zoltar"]),
    (15, ["alphabet", "neon letters"]),
    (16, ["elvis"]),
]


def guess_quest(text):
    """Infer the quest number from the post caption's own words, else None."""
    t = (text or "").lower()
    for quest, words in QUEST_KEYWORDS:
        if any(w in t for w in words):
            return quest
    return None


def full_quest_points(flag):
    """Full value of the post's quest: approve = the post counts fully.

    fixed quest -> its points; per-item quest -> points x (items matched, or the
    full item list when the reviewer could not confirm items), capped at
    base_item_cap. Returns suggested_points when the quest is unknown.
    """
    if not os.path.exists(QUESTS_PATH):
        return flag.get("suggested_points", 0)
    with open(QUESTS_PATH) as f:
        quests = json.load(f).get("quests", {})
    spec = quests.get(str(flag.get("quest")))
    if not spec:
        return flag.get("suggested_points", 0)
    if spec.get("points_model") == "per_item":
        n = len(flag.get("items_matched") or []) or len(spec.get("items") or [])
        cap = spec.get("base_item_cap", len(spec.get("items") or []))
        return spec.get("points", 0) * min(n, cap)
    return spec.get("points", 0)


def load(path, default):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)


def save(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def apply(flag_id, action, points=None):
    """Apply a ruling programmatically (used by the dashboard server). Returns dict."""
    flags = load(FLAGS_PATH, [])
    target = next((f for f in flags if f.get("flag_id") == flag_id), None)
    if not target:
        return {"ok": False, "error": "flag %s not found" % flag_id}
    action = action.lower()
    if action not in ("ok", "override", "reject"):
        return {"ok": False, "error": "action must be ok | override | reject"}
    target["ruling"] = action
    if action == "ok":
        # approve = the post counts fully, regardless of the vision verdict's
        # suggested 0 on review/fail verdicts (David's ruling beats the reviewer).
        # Quest number missing → assume the challenge from the post's own words.
        if target.get("quest") is None and points is None:
            post_text = ""
            posts_path = os.path.join(DATA_DIR, "posts.jsonl")
            if os.path.exists(posts_path):
                with open(posts_path) as f:
                    for line in f:
                        try:
                            p = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if p.get("id") == target.get("post_id"):
                            post_text = p.get("text") or ""
                            break
            assumed = guess_quest(post_text)
            if assumed:
                target["assumed_quest"] = assumed
                target["ruled_points"] = full_quest_points(
                    {"quest": assumed, "items_matched": []})
        if "ruled_points" not in target:
            target["ruled_points"] = int(points) if points is not None else full_quest_points(target)
    elif points is not None:
        target["ruled_points"] = int(points)
    target["ruled_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save(FLAGS_PATH, flags)
    confirmations = load(CONFIRMATIONS_PATH, [])
    confirmations.append({
        "flag_id": flag_id,
        "post_id": target.get("post_id"),
        "team": target.get("team"),
        "quest": target.get("quest"),
        "ruling": action,
        "points": target.get("ruled_points") if action != "reject" else 0,
        "ruled_at": target["ruled_at"],
    })
    save(CONFIRMATIONS_PATH, confirmations)
    return {"ok": True, "flag_id": flag_id, "ruling": action, "points": points}


def classify(post_id, team, quest):
    """Classify an unidentified post (dashboard): set team/quest, approve at full points."""
    import time as _t
    if not post_id:
        return {"ok": False, "error": "post_id required"}
    try:
        team = int(team)
        quest = int(quest)
    except (TypeError, ValueError):
        return {"ok": False, "error": "team and quest must be integers"}
    posts_path = os.path.join(DATA_DIR, "posts.jsonl")
    if not os.path.exists(posts_path):
        return {"ok": False, "error": "posts.jsonl missing"}
    with open(posts_path) as f:
        lines = f.read().splitlines()
    out, found = [], False
    for line in lines:
        try:
            p = json.loads(line)
        except json.JSONDecodeError:
            out.append(line)
            continue
        if p.get("id") == post_id:
            p["team"], p["quest"], found = team, quest, True
        out.append(json.dumps(p))
    if not found:
        return {"ok": False, "error": "post %s not found" % post_id}
    tmp = posts_path + ".tmp"
    with open(tmp, "w") as f:
        f.write("\n".join(out) + "\n")
    os.replace(tmp, posts_path)

    full = full_quest_points({"quest": quest, "items_matched": []})
    flags = load(FLAGS_PATH, [])
    target = next((f for f in flags if f.get("post_id") == post_id), None)
    if target:
        target["team"], target["quest"] = team, quest
        target["ruling"] = "ok"
        target["ruled_points"] = full
        target["ruled_at"] = _t.strftime("%Y-%m-%dT%H:%M:%S")
        target.setdefault("reasons", []).append("classified by David from dashboard")
        flag_id = target.get("flag_id")
    else:
        flag_id = "T%d-Q%d-1" % (team, quest)
        base, n = flag_id, 2
        while any(f.get("flag_id") == flag_id for f in flags):
            flag_id = "%s-%d" % (base, n)
            n += 1
        flags.append({"flag_id": flag_id, "post_id": post_id, "team": team, "quest": quest,
                      "verdict": "pass", "reasons": ["classified by David from dashboard"],
                      "items_matched": [], "suggested_points": full, "bonus_candidate": False,
                      "ruling": "ok", "ruled_points": full,
                      "ruled_at": _t.strftime("%Y-%m-%dT%H:%M:%S")})
    save(FLAGS_PATH, flags)
    confirmations = load(CONFIRMATIONS_PATH, [])
    confirmations.append({"flag_id": flag_id, "post_id": post_id, "team": team, "quest": quest,
                          "ruling": "ok", "points": full,
                          "ruled_at": _t.strftime("%Y-%m-%dT%H:%M:%S")})
    save(CONFIRMATIONS_PATH, confirmations)
    return {"ok": True, "flag_id": flag_id, "post_id": post_id, "team": team,
            "quest": quest, "points": full}


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)

    flags = load(FLAGS_PATH, [])
    if args[0] == "--list":
        pending = [f for f in flags if not f.get("ruled_at")]
        for f in pending:
            print("%s\tT%s Q%s\t%s\t%s" % (f.get("flag_id"), f.get("team"), f.get("quest"),
                                          f.get("verdict"), "; ".join(f.get("reasons", []))[:80]))
        print("(%d flag(s) awaiting ruling)" % len(pending))
        return

    if len(args) < 2:
        print(__doc__)
        sys.exit(2)
    flag_id, action = args[0], args[1].lower()
    if action not in ("ok", "override", "reject"):
        print("action must be ok | override POINTS | reject", file=sys.stderr)
        sys.exit(2)
    points = None
    if action == "override":
        if len(args) < 3 or not args[2].isdigit():
            print("override requires POINTS", file=sys.stderr)
            sys.exit(2)
        points = int(args[2])

    result = apply(flag_id, action, points)
    if not result.get("ok"):
        print(result.get("error"), file=sys.stderr)
        sys.exit(1)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
