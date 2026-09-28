"""Retrieval-grounded career assistant endpoint."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.ai.career_assistant import (
	AssistantProviderError,
	AssistantStudentNotFoundError,
	answer_career_question,
)
from backend.database.database import get_db
from backend.schemas.assistant import AssistantAnswer, AssistantQuestion

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("", response_model=AssistantAnswer)
def ask_career_assistant(
	payload: AssistantQuestion, session: Session = Depends(get_db)
) -> AssistantAnswer:
	try:
		return answer_career_question(session, payload.student_id, payload.message)
	except AssistantStudentNotFoundError as error:
		raise HTTPException(status_code=404, detail="Student not found") from error
	except AssistantProviderError as error:
		raise HTTPException(
			status_code=502, detail="The configured Gemini provider is unavailable"
		) from error