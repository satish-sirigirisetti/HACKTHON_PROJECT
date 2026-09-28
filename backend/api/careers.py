"""Career catalog endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.career import CareerDetailRead, CareerRead
from backend.services.career_service import get_career_detail, list_careers

router = APIRouter(prefix="/careers", tags=["careers"])


@router.get("", response_model=list[CareerRead])
def read_careers(session: Session = Depends(get_db)) -> list[CareerRead]:
    return list_careers(session)


@router.get("/{career_id}", response_model=CareerDetailRead)
def read_career_detail(career_id: int, session: Session = Depends(get_db)) -> CareerDetailRead:
    career = get_career_detail(session, career_id)
    if career is None:
        raise HTTPException(status_code=404, detail="Career not found")
    return career