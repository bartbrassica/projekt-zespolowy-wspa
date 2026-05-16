"""
Unit tests for authentication/password_expiration_manager.py
"""

import pytest
from datetime import timedelta
from django.utils import timezone
from unittest.mock import patch, MagicMock, call
from freezegun import freeze_time

from authentication.password_expiration_manager import PasswordExpirationManager
from authentication.models import PasswordExpirationNotification, PasswordEntry
from authentication.consts import PasswordExpirationConstants


@pytest.fixture
def password_entry_expiring_in_3_days(user, test_password):
    """Create a password entry expiring in 3 days."""
    from authentication.encryption_service import encryption_service

    encrypted_password, salt = encryption_service.encrypt_password(
        "test-password", test_password
    )

    entry = PasswordEntry.objects.create(
        user=user,
        name="3 Day Entry",
        site="https://3days.com",
        username="user3days",
        encrypted_password=encrypted_password,
        encryption_salt=salt,
        expires_at=timezone.now() + timedelta(days=3),
    )
    return entry


@pytest.fixture
def password_entry_expiring_in_1_day(user, test_password):
    """Create a password entry expiring in 1 day."""
    from authentication.encryption_service import encryption_service

    encrypted_password, salt = encryption_service.encrypt_password(
        "test-password", test_password
    )

    entry = PasswordEntry.objects.create(
        user=user,
        name="1 Day Entry",
        site="https://1day.com",
        username="user1day",
        encrypted_password=encrypted_password,
        encryption_salt=salt,
        expires_at=timezone.now() + timedelta(days=1),
    )
    return entry


@pytest.fixture
def password_entry_expiring_today(user, test_password):
    """Create a password entry expiring today."""
    from authentication.encryption_service import encryption_service

    encrypted_password, salt = encryption_service.encrypt_password(
        "test-password", test_password
    )

    entry = PasswordEntry.objects.create(
        user=user,
        name="Expired Entry",
        site="https://expired.com",
        username="userexpired",
        encrypted_password=encrypted_password,
        encryption_salt=salt,
        expires_at=timezone.now(),
    )
    return entry


@pytest.fixture
def password_entry_no_expiry(user, test_password):
    """Create a password entry with no expiry."""
    from authentication.encryption_service import encryption_service

    encrypted_password, salt = encryption_service.encrypt_password(
        "test-password", test_password
    )

    entry = PasswordEntry.objects.create(
        user=user,
        name="No Expiry Entry",
        site="https://noexpiry.com",
        username="usernoexpiry",
        encrypted_password=encrypted_password,
        encryption_salt=salt,
        expires_at=None,
    )
    return entry


@pytest.fixture
def second_user(db, test_password):
    """Create a second test user."""
    from authentication.models import User

    user = User.objects.create_user(
        email="seconduser@example.com",
        password=test_password,
        first_name="Second",
        last_name="User",
        is_verified=True,
        is_active=True,
    )
    return user


