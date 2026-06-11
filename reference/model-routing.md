# Model Routing — Agent Defaults and Step-Level Guidance

## Agent defaults

| Agent | Default model | Rationale |
|-------|--------------|-----------|
| Chief | `sonnet` | Briefing synthesis requires coherent narrative |
| Knox | `haiku` | Mechanical transforms, file I/O, API calls — most steps are pure data movement |
| Chase | `sonnet` | Relationship nuance and deal context need judgment |
| Quinn | `opus` | Strategy, pattern recognition, and coaching require deep reasoning |
| Rigby | `sonnet` | Error analysis and evolution packaging need careful reading |
| Shep | `sonnet` | 1:1 prep and coaching tone require interpersonal judgment |
| Harper | `sonnet` | Writing quality matters |
| Galen | `sonnet` | Medical interpretation requires care |

## Step-level guidance

When writing or reviewing step files, apply this heuristic:

| Step does this | Use |
|---|---|
| API calls, file reads/writes, script execution, staging ops | `haiku` |
| Calendar cross-reference, heuristic matching, speaker ID | `sonnet` |
| Synthesis, analytical rewriting, action item extraction | `sonnet` |
| Strategy, pattern analysis, complex coaching | `opus` |
