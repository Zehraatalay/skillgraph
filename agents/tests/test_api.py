from fastapi.testclient import TestClient

from api.dependencies import get_workflow
from api.main import app


class FakeWorkflow:
    def __init__(self):
        self.received_input = None

    def invoke(self, state):
        self.received_input = state

        return {
            "candidate_profile": {
                "skills": [],
            },
            "job_analyses": [],
            "results": [],
        }


def test_health_endpoint():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "skillgraph",
    }


def test_analyze_endpoint():
    fake_workflow = FakeWorkflow()

    app.dependency_overrides[get_workflow] = lambda: fake_workflow

    try:
        client = TestClient(app)

        response = client.post(
            "/analyze",
            json={
                "cv_text": "Python developer",
                "job_postings": [
                    {
                        "id": "job-001",
                        "title": "ML Engineer",
                        "company": "Example",
                        "description": "Python required",
                    }
                ],
            },
        )

        assert response.status_code == 200

        assert fake_workflow.received_input["cv_text"] == "Python developer"

        assert response.json()["candidate_profile"] == {
            "skills": [],
        }

    finally:
        app.dependency_overrides.clear()


def test_rejects_missing_candidate_input():
    client = TestClient(app)

    response = client.post(
        "/analyze",
        json={
            "job_postings": [
                {
                    "id": "job-001",
                    "title": "ML Engineer",
                    "company": "Example",
                    "description": "Python required",
                }
            ]
        },
    )

    assert response.status_code == 422


def test_rejects_empty_job_postings():
    client = TestClient(app)

    response = client.post(
        "/analyze",
        json={
            "cv_text": "Python developer",
            "job_postings": [],
        },
    )

    assert response.status_code == 422
