import { api } from "./api";
import type {
  AssessmentReport,
  AssessmentState,
  AssessmentSummary,
  Profile,
  ReadinessResult,
  ResumeParseResult,
} from "@/types";

export const client = {
  // Profile
  getProfile: () => api.get<Profile>("/api/v1/profile"),
  updateProfile: (data: Partial<Profile>) => api.put<Profile>("/api/v1/profile", data),

  // Resume
  uploadResume: (file: File) => api.upload<ResumeParseResult>("/api/v1/resume", file),
  reparseResume: () => api.post<ResumeParseResult>("/api/v1/resume/parse"),

  // Assessments
  listAssessments: () => api.get<AssessmentSummary[]>("/api/v1/assessments"),
  startAssessment: (introduction?: string) =>
    api.post<AssessmentState>("/api/v1/assessments", { introduction }),
  getAssessment: (id: string) => api.get<AssessmentState>(`/api/v1/assessments/${id}`),
  submitResponse: (
    id: string,
    data: { question_id?: string; text?: string; selected_option_id?: string; submission_key?: string; duration_seconds?: number }
  ) => api.post<AssessmentState>(`/api/v1/assessments/${id}/responses`, data),
  getResult: (id: string) => api.get<ReadinessResult>(`/api/v1/assessments/${id}/result`),
  getReport: (id: string) => api.get<AssessmentReport>(`/api/v1/assessments/${id}/report`),
};
