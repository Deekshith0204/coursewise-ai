import re
import json
import uuid
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..models.entities import Concept, DocumentChunk
from .ai_service import ai_service

logger = logging.getLogger(__name__)


class ConceptService:
    @classmethod
    async def extract_and_store_concepts(
        cls,
        db: Session,
        document_id: str,
        document_title: str,
        chunks: List[Dict[str, Any]]
    ) -> List[Concept]:
        """
        Extract key technical concepts using AI if available, combined with
        NLP keyword & definition pattern extraction, and persist to database.
        """
        extracted_concepts = []

        # Try LLM extraction if AI service is configured
        if ai_service.is_configured():
            try:
                ai_data = await ai_service.extract_concepts_and_prerequisites(document_title, chunks)
                for item in ai_data.get("concepts", []):
                    extracted_concepts.append({
                        "name": item.get("name", "Key Concept").strip(),
                        "explanation": item.get("explanation", "").strip(),
                        "source_pages": item.get("source_pages", [1]),
                        "importance_score": float(item.get("importance_score", 0.85))
                    })
            except Exception as e:
                logger.warning(f"AI concept extraction failed or unavailable: {e}. Using NLP heuristic extractor.")

        # Fallback / complementary NLP rule-based extraction
        if not extracted_concepts:
            extracted_concepts = cls._extract_concepts_nlp(chunks)

        # Persist to database
        db_concepts = []
        for c in extracted_concepts:
            concept_obj = Concept(
                id=str(uuid.uuid4()),
                document_id=document_id,
                name=c["name"],
                explanation=c["explanation"] or f"Core concept discussed in {document_title}.",
                source_pages_json=json.dumps(c.get("source_pages", [1])),
                importance_score=c.get("importance_score", 0.5)
            )
            db.add(concept_obj)
            db_concepts.append(concept_obj)

        db.commit()
        return db_concepts

    @classmethod
    def _extract_concepts_nlp(cls, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract concepts using definition patterns, technical phrases, and headings."""
        concepts: Dict[str, Dict[str, Any]] = {}

        # 1. From headings
        for chunk in chunks:
            loc = chunk.get("source_location") or f"Page {chunk.get('page_number', 1)}"
            text = chunk.get("text", "")
            heading = chunk.get("heading", "")

            if heading and not heading.startswith("Page ") and not heading.startswith("Slide ") and not heading.startswith("Lines "):
                clean_heading = re.sub(r"^(\d+(\.\d+)*|[A-Z](\.\d+)*)\s+", "", heading).strip()
                if 3 < len(clean_heading) < 60 and clean_heading not in concepts:
                    first_sent = text.split(".")[0].strip() + "." if text else "Core technical subject area."
                    concepts[clean_heading] = {
                        "name": clean_heading,
                        "explanation": first_sent[:250],
                        "source_pages": [loc],
                        "importance_score": 0.9
                    }

        # 2. Definition patterns: "X is defined as Y", "X refers to Y", "X is a Y"
        definition_pattern = re.compile(
            r"\b([A-Z][a-zA-Z0-9\-]+(?:\s+[A-Za-z0-9\-]+){0,3})\s+(is defined as|refers to|is an?|denotes|represents)\s+([^.\n]{10,250}\.)",
            re.IGNORECASE
        )

        for chunk in chunks:
            loc = chunk.get("source_location") or f"Page {chunk.get('page_number', 1)}"
            text = chunk.get("text", "")
            for match in definition_pattern.finditer(text):
                term = match.group(1).strip()
                explanation = f"{match.group(2)} {match.group(3)}".strip()
                if len(term) < 3 or len(term) > 40 or term.lower() in {"this", "it", "they", "there", "we", "the", "an", "a", "which", "these", "those"}:
                    continue
                if term not in concepts:
                    concepts[term] = {
                        "name": term,
                        "explanation": explanation[:300],
                        "source_pages": [loc],
                        "importance_score": 0.85
                    }
                elif loc not in concepts[term]["source_pages"]:
                    concepts[term]["source_pages"].append(loc)

        # 3. Capitalized technical phrases (e.g. "Distributed Systems", "Consensus Protocols")
        tech_phrase_pat = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b")
        for chunk in chunks:
            loc = chunk.get("source_location") or f"Page {chunk.get('page_number', 1)}"
            text = chunk.get("text", "")
            for phrase in tech_phrase_pat.findall(text):
                phrase = phrase.strip()
                if len(phrase) < 4 or phrase.lower() in {"coursewise ai", "page content", "slide content"}:
                    continue
                if phrase not in concepts:
                    sentences = [s.strip() for s in text.split(".") if phrase in s]
                    explanation = (sentences[0] + ".") if sentences else f"Technical concept {phrase} discussed in {loc}."
                    concepts[phrase] = {
                        "name": phrase,
                        "explanation": explanation[:250],
                        "source_pages": [loc],
                        "importance_score": 0.75
                    }
                elif loc not in concepts[phrase]["source_pages"]:
                    concepts[phrase]["source_pages"].append(loc)

        result = list(concepts.values())
        result.sort(key=lambda x: x["importance_score"], reverse=True)
        return result[:12]
