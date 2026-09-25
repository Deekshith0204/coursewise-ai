from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...models.entities import Summary, Evaluation
from ...schemas.schemas import (
    SummaryGenerateRequest,
    SummaryResponse,
    SummaryHistoryItem,
    EvaluationRateRequest
)
from ...services.summary_service import SummaryService
from ...services.ai_service import AIConfigurationError, AIServiceError

router = APIRouter(prefix="/summaries", tags=["Summaries"])


@router.post("/generate", response_model=SummaryResponse, status_code=status.HTTP_201_CREATED)
async def generate_summary(
    request: SummaryGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate personalized learning summary adapted to knowledge level,
    summary depth, and learning preference with strict source attribution.
    """
    doc_ids = request.document_ids or ([request.document_id] if request.document_id else [])
    if not doc_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No document IDs specified for summary generation."
        )

    try:
        summary_response = await SummaryService.generate_summary(
            db=db,
            document_ids=doc_ids,
            knowledge_level=request.knowledge_level,
            summary_depth=request.summary_depth,
            learning_preference=request.learning_preference
        )
        return summary_response
    except AIConfigurationError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except AIServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI generation failed: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summary generation error: {str(e)}"
        )


@router.get("/history", response_model=List[SummaryHistoryItem])
def get_summary_history(db: Session = Depends(get_db)):
    """Retrieve full history of generated summaries."""
    return SummaryService.list_history(db)


@router.get("/{summary_id}", response_model=SummaryResponse)
def get_summary(summary_id: str, db: Session = Depends(get_db)):
    """Retrieve an existing summary by ID."""
    summary = SummaryService.get_summary(db, summary_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found."
        )
    return summary


@router.delete("/{summary_id}", status_code=status.HTTP_200_OK)
def delete_summary(summary_id: str, db: Session = Depends(get_db)):
    """Delete a summary from history."""
    deleted = SummaryService.delete_summary(db, summary_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found."
        )
    return {"message": "Summary deleted successfully.", "id": summary_id}


@router.post("/{summary_id}/rate", status_code=status.HTTP_200_OK)
def rate_summary(
    summary_id: str,
    rating_data: EvaluationRateRequest,
    db: Session = Depends(get_db)
):
    """Save user usefulness evaluation rating for academic validation."""
    summary = db.query(Summary).filter(Summary.id == summary_id).first()
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found.")

    if not summary.evaluation:
        evaluation = Evaluation(
            summary_id=summary_id,
            user_rating=rating_data.rating,
            feedback_notes=rating_data.feedback_notes
        )
        db.add(evaluation)
    else:
        summary.evaluation.user_rating = rating_data.rating
        summary.evaluation.feedback_notes = rating_data.feedback_notes

    db.commit()
    return {"message": "Rating saved successfully."}
