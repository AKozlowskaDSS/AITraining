"""
Test cases for the Mergington High School Activities API endpoints.
"""

import pytest
from fastapi import status


class TestRootEndpoint:
    """Test cases for the root endpoint."""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Test cases for the activities endpoints."""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all available activities."""
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check that all activities have required fields
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)
            assert isinstance(activity_details["max_participants"], int)
    
    def test_get_activities_includes_expected_activities(self, client, reset_activities):
        """Test that GET /activities includes expected default activities."""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", 
            "Soccer Team", "Basketball Club", "Art Workshop",
            "Drama Club", "Math Olympiad", "Science Club"
        ]
        
        for activity in expected_activities:
            assert activity in data


class TestSignupEndpoint:
    """Test cases for the signup endpoint."""
    
    def test_signup_for_existing_activity_success(self, client, reset_activities):
        """Test successful signup for an existing activity."""
        test_email = "newstudent@mergington.edu"
        activity_name = "Chess Club"
        
        response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert test_email in data["message"]
        assert activity_name in data["message"]
        
        # Verify the student was actually added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email in activities_data[activity_name]["participants"]
    
    def test_signup_for_nonexistent_activity_fails(self, client, reset_activities):
        """Test signup for non-existent activity returns 404."""
        test_email = "newstudent@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_participant(self, client, reset_activities):
        """Test signup with duplicate participant returns appropriate message."""
        # Use an existing participant
        test_email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"
        
        response = client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "already signed up" in data["message"]
    
    def test_signup_with_url_encoded_activity_name(self, client, reset_activities):
        """Test signup works with URL-encoded activity names containing spaces."""
        test_email = "newstudent@mergington.edu"
        activity_name = "Programming Class"
        encoded_name = "Programming%20Class"
        
        response = client.post(
            f"/activities/{encoded_name}/signup?email={test_email}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email in activities_data[activity_name]["participants"]


class TestRemoveParticipantEndpoint:
    """Test cases for the remove participant endpoint."""
    
    def test_remove_existing_participant_success(self, client, reset_activities):
        """Test successful removal of an existing participant."""
        # Use an existing participant
        test_email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"
        
        # Verify participant exists first
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email in activities_data[activity_name]["participants"]
        
        # Remove the participant
        response = client.delete(
            f"/activities/{activity_name}/remove?email={test_email}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "Removed" in data["message"]
        assert test_email in data["message"]
        
        # Verify the participant was actually removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email not in activities_data[activity_name]["participants"]
    
    def test_remove_nonexistent_participant_fails(self, client, reset_activities):
        """Test removal of non-existent participant returns 404."""
        test_email = "nonexistent@mergington.edu"
        activity_name = "Chess Club"
        
        response = client.delete(
            f"/activities/{activity_name}/remove?email={test_email}"
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "Student not found in activity" in data["detail"]
    
    def test_remove_participant_from_nonexistent_activity_fails(self, client, reset_activities):
        """Test removal from non-existent activity returns 404."""
        test_email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        response = client.delete(
            f"/activities/{activity_name}/remove?email={test_email}"
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_remove_with_url_encoded_activity_name(self, client, reset_activities):
        """Test removal works with URL-encoded activity names containing spaces."""
        # First add a participant to Programming Class
        test_email = "testremoval@mergington.edu"
        activity_name = "Programming Class"
        encoded_name = "Programming%20Class"
        
        # Add the participant
        client.post(f"/activities/{encoded_name}/signup?email={test_email}")
        
        # Remove the participant
        response = client.delete(
            f"/activities/{encoded_name}/remove?email={test_email}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify removal
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email not in activities_data[activity_name]["participants"]


class TestDataIntegrity:
    """Test cases for data integrity and edge cases."""
    
    def test_participant_count_consistency(self, client, reset_activities):
        """Test that participant counts are consistent with actual participants."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            participant_count = len(activity_details["participants"])
            max_participants = activity_details["max_participants"]
            
            # Count should not exceed maximum
            assert participant_count <= max_participants
            
            # All participants should be valid email-like strings
            for participant in activity_details["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant
                assert "mergington.edu" in participant
    
    def test_activities_are_immutable_across_requests(self, client, reset_activities):
        """Test that activities structure remains consistent across requests."""
        # Get activities twice
        response1 = client.get("/activities")
        response2 = client.get("/activities")
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Structure should be identical
        assert set(data1.keys()) == set(data2.keys())
        
        for activity_name in data1.keys():
            assert data1[activity_name]["description"] == data2[activity_name]["description"]
            assert data1[activity_name]["schedule"] == data2[activity_name]["schedule"]
            assert data1[activity_name]["max_participants"] == data2[activity_name]["max_participants"]
