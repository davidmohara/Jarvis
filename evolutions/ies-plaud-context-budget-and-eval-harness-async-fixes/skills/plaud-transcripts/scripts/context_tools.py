#!/usr/bin/env python3
"""Bounded context broker for Plaud transcript handling (plaud-ingest context budget).

The plaud-ingest workflow's non-no-op cost driver is transcript bodies entering
the Knox agent's conversation context and then being re-carried across every
remaining turn (~8.8M re-carried input tokens per ingest day, boot token analysis
2026-10-28 follow-up 5). This script moves transcript text file-to-file and
returns only bounded evidence the agent needs for judgment:

  speaker-evidence   per-speaker self-ID candidates, opening/closing utterances,
                    name mentions, scan stats (proves a full-transcript scan)
  action-candidates commitment-candidate lines from every speaker, bounded
  assemble-note      writes the complete vault note (transcript block verbatim,
                    speaker renames applied) and prints a transcript-free digest
  note-digest       prints an existing vault note without its transcript block

Stdlib only. Run with python3. Structured JSON to stdout, diagnostics to stderr.
Exit codes: 0 success, 1 usage/precondition, 2 execution failure.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SEGMENT_RE = re.compile(
    r"^\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*\*\*([^*]+?)\*\*\s*::?\s*(.*)$"
)
SELF_ID_RE = re.compile(
    r"(?i)\b(?:i'?m|i am|my name is|this is|it'?s)\s+"
    r"([A-Z][a-zA-Z.'-]+(?:\s+[A-Z][a-zA-Z.'-]+){0,2})\b"
    r"|\b([A-Z][a-zA-Z.'-]+)\s+here\b"
    r"|\bthis is\s+\w+\s+from\s+([A-Za-z &]+)"
)
NAME_MENTION_RE = re.compile(
    r"(?i)\b(?:ask|check with|talk to|call|email|send(?:\s+this)?\s+to|"
    r"loop in|introduce(?:\s+us)?\s+to|ping|follow up with)\s+"
    r"([A-Z][a-zA-Z.'-]+(?:\s+[A-Z][a-zA-Z.'-]+)?)\b"
)
ACTION_RE = re.compile(
    r"(?i)\b(i'?ll|i will|we'?ll|we will|i can|can you|could you|let'?s|"
    r"need to|needs to|have to|has to|should|must|"
    r"by\s+(?:mon|tues|wednes|thurs|fri|satur|sun)day|"
    r"by end of (?:the )?(?:day|week|month|quarter)|by tomorrow|by next week|"
    r"follow(?:ing)? up|send (?:you|me|us|it|that|the)|"
    r"schedule|invite|draft|deliver|review|share (?:that|this|it))\b"
)
PLACEHOLDERS = {
    "attendees": "<!--FILL:attendees-->",
    "summary": "<!--FILL:summary-->",
    "key_points": "<!--FILL:key-points-->",
    "action_items": "<!--FILL:action-items-->",
}


def err(msg):
    print(f"context_tools: {msg}", file=sys.stderr)


def cap(text, limit=300):
    text = text.strip()
    return text if len(text) <= limit else text[: limit - 3] + "..."


def parse_staged(path):
    """Parse a staged plaud_*.md into title, date, duration, summary, segments."""
    text = path.read_text(encoding="utf-8", errors="replace")
    title = ""
    m = re.match(r"^#\s+(.+)$", text, re.M)
    if m:
        title = m.group(1).strip()
    date = ""
    m = re.search(r"^\*\*Date:\*\*\s*(.+)$", text, re.M)
    if m:
        date = m.group(1).strip()
    duration = None
    m = re.search(r"^\*\*Duration:\*\*\s*(\d+)\s*s", text, re.M)
    if m:
        duration = int(m.group(1))
        if duration > 7200:  # list endpoint ms bug (see 2026-10-28 state notes)
            duration = duration // 1000
    summary = ""
    m = re.search(r"^##\s+AI Summary\s*\n(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    if m:
        summary = m.group(1).strip()
    segments = []
    for line in text.splitlines():
        m = SEGMENT_RE.match(line.strip())
        if m:
            segments.append({"t": m.group(1), "speaker": m.group(2).strip(),
                            "text": m.group(3).strip()})
    return {"title": title, "date": date, "duration": duration,
            "summary": summary, "segments": segments, "raw_len": len(text)}


def topic_context(parsed, cap_bytes=900):
    return {
        "title": parsed["title"],
        "date": parsed["date"],
        "duration_seconds": parsed["duration"],
        "ai_summary_excerpt": cap(parsed["summary"], cap_bytes),
        "ai_summary_chars": len(parsed["summary"]),
        "first_utterances": [
            {"t": s["t"], "speaker": s["speaker"], "text": cap(s["text"])}
            for s in parsed["segments"][:3]
        ],
    }


def cmd_speaker_evidence(args):
    path = Path(args.staged_file).expanduser()
    if not path.is_file():
        err(f"staged file not found: {path}")
        return 1
    parsed = parse_staged(path)
    segs = parsed["segments"]
    speakers = {}
    for s in segs:
        speakers.setdefault(s["speaker"], []).append(s)
    out = {
        "staged_file": str(path),
        "topic_context": topic_context(parsed),
        "scan": {
            "total_segments": len(segs),
            "segments_scanned": len(segs),  # regex pass covers every line
            "distinct_speakers": sorted(speakers.keys()),
        },
    }
    sp = {}
    for name, utter in speakers.items():
        self_ids, mentions = [], []
        for u in utter:
            if SELF_ID_RE.search(u["text"]):
                self_ids.append({"t": u["t"], "text": cap(u["text"])})
            m = NAME_MENTION_RE.search(u["text"])
            if m:
                mentions.append({"t": u["t"], "text": cap(u["text"])})
        sp[name] = {
            "segment_count": len(utter),
            "opening_utterances": [
                {"t": u["t"], "text": cap(u["text"])} for u in utter[:2]],
            "closing_utterances": [
                {"t": u["t"], "text": cap(u["text"])} for u in utter[-3:]],
            "self_id_candidates": self_ids[:8],
            "addresses_other_names": mentions[:6],
        }
    out["speakers"] = sp
    payload = json.dumps(out, indent=1)
    while len(payload) > args.max_bytes:
        trimmed = False
        for name in sp:
            b = sp[name]
            for key in ("closing_utterances", "self_id_candidates",
                        "addresses_other_names", "opening_utterances"):
                if len(b[key]) > 2:
                    b[key] = b[key][:-1]
                    trimmed = True
        if not trimmed:
            break
        payload = json.dumps(out, indent=1)
    out["truncated_to_fit_budget"] = len(payload) > args.max_bytes
    print(json.dumps(out, indent=1))
    err(f"evidence for {len(sp)} speaker(s), {len(segs)} segments scanned, "
        f"{len(payload)} bytes emitted (budget {args.max_bytes})")
    return 0


def cmd_action_candidates(args):
    path = Path(args.staged_file).expanduser()
    if not path.is_file():
        err(f"staged file not found: {path}")
        return 1
    parsed = parse_staged(path)
    hits = [
        {"speaker": s["speaker"], "t": s["t"], "text": cap(s["text"], 240)}
        for s in parsed["segments"] if ACTION_RE.search(s["text"])
    ]
    summary_lines = [
        {"speaker": "(AI Summary)", "t": "-", "text": cap(line.strip(), 240)}
        for line in parsed["summary"].splitlines()
        if line.strip() and ACTION_RE.search(line)
    ]
    out = {
        "staged_file": str(path),
        "scan": {"total_segments": len(parsed["segments"]),
                 "candidate_lines": len(hits) + len(summary_lines)},
        "summary_candidates": summary_lines[:10],
        "candidates": hits,
    }
    while len(json.dumps(out)) > args.max_bytes and len(out["candidates"]) > 5:
        out["candidates"] = out["candidates"][: int(len(out["candidates"]) * 0.8)]
    out["truncated_to_fit_budget"] = len(
        out["candidates"]) < len(hits)
    print(json.dumps(out, indent=1))
    err(f"{len(hits)} transcript + {len(summary_lines)} summary candidates "
        f"from {len(parsed['segments'])} segments (budget {args.max_bytes})")
    return 0


def load_speaker_map(args):
    if not args.speakers:
        return {}
    raw = args.speakers
    if raw.startswith("@"):
        p = Path(raw[1:]).expanduser()
        if not p.is_file():
            err(f"speaker mapping file not found: {p}")
            sys.exit(1)
        raw = p.read_text()
    try:
        m = json.loads(raw)
        if not isinstance(m, dict) or not all(
                isinstance(k, str) and isinstance(v, str) for k, v in m.items()):
            raise ValueError("mapping must be {\"Speaker N\": \"Real Name\"}")
        return m
    except ValueError as e:
        err(f"invalid --speakers JSON: {e}")
        sys.exit(1)


def cmd_assemble_note(args):
    path = Path(args.staged_file).expanduser()
    if not path.is_file():
        err(f"staged file not found: {path}")
        return 1
    if not args.file_id:
        err("--file-id is required (Gate 5 traceability: every note must "
            "carry the Plaud file_id)")
        return 1
    target = Path(args.target).expanduser()
    if target.exists() and not args.force:
        err(f"target exists: {target} (use --force to overwrite)")
        return 1
    parsed = parse_staged(path)
    mapping = load_speaker_map(args)
    date = parsed["date"] or "1970-01-01"
    parts = [p for p in date.split("-")]
    timeline = "/".join(parts) if len(parts) == 3 else date
    tags = ["content/meeting"] + (args.tags or []) + [f"meta/timeline/{timeline}"]
    duration_min = round((parsed["duration"] or 0) / 60.0, 1)
    if not (args.tags or []):
        tags.insert(1, "work/operations")  # safe default; agent may Edit-swap
    trans_lines = []
    for s in parsed["segments"]:
        name = mapping.get(s["speaker"], s["speaker"])
        trans_lines.append(f"**{name}** ({s['t']}):\n{s['text']}\n")
    transcript_block = "\n".join(trans_lines)
    note = f"""---
