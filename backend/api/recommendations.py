"""Explainable career recommendation endpoint."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.recommendation import CareerRecommendation
from backend.services.recommendation_service import recommend_careers

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{student_id}", response_model=list[CareerRecommendation])
def read_recommendations(
    student_id: int, session: Session = Depends(get_db)
) -> list[CareerRecommendation]:
    recommendations = recommend_careers(session, student_id)
    if recommendations is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return recommendations