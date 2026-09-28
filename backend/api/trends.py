"""Industry trend endpoints for sourced qualitative and labeled sample data."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.catalog import IndustryTrendRead
from backend.services.trend_service import list_trends

router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("", response_model=list[IndustryTrendRead])
def read_trends(session: Session = Depends(get_db)) -> list[IndustryTrendRead]:
	return list_trends(session)