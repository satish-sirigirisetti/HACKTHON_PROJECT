"""Generate, retrieve, and update persistent learning roadmaps."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import Career, LearningResource, Roadmap, RoadmapItem, Student
from backend.schemas.roadmap import (
	RoadmapItemRead,
	RoadmapRead,
	SkillGapResource,
)
from backend.services.skill_gap_service import analyze_skill_gaps


def _roadmap_response(session: Session, roadmap: Roadmap) -> RoadmapRead:
	items = list(
		session.scalars(
			select(RoadmapItem)
			.where(RoadmapItem.roadmap_id == roadmap.id)
			.order_by(RoadmapItem.position)
		)
	)
	response_items: list[RoadmapItemRead] = []
	for item in items:
		resource = session.scalar(
			select(LearningResource)
			.where(LearningResource.skill_name.ilike(item.title))
			.order_by(LearningResource.title)
		)
		response_items.append(
			RoadmapItemRead(
				id=item.id,
				title=item.title,
				description=item.description,
				position=item.position,
				completed=item.completed,
				resource=(
					SkillGapResource(
						title=resource.title,
						provider=resource.provider,
						resource_type=resource.resource_type,
						url=resource.url,
					)
					if resource
					else None
				),
			)
		)
	return RoadmapRead(
		id=roadmap.id,
		title=roadmap.title,
		target_role=roadmap.target_role,
		created_at=roadmap.created_at,
		items=response_items,
	)


def create_roadmap(session: Session, student_id: int, career_id: int) -> RoadmapRead:
	"""Create ordered learning steps for the current required-skill gaps."""
	gaps = analyze_skill_gaps(session, student_id, career_id)
	roadmap = Roadmap(
		student_id=student_id,
		title=f"Learning plan for {gaps.career_name}",
		target_role=gaps.career_name,
	)
	session.add(roadmap)
	session.flush()
	for position, gap in enumerate(gaps.gaps, start=1):
		resource_note = (
			f" Start with {gap.resources[0].title} by {gap.resources[0].provider}."
			if gap.resources
			else " Choose a practice project or learning resource for this skill."
		)
		session.add(
			RoadmapItem(
				roadmap_id=roadmap.id,
				title=gap.skill_name,
				description=(
					f"Build from your current self-reported proficiency of "
					f"{gap.proficiency:.0%}; priority {gap.priority:.2f}." + resource_note
				),
				position=position,
			)
		)
	session.commit()
	session.refresh(roadmap)
	return _roadmap_response(session, roadmap)


def get_latest_roadmap(session: Session, student_id: int) -> RoadmapRead | None:
	"""Return the student's most recently generated roadmap, if present."""
	if session.get(Student, student_id) is None:
		raise LookupError("Student not found")
	roadmap = session.scalar(
		select(Roadmap)
		.where(Roadmap.student_id == student_id)
		.order_by(Roadmap.id.desc())
	)
	return _roadmap_response(session, roadmap) if roadmap else None


def set_roadmap_item_completed(
	session: Session, student_id: int, roadmap_id: int, item_id: int, completed: bool
) -> RoadmapRead:
	"""Update an item only when it belongs to the student's roadmap."""
	item = session.scalar(
		select(RoadmapItem)
		.join(Roadmap, Roadmap.id == RoadmapItem.roadmap_id)
		.where(
			Roadmap.id == roadmap_id,
			Roadmap.student_id == student_id,
			RoadmapItem.id == item_id,
		)
	)
	if item is None:
		raise LookupError("Roadmap item not found")
	item.completed = completed
	session.commit()
	roadmap = session.get(Roadmap, roadmap_id)
	return _roadmap_response(session, roadmap)