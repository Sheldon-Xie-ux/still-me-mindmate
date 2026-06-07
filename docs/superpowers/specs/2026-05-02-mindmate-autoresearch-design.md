# MindMate AutoResearch Design

## Overview

MindMate AutoResearch is a sustained research capability for studying human-AI deep collaboration in the AI-native era. It adapts the core idea from Andrej Karpathy's `autoresearch` project: a bounded loop that proposes an experiment, runs it, evaluates it with a stable metric, keeps useful progress, and records the rest.

For MindMate, the "experiment" is not a model-training run. It is an evidence-seeking research cycle:

1. Generate or select a research question about human-AI coexistence.
2. Search Chinese and international sources.
3. Extract evidence cards with citations and stance.
4. Form or update hypotheses.
5. Score hypotheses using stable research and product criteria.
6. Preserve high-value hypotheses as design principles, research briefs, or future product requirements.

The goal is to turn MindMate from a cognitive-health interaction prototype into a living research system. It should continuously study how AI collaboration may affect attention, judgment, learning, creativity, agency, education, and professional expertise, then translate that research into engineering guidance for future AI-native products.

## Product Positioning

MindMate already frames itself as cognitive health infrastructure for the AI era: "Harness AI. Keep yourself." AutoResearch extends that mission upstream. Instead of only measuring one user's behavior in a single AI session, it studies the wider scientific, educational, and industry evidence around human-AI collaboration.

The feature is a research assistant, not a medical diagnostic system and not an autonomous truth authority. It should help the team find, organize, compare, and operationalize evidence. It must keep source links visible and distinguish evidence-backed claims from speculation.

## Primary Users

### Founder / Product Researcher

Uses the system to track new AI cognition, education, safety, and human oversight research. The desired output is product strategy, design principles, pitch material, and a defensible research narrative.

### AI Product Engineer

Uses the system to convert evidence into concrete engineering patterns, such as intervention timing, explanation design, default answer structure, user reflection prompts, or child/education safeguards.

### Medical / Academic Advisor

Uses the system to inspect evidence quality, flag overclaiming, review wording boundaries, and decide which hypotheses deserve human expert review.

## Core Research Themes

The first version should focus on five durable themes:

1. Cognitive offloading and skill degradation
   - How AI assistance changes memory, reasoning, writing, search behavior, and professional skill maintenance.

2. Attention, judgment, and critical thinking
   - Whether fluent AI output reduces reading depth, independent verification, disagreement, and reflective judgment.

3. AI-native education and children
   - How students and younger generations learn in environments where AI can answer, write, summarize, and plan for them.

4. Human oversight and collaborative agency
   - How systems can keep humans meaningfully in the loop without creating fake oversight, fatigue, or ceremonial approval.

5. Engineering patterns for cognitive protection
   - Product designs that preserve effort, reflection, friction, authorship, learning, and user agency while still using AI effectively.

## MVP Outcome

The first implementation should let a user open a Research Lab module and:

1. See a queue of research questions.
2. Run one bounded research cycle manually.
3. View generated evidence cards with source metadata.
4. View hypotheses ranked by score.
5. Open a research run log showing what was searched, what was found, what changed, and what was rejected.
6. Read a concise weekly-style research brief generated from the current evidence base.

The MVP does not need full unattended crawling, paid scholarly databases, complex multi-agent orchestration, or production-grade scheduling. It should establish the loop, data model, evaluation rubric, and user-facing research surface.

## Product Architecture

### Frontend: Research Lab

Add a new Research Lab area to the existing React app. It should feel like a working research console rather than a marketing page.

Primary sections:

- Research Question Queue
- Current Research Run
- Evidence Cards
- Hypothesis Leaderboard
- Research Brief

The Research Lab should be dense, calm, and scannable. It should not use giant hero sections. The user is doing serious research work, so the design should prioritize source inspection, comparison, status, and traceability.

### Backend: Research Loop Service

Add a backend service layer that coordinates each research cycle:

