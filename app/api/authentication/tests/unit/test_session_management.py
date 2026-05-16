"""
Unit tests for session management models and utilities.
"""

import pytest
from datetime import timedelta
from django.utils import timezone

from authentication.models import UserSession
from authentication.db_utils import (
    create_user_session,
    get_user_active_sessions,
    terminate_user_session,
)


@pytest.mark.unit
@pytest.mark.django_db
class TestUserSessionModel:
    """Test UserSession model."""

    def test_create_user_session(self, user):
        """Test creating a user session."""
        session = UserSession.objects.create(
            user=user,
            session_key="test-session-key-123",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            device_name="Chrome on Windows",
        )

        assert session.id is not None
        assert session.user == user
        assert session.session_key == "test-session-key-123"
        assert session.ip_address == "192.168.1.1"
        assert session.user_agent == "Mozilla/5.0"
        assert session.device_name == "Chrome on Windows"
        assert session.is_active is True
        assert session.created_at is not None
        assert session.last_activity is not None

    def test_user_session_str_representation(self, user):
        """Test string representation of UserSession."""
        session = UserSession.objects.create(
            user=user,
            session_key="test-key",
            device_name="Test Device",
        )

        assert str(session) == f"Session for {user.email} on Test Device"

    def test_user_session_str_without_device_name(self, user):
        """Test string representation without device name."""
        session = UserSession.objects.create(
            user=user,
            session_key="test-key",
        )

        assert str(session) == f"Session for {user.email} on unknown device"

    def test_user_session_ordering(self, user):
        """Test that sessions are ordered by last_activity descending."""
        session1 = UserSession.objects.create(
            user=user,
            session_key="key1",
        )

        # Create session with older last_activity
        session2 = UserSession.objects.create(
            user=user,
            session_key="key2",
        )
        # Use queryset update to bypass auto_now
        UserSession.objects.filter(id=session2.id).update(
            last_activity=timezone.now() - timedelta(hours=1)
        )

        sessions = list(UserSession.objects.all())
        assert sessions[0].id == session1.id
        assert sessions[1].id == session2.id

    def test_user_session_unique_session_key(self, user):
        """Test that session_key must be unique."""
        UserSession.objects.create(
            user=user,
            session_key="duplicate-key",
        )

        with pytest.raises(Exception):  # IntegrityError
            UserSession.objects.create(
                user=user,
                session_key="duplicate-key",
            )

    def test_user_session_cascade_delete(self, user):
        """Test that sessions are deleted when user is deleted."""
        session = UserSession.objects.create(
            user=user,
            session_key="test-key",
        )

        user_id = user.id
        user.delete()

        assert not UserSession.objects.filter(user_id=user_id).exists()

    def test_user_session_with_ipv6_address(self, user):
        """Test session with IPv6 address."""
        session = UserSession.objects.create(
            user=user,
            session_key="ipv6-session",
            ip_address="2001:0db8:85a3:0000:0000:8a2e:0370:7334",
        )

        assert session.ip_address == "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

    def test_user_session_nullable_fields(self, user):
        """Test that ip_address and user_agent can be null/empty."""
        session = UserSession.objects.create(
            user=user,
            session_key="minimal-session",
        )

        assert session.ip_address is None
        assert session.user_agent == ""
        assert session.device_name == ""


@pytest.mark.unit
@pytest.mark.django_db
class TestCreateUserSession:
    """Test create_user_session utility function."""

    def test_create_user_session_from_request(self, user, mock_request):
        """Test creating session from HTTP request."""
        session = create_user_session(user, mock_request)

        assert session.user == user
        assert session.ip_address == "127.0.0.1"
        assert session.user_agent == "Test Agent"
        assert session.is_active is True

    def test_create_user_session_without_ip(self, user):
        """Test creating session when request has no IP."""
        class MockRequest:
            META = {}

        request = MockRequest()
        session = create_user_session(user, request)

        assert session.user == user
        assert session.ip_address is None
        assert session.user_agent == ""

    def test_create_user_session_with_forwarded_ip(self, user):
        """Test creating session with forwarded IP."""
        class MockRequest:
            META = {
                "REMOTE_ADDR": "10.0.0.1",
                "HTTP_USER_AGENT": "Custom Agent",
            }

        request = MockRequest()
        session = create_user_session(user, request)

        assert session.ip_address == "10.0.0.1"
        assert session.user_agent == "Custom Agent"

    def test_create_multiple_sessions_for_user(self, user, mock_request):
        """Test that multiple sessions can be created for one user."""
        session1 = create_user_session(user, mock_request)
        session2 = create_user_session(user, mock_request)

        assert session1.id != session2.id
        assert session1.session_key != session2.session_key
        assert UserSession.objects.filter(user=user).count() == 2


