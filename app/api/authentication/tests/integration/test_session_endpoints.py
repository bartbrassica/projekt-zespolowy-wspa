"""
Integration tests for session management endpoints.
Tests for listing active sessions and terminating sessions.
"""

import pytest
import json
from django.utils import timezone

from authentication.models import UserSession


@pytest.mark.integration
@pytest.mark.django_db
class TestListSessionsEndpoint:
    """Test GET /api/sessions endpoint."""

    def test_list_sessions_authenticated_user(self, authenticated_client, user):
        """Test listing sessions for authenticated user."""
        # Create some sessions
        session1 = UserSession.objects.create(
            user=user,
            session_key="key1",
            ip_address="192.168.1.1",
            user_agent="Chrome/90.0",
            device_name="Chrome on Windows",
            is_active=True,
        )
        session2 = UserSession.objects.create(
            user=user,
            session_key="key2",
            ip_address="192.168.1.2",
            user_agent="Firefox/88.0",
            device_name="Firefox on Linux",
            is_active=True,
        )

        response = authenticated_client.get("/api/sessions")

        assert response.status_code == 200
        data = response.json()

        assert "sessions" in data
        assert len(data["sessions"]) == 2

        # Verify session data structure
        session_data = data["sessions"][0]
        assert "id" in session_data
        assert "device_name" in session_data
        assert "ip_address" in session_data
        assert "user_agent" in session_data
        assert "created_at" in session_data
        assert "last_activity" in session_data
        assert "is_active" in session_data

    def test_list_sessions_only_active_sessions(self, authenticated_client, user):
        """Test that only active sessions are listed."""
        # Create active session
        UserSession.objects.create(
            user=user,
            session_key="active-key",
            is_active=True,
        )

        # Create inactive session
        UserSession.objects.create(
            user=user,
            session_key="inactive-key",
            is_active=False,
        )

        response = authenticated_client.get("/api/sessions")

        assert response.status_code == 200
        data = response.json()

        assert len(data["sessions"]) == 1
        assert data["sessions"][0]["is_active"] is True

    def test_list_sessions_ordered_by_last_activity(self, authenticated_client, user):
        """Test that sessions are ordered by last_activity descending."""
        session1 = UserSession.objects.create(
            user=user,
            session_key="key1",
            device_name="Device 1",
            is_active=True,
        )

        session2 = UserSession.objects.create(
            user=user,
            session_key="key2",
            device_name="Device 2",
            is_active=True,
        )

        # Make session2 older using queryset update to bypass auto_now
        from datetime import timedelta
        UserSession.objects.filter(id=session2.id).update(
            last_activity=timezone.now() - timedelta(hours=1)
        )

        response = authenticated_client.get("/api/sessions")
        data = response.json()

        assert len(data["sessions"]) == 2
        # First session should be the most recent
        assert data["sessions"][0]["device_name"] == "Device 1"
        assert data["sessions"][1]["device_name"] == "Device 2"

    def test_list_sessions_without_authentication(self, api_client):
        """Test listing sessions without authentication."""
        response = api_client.get("/api/sessions")
        assert response.status_code == 401

    def test_list_sessions_empty_list(self, authenticated_client, user):
        """Test listing sessions when user has no sessions."""
        response = authenticated_client.get("/api/sessions")

        assert response.status_code == 200
        data = response.json()
        assert data["sessions"] == []

    def test_list_sessions_with_invalid_token(self, api_client):
        """Test listing sessions with invalid authentication token."""
        api_client.defaults["HTTP_AUTHORIZATION"] = "Bearer invalid.token.here"
        response = api_client.get("/api/sessions")
        assert response.status_code == 401

    def test_list_sessions_user_isolation(self, api_client, multiple_users, test_password):
        """Test that users only see their own sessions."""
        user1, user2, _ = multiple_users

        # Create sessions for both users
        UserSession.objects.create(user=user1, session_key="user1-key", is_active=True)
        UserSession.objects.create(user=user2, session_key="user2-key1", is_active=True)
        UserSession.objects.create(user=user2, session_key="user2-key2", is_active=True)

        # Login as user1
        from authentication.utils import create_jwt_tokens
        tokens = create_jwt_tokens(user1)
        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {tokens['access_token']}"

        response = api_client.get("/api/sessions")
        data = response.json()

        # User1 should only see their own session
        assert len(data["sessions"]) == 1

    def test_list_sessions_includes_all_fields(self, authenticated_client, user):
        """Test that all session fields are included in response."""
        session = UserSession.objects.create(
            user=user,
            session_key="test-key",
            ip_address="203.0.113.1",
            user_agent="Mozilla/5.0 (Test)",
            device_name="Test Device",
            is_active=True,
        )

        response = authenticated_client.get("/api/sessions")
        data = response.json()

        session_data = data["sessions"][0]
        assert session_data["id"] == str(session.id)
        assert session_data["ip_address"] == "203.0.113.1"
        assert session_data["user_agent"] == "Mozilla/5.0 (Test)"
        assert session_data["device_name"] == "Test Device"
        assert session_data["is_active"] is True

    def test_list_sessions_with_null_fields(self, authenticated_client, user):
        """Test listing sessions with null/empty fields."""
        UserSession.objects.create(
            user=user,
            session_key="minimal-key",
            ip_address=None,
            user_agent="",
            device_name="",
            is_active=True,
        )

        response = authenticated_client.get("/api/sessions")
        data = response.json()

        session_data = data["sessions"][0]
        assert session_data["ip_address"] is None
        assert session_data["user_agent"] == ""
        assert session_data["device_name"] == ""

    def test_list_sessions_datetime_format(self, authenticated_client, user):
        """Test that datetime fields are properly formatted."""
        UserSession.objects.create(
            user=user,
            session_key="test-key",
            is_active=True,
        )

        response = authenticated_client.get("/api/sessions")
        data = response.json()

        session_data = data["sessions"][0]
        # Verify datetime strings are present and valid
        assert "created_at" in session_data
        assert "last_activity" in session_data
        # Basic ISO format check
        assert "T" in session_data["created_at"]
        assert "T" in session_data["last_activity"]

    def test_list_many_sessions(self, authenticated_client, user):
        """Test listing many sessions."""
        # Create 50 sessions
        for i in range(50):
            UserSession.objects.create(
                user=user,
                session_key=f"key-{i}",
                device_name=f"Device {i}",
                is_active=True,
            )

        response = authenticated_client.get("/api/sessions")
        data = response.json()

        assert response.status_code == 200
        assert len(data["sessions"]) == 50


