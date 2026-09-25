from datetime import datetime
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# --- Health & Config ---
class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.1.0"
    app_name: str = "CourseWise AI"
    ai_configured: bool = False
    ai_provider: str = "none"
    ai_model: str = ""
    supported_formats: List[str] = Field(default_factory=lambda: ["pdf", "docx", "pptx", "txt", "md"])


# --- Document Schemas ---
class DocumentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    original_filename: str
    file_type: str = "pdf"
    mime_type: Optional[str] = None
    file_size: int
    page_count: int = 0
    slide_count: int = 0
    section_count: int = 0
    title: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime


class DocumentDetailResponse(DocumentBase):
    chunks_count: int = 0
    concepts_count: int = 0
    prerequisites_count: int = 0
    summaries_count: int = 0


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    file_size: int
    page_count: int = 0
    slide_count: int = 0
    section_count: int = 0
    status: str = "uploaded"
    message: str


class DocumentProcessResponse(BaseModel):
    document_id: str
    filename: str = ""
    file_type: str = "pdf"
    status: str
    units_count: int = 0
    unit_label: str = "units"
    chunks_created: int
    concepts_found: int
    prerequisites_found: int
    message: str


# --- Concept & Prerequisite Schemas ---
class ConceptItem(BaseModel):
    id: Optional[str] = None
    name: str
    explanation: str
    source_pages: List[str] = Field(default_factory=list)  # can be "Page 1", "Slide 5", etc.
    importance_score: float = 0.5


class PrerequisiteItem(BaseModel):
    id: Optional[str] = None
    topic: str
    name: str
    reason: str
    source_pages: List[str] = Field(default_factory=list)


# --- Summary Schemas ---
KnowledgeLevel = Literal["BEGINNER", "INTERMEDIATE", "ADVANCED"]
SummaryDepth = Literal["QUICK", "STANDARD", "DETAILED"]
LearningPreference = Literal["CONCEPT FOCUSED", "EXAM FOCUSED", "PRACTICAL FOCUSED"]


class SummaryGenerateRequest(BaseModel):
    document_ids: Optional[List[str]] = None
    document_id: Optional[str] = None  # backward compatibility
    knowledge_level: KnowledgeLevel = "INTERMEDIATE"
    summary_depth: SummaryDepth = "STANDARD"
    learning_preference: LearningPreference = "CONCEPT FOCUSED"


class SummarySection(BaseModel):
    heading: str
    content: str
    source_pages: List[str] = Field(default_factory=list)


class DocumentSummaryItem(BaseModel):
    document_id: str
    document_name: str
    file_type: str
    summary: str


class SummarySourceItem(BaseModel):
    chunk_id: Optional[str] = None
    document_name: Optional[str] = None
    source_type: str = "pdf"
    source_location: str = "Page 1"
    page_number: Optional[int] = None
    slide_number: Optional[int] = None
    section_name: Optional[str] = "Source Section"
    snippet: str


class EvaluationResponse(BaseModel):
    compression_ratio: float
    source_word_count: int
    summary_word_count: int
    user_rating: Optional[int] = None
    feedback_notes: Optional[str] = None


class SummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: Optional[str] = None
    document_ids: List[str] = Field(default_factory=list)
    document_title: str
    file_types: List[str] = Field(default_factory=list)
    is_multi_document: bool = False
    knowledge_level: str
    summary_depth: str
    learning_preference: str
    title: str
    overview: str
    document_wise_summaries: List[DocumentSummaryItem] = Field(default_factory=list)
    sections: List[SummarySection] = Field(default_factory=list)
    key_points: List[str] = Field(default_factory=list)
    key_concepts: List[ConceptItem] = Field(default_factory=list)
    prerequisites: List[PrerequisiteItem] = Field(default_factory=list)
    sources: List[SummarySourceItem] = Field(default_factory=list)
    response_time_ms: int = 0
    created_at: datetime
    evaluation: Optional[EvaluationResponse] = None


class SummaryHistoryItem(BaseModel):
    id: str
    document_id: Optional[str] = None
    document_name: str
    file_type: str = "pdf"
    file_types: List[str] = Field(default_factory=list)
    is_multi_document: bool = False
    title: str
    knowledge_level: str
    summary_depth: str
    learning_preference: str
    created_at: datetime


class EvaluationRateRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    feedback_notes: Optional[str] = None


class ConfigUpdateRequest(BaseModel):
    api_key: str
    model: Optional[str] = "gemini-1.5-flash"
    base_url: Optional[str] = None
    provider: Optional[str] = "openai"