@pytest.mark.unit
@pytest.mark.django_db
class TestGetUserActiveSessions:
    """Test get_user_active_sessions utility function."""

    def test_get_active_sessions_for_user(self, user):
        """Test getting active sessions for a user."""
        # Create active sessions
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

        # Create inactive session
        UserSession.objects.create(
            user=user,
            session_key="key3",
            is_active=False,
        )

        active_sessions = get_user_active_sessions(user)

        assert len(active_sessions) == 2
        assert session1 in active_sessions
        assert session2 in active_sessions

    def test_get_active_sessions_empty(self, user):
        """Test getting active sessions when user has none."""
        active_sessions = get_user_active_sessions(user)
        assert len(active_sessions) == 0

    def test_get_active_sessions_ordered_by_activity(self, user):
        """Test that sessions are ordered by last_activity descending."""
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
        # Make session2 older using queryset update to bypass auto_now
        UserSession.objects.filter(id=session2.id).update(
            last_activity=timezone.now() - timedelta(hours=1)
        )

        active_sessions = get_user_active_sessions(user)

        assert active_sessions[0].id == session1.id
        assert active_sessions[1].id == session2.id

    def test_get_active_sessions_only_for_specific_user(self, multiple_users):
        """Test that only sessions for the specific user are returned."""
        user1, user2, user3 = multiple_users

        UserSession.objects.create(user=user1, session_key="key1", is_active=True)
        UserSession.objects.create(user=user2, session_key="key2", is_active=True)
        UserSession.objects.create(user=user2, session_key="key3", is_active=True)

        user1_sessions = get_user_active_sessions(user1)
        user2_sessions = get_user_active_sessions(user2)

        assert len(user1_sessions) == 1
        assert len(user2_sessions) == 2


@pytest.mark.unit
@pytest.mark.django_db
class TestTerminateUserSession:
    """Test terminate_user_session utility function."""

    def test_terminate_existing_session(self, user):
        """Test terminating an existing session."""
        session = UserSession.objects.create(
            user=user,
            session_key="test-key",
            is_active=True,
        )

        result = terminate_user_session(user, str(session.id))

        assert result is True
        session.refresh_from_db()
        assert session.is_active is False

    def test_terminate_nonexistent_session(self, user):
        """Test terminating a session that doesn't exist."""
        result = terminate_user_session(user, "99999")  # Non-existent integer ID
        assert result is False

    def test_terminate_other_users_session(self, multiple_users):
        """Test that user cannot terminate another user's session."""
        user1, user2, _ = multiple_users

        session = UserSession.objects.create(
            user=user1,
            session_key="user1-key",
            is_active=True,
        )

        # Try to terminate user1's session as user2
        result = terminate_user_session(user2, str(session.id))

        assert result is False
        session.refresh_from_db()
        assert session.is_active is True

    def test_terminate_already_inactive_session(self, user):
        """Test terminating a session that's already inactive."""
        session = UserSession.objects.create(
            user=user,
            session_key="test-key",
            is_active=False,
        )

        result = terminate_user_session(user, str(session.id))

        assert result is True
        session.refresh_from_db()
        assert session.is_active is False

    def test_terminate_session_with_invalid_id(self, user):
        """Test terminating with an invalid session ID format."""
        result = terminate_user_session(user, "invalid-id")  # Invalid format
        assert result is False

    def test_terminate_multiple_sessions(self, user):
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

        result1 = terminate_user_session(user, str(session1.id))
        result2 = terminate_user_session(user, str(session2.id))

        assert result1 is True
        assert result2 is True

        session1.refresh_from_db()
        session2.refresh_from_db()
        assert session1.is_active is False
        assert session2.is_active is False


@pytest.mark.unit
@pytest.mark.django_db
class TestUserSessionRelationships:
    """Test UserSession relationships with User model."""

    def test_user_sessions_relationship(self, user):
        """Test accessing sessions through user.sessions."""
        session1 = UserSession.objects.create(user=user, session_key="key1")
        session2 = UserSession.objects.create(user=user, session_key="key2")

        user_sessions = user.sessions.all()

        assert user_sessions.count() == 2
        assert session1 in user_sessions
        assert session2 in user_sessions

    def test_filter_user_sessions_by_status(self, user):
        """Test filtering user sessions by active status."""
        UserSession.objects.create(user=user, session_key="key1", is_active=True)
        UserSession.objects.create(user=user, session_key="key2", is_active=False)
        UserSession.objects.create(user=user, session_key="key3", is_active=True)

        active = user.sessions.filter(is_active=True)
        inactive = user.sessions.filter(is_active=False)

        assert active.count() == 2
        assert inactive.count() == 1

    def test_session_last_activity_updates(self, user):
        """Test that last_activity is updated automatically."""
        # Set an older time initially using queryset update
        session = UserSession.objects.create(
            user=user,
            session_key="test-key",
        )
        old_time = timezone.now() - timedelta(minutes=5)
        UserSession.objects.filter(id=session.id).update(last_activity=old_time)

        session.refresh_from_db()
        original_activity = session.last_activity

        # Now save the instance, which should trigger auto_now
        session.user_agent = "Updated Agent"
        session.save()

        session.refresh_from_db()
        assert session.last_activity > original_activity
