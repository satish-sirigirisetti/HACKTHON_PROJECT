"""Core API and schema initialization tests."""

from sqlalchemy import inspect

from backend.database.database import Base


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "CareerAI"}


def test_single_service_serves_frontend_and_static_modules(client):
    page = client.get("/")
    script = client.get("/js/api.js")

    assert page.status_code == 200
    assert "CareerAI" in page.text
    assert script.status_code == 200
    assert "defaultApiBase" in script.text


def test_cors_allows_roadmap_progress_patch(client):
    response = client.options(
        "/api/roadmaps/1/1/items/1",
        headers={
            "Origin": "http://127.0.0.1:5500",
            "Access-Control-Request-Method": "PATCH",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-methods"]
    assert "PATCH" in response.headers["access-control-allow-methods"]


def test_database_initialization(test_engine):
    expected = {
        "students", "skills", "student_skills", "careers", "career_skills",
        "assessments", "assessment_questions", "assessment_results", "projects",
        "certifications", "internships", "learning_resources", "roadmaps",
        "roadmap_items", "industry_trends",
    }
    assert expected <= set(inspect(test_engine).get_table_names())
    assert expected <= set(Base.metadata.tables)