# HarmonyMind Web MVP Design

## Overview

HarmonyMind is a focus-first AI productivity companion with built-in psychological safety boundaries. The product is not designed as a therapy or crisis tool. Its value comes from helping users capture work, prioritize what matters, enter focus mode, and receive low-friction protective guidance only when needed.

This first web MVP is intentionally scoped to support two goals at once:

1. Deliver a polished, end-to-end demo suitable for a hackathon presentation before Sunday.
2. Establish a credible product foundation that can evolve into a real long-term product without rewriting the core interaction model.

The MVP will use a mixed interface:

- a conversation-led workspace on the left
- an execution dashboard on the right
- background safety logic that stays mostly invisible unless intervention is necessary

## Product Principles

### 1. Focus, Not Dependence

HarmonyMind should help the user move toward action, not keep them chatting with the system. Responses should translate into clearer plans, fewer competing priorities, and one current focus target.

### 2. Safety by Background Guardrails

Psychological safety is part of the system design, but not a visible scorecard. Users should not see continuous risk metrics or feel surveilled. Safety mechanisms should operate in the background and only surface when there is a meaningful reason to interrupt or gently nudge.

### 3. Real Product, Narrow First Version

The Sunday demo version is a constrained first slice of a longer-term product. The scope is narrowed for delivery speed, but the architecture should preserve future expansion into external integrations, richer analysis, and more channels.

### 4. Human-Centered Tone

The assistant should feel calm, structured, and non-dramatic. It should avoid over-anthropomorphizing itself, avoid dependency-reinforcing language, and avoid presenting itself as a clinical or emotional authority.

## Target MVP Outcome

By the end of this implementation, a user should be able to:

1. Open a web app and describe a messy real-life situation in natural language.
2. See the system extract tasks, prioritize them, and explain the reasoning.
3. Start a single focus session on the most important task.
4. Receive gentle pacing support if they show overload or overuse patterns.
5. See a lightweight daily rhythm summary rather than a diagnostic risk panel.
6. Trigger a safe interruption flow if crisis language is detected.

## User Experience

## Primary Layout

The main page uses a two-column layout with a compact top status area.

### Left: Conversation Workspace

This is the user's main input channel. The user enters natural language statements such as:

> "I need to finish my pitch deck by Friday, reply to two investors, and I am feeling overwhelmed. Help me sort this out."

The assistant responds with structured, action-oriented help. Typical response content includes:

- recognized tasks
- recommended task order
- concise rationale for prioritization
- focus recommendation
- occasional pacing guidance

The conversation should not become a generic chat feed. Each assistant response should aim to update the right-hand workspace.

### Right: Execution Workspace

The right side contains three persistent product modules.

#### Today Tasks

Shows the top tasks for today in priority order. Each card includes:

- title
- due timing if available
- priority label
- status
- short explanation of why it is ranked where it is

The visual goal is to make the list feel actionable rather than overwhelming.

#### Focus Session

Shows the one task currently selected for focus. Includes:

- current focus task
- session timer
- start action
- pause action
- complete action
- extend by 10 minutes

When a focus session completes, the system generates a short reflection summary and updates the task state.

#### Daily Rhythm

Shows non-clinical, supportive daily pacing information:

- tasks completed today
- minutes spent in focus
- current work rhythm
- a simple suggestion such as "good moment for a short break" or "you still have room for one more focused block"

This module is intentionally framed around rhythm and pacing rather than mental health scoring.

## Hidden Safety Design

Safety logic is a background system concern rather than a persistent front-end widget.

### Normal State

No risk score or warning state is shown in the interface.

### Gentle Nudge State

If the system detects sustained overload language, repeated distress cues, or very long uninterrupted usage, it may insert a low-interruption message into the conversation or rhythm area. This should feel like supportive pacing, not surveillance.

Examples:

- "You have been pushing for a while. It may help to take a short pause before the next block."
- "There is a lot competing for attention here. Let's narrow to one step first."

### Safe Interrupt State

If crisis language or clearly unsafe self-harm-related language is detected, the normal task flow stops. The UI replaces the ordinary action response with a safety response card that:

- states clearly that the system cannot provide crisis or medical help
- encourages immediate contact with trusted people or local professional resources
- avoids continuing normal productivity planning in that moment

This state must be intentionally rare and rule-based in the MVP.

## Demo Narrative

The MVP should support a compelling, realistic demo path.

### Demo Flow

1. The presenter enters a realistic mixed-intent statement involving multiple tasks and signs of overload.
2. The system extracts tasks and updates the task list.
3. The system explains which task should come first and why.
4. The presenter starts a focus session on the top task.
5. During the flow, the system may show a gentle pacing nudge.
6. The presenter completes the session and shows the updated task state and summary.

### Demo Message Example

> "I need to finish my roadshow pitch, revise the business plan, and send follow-ups today. Messages keep distracting me and I feel a bit overwhelmed. Help me plan this."

This example demonstrates both productivity value and background safety logic without turning the product into a visible mental health dashboard.

## Technical Architecture

The recommended implementation is:

- React + Vite frontend
- Python API backend
- SQLite for persistence

This provides enough UI flexibility for a polished demo while keeping backend delivery realistic within the timeline.

### Frontend Responsibilities

- render the mixed conversation + dashboard UI
- manage local interaction state
- send user messages to the backend
- render structured assistant results
- reflect task, focus, and rhythm updates immediately

### Backend Responsibilities

- orchestrate user message processing
- extract or update tasks from conversation input
- calculate task priority
- determine focus recommendation
- run background safety checks
- track usage analytics
- persist state to SQLite

## Backend Modules

### 1. Chat Orchestration Service

Entry point for the main user message flow.

Responsibilities:

