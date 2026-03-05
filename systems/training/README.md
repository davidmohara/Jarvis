# IES Training & Progression System

<!-- system:start -->

## Philosophy

Training in IES is not a course — it's guided repetition with real data. Executives learn by doing their actual work through the system, with Shep coaching them through progressively more capable workflows.

### Core Principles

**Learn by doing, not reading.** Every training module is a guided walkthrough of a real task with real data. There are no slides, no quizzes, no simulations.

**Guided but open.** Nothing is locked. An executive can use any capability from day one. The training system tracks mastery and suggests what to learn next — it doesn't gatekeep.

**Modular and evolution-aware.** Training content lives separately from agents. When an evolution adds new capabilities, it registers new training modules in the curriculum. The system grows automatically.

**Three categories, one curriculum.** Agent tasks, system operations, and connector integrations all live in the same progression framework. Because executives need all three to be effective.

**Role-adaptive.** A CEO's morning briefing looks different from a VP's. Training modules include role-specific coaching notes that Shep applies during delivery.

---

## Tiers

Progression is measured as a percentage (0-100%) across four tiers. Tiers are aspirational markers, not gates.

### Getting Started (0-25%)

Daily operations loop. The executive can run Chief smoothly — morning briefing, inbox processing, daily review. They understand the file structure and core operations.

**Core modules:** Morning Briefing, Inbox Processing, Daily Review
**System modules:** System Orientation, Core Operations

### Building Rhythm (25-50%)

Delegation, coaching, and connecting daily work to quarterly rocks. The executive uses Shep for people management and Quinn for goal alignment.

**Core modules:** Delegation Tracking, 1:1 Prep, Rock Review
**System modules:** Delegation System, Review Operations, Decision Framework

### Strategic Mode (50-75%)

Pipeline management, client strategy, and thought leadership. The executive engages Chase for revenue work and Harper for communications.

**Core modules:** Pipeline Review, Client Meeting Prep, Strategy Builder, Email Drafting
**System modules:** Personal Customization

### Full System (75-100%)

Multi-agent orchestration. The executive uses all agents fluidly, understands the evolution system, and has all connectors configured.

**Core modules:** Account Strategy, Initiative Tracker, Presentation Builder, Content Calendar
**System modules:** Evolution System
**Connector modules:** M365, CRM

---

## How It Works

### For Users

1. **Onboard** — `/training-onboard` runs once. Interview, orientation, first real task.
2. **Check progress** — `/training-status` shows your dashboard anytime.
3. **Learn next** — `/training-next` gets Shep's recommendation for what to try next.
4. **Run a module** — `/training-module [name]` walks you through a specific capability.

### For the System

- `curriculum.json` is the master index of all training modules
- Each module has a guided walkthrough file in `modules/{category}/`
- User state is tracked in `state/` (single-user per deployment)
- Shep orchestrates all coaching via the `shep-training` skill
- Evolutions register new modules via the `training_prompts` manifest field

### For Evolutions

When Rigby applies an evolution that includes `training_prompts`:
1. New module entries are added to `curriculum.json` with `evolution_source` set
2. Guided walkthrough files are created in the appropriate `modules/{category}/` directory
3. Shep surfaces "New capability available" in the next `/training-next` call

---

## File Map

```
systems/training/
├── README.md                    ← You are here
├── curriculum.json              ← Master curriculum index
├── modules/
│   ├── agent/                   ← Agent task walkthroughs
│   ├── system/                  ← System operation walkthroughs
│   └── connector/               ← Connector setup walkthroughs
└── state/                       ← Current user's training state
    ├── config.json              ← Role, rhythm, preferences (set during onboard)
    ├── progress.json            ← Tier, completion %, session count
    ├── mastery.json             ← Per-module attempts, skill level
    └── history.md               ← Session log
```
<!-- system:end -->
