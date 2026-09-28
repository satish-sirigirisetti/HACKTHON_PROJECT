"""Structured learning-path catalog lookup."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import Certification


def list_certifications(session: Session) -> list[Certification]:
	return list(session.scalars(select(Certification).order_by(Certification.name)))