- accept the raw user message
- classify intent at a lightweight level
- call task extraction
- call prioritization
- call safety guard
- assemble a structured response payload for the frontend

Output should contain both conversational text and UI state updates.

### 2. Task Service

Handles task CRUD and lifecycle transitions.

Task fields for MVP:

- `id`
- `title`
- `description`
- `category`
- `priority_score`
- `priority_label`
- `status`
- `due_date`
- `estimated_minutes`
- `created_at`
- `updated_at`

### 3. Priority Engine

Calculates ranking based on a practical weighted model.

Initial dimensions:

- urgency
- importance
- effort or duration cost

The engine should also return a short explanation such as:

- "This is first because it is both urgent and high-impact."
- "This is second because it matters, but it can wait until after the deadline-driven item."

The MVP does not need a highly adaptive model. It needs understandable and defensible ranking logic.

### 4. Focus Service

Manages a single current focus session.

Responsibilities:

- select focus task
- start session
- pause session
- complete session
- extend session
- record focus duration
- produce short completion summary

Only one active focus session should exist at a time in the MVP.

### 5. Safety Guard

Runs in the background on message input and usage state changes.

MVP output states:

- `none`
- `gentle_nudge`
- `safe_interrupt`

Detection methods for MVP:

- keyword-based crisis phrase detection
- simple overload or negative-expression heuristics
- uninterrupted usage duration thresholds

This module should be easy to replace later with more advanced models, but the MVP should remain intentionally conservative and explicit.

### 6. Analytics Service

Tracks lightweight behavioral usage data.

MVP fields:

- daily message count
- focus minutes today
- current uninterrupted usage duration
- last break timestamp

These values support pacing suggestions but are not exposed as risk scores.

### 7. Persistence Layer

SQLite stores:

- tasks
- chat history summaries or messages as needed for MVP
- focus sessions
- analytics counters
- system events such as gentle nudges or interrupts

SQLite is chosen for delivery speed and local reliability. The schema should remain clean enough to migrate later if needed.

## Real vs Mock Boundaries

### Must Be Real in MVP

- user-to-backend message flow
- task extraction from conversation
- task persistence
- priority calculation
- focus session state changes
- gentle nudge and safe interrupt logic
- daily rhythm metrics
- SQLite-backed state

### Can Be Mocked or Deferred

- calendar integration
- email integration
- project management integrations
- multi-channel messaging gateways
- advanced model-driven emotion classification
- long-term personalized learning loops

These deferred areas should be represented, if at all, as future-facing extension points rather than fake core functionality.

## Interaction Model

Each user message should produce a structured backend result with these conceptual parts:

- assistant reply text
- extracted task changes
- refreshed task list
- focus recommendation or update
- rhythm summary update
- optional safety event

The frontend should treat the assistant as a state-producing orchestrator, not only a text generator.

## Design Constraints

### Constraint 1: No Visible Risk Dashboard

Risk values, severity scores, or continuous safety panels must not appear in the default UI.

### Constraint 2: Non-Clinical Boundaries

The product must not imply diagnosis, treatment, or therapeutic authority.

### Constraint 3: Demo-Ready but Honest

Core functionality shown in the demo should actually work. Peripheral integrations may be deferred, but the presentation should not depend on fake end-to-end behavior for the primary loop.

### Constraint 4: Long-Term Compatibility

The architecture should not assume this product is only a hackathon artifact. The chosen module boundaries should still make sense if the product continues after the event.

## Error Handling

### Task Extraction Failure

If the system cannot confidently extract tasks, it should still respond helpfully by asking for a clearer next step and preserving the raw user message in the conversation.

### Safety Conflict

If a safe interrupt is triggered, all ordinary prioritization and focus guidance should be suppressed in that response.

### Persistence Failure

If SQLite writes fail, the backend should return a clear recoverable error and the frontend should show a non-technical retry message.

### Timer Desynchronization

If focus timer state becomes inconsistent between frontend and backend, backend state is the source of truth.

## Testing Strategy

The MVP should be tested at four levels:

### 1. Unit Tests

- priority scoring
- safety guard detection states
- focus session transitions
- analytics counters

### 2. API Tests

- message submission
- task list refresh
- focus start and complete flows
- safe interrupt response behavior

### 3. UI Integration Tests

- mixed layout renders correctly
- chat submission updates right-hand state
- focus session controls update the UI properly
- gentle nudge rendering appears only when triggered

### 4. Demo Regression Checks

A small set of seeded example prompts should be verified before presentation to ensure the main story always works.

## Out of Scope for This MVP

- real calendar and email sync
- rich multi-user collaboration
- advanced permissions and auth
- personalized adaptive prioritization based on long-term feedback
- model fine-tuning
- mobile app packaging

## Future Expansion Path

After the MVP, likely next steps are:

1. external integrations for calendar and inbox awareness
2. stronger structured task extraction
3. richer daily planning and review flows
4. better long-term learning from user feedback
5. production-ready safety policy refinement and localization

## Recommended Build Sequence

1. Backend foundation and SQLite schema
2. Task and priority services
3. Safety guard and analytics tracking
4. Focus service
5. Frontend mixed workspace UI
6. Frontend and backend integration
7. Demo prompt seeding and regression verification

## Acceptance Criteria

The MVP is considered successful when:

1. A user can input a realistic mixed task statement and receive a structured response.
2. The task list updates based on extracted tasks stored in SQLite.
3. The system ranks tasks and explains the top priority.
4. The user can start and complete a focus session in the web UI.
5. The interface shows pacing information without exposing risk metrics.
6. A gentle nudge appears only under defined conditions.
7. A safe interrupt overrides ordinary productivity responses when crisis language is entered.
8. The full demo loop can be completed reliably in a local environment.
