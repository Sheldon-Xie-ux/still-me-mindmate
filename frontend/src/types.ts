export type SafetyState = "none" | "gentle_nudge" | "safe_interrupt" | string;

export interface TaskItem {
  id: number;
  title: string;
  description?: string | null;
  category: string;
  priority_score: number;
  priority_label: string;
  priority_reason: string;
  status: string;
  due_date?: string | null;
  estimated_minutes?: number | null;
  created_at: string;
  updated_at: string;
}

export interface FocusRecommendation {
  recommended_task_id: number | null;
  summary: string;
}

export interface CurrentPriorityPayload {
  title: string;
  reason: string;
}

export interface NextActionPayload {
  label: string;
  detail: string;
}

export interface SystemObservationPayload {
  suggestion: string;
  safety_state: SafetyState;
  message: string | null;
}

export interface RhythmPayload {
  focus_minutes_today: number;
  completed_tasks_today: number;
  suggestion: string;
}

export interface SafetyPayload {
  state: SafetyState;
  message: string | null;
}

export interface ChatResponse {
  reply: string;
  current_priority?: CurrentPriorityPayload | null;
  next_action?: NextActionPayload | null;
  system_observation?: SystemObservationPayload | null;
  tasks: TaskItem[];
  focus: FocusRecommendation;
  rhythm: RhythmPayload;
  safety: SafetyPayload;
}

export interface FocusSession {
  id: number;
  task_id: number;
  duration_minutes: number;
  status: string;
  started_at: string;
  ended_at: string | null;
}

export interface ResearchQuestion {
  id: number;
  title: string;
  theme: string;
  description: string;
  status: string;
  priority: number;
  created_at: string;
  updated_at: string;
}

export interface ResearchRunCreateResponse {
  run_id: number;
  status: string;
  evidence_created: number;
  hypotheses_created: number;
  hypotheses_updated: number;
}

export interface SourceDocument {
  id: number;
  url: string;
  title: string;
  authors: string;
  publisher: string;
  published_at: string | null;
  language: string;
  source_type: string;
  snippet: string;
  credibility_score: number;
  retrieved_at: string;
}

export interface EvidenceCard {
  id: number;
  question_id: number;
  source_document_id: number;
  source: SourceDocument;
  claim: string;
  summary: string;
  stance: string;
  evidence_strength: number;
  relevance_score: number;
  risk_domain: string;
  limitations: string;
  created_at: string;
}

export interface Hypothesis {
  id: number;
  title: string;
  statement: string;
  theme: string;
  status: string;
  evidence_score: number;
  product_value_score: number;
  engineering_feasibility_score: number;
  risk_sensitivity_score: number;
  overall_score: number;
  rationale: string;
  created_at: string;
  updated_at: string;
}

export interface ResearchBrief {
  title: string;
  summary: string;
  strongest_claims: string[];
  open_questions: string[];
  design_implications: string[];
  expert_review_queue: string[];
}
