#!/usr/bin/env python3
"""
One-shot backfill: enrich untagged episodic files with date, tags, source_file,
related_people. Uses corpus-derived vocabulary from April-era files plus body
keyword matching. Idempotent — skips files that already have date+tags.

Usage:
  python3 systems/dream-cycle/backfill-episodic-tags.py            # dry run
  python3 systems/dream-cycle/backfill-episodic-tags.py --apply    # write changes

Author: jarvis (generated 2026-06-09 during tag-starvation recovery)
"""

import os
import re
import sys
import argparse
import datetime

EPISODIC = "memory/episodic"

# Corpus-derived vocabulary. Each tag maps to a list of body-keyword patterns
# (case-insensitive). Match any → emit tag.
TAG_VOCAB = {
    "briefing":        [r"\bmorning briefing\b", r"\bbriefing\b"],
    "morning-briefing":[r"\bmorning briefing\b"],
    "calendar":        [r"\bcalendar\b", r"\bm365\b", r"\boutlook\b"],
    "omnifocus":       [r"\bomnifocus\b", r"\bOF\b"],
    "omnifocus-timeout":[r"omnifocus.*timeout", r"OF.*timeout"],
    "leads":           [r"\bleads?\b", r"\blead review\b"],
    "travel":          [r"\btravel\b", r"\bflight\b", r"\bairport\b"],
    "flight":          [r"\bflight\b", r"\bairline\b", r"\bairport\b"],
    "flight-conflict": [r"flight.*conflict", r"conflict.*flight"],
    "glc-chicago":     [r"glc.{0,5}chicago", r"global leadership", r"glc-day"],
    "cabo":            [r"\bcabo\b"],
    "ypo":             [r"\bypo\b", r"young presidents"],
    "google-next":     [r"google next", r"google.{0,5}next"],
    "drc-workshop":    [r"drc workshop", r"\bdrc\b"],
    "gold-forum":      [r"gold forum"],
    "make-a-wish":     [r"make.a.wish"],
    "utb-board":       [r"\butb\b", r"university.+texas.+brownsville"],
    "graduation":      [r"\bgraduation\b"],
    "rock2":           [r"\brock ?2\b", r"\brock-2\b"],
    "rock3":           [r"\brock ?3\b", r"\brock-3\b"],
    "rock4":           [r"\brock ?4\b", r"\brock-4\b"],
    "quarterly-rocks": [r"quarterly rock", r"\brocks?\b.*pipeline", r"rock.*review"],
    "one-texas":       [r"one texas", r"one.texas"],
    "revenue":         [r"\brevenue\b", r"\bbookings\b"],
    "pipeline":        [r"\bpipeline\b", r"\bdeals?\b"],
    "co-sell":         [r"\bco-?sell\b"],
    "scorecard":       [r"\bscorecard\b"],
    "1on1-prep":       [r"1on1", r"one.on.one", r"1.on.1"],
    "email":           [r"\bemail\b", r"\binbox\b"],
    "email-triage":    [r"email triage", r"triage.*email"],
    "plaud":           [r"\bplaud\b"],
    "jarvis-inbox":    [r"jarvis.inbox", r"jarvis_inbox"],
    "wfh":             [r"\bwfh\b", r"work from home"],
    "overdue-tasks":   [r"overdue task", r"overdue\b"],
    "boot":            [r"session boot", r"morning boot", r"\bboot\b"],
    "system-maintenance":[r"system maintenance", r"maintenance"],
    "system-health":   [r"system health"],
    "memory-system":   [r"memory system"],
    "memory-pipeline": [r"memory pipeline"],
    "semantic-promotion":[r"semantic promotion", r"promote.*semantic"],
    "score-inflation": [r"score.*inflation", r"score inflation"],
    "dream-cycle":     [r"dream cycle", r"dream-cycle"],
    "git-issues":      [r"git.*lock", r"git.*fail", r"index\.lock", r"non.fast.forward"],
    "git-sync":        [r"git sync", r"sync.gap", r"remote.*ahead"],
    "error-patterns":  [r"error pattern", r"error.*categor"],
    "skills-rewrite":  [r"skills rewrite", r"skill rewrite"],
    "credit-cards":    [r"credit card", r"\bcard\b.*offer", r"card-offer"],
    "rewards":         [r"\brewards?\b"],
    "amex":            [r"\bamex\b", r"american express"],
    "citi":            [r"\bciti\b"],
    "chase":           [r"\bchase\b"],
    "discover":        [r"\bdiscover\b.*card"],
    "atlas":           [r"\batlas\b"],
    "ynab":            [r"\bynab\b"],
    "portfolio-review":[r"portfolio review"],
    "cyber-training":  [r"cyber training", r"cyber.training"],
    "session-index":   [r"session index"],
    "health":          [r"\bgalen\b", r"\bhealth\b.*(review|check|labs)"],
    "lessons":         [r"\blessons\.md\b", r"\blesson learned\b"],
    "podcast":         [r"\bpodcast\b"],
    "rigby":           [r"\brigby\b"],
    "harper":          [r"\bharper\b"],
    "knox":            [r"\bknox\b"],
    "chase-agent":     [r"chase agent"],
    "galen":           [r"\bgalen\b"],
    "sterling":        [r"\bsterling\b"],
    "shep":            [r"\bshep\b"],
    "quinn":           [r"\bquinn\b"],
    "chief":           [r"agent-source:\s*chief", r"chief\b"],
}

