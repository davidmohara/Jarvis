---
name: plaud-transcripts
owning_agent: knox
description: >
  Process Plaud.ai recording transcripts from a staging folder and convert them into
  tagged Obsidian markdown notes filed into the user's vault. Use this skill whenever
  the user mentions Plaud transcripts, Plaud recordings, importing Plaud notes, or
  wants to process recordings from their Plaud device into Obsidian. Also trigger on
  "process my Plaud recordings", "import Plaud transcripts", "get my Plaud notes into
  the vault", "sync Plaud to Obsidian", or any request involving Plaud recordings
  becoming vault notes. A scheduled task pre-fetches Plaud data daily via the API, so
  this skill's job is to transform what's already waiting in the staging folder into
  proper Obsidian notes.
model: sonnet
trigger_keywords: [plaud, transcript, recording, ingest, audio]
trigger_agents: [chief, knox]
---

<!-- system:start -->
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->