from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_unregister_participant_removes_email_from_activity():
    email = "temp-register@mergington.edu"

    register_response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )
    assert register_response.status_code == 200

    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"

    activities_response = client.get("/activities")
    assert activities_response.status_code == 200
    assert email not in activities_response.json()["Chess Club"]["participants"]


def test_unregister_unknown_participant_returns_404():
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "missing@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
