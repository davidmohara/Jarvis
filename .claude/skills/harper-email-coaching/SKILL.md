---
name: harper-email-coaching
description: Analyze sent emails to provide personalized feedback on communication effectiveness, executive presence, and delegation clarity
context: fork
agent: general-purpose
model: sonnet
---

# Harper Email Coaching Skill

## Overview

Harper's email coaching skill analyzes the executive's sent emails to provide personalized feedback on communication effectiveness, executive presence, and delegation clarity.

Load agent persona from `agents/harper.md` before executing this skill.

## Capabilities

### Email Analysis
- **Retrieval**: Accesses sent emails from past 2 weeks or since last coaching session
- **Fallback**: Manual paste option when local mail client unavailable
- **Calibration**: Aligns feedback with executive's VOICE.md preferences
- **Baseline Assessment**: Asks about intentions and self-assessment before analysis

### Analysis Framework
Harper evaluates emails across five key dimensions:

| Dimension | What Harper Analyzes | Executive Impact |
|-----------|----------------------|------------------|
| **Tone** | Warmth-authority balance, audience calibration | Builds trust and credibility |
| **Clarity** | Conciseness, directness, lack of ambiguity | Reduces back-and-forth, speeds decisions |
| **Delegation** | Clear asks, named owners, follow-up expectations | Improves execution and accountability |
| **Executive Presence** | Confidence, decisiveness, strategic thinking | Strengthens leadership perception |
| **Consistency** | Voice alignment across contexts and audiences | Builds reliable personal brand |

### Output Format

Each coaching session delivers:

1. **Scorecard**: Rating across 5 dimensions (Strong/Good/Needs Work)
2. **Email Highlights**: 2-3 specific emails with before/after rewrites
3. **Pattern Insights**: Key observations about communication patterns
4. **Action Focus**: One concrete improvement for the coming week
5. **Baseline Context**: Executive's intentions and self-assessment

## Usage

### Basic Coaching
```typescript
import { executeEmailCoaching } from "~/src/skills/harper-email-coaching";

const result = await executeEmailCoaching();
console.log(result.scorecard);
console.log(result.actionable_focus);
```

### With Manual Email Paste
```typescript
const emails = [
  "Subject: Project Update\n\nTeam, I wanted to follow up...",
  "Subject: Meeting Notes\n\nHi everyone, here are my notes..."
];

const result = await executeEmailCoaching({
  manualPaste: emails
});
```

### With Baseline Assessment
```typescript
const result = await executeEmailCoaching({
  askUser: async (question) => {
    // Interactive prompt for executive
    return {
      intentions: "Be more direct in delegation",
      self_assessment: "I over-explain context"
    };
  }
});
```

## Integration Points

### Training Module Integration
- Triggered by `email-coaching` training module completion
- Tracks progress in `training/state/coaching/email-history.json`
- Updates mastery tracker after each session

### VOICE.md Calibration
- Reads executive's communication style preferences
- Calibrates tone and style feedback accordingly
- Flags drift from intended voice

### Harper Agent Integration
- Registered in Harper's task portfolio
- Trigger: "email coaching" or "review my emails"
- Data requirement: Email (Sent Items) access

## Technical Implementation

### Email Sources
1. **Local Mail Client** (Primary)
   - Retrieves from sent items folder
   - Timeframe: Past 2 weeks or since last session
   - Automatic filtering and parsing

2. **Manual Paste** (Fallback)
   - User copies emails directly
   - Format: Subject, recipients, body
   - Recommended: 5-10 recent emails

### Analysis Pipeline
1. **Baseline Assessment**: Capture executive's intentions and self-perception
2. **Voice Calibration**: Load and parse VOICE.md preferences
3. **Content Analysis**: Evaluate each email against framework
4. **Pattern Detection**: Identify recurring communication habits
5. **Recommendation Generation**: Create actionable improvements

### Privacy & Security
- Processes only sent emails (never incoming)
- Content analyzed locally, not stored beyond observations
- Observations reference emails by subject/date only
- Executive controls which emails to include

## Configuration

### Required Files
- `VOICE.md`: Executive's communication style preferences
- Access to sent emails folder or manual paste capability

### Optional Configuration
- Custom timeframe (default: 2 weeks)
- Analysis focus areas
- Output format preferences

## Error Handling

### Mail Client Access
- Falls back to manual paste when local client unavailable
- Prompts user for email content with clear formatting guidelines

### VOICE.md Missing
- Proceeds with generic coaching framework
- Recommends creating VOICE.md for better calibration

### Insufficient Emails
- Requires minimum 3 emails for meaningful analysis
- Prompts for additional content if needed

## Examples

### Scorecard Output
```json
{
  "scorecard": {
    "tone": "Needs Work",
    "clarity": "Good", 
    "delegation": "Needs Work",
    "executive_presence": "Good",
    "consistency": "Good"
  }
}
```

### Email Highlight
```json
{
  "subject": "Q2 Planning Meeting",
  "before": "Team, I wanted to follow up on our discussion...",
  "after": "Team, Decision: Postpone initiative until Q3...",
  "reasoning": "Lead with decision, reduce context"
}
```

### Pattern Insight
```json
{
  "pattern": "Over-explains context before making requests",
  "impact": "Reduces clarity, slows decision-making"
}
```

## Development Notes

### Extension Points
- Custom analysis dimensions for specific roles
- Industry-specific communication patterns
- Integration with email providers beyond local client

### Testing
- Mock email retrieval for consistent test data
- Simulate VOICE.md variations
- Test fallback scenarios (no mail client, missing VOICE.md)

---

*This skill transforms email from a communication tool into a leadership development asset.*
