# HarmonyMind OpenClaw Skill Design

## Overview

HarmonyMind should no longer be designed as a standalone productivity surface that waits for the user to ask for prioritization. Its intended long-term form is an embedded OpenClaw skill that quietly watches for drift, overload, and deadline compression inside the user's ongoing conversations with their agent.

The user experience goal is simple:

- most of the time, the skill is invisible
- when the user is getting pulled off course, the skill helps the agent gently re-center them
- when needed, the agent should surface one clear current focus and one concrete next step
- psychological safety remains a background guardrail, not a visible scoring system

This design defines the first real OpenClaw version of HarmonyMind as a structured skill rather than a web product.

## Product Definition

### What It Is

HarmonyMind is an OpenClaw skill that helps the host agent detect when the user is:

- splitting attention across too many competing goals
- entering a compressed deadline window
- showing clear signs of cognitive or emotional overload

When one of those states is detected, the skill nudges the host agent to briefly shift from normal conversation into a tighter intervention shape:

- `当前重点`
- `下一步`

### What It Is Not

HarmonyMind is not:

- a standalone task manager
- a visible ranking dashboard
- a therapy bot
- a mental health scoring product
- a system that permanently stores short-term tasks as long-term memory

## Experience Goals

The first OpenClaw version should create five effects:

1. The user does not feel they need to explicitly ask for prioritization.
2. The host agent notices when the user is drifting, overloaded, or deadline-compressed.
3. The intervention is brief and useful rather than preachy or repetitive.
4. The skill preserves the host agent's voice instead of acting like a separate persona.
5. Long-term memory captures durable goals and recurring drift patterns without becoming a dump of temporary to-dos.

## Trigger Logic

HarmonyMind should be silent by default.

It should not intervene every turn. It should only activate when the host agent detects that the user's current context needs active narrowing.

### Trigger Categories

#### 1. Multi-goal drift

Trigger when the user is juggling several goals, projects, or requests at once and no clear working center remains.

Examples:

- they keep adding new objectives without closing the previous one
- they are switching between several meaningful threads in the same turn
- the conversation shows spreading rather than convergence

The important signal is not "many tasks exist". The signal is "the user is losing a clear center of gravity."

#### 2. Deadline compression

Trigger when an external time boundary is near enough that the agent should help the user stop diffusing effort.

Examples:

- "tonight"
- "before Friday"
- "I have to send this in two hours"
- a previously known external commitment is now inside a short decision window

The goal is not to list all pending work. The goal is to help the agent say which result matters most now.

#### 3. Clear overload

Trigger when the user shows signs of cognitive overload, emotional overload, or inability to choose a next step.

Examples:

- "I'm too scattered"
- "my head is exploding"
- "I don't know what to do first"
- repeated signs of pressure, confusion, or paralysis

This is not diagnosis. It is a practical signal that the user needs the decision surface reduced.

### Trigger States

HarmonyMind should use three simple states:

- `silent`
- `focus_intervene`
- `safe_interrupt`

`safe_interrupt` takes precedence over all normal focus behavior.

### Trigger Rule

The skill should activate when the host agent judges that the user is either:

- losing focus due to spread and overload
- or already inside a constraint window that should narrow focus now

## Intervention Shape

When HarmonyMind activates, it should not replace the whole response. It should insert a small structure into the host agent's normal reply.

### Visible Structure

#### 当前重点

One sentence that states what matters most right now.

Requirements:

- it is a judgment, not a task dump
- it explains why this matters now
- it implicitly narrows what not to focus on yet

Good example:

- `当前重点：先把路演材料推进到可讲状态，其他事项先不要一起展开。`

#### 下一步

One concrete action the user can start immediately.

Requirements:

- small enough to start in roughly 5 to 15 minutes
- concrete enough to reduce hesitation
- not abstract encouragement

Good example:

- `下一步：先只补齐路演的目录、核心结论和最想让对方记住的一页。`

### Tone Rules

HarmonyMind interventions should be:

- calm
- direct
- low-drama
- non-commanding

Avoid:

- long justifications
- visible ranking explanations
- therapeutic overreach
- a second "character" appearing inside the host reply

Preferred style:

- "我建议我们先收住这一件事"
- "先别一起推三件事，我们先把最影响结果的那一项推进起来"

