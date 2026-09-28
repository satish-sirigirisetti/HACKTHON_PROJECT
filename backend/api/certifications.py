"""Certification and learning-path catalog endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.catalog import CertificationRead
from backend.services.certification_service import list_certifications

router = APIRouter(prefix="/certifications", tags=["certifications"])


@router.get("", response_model=list[CertificationRead])
def read_certifications(session: Session = Depends(get_db)) -> list[CertificationRead]:
	return list_certifications(session)