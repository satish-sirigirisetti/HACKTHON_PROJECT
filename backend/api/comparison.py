"""Career comparison endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.comparison import CareerComparisonRead
from backend.services.comparison_service import compare_careers

router = APIRouter(prefix="/comparison", tags=["comparison"])


@router.get("", response_model=CareerComparisonRead)
def read_comparison(
	student_id: int = Query(gt=0),
	career_ids: list[int] = Query(min_length=2, max_length=3),
	session: Session = Depends(get_db),
) -> CareerComparisonRead:
	try:
		return compare_careers(session, student_id, career_ids)
	except LookupError as error:
		raise HTTPException(status_code=404, detail=str(error)) from error
	except ValueError as error:
		raise HTTPException(status_code=422, detail=str(error)) from error