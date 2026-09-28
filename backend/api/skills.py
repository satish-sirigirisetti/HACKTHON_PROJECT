"""Canonical skill catalog endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.catalog import SkillRead
from backend.services.skill_service import list_skills

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[SkillRead])
def read_skills(session: Session = Depends(get_db)) -> list[SkillRead]:
    return list_skills(session)