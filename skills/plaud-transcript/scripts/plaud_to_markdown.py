#!/usr/bin/env python3
"""
Convert a Plaud transcript JSON file to formatted markdown.

Usage:
    python3 plaud_to_markdown.py <json_path> <title> <date> <duration> [--output <path>]

Arguments:
    json_path   Path to the transcript JSON file
    title       Meeting title (e.g., "FUB AI Training Program")
    date        Meeting date in YYYY-MM-DD format
    duration    Duration string (e.g., "30m 59s")
    --output    Optional output file path. If omitted, prints to stdout.

The transcript JSON should be an array of objects:
    [{"content": "...", "start_time": 960, "end_time": 22620, "speaker": "Name", ...}, ...]
"""

import json
import sys
import argparse


def ms_to_timestamp(ms):
    """Convert milliseconds to MM:SS format."""
    total_sec = ms // 1000
    minutes = total_sec // 60
    seconds = total_sec % 60
    return f"{minutes:02d}:{seconds:02d}"


def extract_speakers(data):
    """Get unique speaker names in order of first appearance."""
    seen = set()
    speakers = []
    for item in data:
        speaker = item.get("speaker") or item.get("original_speaker", "Unknown")
        if speaker not in seen:
            seen.add(speaker)
            speakers.append(speaker)
    return speakers


def convert_transcript(data, title, date, duration):
    """Convert transcript JSON array to markdown string."""
    speakers = extract_speakers(data)

    lines = []
    # Reconstruct the original Plaud title format
    month_day = date[5:7] + "-" + date[8:10]
    lines.append(f"# {month_day} Meeting: {title}")
    lines.append("")
    lines.append(f"**Date**: {date}")
    lines.append(f"**Duration**: {duration}")
    lines.append("**Source**: Plaud AI Recording")
    lines.append(f"**Participants**: {', '.join(speakers)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    current_speaker = None
    for item in data:
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
            # Merge consecutive utterances from same speaker
            lines[-1] = lines[-1] + " " + content

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Convert Plaud transcript JSON to markdown")
    parser.add_argument("json_path", help="Path to transcript JSON file")
    parser.add_argument("title", help="Meeting title")
    parser.add_argument("date", help="Meeting date (YYYY-MM-DD)")
    parser.add_argument("duration", help="Duration string (e.g., '30m 59s')")
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
    args = parser.parse_args()

    with open(args.json_path, "r") as f:
        data = json.load(f)

    markdown = convert_transcript(data, args.title, args.date, args.duration)

    if args.output:
        with open(args.output, "w") as f:
            f.write(markdown)
        print(f"Saved {len(markdown)} chars to {args.output}", file=sys.stderr)
    else:
        print(markdown)


if __name__ == "__main__":
    main()
