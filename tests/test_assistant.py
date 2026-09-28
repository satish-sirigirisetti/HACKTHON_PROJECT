"""Career assistant retrieval and provider boundary tests."""

from sqlalchemy.orm import Session

from backend.database.models import LearningResource, Skill, Student


def seed_assistant_profile(engine):
    with Session(engine) as session:
        student = Student(
            name="Avery Student",
            email="avery@example.edu",
            major="Computer Science",
            target_role="ML Engineer",
        )
        python = Skill(name="Python", category="Programming", description="Write Python programs.")
        resource = LearningResource(
            title="Python language tutorial",
            provider="Python Software Foundation",
            resource_type="documentation",
            skill_name="Python",
            url="https://docs.python.org/3/tutorial/",
        )
        session.add_all([student, python, resource])
        session.commit()
        return student.id


def test_assistant_returns_retrieved_sources_without_faking_generation(
    client, test_engine, monkeypatch
):
    student_id = seed_assistant_profile(test_engine)
    monkeypatch.setattr("backend.ai.llm_service.settings.gemini_api_key", "")

    response = client.post(
        "/api/assistant",
        json={"student_id": student_id, "message": "Python language tutorial"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["generation_status"] == "retrieval_only"
    assert payload["sources"][0]["title"] == "Python language tutorial"
    assert "GEMINI_API_KEY" in payload["answer"]


def test_assistant_uses_provider_and_returns_context_citations(client, test_engine, monkeypatch):
    student_id = seed_assistant_profile(test_engine)
    observed_prompts = []

    def generate(prompt):
        observed_prompts.append(prompt)
        return "Start with the official tutorial [1]."

    monkeypatch.setattr("backend.ai.career_assistant.generate_text", generate)

    response = client.post(
        "/api/assistant",
        json={"student_id": student_id, "message": "Python language tutorial"},
    )

    assert response.status_code == 200
    assert response.json()["generation_status"] == "generated"
    assert response.json()["answer"] == "Start with the official tutorial [1]."
    assert "Student target role: ML Engineer" in observed_prompts[0]
    assert "Retrieved context:" in observed_prompts[0]


def test_assistant_requires_existing_student(client):
    response = client.post(
        "/api/assistant", json={"student_id": 999, "message": "Python tutorial"}
    )
    assert response.status_code == 404


def test_learning_question_prioritizes_learning_resource(client, test_engine, monkeypatch):
    student_id = seed_assistant_profile(test_engine)
    monkeypatch.setattr("backend.ai.llm_service.settings.gemini_api_key", "")

    response = client.post(
        "/api/assistant",
        json={"student_id": student_id, "message": "Where can I learn Python?"},
    )

    assert response.status_code == 200
    assert response.json()["sources"][0]["title"] == "Python language tutorial"