PEOPLE_VOCAB = [
    "alice-mburu", "ehren-seim", "scott-mcmichael", "don-mcgreal",
    "david-ohara", "devlin", "randy-mccabe", "mladen-raickovic",
    "tim-rayburn", "ethel-mangum", "sam-dobbins", "vicki",
    "steve-hall", "robyn-fuentes", "dennis-howard", "stuart",
    "tonya-guadiz", "stuart-sides", "curtis", "richard",
    "derek-nwamadi", "kapil-dai", "salah", "david-faircloth",
    "aren-cambre", "vicki-kelly", "scott-pine", "gabriela-garza-ramos",
    "christopher-mcmillan",
]


def parse_frontmatter(text):
    if not text.startswith("---"):
        return None, text
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.DOTALL)
    if not m:
        return None, text
    return m.group(1), m.group(2)


def field(fm, name):
    if fm is None:
        return None
    m = re.search(rf"^{re.escape(name)}\s*:\s*(.+?)$", fm, re.MULTILINE)
    return m.group(1).strip() if m else None


def has_block(fm, name):
    if fm is None:
        return False
    return bool(re.search(rf"^{re.escape(name)}\s*:\s*\n\s*-\s+", fm, re.MULTILINE)) or \
           bool(re.search(rf"^{re.escape(name)}\s*:\s*\[", fm, re.MULTILINE))


def derive_date(fm, fname):
    # Try `created` first
    created = field(fm, "created") if fm else None
    if created:
        m = re.match(r"(\d{4}-\d{2}-\d{2})", created.strip().strip("'\""))
        if m:
            return m.group(1)
    # Fall back to filename prefix
    m = re.search(r"(\d{4}-\d{2}-\d{2})", fname)
    if m:
        return m.group(1)
    return None


def derive_deliverable_tag(fname, fm):
    fname_lower = fname.lower()
    if "morning-briefing" in fname_lower or "morning_briefing" in fname_lower:
        return "briefing"
    if "session-boot" in fname_lower and "briefing" in fname_lower:
        return "briefing"
    if "daily-review" in fname_lower:
        return "daily-review"
    if "dream-summary" in fname_lower or "dream-cycle-summary" in fname_lower:
        return "dream-summary"
    if "session-wrap" in fname_lower or "shutdown" in fname_lower:
        return "session-wrap"
    if "pipeline" in fname_lower:
        return "pipeline-review"
    if "rock" in fname_lower and "review" in fname_lower:
        return "rock-review"
    return None


def derive_tags(body, fname, fm):
    tags = []
    # 1. Deliverable type first
    deliverable = derive_deliverable_tag(fname, fm)
    if deliverable:
        tags.append(deliverable)
    # 2. Agent source if present
    agent = field(fm, "agent-source") if fm else None
    if agent:
        agent_clean = agent.strip().strip("'\"").lower()
        if agent_clean and agent_clean not in tags:
            tags.append(agent_clean)
    # 3. Keyword matching against vocabulary
    body_lower = body.lower()
    full_text = (body + "\n" + (fm or "")).lower()
    for tag, patterns in TAG_VOCAB.items():
        if tag in tags:
            continue
        for pat in patterns:
            if re.search(pat, full_text, re.IGNORECASE):
                tags.append(tag)
                break
        if len(tags) >= 10:
            break
    # Ensure minimum 3 tags
    if len(tags) < 3:
        # add safety fallbacks
        for fallback in ["session", "automated", "scheduled"]:
            if fallback not in tags:
                tags.append(fallback)
            if len(tags) >= 3:
                break
    return tags[:10]


