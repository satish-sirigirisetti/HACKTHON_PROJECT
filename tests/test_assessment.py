"""Assessment question delivery, answer validation, and skill updates."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import (
    Assessment,
    AssessmentQuestion,
    AssessmentResult,
    Skill,
    Student,
    StudentSkill,
)


def seed_assessment(engine):
    with Session(engine) as session:
        python = Skill(name="Python", category="Programming")
        sql = Skill(name="SQL", category="Data")
        student = Student(name="Taylor Student", email="taylor@example.edu")
        assessment = Assessment(
            title="Career foundations skill self-assessment",
            description="Self-reported skill snapshot.",
        )
        session.add_all([python, sql, student, assessment])
        session.flush()
        options = [
            {"label": "Beginner", "proficiency": 0.25},
            {"label": "Confident", "proficiency": 0.75},
        ]
        questions = [
            AssessmentQuestion(
                assessment_id=assessment.id,
                prompt="How comfortable are you using Python?",
                skill_id=python.id,
                question_type="self_report",
                options=options,
            ),
            AssessmentQuestion(
                assessment_id=assessment.id,
                prompt="How comfortable are you querying data with SQL?",
                skill_id=sql.id,
                question_type="self_report",
                options=options,
            ),
        ]
        session.add_all(questions)
        session.commit()
        return student.id, [question.id for question in questions]


def test_assessment_questions_are_served_from_database(client, test_engine):
    _, question_ids = seed_assessment(test_engine)

    response = client.get("/api/assessment/questions")

    assert response.status_code == 200
    assert [question["id"] for question in response.json()] == question_ids
    assert response.json()[0]["skill_name"] == "Python"
    assert response.json()[0]["options"][1] == {"label": "Confident", "proficiency": 0.75}


def test_submission_persists_result_and_updates_student_skills(client, test_engine):
    student_id, question_ids = seed_assessment(test_engine)

    response = client.post(
        "/api/assessment/submit",
        json={
            "student_id": student_id,
            "answers": [
                {"question_id": question_ids[0], "proficiency": 0.75},
                {"question_id": question_ids[1], "proficiency": 0.25},
            ],
        },
    )

    assert response.status_code == 201
    assert response.json()["score"] == 0.5
    assert response.json()["skills_updated"] == ["Python", "SQL"]
    with Session(test_engine) as session:
        result = session.scalar(select(AssessmentResult).where(AssessmentResult.student_id == student_id))
        assert result is not None
        assert result.details["source"] == "self_report"
        proficiencies = {
            session.get(Skill, item.skill_id).name: item.proficiency
            for item in session.scalars(
                select(StudentSkill).where(StudentSkill.student_id == student_id)
            )
        }
        assert proficiencies == {"Python": 0.75, "SQL": 0.25}


def test_submission_requires_every_question(client, test_engine):
    student_id, question_ids = seed_assessment(test_engine)

    response = client.post(
        "/api/assessment/submit",
        json={
            "student_id": student_id,
            "answers": [{"question_id": question_ids[0], "proficiency": 0.5}],
        },
    )

    assert response.status_code == 422


def test_submission_rejects_invalid_or_duplicate_answers(client, test_engine):
    student_id, question_ids = seed_assessment(test_engine)
    invalid_proficiency = client.post(
        "/api/assessment/submit",
        json={"student_id": student_id, "answers": [{"question_id": question_ids[0], "proficiency": 1.2}]},
    )
    duplicate_question = client.post(
        "/api/assessment/submit",
        json={
            "student_id": student_id,
            "answers": [
                {"question_id": question_ids[0], "proficiency": 0.5},
                {"question_id": question_ids[0], "proficiency": 0.75},
            ],
        },
    )

    assert invalid_proficiency.status_code == 422
    assert duplicate_question.status_code == 422


def test_submission_rejects_rating_not_offered_by_question(client, test_engine):
    student_id, question_ids = seed_assessment(test_engine)

    response = client.post(
        "/api/assessment/submit",
        json={
            "student_id": student_id,
            "answers": [
                {"question_id": question_ids[0], "proficiency": 0.5},
                {"question_id": question_ids[1], "proficiency": 0.75},
            ],
        },
    )

    assert response.status_code == 422