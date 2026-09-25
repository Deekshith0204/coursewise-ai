import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...models.entities import Concept
from ...schemas.schemas import ConceptItem

router = APIRouter(prefix="/concepts", tags=["Concepts"])


@router.get("/{document_id}", response_model=List[ConceptItem])
def get_document_concepts(document_id: str, db: Session = Depends(get_db)):
    """Fetch all key concepts identified for a given document."""
    concepts = (
        db.query(Concept)
        .filter(Concept.document_id == document_id)
        .order_by(Concept.importance_score.desc())
        .all()
    )

    result = []
    for c in concepts:
        source_pages = json.loads(c.source_pages_json or "[]")
        result.append(
            ConceptItem(
                id=c.id,
                name=c.name,
                explanation=c.explanation,
                source_pages=source_pages,
                importance_score=c.importance_score
            )
        )
    return result