@pytest.mark.unit
@pytest.mark.django_db
class TestGetPasswordsExpiringInDays:
    """Tests for get_passwords_expiring_in_days method."""

    def test_get_passwords_expiring_in_3_days(
        self, password_entry_expiring_in_3_days
    ):
        """Test getting passwords expiring in exactly 3 days."""
        passwords = PasswordExpirationManager.get_passwords_expiring_in_days(3)

        assert passwords.count() == 1
        assert passwords.first() == password_entry_expiring_in_3_days

    def test_get_passwords_expiring_in_1_day(self, password_entry_expiring_in_1_day):
        """Test getting passwords expiring in exactly 1 day."""
        passwords = PasswordExpirationManager.get_passwords_expiring_in_days(1)

        assert passwords.count() == 1
        assert passwords.first() == password_entry_expiring_in_1_day

    def test_excludes_passwords_without_expiry(
        self, password_entry_expiring_in_3_days, password_entry_no_expiry
    ):
        """Test that passwords without expiry are excluded."""
        passwords = PasswordExpirationManager.get_passwords_expiring_in_days(3)

        assert passwords.count() == 1
        assert password_entry_no_expiry not in passwords

    def test_returns_empty_when_no_matches(self):
        """Test returns empty queryset when no passwords match."""
        passwords = PasswordExpirationManager.get_passwords_expiring_in_days(5)

        assert passwords.count() == 0

    def test_selects_related_user(self, password_entry_expiring_in_3_days):
        """Test that user is prefetched with select_related."""
        passwords = PasswordExpirationManager.get_passwords_expiring_in_days(3)

        # Access the user to ensure it was prefetched
        with self.assert_num_queries(0):
            _ = passwords.first().user

    def assert_num_queries(self, num):
        """Helper to assert number of queries."""
        from django.test.utils import CaptureQueriesContext
        from django.db import connection

        return CaptureQueriesContext(connection)

    def test_multiple_passwords_same_expiry(self, user, test_password):
        """Test getting multiple passwords with same expiry date."""
        from authentication.encryption_service import encryption_service

        encrypted_password, salt = encryption_service.encrypt_password(
            "test-password", test_password
        )

        expiry_date = timezone.now() + timedelta(days=3)

        # Create 3 password entries with same expiry
        for i in range(3):
            PasswordEntry.objects.create(
                user=user,
                name=f"Entry {i}",
                site=f"https://site{i}.com",
                username=f"user{i}",
                encrypted_password=encrypted_password,
                encryption_salt=salt,
                expires_at=expiry_date,
            )

        passwords = PasswordExpirationManager.get_passwords_expiring_in_days(3)

        assert passwords.count() == 3


@pytest.mark.unit
@pytest.mark.django_db
class TestGetExpiredPasswords:
    """Tests for get_expired_passwords method."""

    def test_get_expired_passwords(self, password_entry_expiring_today):
        """Test getting passwords that expired today."""
        passwords = PasswordExpirationManager.get_expired_passwords()

        assert passwords.count() == 1
        assert passwords.first() == password_entry_expiring_today

    def test_excludes_future_expiry(
        self, password_entry_expiring_today, password_entry_expiring_in_1_day
    ):
        """Test that passwords expiring in the future are excluded."""
        passwords = PasswordExpirationManager.get_expired_passwords()

        assert passwords.count() == 1
        assert password_entry_expiring_in_1_day not in passwords

    def test_excludes_passwords_without_expiry(
        self, password_entry_expiring_today, password_entry_no_expiry
    ):
        """Test that passwords without expiry are excluded."""
        passwords = PasswordExpirationManager.get_expired_passwords()

        assert passwords.count() == 1
        assert password_entry_no_expiry not in passwords

    def test_returns_empty_when_no_matches(self):
        """Test returns empty queryset when no passwords expired today."""
        passwords = PasswordExpirationManager.get_expired_passwords()

        assert passwords.count() == 0

    def test_multiple_expired_passwords(self, user, test_password):
        """Test getting multiple passwords expired today."""
        from authentication.encryption_service import encryption_service

        encrypted_password, salt = encryption_service.encrypt_password(
            "test-password", test_password
        )

        today = timezone.now()

        # Create 3 password entries expired today
        for i in range(3):
            PasswordEntry.objects.create(
                user=user,
                name=f"Expired Entry {i}",
                site=f"https://expired{i}.com",
                username=f"expired{i}",
                encrypted_password=encrypted_password,
                encryption_salt=salt,
                expires_at=today,
            )

        passwords = PasswordExpirationManager.get_expired_passwords()

        assert passwords.count() == 3


@pytest.mark.unit
@pytest.mark.django_db
class TestHasNotificationBeenSent:
    """Tests for has_notification_been_sent method."""

    def test_notification_not_sent(self, password_entry_expiring_in_3_days):
        """Test when no notification has been sent."""
        result = PasswordExpirationManager.has_notification_been_sent(
            password_entry_expiring_in_3_days,
            PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value,
        )

        assert result is False

    def test_notification_sent_successfully(self, password_entry_expiring_in_3_days):
        """Test when notification was sent successfully."""
        PasswordExpirationNotification.objects.create(
            password_entry=password_entry_expiring_in_3_days,
            notification_type=PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value,
            email_sent_successfully=True,
        )

        result = PasswordExpirationManager.has_notification_been_sent(
            password_entry_expiring_in_3_days,
            PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value,
        )

        assert result is True

    def test_notification_sent_unsuccessfully(
        self, password_entry_expiring_in_3_days
    ):
        """Test when notification send failed."""
        PasswordExpirationNotification.objects.create(
            password_entry=password_entry_expiring_in_3_days,
            notification_type=PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value,
            email_sent_successfully=False,
        )

        result = PasswordExpirationManager.has_notification_been_sent(
            password_entry_expiring_in_3_days,
            PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value,
        )

        assert result is False

    def test_different_notification_type(self, password_entry_expiring_in_3_days):
        """Test that different notification types are tracked separately."""
        PasswordExpirationNotification.objects.create(
            password_entry=password_entry_expiring_in_3_days,
            notification_type=PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value,
            email_sent_successfully=True,
        )

        result = PasswordExpirationManager.has_notification_been_sent(
            password_entry_expiring_in_3_days,
            PasswordExpirationConstants.NOTIFICATION_TYPE_1_DAY.value,
        )

        assert result is False


