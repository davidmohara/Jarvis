# Dream Cycle Systems

Support scripts for the dream-cycle workflow.

## llm_tag_extractor.py

LLM-based metadata extractor. Takes a working-memory file's frontmatter and body, returns `date`, `tags`, `related_people` as structured JSON. Called by step-01 archival as the primary enrichment path.

**How it calls Claude:** subprocess to `claude -p` with the prompt over stdin (same pattern as `.claude/skills/rigby-capability-build/scripts/improve_description.py`). No separate API key required — uses the session's Claude Code auth. Default model is `haiku` (fast, ~$0.001 per file).

**Raises `ClaudeAuthError`** when `claude -p` reports "Not logged in". Callers catch this and fall back to the heuristic extractor in `backfill-episodic-tags.py`. This makes the system robust to sandboxed environments (Cowork) where `claude -p` is unavailable, while still using LLM extraction on David's Mac where the scheduled dream-cycle runs.

**Debug CLI:**

```bash
python3 systems/dream-cycle/llm_tag_extractor.py --file memory/episodic/2026-05-12-061241-session-boot-morning-briefing.md
```

## backfill-episodic-tags.py

One-shot recovery tool for episodic files that pre-date the step-01 enrichment fix (May 8 – June 9 window). Two modes:

- **Heuristic (default):** corpus-derived vocabulary plus body keyword matching. Fast, deterministic, no auth.
- **`--llm`:** calls `llm_tag_extractor.py` per file. Higher quality, requires `claude /login` on the host.

If `--llm` is set but auth fails on the first call, the script logs a warning and falls back to heuristic mode for the remainder of the run (no partial-LLM/partial-heuristic file sets).

**Usage:**

```bash
# Dry run, heuristic
python3 systems/dream-cycle/backfill-episodic-tags.py

# Apply, heuristic
python3 systems/dream-cycle/backfill-episodic-tags.py --apply

# Apply, LLM (preferred on David's Mac)
python3 systems/dream-cycle/backfill-episodic-tags.py --llm --apply

# Re-enrich everything (including files that already have tags)
python3 systems/dream-cycle/backfill-episodic-tags.py --llm --force --apply

# Test on 5 files only
python3 systems/dream-cycle/backfill-episodic-tags.py --llm --limit 5
```

## Recommended Re-Backfill on David's Mac

The 50 files backfilled on 2026-06-09 used heuristic tags because the Cowork sandbox couldn't auth `claude -p`. To upgrade them to LLM-quality tags:

```bash
cd ~/develop/jarvis
# Verify claude -p is logged in
echo "ping" | claude -p --output-format text
# If not, run: claude /login

# Then re-enrich the 50 files using LLM
python3 systems/dream-cycle/backfill-episodic-tags.py --llm --force --apply

# Commit
git add memory/episodic/
git commit -m "dream-cycle: upgrade backfilled tags to LLM-extracted (was heuristic)"
git push origin main
```

This is optional — heuristic tags already restored the co-occurrence signal (83/91 entries now scoring ≥3). LLM re-backfill would refine tag selection further.
