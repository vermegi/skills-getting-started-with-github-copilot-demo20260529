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
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
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
    assert response.json() == {"detail": "Student is not signed up for this activity"}