#!/usr/bin/env python3
"""
DEPRECATED — This script is no longer the active version.

The canonical, maintained copy lives at:
    skills/plaud-transcripts/scripts/fetch_plaud.py

This root copy was used in early pipeline development and lacks:
  - trigger_transcript_regeneration()
  - speaker rename verification / retry loop
  - check_speaker_names_in_transcript()

Do not run this file directly. It is retained for git history only.

All Plaud ingest operations run through:
    workflows/plaud-ingest/workflow.md  (step-04)
which references the skills-copy script above.
"""

raise SystemExit(
    "DEPRECATED: Use skills/plaud-transcripts/scripts/fetch_plaud.py instead."
)
