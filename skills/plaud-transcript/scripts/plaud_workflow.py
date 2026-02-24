#!/usr/bin/env python3
"""
Plaud Transcript Extraction Workflow

This is the end-to-end executable workflow for extracting meeting transcripts
from Plaud AI and saving them to Obsidian. Designed to be called from osascript
or directly from the Mac host.

Usage:
    python3 plaud_workflow.py --file-id <id> --output-dir <path>
    python3 plaud_workflow.py --check-new --output-dir <path>

The --check-new flag lists all recordings and identifies unprocessed ones
by comparing against existing files in the output directory.

Note: This script cannot fetch from the Plaud API directly — it needs the
auth token from Chrome's localStorage. The calling agent (Jarvis/Chief) handles
the Chrome JS execution and passes the fetched JSON data via --transcript-json
and --summary-json arguments or temp files.

This script handles:
  - Parsing transcript JSON into formatted markdown
  - Parsing summary/action items/highlights into structured sections
  - Assembling the complete markdown document
  - Identifying action items assigned to O'Hara for OmniFocus routing
"""

import json
import argparse
import os
import re
import sys
from datetime import datetime


OBSIDIAN_PLAUD = "/Users/davidohara/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian/zzPlaud"


def ms_to_timestamp(ms):
    """Convert milliseconds to MM:SS format."""
    total_sec = ms // 1000
    minutes = total_sec // 60
    seconds = total_sec % 60
    return f"{minutes:02d}:{seconds:02d}"


def format_duration(duration_ms):
    """Convert duration in ms to 'XXm XXs' format."""
    total_sec = duration_ms // 1000
    minutes = total_sec // 60
    seconds = total_sec % 60
    return f"{minutes}m {seconds:02d}s"


def extract_speakers(transcript_data):
    """Get unique speaker names in order of first appearance."""
    seen = set()
    speakers = []
    for item in transcript_data:
        speaker = item.get("speaker") or item.get("original_speaker", "Unknown")
        if speaker not in seen:
            seen.add(speaker)
            speakers.append(speaker)
    return speakers


def build_transcript_section(transcript_data):
    """Convert transcript JSON array to markdown transcript section."""
    lines = []
    current_speaker = None
    for item in transcript_data:
        timestamp = ms_to_timestamp(item.get("start_time", 0))
        speaker = item.get("speaker") or item.get("original_speaker", "Unknown")
        content = item.get("content", "").strip()
        if not content:
            continue
        if speaker != current_speaker:
            if current_speaker is not None:
                lines.append("")
            lines.append(f"**{speaker}** [{timestamp}]:")
            lines.append(content)
            current_speaker = speaker
        else:
            lines[-1] = lines[-1] + " " + content
    return "\n".join(lines)


def clean_summary(ai_content):
    """Extract meeting notes from auto_sum_note, removing Plaud boilerplate."""
    if not ai_content:
        return ""
    # Remove ## Meeting Information block and everything before ## Meeting Notes
    lines = ai_content.split("\n")
    output = []
    skip = True
    for line in lines:
        if line.strip().startswith("## Meeting Notes"):
            skip = False
            continue  # Skip the header itself, we'll add our own
        if not skip:
            output.append(line)
    result = "\n".join(output).strip()
    if not result:
        # Fallback: return everything after the > metadata block
        in_meta = False
        output = []
        for line in lines:
            if line.strip().startswith(">"):
                in_meta = True
                continue
            if in_meta and not line.strip().startswith(">"):
                in_meta = False
            if not in_meta and line.strip() and not line.strip().startswith("## Meeting Information"):
                output.append(line)
        result = "\n".join(output).strip()
    return result