- select or create research question
- build search queries in Chinese and English
- call source adapters
- normalize source results
- extract evidence cards
- update hypotheses
- score hypotheses
- write a research run log

The loop should be deterministic enough to test. AI model calls can be introduced behind interfaces, but the first version should include a fixture-backed path so tests and demos run without external API keys.

### Storage: SQLite Research Tables

Use the existing backend and SQLite foundation. Add tables for research questions, source documents, evidence cards, hypotheses, research runs, and design principles.

## Data Model

### ResearchQuestion

Fields:

- `id`
- `title`
- `theme`
- `description`
- `status`: `queued`, `active`, `archived`
- `priority`
- `created_at`
- `updated_at`

Example:

> How does frequent AI writing assistance affect students' independent argument formation?

### SourceDocument

Fields:

- `id`
- `url`
- `title`
- `authors`
- `publisher`
- `published_at`
- `language`: `zh`, `en`, or `other`
- `source_type`: `paper`, `news`, `blog`, `policy`, `report`, `social`, `unknown`
- `snippet`
- `credibility_score`
- `retrieved_at`

### EvidenceCard

Fields:

- `id`
- `question_id`
- `source_document_id`
- `claim`
- `summary`
- `stance`: `supports`, `weakly_supports`, `contradicts`, `context`, `unclear`
- `evidence_strength`: 0-100
- `relevance_score`: 0-100
- `risk_domain`: `attention`, `judgment`, `education`, `agency`, `skill`, `wellbeing`, `governance`
- `limitations`
- `created_at`

### Hypothesis

Fields:

- `id`
- `title`
- `statement`
- `theme`
- `status`: `candidate`, `promising`, `accepted`, `rejected`, `needs_expert_review`
- `evidence_score`: 0-100
- `product_value_score`: 0-100
- `engineering_feasibility_score`: 0-100
- `risk_sensitivity_score`: 0-100
- `overall_score`: 0-100
- `rationale`
- `created_at`
- `updated_at`

Example:

> AI collaboration systems should ask users to state an initial judgment before revealing a complete recommendation in high-stakes reasoning tasks.

### ResearchRun

Fields:

- `id`
- `question_id`
- `status`: `pending`, `running`, `completed`, `failed`
- `query_plan`
- `sources_examined`
- `evidence_created`
- `hypotheses_created`
- `hypotheses_updated`
- `kept_summary`
- `rejected_summary`
- `error_message`
- `started_at`
- `completed_at`

### DesignPrinciple

Fields:

- `id`
- `hypothesis_id`
- `title`
- `principle`
- `product_pattern`
- `applicability`
- `evidence_summary`
- `caution`
- `status`: `draft`, `reviewed`, `adopted`, `retired`
- `created_at`
- `updated_at`

Example:

> Require user judgment before AI recommendation in decisions where overreliance would be costly.

## Research Loop

### Step 1: Select Question

The first MVP can use a seeded queue of 10-20 research questions based on MindMate's current thesis:

- cognitive offloading
- attention collapse
- judgment outsourcing
- AI-native education
- children and AI tutors
- human oversight
- expertise degradation
- reflective friction
- AI answer anchoring
- productive constraints in AI UX

The user can manually start a run from one question.

### Step 2: Build Search Plan

For each question, generate Chinese and English query variants.

Example English queries:

- "AI cognitive offloading critical thinking study"
- "generative AI writing assistance student learning effects"
- "human AI collaboration overreliance automation bias"

Example Chinese queries:

- "生成式AI 认知外包 批判性思维 研究"
- "人工智能 写作辅助 学生 学习能力 影响"
- "人机协同 自动化偏差 人类监督"

The search plan should record what it tried, even when no good results are found.

### Step 3: Retrieve Sources

The MVP should support a small adapter interface:

- Web search adapter
- Fixture adapter for tests and offline demos
- Manual source adapter for user-provided URLs or pasted text

Future adapters can cover arXiv, Semantic Scholar, Crossref, Google Scholar-like sources where legally and technically available, Chinese academic/news sources, policy databases, Reddit/Hacker News, and organization blogs.

