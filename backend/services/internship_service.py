"""Internship catalog lookup for explicitly sample-only listings."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import Internship


def list_internships(session: Session) -> list[Internship]:
	return list(session.scalars(select(Internship).order_by(Internship.title)))