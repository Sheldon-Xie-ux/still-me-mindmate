# HarmonyMind Agentic Interaction Redesign

## Overview

This redesign shifts HarmonyMind away from behaving like a visible task sorter and toward behaving like a judgment-oriented agent. The current MVP can already extract tasks, rank them, and show focus and rhythm information. However, the exposed interaction still makes the user feel like they are manually feeding a productivity tool.

The intended direction is different:

- the user shares context, pressure, goals, constraints, or confusion
- the system internally determines what matters most
- the interface presents the system's current judgment and the best immediate next action

This brings HarmonyMind closer to the desired Hermes-like agent behavior, where prioritization exists inside the system structure rather than being surfaced as the primary product experience.

## Product Shift

### From

HarmonyMind currently feels like:

- "Tell me your tasks"
- "I will sort them"
- "Here is the resulting list"

### To

HarmonyMind should feel like:

- "Tell me what is going on"
- "I understand the signals in your situation"
- "Here is what I think matters most right now"
- "Here is the first step you should take"

The prioritization engine still exists, but it becomes a hidden internal mechanism rather than the visible center of the UI.

## Experience Goals

The redesign should create four user-facing effects:

1. The user feels they are briefing an agent, not filing tasks.
2. The right side of the UI emphasizes judgment and action, not list management.
3. The system gives one strong current priority instead of surfacing a visible ranking process.
4. Safety and pacing remain background intelligence rather than a visible risk workflow.

## Information Architecture

## Right Column

The right side should no longer be led by a stacked visible task list. Its main structure becomes:

### 1. 当前最重要的一件事

This is the primary card and the center of the product experience.

It should show:

- the system's current best judgment about what matters most right now
- a short reason explaining that judgment
- a tone of confidence without pretending certainty

This card answers:

- what should I focus on now?
- why this and not something else?

It should not expose a full ranking table or a visible prioritization mechanism.

### 2. 现在就开始

This card translates the current priority into a concrete starting action.

It should show:

- one immediate next step
- wording that is specific and executable
- a low-friction action framing

Examples:

- "先打开路演 PPT，把目录、核心问题和结论页补齐。"
- "先写给投资人的三句更新摘要，不要一次把整封邮件写完。"

This card answers:

- what do I do in the next five minutes?

### 3. 系统观察

This replaces the current rhythm card as a broader, quieter system-awareness surface.

It should show:

- pacing suggestions
- workload or overload nudges
- brief state observations
- safety notices only when needed

It should not show:

- a risk score
- a mental health metric
- an always-on alert surface

The default state should feel calm and low-noise.

### Supporting Items

Detailed tasks can still exist internally and may still be stored, but they should become secondary support information rather than the most prominent visible surface.

If retained in the UI, they should either:

- move below the three core cards
- or become an expandable supporting section

They should no longer dominate the screen.

## Left Column

## Input Framing

The left side should stop presenting itself as a task entry form.

### Current Problem

Current wording implies:

- tell me your tasks
- I will rank them

That leads users to behave like they are operating a productivity database.

### New Framing

The input should instead invite mixed-context input.

It should communicate that users can share:

- recent situation
- goals
- limits
- time pressure
- blockers
- emotional load

Example framing:

- "告诉我现在发生了什么"
- "你可以直接说近况、目标、限制，或者当前最卡的一件事"

This supports a more agentic relationship: the user provides context, and the system interprets it.

## Response Style

The assistant reply should stop narrating visible task-sorting behavior.

### Avoid

- "我先帮你拆成 4 个任务，并按轻重缓急排好了顺序。"

### Prefer

- "我判断你现在最该先推进的是路演 PPT，因为它最接近外部结果，也最容易带动后续事项。"
- "你现在先不要同时推进商业计划书和投资人回复，先把最影响结果的那一件做成。"

## Recommended Response Structure

The system reply should usually contain two visible parts:

### 当前判断

- what the system believes is the most important thing now
- why it made that judgment

### 现在就开始

- the first concrete step
- phrased as a small, immediate action

This keeps the interaction consistent with the right-side cards.

## Backend Mental Model

The backend should no longer think of itself primarily as:

- message in
- tasks out
- sorted list shown

Instead, it should think in terms of agent judgment.

## New Internal Pipeline

### 1. Context Parsing

The system extracts signals such as:

- deadline pressure
- external consequence
- desired outcome
- blockers
- context switching pressure
- emotional overload or cognitive strain

### 2. Current Priority Determination

The system computes one `current_priority`.

This is not just the top visible task row. It is the system's best current judgment about what deserves attention first.

### 3. Next Action Generation

The system converts `current_priority` into one concrete, immediate action.

This action should be:

- small
- clear
- directly startable

### 4. System Observation Layer

The system separately produces:

- rhythm observations
- overload nudges
- safety interrupt state

These remain low-visibility unless needed.

## Backend Contract Direction

The current backend response shape is task-centered:

- `tasks`
- `focus`
- `rhythm`
- `safety`

The redesigned direction should move toward an agent-centered contract:

- `current_priority`
- `next_action`
- `system_observation`
- optional `supporting_items`

## Transitional Strategy

To avoid destabilizing the MVP, the redesign should happen in two stages.

### Stage 1: Presentation Shift

Keep the existing backend task extraction and ranking engine, but change what the UI emphasizes.

Map current backend outputs into:

- one visible current priority
- one visible next action
- one system observation card

The old task list becomes secondary.

### Stage 2: Contract Shift

Refactor backend orchestration to return explicit agent-centered fields:

- `current_priority`
- `next_action`
- `system_observation`

The frontend then stops depending on task-list-first semantics.

This staged approach preserves momentum before the hackathon while aligning the system with the intended long-term product direction.

## Immediate UI Changes

For the next implementation slice, the UI should change as follows:

### Replace

- `今日任务`

### With

- `当前最重要的一件事`

### Replace

- `专注模式`

### With

- `现在就开始`

This card may still reuse existing focus data behind the scenes, but the visible framing should be action-oriented, not timer-oriented.

### Replace

- `今日节奏`

### With

- `系统观察`

This card should unify pacing suggestions and low-interruption notices.

### Left Side

Change:

- `对话输入`

to something closer to:

- `告诉我现在发生了什么`

And change the helper copy to signal mixed-context input rather than task entry.

## Design Constraints

### 1. No Visible Sorting UI as the Center

The product must not visually feel like a ranked task manager.

### 2. No Risk Dashboard

Safety remains background logic that only surfaces when needed.

### 3. Preserve Demo Stability

The redesign should move the product toward the intended direction without introducing large-scale instability before presentation use.

### 4. Preserve Long-Term Architecture

This should not be a fake presentation-only layer. It should be a step toward the actual product model.

## Acceptance Criteria

The redesign is successful when:

1. The user no longer feels asked to manually supply a task list.
2. The most prominent right-side card shows the system's current best judgment.
3. The second card gives a concrete first step rather than only a focus label.
4. The UI emphasizes conclusion and action, not sorting mechanics.
5. Safety remains background and low-disruption.
6. The system still supports the existing demo flow while feeling more agentic.