def parse_action_items(ai_content):
    """Extract action items and key decisions from sum_multi_note."""
    if not ai_content:
        return "", "", ""

    sections = {"action_items": "", "key_decisions": "", "detailed_minutes": ""}
    current_section = None
    current_lines = []

    for line in ai_content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("## Action Items") or stripped.startswith("### Action Items"):
            if current_section:
                sections[current_section] = "\n".join(current_lines).strip()
            current_section = "action_items"
            current_lines = []
        elif stripped.startswith("## Key Decisions") or stripped.startswith("### Key Decisions"):
            if current_section:
                sections[current_section] = "\n".join(current_lines).strip()
            current_section = "key_decisions"
            current_lines = []
        elif stripped.startswith("## Detailed Minutes") or stripped.startswith("### Detailed Minutes"):
            if current_section:
                sections[current_section] = "\n".join(current_lines).strip()
            current_section = "detailed_minutes"
            current_lines = []
        elif current_section:
            current_lines.append(line)

    if current_section:
        sections[current_section] = "\n".join(current_lines).strip()

    return sections["action_items"], sections["key_decisions"], sections["detailed_minutes"]


def extract_ohara_actions(action_items_text, meeting_title, meeting_date):
    """Find action items assigned to O'Hara/David for OmniFocus routing."""
    ohara_items = []
    if not action_items_text:
        return ohara_items

    for line in action_items_text.split("\n"):
        line = line.strip()
        if not line.startswith("-"):
            continue
        # Check if assigned to O'Hara or David
        lower = line.lower()
        if "@o'hara" in lower or "@ohara" in lower or "@david" in lower or "@[o'hara]" in lower:
            # Clean up the action item text
            item = re.sub(r'@\[?O\'?Hara\]?', '', line, flags=re.IGNORECASE).strip()
            item = re.sub(r'^-\s*', '', item).strip()
            item = re.sub(r'^-\s*', '', item).strip()
            if item:
                ohara_items.append(item)

    return ohara_items


