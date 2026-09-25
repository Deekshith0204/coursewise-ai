# CourseWise AI
**AI-Based Personalized Course Content Summarizer for Dense Technical Material**

> *"Turn dense technical material into clear, personalized learning content across PDFs, Word documents, PowerPoint presentations, and text notes."*

CourseWise AI is a full-stack, pedagogical AI web application designed to help university students and researchers master complex, dense technical textbooks, research papers, lecture slide decks, and lab guides. Rather than producing generic, ungrounded summaries, CourseWise AI extracts structural semantics across **PDF, DOCX, PPTX, and TXT** documents, creates unified semantic chunks and vector embeddings, identifies key concepts and prerequisite dependencies, and adapts explanations to the learner's knowledge level, summary depth, and learning preference with strict hallucination controls and fine-grained source traceability.

---

## Table of Contents
1. [Key Features & Multi-Format Support](#key-features--multi-format-support)
2. [Supported Technical Document Formats](#supported-technical-document-formats)
3. [Multi-Document Summarization Architecture](#multi-document-summarization-architecture)
4. [Technology Stack](#technology-stack)
5. [Prerequisites](#prerequisites)
6. [Installation & Setup](#installation--setup)
7. [AI Provider Configuration](#ai-provider-configuration)
8. [Running the Application](#running-the-application)
9. [Sample Test Datasets](#sample-test-datasets)
10. [Core User Workflow](#core-user-workflow)
11. [REST API Documentation](#rest-api-documentation)
12. [Academic Pedagogical Alignment](#academic-pedagogical-alignment)
13. [Testing & Verification](#testing--verification)

---

## Key Features & Multi-Format Support

- **Multi-Format Technical Document Ingestion**:
  - Ingests **PDF**, **Microsoft Word (.docx)**, **Microsoft PowerPoint (.pptx)**, and **Plain Text (.txt / .md)** files into a unified normalized document model.
  - Automatically detects file types, assigns color-coded badges, and extracts deep structural hierarchy.
- **Multi-File Workspace ("MY COURSE MATERIAL")**:
  - Upload multiple technical files simultaneously via an intuitive multi-file drag-and-drop dropzone.
  - View individual file status badges (`Ready`, `Extracting & Chunking...`, `Failed`).
  - Select or deselect specific documents using checkboxes or the "Select All / Deselect All" toggle.
  - Add more course materials dynamically to your active study collection.
- **Cross-Document Synthesis & Breakdown**:
  - Generates a coherent **Overall Executive Summary** synthesizing concepts across multiple uploaded files.
  - Provides a **Document-Wise Summary Breakdown** detailing the specific contributions of each individual slide deck, document, or textbook chapter.
- **File-Type-Specific Source Traceability**:
  - Every extracted concept, prerequisite, and summary citation is mapped back to its precise origin:
    - **PDF**: `Page X`
    - **PowerPoint (PPTX)**: `Slide X`
    - **Word (DOCX)**: `Section: Heading Name`
    - **Plain Text (TXT)**: `Lines X-Y`
    - **Multi-Document Collections**: `DocumentName — Location`
- **Semantic Chunking & Local Dense Embeddings**:
  - Avoids arbitrary character cutoffs by partitioning text along headings, slide boundaries, table structures, and paragraph blocks.
  - Computes dense vector representations with exact cosine similarity search locally without external vector database dependencies.
- **Key Concept & Prerequisite Dependency Extraction**:
  - Automatically identifies core technical concepts, explanations, importance weights, and source locations.
  - Identifies foundational subjects the student needs to understand before studying major topics.
- **Multi-Dimensional Learner Personalization**:
  - **Knowledge Level**: `BEGINNER`, `INTERMEDIATE`, `ADVANCED`.
  - **Summary Depth**: `QUICK`, `STANDARD`, `DETAILED`.
  - **Learning Preference**: `CONCEPT FOCUSED`, `EXAM FOCUSED`, `PRACTICAL FOCUSED`.
- **Hallucination Safeguards**: Prompts enforce primary source grounding; unsupported claims state *"Not clearly available in the uploaded material"*.

---

## Supported Technical Document Formats

| Format | Parser Engine | Structural Elements Extracted | Traceability Unit |
|---|---|---|---|
| **PDF (`.pdf`)** | PyMuPDF (`fitz`) | Text, section headings, cleaned headers/footers, scanned-PDF check | `Page X` |
| **Word (`.docx`)** | `python-docx` | Document title, H1/H2/H3 headings, paragraph body, bullet lists, markdown tables (`\| col \| col \|`) | `Section: [Title]` |
| **PowerPoint (`.pptx`)** | `python-pptx` | Slide number, slide title, shapes/text boxes, bullet lists, tables, speaker notes (`[Speaker Notes]: ...`) | `Slide X` |
| **Plain Text (`.txt`)** | UTF-8 / latin-1 fallback | Section headings, line blocks, code snippets | `Lines X-Y` |
| **Markdown (`.md`)** | MarkdownParser | ATX `#` headings, lists, code fences | `Section: [Title]` |

---

## Multi-Document Summarization Architecture

```
                      +--------------------------------------------------------+
                      |         Next.js 14 + Tailwind CSS Frontend            |
                      |  (Multi-File Dropzone, File Collection, Viewer)        |
                      +---------------------------+----------------------------+
                                                  | REST JSON
                                                  v
                      +--------------------------------------------------------+
                      |                 FastAPI Application                    |
                      +---------------------------+----------------------------+
                                                  |
       +-----------------------+------------------+------------------+-----------------------+
       |                       |                                     |                       |
       v                       v                                     v                       v
+---------------+      +---------------+                     +---------------+      +---------------+
|   PDFParser   |      |  DocxParser   |                     |  PptxParser   |      |   TxtParser   |
|   (PyMuPDF)   |      | (python-docx) |                     | (python-pptx) |      | (Lines/Enc.)  |
+-------+-------+      +-------+-------+                     +-------+-------+      +-------+-------+
        |                      |                                     |                      |
        +----------------------+------------------+------------------+----------------------+
                                                  |
                                                  v
                                     +--------------------------+
                                     |    NormalizedDocument    |
                                     | (Sections, Units, Meta)  |
                                     +------------+-------------+
                                                  |
                                                  v
                                     +--------------------------+
                                     |  SemanticChunkingService |
                                     | (Unit/Location Tracking) |
                                     +------------+-------------+
                                                  |
                                                  v
                                     +--------------------------+
                                     |    DenseVectorService    |
                                     |  (Embeddings & Search)   |
                                     +------------+-------------+
                                                  |
                                                  v
                                     +--------------------------+
                                     |    ConceptService &      |
                                     |   PrerequisiteService    |
                                     +------------+-------------+
                                                  |
                                                  v
                                     +--------------------------+
                                     |  AIService (LLM Engine)  |
                                     | (Overall + Doc Breakdown)|
                                     +------------+-------------+
                                                  |
                                                  v
                                     +--------------------------+
                                     |   SQLite (SQLAlchemy)    |
                                     | (Multi-File Persisted)   |
                                     +--------------------------+
```

---

## Technology Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Library**: React 18 & TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Server**: Uvicorn (ASGI)
- **Document Parsers**: PyMuPDF (`pymupdf`), `python-docx`, `python-pptx`
- **ORM / Database**: SQLAlchemy 2.0 with SQLite
- **Validation**: Pydantic v2 & Pydantic-Settings
- **Vector Search**: NumPy vectorized cosine similarity

---

## Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: v18.0 or v20.0+
- **npm**: 9.0+

---

## Installation & Setup

### 1. Clone or Open Workspace
```bash
cd coursewise-ai
```

### 2. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

---

## AI Provider Configuration

CourseWise AI uses environment variables for AI provider configuration.

1. Create or edit `backend/.env`:
```bash
cp backend/.env.example backend/.env
```

2. Configure your preferred AI provider:

### Option A: Google Gemini (Recommended)
Get an API key from [Google AI Studio](https://aistudio.google.com/):
```env
AI_API_KEY=your_gemini_api_key_here
AI_MODEL=gemini-1.5-flash
AI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
AI_PROVIDER=openai
```

### Option B: OpenAI
```env
AI_API_KEY=your_openai_api_key_here
AI_MODEL=gpt-4o-mini
AI_BASE_URL=https://api.openai.com/v1
AI_PROVIDER=openai
```

### Option C: Local Ollama (Completely Offline)
```env
AI_API_KEY=ollama
AI_MODEL=llama3:8b
AI_BASE_URL=http://localhost:11434/v1
AI_PROVIDER=openai
```

> **Note on Unconfigured State**: If `AI_API_KEY` is not set, all parsing, multi-file ingestion, semantic chunking, embeddings, concepts, and prerequisites operate normally, while the summary generation gracefully informs the user to configure an API key.

---

## Running the Application

### Start the Backend (Terminal 1)
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Health: `http://127.0.0.1:8000/api/health`
- Interactive Swagger Docs: `http://127.0.0.1:8000/docs`

### Start the Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```
Open your browser at `http://localhost:3000`.

---

## Sample Test Datasets

Pre-built sample technical files are included in `coursewise-ai/data/`:
- `data/sample_dense_technical_course.pdf`: Comprehensive Distributed Systems and Machine Learning textbook chapter.
- `data/sample_cloud_edge.docx`: Cloud Computing and Edge Systems architecture guide with markdown tables.
- `data/sample_deep_learning.pptx`: Deep Learning and Neural Networks lecture slides with bullet points and speaker notes.
- `data/sample_os_memory.txt`: Operating Systems Virtual Memory and Paging technical notes with line-range traceability.

---

## Core User Workflow

1. **Open Dashboard**: Go to `http://localhost:3000`.
2. **Upload Technical Documents**:
   - Drag and drop one or more files (`.pdf`, `.docx`, `.pptx`, `.txt`, `.md`).
   - The system uploads each document and displays real-time processing indicators (`Extracting & Chunking...`, `Ready`).
3. **Manage Course Materials**:
   - Review the **MY COURSE MATERIAL** list.
   - Select individual files or click **Select All** to synthesize a combined multi-document summary.
   - Use the compact **Add More Course Materials** box to expand your workspace.
4. **Configure Personalization**:
   - Select **Knowledge Level**: `Beginner`, `Intermediate`, or `Advanced`.
   - Select **Summary Depth**: `Quick`, `Standard`, or `Detailed`.
   - Select **Learning Preference**: `Concept Focused`, `Exam Focused`, or `Practical Focused`.
5. **Generate Summary**:
   - Click **Generate Personalized Summary**.
   - If multiple documents are selected, the engine synthesizes across all selected materials.
6. **Explore Results**:
   - Read the **Overall Synthesis**.
   - Explore the **Document-Wise Summary Breakdown** cards with file badges.
   - Review **Key Concepts** and **Prerequisites** with interactive source references.
   - Check **Source References** displaying `Page X`, `Slide X`, `Section: X`, or `Lines X-Y`.
   - Review quantitative metrics in the **Evaluation Metrics** tab.
7. **Export & Review**:
   - Click **Export** to save as formatted Markdown or copy to clipboard.
   - Visit the **History** tab (`/history`) to view previous single and multi-document summaries.

---

## REST API Documentation

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check, supported formats, & AI configuration status |
| `GET` | `/api/health/config` | Active AI provider model & non-sensitive configuration |
| `POST` | `/api/documents/upload` | Upload multiple technical files (`files: List[UploadFile]`) |
| `GET` | `/api/documents` | List all uploaded course materials with metadata |
| `GET` | `/api/documents/{id}` | Retrieve document metadata & processing status |
| `DELETE` | `/api/documents/{id}` | Delete a document, its stored chunks, and uploaded file |
| `POST` | `/api/documents/{id}/process` | Run extraction, chunking, embeddings, concepts |
| `POST` | `/api/summaries/generate` | Generate personalized summary for one or multiple `document_ids` |
| `GET` | `/api/summaries/{id}` | Retrieve generated summary details |
| `GET` | `/api/summaries/history` | List all past summaries (includes multi-document metadata) |
| `DELETE` | `/api/summaries/{id}` | Remove summary from history |
| `POST` | `/api/summaries/{id}/rate` | Record educational usefulness rating (1-5) |
| `GET` | `/api/concepts/{doc_id}` | Retrieve extracted technical concepts |
| `GET` | `/api/prerequisites/{doc_id}` | Retrieve detected prerequisite topics |

---

## Academic Pedagogical Alignment

CourseWise AI directly addresses fundamental challenges in higher education learning technology:
1. **Multi-Source Synthesis**: Students study from lecture slides, textbooks, lab notes, and word briefs simultaneously. CourseWise AI harmonizes disparate file formats into a singular, cohesive learning map.
2. **Cognitive Load Reduction**: Layered summaries allow students to adjust depth (`Quick` -> `Standard` -> `Detailed`) as their comprehension deepens.
3. **Zone of Proximal Development (ZPD)**: Beginner modes bridge knowledge gaps with intuitive conceptual anchors, while Advanced modes maintain rigorous technical terminology.
4. **Prerequisite Discovery**: Explicit prerequisite mapping guides students on foundational knowledge to review prior to tackling dense engineering topics.
5. **Factual Traceability**: Preventing LLM hallucinations through explicit source grounding gives students confidence in study prep.

---

## Testing & Verification

Run the test suite using `pytest`:
```bash
cd backend
python -m pytest tests/test_core.py -v
```

All 8 integration and format-parsing test suites verify:
- Health check and supported formats (`pdf`, `docx`, `pptx`, `txt`, `md`).
- PDF extraction, page retention, and semantic chunking.
- Vector embeddings and cosine similarity search.
- Unconfigured AI key safeguard (503 response with instructions).
- Unified document upload and processing pipeline.
- Summary database, rating, and history operations.
- Multi-format parser accuracy: DOCX tables, PPTX slides & notes, TXT line ranges.
- Multi-file batch upload, processing, and multi-document summary payload generation.
