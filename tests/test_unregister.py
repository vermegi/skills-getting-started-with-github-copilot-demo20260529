import src.app as app_module


def test_unregister_from_activity_succeeds(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    path = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(path, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}", "status": "removed_from_participants"}
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_from_activity_returns_404_when_activity_missing(client):
    # Arrange
    activity_name = "Debate Club"
    email = "student@mergington.edu"
    path = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(path, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_from_activity_returns_404_for_non_member(client):
    # Arrange
    activity_name = "Chess Club"
    email = "not.enrolled@mergington.edu"
    path = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(path, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not registered for this activity"}


def test_unregister_participant_promotes_first_waitlisted_student(client):
    # Arrange: add a student to the waitlist
    activity_name = "Chess Club"
    activity = app_module.activities[activity_name]
    waitlisted_email = "waitlisted.student@mergington.edu"
    activity["waitlist"].append(waitlisted_email)
    participant_email = "michael@mergington.edu"
    path = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(path, params={"email": participant_email})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "removed_from_participants"
    assert data["promoted"] == waitlisted_email
    assert participant_email not in app_module.activities[activity_name]["participants"]
    assert waitlisted_email in app_module.activities[activity_name]["participants"]
    assert waitlisted_email not in app_module.activities[activity_name]["waitlist"]


def test_unregister_waitlisted_student_removes_from_waitlist(client):
    # Arrange: add a student to the waitlist
    activity_name = "Chess Club"
    activity = app_module.activities[activity_name]
    waitlisted_email = "waitlisted.student@mergington.edu"
    activity["waitlist"].append(waitlisted_email)
    path = f"/activities/{activity_name}/participants"

    # Act
    response = client.delete(path, params={"email": waitlisted_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Removed {waitlisted_email} from the waitlist for {activity_name}",
        "status": "removed_from_waitlist"
    }
    assert waitlisted_email not in app_module.activities[activity_name]["waitlist"]