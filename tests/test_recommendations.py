"""Recommendation baseline tests."""

from backend.database.models import Career, CareerSkill, Skill, Student, StudentSkill
from backend.services.recommendation_service import recommend_careers


def test_recommendations_rank_required_skill_overlap(test_engine):
    from sqlalchemy.orm import Session

    with Session(test_engine) as session:
        python = Skill(name="Python")
        sql = Skill(name="SQL")
        student = Student(name="Alex Student", email="alex@example.edu")
        analyst = Career(name="Data Analyst", description="Analyze data", category="Data")
        engineer = Career(name="ML Engineer", description="Build models", category="AI & ML")
        session.add_all([python, sql, student, analyst, engineer])
        session.flush()
        session.add_all(
            [
                StudentSkill(student_id=student.id, skill_id=python.id, proficiency=1.0),
                CareerSkill(career_id=analyst.id, skill_id=python.id),
                CareerSkill(career_id=analyst.id, skill_id=sql.id),
                CareerSkill(career_id=engineer.id, skill_id=python.id),
            ]
        )
        session.commit()

        results = recommend_careers(session, student.id)
        assert results is not None
        assert results[0].career_name == "ML Engineer"
        assert results[0].match_score == 1.0


def test_missing_student_returns_none(test_engine):
    from sqlalchemy.orm import Session

    with Session(test_engine) as session:
        assert recommend_careers(session, 999) is None


def test_student_api_recommendations_explain_match(client, test_engine):
    from sqlalchemy.orm import Session

    created = client.post(
        "/api/students",
        json={"name": "Casey Student", "email": "casey@example.edu", "skills": [{"name": "Python"}]},
    ).json()
    with Session(test_engine) as session:
        skill = session.query(Skill).filter_by(name="Python").one()
        career = Career(name="Python Career", description="Uses Python", category="Software")
        session.add(career)
        session.flush()
        session.add(CareerSkill(career_id=career.id, skill_id=skill.id))
        session.commit()

    response = client.get(f"/api/recommendations/{created['id']}")
    assert response.status_code == 200
    assert response.json()[0]["matched_skills"] == ["Python"]
    assert "not an ML prediction" in response.json()[0]["method"]