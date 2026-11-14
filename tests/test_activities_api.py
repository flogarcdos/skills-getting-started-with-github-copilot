"""
Test suite for Mergington High School Activities API

Uses AAA (Arrange-Act-Assert) pattern for clear test structure:
- ARRANGE: Set up test data and preconditions
- ACT: Execute the action being tested
- ASSERT: Verify the results
"""

import pytest
from src.app import activities


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """
        ARRANGE: Client is ready
        ACT: Make GET request to /activities
        ASSERT: Response status is 200
        """
        # ARRANGE
        # (implicit via fixture)

        # ACT
        response = client.get("/activities")

        # ASSERT
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """
        ARRANGE: Client is ready
        ACT: Make GET request to /activities
        ASSERT: Response is a dictionary
        """
        # ARRANGE
        # (implicit via fixture)

        # ACT
        response = client.get("/activities")
        data = response.json()

        # ASSERT
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_get_activities_has_required_fields(self, client):
        """
        ARRANGE: Client is ready
        ACT: Make GET request to /activities
        ASSERT: Each activity has required fields
        """
        # ARRANGE
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # ACT
        response = client.get("/activities")
        activities_data = response.json()

        # ASSERT
        for activity_name, activity_data in activities_data.items():
            assert required_fields.issubset(activity_data.keys()), \
                f"Activity '{activity_name}' missing required fields"

    def test_get_activities_participants_is_list(self, client):
        """
        ARRANGE: Client is ready
        ACT: Make GET request to /activities
        ASSERT: Participants field is a list for each activity
        """
        # ARRANGE
        # (implicit via fixture)

        # ACT
        response = client.get("/activities")
        activities_data = response.json()

        # ASSERT
        for activity_name, activity_data in activities_data.items():
            assert isinstance(activity_data["participants"], list), \
                f"Activity '{activity_name}' participants is not a list"


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_successful_signup(self, client, reset_activities):
        """
        ARRANGE: Client ready, new email
        ACT: POST signup request
        ASSERT: Response 200, participant added to activity
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # ASSERT
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]
        assert "Signed up" in response.json()["message"]

    def test_signup_increments_participants_count(self, client, reset_activities):
        """
        ARRANGE: Get initial participant count
        ACT: POST signup request
        ASSERT: Participant count increased by 1
        """
        # ARRANGE
        activity_name = "Basketball Club"
        email = "player@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # ASSERT
        assert response.status_code == 200
        assert len(activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_decrements_available_spots(self, client, reset_activities):
        """
        ARRANGE: Calculate initial available spots
        ACT: POST signup request
        ASSERT: Available spots decreased by 1
        """
        # ARRANGE
        activity_name = "Track and Field"
        email = "runner@mergington.edu"
        max_participants = activities[activity_name]["max_participants"]
        initial_participants = len(activities[activity_name]["participants"])
        initial_spots = max_participants - initial_participants

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # ASSERT
        assert response.status_code == 200
        new_spots = max_participants - len(activities[activity_name]["participants"])
        assert new_spots == initial_spots - 1

    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        ARRANGE: Prepare request with invalid activity name
        ACT: POST signup request for non-existent activity
        ASSERT: Response 404
        """
        # ARRANGE
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # ASSERT
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_email_returns_400(self, client, reset_activities):
        """
        ARRANGE: Email already signed up for activity
        ACT: POST signup request with duplicate email
        ASSERT: Response 400, error message
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # ASSERT
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_full_activity_returns_400(self, client, reset_activities):
        """
        ARRANGE: Fill an activity to capacity
        ACT: Try to signup one more participant
        ASSERT: Response 400, error message
        """
        # ARRANGE
        activity_name = "Debate Club"
        max_participants = activities[activity_name]["max_participants"]
        # Fill the activity to capacity
        for i in range(max_participants):
            activities[activity_name]["participants"].append(f"student{i}@test.com")

        new_email = "extra@mergington.edu"

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )

        # ASSERT
        assert response.status_code == 400
        assert "full" in response.json()["detail"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_successful_unregister(self, client, reset_activities):
        """
        ARRANGE: Participant is signed up for activity
        ACT: DELETE unregister request
        ASSERT: Response 200, participant removed
        """
        # ARRANGE
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        assert email in activities[activity_name]["participants"]

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # ASSERT
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        assert "Unregistered" in response.json()["message"]

    def test_unregister_decrements_participants_count(self, client, reset_activities):
        """
        ARRANGE: Get initial participant count
        ACT: DELETE unregister request
        ASSERT: Participant count decreased by 1
        """
        # ARRANGE
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # ASSERT
        assert response.status_code == 200
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_increments_available_spots(self, client, reset_activities):
        """
        ARRANGE: Calculate initial available spots
        ACT: DELETE unregister request
        ASSERT: Available spots increased by 1
        """
        # ARRANGE
        activity_name = "Gym Class"
        email = "john@mergington.edu"
        max_participants = activities[activity_name]["max_participants"]
        initial_participants = len(activities[activity_name]["participants"])
        initial_spots = max_participants - initial_participants

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # ASSERT
        assert response.status_code == 200
        new_spots = max_participants - len(activities[activity_name]["participants"])
        assert new_spots == initial_spots + 1

    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        ARRANGE: Prepare request with invalid activity name
        ACT: DELETE unregister request for non-existent activity
        ASSERT: Response 404
        """
        # ARRANGE
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # ASSERT
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_signed_up_returns_400(self, client, reset_activities):
        """
        ARRANGE: Email not signed up for activity
        ACT: DELETE unregister request
        ASSERT: Response 400, error message
        """
        # ARRANGE
        activity_name = "Art Club"
        email = "notregistered@mergington.edu"

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # ASSERT
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]