### Step 4: Extract Evidence Cards

Each source should produce zero or more evidence cards. Extraction must preserve uncertainty. A weak news article should not be treated like a controlled study.

The extractor should identify:

- claim
- source type
- study or argument summary
- population or context
- whether it supports or challenges the current hypothesis
- limitations
- relevance to MindMate product design

### Step 5: Update Hypotheses

The hypothesis engine clusters evidence into candidate claims. It should create new hypotheses when evidence points to a new engineering principle, and update existing hypotheses when new evidence supports, weakens, or complicates them.

Hypotheses should be written in a form that can influence product design, not only as academic statements.

Weak form:

> AI may hurt thinking.

Useful form:

> For decision tasks, delaying full AI recommendations until after the user states their own criteria may reduce anchoring and preserve judgment.

### Step 6: Score

Use a stable rubric:

- Evidence strength: quality, recency, source credibility, reproducibility, methodological fit
- Relevance: connection to human-AI collaboration and MindMate's cognitive-health thesis
- Product value: ability to shape a product feature or user-facing intervention
- Engineering feasibility: can this become a measurable or buildable feature
- Risk sensitivity: whether mishandling the principle could create harm, anxiety, surveillance, or overclaiming

Overall score can begin as:

`0.35 * evidence + 0.25 * relevance + 0.20 * product_value + 0.10 * feasibility + 0.10 * risk_sensitivity`

High risk sensitivity should not mean "safe to ship." It means the topic needs careful treatment and possibly expert review.

### Step 7: Keep, Reject, or Review

The loop should classify hypotheses:

- `accepted`: strong enough to become a draft design principle
- `promising`: worth tracking with more evidence
- `needs_expert_review`: important but medically, educationally, or ethically sensitive
- `rejected`: weak, redundant, unsupported, or outside scope

This mirrors Karpathy's keep-or-discard loop, but the artifact is a research claim rather than model code.

## Initial Seed Questions

1. Does AI writing assistance reduce independent argument formation in students?
2. When does AI summarization improve learning, and when does it reduce deep reading?
3. How does automation bias appear in LLM-assisted decision-making?
4. What product patterns preserve human oversight without creating rubber-stamp approval?
5. How should AI tools protect children from answer dependence while still supporting learning?
6. Can reflective prompts reduce overreliance on AI recommendations?
7. What signs indicate that AI collaboration is causing skill atrophy rather than skill amplification?
8. How should AI copilots expose uncertainty so users remain actively critical?
9. What does research say about cognitive offloading and memory formation in digital tools?
10. Which interface frictions improve learning without making AI tools feel punitive?

## API Design

### `GET /api/research/questions`

Returns the research question queue.

### `POST /api/research/runs`

Starts one bounded research run.

Request:

```json
{
  "question_id": 1,
  "mode": "fixture"
}
```

Response:

```json
{
  "run_id": 12,
  "status": "completed",
  "evidence_created": 6,
  "hypotheses_created": 2,
  "hypotheses_updated": 1
}
```

### `GET /api/research/runs/{run_id}`

Returns the run log and generated artifacts.

### `GET /api/research/evidence?question_id=1`

Returns evidence cards for a question.

### `GET /api/research/hypotheses`

Returns ranked hypotheses.

### `GET /api/research/brief`

Returns a current research brief summarizing top findings, open questions, and product implications.

## Frontend UX

### Research Question Queue

Shows each question with:

- theme
- status
- priority
- last run time
- evidence count
- top hypothesis count
- run button

### Current Research Run

Shows:

- selected question
- search plan
- source count
- evidence count
- hypothesis changes
- status timeline

For MVP, a run can complete synchronously. The UI should still be shaped as a run log so async execution can be added later.

### Evidence Cards

Each card shows:

- claim
- short source summary
- source link
- stance
- strength score
- relevance score
- limitations

Cards should clearly label whether a source is a peer-reviewed paper, policy report, news article, blog post, or unknown source.

### Hypothesis Leaderboard

Shows hypotheses ranked by overall score with:

