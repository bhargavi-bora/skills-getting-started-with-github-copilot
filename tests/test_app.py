import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        # Arrange
        # No setup needed - activities are predefined in app.py

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert len(activities) > 0

    def test_get_activities_returns_correct_structure(self, client):
        # Arrange
        expected_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict)
            assert expected_fields.issubset(activity_data.keys())
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, sample_email):
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={sample_email}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert activity_name in data["message"]

    def test_signup_adds_participant_to_activity(self, client, sample_email):
        # Arrange
        activity_name = "Programming Class"
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"]
        initial_count = len(initial_participants)

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={sample_email}"
        )

        # Assert
        assert response.status_code == 200
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        assert sample_email in updated_participants
        assert len(updated_participants) == initial_count + 1

    def test_signup_duplicate_registration_fails(self, client, sample_email):
        # Arrange
        activity_name = "Programming Class"
        client.post(f"/activities/{activity_name}/signup?email={sample_email}")

        # Act - attempt duplicate signup
        response = client.post(
            f"/activities/{activity_name}/signup?email={sample_email}"
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_fails(self, client, sample_email):
        # Arrange
        activity_name = "Non Existent Activity"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={sample_email}"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client, sample_email):
        # Arrange
        activity_name = "Chess Club"
        client.post(f"/activities/{activity_name}/signup?email={sample_email}")

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={sample_email}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]

    def test_unregister_removes_participant(self, client, sample_email):
        # Arrange
        activity_name = "Programming Class"
        client.post(f"/activities/{activity_name}/signup?email={sample_email}")
        response_after_signup = client.get("/activities")
        count_after_signup = len(
            response_after_signup.json()[activity_name]["participants"]
        )

        # Act
        client.delete(
            f"/activities/{activity_name}/unregister?email={sample_email}"
        )

        # Assert
        response_after_unregister = client.get("/activities")
        count_after_unregister = len(
            response_after_unregister.json()[activity_name]["participants"]
        )
        assert count_after_unregister == count_after_signup - 1
        assert sample_email not in response_after_unregister.json()[activity_name]["participants"]

    def test_unregister_not_registered_fails(self, client, sample_email):
        # Arrange
        activity_name = "Gym Class"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={sample_email}"
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_nonexistent_activity_fails(self, client, sample_email):
        # Arrange
        activity_name = "Non Existent Activity"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={sample_email}"
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
