import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

def test_root_redirect():
    # Arrange
    # No special setup needed

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    # Arrange
    # Activities are predefined in the app

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure
    activity = data["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)

def test_successful_signup():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    initial_participants = activities[activity_name]["participants"].copy()

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    # Check side effect
    assert email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == len(initial_participants) + 1

def test_signup_activity_not_found():
    # Arrange
    activity_name = "NonExistent Activity"
    email = "test@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_signup_already_signed_up():
    # Arrange
    activity_name = "Programming Class"
    email = "emma@mergington.edu"  # Already in participants

    # Act
    response = client.post(f"/activities/{activity_name}/signup", json={"email": email})

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up" in data["detail"]

def test_successful_participant_removal():
    # Arrange
    activity_name = "Gym Class"
    email = "john@mergington.edu"  # Already in participants
    initial_participants = activities[activity_name]["participants"].copy()

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    # Check side effect
    assert email not in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == len(initial_participants) - 1

def test_remove_participant_activity_not_found():
    # Arrange
    activity_name = "NonExistent Activity"
    email = "test@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_remove_participant_not_found():
    # Arrange
    activity_name = "Soccer Club"
    email = "nonexistent@mergington.edu"  # Not in participants

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Participant not found" in data["detail"]