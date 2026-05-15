"""
Unit tests for remaining models.

Tests cover:
- LoginAttempt
- UserSession
- PasswordHistory
- UserPermissionOverride
- PasswordEntryHistory
- PasswordAccessLog
- PasswordExpirationNotification
"""

import pytest
from datetime import timedelta
from django.utils import timezone

from authentication.models import (
    LoginAttempt,
    UserSession,
    PasswordHistory,
    UserPermissionOverride,
    PasswordEntryHistory,
    PasswordAccessLog,
    PasswordExpirationNotification,
)
from tests.fixtures.factories import (
    UserFactory,
    LoginAttemptFactory,
    SuccessfulLoginAttemptFactory,
    UserSessionFactory,
    PasswordHistoryFactory,
    PasswordEntryFactory,
    PasswordEntryWithExpirationFactory,
)


# ============================================================================
# LoginAttempt Model Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.django_db
class TestLoginAttemptModel:
    """Tests for LoginAttempt model."""

    def test_create_login_attempt(self, user):
        """Test creating a login attempt."""
        attempt = LoginAttempt.objects.create(
            user=user,
            email=user.email,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            successful=False,
        )

        assert attempt.user == user
        assert attempt.email == user.email
        assert attempt.ip_address == "192.168.1.1"
        assert attempt.user_agent == "Mozilla/5.0"
        assert attempt.successful is False

    def test_create_login_attempt_with_factory(self, user):
        """Test creating login attempt with factory."""
        attempt = LoginAttemptFactory(user=user)
        assert attempt.user == user
        assert attempt.email == user.email

    def test_successful_login_attempt(self, user):
        """Test successful login attempt."""
        attempt = SuccessfulLoginAttemptFactory(user=user)
        assert attempt.successful is True

    def test_failed_login_attempt(self, user):
        """Test failed login attempt."""
        attempt = LoginAttemptFactory(user=user, successful=False)
        assert attempt.successful is False

    def test_login_attempt_without_user(self):
        """Test login attempt without user (for non-existent email)."""
        attempt = LoginAttempt.objects.create(
            user=None,
            email="nonexistent@example.com",
            ip_address="192.168.1.1",
            successful=False,
        )

        assert attempt.user is None
        assert attempt.email == "nonexistent@example.com"

    def test_login_attempt_timestamp_auto_set(self):
        """Test that timestamp is automatically set."""
        attempt = LoginAttemptFactory()
        assert attempt.timestamp is not None
        assert attempt.timestamp <= timezone.now()

    def test_login_attempt_str_representation(self, user):
        """Test string representation of login attempt."""
        attempt = SuccessfulLoginAttemptFactory(user=user)
        assert "Successful" in str(attempt)
        assert user.email in str(attempt)

        failed_attempt = LoginAttemptFactory(user=user, successful=False)
        assert "Failed" in str(failed_attempt)

    def test_login_attempts_ordering(self, user):
        """Test that login attempts are ordered by timestamp descending."""
        attempt1 = LoginAttemptFactory(user=user)
        attempt2 = LoginAttemptFactory(user=user)
        attempt3 = LoginAttemptFactory(user=user)

        attempts = LoginAttempt.objects.filter(user=user)
        assert attempts[0].timestamp >= attempts[1].timestamp >= attempts[2].timestamp

    def test_deleting_user_deletes_login_attempts(self, user):
        """Test that deleting user cascades to login attempts."""
        attempt1 = LoginAttemptFactory(user=user)
        attempt2 = LoginAttemptFactory(user=user)
        attempt_ids = [attempt1.id, attempt2.id]

        user.delete()

        assert LoginAttempt.objects.filter(id__in=attempt_ids).count() == 0


