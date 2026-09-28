"""Student API persistence and validation tests."""


def test_create_and_retrieve_student(client):
    response = client.post(
        "/api/students",
        json={
            "name": "Jordan Lee",
            "email": "JORDAN@example.edu",
            "major": "Computer Science",
            "skills": [{"name": "Python", "proficiency": 0.8}],
        },
    )
    assert response.status_code == 201
    created = response.json()
    assert created["email"] == "jordan@example.edu"

    retrieved = client.get(f"/api/students/{created['id']}")
    assert retrieved.status_code == 200
    assert retrieved.json()["name"] == "Jordan Lee"
    assert retrieved.json()["skills"] == [{"name": "Python", "proficiency": 0.8}]


def test_student_input_validation(client):
    response = client.post(
        "/api/students",
        json={"name": " ", "email": "not-an-email", "graduation_year": 1800},
    )
    assert response.status_code == 422


def test_student_rejects_duplicate_skills(client):
    response = client.post(
        "/api/students",
        json={
            "name": "Jordan Lee",
            "email": "jordan@example.edu",
            "skills": [{"name": "Python"}, {"name": "python"}],
        },
    )
    assert response.status_code == 422


def test_replace_student_profile(client):
    created = client.post(
        "/api/students", json={"name": "Jordan Lee", "email": "jordan@example.edu"}
    ).json()
    response = client.put(
        f"/api/students/{created['id']}",
        json={
            "name": "Jordan Lee",
            "email": "jordan@example.edu",
            "major": "Computer Science",
            "skills": [{"name": "SQL", "proficiency": 0.7}],
        },
    )
    assert response.status_code == 200
    assert response.json()["major"] == "Computer Science"
    assert response.json()["skills"] == [{"name": "SQL", "proficiency": 0.7}]


def test_duplicate_email_returns_conflict(client):
    student = {"name": "Jordan Lee", "email": "jordan@example.edu"}
    assert client.post("/api/students", json=student).status_code == 201
    assert client.post("/api/students", json=student).status_code == 409