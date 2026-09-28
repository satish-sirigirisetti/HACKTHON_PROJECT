"""Personalized learning roadmap endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.roadmap import RoadmapCreate, RoadmapItemUpdate, RoadmapRead
from backend.services.roadmap_service import (
	create_roadmap,
	get_latest_roadmap,
	set_roadmap_item_completed,
)

router = APIRouter(prefix="/roadmaps", tags=["roadmaps"])


@router.post("/{student_id}", response_model=RoadmapRead, status_code=status.HTTP_201_CREATED)
def generate_roadmap(
	student_id: int, payload: RoadmapCreate, session: Session = Depends(get_db)
) -> RoadmapRead:
	try:
		return create_roadmap(session, student_id, payload.career_id)
	except LookupError as error:
		raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{student_id}", response_model=RoadmapRead | None)
def read_latest_roadmap(
	student_id: int, session: Session = Depends(get_db)
) -> RoadmapRead | None:
	try:
		return get_latest_roadmap(session, student_id)
	except LookupError as error:
		raise HTTPException(status_code=404, detail=str(error)) from error


@router.patch("/{student_id}/{roadmap_id}/items/{item_id}", response_model=RoadmapRead)
def update_roadmap_item(
	student_id: int,
	roadmap_id: int,
	item_id: int,
	payload: RoadmapItemUpdate,
	session: Session = Depends(get_db),
) -> RoadmapRead:
	try:
		return set_roadmap_item_completed(
			session, student_id, roadmap_id, item_id, payload.completed
		)
	except LookupError as error:
		raise HTTPException(status_code=404, detail=str(error)) from error