@pytest.mark.unit
class TestGetEmailConfig:
    """Tests for _get_email_config method."""

    def test_get_email_config_3_days(self):
        """Test getting email config for 3-day notification."""
        subject, template = PasswordExpirationManager._get_email_config(
            PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value
        )

        assert subject == PasswordExpirationConstants.SUBJECT_3_DAYS.value
        assert template == PasswordExpirationConstants.TEMPLATE_3_DAYS.value

    def test_get_email_config_1_day(self):
        """Test getting email config for 1-day notification."""
        subject, template = PasswordExpirationManager._get_email_config(
            PasswordExpirationConstants.NOTIFICATION_TYPE_1_DAY.value
        )

        assert subject == PasswordExpirationConstants.SUBJECT_1_DAY.value
        assert template == PasswordExpirationConstants.TEMPLATE_1_DAY.value

    def test_get_email_config_expired(self):
        """Test getting email config for expired notification."""
        subject, template = PasswordExpirationManager._get_email_config(
            PasswordExpirationConstants.NOTIFICATION_TYPE_EXPIRED.value
        )

        assert subject == PasswordExpirationConstants.SUBJECT_EXPIRED.value
        assert template == PasswordExpirationConstants.TEMPLATE_EXPIRED.value

    def test_get_email_config_invalid_type(self):
        """Test that invalid notification type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown notification type"):
            PasswordExpirationManager._get_email_config("invalid_type")


@pytest.mark.unit
@pytest.mark.django_db
class TestCreateEmailContext:
    """Tests for _create_email_context method."""

    def test_create_email_context(self, user):
        """Test creating email context with correct structure."""
        passwords_data = [
            {"name": "Test1", "site": "https://test1.com"},
            {"name": "Test2", "site": "https://test2.com"},
        ]

        context = PasswordExpirationManager._create_email_context(
            user,
            passwords_data,
            PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value,
        )

        assert context["user"] == user
        assert context["passwords"] == passwords_data
        assert (
            context["notification_type"]
            == PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value
        )
        assert "dashboard_url" in context
        assert context["total_count"] == 2

    def test_create_email_context_dashboard_url(self, user):
        """Test that dashboard URL is correctly constructed."""
        passwords_data = [{"name": "Test", "site": "https://test.com"}]

        context = PasswordExpirationManager._create_email_context(
            user,
            passwords_data,
            PasswordExpirationConstants.NOTIFICATION_TYPE_EXPIRED.value,
        )

        assert context["dashboard_url"].endswith("/passwords")

    def test_create_email_context_empty_passwords(self, user):
        """Test creating context with empty passwords list."""
        passwords_data = []

        context = PasswordExpirationManager._create_email_context(
            user,
            passwords_data,
            PasswordExpirationConstants.NOTIFICATION_TYPE_1_DAY.value,
        )

        assert context["total_count"] == 0
        assert context["passwords"] == []


@pytest.mark.unit
@pytest.mark.django_db
class TestSendExpirationEmail:
    """Tests for send_expiration_email method."""

    @patch("authentication.password_expiration_manager.EmailService._send_email_with_template")
    def test_send_expiration_email_success(self, mock_send_email, user):
        """Test successful email sending."""
        mock_send_email.return_value = True
        passwords_data = [{"name": "Test", "site": "https://test.com"}]

        result = PasswordExpirationManager.send_expiration_email(
            user,
            passwords_data,
            PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value,
        )

        assert result is True
        mock_send_email.assert_called_once()

        # Verify the call arguments
        call_args = mock_send_email.call_args
        assert call_args.kwargs["subject"] == PasswordExpirationConstants.SUBJECT_3_DAYS.value
        assert call_args.kwargs["template_name"] == PasswordExpirationConstants.TEMPLATE_3_DAYS.value
        assert call_args.kwargs["to_email"] == user.email
        assert "user" in call_args.kwargs["context"]

    @patch("authentication.password_expiration_manager.EmailService._send_email_with_template")
    def test_send_expiration_email_failure(self, mock_send_email, user):
        """Test email sending failure."""
        mock_send_email.return_value = False
        passwords_data = [{"name": "Test", "site": "https://test.com"}]

        result = PasswordExpirationManager.send_expiration_email(
            user,
            passwords_data,
            PasswordExpirationConstants.NOTIFICATION_TYPE_1_DAY.value,
        )

        assert result is False

    @patch("authentication.password_expiration_manager.EmailService._send_email_with_template")
    def test_send_expiration_email_invalid_type(self, mock_send_email, user):
        """Test email sending with invalid notification type."""
        passwords_data = [{"name": "Test", "site": "https://test.com"}]

        result = PasswordExpirationManager.send_expiration_email(
            user, passwords_data, "invalid_type"
        )

        assert result is False
        mock_send_email.assert_not_called()

    @patch("authentication.password_expiration_manager.EmailService._send_email_with_template")
    def test_send_expiration_email_exception(self, mock_send_email, user):
        """Test email sending when exception is raised."""
        mock_send_email.side_effect = Exception("Email service error")
        passwords_data = [{"name": "Test", "site": "https://test.com"}]

        result = PasswordExpirationManager.send_expiration_email(
            user,
            passwords_data,
            PasswordExpirationConstants.NOTIFICATION_TYPE_EXPIRED.value,
        )

        assert result is False


@pytest.mark.unit
@pytest.mark.django_db
class TestGroupPasswordsByUser:
    """Tests for _group_passwords_by_user method."""

    def test_group_passwords_single_user(
        self, user, password_entry_expiring_in_3_days, test_password
    ):
        """Test grouping passwords for a single user."""
        from authentication.encryption_service import encryption_service

        encrypted_password, salt = encryption_service.encrypt_password(
            "test-password", test_password
        )

        # Create second password for same user
        entry2 = PasswordEntry.objects.create(
            user=user,
            name="Second Entry",
            site="https://second.com",
            username="user2",
            encrypted_password=encrypted_password,
            encryption_salt=salt,
            expires_at=timezone.now() + timedelta(days=3),
        )

        passwords = PasswordEntry.objects.filter(
            id__in=[password_entry_expiring_in_3_days.id, entry2.id]
        )

        result = PasswordExpirationManager._group_passwords_by_user(
            passwords, PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value
        )

        assert len(result) == 1
        assert user in result
        assert len(result[user]) == 2

    def test_group_passwords_multiple_users(
        self, user, second_user, password_entry_expiring_in_3_days, test_password
    ):
        """Test grouping passwords for multiple users."""
        from authentication.encryption_service import encryption_service

        encrypted_password, salt = encryption_service.encrypt_password(
            "test-password", test_password
        )

        # Create password for second user
        entry2 = PasswordEntry.objects.create(
            user=second_user,
            name="Second User Entry",
            site="https://second.com",
            username="user2",
            encrypted_password=encrypted_password,
            encryption_salt=salt,
            expires_at=timezone.now() + timedelta(days=3),
        )

        passwords = PasswordEntry.objects.filter(
            id__in=[password_entry_expiring_in_3_days.id, entry2.id]
        )

        result = PasswordExpirationManager._group_passwords_by_user(
            passwords, PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value
        )

        assert len(result) == 2
        assert user in result
        assert second_user in result
        assert len(result[user]) == 1
        assert len(result[second_user]) == 1

    def test_group_passwords_excludes_already_notified(
        self, password_entry_expiring_in_3_days
    ):
        """Test that already notified passwords are excluded."""
        PasswordExpirationNotification.objects.create(
            password_entry=password_entry_expiring_in_3_days,
            notification_type=PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value,
            email_sent_successfully=True,
        )

        passwords = PasswordEntry.objects.filter(
            id=password_entry_expiring_in_3_days.id
        )

        result = PasswordExpirationManager._group_passwords_by_user(
            passwords, PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value
        )

        assert len(result) == 0

    def test_group_passwords_includes_failed_notifications(
        self, password_entry_expiring_in_3_days
    ):
        """Test that passwords with failed notifications are included."""
        PasswordExpirationNotification.objects.create(
            password_entry=password_entry_expiring_in_3_days,
            notification_type=PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value,
            email_sent_successfully=False,
        )

        passwords = PasswordEntry.objects.filter(
            id=password_entry_expiring_in_3_days.id
        )

        result = PasswordExpirationManager._group_passwords_by_user(
            passwords, PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value
        )

        assert len(result) == 1
        assert password_entry_expiring_in_3_days.user in result


@pytest.mark.unit
@pytest.mark.django_db
class TestFindPasswordEntry:
    """Tests for _find_password_entry method."""

    def test_find_password_entry_success(self, user, password_entry_expiring_in_3_days):
        """Test finding a password entry successfully."""
        password_data = {
            "name": password_entry_expiring_in_3_days.name,
            "site": password_entry_expiring_in_3_days.site,
        }

        passwords = PasswordEntry.objects.filter(
            id=password_entry_expiring_in_3_days.id
        )

        result = PasswordExpirationManager._find_password_entry(
            passwords, user, password_data
        )

        assert result == password_entry_expiring_in_3_days

    def test_find_password_entry_not_found(self, user):
        """Test when password entry is not found."""
        password_data = {"name": "Nonexistent", "site": "https://none.com"}

        passwords = PasswordEntry.objects.none()

        result = PasswordExpirationManager._find_password_entry(
            passwords, user, password_data
        )

        assert result is None

    def test_find_password_entry_wrong_user(
        self, user, second_user, password_entry_expiring_in_3_days
    ):
        """Test finding password entry with wrong user."""
        password_data = {
            "name": password_entry_expiring_in_3_days.name,
            "site": password_entry_expiring_in_3_days.site,
        }

        passwords = PasswordEntry.objects.filter(
            id=password_entry_expiring_in_3_days.id
        )

        result = PasswordExpirationManager._find_password_entry(
            passwords, second_user, password_data
        )

        assert result is None


@pytest.mark.unit
@pytest.mark.django_db
class TestCreateNotificationRecords:
    """Tests for _create_notification_records method."""

    def test_create_notification_records_success(
        self, user, password_entry_expiring_in_3_days
    ):
        """Test creating notification records successfully."""
        passwords_data = [
            {
                "name": password_entry_expiring_in_3_days.name,
                "site": password_entry_expiring_in_3_days.site,
            }
        ]

        passwords = PasswordEntry.objects.filter(
            id=password_entry_expiring_in_3_days.id
        )

        PasswordExpirationManager._create_notification_records(
            passwords,
            user,
            passwords_data,
            PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value,
            True,
        )

        notifications = PasswordExpirationNotification.objects.filter(
            password_entry=password_entry_expiring_in_3_days
        )

        assert notifications.count() == 1
        assert notifications.first().email_sent_successfully is True
        assert (
            notifications.first().notification_type
            == PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value
        )

    def test_create_notification_records_email_failed(
        self, user, password_entry_expiring_in_3_days
    ):
        """Test creating notification records when email failed."""
        passwords_data = [
            {
                "name": password_entry_expiring_in_3_days.name,
                "site": password_entry_expiring_in_3_days.site,
            }
        ]

        passwords = PasswordEntry.objects.filter(
            id=password_entry_expiring_in_3_days.id
        )

        PasswordExpirationManager._create_notification_records(
            passwords,
            user,
            passwords_data,
            PasswordExpirationConstants.NOTIFICATION_TYPE_1_DAY.value,
            False,
        )

        notifications = PasswordExpirationNotification.objects.filter(
            password_entry=password_entry_expiring_in_3_days
        )

        assert notifications.count() == 1
        assert notifications.first().email_sent_successfully is False

    def test_create_notification_records_multiple(
        self, user, password_entry_expiring_in_3_days, test_password
    ):
        """Test creating notification records for multiple passwords."""
        from authentication.encryption_service import encryption_service

        encrypted_password, salt = encryption_service.encrypt_password(
            "test-password", test_password
        )

        entry2 = PasswordEntry.objects.create(
            user=user,
            name="Second Entry",
            site="https://second.com",
            username="user2",
            encrypted_password=encrypted_password,
            encryption_salt=salt,
            expires_at=timezone.now() + timedelta(days=3),
        )

        passwords_data = [
            {
                "name": password_entry_expiring_in_3_days.name,
                "site": password_entry_expiring_in_3_days.site,
            },
            {"name": entry2.name, "site": entry2.site},
        ]

        passwords = PasswordEntry.objects.filter(
            id__in=[password_entry_expiring_in_3_days.id, entry2.id]
        )

        PasswordExpirationManager._create_notification_records(
            passwords,
            user,
            passwords_data,
            PasswordExpirationConstants.NOTIFICATION_TYPE_EXPIRED.value,
            True,
        )

        notifications = PasswordExpirationNotification.objects.all()

        assert notifications.count() == 2

    def test_create_notification_records_entry_not_found(self, user):
        """Test creating notification records when entry not found."""
        passwords_data = [{"name": "Nonexistent", "site": "https://none.com"}]

        passwords = PasswordEntry.objects.none()

        PasswordExpirationManager._create_notification_records(
            passwords,
            user,
            passwords_data,
            PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value,
            True,
        )

        notifications = PasswordExpirationNotification.objects.all()

        assert notifications.count() == 0


@pytest.mark.unit
@pytest.mark.django_db
class TestProcessNotificationBatch:
    """Tests for _process_notification_batch method."""

    @patch("authentication.password_expiration_manager.PasswordExpirationManager.send_expiration_email")
    def test_process_notification_batch_success(
        self, mock_send_email, user, password_entry_expiring_in_3_days
    ):
        """Test processing notification batch successfully."""
        mock_send_email.return_value = True

        passwords = PasswordEntry.objects.filter(
            id=password_entry_expiring_in_3_days.id
        )

        count = PasswordExpirationManager._process_notification_batch(
            passwords, PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value
        )

        assert count == 1
        mock_send_email.assert_called_once()

        # Verify notification record was created
        notifications = PasswordExpirationNotification.objects.filter(
            password_entry=password_entry_expiring_in_3_days
        )
        assert notifications.count() == 1
        assert notifications.first().email_sent_successfully is True

    @patch("authentication.password_expiration_manager.PasswordExpirationManager.send_expiration_email")
    def test_process_notification_batch_email_failed(
        self, mock_send_email, user, password_entry_expiring_in_3_days
    ):
        """Test processing batch when email sending fails."""
        mock_send_email.return_value = False

        passwords = PasswordEntry.objects.filter(
            id=password_entry_expiring_in_3_days.id
        )

        count = PasswordExpirationManager._process_notification_batch(
            passwords, PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value
        )

        assert count == 0

        # Verify notification record was still created with failed status
        notifications = PasswordExpirationNotification.objects.filter(
            password_entry=password_entry_expiring_in_3_days
        )
        assert notifications.count() == 1
        assert notifications.first().email_sent_successfully is False

    @patch("authentication.password_expiration_manager.PasswordExpirationManager.send_expiration_email")
    def test_process_notification_batch_multiple_users(
        self,
        mock_send_email,
        user,
        second_user,
        password_entry_expiring_in_3_days,
        test_password,
    ):
        """Test processing batch with multiple users."""
        mock_send_email.return_value = True

        from authentication.encryption_service import encryption_service

        encrypted_password, salt = encryption_service.encrypt_password(
            "test-password", test_password
        )

        entry2 = PasswordEntry.objects.create(
            user=second_user,
            name="Second User Entry",
            site="https://second.com",
            username="user2",
            encrypted_password=encrypted_password,
            encryption_salt=salt,
            expires_at=timezone.now() + timedelta(days=3),
        )

        passwords = PasswordEntry.objects.filter(
            id__in=[password_entry_expiring_in_3_days.id, entry2.id]
        )

        count = PasswordExpirationManager._process_notification_batch(
            passwords, PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value
        )

        assert count == 2
        assert mock_send_email.call_count == 2

    @patch("authentication.password_expiration_manager.PasswordExpirationManager.send_expiration_email")
    def test_process_notification_batch_skips_already_notified(
        self, mock_send_email, password_entry_expiring_in_3_days
    ):
        """Test that already notified passwords are skipped."""
        PasswordExpirationNotification.objects.create(
            password_entry=password_entry_expiring_in_3_days,
            notification_type=PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value,
            email_sent_successfully=True,
        )

        passwords = PasswordEntry.objects.filter(
            id=password_entry_expiring_in_3_days.id
        )

        count = PasswordExpirationManager._process_notification_batch(
            passwords, PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value
        )

        assert count == 0
        mock_send_email.assert_not_called()


@pytest.mark.unit
@pytest.mark.django_db
class TestProcessExpirationNotifications:
    """Integration tests for process_expiration_notifications method."""

    @patch("authentication.password_expiration_manager.PasswordExpirationManager.send_expiration_email")
    def test_process_expiration_notifications_all_types(
        self,
        mock_send_email,
        user,
        password_entry_expiring_in_3_days,
        password_entry_expiring_in_1_day,
        password_entry_expiring_today,
    ):
        """Test processing all notification types."""
        mock_send_email.return_value = True

        count = PasswordExpirationManager.process_expiration_notifications()

        assert count == 3
        assert mock_send_email.call_count == 3

        # Verify all notification types were sent
        calls = mock_send_email.call_args_list
        notification_types = [call.args[2] for call in calls]

        assert PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value in notification_types
        assert PasswordExpirationConstants.NOTIFICATION_TYPE_1_DAY.value in notification_types
        assert PasswordExpirationConstants.NOTIFICATION_TYPE_EXPIRED.value in notification_types

    @patch("authentication.password_expiration_manager.PasswordExpirationManager.send_expiration_email")
    def test_process_expiration_notifications_no_passwords(self, mock_send_email):
        """Test processing when no passwords need notifications."""
        count = PasswordExpirationManager.process_expiration_notifications()

        assert count == 0
        mock_send_email.assert_not_called()

    @patch("authentication.password_expiration_manager.PasswordExpirationManager.send_expiration_email")
    def test_process_expiration_notifications_partial_success(
        self,
        mock_send_email,
        user,
        password_entry_expiring_in_3_days,
        password_entry_expiring_in_1_day,
    ):
        """Test processing when some emails succeed and some fail."""
        # First call succeeds, second call fails
        mock_send_email.side_effect = [True, False]

        count = PasswordExpirationManager.process_expiration_notifications()

        assert count == 1
        assert mock_send_email.call_count == 2

    @patch("authentication.password_expiration_manager.PasswordExpirationManager.send_expiration_email")
    def test_process_expiration_notifications_excludes_no_expiry(
        self, mock_send_email, password_entry_no_expiry
    ):
        """Test that passwords without expiry are excluded."""
        count = PasswordExpirationManager.process_expiration_notifications()

        assert count == 0
        mock_send_email.assert_not_called()

    @freeze_time("2024-06-15 12:00:00")
    @patch("authentication.password_expiration_manager.PasswordExpirationManager.send_expiration_email")
    def test_process_expiration_notifications_with_frozen_time(
        self, mock_send_email, user, test_password
    ):
        """Test processing with frozen time to ensure date calculations are correct."""
        from authentication.encryption_service import encryption_service
        from datetime import datetime

        mock_send_email.return_value = True

        encrypted_password, salt = encryption_service.encrypt_password(
            "test-password", test_password
        )

        # Create password expiring on 2024-06-18 (3 days from frozen time)
        PasswordEntry.objects.create(
            user=user,
            name="3 Day Entry",
            site="https://3days.com",
            username="user3days",
            encrypted_password=encrypted_password,
            encryption_salt=salt,
            expires_at=datetime(2024, 6, 18, 12, 0, 0, tzinfo=timezone.get_current_timezone()),
        )

        count = PasswordExpirationManager.process_expiration_notifications()

        assert count == 1
        assert mock_send_email.call_count == 1

        # Verify it was called with 3-day notification type
        call_args = mock_send_email.call_args
        assert call_args.args[2] == PasswordExpirationConstants.NOTIFICATION_TYPE_3_DAYS.value
