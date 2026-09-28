"""Side-by-side career requirements and student profile comparison."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import Skill, Student, StudentSkill
from backend.schemas.comparison import CareerComparisonRead
from backend.services.career_service import get_career_detail


def compare_careers(
    session: Session, student_id: int, career_ids: list[int]
) -> CareerComparisonRead:
    if len(career_ids) not in (2, 3) or len(set(career_ids)) != len(career_ids):
        raise ValueError("Choose two or three different careers")
    if session.get(Student, student_id) is None:
        raise LookupError("Student not found")

    career_details = []
    for career_id in career_ids:
        career = get_career_detail(session, career_id)
        if career is None:
            raise LookupError("Career not found")
        career_details.append(career)

    required_by_career = {
        career.id: {skill.name for skill in career.required_skills if skill.required}
        for career in career_details
    }
    shared = set.intersection(*required_by_career.values())
    distinct = {
        str(career.id): sorted(
            required_by_career[career.id]
            - set.union(
                *(skills for other_id, skills in required_by_career.items() if other_id != career.id)
            ),
            key=str.casefold,
        )
        for career in career_details
    }
    skill_levels = dict(
        session.execute(
            select(Skill.name, StudentSkill.proficiency)
            .join(StudentSkill, StudentSkill.skill_id == Skill.id)
            .where(StudentSkill.student_id == student_id)
        ).all()
    )
    return CareerComparisonRead(
        careers=career_details,
        shared_required_skills=sorted(shared, key=str.casefold),
        distinct_required_skills=distinct,
        student_skill_levels=skill_levels,
    )