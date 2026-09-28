"""Structured project catalog lookup."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import Project


def list_projects(session: Session) -> list[Project]:
	return list(session.scalars(select(Project).order_by(Project.title)))