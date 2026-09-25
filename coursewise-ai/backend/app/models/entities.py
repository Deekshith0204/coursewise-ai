import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Text,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from ..database.session import Base


def generate_uuid():
    return str(uuid.uuid4())


def utc_now():
    return datetime.now(timezone.utc)


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(20), default="pdf")  # pdf, docx, pptx, txt, md
    mime_type = Column(String(120), default="application/pdf")
    file_size = Column(Integer, nullable=False)
    page_count = Column(Integer, default=0)
    slide_count = Column(Integer, default=0)
    section_count = Column(Integer, default=0)
    title = Column(String(255), nullable=True)
    status = Column(String(50), default="uploaded")  # uploaded, processing, processed, error
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    concepts = relationship("Concept", back_populates="document", cascade="all, delete-orphan")
    prerequisites = relationship("Prerequisite", back_populates="document", cascade="all, delete-orphan")
    summaries = relationship("Summary", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    heading = Column(String(255), nullable=True)
    text = Column(Text, nullable=False)
    source_type = Column(String(20), default="pdf")
    source_location = Column(String(100), default="Page 1")
    page_number = Column(Integer, nullable=True)
    slide_number = Column(Integer, nullable=True)
    section_name = Column(String(255), nullable=True)
    start_line = Column(Integer, nullable=True)
    end_line = Column(Integer, nullable=True)
    token_count = Column(Integer, default=0)
    embedding_json = Column(Text, nullable=True)  # JSON-encoded vector list

    document = relationship("Document", back_populates="chunks")


class Concept(Base):
    __tablename__ = "concepts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=False)
    source_pages_json = Column(Text, default="[]")  # e.g., ["Page 1", "Slide 5"]
    importance_score = Column(Float, default=0.5)
    created_at = Column(DateTime, default=utc_now)

    document = relationship("Document", back_populates="concepts")


class Prerequisite(Base):
    __tablename__ = "prerequisites"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    topic = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)
    source_pages_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=utc_now)

    document = relationship("Document", back_populates="prerequisites")


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=True)
    document_ids_json = Column(Text, default="[]")  # Multi-file support: list of IDs
    knowledge_level = Column(String(50), nullable=False)  # BEGINNER, INTERMEDIATE, ADVANCED
    summary_depth = Column(String(50), nullable=False)    # QUICK, STANDARD, DETAILED
    learning_preference = Column(String(50), default="CONCEPT FOCUSED")  # CONCEPT FOCUSED, EXAM FOCUSED, PRACTICAL FOCUSED
    title = Column(String(255), nullable=False)
    overview = Column(Text, nullable=False)
    full_content_json = Column(Text, nullable=False)      # JSON list of section objects
    document_wise_summary_json = Column(Text, default="[]") # JSON list of document-wise breakdown
    key_points_json = Column(Text, default="[]")         # JSON list of strings
    key_concepts_json = Column(Text, default="[]")       # JSON list of concept objects
    prerequisites_json = Column(Text, default="[]")      # JSON list of prerequisite objects
    response_time_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)

    document = relationship("Document", back_populates="summaries")
    sources = relationship("SummarySource", back_populates="summary", cascade="all, delete-orphan")
    evaluation = relationship("Evaluation", back_populates="summary", uselist=False, cascade="all, delete-orphan")


class SummarySource(Base):
    __tablename__ = "summary_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    summary_id = Column(String(36), ForeignKey("summaries.id", ondelete="CASCADE"), nullable=False)
    document_name = Column(String(255), nullable=True)
    chunk_id = Column(String(36), nullable=True)
    source_type = Column(String(20), default="pdf")  # pdf, docx, pptx, txt, md
    source_location = Column(String(100), default="Page 1")  # Page 5, Slide 12, Section: X, Lines 40-52
    page_number = Column(Integer, nullable=True)
    slide_number = Column(Integer, nullable=True)
    section_name = Column(String(255), nullable=True)
    snippet = Column(Text, nullable=False)

    summary = relationship("Summary", back_populates="sources")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    summary_id = Column(String(36), ForeignKey("summaries.id", ondelete="CASCADE"), nullable=False)
    compression_ratio = Column(Float, default=0.0)
    source_word_count = Column(Integer, default=0)
    summary_word_count = Column(Integer, default=0)
    user_rating = Column(Integer, nullable=True)
    feedback_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    summary = relationship("Summary", back_populates="evaluation")
