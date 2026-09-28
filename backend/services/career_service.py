"""Career catalog lookup."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import Career, CareerSkill, Skill
from backend.schemas.career import CareerDetailRead, CareerSkillRead


def list_careers(session: Session) -> list[Career]:
    return list(session.scalars(select(Career).order_by(Career.name)))


def get_career_detail(session: Session, career_id: int) -> CareerDetailRead | None:
    career = session.get(Career, career_id)
    if career is None:
        return None
    skills = session.execute(
        select(Skill.name, CareerSkill.importance, CareerSkill.required)
        .join(CareerSkill, CareerSkill.skill_id == Skill.id)
        .where(CareerSkill.career_id == career_id)
        .order_by(CareerSkill.required.desc(), Skill.name)
    ).all()
    return CareerDetailRead(
        id=career.id,
        name=career.name,
        description=career.description,
        category=career.category,
        required_skills=[
            CareerSkillRead(name=name, importance=importance, required=required)
            for name, importance, required in skills
        ],
    )