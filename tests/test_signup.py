import src.app as app_module


def _fill_activity_to_capacity(activity_name):
    """Helper to fill an activity's participant list to max_participants."""
    activity = app_module.activities[activity_name]
    while len(activity["participants"]) < activity["max_participants"]:
        activity["participants"].append(f"filler{len(activity['participants'])}@mergington.edu")


def test_signup_for_activity_succeeds(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    path = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(path, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}", "status": "enrolled"}
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_for_activity_returns_404_when_activity_missing(client):
    # Arrange
    activity_name = "Debate Club"
    email = "student@mergington.edu"
    path = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(path, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_for_activity_returns_400_for_duplicate_student(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    path = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(path, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_signup_places_student_on_waitlist_when_activity_is_full(client):
    # Arrange: fill Chess Club (max 12) to capacity
    activity_name = "Chess Club"
    _fill_activity_to_capacity(activity_name)
    email = "waitlisted.student@mergington.edu"
    path = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(path, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"{email} has been added to the waitlist for {activity_name}",
        "status": "waitlisted"
    }
    assert email not in app_module.activities[activity_name]["participants"]
    assert email in app_module.activities[activity_name]["waitlist"]


def test_signup_returns_400_for_duplicate_waitlisted_student(client):
    # Arrange: fill activity to capacity and add student to waitlist
    activity_name = "Chess Club"
    _fill_activity_to_capacity(activity_name)
    email = "waitlisted.student@mergington.edu"
    app_module.activities[activity_name]["waitlist"].append(email)
    path = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(path, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already on the waitlist for this activity"}