"""Learning roadmap generation and progress tests."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import Career, CareerSkill, LearningResource, Roadmap, RoadmapItem, Skill, Student


def test_generate_and_update_roadmap(client, test_engine):
	with Session(test_engine) as session:
		student = Student(name="Jamie Student", email="jamie@example.edu")
		python = Skill(name="Python", description="Write Python programs")
		career = Career(name="ML Engineer", description="Build models", category="AI & ML")
		session.add_all([student, python, career])
		session.flush()
		session.add(
			CareerSkill(career_id=career.id, skill_id=python.id, importance=1.0, required=True)
		)
		session.add(
			LearningResource(
				title="Python tutorial",
				provider="Python docs",
				resource_type="documentation",
				skill_name="Python",
				url="https://docs.python.org/3/tutorial/",
			)
		)
		session.commit()
		student_id, career_id = student.id, career.id

	created = client.post(
		f"/api/roadmaps/{student_id}", json={"career_id": career_id}
	)
	assert created.status_code == 201
	roadmap = created.json()
	assert roadmap["target_role"] == "ML Engineer"
	assert roadmap["items"][0]["title"] == "Python"
	assert roadmap["items"][0]["resource"]["title"] == "Python tutorial"

	updated = client.patch(
		f"/api/roadmaps/{student_id}/{roadmap['id']}/items/{roadmap['items'][0]['id']}",
		json={"completed": True},
	)
	assert updated.status_code == 200
	assert updated.json()["items"][0]["completed"] is True
	with Session(test_engine) as session:
		assert session.scalar(select(Roadmap).where(Roadmap.id == roadmap["id"])) is not None
		assert session.scalar(select(RoadmapItem).where(RoadmapItem.roadmap_id == roadmap["id"])).completed