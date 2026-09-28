"""Project catalog endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.catalog import ProjectRead
from backend.services.project_service import list_projects

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead])
def read_projects(session: Session = Depends(get_db)) -> list[ProjectRead]:
	return list_projects(session)