class TestIntegration:
    """Integration tests for complete workflows"""

    def test_signup_and_unregister_flow(self, client, reset_activities):
        """
        ARRANGE: Prepare client
        ACT: Sign up then unregister
        ASSERT: Participant added then removed, activities unchanged
        """
        # ARRANGE
        activity_name = "Science Club"
        email = "scientist@mergington.edu"

        # ACT - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # ASSERT signup successful
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]

        # ACT - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # ASSERT unregister successful and state restored
        assert unregister_response.status_code == 200
        assert email not in activities[activity_name]["participants"]

    def test_multiple_signups_to_same_activity(self, client, reset_activities):
        """
        ARRANGE: Multiple emails ready
        ACT: Sign up multiple participants
        ASSERT: All participants in activity
        """
        # ARRANGE
        activity_name = "Drama Club"
        emails = ["actor1@mergington.edu", "actor2@mergington.edu", "actor3@mergington.edu"]

        # ACT
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200

        # ASSERT
        for email in emails:
            assert email in activities[activity_name]["participants"]

    def test_fill_and_refill_activity(self, client, reset_activities):
        """
        ARRANGE: Get activity near capacity
        ACT: Fill to capacity, unregister, sign up new participant
        ASSERT: Can sign up after spot becomes available
        """
        # ARRANGE
        activity_name = "Art Club"
        max_participants = activities[activity_name]["max_participants"]
        current_count = len(activities[activity_name]["participants"])
        spots_to_fill = max_participants - current_count

        # ACT - Fill remaining spots
        new_emails = [f"artist{i}@test.com" for i in range(spots_to_fill)]
        for email in new_emails:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200

        # ASSERT - Activity is full
        assert len(activities[activity_name]["participants"]) == max_participants

        # ACT - Try to signup to full activity
        response = client.post(
            f"/activities/{activity_name}/signup?email=extra@test.com"
        )
        assert response.status_code == 400

        # ACT - Unregister one participant
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={new_emails[0]}"
        )
        assert response.status_code == 200

        # ASSERT - Spot is available
        assert len(activities[activity_name]["participants"]) == max_participants - 1

        # ACT - Sign up new participant to freed spot
        response = client.post(
            f"/activities/{activity_name}/signup?email=newperson@test.com"
        )

        # ASSERT - Signup successful
        assert response.status_code == 200
        assert "newperson@test.com" in activities[activity_name]["participants"]
