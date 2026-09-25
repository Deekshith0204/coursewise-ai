import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...models.entities import Prerequisite
from ...schemas.schemas import PrerequisiteItem

router = APIRouter(prefix="/prerequisites", tags=["Prerequisites"])


@router.get("/{document_id}", response_model=List[PrerequisiteItem])
def get_document_prerequisites(document_id: str, db: Session = Depends(get_db)):
    """Fetch detected prerequisite concepts for a given document."""
    prereqs = (
        db.query(Prerequisite)
        .filter(Prerequisite.document_id == document_id)
        .all()
    )

    result = []
    for p in prereqs:
        source_pages = json.loads(p.source_pages_json or "[]")
        result.append(
            PrerequisiteItem(
                id=p.id,
                topic=p.topic,
                name=p.name,
                reason=p.reason,
                source_pages=source_pages
            )
        )
    return result