@pytest.mark.integration
@pytest.mark.django_db
class TestTerminateSessionEndpoint:
    """Test DELETE /api/sessions/{session_id} endpoint."""

    def test_terminate_own_session_success(self, authenticated_client, user):
        """Test successfully terminating own session."""
        session = UserSession.objects.create(
            user=user,
            session_key="test-key",
            is_active=True,
        )

        response = authenticated_client.delete(f"/api/sessions/{session.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Session terminated successfully"

        # Verify session is marked as inactive
        session.refresh_from_db()
        assert session.is_active is False

    def test_terminate_nonexistent_session(self, authenticated_client, user):
        """Test terminating a session that doesn't exist."""
        fake_id = 99999  # Use a non-existent integer ID
        response = authenticated_client.delete(f"/api/sessions/{fake_id}")

        assert response.status_code == 404

    def test_terminate_other_users_session(self, api_client, multiple_users, test_password):
        """Test that user cannot terminate another user's session."""
        user1, user2, _ = multiple_users

        # Create session for user2
        user2_session = UserSession.objects.create(
            user=user2,
            session_key="user2-key",
            is_active=True,
        )

        # Authenticate as user1
        from authentication.utils import create_jwt_tokens
        tokens = create_jwt_tokens(user1)
        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {tokens['access_token']}"

        # Try to terminate user2's session
        response = api_client.delete(f"/api/sessions/{user2_session.id}")

        assert response.status_code == 404

        # Verify user2's session is still active
        user2_session.refresh_from_db()
        assert user2_session.is_active is True

    def test_terminate_session_without_authentication(self, api_client, user):
        """Test terminating session without authentication."""
        session = UserSession.objects.create(
            user=user,
            session_key="test-key",
            is_active=True,
        )

        response = api_client.delete(f"/api/sessions/{session.id}")
        assert response.status_code == 401

    def test_terminate_already_inactive_session(self, authenticated_client, user):
        """Test terminating a session that's already inactive."""
        session = UserSession.objects.create(
            user=user,
            session_key="test-key",
            is_active=False,
        )

        response = authenticated_client.delete(f"/api/sessions/{session.id}")

        # Should still return success
        assert response.status_code == 200
        session.refresh_from_db()
        assert session.is_active is False

    def test_terminate_session_with_invalid_id_format(self, authenticated_client, user):
        """Test terminating session with invalid ID format."""
        response = authenticated_client.delete("/api/sessions/invalid-id")

        # Django/Ninja should return 404 or 422 for invalid ID
        assert response.status_code in [404, 422]

    def test_terminate_multiple_sessions(self, authenticated_client, user):
        """Test terminating multiple sessions."""
        session1 = UserSession.objects.create(
            user=user,
            session_key="key1",
            is_active=True,
        )
        session2 = UserSession.objects.create(
            user=user,
            session_key="key2",
            is_active=True,
        )

        # Terminate first session
        response1 = authenticated_client.delete(f"/api/sessions/{session1.id}")
        assert response1.status_code == 200

        # Terminate second session
        response2 = authenticated_client.delete(f"/api/sessions/{session2.id}")
        assert response2.status_code == 200

        # Verify both are inactive
        session1.refresh_from_db()
        session2.refresh_from_db()
        assert session1.is_active is False
        assert session2.is_active is False

    def test_terminate_session_twice(self, authenticated_client, user):
        """Test terminating the same session twice."""
        session = UserSession.objects.create(
            user=user,
            session_key="test-key",
            is_active=True,
        )

        # First termination
        response1 = authenticated_client.delete(f"/api/sessions/{session.id}")
        assert response1.status_code == 200

        # Second termination
        response2 = authenticated_client.delete(f"/api/sessions/{session.id}")
        assert response2.status_code == 200

    def test_terminate_session_response_format(self, authenticated_client, user):
        """Test that terminate response has correct format."""
        session = UserSession.objects.create(
            user=user,
            session_key="test-key",
            is_active=True,
        )

        response = authenticated_client.delete(f"/api/sessions/{session.id}")
        data = response.json()

        assert "message" in data
        assert isinstance(data["message"], str)

    def test_terminate_session_with_invalid_token(self, api_client, user):
        """Test terminating session with invalid authentication token."""
        session = UserSession.objects.create(
            user=user,
            session_key="test-key",
            is_active=True,
        )

        api_client.defaults["HTTP_AUTHORIZATION"] = "Bearer invalid.token.here"
        response = api_client.delete(f"/api/sessions/{session.id}")

        assert response.status_code == 401

        # Session should still be active
        session.refresh_from_db()
        assert session.is_active is True


@pytest.mark.integration
@pytest.mark.django_db
class TestSessionManagementWorkflows:
    """Test complete session management workflows."""

    def test_login_creates_session_and_can_list(self, api_client, verified_user, test_password):
        """Test that login creates a session that can be listed."""
        # Login
        login_data = {"email": verified_user.email, "password": test_password}
        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )

        assert login_response.status_code == 200
        tokens = login_response.json()

        # Verify session was created
        assert UserSession.objects.filter(user=verified_user, is_active=True).exists()

        # List sessions
        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {tokens['access_token']}"
        sessions_response = api_client.get("/api/sessions")

        assert sessions_response.status_code == 200
        data = sessions_response.json()
        assert len(data["sessions"]) >= 1

    def test_list_and_terminate_session_flow(self, authenticated_client, user):
        """Test complete flow of listing and terminating sessions."""
        # Create sessions
        session1 = UserSession.objects.create(
            user=user,
            session_key="key1",
            device_name="Device 1",
            is_active=True,
        )
        session2 = UserSession.objects.create(
            user=user,
            session_key="key2",
            device_name="Device 2",
            is_active=True,
        )

        # List sessions
        list_response = authenticated_client.get("/api/sessions")
        list_data = list_response.json()

        assert len(list_data["sessions"]) == 2

        # Terminate one session
        terminate_response = authenticated_client.delete(f"/api/sessions/{session1.id}")
        assert terminate_response.status_code == 200

        # List sessions again
        list_response2 = authenticated_client.get("/api/sessions")
        list_data2 = list_response2.json()

        # Should only see one active session now
        assert len(list_data2["sessions"]) == 1
        assert list_data2["sessions"][0]["id"] == str(session2.id)

    def test_terminate_all_sessions_workflow(self, authenticated_client, user):
        """Test terminating all sessions for a user."""
        # Create multiple sessions
        sessions = []
        for i in range(5):
            session = UserSession.objects.create(
                user=user,
                session_key=f"key{i}",
                device_name=f"Device {i}",
                is_active=True,
            )
            sessions.append(session)

        # List all sessions
        list_response = authenticated_client.get("/api/sessions")
        list_data = list_response.json()
        assert len(list_data["sessions"]) == 5

        # Terminate all sessions
        for session_data in list_data["sessions"]:
            response = authenticated_client.delete(f"/api/sessions/{session_data['id']}")
            assert response.status_code == 200

        # Verify all sessions are inactive
        list_response2 = authenticated_client.get("/api/sessions")
        list_data2 = list_response2.json()
        assert len(list_data2["sessions"]) == 0

    def test_session_list_after_logout(self, api_client, verified_user, test_password):
        """Test session list after user logs out."""
        # Login
        login_data = {"email": verified_user.email, "password": test_password}
        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )
        tokens = login_response.json()

        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {tokens['access_token']}"

        # Create a session
        UserSession.objects.create(
            user=verified_user,
            session_key="test-key",
            is_active=True,
        )

        # Logout
        api_client.post("/api/logout")

        # Session list should still work with valid access token
        # (logout only invalidates refresh tokens, not access tokens)
        list_response = api_client.get("/api/sessions")
        assert list_response.status_code == 200

    def test_concurrent_session_management(self, api_client, verified_user, test_password):
        """Test managing sessions from multiple devices concurrently."""
        from authentication.utils import create_jwt_tokens

        # Create multiple sessions simulating different devices
        session1 = UserSession.objects.create(
            user=verified_user,
            session_key="device1-key",
            device_name="Desktop",
            is_active=True,
        )
        session2 = UserSession.objects.create(
            user=verified_user,
            session_key="device2-key",
            device_name="Mobile",
            is_active=True,
        )

        # Get tokens for user
        tokens = create_jwt_tokens(verified_user)
        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {tokens['access_token']}"

        # List sessions
        list_response = api_client.get("/api/sessions")
        assert list_response.status_code == 200
        assert len(list_response.json()["sessions"]) == 2

        # Terminate mobile session from desktop
        terminate_response = api_client.delete(f"/api/sessions/{session2.id}")
        assert terminate_response.status_code == 200

        # Verify only desktop session remains
        list_response2 = api_client.get("/api/sessions")
        list_data = list_response2.json()
        assert len(list_data["sessions"]) == 1
        assert list_data["sessions"][0]["device_name"] == "Desktop"

    def test_session_timestamps_update(self, authenticated_client, user):
        """Test that session timestamps are properly maintained."""
        from datetime import timedelta

        session = UserSession.objects.create(
            user=user,
            session_key="test-key",
            is_active=True,
        )

        created_at = session.created_at

        # Set an older last_activity using queryset update
        old_time = timezone.now() - timedelta(minutes=5)
        UserSession.objects.filter(id=session.id).update(last_activity=old_time)

        session.refresh_from_db()
        initial_activity = session.last_activity

        # Simulate activity by updating session (auto_now will trigger)
        session.save()
        session.refresh_from_db()

        # created_at should not change
        assert session.created_at == created_at
        # last_activity should update (due to auto_now)
        assert session.last_activity > initial_activity
