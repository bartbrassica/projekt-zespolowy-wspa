"""
Pytest configuration and fixtures for Digital Lockbox API tests.
"""

import os
import pytest
from django.conf import settings
from django.core.management import call_command
from django.test import Client
from datetime import timedelta
from django.utils import timezone

# Set test environment variables
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "authentication.settings")
os.environ.setdefault("DB_NAME", "test_lockbox")
os.environ.setdefault("DB_USER", "postgres")
os.environ.setdefault("DB_PASSWORD", "postgres")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5433")
os.environ.setdefault("CLIENT_SECRET", "test-secret-key-for-testing-only")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("JWT_ALG", "HS256")
os.environ.setdefault("EMAIL_BACKEND", "django.core.mail.backends.locmem.EmailBackend")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Set up test database and create necessary keys for JWT.
    """
    with django_db_blocker.unblock():
        # Create keys directory if it doesn't exist
        keys_dir = settings.BASE_DIR / "keys"
        keys_dir.mkdir(exist_ok=True)

        # For testing, we'll use HS256 instead of ES512 to avoid key generation
        # This is set in the environment variables above


@pytest.fixture
def api_client():
    """
    Django test client for API requests.
    """
    return Client()


@pytest.fixture
def authenticated_client(api_client, user):
    """
    Django test client with authenticated user.
    """
    from authentication.utils import create_jwt_tokens

    tokens = create_jwt_tokens(user)
    api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {tokens['access_token']}"
    return api_client


@pytest.fixture
def test_password():
    """
    Standard test password for user accounts.
    """
    return "TestPassword123!"


@pytest.fixture
def test_master_password():
    """
    Standard test master password for password entries.
    """
    return "MasterPassword123!"


@pytest.fixture
def user(db, test_password):
    """
    Create a standard test user.
    """
    from authentication.models import User

    user = User.objects.create_user(
        email="testuser@example.com",
        password=test_password,
        first_name="Test",
        last_name="User",
        is_verified=True,
        is_active=True,
    )
    return user


@pytest.fixture
def verified_user(db, test_password):
    """
    Create a verified test user.
    """
    from authentication.models import User

    user = User.objects.create_user(
        email="verified@example.com",
        password=test_password,
        first_name="Verified",
        last_name="User",
        is_verified=True,
        is_active=True,
    )
    return user


@pytest.fixture
def unverified_user(db, test_password):
    """
    Create an unverified test user.
    """
    from authentication.models import User

    user = User.objects.create_user(
        email="unverified@example.com",
        password=test_password,
        first_name="Unverified",
        last_name="User",
        is_verified=False,
        is_active=True,
    )
    return user


@pytest.fixture
def inactive_user(db, test_password):
    """
    Create an inactive test user.
    """
    from authentication.models import User

    user = User.objects.create_user(
        email="inactive@example.com",
        password=test_password,
        first_name="Inactive",
        last_name="User",
        is_verified=True,
        is_active=False,
    )
    return user


@pytest.fixture
def multiple_users(db, test_password):
    """
    Create multiple test users.
    """
    from authentication.models import User

    users = []
    for i in range(3):
        user = User.objects.create_user(
            email=f"user{i}@example.com",
            password=test_password,
            first_name=f"User{i}",
            last_name="Test",
            is_verified=True,
            is_active=True,
        )
        users.append(user)
    return users


@pytest.fixture
def verification_token(user):
    """
    Create a verification token for a user.
    """
    from authentication.db_utils import create_verification_token

    return create_verification_token(user)


@pytest.fixture
def password_reset_token(verified_user):
    """
    Create a password reset token for a verified user.
    """
    from authentication.db_utils import create_password_reset_token

    return create_password_reset_token(verified_user)


@pytest.fixture
def expired_token(verified_user):
    """
    Create an expired token for testing.
    """
    from authentication.models import Token

    token = Token.objects.create(
        user=verified_user,
        token_type="password_reset",
        expires_at=timezone.now() - timedelta(hours=1),
    )
    return token


@pytest.fixture
def access_token(user):
    """
    Create a valid access token for a user.
    """
    from authentication.utils import create_jwt_tokens

    tokens = create_jwt_tokens(user)
    return tokens["access_token"]


@pytest.fixture
def refresh_token(user):
    """
    Create a valid refresh token for a user.
    """
    from authentication.utils import create_jwt_tokens
    from authentication.db_utils import create_refresh_token

    tokens = create_jwt_tokens(user)
    create_refresh_token(user, tokens["jti"])
    return tokens["refresh_token"]


@pytest.fixture
def user_session(user):
    """
    Create a user session.
    """
    from authentication.models import UserSession

    session = UserSession.objects.create(
        user=user,
        session_key="test-session-key",
        ip_address="127.0.0.1",
        user_agent="Test Browser",
        device_name="Test Device",
    )
    return session


@pytest.fixture
def password_entry(user, test_master_password):
    """
    Create a test password entry.
    """
    from authentication.models import PasswordEntry
    from authentication.encryption_service import encryption_service

    encrypted_password, salt = encryption_service.encrypt_password(
        "test-password-123", test_master_password
    )

    entry = PasswordEntry.objects.create(
        user=user,
        name="Test Entry",
        site="https://example.com",
        username="testuser",
        encrypted_password=encrypted_password,
        encryption_salt=salt,
        notes="Test notes",
    )
    return entry


@pytest.fixture
def password_folder(user):
    """
    Create a test password folder.
    """
    from authentication.models import PasswordFolder

    folder = PasswordFolder.objects.create(
        user=user,
        name="Test Folder",
        icon="folder",
        color="#FF0000",
    )
    return folder


@pytest.fixture
def password_tag(user):
    """
    Create a test password tag.
    """
    from authentication.models import PasswordTag

    tag = PasswordTag.objects.create(
        user=user,
        name="test-tag",
        color="#00FF00",
    )
    return tag


@pytest.fixture
def password_share_link(password_entry, user):
    """
    Create a test password share link.
    """
    from authentication.models import PasswordShareLink

    share_link = PasswordShareLink.objects.create(
        password_entry=password_entry,
        created_by=user,
        max_views=5,
        expires_at=timezone.now() + timedelta(hours=24),
        require_authentication=False,
    )
    return share_link


@pytest.fixture
def mock_request():
    """
    Create a mock HTTP request object.
    """
    from unittest.mock import MagicMock

    request = MagicMock()
    request.META = {
        "REMOTE_ADDR": "127.0.0.1",
        "HTTP_USER_AGENT": "Test Agent",
    }
    return request


@pytest.fixture(autouse=True)
def email_backend_setup(settings):
    """
    Automatically use in-memory email backend for all tests.
    """
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


@pytest.fixture
def clear_emails():
    """
    Clear the email outbox.
    """
    from django.core import mail

    mail.outbox = []
    yield
    mail.outbox = []