# ============================================================================
# UserSession Model Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.django_db
class TestUserSessionModel:
    """Tests for UserSession model."""

    def test_create_user_session(self, user):
        """Test creating a user session."""
        session = UserSession.objects.create(
            user=user,
            session_key="test-session-key-123",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            device_name="Chrome on Windows",
            is_active=True,
        )

        assert session.user == user
        assert session.session_key == "test-session-key-123"
        assert session.ip_address == "192.168.1.1"
        assert session.device_name == "Chrome on Windows"
        assert session.is_active is True

    def test_create_user_session_with_factory(self, user):
        """Test creating user session with factory."""
        session = UserSessionFactory(user=user)
        assert session.user == user
        assert session.session_key is not None

    def test_session_key_is_unique(self, user):
        """Test that session keys are unique."""
        session1 = UserSessionFactory(user=user)
        session2 = UserSessionFactory(user=user)

        assert session1.session_key != session2.session_key

    def test_session_created_at_auto_set(self):
        """Test that created_at is automatically set."""
        session = UserSessionFactory()
        assert session.created_at is not None

    def test_session_last_activity_auto_set(self):
        """Test that last_activity is automatically set and updates."""
        session = UserSessionFactory()
        original_last_activity = session.last_activity

        session.device_name = "Updated Device"
        session.save()

        assert session.last_activity >= original_last_activity

    def test_session_str_representation(self, user):
        """Test string representation of user session."""
        session = UserSessionFactory(
            user=user, device_name="Chrome on Windows"
        )
        assert user.email in str(session)
        assert "Chrome on Windows" in str(session)

    def test_session_ordering(self, user):
        """Test that sessions are ordered by last_activity descending."""
        session1 = UserSessionFactory(user=user)
        session2 = UserSessionFactory(user=user)
        session3 = UserSessionFactory(user=user)

        sessions = UserSession.objects.filter(user=user)
        assert (
            sessions[0].last_activity
            >= sessions[1].last_activity
            >= sessions[2].last_activity
        )

    def test_active_session(self, user):
        """Test active session."""
        session = UserSessionFactory(user=user, is_active=True)
        assert session.is_active is True

    def test_inactive_session(self, user):
        """Test inactive session."""
        session = UserSessionFactory(user=user, is_active=False)
        assert session.is_active is False

    def test_deleting_user_deletes_sessions(self, user):
        """Test that deleting user cascades to sessions."""
        session1 = UserSessionFactory(user=user)
        session2 = UserSessionFactory(user=user)
        session_ids = [session1.id, session2.id]

        user.delete()

        assert UserSession.objects.filter(id__in=session_ids).count() == 0


# ============================================================================
# PasswordHistory Model Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordHistoryModel:
    """Tests for PasswordHistory model."""

    def test_create_password_history(self, user):
        """Test creating a password history entry."""
        history = PasswordHistory.objects.create(
            user=user,
            password="hashed_password_here",
        )

        assert history.user == user
        assert history.password == "hashed_password_here"

    def test_create_password_history_with_factory(self, user):
        """Test creating password history with factory."""
        history = PasswordHistoryFactory(user=user)
        assert history.user == user
        assert history.password is not None

    def test_password_history_created_at_auto_set(self):
        """Test that created_at is automatically set."""
        history = PasswordHistoryFactory()
        assert history.created_at is not None

    def test_password_history_str_representation(self, user):
        """Test string representation of password history."""
        history = PasswordHistoryFactory(user=user)
        assert user.email in str(history)
        assert "Password change" in str(history)

    def test_password_history_ordering(self, user):
        """Test that password history is ordered by created_at descending."""
        history1 = PasswordHistoryFactory(user=user)
        history2 = PasswordHistoryFactory(user=user)
        history3 = PasswordHistoryFactory(user=user)

        histories = PasswordHistory.objects.filter(user=user)
        assert (
            histories[0].created_at
            >= histories[1].created_at
            >= histories[2].created_at
        )

    def test_deleting_user_deletes_password_history(self, user):
        """Test that deleting user cascades to password history."""
        history1 = PasswordHistoryFactory(user=user)
        history2 = PasswordHistoryFactory(user=user)
        history_ids = [history1.id, history2.id]

        user.delete()

        assert PasswordHistory.objects.filter(id__in=history_ids).count() == 0


