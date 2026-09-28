"""Canonical skill catalog lookup."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import Skill


def list_skills(session: Session) -> list[Skill]:
    return list(session.scalars(select(Skill).order_by(Skill.category, Skill.name)))