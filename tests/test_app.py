from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import app, activities

INITIAL_ACTIVITIES = deepcopy(activities)


def setup_function():
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_initial_activity_data():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "Programming Class" in payload
    assert "Gym Class" in payload
    assert payload["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert payload["Chess Club"]["max_participants"] == 12
    assert "michael@mergington.edu" in payload["Chess Club"]["participants"]


def test_signup_for_activity_adds_new_participant():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    email = "alex@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    follow_up_response = client.get("/activities")
    assert follow_up_response.status_code == 200
    activity_payload = follow_up_response.json()[activity_name]
    assert email in activity_payload["participants"]
    assert len(activity_payload["participants"]) == 3


def test_signup_for_invalid_activity_returns_404():
    # Arrange
    client = TestClient(app)
    activity_name = "Not a Real Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
