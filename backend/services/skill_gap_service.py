"""Required-skill gap analysis and resource matching."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import Career, CareerSkill, LearningResource, Skill, Student, StudentSkill
from backend.schemas.roadmap import SkillGapItem, SkillGapRead, SkillGapResource


def analyze_skill_gaps(session: Session, student_id: int, career_id: int) -> SkillGapRead:
    """Compare required career proficiencies with the student's self-reported levels."""
    student = session.get(Student, student_id)
    if student is None:
        raise LookupError("Student not found")
    career = session.get(Career, career_id)
    if career is None:
        raise LookupError("Career not found")

    requirements = session.execute(
        select(Skill.id, Skill.name, Skill.description, CareerSkill.importance, StudentSkill.proficiency)
        .join(CareerSkill, CareerSkill.skill_id == Skill.id)
        .outerjoin(
            StudentSkill,
            (StudentSkill.skill_id == Skill.id) & (StudentSkill.student_id == student_id),
        )
        .where(CareerSkill.career_id == career_id, CareerSkill.required.is_(True))
    ).all()

    gaps: list[SkillGapItem] = []
    for skill_id, skill_name, _, importance, current_level in requirements:
        proficiency = current_level or 0.0
        if proficiency >= 1.0:
            continue
        resource_rows = session.scalars(
            select(LearningResource)
            .where(LearningResource.skill_name.ilike(skill_name))
            .order_by(LearningResource.title)
        ).all()
        gaps.append(
            SkillGapItem(
                skill_id=skill_id,
                skill_name=skill_name,
                proficiency=proficiency,
                importance=importance,
                priority=round(importance * (1.0 - proficiency), 3),
                resources=[
                    SkillGapResource(
                        title=resource.title,
                        provider=resource.provider,
                        resource_type=resource.resource_type,
                        url=resource.url,
                    )
                    for resource in resource_rows
                ],
            )
        )

    gaps.sort(key=lambda gap: (-gap.priority, gap.skill_name.casefold()))
    return SkillGapRead(
        student_id=student.id,
        career_id=career.id,
        career_name=career.name,
        gaps=gaps,
    )