tags:
{chr(10).join('  - ' + t for t in tags)}
file_id: {args.file_id}
date: {date}
duration_minutes: {duration_min}
source: Plaud AI
---

# {parsed['title'] or target.stem}

## Meeting Details

- **Date:** {date}
- **Duration:** {duration_min} min
- **Platform:** Plaud.ai
- **Organizer:** <!--FILL:organizer-->

## Attendees

{PLACEHOLDERS['attendees']}

## Summary

{PLACEHOLDERS['summary']}

## Key Discussion Points

{PLACEHOLDERS['key_points']}

## Action Items

{PLACEHOLDERS['action_items']}

## Transcript

<details>
<summary>Full Transcript</summary>

{transcript_block}

</details>
"""
    if args.dry_run:
        err(f"dry run: would write {len(note)} bytes to {target}")
    else:
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(note, encoding="utf-8")
        except OSError as e:
            err(f"write failed: {e}")
            return 2
    digest = {
        "action": "assembled" if not args.dry_run else "dry-run",
        "target": str(target),
        "note_bytes": len(note),
        "file_id": args.file_id,
        "date": date,
        "duration_minutes": duration_min,
        "tags": tags,
        "speaker_renames_applied": mapping,
        "unrenamed_generic_labels": sorted(
            {s['speaker'] for s in parsed['segments']
             if re.match(r"(?i)^speaker\s+\d+$", s['speaker'])
             and s['speaker'] not in mapping}),
        "transcript_block": {
            "segments": len(parsed["segments"]),
            "bytes": len(transcript_block),
            "sha256": hashlib.sha256(
                transcript_block.encode()).hexdigest()[:16],
        },
        "ai_summary_excerpt": cap(parsed["summary"], 900),
        "ai_summary_chars": len(parsed["summary"]),
        "placeholders_to_fill": list(PLACEHOLDERS.values()) + [
            "<!--FILL:organizer-->"],
    }
    print(json.dumps(digest, indent=1))
    err(f"note assembled: {len(parsed['segments'])} segments moved to "
        f"{target} without entering conversation context")
    return 0


def cmd_note_digest(args):
    paths = []
    for pat in args.notes:
        p = Path(pat).expanduser()
        if p.is_file():
            paths.append(p)
        else:
            paths.extend(sorted(Path.cwd().glob(pat)))
    if not paths:
        err(f"no notes matched: {args.notes}")
        return 1
    for p in paths:
        text = p.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"<details>.*?</details>", text, re.S)
        block = m.group(0) if m else ""
        seg_count = len(re.findall(r"^\*\*.*?\*\* \(", block, re.M))
        digest = text.replace(block, (
            f"[TRANSCRIPT BLOCK OMITTED: {seg_count} segments, "
            f"{len(block)} bytes]") if block else
            "[no transcript block found]")
        if len(digest) > args.max_bytes:
            digest = digest[: args.max_bytes] + "\n[digest truncated at budget]"
        print(f"===== {p} =====\n{digest}")
        err(f"digest of {p.name}: {len(digest)} bytes "
            f"(transcript block {len(block)} bytes omitted)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="context_tools.py",
        description="Bounded context broker for Plaud transcripts: move "
                    "transcript bodies file-to-file, surface only bounded "
                    "evidence. See example under each subcommand's --help.",
        epilog="Example: python3 context_tools.py speaker-evidence "
               "~/Downloads/transcript-staging/plaud_meeting.md --max-bytes 12000")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("speaker-evidence",
                       help="bounded per-speaker self-ID evidence + scan stats")
    p.add_argument("staged_file")
    p.add_argument("--max-bytes", type=int, default=12000)
    p.set_defaults(fn=cmd_speaker_evidence)

    p = sub.add_parser("action-candidates",
                       help="bounded commitment-candidate lines per speaker")
    p.add_argument("staged_file")
    p.add_argument("--max-bytes", type=int, default=8000)
    p.set_defaults(fn=cmd_action_candidates)

    p = sub.add_parser("assemble-note",
                       help="write full vault note (transcript verbatim, renames "
                            "applied); print transcript-free digest")
    p.add_argument("staged_file")
    p.add_argument("--target", required=True,
                   help="vault note path to write, e.g. "
                        "'zzPlaud/Client/2026-10-27 Meeting.md'")
    p.add_argument("--file-id", required=False,
                   help="Plaud file_id (required unless --dry-run)")
    p.add_argument("--speakers", default=None,
                   help='rename map JSON or @file: {"Speaker 1": "Steve Idoux"}')
    p.add_argument("--tags", default=None,
                   help='extra frontmatter tags JSON: ["work/client"]')
    p.add_argument("--force", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_assemble_note)

    p = sub.add_parser("note-digest",
                       help="print vault note(s) minus transcript block")
    p.add_argument("notes", nargs="+",
                   help="note path(s) or glob, e.g. 'zzPlaud/Client/2026-10-*.md'")
    p.add_argument("--max-bytes", type=int, default=6000)
    p.set_defaults(fn=cmd_note_digest)

    args = ap.parse_args(argv)
    try:
        if args.cmd == "assemble-note" and args.tags:
            args.tags = json.loads(args.tags)
            if not isinstance(args.tags, list):
                err("--tags must be a JSON array")
                return 1
        return args.fn(args)
    except BrokenPipeError:
        return 0
    except Exception as e:  # execution failure class
        err(f"unexpected failure: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
