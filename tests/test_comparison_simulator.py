"""Career comparison and non-persistent simulation tests."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import Career, CareerSkill, Skill, Student, StudentSkill


def seed_career_scenarios(engine):
    with Session(engine) as session:
        student = Student(name="Riley Student", email="riley@example.edu")
        python = Skill(name="Python")
        sql = Skill(name="SQL")
        backend = Career(name="Backend Engineer", description="Build APIs", category="Software")
        analyst = Career(name="Data Analyst", description="Analyze information", category="Data")
        session.add_all([student, python, sql, backend, analyst])
        session.flush()
        session.add_all(
            [
                StudentSkill(student_id=student.id, skill_id=python.id, proficiency=0.25),
                CareerSkill(career_id=backend.id, skill_id=python.id, importance=1, required=True),
                CareerSkill(career_id=backend.id, skill_id=sql.id, importance=1, required=True),
                CareerSkill(career_id=analyst.id, skill_id=python.id, importance=1, required=True),
            ]
        )
        session.commit()
        return student.id, backend.id, analyst.id


def test_compare_careers_shows_shared_and_distinct_requirements(client, test_engine):
    student_id, backend_id, analyst_id = seed_career_scenarios(test_engine)

    response = client.get(
        f"/api/comparison?student_id={student_id}&career_ids={backend_id}&career_ids={analyst_id}"
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["shared_required_skills"] == ["Python"]
    assert payload["distinct_required_skills"][str(backend_id)] == ["SQL"]
    assert payload["student_skill_levels"] == {"Python": 0.25}


def test_what_if_simulation_does_not_change_saved_profile(client, test_engine):
    student_id, backend_id, analyst_id = seed_career_scenarios(test_engine)

    response = client.post(
        f"/api/simulator/{student_id}",
        json={"skills": [{"name": "SQL", "proficiency": 1.0}]},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "not saved" in payload["method"]
    current = {career["career_id"]: career for career in payload["baseline"]}
    hypothetical = {career["career_id"]: career for career in payload["simulated"]}
    assert hypothetical[backend_id]["match_score"] > current[backend_id]["match_score"]
    with Session(test_engine) as session:
        student = session.get(Student, student_id)
        levels = {
            session.get(Skill, item.skill_id).name: item.proficiency
            for item in session.scalars(
                select(StudentSkill).where(StudentSkill.student_id == student_id)
            )
        }
        assert levels == {"Python": 0.25}
        assert student.email == "riley@example.edu"


def test_comparison_requires_distinct_careers(client, test_engine):
    student_id, career_id, _ = seed_career_scenarios(test_engine)
    response = client.get(
        f"/api/comparison?student_id={student_id}&career_ids={career_id}&career_ids={career_id}"
    )
    assert response.status_code == 422