- title
- statement
- status
- score breakdown
- supporting evidence count
- contradictory/context evidence count
- product implication

### Research Brief

A generated narrative summary:

- what changed in the latest run
- strongest current claims
- unsettled questions
- design implications for MindMate
- expert review queue

The brief should avoid medical certainty. It should use language like "evidence suggests," "early signal," "needs expert review," and "design implication," not "proves" or "diagnoses."

## Source Quality Rules

The system should not flatten all sources into one credibility tier.

Initial source scoring:

- Peer-reviewed paper or major academic venue: high baseline
- Preprint: medium-high baseline with review caveat
- Policy report from credible institution: medium-high baseline
- Reputable technical organization blog: medium baseline
- News article: medium or low depending on sourcing
- Social media discussion: low baseline, useful for detecting lived concerns or language, not for causal claims
- Unknown source: low baseline

The score can be adjusted by recency, specificity, author/institution credibility, and whether the source directly addresses the research question.

## Safety and Ethics Boundaries

AutoResearch must not imply that MindMate can diagnose cognitive decline, mental illness, learning disability, or neurological harm.

The system should:

- distinguish research synthesis from clinical advice
- flag medically sensitive claims for expert review
- avoid fear-based wording
- avoid turning cognitive health into employee surveillance
- preserve privacy by design when later connected to real user behavior
- treat children and education topics as high-sensitivity domains

## Testing Strategy

Backend tests:

- research question seeding
- fixture research run creates evidence cards
- hypothesis scoring is deterministic
- run log records kept and rejected artifacts
- sensitive topics can be marked `needs_expert_review`
- source credibility affects evidence strength

Frontend tests:

- Research Lab renders queue, evidence, hypotheses, and brief
- user can start a fixture-backed research run
- evidence card source labels are visible
- hypothesis score breakdown is visible
- empty states render before the first run

Manual verification:

- run backend tests
- run frontend tests
- start backend and frontend locally
- run one fixture research cycle from the browser
- inspect that all generated claims have visible sources and limitations

## Future Expansion

After the MVP, the system can grow in these directions:

1. Scheduled daily or weekly research runs.
2. Real web search with domain allowlists and source-type filters.
3. Multi-agent review: searcher, skeptic, synthesizer, product translator, medical-boundary reviewer.
4. Exportable weekly research reports for advisors, investors, and internal strategy.
5. Design principle library connected to MindMate feature specs.
6. Human expert review workflow for medical, educational, and child-safety claims.
7. Browser extension or sidecar integration that links live product metrics with the research knowledge base.

## Implementation Boundary

The first build should be deliberately narrow:

- use existing React + Vite frontend
- use existing FastAPI + SQLite backend
- add fixture-backed sources before live search
- implement one manual research run endpoint
- seed 10 research questions
- create evidence and hypothesis views
- generate a simple brief from stored data

Do not implement background cron jobs, unbounded crawling, paid database integrations, or a fully autonomous multi-agent organization in the first pass.

## Success Criteria

The feature is successful when:

1. The user can run a bounded research cycle from the web app.
2. The system produces source-linked evidence cards.
3. The system produces scored hypotheses related to human-AI coexistence.
4. The highest-scoring hypotheses translate into concrete MindMate design implications.
5. Sensitive claims are clearly marked for expert review instead of overclaimed.
6. The run log makes the AI research process inspectable rather than magical.

## Relationship to Karpathy Autoresearch

Karpathy's `autoresearch` demonstrates that autonomous research becomes practical when the loop is constrained: one editable surface, one runtime budget, one metric, and clear keep-or-discard behavior.

MindMate AutoResearch keeps that discipline but changes the research object:

- editable surface: research questions, extraction prompts, scoring rubric, and source adapters
- runtime budget: one bounded research run
- metric: evidence strength, relevance, product value, feasibility, and risk sensitivity
- keep-or-discard object: hypotheses and design principles

The result is not an autonomous scientist. It is a disciplined research engine that helps MindMate learn continuously while keeping human review and evidence traceability at the center.
