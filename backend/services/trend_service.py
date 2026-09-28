"""Industry trend catalog lookup; sample records remain labeled as such."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import IndustryTrend


def list_trends(session: Session) -> list[IndustryTrend]:
	return list(session.scalars(select(IndustryTrend).order_by(IndustryTrend.topic)))