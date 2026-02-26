export interface AnalysisRequest {
  query: string;
  analysis_type: 'debug' | 'review' | 'refactor' | 'explain' | 'test_generate';
  code_location?: {
    file_path: string;
    line_start: number;
    line_end: number;
  };
  include_codebase?: boolean;
  stream?: boolean;
}

export interface SuggestedAction {
  action_type: 'edit' | 'create' | 'delete' | 'test' | 'pr_comment' | 'slack_notify';
  target_file: string;
  description: string;
  diff?: string;
  new_content?: string;
  reasoning: string;
  confidence: number;
}

export interface AnalysisResponse {
  summary: string;
  detailed_analysis: string;
  suggested_actions: SuggestedAction[];
  follow_up_questions: string[];
}