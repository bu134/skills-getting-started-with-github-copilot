from copy import deepcopy
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

import src.app as app_module
from src.app import app


BASELINE_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(deepcopy(BASELINE_ACTIVITIES))


client = TestClient(app)


def test_get_activities_returns_activity_data():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert "participants" in response.json()["Chess Club"]


def test_signup_registers_new_participant():
    # Arrange
    email = f"signup-{uuid4()}@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"

    # Act
    activities_response = client.get("/activities")

    # Assert
    assert activities_response.status_code == 200
    assert email in activities_response.json()["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    email = f"duplicate-{uuid4()}@mergington.edu"

    # Act
    first_response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert first_response.status_code == 200

    # Act
    second_response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_participant_removes_email_from_activity():
    # Arrange
    email = f"temp-register-{uuid4()}@mergington.edu"

    # Act
    register_response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert register_response.status_code == 200

    # Act
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"

    # Act
    activities_response = client.get("/activities")

    # Assert
    assert activities_response.status_code == 200
    assert email not in activities_response.json()["Chess Club"]["participants"]


def test_unregister_unknown_participant_returns_404():
    # Arrange
    email = "missing@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