def derive_people(body, fm):
    people = []
    full_text = body + "\n" + (fm or "")
    full_lower = full_text.lower()
    for person in PEOPLE_VOCAB:
        # Match kebab name or "first last" form
        parts = person.split("-")
        kebab_pat = re.escape(person)
        # also try "First Last" matching (first + last separately)
        if re.search(rf"\b{kebab_pat}\b", full_lower):
            people.append(person)
            continue
        if len(parts) >= 2:
            name_pat = r"\b" + r"\s+".join(re.escape(p) for p in parts) + r"\b"
            if re.search(name_pat, full_lower):
                people.append(person)
    return people


def enrich_frontmatter(fm, date_val, source_path, tags, people):
    """Append/overwrite the four enrichment fields. Preserve everything else."""
    if fm is None:
        fm = ""

    # Remove any prior enrichment fields (idempotency)
    for fname_to_strip in ["date", "source_file"]:
        fm = re.sub(rf"^{fname_to_strip}\s*:.*\n?", "", fm, flags=re.MULTILINE)
    # Remove existing tags/related_people blocks
    fm = re.sub(r"^tags\s*:\s*(?:\n(?:\s*-\s*.+\n?)+|.+\n)", "", fm, flags=re.MULTILINE)
    fm = re.sub(r"^related_people\s*:\s*(?:\n(?:\s*-\s*.+\n?)+|\s*\n|.+\n)", "", fm, flags=re.MULTILINE)

    # Build enrichment block
    lines = []
    if date_val:
        lines.append(f"date: {date_val}")
    lines.append(f"source_file: {source_path}")
    lines.append("tags:")
    for t in tags:
        lines.append(f"  - {t}")
    lines.append("related_people:")
    for p in people:
        lines.append(f"  - {p}")

    enrichment = "\n".join(lines)
    fm = fm.rstrip("\n") + "\n" + enrichment
    return fm


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="actually write changes")
    parser.add_argument("--force", action="store_true", help="re-enrich even files that already have tags")
    args = parser.parse_args()

    targets = []
    skipped = []

    for root, dirs, files in os.walk(EPISODIC):
        if "digests" in dirs:
            dirs.remove("digests")
        if os.path.basename(root) == "digests":
            continue
        for fn in files:
            if not fn.endswith(".md") or fn == "README.md":
                continue
            p = os.path.join(root, fn)
            with open(p) as f:
                content = f.read()
            fm, body = parse_frontmatter(content)
            if fm is None:
                skipped.append((p, "no frontmatter"))
                continue
            has_date = bool(field(fm, "date"))
            has_tags = has_block(fm, "tags")
            if has_date and has_tags and not args.force:
                skipped.append((p, "already enriched"))
                continue
            date_val = derive_date(fm, fn)
            source_path = f"memory/working/{fn}"  # canonical source guess
            tags = derive_tags(body, fn, fm)
            people = derive_people(body, fm)
            new_fm = enrich_frontmatter(fm, date_val, source_path, tags, people)
            new_content = f"---\n{new_fm}\n---\n{body}"
            targets.append((p, date_val, tags, people, new_content))

    print(f"Found {len(targets)} files to enrich, {len(skipped)} skipped.")
    print()
    for p, d, t, ppl, _ in targets[:5]:
        print(f"  {p}")
        print(f"    date: {d}")
        print(f"    tags: {t}")
        print(f"    people: {ppl}")
        print()
    if len(targets) > 5:
        print(f"  ... +{len(targets)-5} more")

    if args.apply:
        written = 0
        for p, _, _, _, new_content in targets:
            try:
                with open(p, "w") as f:
                    f.write(new_content)
                written += 1
            except Exception as e:
                print(f"  FAILED: {p}: {e}")
        print(f"\nApplied: {written}/{len(targets)} files written.")
    else:
        print("\n[DRY RUN] Re-run with --apply to write changes.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
