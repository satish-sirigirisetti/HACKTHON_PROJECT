"""Load the versioned career and skill catalog CSV files idempotently."""

import csv
from pathlib import Path

from sqlalchemy import select

from backend.database.database import SessionLocal, initialize_database
from backend.database.models import (
    Assessment,
    AssessmentQuestion,
    Certification,
    Career,
    CareerSkill,
    IndustryTrend,
    Internship,
    LearningResource,
    Project,
    Skill,
)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
ASSESSMENT_OPTIONS = [
    {"label": "No experience yet", "proficiency": 0.0},
    {"label": "Beginner", "proficiency": 0.25},
    {"label": "Developing", "proficiency": 0.5},
    {"label": "Confident", "proficiency": 0.75},
    {"label": "Advanced", "proficiency": 1.0},
]


def _rows(filename: str) -> list[dict[str, str]]:
    with (DATA_DIR / filename).open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def seed_catalog() -> None:
    """Upsert career and skill catalog records and their requirement edges."""
    initialize_database()
    with SessionLocal() as session:
        skills = {
            row["name"]: session.scalar(select(Skill).where(Skill.name == row["name"]))
            for row in _rows("skills.csv")
        }
        for row in _rows("skills.csv"):
            if skills[row["name"]] is None:
                skill = Skill(name=row["name"], category=row["category"], description=row["description"])
                session.add(skill)
                skills[row["name"]] = skill
        careers = {
            row["name"]: session.scalar(select(Career).where(Career.name == row["name"]))
            for row in _rows("careers.csv")
        }
        for row in _rows("careers.csv"):
            career = careers[row["name"]]
            if career is None:
                career = Career(name=row["name"], description=row["description"], category=row["category"])
                session.add(career)
                careers[row["name"]] = career
        session.flush()
        for row in _rows("career_skills.csv"):
            career = careers[row["career_name"]]
            skill = skills[row["skill_name"]]
            existing = session.scalar(
                select(CareerSkill).where(
                    CareerSkill.career_id == career.id,
                    CareerSkill.skill_id == skill.id,
                )
            )
            if existing is None:
                session.add(
                    CareerSkill(
                        career_id=career.id,
                        skill_id=skill.id,
                        importance=float(row["importance"]),
                        required=row["required"].casefold() == "true",
                    )
                )
        assessment = session.scalar(
            select(Assessment).where(Assessment.title == "Career foundations skill self-assessment")
        )
        if assessment is None:
            assessment = Assessment(
                title="Career foundations skill self-assessment",
                description="A self-reported snapshot of foundational technical skills.",
            )
            session.add(assessment)
            session.flush()
        for row in _rows("assessment_questions.csv"):
            skill = next(
                (candidate for name, candidate in skills.items() if name.casefold() == row["skill_name"].casefold()),
                None,
            )
            if skill is None:
                continue
            existing = session.scalar(
                select(AssessmentQuestion).where(
                    AssessmentQuestion.assessment_id == assessment.id,
                    AssessmentQuestion.prompt == row["prompt"],
                )
            )
            if existing is None:
                session.add(
                    AssessmentQuestion(
                        assessment_id=assessment.id,
                        prompt=row["prompt"],
                        skill_id=skill.id,
                        question_type="self_report",
                        options=ASSESSMENT_OPTIONS,
                    )
                )
        for row in _rows("projects.csv"):
            project = session.scalar(select(Project).where(Project.title == row["title"]))
            values = {
                "description": row["description"],
                "skill_names": [name.strip() for name in row["skills"].split(";") if name.strip()],
            }
            if project is None:
                session.add(Project(title=row["title"], **values))
            else:
                for field, value in values.items():
                    setattr(project, field, value)
        for row in _rows("certifications.csv"):
            certification = session.scalar(
                select(Certification).where(Certification.name == row["name"])
            )
            values = {
                "provider": row["provider"],
                "description": row["description"],
                "skills": [name.strip() for name in row["skills"].split(";") if name.strip()],
                "url": row["url"] or None,
            }
            if certification is None:
                session.add(Certification(name=row["name"], **values))
            else:
                for field, value in values.items():
                    setattr(certification, field, value)
        for row in _rows("internships.csv"):
            internship = session.scalar(
                select(Internship).where(
                    Internship.title == row["title"],
                    Internship.organization == row["organization"],
                )
            )
            values = {
                "description": row["description"],
                "skills": [name.strip() for name in row["skills"].split(";") if name.strip()],
                "source_url": row["source_url"] or None,
            }
            if internship is None:
                session.add(
                    Internship(title=row["title"], organization=row["organization"], **values)
                )
            else:
                for field, value in values.items():
                    setattr(internship, field, value)
        for row in _rows("learning_resources.csv"):
            resource = session.scalar(
                select(LearningResource).where(
                    LearningResource.title == row["title"],
                    LearningResource.skill_name == row["skill_name"],
                )
            )
            values = {
                "provider": row["provider"],
                "resource_type": row["resource_type"],
                "url": row["url"] or None,
            }
            if resource is None:
                session.add(
                    LearningResource(
                        title=row["title"], skill_name=row["skill_name"], **values
                    )
                )
            else:
                for field, value in values.items():
                    setattr(resource, field, value)
        for row in _rows("industry_trends.csv"):
            trend = session.scalar(
                select(IndustryTrend).where(
                    IndustryTrend.topic == row["topic"], IndustryTrend.source == row["source"]
                )
            )
            values = {
                "summary": row["summary"],
                "is_sample": row["is_sample"].casefold() == "true",
            }
            if trend is None:
                session.add(
                    IndustryTrend(topic=row["topic"], source=row["source"], **values)
                )
            else:
                trend.summary = values["summary"]
                trend.is_sample = values["is_sample"]
        session.commit()


if __name__ == "__main__":
    seed_catalog()
    print("CareerAI career and skill catalog seeded.")