# ============================================================================
# UserPermissionOverride Model Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.django_db
class TestUserPermissionOverrideModel:
    """Tests for UserPermissionOverride model."""

    def test_create_permission_override(self, user):
        """Test creating a permission override."""
        override = UserPermissionOverride.objects.create(
            user=user,
            permission_name="can_export_data",
            is_granted=True,
        )

        assert override.user == user
        assert override.permission_name == "can_export_data"
        assert override.is_granted is True
        assert override.expires_at is None

    def test_create_permission_override_with_expiration(self, user):
        """Test creating permission override with expiration."""
        expires_at = timezone.now() + timedelta(days=30)
        override = UserPermissionOverride.objects.create(
            user=user,
            permission_name="can_share",
            is_granted=True,
            expires_at=expires_at,
        )

        assert override.expires_at == expires_at

    def test_permission_override_is_expired_property(self, user):
        """Test is_expired property."""
        # Not expired
        future_override = UserPermissionOverride.objects.create(
            user=user,
            permission_name="perm1",
            is_granted=True,
            expires_at=timezone.now() + timedelta(days=1),
        )
        assert future_override.is_expired is False

        # Expired
        expired_override = UserPermissionOverride.objects.create(
            user=user,
            permission_name="perm2",
            is_granted=True,
            expires_at=timezone.now() - timedelta(days=1),
        )
        assert expired_override.is_expired is True

        # No expiration
        no_expiry = UserPermissionOverride.objects.create(
            user=user,
            permission_name="perm3",
            is_granted=True,
            expires_at=None,
        )
        assert no_expiry.is_expired is False

    def test_permission_override_is_active_property(self, user):
        """Test is_active property."""
        # Active: granted and not expired
        active = UserPermissionOverride.objects.create(
            user=user,
            permission_name="perm1",
            is_granted=True,
            expires_at=timezone.now() + timedelta(days=1),
        )
        assert active.is_active is True

        # Not active: not granted
        denied = UserPermissionOverride.objects.create(
            user=user,
            permission_name="perm2",
            is_granted=False,
            expires_at=timezone.now() + timedelta(days=1),
        )
        assert denied.is_active is False

        # Not active: expired
        expired = UserPermissionOverride.objects.create(
            user=user,
            permission_name="perm3",
            is_granted=True,
            expires_at=timezone.now() - timedelta(days=1),
        )
        assert expired.is_active is False

    def test_permission_override_str_representation(self, user):
        """Test string representation of permission override."""
        override = UserPermissionOverride.objects.create(
            user=user,
            permission_name="can_export",
            is_granted=True,
        )

        assert "can_export" in str(override)
        assert "granted" in str(override)
        assert user.email in str(override)

    def test_permission_override_unique_together(self, user):
        """Test that user and permission_name must be unique together."""
        UserPermissionOverride.objects.create(
            user=user,
            permission_name="duplicate_perm",
            is_granted=True,
        )

        from django.db.utils import IntegrityError

        with pytest.raises(IntegrityError):
            UserPermissionOverride.objects.create(
                user=user,
                permission_name="duplicate_perm",
                is_granted=False,
            )

    def test_deleting_user_deletes_permission_overrides(self, user):
        """Test that deleting user cascades to permission overrides."""
        override1 = UserPermissionOverride.objects.create(
            user=user, permission_name="perm1", is_granted=True
        )
        override2 = UserPermissionOverride.objects.create(
            user=user, permission_name="perm2", is_granted=True
        )
        override_ids = [override1.id, override2.id]

        user.delete()

        assert (
            UserPermissionOverride.objects.filter(id__in=override_ids).count()
            == 0
        )


