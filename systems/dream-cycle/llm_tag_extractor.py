#!/usr/bin/env python3
"""
LLM-based tag extractor for working-memory archival enrichment.

Takes a working-memory file's frontmatter + body and returns:
  - date         (YYYY-MM-DD)
  - tags         (5-10 lowercase kebab-case strings)
  - related_people (lowercase kebab-case names)

Calls `claude -p` as a subprocess — same pattern as
.claude/skills/rigby-capability-build/scripts/improve_description.py.
No separate ANTHROPIC_API_KEY needed; uses the session's Claude Code auth.

Usage as module:
  from llm_tag_extractor import extract_enrichment
  result = extract_enrichment(frontmatter_str, body_str, filename, model="haiku")
  # → {"date": "2026-05-13", "tags": [...], "related_people": [...]}

Usage as CLI (for debugging):
  python3 llm_tag_extractor.py --file memory/working/foo.md
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Default model — haiku is fast and cheap, sufficient for tag extraction
DEFAULT_MODEL = "haiku"

# Hard cap on body length sent to LLM. Tag extraction doesn't need the entire
# briefing — first 8KB captures the substance of any morning-briefing, daily-
# review, or dream-summary we've seen.
MAX_BODY_CHARS = 8000

# Reference vocabulary — corpus-derived tag tokens from April-era files. We
# pass this to the LLM as a STRONG PREFERENCE list so co-occurrence matches
# stay aligned across the corpus. New tokens are allowed when nothing in the
# vocabulary fits.
TAG_VOCABULARY = [
    "briefing", "morning-briefing", "daily-review", "dream-summary", "session-wrap",
    "calendar", "omnifocus", "omnifocus-timeout", "leads", "email", "email-triage",
    "travel", "flight", "flight-conflict", "glc-chicago", "cabo", "las-vegas",
    "ypo", "google-next", "drc-workshop", "gold-forum", "utb-board", "graduation",
    "rock1", "rock2", "rock3", "rock4", "quarterly-rocks",
    "one-texas", "revenue", "pipeline", "co-sell", "scorecard", "1on1-prep",
    "credit-cards", "rewards", "amex", "citi", "chase", "discover", "atlas",
    "ynab", "portfolio-review", "card-offers",
    "plaud", "jarvis-inbox", "wfh", "overdue-tasks", "boot", "session-index",
    "system-maintenance", "system-health", "memory-system", "memory-pipeline",
    "semantic-promotion", "score-inflation", "dream-cycle", "git-issues", "git-sync",
    "error-patterns", "lessons", "skills-rewrite",
    "podcast", "health", "make-a-wish", "cyber-training", "1on1",
    # Agent identifiers
    "chief", "rigby", "harper", "knox", "galen", "sterling", "shep", "quinn", "chase-agent", "jarvis",
]


class ClaudeAuthError(RuntimeError):
    """Raised when `claude -p` is not authenticated (sandbox, fresh machine, etc.)."""


def _call_claude(prompt: str, model: str = DEFAULT_MODEL, timeout: int = 60) -> str:
    """Invoke `claude -p`, send prompt over stdin, return stdout.

    Raises ClaudeAuthError if the CLI reports it is not logged in — callers
    can catch this to fall back to a heuristic extractor.
    """
    cmd = ["claude", "-p", "--output-format", "text"]
    if model:
        cmd.extend(["--model", model])

    # Strip CLAUDECODE env var so nesting inside an existing session is safe.
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    result = subprocess.run(
        cmd, input=prompt, capture_output=True, text=True,
        env=env, timeout=timeout,
    )
    if result.returncode != 0:
        combined = (result.stdout + " " + result.stderr).lower()
        if "not logged in" in combined or "please run /login" in combined or "unauthorized" in combined:
            raise ClaudeAuthError(
                "claude -p reports not logged in. Run `claude /login` on this machine."
            )
        raise RuntimeError(
            f"claude -p exited {result.returncode}\nstderr: {result.stderr[:500]}"
        )
    # Some `claude -p` builds print auth errors to stdout with exit 0
    if "Not logged in" in result.stdout and len(result.stdout) < 200:
        raise ClaudeAuthError(
            "claude -p reports not logged in. Run `claude /login` on this machine."
        )
    return result.stdout


def _build_prompt(frontmatter: str, body: str, filename: str) -> str:
    body_trimmed = body[:MAX_BODY_CHARS]
    truncated_note = "" if len(body) <= MAX_BODY_CHARS else f"\n\n[Body truncated at {MAX_BODY_CHARS} chars; original was {len(body)} chars]"
    vocab_str = ", ".join(TAG_VOCABULARY)

    return f"""You are extracting structured metadata from a working-memory file for the Jarvis dream cycle. The metadata will drive co-occurrence-based salience scoring across many such files.

