import json
import time
import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ..models.entities import (
    Document,
    DocumentChunk,
    Summary,
    SummarySource,
    Evaluation
)
from ..schemas.schemas import (
    SummaryResponse,
    SummarySection,
    ConceptItem,
    PrerequisiteItem,
    SummarySourceItem,
    DocumentSummaryItem,
    EvaluationResponse,
    SummaryHistoryItem
)
from .ai_service import ai_service, AIConfigurationError, AIServiceError

logger = logging.getLogger(__name__)


class SummaryService:
    @classmethod
    async def generate_summary(
        cls,
        db: Session,
        document_ids: List[str],
        knowledge_level: str,
        summary_depth: str,
        learning_preference: str
    ) -> SummaryResponse:
        """
        Orchestrate personalized summary generation across one or more documents.
        """
        if not document_ids:
            raise ValueError("No document IDs provided for summary generation.")

        # Check if AI provider is configured
        if not ai_service.is_configured():
            raise AIConfigurationError(
                "AI provider not configured. Please set AI_API_KEY in backend/.env to generate summaries."
            )

        docs = db.query(Document).filter(Document.id.in_(document_ids)).all()
        if not docs:
            raise ValueError(f"No documents found matching IDs: {document_ids}")

        doc_dict = {d.id: d for d in docs}
        is_multi_doc = len(docs) > 1

        # Retrieve chunks for all selected documents
        db_chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id.in_(document_ids))
            .order_by(DocumentChunk.document_id, DocumentChunk.chunk_index.asc())
            .all()
        )

        if not db_chunks:
            raise ValueError("The selected documents have no processed text chunks. Please process them first.")

        # Format chunk data with document attribution
        chunks_data = []
        for c in db_chunks:
            parent_doc = doc_dict.get(c.document_id)
            doc_name = parent_doc.original_filename if parent_doc else "Document"
            chunks_data.append({
                "id": c.id,
                "document_id": c.document_id,
                "document_name": doc_name,
                "source_type": c.source_type or parent_doc.file_type if parent_doc else "pdf",
                "source_location": c.source_location or f"Page {c.page_number or 1}",
                "page_number": c.page_number,
                "slide_number": c.slide_number,
                "section_name": c.section_name or c.heading,
                "heading": c.heading or "Content Section",
                "text": c.text
            })

        start_time = time.time()

        overall_title = (
            f"Course Collection Summary: {', '.join(d.original_filename for d in docs[:3])}"
            if is_multi_doc
            else (docs[0].title or docs[0].original_filename)
        )

        # Invoke AI generation
        ai_result = await ai_service.generate_personalized_summary(
            document_title=overall_title,
            chunks=chunks_data,
            knowledge_level=knowledge_level,
            summary_depth=summary_depth,
            learning_preference=learning_preference,
            is_multi_document=is_multi_doc,
            document_names=[d.original_filename for d in docs]
        )

        response_time_ms = int((time.time() - start_time) * 1000)

        # Extract structured fields
        summary_title = ai_result.get("title", overall_title)
        overview = ai_result.get("overview", "")
        doc_wise_data = ai_result.get("document_wise_summaries", [])
        sections_data = ai_result.get("sections", [])
        key_points = ai_result.get("key_points", [])
        key_concepts = ai_result.get("key_concepts", [])
        prerequisites = ai_result.get("prerequisites", [])
        sources_data = ai_result.get("sources", [])

        # Persist Summary
        summary_id = str(uuid.uuid4())
        summary_obj = Summary(
            id=summary_id,
            document_id=docs[0].id,
            document_ids_json=json.dumps([d.id for d in docs]),
            knowledge_level=knowledge_level,
            summary_depth=summary_depth,
            learning_preference=learning_preference,
            title=summary_title,
            overview=overview,
            full_content_json=json.dumps(sections_data),
            document_wise_summary_json=json.dumps(doc_wise_data),
            key_points_json=json.dumps(key_points),
            key_concepts_json=json.dumps(key_concepts),
            prerequisites_json=json.dumps(prerequisites),
            response_time_ms=response_time_ms
        )
        db.add(summary_obj)

        # Persist Sources with specific document attribution
        for s in sources_data:
            doc_name = s.get("document_name") or docs[0].original_filename
            src_type = s.get("source_type", "pdf")
            src_loc = s.get("source_location") or "Source Ref"
            source_obj = SummarySource(
                id=str(uuid.uuid4()),
                summary_id=summary_id,
                document_name=doc_name,
                chunk_id=s.get("chunk_id"),
                source_type=src_type,
                source_location=src_loc,
                page_number=int(s.get("page_number", 1)) if s.get("page_number") else None,
                slide_number=int(s.get("slide_number", 1)) if s.get("slide_number") else None,
                section_name=s.get("section_name", src_loc),
                snippet=s.get("snippet", "")[:600]
            )
            db.add(source_obj)

        # Compute evaluation metrics
        source_words = sum(len(c.text.split()) for c in db_chunks)
        summary_words = (
            len(overview.split())
            + sum(len(d.get("summary", "").split()) for d in doc_wise_data)
            + sum(len(sec.get("content", "").split()) for sec in sections_data)
        )
        compression_ratio = round(summary_words / max(1, source_words), 3)

        evaluation_obj = Evaluation(
            id=str(uuid.uuid4()),
            summary_id=summary_id,
            compression_ratio=compression_ratio,
            source_word_count=source_words,
            summary_word_count=summary_words
        )
        db.add(evaluation_obj)

        db.commit()
        db.refresh(summary_obj)

        return cls._to_response_schema(db, summary_obj, docs)

    @classmethod
    def get_summary(cls, db: Session, summary_id: str) -> Optional[SummaryResponse]:
        """Fetch a summary by ID."""
        summary_obj = db.query(Summary).filter(Summary.id == summary_id).first()
        if not summary_obj:
            return None

        # Fetch associated docs
        doc_ids = json.loads(summary_obj.document_ids_json or "[]")
        if not doc_ids and summary_obj.document_id:
            doc_ids = [summary_obj.document_id]

        docs = db.query(Document).filter(Document.id.in_(doc_ids)).all()
        return cls._to_response_schema(db, summary_obj, docs)

    @classmethod
    def list_history(cls, db: Session) -> List[SummaryHistoryItem]:
        """List past summaries for history dashboard."""
        summaries = (
            db.query(Summary)
            .order_by(Summary.created_at.desc())
            .all()
        )
        history = []
        for s in summaries:
            doc_ids = json.loads(s.document_ids_json or "[]")
            if not doc_ids and s.document_id:
                doc_ids = [s.document_id]

            docs = db.query(Document).filter(Document.id.in_(doc_ids)).all()
            if len(docs) > 1:
                doc_name = f"Collection ({len(docs)} files: {', '.join(d.original_filename for d in docs[:2])}...)"
                primary_file_type = "collection"
                file_types = list({d.file_type or "pdf" for d in docs})
                is_multi = True
            elif len(docs) == 1:
                doc_name = docs[0].original_filename
                primary_file_type = docs[0].file_type or "pdf"
                file_types = [primary_file_type]
                is_multi = False
            else:
                doc_name = "Course Document"
                primary_file_type = "pdf"
                file_types = ["pdf"]
                is_multi = False

            history.append(
                SummaryHistoryItem(
                    id=s.id,
                    document_id=s.document_id,
                    document_name=doc_name,
                    file_type=primary_file_type,
                    file_types=file_types,
                    is_multi_document=is_multi,
                    title=s.title,
                    knowledge_level=s.knowledge_level,
                    summary_depth=s.summary_depth,
                    learning_preference=s.learning_preference,
                    created_at=s.created_at
                )
            )
        return history

    @classmethod
    def delete_summary(cls, db: Session, summary_id: str) -> bool:
        """Delete a summary from history."""
        summary_obj = db.query(Summary).filter(Summary.id == summary_id).first()
        if not summary_obj:
            return False
        db.delete(summary_obj)
        db.commit()
        return True

    @classmethod
    def _to_response_schema(
        cls,
        db: Session,
        s: Summary,
        docs: List[Document]
    ) -> SummaryResponse:
        """Convert database entity to API response schema."""
        raw_sections = json.loads(s.full_content_json or "[]")
        sections = [
            SummarySection(
                heading=sec.get("heading", "Section"),
                content=sec.get("content", ""),
                source_pages=[str(p) for p in sec.get("source_pages", [])]
            )
            for sec in raw_sections
        ]

        raw_doc_summaries = json.loads(s.document_wise_summary_json or "[]")
        doc_summaries = [
            DocumentSummaryItem(
                document_id=d.get("document_id", ""),
                document_name=d.get("document_name", "Document"),
                file_type=d.get("file_type", "pdf"),
                summary=d.get("summary", "")
            )
            for d in raw_doc_summaries
        ]

        key_points = json.loads(s.key_points_json or "[]")
        raw_concepts = json.loads(s.key_concepts_json or "[]")
        key_concepts = [
            ConceptItem(
                name=c.get("name", "Concept"),
                explanation=c.get("explanation", ""),
                source_pages=[str(p) for p in c.get("source_pages", [])],
                importance_score=c.get("importance_score", 0.5)
            )
            for c in raw_concepts
        ]

        raw_prereqs = json.loads(s.prerequisites_json or "[]")
        prerequisites = [
            PrerequisiteItem(
                topic=p.get("topic", "Topic"),
                name=p.get("name", "Prerequisite"),
                reason=p.get("reason", ""),
                source_pages=[str(p) for p in p.get("source_pages", [])]
            )
            for p in raw_prereqs
        ]

        sources = [
            SummarySourceItem(
                chunk_id=src.chunk_id,
                document_name=src.document_name,
                source_type=src.source_type or "pdf",
                source_location=src.source_location or f"Page {src.page_number or 1}",
                page_number=src.page_number,
                slide_number=src.slide_number,
                section_name=src.section_name or "Source Reference",
                snippet=src.snippet
            )
            for src in s.sources
        ]

        eval_resp = None
        if s.evaluation:
            eval_resp = EvaluationResponse(
                compression_ratio=s.evaluation.compression_ratio,
                source_word_count=s.evaluation.source_word_count,
                summary_word_count=s.evaluation.summary_word_count,
                user_rating=s.evaluation.user_rating,
                feedback_notes=s.evaluation.feedback_notes
            )

        is_multi = len(docs) > 1
        doc_title = (
            f"Collection ({len(docs)} documents: {', '.join(d.original_filename for d in docs)})"
            if is_multi
            else (docs[0].original_filename if docs else "Course Document")
        )
        file_types = list({d.file_type or "pdf" for d in docs})

        return SummaryResponse(
            id=s.id,
            document_id=s.document_id,
            document_ids=[d.id for d in docs],
            document_title=doc_title,
            file_types=file_types,
            is_multi_document=is_multi,
            knowledge_level=s.knowledge_level,
            summary_depth=s.summary_depth,
            learning_preference=s.learning_preference,
            title=s.title,
            overview=s.overview,
            document_wise_summaries=doc_summaries,
            sections=sections,
            key_points=key_points,
            key_concepts=key_concepts,
            prerequisites=prerequisites,
            sources=sources,
            response_time_ms=s.response_time_ms,
            created_at=s.created_at,
            evaluation=eval_resp
        )