def build_document(title, date, duration_str, transcript_data, summary_content=None,
                   action_items_content=None, highlights_content=None):
    """Assemble the complete markdown document."""
    speakers = extract_speakers(transcript_data)
    month_day = date[5:7] + "-" + date[8:10]

    lines = []
    lines.append(f"# {month_day} Meeting: {title}")
    lines.append("")
    lines.append(f"**Date**: {date}")
    lines.append(f"**Duration**: {duration_str}")
    lines.append("**Source**: Plaud AI Recording")
    lines.append(f"**Participants**: {', '.join(speakers)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Summary section
    if summary_content:
        cleaned = clean_summary(summary_content)
        if cleaned:
            lines.append("## Summary")
            lines.append("")
            lines.append(cleaned)
            lines.append("")

    # Action Items section
    if action_items_content:
        action_items, key_decisions, _ = parse_action_items(action_items_content)
        if action_items:
            lines.append("## Action Items")
            lines.append("")
            lines.append(action_items)
            lines.append("")
        if key_decisions:
            lines.append("## Key Decisions")
            lines.append("")
            lines.append(key_decisions)
            lines.append("")

    # AI Highlights section
    if highlights_content:
        lines.append("## AI Highlights")
        lines.append("")
        lines.append(highlights_content)
        lines.append("")

    # Transcript separator and content
    lines.append("---")
    lines.append("")
    lines.append(build_transcript_section(transcript_data))

    return "\n".join(lines)


def get_existing_dates(output_dir):
    """Get set of YYYY-MM-DD dates already processed."""
    dates = set()
    if not os.path.exists(output_dir):
        return dates
    for f in os.listdir(output_dir):
        if f.endswith(".md") and len(f) >= 10:
            date_prefix = f[:10]
            try:
                datetime.strptime(date_prefix, "%Y-%m-%d")
                dates.add(date_prefix)
            except ValueError:
                continue
    return dates


def main():
    parser = argparse.ArgumentParser(description="Plaud transcript workflow")
    parser.add_argument("--transcript-json", help="Path to transcript JSON file")
    parser.add_argument("--summary-json", help="Path to summary JSON (auto_sum_note)")
    parser.add_argument("--actions-json", help="Path to action items JSON (sum_multi_note)")
    parser.add_argument("--highlights-json", help="Path to highlights JSON (sum_multi_note)")
    parser.add_argument("--title", help="Meeting title")
    parser.add_argument("--date", help="Meeting date (YYYY-MM-DD)")
    parser.add_argument("--duration", help="Duration string (e.g., '30m 59s')")
    parser.add_argument("--duration-ms", type=int, help="Duration in milliseconds")
    parser.add_argument("--output-dir", default=OBSIDIAN_PLAUD, help="Output directory")
    parser.add_argument("--check-new", action="store_true", help="List unprocessed recordings")
    parser.add_argument("--file-list-json", help="Path to Plaud file list JSON")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    if args.check_new and args.file_list_json:
        # Compare file list against existing
        with open(args.file_list_json) as f:
            file_list = json.load(f)
        existing = get_existing_dates(args.output_dir)

        recordings = file_list if isinstance(file_list, list) else file_list.get("data_file_list", [])
        new_recordings = []
        for rec in recordings:
            start_ms = rec.get("start_time", 0)
            rec_date = datetime.fromtimestamp(start_ms / 1000).strftime("%Y-%m-%d")
            if rec_date not in existing and rec.get("is_trans"):
                new_recordings.append({
                    "id": rec.get("id"),
                    "filename": rec.get("filename"),
                    "date": rec_date,
                    "duration": format_duration(rec.get("duration", 0))
                })

        print(json.dumps(new_recordings, indent=2))
        return

    if not args.transcript_json or not args.title or not args.date:
        parser.error("--transcript-json, --title, and --date are required for processing")

    # Load transcript
    with open(args.transcript_json) as f:
        transcript_data = json.load(f)

    # Load optional content
    summary_content = None
    if args.summary_json and os.path.exists(args.summary_json):
        with open(args.summary_json) as f:
            data = json.load(f)
            summary_content = data.get("ai_content", "")

    action_items_content = None
    if args.actions_json and os.path.exists(args.actions_json):
        with open(args.actions_json) as f:
            data = json.load(f)
            action_items_content = data.get("ai_content", "")

    highlights_content = None
    if args.highlights_json and os.path.exists(args.highlights_json):
        with open(args.highlights_json) as f:
            data = json.load(f)
            highlights_content = data.get("ai_content", "")

    # Duration
    duration_str = args.duration
    if not duration_str and args.duration_ms:
        duration_str = format_duration(args.duration_ms)
    if not duration_str:
        duration_str = "Unknown"

    # Build and save document
    doc = build_document(args.title, args.date, duration_str, transcript_data,
                         summary_content, action_items_content, highlights_content)

    # Clean title for filename
    clean_title = re.sub(r'[^\w\s-]', '', args.title).strip()
    clean_title = re.sub(r'\s+', ' ', clean_title)
    output_path = os.path.join(args.output_dir, f"{args.date} {clean_title}.md")

    with open(output_path, "w") as f:
        f.write(doc)

    print(f"Saved: {output_path}", file=sys.stderr)
    print(f"Utterances: {len(transcript_data)}", file=sys.stderr)

    # Extract O'Hara action items for OmniFocus routing
    if action_items_content:
        ohara_items = extract_ohara_actions(action_items_content, args.title, args.date)
        if ohara_items:
            print("\n=== OMNIFOCUS ITEMS ===", file=sys.stderr)
            for item in ohara_items:
                print(f"  - {item}", file=sys.stderr)
            # Output as JSON for the calling agent to route
            print(json.dumps({"omnifocus_items": ohara_items, "meeting": args.title, "date": args.date}))
        else:
            print(json.dumps({"omnifocus_items": [], "meeting": args.title, "date": args.date}))
    else:
        print(json.dumps({"omnifocus_items": [], "meeting": args.title, "date": args.date}))


if __name__ == "__main__":
    main()
