#!/usr/bin/env python3
"""Attribute Fireworks (and Anthropic) token spend to sessions, workflows, and skills.

Source of truth: local Claude Code session transcripts at
~/.claude/projects/*/*.jsonl. Every assistant message records the actual model
used (glm-5p3, kimi-k3, deepseek-flash, ...) plus full token usage including
cache reads. We price each request at the configured Fireworks serverless rates
and roll up by session, day, model, and detected skill/workflow invocations.

Rates are estimates for attribution; reconcile totals against Fireworks
billing export (see reconcile.py).

Usage:
    python3 attribute.py [--since 2026-10-01] [--until 2026-10-21]
                         [--by session|day|model|skill] [--csv out.csv]
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude" / "projects"

# Fireworks serverless rates, $ per Mtok (input, output). From settings.json model descriptions.
RATES = {
    "kimi-k3": (3.0, 15.0),
    "glm-5p3": (1.4, 4.4),
    "glm-flash": (0.15, 0.5),
    "deepseek-flash": (0.3, 1.2),
    "deepseek-v4p1-flash": (0.3, 1.2),
    "deepseek-v4.1-flash": (0.3, 1.2),
    # Anthropic fallbacks (only seen if traffic bypassed the Fireworks router)
    "claude-sonnet": (3.0, 15.0),
    "claude-opus": (15.0, 75.0),
    "claude-haiku": (0.8, 4.0),
}
CACHE_READ_DISCOUNT = 0.115  # calibrated 2026-10-20 via reconcile.py against Fireworks dashboard total
MODEL_LABEL = {
    "kimi-k3": "Kimi K3 (sonnet-tier)",
    "glm-5p3": "GLM 5.3 (opus-tier)",
    "glm-flash": "GLM Flash (fable-tier)",
    "deepseek-flash": "DeepSeek Flash (haiku/subagent-tier)",
}

SKILL_RE = re.compile(r'"skill"\s*:\s*"([^"]+)"')
WORKFLOW_RE = re.compile(r"workflows/([a-z0-9-]+)/")


def rate_for(model):
    m = (model or "").lower()
    for key, r in RATES.items():
        if key in m:
            return key, r
    return m or "unknown", (0.0, 0.0)


def price(model, u):
    key, (ri, ro) = rate_for(model)
    it = u.get("input_tokens", 0)
    cr = u.get("cache_read_input_tokens", 0)
    cc = u.get("cache_creation_input_tokens", 0)
    ot = u.get("output_tokens", 0)
    cost = (it * ri + cc * ri + cr * ri * CACHE_READ_DISCOUNT + ot * ro) / 1e6
    return key, cost, it + cc + cr, ot


def iter_records(since, until):
    for proj in sorted(PROJECTS_DIR.iterdir()):
        if not proj.is_dir():
            continue
        for f in proj.glob("*.jsonl"):
            mtime_ok = True  # cheap prefilter: skip files untouched before `since`
            try:
                if f.stat().st_mtime < since_ts:
                    mtime_ok = False
            except Exception:
                pass
            if not mtime_ok:
                continue
            try:
                fh = open(f)
            except Exception:
                continue
            with fh:
                for line in fh:
                    if '"usage"' not in line:
                        continue
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    if d.get("type") != "assistant":
                        continue
                    msg = d.get("message") or {}
                    u = msg.get("usage")
                    ts = d.get("timestamp", "")
                    if not u or not ts or ts < since or ts >= until:
                        continue
                    yield proj.name, f.stem, ts, msg.get("model", ""), u


def session_skills(path):
    """Scan a transcript for skill and workflow references (labels only)."""
    skills, workflows = set(), set()
    try:
        with open(path) as fh:
            for line in fh:
                if '"skill"' in line:
                    skills.update(SKILL_RE.findall(line))
                if "workflows/" in line:
                    workflows.update(WORKFLOW_RE.findall(line))
    except Exception:
        pass
    return sorted(skills), sorted(workflows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-10-01")
    ap.add_argument("--until", default="2026-10-21")
    ap.add_argument("--by", default="session", choices=["session", "day", "model", "skill"])
    ap.add_argument("--csv")
    ap.add_argument("--top", type=int, default=25)
    args = ap.parse_args()

    global since_ts
    since_ts = __import__("datetime").datetime.fromisoformat(args.since).timestamp()

    sess_cost = defaultdict(float)
    sess_tok = defaultdict(lambda: [0, 0])
    sess_proj = {}
    day_cost = defaultdict(float)
    model_cost = defaultdict(float)
    model_tok = defaultdict(lambda: [0, 0])

    for proj, sess, ts, model, u in iter_records(args.since, args.until):
        key, cost, itoks, otoks = price(model, u)
        sess_cost[(proj, sess)] += cost
        sess_tok[(proj, sess)][0] += itoks
        sess_tok[(proj, sess)][1] += otoks
        sess_proj[(proj, sess)] = proj
        day_cost[ts[:10]] += cost
        model_cost[key] += cost
        model_tok[key][0] += itoks
        model_tok[key][1] += otoks

    total = sum(sess_cost.values())
    if args.by in ("day", "model"):
        if args.by == "day":
            print(f"{'day':<12} {'est. cost':>10}")
            for d in sorted(day_cost):
                print(f"{d:<12} ${day_cost[d]:>9.2f}")
        else:
            print(f"{'model':<28} {'est. cost':>10} {'input Mt':>10} {'output Mt':>10}")
            for m, c in sorted(model_cost.items(), key=lambda x: -x[1]):
                print(f"{MODEL_LABEL.get(m, m):<28} ${c:>9.2f} {model_tok[m][0]/1e6:>10.2f} {model_tok[m][1]/1e6:>10.2f}")
        print(f"\nTotal est.: ${total:.2f}")
        return

    # Session-level (and skill) attribution requires scanning transcripts for labels.
    skill_cost = defaultdict(float)
    rows = []
    for (proj, sess), c in sorted(sess_cost.items(), key=lambda x: -x[1]):
        path = PROJECTS_DIR / proj / f"{sess}.jsonl"
        skills, wfs = ([], []) if args.by == "skill" or c > total * 0.005 else ([], [])
        if args.by == "skill" or c > total * 0.005:
            skills, wfs = session_skills(path)
        label = ", ".join((skills + wfs)[:4]) or "(no skill/workflow)"
        for s in skills + wfs:
            skill_cost[s] += c
        it, ot = sess_tok[(proj, sess)]
        rows.append((proj[:28], sess[:8], label[:60], c, it, ot))

    if args.by == "skill":
        print(f"{'skill/workflow':<40} {'est. cost':>10} {'share':>6}")
        for s, c in sorted(skill_cost.items(), key=lambda x: -x[1])[: args.top]:
            print(f"{s:<40} ${c:>9.2f} {c/total*100:>5.1f}%")
        print(f"\nTotal est.: ${total:.2f}")
        return

    print(f"{'project':<30} {'sess':<9} {'skills/workflows':<61} {'est. cost':>10} {'in Mt':>8} {'out Mt':>8}")
    for proj, sess, label, c, it, ot in rows[: args.top]:
        print(f"{proj:<30} {sess:<9} {label:<61} ${c:>9.2f} {it/1e6:>8.2f} {ot/1e6:>8.2f}")
    print(f"\n{len(rows)} sessions, total est.: ${total:.2f}")

    if args.csv:
        import csv as _csv
        with open(args.csv, "w", newline="") as fh:
            w = _csv.writer(fh)
            w.writerow(["project", "session", "labels", "est_cost_usd", "input_mt", "output_mt"])
            for proj, sess, label, c, it, ot in rows:
                w.writerow([proj, sess, label, f"{c:.4f}", f"{it/1e6:.3f}", f"{ot/1e6:.3f}"])
        print(f"Wrote {args.csv}")


if __name__ == "__main__":
    since_ts = 0.0
    main()
