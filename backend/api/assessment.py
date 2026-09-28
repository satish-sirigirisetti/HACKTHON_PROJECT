"""Skill self-assessment question and submission endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.assessment import (
	AssessmentQuestionRead,
	AssessmentResultRead,
	AssessmentSubmission,
)
from backend.services.assessment_service import (
	AssessmentNotFoundError,
	InvalidAssessmentAnswerError,
	IncompleteAssessmentError,
	get_assessment_questions,
	submit_assessment,
)

router = APIRouter(prefix="/assessment", tags=["assessment"])


@router.get("/questions", response_model=list[AssessmentQuestionRead])
def read_assessment_questions(session: Session = Depends(get_db)) -> list[AssessmentQuestionRead]:
	return get_assessment_questions(session)


@router.post("/submit", response_model=AssessmentResultRead, status_code=status.HTTP_201_CREATED)
def submit_skill_assessment(
	payload: AssessmentSubmission, session: Session = Depends(get_db)
) -> AssessmentResultRead:
	try:
		return submit_assessment(session, payload)
	except LookupError as error:
		raise HTTPException(status_code=404, detail=str(error)) from error
	except IncompleteAssessmentError as error:
		raise HTTPException(
			status_code=422, detail="Answer every question in the assessment before submitting"
		) from error
	except InvalidAssessmentAnswerError as error:
		raise HTTPException(
			status_code=422, detail="Choose one of the listed proficiency options for every question"
		) from error
	except AssessmentNotFoundError as error:
		raise HTTPException(
			status_code=503, detail="Assessment questions have not been seeded"
		) from error