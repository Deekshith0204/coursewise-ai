import json
import uuid
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..models.entities import Prerequisite
from .ai_service import ai_service

logger = logging.getLogger(__name__)

# Common academic domain prerequisite heuristic mappings
DOMAIN_PREREQUISITE_RULES = {
    "neural network": [
        ("Linear Algebra", "Understanding weight matrices, vector transformations, and dot products"),
        ("Calculus & Gradient Descent", "Necessary for backpropagation and parameter optimization"),
        ("Probability & Statistics", "Essential for loss distributions and likelihood estimation")
    ],
    "deep learning": [
        ("Basic Machine Learning", "Concepts like overfitting, regularization, and train/test splits"),
        ("Matrix Multiplication", "Foundational tensor operations in dense and convolutional layers")
    ],
    "convolution": [
        ("Digital Image Representation", "Understanding 2D/3D pixel matrices, channels, and spatial filters"),
        ("Linear Algebra", "Matrix kernel operations and inner products")
    ],
    "transformer": [
        ("Attention Mechanisms", "Understanding Query, Key, Value matrix projections"),
        ("Recurrent Neural Networks / Seq2Seq", "Contextual background on sequential token modeling")
    ],
    "graph": [
        ("Discrete Mathematics", "Graph theory fundamentals including vertices, edges, paths, and cycles"),
        ("Adjacency Matrices", "Matrix representation of relationships and edge weights")
    ],
    "database": [
        ("Relational Algebra", "Understanding projection, selection, cartesian products, and joins"),
        ("Data Structures (B-Trees / Hashing)", "Core indexing and lookup mechanisms")
    ],
    "concurrency": [
        ("Operating System Basics", "Processes, threads, context switching, and virtual memory"),
        ("Mutual Exclusion & Locks", "Understanding race conditions, deadlocks, and atomic operations")
    ],
    "distributed": [
        ("Computer Networking (TCP/IP)", "Understanding packet loss, latency, and socket communication"),
        ("Consensus & Fault Tolerance", "Knowledge of partition tolerance and state synchronization")
    ],
    "algorithm": [
        ("Asymptotic Analysis (Big-O)", "Evaluating time and space complexity"),
        ("Basic Data Structures", "Arrays, linked lists, stacks, and recursion")
    ],
    "security": [
        ("Cryptography Basics", "Symmetric and asymmetric encryption, public/private keys"),
        ("Network Protocols", "Understanding packet headers, TLS/SSL handshakes, and certificates")
    ]
}


class PrerequisiteService:
    @classmethod
    async def detect_and_store_prerequisites(
        cls,
        db: Session,
        document_id: str,
        document_title: str,
        chunks: List[Dict[str, Any]],
        concepts: List[Any]
    ) -> List[Prerequisite]:
        """
        Identify prerequisite concepts using AI if available, combined with
        domain rule-based prerequisite mapping, and persist to database.
        """
        extracted_prereqs = []

        # Try LLM extraction if AI is configured
        if ai_service.is_configured():
            try:
                ai_data = await ai_service.extract_concepts_and_prerequisites(document_title, chunks)
                for item in ai_data.get("prerequisites", []):
                    extracted_prereqs.append({
                        "topic": item.get("topic", document_title).strip(),
                        "name": item.get("name", "Prerequisite Concept").strip(),
                        "reason": item.get("reason", "Required foundation for this topic.").strip(),
                        "source_pages": item.get("source_pages", [1])
                    })
            except Exception as e:
                logger.warning(f"AI prerequisite detection failed or unavailable: {e}. Using domain heuristics.")

        # Fallback / heuristic domain mapping
        if not extracted_prereqs:
            extracted_prereqs = cls._detect_prerequisites_heuristics(document_title, chunks, concepts)

        # Persist to database
        db_prereqs = []
        for p in extracted_prereqs:
            prereq_obj = Prerequisite(
                id=str(uuid.uuid4()),
                document_id=document_id,
                topic=p["topic"],
                name=p["name"],
                reason=p["reason"],
                source_pages_json=json.dumps(p.get("source_pages", [1]))
            )
            db.add(prereq_obj)
            db_prereqs.append(prereq_obj)

        db.commit()
        return db_prereqs

    @classmethod
    def _detect_prerequisites_heuristics(
        cls,
        document_title: str,
        chunks: List[Dict[str, Any]],
        concepts: List[Any]
    ) -> List[Dict[str, Any]]:
        """Identify prerequisites based on document domain keywords."""
        corpus = (document_title + " " + " ".join(c.get("text", "")[:300] for c in chunks[:10])).lower()
        
        prereqs: List[Dict[str, Any]] = []
        seen_names = set()

        first_loc = chunks[0].get("source_location") if chunks else "Page 1"

        for domain_key, req_list in DOMAIN_PREREQUISITE_RULES.items():
            if domain_key in corpus:
                for prereq_name, reason in req_list:
                    if prereq_name not in seen_names:
                        seen_names.add(prereq_name)
                        prereqs.append({
                            "topic": domain_key.title() + " Concepts",
                            "name": prereq_name,
                            "reason": reason,
                            "source_pages": [first_loc]
                        })

        # If none matched, provide generic academic foundational prerequisite
        if not prereqs:
            prereqs.append({
                "topic": document_title,
                "name": "Fundamental Domain Foundations",
                "reason": "Basic introductory terminology and mathematical/computational foundations relevant to this domain.",
                "source_pages": [first_loc]
            })

        return prereqs[:8]
