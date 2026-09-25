import os
import uuid
import re
from pathlib import Path
from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from ...database.session import get_db, DATA_DIR
from ...models.entities import Document, DocumentChunk, Concept, Prerequisite
from ...schemas.schemas import (
    DocumentUploadResponse,
    DocumentDetailResponse,
    DocumentProcessResponse
)
from ...document_processing.document_normalizer import DocumentNormalizer, SUPPORTED_EXTENSIONS
from ...document_processing.base_parser import DocumentParsingError
from ...services.chunking_service import ChunkingService
from ...services.embedding_service import embedding_service
from ...services.concept_service import ConceptService
from ...services.prerequisite_service import PrerequisiteService

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOADS_DIR = DATA_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal or invalid characters."""
    base = os.path.basename(filename)
    clean = re.sub(r"[^a-zA-Z0-9_.-]", "_", base)
    return clean[:100] if clean else "document.dat"


@router.post("/upload", response_model=List[DocumentUploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_documents(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Validate and upload one or more course materials (.pdf, .docx, .pptx, .txt, .md).
    Processes file type detection, saves securely, and creates database records.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided for upload."
        )

    results: List[DocumentUploadResponse] = []

    for file in files:
        ext = Path(file.filename).suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type '{ext}'. Supported formats: PDF, DOCX, PPTX, TXT."
            )

        content = await file.read()
        file_size = len(content)

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The uploaded file '{file.filename}' is empty (0 bytes)."
            )

        if file_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File '{file.filename}' exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB."
            )

        doc_id = str(uuid.uuid4())
        safe_name = sanitize_filename(file.filename)
        file_type = DocumentNormalizer.get_file_type(file.filename)
        mime_type = DocumentNormalizer.get_mime_type(file.filename)
        stored_filename = f"{doc_id}_{safe_name}"
        file_path = UPLOADS_DIR / stored_filename

        # Save to disk
        with open(file_path, "wb") as f:
            f.write(content)

        # Quick probe parse to validate file integrity
        try:
            norm_doc = DocumentNormalizer.parse_document(str(file_path), file.filename)
            doc_title = norm_doc.title
            page_count = norm_doc.total_units if norm_doc.unit_label == "pages" else 0
            slide_count = norm_doc.total_units if norm_doc.unit_label == "slides" else 0
            section_count = norm_doc.total_units if norm_doc.unit_label in ["sections", "lines"] else 0
        except DocumentParsingError as e:
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
        except Exception as e:
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to process '{file.filename}': {str(e)}")

        doc_obj = Document(
            id=doc_id,
            filename=stored_filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_type=file_type,
            mime_type=mime_type,
            file_size=file_size,
            page_count=page_count,
            slide_count=slide_count,
            section_count=section_count,
            title=doc_title,
            status="uploaded"
        )
        db.add(doc_obj)
        db.commit()
        db.refresh(doc_obj)

        results.append(
            DocumentUploadResponse(
                document_id=doc_obj.id,
                filename=doc_obj.original_filename,
                file_type=doc_obj.file_type,
                file_size=doc_obj.file_size,
                page_count=doc_obj.page_count,
                slide_count=doc_obj.slide_count,
                section_count=doc_obj.section_count,
                status="uploaded",
                message=f"'{file.filename}' uploaded and verified successfully."
            )
        )

    return results


@router.get("", response_model=List[DocumentDetailResponse])
def list_documents(db: Session = Depends(get_db)):
    """List all course material documents currently stored."""
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return [
        DocumentDetailResponse(
            id=doc.id,
            filename=doc.filename,
            original_filename=doc.original_filename,
            file_type=doc.file_type or "pdf",
            mime_type=doc.mime_type,
            file_size=doc.file_size,
            page_count=doc.page_count or 0,
            slide_count=doc.slide_count or 0,
            section_count=doc.section_count or 0,
            title=doc.title,
            status=doc.status,
            error_message=doc.error_message,
            created_at=doc.created_at,
            chunks_count=len(doc.chunks),
            concepts_count=len(doc.concepts),
            prerequisites_count=len(doc.prerequisites),
            summaries_count=len(doc.summaries)
        )
        for doc in docs
    ]


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    """Fetch details and metrics for a specific document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    return DocumentDetailResponse(
        id=doc.id,
        filename=doc.filename,
        original_filename=doc.original_filename,
        file_type=doc.file_type or "pdf",
        mime_type=doc.mime_type,
        file_size=doc.file_size,
        page_count=doc.page_count or 0,
        slide_count=doc.slide_count or 0,
        section_count=doc.section_count or 0,
        title=doc.title,
        status=doc.status,
        error_message=doc.error_message,
        created_at=doc.created_at,
        chunks_count=len(doc.chunks),
        concepts_count=len(doc.concepts),
        prerequisites_count=len(doc.prerequisites),
        summaries_count=len(doc.summaries)
    )


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Delete a document, its database records, and physical file."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    # Remove physical file if exists
    try:
        p = Path(doc.file_path)
        if p.exists():
            p.unlink()
    except Exception:
        pass

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully.", "id": document_id}


