export type KnowledgeLevel = 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';
export type SummaryDepth = 'QUICK' | 'STANDARD' | 'DETAILED';
export type LearningPreference = 'CONCEPT FOCUSED' | 'EXAM FOCUSED' | 'PRACTICAL FOCUSED';

export type FileType = 'pdf' | 'docx' | 'pptx' | 'txt' | 'md';

export interface DocumentInfo {
  id: string;
  filename: string;
  original_filename: string;
  file_type: FileType | string;
  mime_type?: string | null;
  file_size: number;
  page_count: number;
  slide_count: number;
  section_count: number;
  title: string | null;
  status: 'uploaded' | 'processing' | 'processed' | 'error';
  error_message?: string | null;
  created_at: string;
  chunks_count?: number;
  concepts_count?: number;
  prerequisites_count?: number;
  summaries_count?: number;
}

export interface ConceptItem {
  id?: string;
  name: string;
  explanation: string;
  source_pages: string[];
  importance_score: number;
}

export interface PrerequisiteItem {
  id?: string;
  topic: string;
  name: string;
  reason: string;
  source_pages: string[];
}

export interface SummarySection {
  heading: string;
  content: string;
  source_pages: string[];
}

export interface DocumentSummaryItem {
  document_id: string;
  document_name: string;
  file_type: string;
  summary: string;
}

export interface SummarySourceItem {
  chunk_id?: string;
  document_name?: string;
  source_type: string;
  source_location: string;
  page_number?: number | null;
  slide_number?: number | null;
  section_name?: string | null;
  snippet: string;
}

export interface EvaluationResponse {
  compression_ratio: number;
  source_word_count: number;
  summary_word_count: number;
  user_rating?: number | null;
  feedback_notes?: string | null;
}

export interface SummaryResponse {
  id: string;
  document_id?: string | null;
  document_ids: string[];
  document_title: string;
  file_types: string[];
  is_multi_document: boolean;
  knowledge_level: KnowledgeLevel;
  summary_depth: SummaryDepth;
  learning_preference: LearningPreference;
  title: string;
  overview: string;
  document_wise_summaries: DocumentSummaryItem[];
  sections: SummarySection[];
  key_points: string[];
  key_concepts: ConceptItem[];
  prerequisites: PrerequisiteItem[];
  sources: SummarySourceItem[];
  response_time_ms: number;
  created_at: string;
  evaluation?: EvaluationResponse | null;
}

export interface SummaryHistoryItem {
  id: string;
  document_id?: string | null;
  document_name: string;
  file_type: string;
  file_types: string[];
  is_multi_document: boolean;
  title: string;
  knowledge_level: KnowledgeLevel;
  summary_depth: SummaryDepth;
  learning_preference: LearningPreference;
  created_at: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  app_name: string;
  ai_configured: boolean;
  ai_provider: string;
  ai_model: string;
  supported_formats: string[];
}

export interface AIConfigInfo {
  configured: boolean;
  provider: string;
  model: string;
  base_url: string;
  masked_key: string;
}
