---
name: plaud-speaker-id
owning_agent: knox
model: sonnet
description: >
  Identify generic speaker labels (Speaker 1, Speaker 2, etc.) in Plaud recordings
  by cross-referencing recording timestamps against calendar attendees. Auto-resolves
  when confidence is high; surfaces a consolidated question to the controller when it
  cannot. Use during the plaud-ingest workflow step-03, or standalone when a recording
  has unidentified speakers. Also triggered by "who is Speaker 1", "identify the
  speakers in this recording", or "I need to label the speakers".
trigger_keywords: [speaker id, identify speaker, who was on the call]
trigger_agents: [knox, chief]
---

<!-- system:start -->
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->