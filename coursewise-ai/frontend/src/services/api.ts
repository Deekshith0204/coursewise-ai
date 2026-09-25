import {
  DocumentInfo,
  SummaryResponse,
  SummaryHistoryItem,
  ConceptItem,
  PrerequisiteItem,
  HealthResponse,
  AIConfigInfo,
  KnowledgeLevel,
  SummaryDepth,
  LearningPreference
} from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' ? '/api' : 'http://127.0.0.1:8000/api');

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Accept': 'application/json',
        ...(options?.headers || {}),
      },
    });

    if (!response.ok) {
      let errorMessage = `API request failed (${response.status})`;
      try {
        const rawText = await response.text();
        try {
          const errorData = JSON.parse(rawText);
          if (errorData && errorData.detail) {
            errorMessage = typeof errorData.detail === 'string' 
              ? errorData.detail 
              : JSON.stringify(errorData.detail);
          } else if (rawText) {
            errorMessage = rawText;
          }
        } catch {
          if (rawText) errorMessage = rawText;
        }
      } catch {
        // Stream read failed
      }
      throw new Error(errorMessage);
    }

    return response.json();
  }

  async getHealth(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health');
  }

  async getConfig(): Promise<AIConfigInfo> {
    return this.request<AIConfigInfo>('/health/config');
  }

  async updateConfig(payload: { api_key: string; model?: string; base_url?: string; provider?: string }): Promise<AIConfigInfo> {
    return this.request<AIConfigInfo>('/health/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  }

  async listDocuments(): Promise<DocumentInfo[]> {
    return this.request<DocumentInfo[]>('/documents');
  }

  async uploadDocuments(files: File[]): Promise<{ document_id: string; filename: string; file_type: string; page_count: number; slide_count: number; section_count: number; file_size: number }[]> {
    const formData = new FormData();
    for (const file of files) {
      formData.append('files', file);
    }

    const response = await fetch(`${API_BASE_URL}/documents/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Upload failed');
    }

    return response.json();
  }

  // Backward-compatible single document upload
  async uploadDocument(file: File) {
    const results = await this.uploadDocuments([file]);
    return results[0];
  }

  async getDocument(documentId: string): Promise<DocumentInfo> {
    return this.request<DocumentInfo>(`/documents/${documentId}`);
  }

  async deleteDocument(documentId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/documents/${documentId}`, {
      method: 'DELETE',
    });
  }

  async processDocument(documentId: string): Promise<{ status: string; chunks_created: number; concepts_found: number; prerequisites_found: number }> {
    return this.request<{ status: string; chunks_created: number; concepts_found: number; prerequisites_found: number }>(
      `/documents/${documentId}/process`,
      { method: 'POST' }
    );
  }

  async generateSummary(
    documentIds: string | string[],
    knowledgeLevel: KnowledgeLevel,
    summaryDepth: SummaryDepth,
    learningPreference: LearningPreference
  ): Promise<SummaryResponse> {
    const docIds = Array.isArray(documentIds) ? documentIds : [documentIds];
    return this.request<SummaryResponse>('/summaries/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        document_ids: docIds,
        knowledge_level: knowledgeLevel,
        summary_depth: summaryDepth,
        learning_preference: learningPreference,
      }),
    });
  }

  async getSummary(summaryId: string): Promise<SummaryResponse> {
    return this.request<SummaryResponse>(`/summaries/${summaryId}`);
  }

  async getHistory(): Promise<SummaryHistoryItem[]> {
    return this.request<SummaryHistoryItem[]>('/summaries/history');
  }

  async deleteSummary(summaryId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/summaries/${summaryId}`, {
      method: 'DELETE',
    });
  }

  async getConcepts(documentId: string): Promise<ConceptItem[]> {
    return this.request<ConceptItem[]>(`/concepts/${documentId}`);
  }

  async getPrerequisites(documentId: string): Promise<PrerequisiteItem[]> {
    return this.request<PrerequisiteItem[]>(`/prerequisites/${documentId}`);
  }

  async rateSummary(summaryId: string, rating: number, feedbackNotes?: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/summaries/${summaryId}/rate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        rating,
        feedback_notes: feedbackNotes,
      }),
    });
  }
}

export const api = new ApiService();