# ============================================================================
# PasswordEntryHistory Model Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordEntryHistoryModel:
    """Tests for PasswordEntryHistory model."""

    def test_create_password_entry_history(self, user, test_master_password):
        """Test creating a password entry history."""
        from authentication.encryption_service import encryption_service

        entry = PasswordEntryFactory(user=user)
        encrypted_password, salt = encryption_service.encrypt_password(
            "old-password", test_master_password
        )

        history = PasswordEntryHistory.objects.create(
            password_entry=entry,
            encrypted_password=encrypted_password,
            encryption_salt=salt,
            changed_by=user,
            change_reason="User requested change",
        )

        assert history.password_entry == entry
        assert history.changed_by == user
        assert history.change_reason == "User requested change"

    def test_password_entry_history_id_is_uuid(self):
        """Test that history ID is UUID."""
        from authentication.encryption_service import encryption_service

        entry = PasswordEntryFactory()
        encrypted_password, salt = encryption_service.encrypt_password(
            "password", "master123"
        )

        history = PasswordEntryHistory.objects.create(
            password_entry=entry,
            encrypted_password=encrypted_password,
            encryption_salt=salt,
        )

        assert history.id is not None
        assert len(str(history.id)) == 36  # UUID format

    def test_password_entry_history_changed_at_auto_set(self):
        """Test that changed_at is automatically set."""
        from authentication.encryption_service import encryption_service

        entry = PasswordEntryFactory()
        encrypted_password, salt = encryption_service.encrypt_password(
            "password", "master123"
        )

        history = PasswordEntryHistory.objects.create(
            password_entry=entry,
            encrypted_password=encrypted_password,
            encryption_salt=salt,
        )

        assert history.changed_at is not None

    def test_password_entry_history_str_representation(self):
        """Test string representation of password entry history."""
        from authentication.encryption_service import encryption_service

        entry = PasswordEntryFactory(name="Test Entry")
        encrypted_password, salt = encryption_service.encrypt_password(
            "password", "master123"
        )

        history = PasswordEntryHistory.objects.create(
            password_entry=entry,
            encrypted_password=encrypted_password,
            encryption_salt=salt,
        )

        assert "Test Entry" in str(history)
        assert "Password history" in str(history)

    def test_deleting_password_entry_deletes_history(self, user):
        """Test that deleting password entry cascades to history."""
        from authentication.encryption_service import encryption_service

        entry = PasswordEntryFactory(user=user)
        encrypted_password, salt = encryption_service.encrypt_password(
            "password", "master123"
        )

        history = PasswordEntryHistory.objects.create(
            password_entry=entry,
            encrypted_password=encrypted_password,
            encryption_salt=salt,
        )
        history_id = history.id

        entry.delete()

        assert (
            PasswordEntryHistory.objects.filter(id=history_id).count() == 0
        )


# ============================================================================
# PasswordAccessLog Model Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordAccessLogModel:
    """Tests for PasswordAccessLog model."""

    def test_create_password_access_log(self, user):
        """Test creating a password access log."""
        entry = PasswordEntryFactory(user=user)

        log = PasswordAccessLog.objects.create(
            password_entry=entry,
            user=user,
            action="view",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )

        assert log.password_entry == entry
        assert log.user == user
        assert log.action == "view"
        assert log.ip_address == "192.168.1.1"

    def test_password_access_log_id_is_uuid(self):
        """Test that log ID is UUID."""
        entry = PasswordEntryFactory()
        log = PasswordAccessLog.objects.create(
            password_entry=entry,
            action="view",
        )

        assert log.id is not None
        assert len(str(log.id)) == 36  # UUID format

    def test_password_access_log_actions(self, user):
        """Test different action types."""
        entry = PasswordEntryFactory(user=user)

        actions = ["view", "copy", "update", "share", "delete"]
        for action in actions:
            log = PasswordAccessLog.objects.create(
                password_entry=entry,
                user=user,
                action=action,
            )
            assert log.action == action

    def test_password_access_log_timestamp_auto_set(self):
        """Test that timestamp is automatically set."""
        entry = PasswordEntryFactory()
        log = PasswordAccessLog.objects.create(
            password_entry=entry,
            action="view",
        )

        assert log.timestamp is not None

    def test_password_access_log_str_representation(self, user):
        """Test string representation of access log."""
        entry = PasswordEntryFactory(user=user, name="Test Entry")
        log = PasswordAccessLog.objects.create(
            password_entry=entry,
            user=user,
            action="view",
        )

        assert "view" in str(log)
        assert "Test Entry" in str(log)
        assert user.email in str(log)

    def test_password_access_log_ordering(self, user):
        """Test that logs are ordered by timestamp descending."""
        entry = PasswordEntryFactory(user=user)

        log1 = PasswordAccessLog.objects.create(
            password_entry=entry, user=user, action="view"
        )
        log2 = PasswordAccessLog.objects.create(
            password_entry=entry, user=user, action="copy"
        )
        log3 = PasswordAccessLog.objects.create(
            password_entry=entry, user=user, action="update"
        )

        logs = PasswordAccessLog.objects.filter(password_entry=entry)
        assert logs[0].timestamp >= logs[1].timestamp >= logs[2].timestamp

    def test_deleting_password_entry_deletes_logs(self, user):
        """Test that deleting password entry cascades to access logs."""
        entry = PasswordEntryFactory(user=user)
        log1 = PasswordAccessLog.objects.create(
            password_entry=entry, user=user, action="view"
        )
        log2 = PasswordAccessLog.objects.create(
            password_entry=entry, user=user, action="copy"
        )
        log_ids = [log1.id, log2.id]

        entry.delete()

        assert PasswordAccessLog.objects.filter(id__in=log_ids).count() == 0


