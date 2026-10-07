import pytest

NEW_EMAIL = "newstudent@mergington.edu"


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (302, 307)
    assert response.headers["location"] == expected_location


def test_get_activities_returns_all_activities_with_details(client):
    # Arrange
    expected_names = {"Chess Club", "Programming Class", "Gym Class"}
    expected_fields = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    data = response.json()
    assert response.status_code == 200
    assert expected_names <= set(data)
    for details in data.values():
        assert expected_fields <= set(details)


def test_signup_adds_participant(client):
    # Arrange
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": NEW_EMAIL})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {NEW_EMAIL} for {activity}"}
    participants = client.get("/activities").json()[activity]["participants"]
    assert NEW_EMAIL in participants


def test_signup_supports_activity_names_with_spaces(client):
    # Arrange
    activity = "Programming Class"
    encoded_path = "/activities/Programming%20Class/signup"

    # Act
    response = client.post(encoded_path, params={"email": NEW_EMAIL})

    # Assert
    assert response.status_code == 200
    participants = client.get("/activities").json()[activity]["participants"]
    assert NEW_EMAIL in participants


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    activity = "Underwater Basket Weaving"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": NEW_EMAIL})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity}"}
    participants = client.get("/activities").json()[activity]["participants"]
    assert email not in participants


def test_unregister_after_signup_round_trip(client):
    # Arrange
    activity = "Gym Class"
    client.post(f"/activities/{activity}/signup", params={"email": NEW_EMAIL})

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": NEW_EMAIL})

    # Assert
    assert response.status_code == 200
    participants = client.get("/activities").json()[activity]["participants"]
    assert NEW_EMAIL not in participants


@pytest.mark.parametrize(
    "activity, email, expected_detail",
    [
        ("Underwater Basket Weaving", "michael@mergington.edu", "Activity not found"),
        ("Chess Club", NEW_EMAIL, "Student is not signed up for this activity"),
    ],
)
def test_unregister_errors_return_404(client, activity, email, expected_detail):
    # Arrange
    path = f"/activities/{activity}/participants"

    # Act
    response = client.delete(path, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": expected_detail}