## Memory Design

HarmonyMind should support cross-session continuity, but only at the level of durable patterns.

### What To Store

The skill may write or update:

- `long_term_goal`
- `desired_outcome`
- `recurring_drift_pattern`
- `support_preference`

### What Not To Store

The skill should not store as long-term memory:

- today-only tasks
- one-off deadlines
- temporary to-do lists
- detailed short project breakdowns

Examples of allowed memory:

- "User is repeatedly working toward fundraising readiness."
- "User tends to fragment attention when deadlines approach."
- "User responds better to one direct priority and one immediate action than to a broad list."

Examples of disallowed memory:

- "Send investor email on Friday."
- "Finish BP today."
- "Revise slide 7."

### Memory Write Rules

Only write or revise durable memory when at least one of these is true:

- the user explicitly states a long-term direction
- the same drift pattern appears repeatedly across conversations
- a stable support preference becomes clear

When updating memory, prefer abstraction over accumulation. The skill should summarize the pattern, not hoard raw conversation details.

## Safety Boundary

HarmonyMind includes a background safety layer, but safety should not be surfaced as a permanent front-stage feature.

### Normal State

- no visible risk scores
- no visible monitoring dashboard
- no mental health metrics

### Mild Safety Signal

If the user appears overloaded or emotionally strained but not in crisis:

- keep the main intervention shape
- allow a brief pacing nudge in the host response

Example:

- `先只推进这一件事。你现在已经有点被太多事情拉散了，先把决策面缩小。`

### Safe Interrupt

If crisis language appears, HarmonyMind should not perform normal focus narrowing. It should yield to the host agent's safety response path.

This skill must never compete with or override explicit crisis handling.

## OpenClaw Integration Shape

HarmonyMind should be packaged as a normal OpenClaw workspace skill.

### Target Location

Primary runtime location:

- `~/.openclaw/workspace/skills/harmonymind-focus-skill`

Project source copy:

- `skills/harmonymind-focus-skill`

The project copy is the sharable artifact. The OpenClaw workspace copy is the local test install.

### Skill Package Structure

- `SKILL.md`
- `references/trigger-signals.md`
- `references/response-rules.md`
- `references/memory-rules.md`

### SKILL.md Responsibilities

The root skill file should stay concise and cover:

- when the skill applies
- trigger states
- the required intervention structure
- memory boundaries
- safety precedence

### Reference File Responsibilities

`trigger-signals.md` should contain:

- positive examples
- non-trigger counterexamples
- edge cases for drift vs ordinary multitasking

`response-rules.md` should contain:

- good and bad intervention examples
- tone constraints
- examples across work-planning, personal overload, and mixed-context turns

`memory-rules.md` should contain:

- allowed memory fields
- write thresholds
- non-examples
- update patterns for abstraction over raw detail

## Testing Strategy

The first test phase should be skill-level dogfooding, not channel integration.

### Phase 1: Local skill validation

Install the skill into the local OpenClaw workspace and pressure-test it with realistic prompts.

The first test pack should cover:

- clear non-trigger turns
- multi-goal drift
- deadline compression
- overload without crisis
- crisis handoff
- repeated conversations that should update long-term memory

### Phase 2: Friend testing

Share the skill package with friends who already have OpenClaw or can place the skill into a workspace manually.

Ask them to validate:

- whether the skill stays quiet when it should
- whether the intervention feels useful instead of annoying
- whether the `当前重点 + 下一步` shape actually helps them start
- whether the memory behavior feels supportive rather than intrusive

### Success Criteria

The first release is successful if:

1. ordinary turns do not trigger noisy interventions
2. drift and overload turns reliably produce a useful narrowing response
3. crisis language defers to safety handling
4. long-term memory captures goals and patterns, not transient task clutter
5. external testers can install the skill without extra hidden steps

## Non-Goals For V1

The first OpenClaw skill version does not need:

- a standalone UI
- visible task boards
- calendar or email integration
- full autonomous task execution
- psychological scoring
- analytics dashboards

## Implementation Direction

V1 should prioritize:

- clean trigger rules
- reliable intervention formatting
- safe memory boundaries
- easy local installation into OpenClaw

Anything that weakens those four priorities should be deferred.
