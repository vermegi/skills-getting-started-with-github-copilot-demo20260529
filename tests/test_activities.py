def test_get_activities_returns_activity_mapping(client):
    # Arrange
    path = "/activities"

    # Act
    response = client.get(path)
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert len(payload) == 8
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]


def test_get_activities_contains_expected_fields(client):
    # Arrange
    path = "/activities"
    required_fields = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get(path)
    payload = response.json()

    # Assert
    assert response.status_code == 200
    for activity in payload.values():
        assert required_fields.issubset(activity.keys())