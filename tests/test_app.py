import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"].endswith("/static/index.html")

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert len(activities) > 0

def test_signup_success():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

def test_signup_duplicate():
    activity_name = "Programming Class"
    email = "emma@mergington.edu"  # Already registered
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_signup_nonexistent_activity():
    activity_name = "NonexistentClub"
    email = "student@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_signup_full_activity():
    # First, fill up an activity
    activity_name = "Chess Club"
    response = client.get("/activities")
    activities = response.json()
    current_participants = len(activities[activity_name]["participants"])
    max_participants = activities[activity_name]["max_participants"]
    
    # Add participants until full
    for i in range(max_participants - current_participants):
        email = f"filler{i}@mergington.edu"
        client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Try to add one more
    email = "onemorestudent@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert "full" in response.json()["detail"].lower()

def test_unregister_success():
    activity_name = "Programming Class"
    email = "emma@mergington.edu"  # Known participant
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

def test_unregister_nonexistent_participant():
    activity_name = "Chess Club"
    email = "nonexistent@mergington.edu"
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_nonexistent_activity():
    activity_name = "NonexistentClub"
    email = "student@mergington.edu"
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()