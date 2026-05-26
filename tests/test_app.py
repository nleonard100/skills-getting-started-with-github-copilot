import copy
import urllib.parse

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Arrange: preserve the original in-memory activities and restore after each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    # Arrange
    # (client and activities fixture are ready)

    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success():
    # Arrange
    email = "test_user@mergington.edu"
    activity_name = "Chess Club"
    quoted = urllib.parse.quote(activity_name, safe="")
    assert email not in activities[activity_name]["participants"]

    # Act
    resp = client.post(f"/activities/{quoted}/signup?email={email}")

    # Assert
    assert resp.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert "Signed up" in resp.json().get("message", "")


def test_signup_duplicate():
    # Arrange
    email = "dup_user@mergington.edu"
    activity_name = "Programming Class"
    quoted = urllib.parse.quote(activity_name, safe="")
    activities[activity_name]["participants"].append(email)

    # Act
    resp = client.post(f"/activities/{quoted}/signup?email={email}")

    # Assert
    assert resp.status_code == 400
    assert email in activities[activity_name]["participants"]


def test_delete_participant_success():
    # Arrange
    email = "delete_me@mergington.edu"
    activity_name = "Gym Class"
    quoted = urllib.parse.quote(activity_name, safe="")
    activities[activity_name]["participants"].append(email)
    assert email in activities[activity_name]["participants"]

    # Act
    resp = client.delete(f"/activities/{quoted}/participants?email={email}")

    # Assert
    assert resp.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_delete_nonexistent():
    # Arrange
    email = "not_exists@mergington.edu"
    activity_name = "Art Studio"
    quoted = urllib.parse.quote(activity_name, safe="")
    assert email not in activities[activity_name]["participants"]

    # Act
    resp = client.delete(f"/activities/{quoted}/participants?email={email}")

    # Assert
    assert resp.status_code == 400
