"""Data-driven, explainable skills-overlap recommendation baseline."""

from collections.abc import Mapping

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import Career, CareerSkill, Skill, Student, StudentSkill
from backend.recommendation.career_matcher import match_required_skills
from backend.recommendation.ranking import rank_recommendations
from backend.schemas.recommendation import CareerRecommendation


def recommend_careers(
    session: Session, student_id: int
) -> list[CareerRecommendation] | None:
    student = session.get(Student, student_id)
    if student is None:
        return None
    student_skills = dict(
        session.execute(
            select(Skill.name, StudentSkill.proficiency)
            .join(StudentSkill, StudentSkill.skill_id == Skill.id)
            .where(StudentSkill.student_id == student_id)
        ).all()
    )
    return recommend_careers_for_skills(session, student_skills)


def recommend_careers_for_skills(
    session: Session, student_skills: Mapping[str, float]
) -> list[CareerRecommendation]:
    """Rank careers for a profile vector without reading or mutating a student."""
    careers = session.scalars(select(Career).order_by(Career.name)).all()
    results: list[CareerRecommendation] = []
    for career in careers:
        requirements = session.execute(
            select(Skill.name, CareerSkill.importance, CareerSkill.required)
            .join(CareerSkill, CareerSkill.skill_id == Skill.id)
            .where(CareerSkill.career_id == career.id)
            .order_by(Skill.name)
        ).all()
        required = [(name, weight) for name, weight, is_required in requirements if is_required]
        if not required:
            continue
        match_score, matched, missing = match_required_skills(required, student_skills)
        results.append(
            CareerRecommendation(
                career_id=career.id,
                career_name=career.name,
                match_score=match_score,
                matched_skills=matched,
                missing_skills=missing,
            )
        )
    return rank_recommendations(results, limit=50)