# ============================================================================
# PasswordExpirationNotification Model Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordExpirationNotificationModel:
    """Tests for PasswordExpirationNotification model."""

    def test_create_expiration_notification(self, user):
        """Test creating a password expiration notification."""
        entry = PasswordEntryWithExpirationFactory(user=user)

        notification = PasswordExpirationNotification.objects.create(
            password_entry=entry,
            notification_type="3_days",
            email_sent_successfully=True,
        )

        assert notification.password_entry == entry
        assert notification.notification_type == "3_days"
        assert notification.email_sent_successfully is True

    def test_expiration_notification_id_is_uuid(self):
        """Test that notification ID is UUID."""
        entry = PasswordEntryWithExpirationFactory()
        notification = PasswordExpirationNotification.objects.create(
            password_entry=entry,
            notification_type="1_day",
        )

        assert notification.id is not None
        assert len(str(notification.id)) == 36  # UUID format

    def test_expiration_notification_types(self, user):
        """Test different notification types."""
        entry = PasswordEntryWithExpirationFactory(user=user)

        types = ["3_days", "1_day", "expired"]
        for notif_type in types:
            notification = PasswordExpirationNotification.objects.create(
                password_entry=entry,
                notification_type=notif_type,
            )
            assert notification.notification_type == notif_type

    def test_expiration_notification_sent_at_auto_set(self):
        """Test that sent_at is automatically set."""
        entry = PasswordEntryWithExpirationFactory()
        notification = PasswordExpirationNotification.objects.create(
            password_entry=entry,
            notification_type="3_days",
        )

        assert notification.sent_at is not None

    def test_expiration_notification_str_representation(self, user):
        """Test string representation of expiration notification."""
        entry = PasswordEntryWithExpirationFactory(user=user, name="Test Entry")
        notification = PasswordExpirationNotification.objects.create(
            password_entry=entry,
            notification_type="3_days",
        )

        assert "3_days" in str(notification)
        assert "Test Entry" in str(notification)

    def test_expiration_notification_unique_together(self, user):
        """Test that password_entry and notification_type must be unique together."""
        entry = PasswordEntryWithExpirationFactory(user=user)

        PasswordExpirationNotification.objects.create(
            password_entry=entry,
            notification_type="3_days",
        )

        from django.db.utils import IntegrityError

        with pytest.raises(IntegrityError):
            PasswordExpirationNotification.objects.create(
                password_entry=entry,
                notification_type="3_days",
            )

    def test_different_notification_types_allowed(self, user):
        """Test that different notification types are allowed for same entry."""
        entry = PasswordEntryWithExpirationFactory(user=user)

        notif1 = PasswordExpirationNotification.objects.create(
            password_entry=entry,
            notification_type="3_days",
        )
        notif2 = PasswordExpirationNotification.objects.create(
            password_entry=entry,
            notification_type="1_day",
        )

        assert notif1.notification_type != notif2.notification_type

    def test_deleting_password_entry_deletes_notifications(self, user):
        """Test that deleting password entry cascades to notifications."""
        entry = PasswordEntryWithExpirationFactory(user=user)
        notif1 = PasswordExpirationNotification.objects.create(
            password_entry=entry, notification_type="3_days"
        )
        notif2 = PasswordExpirationNotification.objects.create(
            password_entry=entry, notification_type="1_day"
        )
        notif_ids = [notif1.id, notif2.id]

        entry.delete()

        assert (
            PasswordExpirationNotification.objects.filter(
                id__in=notif_ids
            ).count()
            == 0
        )

    def test_email_sent_successfully_flag(self, user):
        """Test email_sent_successfully flag."""
        entry = PasswordEntryWithExpirationFactory(user=user)

        # Successfully sent
        notif1 = PasswordExpirationNotification.objects.create(
            password_entry=entry,
            notification_type="3_days",
            email_sent_successfully=True,
        )
        assert notif1.email_sent_successfully is True

        # Failed to send
        notif2 = PasswordExpirationNotification.objects.create(
            password_entry=entry,
            notification_type="1_day",
            email_sent_successfully=False,
        )
        assert notif2.email_sent_successfully is False
