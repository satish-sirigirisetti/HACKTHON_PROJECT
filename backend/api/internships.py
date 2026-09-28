"""Sample internship catalog endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.catalog import InternshipRead
from backend.services.internship_service import list_internships

router = APIRouter(prefix="/internships", tags=["internships"])


@router.get("", response_model=list[InternshipRead])
def read_internships(session: Session = Depends(get_db)) -> list[InternshipRead]:
	return list_internships(session)