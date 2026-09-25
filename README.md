# CourseWise AI
**AI-Based Personalized Course Content Summarizer for Dense Technical Material**

> An AI-powered technical learning platform that converts complex, dense course materials across **PDF, Microsoft Word (.docx), Microsoft PowerPoint (.pptx), and Plain Text (.txt / .md)** into adaptive, source-traceable study summaries.

Detailed architectural documentation is available in [`coursewise-ai/README.md`](./coursewise-ai/README.md).

---

## System Requirements

- **Python**: 3.11 or higher
- **Node.js**: v18.0 or v20.0+
- **npm**: 9.0 or higher
- **Operating System**: Windows, macOS, or Linux

---

## Supported Technical Formats

- **PDF (`.pdf`)**: PyMuPDF page-by-page extraction with page number retention.
- **Word (`.docx`)**: `python-docx` headings, paragraphs, and markdown tables.
- **PowerPoint (`.pptx`)**: `python-pptx` slides, bullet points, tables, and speaker notes.
- **Plain Text (`.txt`)**: UTF-8/fallback encoding reader with line range preservation.
- **Markdown (`.md`)**: ATX heading and section block parser.

---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Backend Installation (Python / FastAPI)
```bash
cd coursewise-ai/backend
python -m pip install -r requirements.txt
```

### 3. Frontend Installation (Next.js 14 / TypeScript / Tailwind)
```bash
cd ../frontend
npm install
```

---

## Environment Setup & AI Configuration

1. Create your backend `.env` file from the provided `.env.example`:
```bash
# From coursewise-ai/backend directory:
cp .env.example .env
```
*(On Windows PowerShell, run: `Copy-Item .env.example .env`)*

2. Open `coursewise-ai/backend/.env` in your text editor and configure your preferred provider:

### Option A: Google Gemini (Recommended)
Get a free API key at [Google AI Studio](https://aistudio.google.com/):
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

### Option C: Local Ollama (Fully Offline)
```env
AI_API_KEY=ollama
AI_MODEL=llama3:8b
AI_BASE_URL=http://localhost:11434/v1
AI_PROVIDER=openai
```

> **Safe Unconfigured Mode**: If `AI_API_KEY` is not provided, the application continues to perform document parsing, semantic chunking, vector embeddings, concept identification, and prerequisite detection, and prompts you to configure your key when requesting a summary.

---

## Running the Application

### 1. Start the Backend Server (Terminal 1)
```bash
cd coursewise-ai/backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Health Check: `http://127.0.0.1:8000/api/health`
- Interactive API Docs (Swagger): `http://127.0.0.1:8000/docs`

### 2. Start the Frontend Server (Terminal 2)
```bash
cd coursewise-ai/frontend
npm run dev
```
Open your web browser at: **`http://localhost:3000`**

---

## Running Automated Tests

Run the backend integration test suite using `pytest`:
```bash
cd coursewise-ai/backend
python -m pytest tests/test_core.py -v
```
All 8 integration tests verify:
- Health check and supported formats (`pdf`, `docx`, `pptx`, `txt`, `md`)
- Multi-format text and table extraction
- Semantic chunking & local vector embeddings
- AI configuration safeguards
- Document upload and ingestion pipeline
- Database persistence and history retrieval