You must return a single JSON object with exactly these fields:
- `date`: A YYYY-MM-DD string. Source priority: (1) the `created` field in the frontmatter, (2) the filename prefix. If neither is parseable, use null.
- `tags`: An array of 5-10 lowercase kebab-case strings (e.g. "briefing", "morning-briefing", "glc-chicago"). See selection rules below.
- `related_people`: An array of lowercase kebab-case names extracted from the body (e.g. "alice-mburu", "scott-mcmichael"). Empty array if none mentioned.

TAG SELECTION RULES:
1. ALWAYS include the deliverable type as the first tag. Possible values: briefing, morning-briefing, daily-review, dream-summary, session-wrap, pipeline-review, rock-review.
2. ALWAYS include the agent source as a tag (read from `agent-source` field — usually `chief`, `harper`, `knox`, `rigby`, `galen`, `sterling`, `shep`, `quinn`, or `jarvis`).
3. Strongly prefer tags from this corpus vocabulary so cross-file co-occurrence matches: {vocab_str}
4. Add new kebab-case tags only when nothing in the vocabulary fits a notable concept in the body.
5. Cover the substantive content: domains touched (calendar, omnifocus, pipeline), notable events (travel, glc-chicago, flight-conflict), specific accounts or initiatives mentioned.
6. All tags must be lowercase, kebab-case (hyphens between words), no spaces, no underscores, no capitals.
7. Cap at 10 tags. Quality and reuse over quantity.

PEOPLE EXTRACTION:
- Match named individuals (first-last form), convert to kebab-case lowercase ("Alice Mburu" → "alice-mburu").
- Skip generic role mentions ("the team", "ops folks").
- Empty array if none.

INPUT FILENAME: {filename}

INPUT FRONTMATTER:
{frontmatter}

INPUT BODY:
{body_trimmed}{truncated_note}

Respond with ONLY the JSON object inside <result> tags. No prose, no commentary.

Example response format:
<result>
{{"date": "2026-05-13", "tags": ["briefing", "chief", "calendar", "omnifocus", "leads", "travel"], "related_people": ["alice-mburu"]}}
</result>"""


def extract_enrichment(
    frontmatter: str,
    body: str,
    filename: str,
    model: str = DEFAULT_MODEL,
    timeout: int = 60,
) -> dict:
    """Call the LLM and parse the structured enrichment fields.

    Returns:
        {
            "date": str | None,
            "tags": list[str],
            "related_people": list[str],
            "_raw_response": str,  # for debugging
        }

    Raises:
        RuntimeError if the LLM call fails or returns un-parseable output.
    """
    prompt = _build_prompt(frontmatter, body, filename)
    response = _call_claude(prompt, model=model, timeout=timeout)

    # Extract JSON from <result> tags
    m = re.search(r"<result>\s*(\{.*?\})\s*</result>", response, re.DOTALL)
    if not m:
        # Fallback: maybe the model returned bare JSON
        m = re.search(r"(\{[^{}]*\"tags\"[^{}]*\})", response, re.DOTALL)
        if not m:
            raise RuntimeError(
                f"Could not parse JSON from LLM response. First 500 chars:\n{response[:500]}"
            )
    json_str = m.group(1)
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from LLM: {e}\nJSON was: {json_str[:500]}")

    # Validate and normalize
    date = data.get("date")
    if date is not None:
        if not isinstance(date, str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            date = None

    tags = data.get("tags", [])
    if not isinstance(tags, list):
        tags = []
    tags = [
        re.sub(r"[^a-z0-9-]", "", t.lower().replace("_", "-").replace(" ", "-"))
        for t in tags if isinstance(t, str) and t.strip()
    ]
    tags = [t for t in tags if t][:10]

    people = data.get("related_people", [])
    if not isinstance(people, list):
        people = []
    people = [
        re.sub(r"[^a-z0-9-]", "", p.lower().replace("_", "-").replace(" ", "-"))
        for p in people if isinstance(p, str) and p.strip()
    ]
    people = [p for p in people if p]

    return {
        "date": date,
        "tags": tags,
        "related_people": people,
        "_raw_response": response,
    }


def main():
    parser = argparse.ArgumentParser(description="LLM-based tag extractor (debug CLI)")
    parser.add_argument("--file", required=True, help="Path to working-memory or episodic .md file")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Claude model (default: haiku)")
    parser.add_argument("--show-raw", action="store_true", help="Print raw LLM response")
    args = parser.parse_args()

    content = Path(args.file).read_text()
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", content, re.DOTALL)
    if not m:
        print(f"ERROR: {args.file} has no parseable frontmatter", file=sys.stderr)
        sys.exit(1)
    fm, body = m.group(1), m.group(2)

    result = extract_enrichment(fm, body, os.path.basename(args.file), model=args.model)
    if not args.show_raw:
        result.pop("_raw_response", None)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
