// API types — mirror the backend response schemas.

export type Dimension =
  | "Engineering Fundamentals"
  | "Problem Solving"
  | "AI Fluency"
  | "Agentic Engineering"
  | "Practical Reasoning"
  | "Communication";

export type QuestionFormat =
  | "written"
  | "scenario"
  | "multiple_choice"
  | "code_review"
  | "debugging"
  | "practical_reasoning"
  | "agent_instruction";

export type AssessmentStatus =
  | "created"
  | "in_progress"
  | "completing"
  | "completed"
  | "failed";

export type ReadinessClassification = "Ready" | "Developing" | "Emerging" | "Foundational";

export type Pathway =
  | "Ready"
  | "Targeted Capability Development"
  | "Structured Capability Development"
  | "Foundation Development";

export interface Project {
  name: string;
  description?: string;
  technologies?: string[];
  url?: string | null;
}

export interface Profile {
  user_id: string;
  name?: string | null;
  education?: string | null;
  graduation_year?: number | null;
  experience?: string | null;
  target_role?: string | null;
  technical_skills: string[];
  projects: Project[];
  ai_tools: string[];
  github?: string | null;
  linkedin?: string | null;
  professional_links: string[];
  background?: string | null;
  resume_parsed: boolean;
  resume_path?: string | null;
}

export interface ResumeParseResult {
  profile: Profile;
  extracted_fields: string[];
}

export interface QuestionOption {
  id: string;
  text: string;
}

export interface Question {
  id: string;
  dimension: Dimension;
  format: QuestionFormat;
  prompt: string;
  context?: string | null;
  options: QuestionOption[];
  sequence: number;
}

export interface AssessmentState {
  id: string;
  status: AssessmentStatus;
  answered_count: number;
  max_questions: number;
  current_question: Question | null;
  dimensions_covered: Dimension[];
  completed: boolean;
  completed_at?: string | null;
  processing_label?: string | null;
}

export interface AssessmentSummary {
  id: string;
  status: AssessmentStatus;
  created_at: string;
  completed_at?: string | null;
  overall_score?: number | null;
  classification?: string | null;
  pathway?: string | null;
}

export interface DimensionResult {
  dimension: Dimension;
  score: number;
  classification: ReadinessClassification;
  strengths: string[];
  gaps: string[];
  summary: string;
}

export interface Recommendation {
  pathway: Pathway;
  rationale: string;
  capability_areas: string[];
  next_action: string;
  learning_priorities: string[];
}

export interface EvidenceItem {
  statement: string;
  supports: string;
}

export interface ReadinessResult {
  overall_score: number;
  classification: ReadinessClassification;
  dimension_results: DimensionResult[];
  key_strengths: string[];
  capability_gaps: string[];
  summary: string;
  recommendation: Recommendation;
  evidence: EvidenceItem[];
  completed_at: string;
}

export interface AssessmentReport {
  assessment_id: string;
  title: string;
  summary: string;
  readiness: {
    overall_score: number;
    classification: string;
    dimensions: DimensionResult[];
  };
  strengths: string[];
  development_areas: string[];
  evidence: EvidenceItem[];
  recommended_pathway: Recommendation;
  learning_priorities: string[];
  created_at: string;
}

export interface ApiError {
  error: { code: string; message: string };
}
