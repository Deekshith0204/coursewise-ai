import os
import io
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.main import app
from app.database.session import Base, engine, SessionLocal
from app.services.pdf_service import PDFService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import embedding_service
from app.services.ai_service import ai_service, AIConfigurationError


@pytest.fixture(scope="module")
def client():
    # Setup test DB tables
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


def generate_sample_pdf_bytes() -> bytes:
    """Create a multi-page technical sample PDF for testing."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)

    # Page 1
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, 750, "Distributed Systems: Fundamentals and Consensus")
    c.setFont("Helvetica", 11)
    c.drawString(72, 710, "1. Introduction to Distributed Systems")
    text1 = (
        "Distributed computing refers to systems where software components on networked computers "
        "communicate and coordinate actions by passing messages. A fundamental challenge in distributed "
        "systems is reaching consensus across nodes in the presence of network partitions and failures. "
        "Consensus is defined as the process of agreeing on a single data value among distributed processes."
    )
    y = 680
    for line in [text1[i:i+75] for i in range(0, len(text1), 75)]:
        c.drawString(72, y, line)
        y -= 15
    c.drawString(250, 40, "CourseWise AI Testing - Page 1")
    c.showPage()

    # Page 2
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, 750, "2. Paxos and Raft Consensus Protocols")
    c.setFont("Helvetica", 11)
    text2 = (
        "The Paxos protocol ensures fault-tolerant state machine replication. Raft is an alternative "
        "designed for understandability, dividing consensus into leader election, log replication, and safety. "
        "Prerequisites include discrete mathematics, graph models, and basic network socket protocols. "
        "A Byzantine fault refers to an arbitrary failure where a node may transmit conflicting information."
    )
    y = 710
    for line in [text2[i:i+75] for i in range(0, len(text2), 75)]:
        c.drawString(72, y, line)
        y -= 15
    c.drawString(250, 40, "CourseWise AI Testing - Page 2")
    c.showPage()

    c.save()
    buf.seek(0)
    return buf.read()


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app_name"] == "CourseWise AI"


def test_pdf_extraction_and_chunking(tmp_path):
    pdf_bytes = generate_sample_pdf_bytes()
    pdf_path = tmp_path / "test_doc.pdf"
    pdf_path.write_bytes(pdf_bytes)

    pages, meta = PDFService.extract_text_and_structure(str(pdf_path))
    assert meta["total_pages"] == 2
    assert len(pages) == 2
    assert "Distributed Systems" in pages[0]["cleaned_text"]

    chunks = ChunkingService.create_chunks(
        document_id="test-doc-123",
        cleaned_pages=pages
    )
    assert len(chunks) >= 1
    assert chunks[0]["page_number"] in [1, 2]
    assert len(chunks[0]["text"]) > 20


def test_embedding_and_vector_search():
    texts = [
        "Distributed consensus algorithms like Raft and Paxos.",
        "Deep convolutional neural networks for computer vision.",
        "Relational database index optimization using B-trees."
    ]
    embeddings = embedding_service.generate_embeddings(texts)
    assert len(embeddings) == 3
    assert len(embeddings[0]) > 0

    # Query similar to distributed consensus
    query_emb = embedding_service.generate_embeddings(["leader election consensus protocols"])[0]
    top_indices = embedding_service.search_similar(query_emb, embeddings, top_k=1)
    assert top_indices[0] == 0  # Nearest should be distributed consensus!


def test_unconfigured_ai_safeguard():
    """Ensure AI service throws explicit configuration error when unconfigured."""
    old_key = os.environ.get("AI_API_KEY", "")
    os.environ["AI_API_KEY"] = ""
    ai_service.api_key = ""

    assert ai_service.is_configured() is False
    with pytest.raises(AIConfigurationError):
        import asyncio
        asyncio.run(ai_service.generate_personalized_summary(
            document_title="Test",
            chunks=[],
            knowledge_level="INTERMEDIATE",
            summary_depth="STANDARD",
            learning_preference="CONCEPT FOCUSED"
        ))

    # Restore
    os.environ["AI_API_KEY"] = old_key
    ai_service.api_key = old_key


def test_document_upload_and_process_pipeline(client, tmp_path):
    pdf_bytes = generate_sample_pdf_bytes()
    
    # Upload
    files = [("files", ("distributed_systems.pdf", pdf_bytes, "application/pdf"))]
    upload_res = client.post("/api/documents/upload", files=files)
    assert upload_res.status_code == 201
    upload_data = upload_res.json()
    item = upload_data[0] if isinstance(upload_data, list) else upload_data
    doc_id = item["document_id"]
    assert item["page_count"] == 2

    # Process
    process_res = client.post(f"/api/documents/{doc_id}/process")
    assert process_res.status_code == 200
    pdata = process_res.json()
    assert pdata["status"] == "processed"
    assert pdata["chunks_created"] >= 1
    assert pdata["concepts_found"] >= 1
    assert pdata["prerequisites_found"] >= 1

    # Check concepts
    concepts_res = client.get(f"/api/concepts/{doc_id}")
    assert concepts_res.status_code == 200
    concepts = concepts_res.json()
    assert len(concepts) > 0

    # Check prerequisites
    prereqs_res = client.get(f"/api/prerequisites/{doc_id}")
    assert prereqs_res.status_code == 200
    prereqs = prereqs_res.json()
    assert len(prereqs) > 0


def test_summary_database_and_history_operations(client):
    import uuid
    import json
    from app.models.entities import Document, Summary, SummarySource, Evaluation

    db = SessionLocal()
    doc = db.query(Document).first()
    assert doc is not None

    summary_id = str(uuid.uuid4())
    summary = Summary(
        id=summary_id,
        document_id=doc.id,
        knowledge_level="BEGINNER",
        summary_depth="QUICK",
        learning_preference="CONCEPT FOCUSED",
        title="Distributed Systems for Beginners",
        overview="Introductory overview of distributed consensus.",
        full_content_json=json.dumps([{"heading": "Basics", "content": "Explains consensus simply.", "source_pages": [1]}]),
        key_points_json=json.dumps(["Nodes communicate via messages", "Consensus ensures agreement"]),
        key_concepts_json=json.dumps([{"name": "Consensus", "explanation": "Agreement among nodes", "source_pages": [1], "importance_score": 0.9}]),
        prerequisites_json=json.dumps([{"topic": "Basics", "name": "Networks", "reason": "Nodes communicate over sockets", "source_pages": [1]}]),
        response_time_ms=1200
    )
    db.add(summary)
    source = SummarySource(
        id=str(uuid.uuid4()),
        summary_id=summary_id,
        page_number=1,
        section_name="Introduction",
        snippet="Distributed computing refers to systems..."
    )
    db.add(source)
    evaluation = Evaluation(
        id=str(uuid.uuid4()),
        summary_id=summary_id,
        compression_ratio=0.35,
        source_word_count=500,
        summary_word_count=175
    )
    db.add(evaluation)
    db.commit()
    db.close()

    # Test GET history
    history_res = client.get("/api/summaries/history")
    assert history_res.status_code == 200
    history = history_res.json()
    assert any(h["id"] == summary_id for h in history)

    # Test GET summary by id
    detail_res = client.get(f"/api/summaries/{summary_id}")
    assert detail_res.status_code == 200
    data = detail_res.json()
    assert data["title"] == "Distributed Systems for Beginners"
    assert len(data["sections"]) == 1
    assert len(data["sources"]) == 1
    assert data["evaluation"]["compression_ratio"] == 0.35

    # Test rating
    rate_res = client.post(f"/api/summaries/{summary_id}/rate", json={"rating": 5, "feedback_notes": "Very clear!"})
    assert rate_res.status_code == 200

    # Test DELETE summary
    del_res = client.delete(f"/api/summaries/{summary_id}")
    assert del_res.status_code == 200

    # Verify deleted
    get_del = client.get(f"/api/summaries/{summary_id}")
    assert get_del.status_code == 404


def test_multi_format_parsers(tmp_path):
    from app.document_processing.document_normalizer import DocumentNormalizer
    from app.database.session import DATA_DIR

    docx_path = DATA_DIR / "sample_cloud_edge.docx"
    pptx_path = DATA_DIR / "sample_deep_learning.pptx"
    txt_path = DATA_DIR / "sample_os_memory.txt"

    # Test DOCX
    docx_doc = DocumentNormalizer.parse_document(str(docx_path), "sample_cloud_edge.docx")
    assert docx_doc.file_type == "docx"
    assert len(docx_doc.sections) >= 2
    assert any("Latency" in s.content for s in docx_doc.sections)  # Table extracted!
    assert docx_doc.sections[0].source_location.startswith("Section:")

    # Test PPTX
    pptx_doc = DocumentNormalizer.parse_document(str(pptx_path), "sample_deep_learning.pptx")
    assert pptx_doc.file_type == "pptx"
    assert pptx_doc.total_units == 4
    assert pptx_doc.sections[1].source_location == "Slide 2"
    assert any("Convolutional" in s.content for s in pptx_doc.sections)

    # Test TXT
    txt_doc = DocumentNormalizer.parse_document(str(txt_path), "sample_os_memory.txt")
    assert txt_doc.file_type == "txt"
    assert len(txt_doc.sections) >= 1
    assert "Lines" in txt_doc.sections[0].source_location
    assert "Paging" in txt_doc.extracted_text


def test_multi_file_upload_and_processing(client):
    from app.database.session import DATA_DIR
    
    docx_bytes = (DATA_DIR / "sample_cloud_edge.docx").read_bytes()
    txt_bytes = (DATA_DIR / "sample_os_memory.txt").read_bytes()

    # Upload DOCX + TXT together
    files = [
        ("files", ("sample_cloud_edge.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")),
        ("files", ("sample_os_memory.txt", txt_bytes, "text/plain")),
    ]
    res = client.post("/api/documents/upload", files=files)
    assert res.status_code == 201
    upload_list = res.json()
    assert len(upload_list) == 2
    assert upload_list[0]["file_type"] == "docx"
    assert upload_list[1]["file_type"] == "txt"

    doc1_id = upload_list[0]["document_id"]
    doc2_id = upload_list[1]["document_id"]

    # Process both documents
    p1 = client.post(f"/api/documents/{doc1_id}/process")
    assert p1.status_code == 200
    assert p1.json()["status"] == "processed"

    p2 = client.post(f"/api/documents/{doc2_id}/process")
    assert p2.status_code == 200
    assert p2.json()["status"] == "processed"

    # Test multi-file summary request safeguard (returns 503 if unconfigured)
    sum_res = client.post(
        "/api/summaries/generate",
        json={
            "document_ids": [doc1_id, doc2_id],
            "knowledge_level": "BEGINNER",
            "summary_depth": "QUICK",
            "learning_preference": "EXAM FOCUSED"
        }
    )
    assert sum_res.status_code == 503
    assert "AI provider not configured" in sum_res.json()["detail"]


