"""Student skill-gap analysis endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.roadmap import SkillGapRead
from backend.services.skill_gap_service import analyze_skill_gaps

router = APIRouter(prefix="/skill-gaps", tags=["skill gaps"])


@router.get("/{student_id}", response_model=SkillGapRead)
def read_skill_gaps(
	student_id: int, career_id: int, session: Session = Depends(get_db)
) -> SkillGapRead:
	try:
		return analyze_skill_gaps(session, student_id, career_id)
	except LookupError as error:
		raise HTTPException(status_code=404, detail=str(error)) from error