@router.post("/{document_id}/process", response_model=DocumentProcessResponse)
async def process_document(document_id: str, db: Session = Depends(get_db)):
    """
    Execute full pipeline for any document type:
    Format Parser -> Normalized Document -> Text Cleaning -> Semantic Chunking ->
    Embeddings -> Concepts -> Prerequisites.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    doc.status = "processing"
    db.commit()

    try:
        # 1. Parse into NormalizedDocument
        norm_doc = DocumentNormalizer.parse_document(doc.file_path, doc.original_filename)
        doc.title = norm_doc.title
        if norm_doc.unit_label == "pages":
            doc.page_count = norm_doc.total_units
        elif norm_doc.unit_label == "slides":
            doc.slide_count = norm_doc.total_units
        else:
            doc.section_count = norm_doc.total_units

        # Clear existing entities if re-processing
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
        db.query(Concept).filter(Concept.document_id == document_id).delete()
        db.query(Prerequisite).filter(Prerequisite.document_id == document_id).delete()
        db.commit()

        # 2. Semantic chunking with source mapping
        raw_chunks = ChunkingService.create_chunks_from_normalized(
            document_id=document_id,
            normalized_doc=norm_doc
        )

        # 3. Generate dense vector embeddings
        chunk_texts = [c["text"] for c in raw_chunks]
        embeddings = embedding_service.generate_embeddings(chunk_texts)

        # Save chunks to database
        import json
        for idx, c in enumerate(raw_chunks):
            emb_json = json.dumps(embeddings[idx]) if idx < len(embeddings) else None
            chunk_db = DocumentChunk(
                id=c["id"],
                document_id=document_id,
                chunk_index=c["chunk_index"],
                heading=c["heading"],
                text=c["text"],
                source_type=c.get("source_type", doc.file_type),
                source_location=c.get("source_location", f"Page {c.get('page_number', 1)}"),
                page_number=c.get("page_number"),
                slide_number=c.get("slide_number"),
                section_name=c.get("section_name"),
                start_line=c.get("start_line"),
                end_line=c.get("end_line"),
                token_count=c["token_count"],
                embedding_json=emb_json
            )
            db.add(chunk_db)
        db.commit()

        # 4. Extract concepts
        concepts = await ConceptService.extract_and_store_concepts(
            db=db,
            document_id=document_id,
            document_title=doc.title or doc.original_filename,
            chunks=raw_chunks
        )

        # 5. Detect prerequisites
        prerequisites = await PrerequisiteService.detect_and_store_prerequisites(
            db=db,
            document_id=document_id,
            document_title=doc.title or doc.original_filename,
            chunks=raw_chunks,
            concepts=concepts
        )

        doc.status = "processed"
        doc.error_message = None
        db.commit()

        return DocumentProcessResponse(
            document_id=doc.id,
            filename=doc.original_filename,
            file_type=doc.file_type or "pdf",
            status="processed",
            units_count=norm_doc.total_units,
            unit_label=norm_doc.unit_label,
            chunks_created=len(raw_chunks),
            concepts_found=len(concepts),
            prerequisites_found=len(prerequisites),
            message=f"'{doc.original_filename}' successfully processed and indexed."
        )

    except DocumentParsingError as e:
        doc.status = "error"
        doc.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        doc.status = "error"
        doc.error_message = f"Processing error: {str(e)}"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing document: {str(e)}"
        )
