import os
import re
import json
import logging
from typing import Dict, Any, List, Optional
import httpx

logger = logging.getLogger(__name__)


class AIConfigurationError(Exception):
    """Raised when the AI provider is not configured or missing an API key."""
    pass


class AIServiceError(Exception):
    """Raised when an AI API call fails or produces invalid output."""
    pass


class AIService:
    def __init__(self):
        self.api_key = os.getenv("AI_API_KEY", "").strip()
        self.model = os.getenv("AI_MODEL", "gemini-1.5-flash").strip()
        default_base_url = "https://generativelanguage.googleapis.com/v1beta/openai" if self.api_key.startswith("AIza") else "https://api.openai.com/v1"
        self.base_url = os.getenv("AI_BASE_URL", default_base_url).strip().rstrip("/")
        self.provider = os.getenv("AI_PROVIDER", "openai").strip().lower()

    def is_configured(self) -> bool:
        """Check if AI provider is properly configured with an API key."""
        self.api_key = os.getenv("AI_API_KEY", self.api_key).strip()
        return bool(self.api_key)

    def get_config_info(self) -> Dict[str, Any]:
        """Return non-sensitive configuration status for frontend."""
        configured = self.is_configured()
        masked_key = ""
        if configured:
            masked_key = self.api_key[:4] + "..." + self.api_key[-4:] if len(self.api_key) > 8 else "***"
        return {
            "configured": configured,
            "provider": self.provider,
            "model": self.model,
            "base_url": self.base_url,
            "masked_key": masked_key
        }

    async def generate_personalized_summary(
        self,
        document_title: str,
        chunks: List[Dict[str, Any]],
        knowledge_level: str,
        summary_depth: str,
        learning_preference: str,
        is_multi_document: bool = False,
        document_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a personalized summary from document chunks adhering strictly
        to the knowledge level, summary depth, and learning preference.
        Supports both single and multi-file document collections.
        """
        if not self.is_configured():
            raise AIConfigurationError(
                "AI provider not configured. Please set AI_API_KEY in backend/.env to generate summaries."
            )

        # Build context payload with document and location-attributed snippets
        context_blocks = []
        for c in chunks[:30]:  # select top relevant chunks across collection
            doc_name = c.get("document_name", document_title)
            loc = c.get("source_location") or f"Page {c.get('page_number', '?')}"
            heading = c.get("heading", "")
            text = c.get("text", "")
            context_blocks.append(f"[{doc_name} | {loc} | {heading}]:\n{text}")

        context_str = "\n\n---\n\n".join(context_blocks)

        system_prompt = self._build_system_prompt(
            knowledge_level=knowledge_level,
            summary_depth=summary_depth,
            learning_preference=learning_preference,
            is_multi_document=is_multi_document
        )

        collection_info = f"DOCUMENTS IN STUDY COLLECTION: {', '.join(document_names)}" if document_names else f"DOCUMENT: {document_title}"

        user_prompt = f"""{collection_info}

LEARNER KNOWLEDGE LEVEL: {knowledge_level}
SUMMARY DEPTH: {summary_depth}
LEARNING PREFERENCE: {learning_preference}

DOCUMENT CONTEXT (Extracted from course materials):
{context_str}

Please generate the comprehensive personalized learning summary strictly matching the requested JSON structure."""

        # Call AI API
        raw_response = await self._call_llm(system_prompt, user_prompt)
        
        # Parse and validate structured output
        parsed_data = self._parse_and_validate_json(raw_response)
        return parsed_data

    async def extract_concepts_and_prerequisites(
        self,
        document_title: str,
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Extract core concepts and prerequisite dependencies from document chunks.
        """
        if not self.is_configured():
            raise AIConfigurationError("AI provider not configured.")

        context_blocks = []
        for c in chunks[:15]:
            loc = c.get("source_location") or f"Page {c.get('page_number', '?')}"
            context_blocks.append(f"[{loc}]:\n{c.get('text', '')}")

        context_str = "\n\n".join(context_blocks)

        system_prompt = """You are an academic NLP extraction system for CourseWise AI.
Your task is to identify:
1. Core technical concepts discussed in the material with clear definitions and source location references (e.g., 'Page 4', 'Slide 7', 'Section: Intro', 'Lines 20-35').
2. Foundational prerequisite concepts the student needs to understand BEFORE tackling these topics, why they are needed, and source location references.

STRICT GROUNDING: Only extract concepts based on the provided text.
OUTPUT FORMAT: Output ONLY valid JSON with keys:
{
  "concepts": [
    {"name": "...", "explanation": "...", "source_pages": ["Page 1"], "importance_score": 0.9}
  ],
  "prerequisites": [
    {"topic": "...", "name": "...", "reason": "...", "source_pages": ["Page 1"]}
  ]
}"""

        user_prompt = f"DOCUMENT TITLE: {document_title}\n\nTEXT:\n{context_str}"

        raw_response = await self._call_llm(system_prompt, user_prompt)
        return self._parse_json(raw_response)

    def _build_system_prompt(
        self,
        knowledge_level: str,
        summary_depth: str,
        learning_preference: str,
        is_multi_document: bool = False
    ) -> str:
        """Construct prompt with strict hallucination control, personalization, and multi-file instructions."""
        
        level_instructions = {
            "BEGINNER": "Use simple, accessible language. Clarify technical jargon with intuitive explanations or analogies. Clearly highlight prerequisite definitions. Avoid gratuitous buzzwords without diluting factual correctness.",
            "INTERMEDIATE": "Use balanced technical terminology. Explain the mechanisms, relationships, and architectures connecting the concepts. Assume working baseline familiarity with domain fundamentals.",
            "ADVANCED": "Use rigorous technical depth and precise engineering/scientific terminology. Highlight mathematical nuance, algorithmic details, edge conditions, and architectural trade-offs present in the source."
        }.get(knowledge_level, "Provide clear, technically accurate explanations.")

        depth_instructions = {
            "QUICK": "Provide a high-level executive summary, overarching thesis, core takeaways, and main concepts. Be concise and high-impact.",
            "STANDARD": "Provide a comprehensive section-by-section breakdown, concept linkages, core technical mechanisms, and prerequisites.",
            "DETAILED": "Provide an exhaustive, in-depth technical analysis covering definitions, architectural relationships, step-by-step mechanisms, formulas or concrete examples present in the text, extensive prerequisites, and source citations."
        }.get(summary_depth, "Provide a balanced, structured summary.")

        pref_instructions = {
            "CONCEPT FOCUSED": "Emphasize theoretical frameworks, core principles, concept maps, and 'why' the system or method behaves as described.",
            "EXAM FOCUSED": "Emphasize formal definitions, essential classifications, comparative distinctions, formulas, and high-yield review points without fabricating fake test questions.",
            "PRACTICAL FOCUSED": "Emphasize real-world workflows, implementation pipelines, practical considerations, and applied examples found in the text."
        }.get(learning_preference, "Focus on clear pedagogical value.")

        multi_doc_guideline = """
MULTI-FILE COLLECTION INSTRUCTIONS:
- Synthesize the uploaded documents as a cohesive course collection.
- In "overview", provide an overarching synthesis across all materials.
- In "document_wise_summaries", generate a targeted summary for EACH individual document in the collection.
- In source citations, reference the specific document name and appropriate location:
  - PDF: "DocumentName — Page X"
  - PowerPoint: "DocumentName — Slide X"
  - Word: "DocumentName — Section: X"
  - Text: "DocumentName — Lines X-Y"
""" if is_multi_document else """
SOURCE LOCATION FORMAT:
- Preserve file-type locations accurately (e.g., 'Page X' for PDF, 'Slide X' for PPTX, 'Section: X' for DOCX, 'Lines X-Y' for TXT).
"""

        return f"""You are CourseWise AI, an expert academic AI pedagogical assistant.
Your purpose is to turn dense technical course material into clear, personalized learning content.

CRITICAL HALLUCINATION CONTROL RULES:
1. Ground your summary STRICTLY in the provided document context.
2. Do NOT invent facts, metrics, experiments, or external claims not supported by the text.
3. If specific information is requested or expected but missing from the source text, explicitly state: 'Not clearly available in the uploaded material.'
4. Always associate concepts, sections, and prerequisites with their actual source locations.
5. Preserve technical terminology faithfully.

LEARNER PERSONALIZATION SPECIFICATION:
- KNOWLEDGE LEVEL ({knowledge_level}): {level_instructions}
- SUMMARY DEPTH ({summary_depth}): {depth_instructions}
- LEARNING PREFERENCE ({learning_preference}): {pref_instructions}
{multi_doc_guideline}

REQUIRED JSON OUTPUT FORMAT:
You MUST output a valid, parseable JSON object with the following exact keys:
{{
  "title": "Comprehensive Course Material Title",
  "overview": "Comprehensive high-level overview personalized for the learner level...",
  "document_wise_summaries": [
    {{
      "document_name": "Filename.ext",
      "file_type": "pdf/docx/pptx/txt",
      "summary": "Specific focus and synthesis of this document..."
    }}
  ],
  "sections": [
    {{
      "heading": "Section Heading",
      "content": "Personalized detailed explanation...",
      "source_pages": ["Page 1", "Slide 5"]
    }}
  ],
  "key_points": [
    "Important takeaway bullet 1",
    "Important takeaway bullet 2"
  ],
  "key_concepts": [
    {{
      "name": "Concept Name",
      "explanation": "Clear explanation adapted to level...",
      "source_pages": ["Page 1", "Slide 3"]
    }}
  ],
  "prerequisites": [
    {{
      "topic": "Main Topic",
      "name": "Prerequisite Concept",
      "reason": "Why this prerequisite is needed to understand the topic...",
      "source_pages": ["Page 1"]
    }}
  ],
  "sources": [
    {{
      "document_name": "Filename.ext",
      "source_type": "pdf/docx/pptx/txt",
      "source_location": "Page 1 / Slide 5 / Section: Intro / Lines 20-35",
      "snippet": "Direct verbatim or tight paraphrased reference..."
    }}
  ]
}}"""

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call the configured LLM API using standard OpenAI-compatible completions."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code != 200:
                    if response.status_code == 400 and "response_format" in response.text:
                        payload.pop("response_format", None)
                        response = await client.post(url, headers=headers, json=payload)

                if response.status_code != 200:
                    error_detail = response.text[:300]
                    logger.error(f"AI API returned status {response.status_code}: {error_detail}")
                    raise AIServiceError(f"AI API request failed ({response.status_code}): {error_detail}")

                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return content
        except httpx.RequestError as e:
            logger.error(f"Network error communicating with AI API: {e}")
            raise AIServiceError(f"Failed to communicate with AI provider: {str(e)}")

    def _parse_and_validate_json(self, raw_text: str) -> Dict[str, Any]:
        """Extract and validate the structured JSON summary response."""
        data = self._parse_json(raw_text)

        required_keys = ["title", "overview", "sections", "key_points", "key_concepts", "prerequisites"]
        for key in required_keys:
            if key not in data:
                data[key] = [] if key != "title" and key != "overview" else "Not provided"

        if not isinstance(data.get("sections"), list):
            data["sections"] = []
        if not isinstance(data.get("document_wise_summaries"), list):
            data["document_wise_summaries"] = []
        if not isinstance(data.get("key_points"), list):
            data["key_points"] = []
        if not isinstance(data.get("key_concepts"), list):
            data["key_concepts"] = []
        if not isinstance(data.get("prerequisites"), list):
            data["prerequisites"] = []
        if not isinstance(data.get("sources"), list):
            data["sources"] = []

        return data

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        """Safely extract JSON from text even if enclosed in markdown backticks."""
        text = raw_text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"(\{.*\})", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            raise AIServiceError("AI output was not valid JSON.")


ai_service = AIService()
