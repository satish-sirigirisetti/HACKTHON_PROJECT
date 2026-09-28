"""Skill-gap analysis API tests."""

from sqlalchemy.orm import Session

from backend.database.models import Career, CareerSkill, LearningResource, Skill, Student, StudentSkill


def test_skill_gaps_rank_missing_required_skills(client, test_engine):
	with Session(test_engine) as session:
		student = Student(name="Morgan Student", email="morgan@example.edu")
		python = Skill(name="Python")
		sql = Skill(name="SQL")
		career = Career(name="Data Engineer", description="Build data systems", category="Data")
		session.add_all([student, python, sql, career])
		session.flush()
		session.add_all(
			[
				StudentSkill(student_id=student.id, skill_id=python.id, proficiency=0.5),
				CareerSkill(career_id=career.id, skill_id=python.id, importance=1.0, required=True),
				CareerSkill(career_id=career.id, skill_id=sql.id, importance=0.8, required=True),
				LearningResource(
					title="SQL basics",
					provider="Example docs",
					resource_type="documentation",
					skill_name="SQL",
					url="https://example.edu/sql",
				),
			]
		)
		session.commit()
		student_id, career_id = student.id, career.id

	response = client.get(f"/api/skill-gaps/{student_id}?career_id={career_id}")

	assert response.status_code == 200
	payload = response.json()
	assert payload["career_name"] == "Data Engineer"
	assert [gap["skill_name"] for gap in payload["gaps"]] == ["SQL", "Python"]
	assert payload["gaps"][0]["priority"] == 0.8
	assert payload["gaps"][0]["resources"][0]["title"] == "SQL basics"


def test_skill_gaps_return_not_found_for_unknown_profile(client):
	response = client.get("/api/skill-gaps/999?career_id=1")
	assert response.status_code == 404