"""
Factory Boy factories for creating test data.
"""

import factory
from factory.django import DjangoModelFactory
from factory import fuzzy
from faker import Faker
from datetime import timedelta
from django.utils import timezone
import uuid

from authentication.models import (
    User,
    Token,
    LoginAttempt,
    UserSession,
    PasswordHistory,
    PasswordEntry,
    PasswordFolder,
    PasswordTag,
    PasswordShareLink,
    PasswordEntryHistory,
    PasswordAccessLog,
    PasswordExpirationNotification,
)
from authentication.encryption_service import encryption_service

fake = Faker()


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances."""

    class Meta:
        model = User

    id = factory.LazyFunction(uuid.uuid4)
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone_number = factory.Faker("msisdn")
    is_active = True
    is_staff = False
    is_verified = True
    date_joined = factory.LazyFunction(timezone.now)

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Set password after user creation."""
        if not create:
            return
        password = extracted or "TestPassword123!"
        obj.set_password(password)
        obj.save()


class UnverifiedUserFactory(UserFactory):
    """Factory for creating unverified User instances."""

    is_verified = False


class InactiveUserFactory(UserFactory):
    """Factory for creating inactive User instances."""

    is_active = False


class TokenFactory(DjangoModelFactory):
    """Factory for creating Token instances."""

    class Meta:
        model = Token

    user = factory.SubFactory(UserFactory)
    token = factory.LazyFunction(uuid.uuid4)
    token_type = "verification"
    created_at = factory.LazyFunction(timezone.now)
    expires_at = factory.LazyFunction(
        lambda: timezone.now() + timedelta(hours=24)
    )
    is_used = False


class VerificationTokenFactory(TokenFactory):
    """Factory for verification tokens."""

    token_type = "verification"


class PasswordResetTokenFactory(TokenFactory):
    """Factory for password reset tokens."""

    token_type = "password_reset"
    expires_at = factory.LazyFunction(
        lambda: timezone.now() + timedelta(hours=1)
    )


class RefreshTokenFactory(TokenFactory):
    """Factory for refresh tokens."""

    token_type = "refresh"
    expires_at = factory.LazyFunction(
        lambda: timezone.now() + timedelta(days=14)
    )


class ExpiredTokenFactory(TokenFactory):
    """Factory for expired tokens."""

    expires_at = factory.LazyFunction(
        lambda: timezone.now() - timedelta(hours=1)
    )


class LoginAttemptFactory(DjangoModelFactory):
    """Factory for creating LoginAttempt instances."""

    class Meta:
        model = LoginAttempt

    user = factory.SubFactory(UserFactory)
    email = factory.SelfAttribute("user.email")
    ip_address = factory.Faker("ipv4")
    user_agent = factory.Faker("user_agent")
    timestamp = factory.LazyFunction(timezone.now)
    successful = False


class SuccessfulLoginAttemptFactory(LoginAttemptFactory):
    """Factory for successful login attempts."""

    successful = True


class UserSessionFactory(DjangoModelFactory):
    """Factory for creating UserSession instances."""

    class Meta:
        model = UserSession

    user = factory.SubFactory(UserFactory)
    session_key = factory.LazyFunction(lambda: uuid.uuid4().hex)
    ip_address = factory.Faker("ipv4")
    user_agent = factory.Faker("user_agent")
    device_name = factory.Faker("word")
    created_at = factory.LazyFunction(timezone.now)
    last_activity = factory.LazyFunction(timezone.now)
    is_active = True


class PasswordHistoryFactory(DjangoModelFactory):
    """Factory for creating PasswordHistory instances."""

    class Meta:
        model = PasswordHistory

    user = factory.SubFactory(UserFactory)
    password = factory.Faker("password")
    created_at = factory.LazyFunction(timezone.now)


class PasswordFolderFactory(DjangoModelFactory):
    """Factory for creating PasswordFolder instances."""

    class Meta:
        model = PasswordFolder

    id = factory.LazyFunction(uuid.uuid4)
    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Folder {n}")
    parent = None
    icon = factory.Faker("word")
    color = factory.Faker("hex_color")
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class PasswordTagFactory(DjangoModelFactory):
    """Factory for creating PasswordTag instances."""

    class Meta:
        model = PasswordTag

    id = factory.LazyFunction(uuid.uuid4)
    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"tag-{n}")
    color = factory.Faker("hex_color")
    created_at = factory.LazyFunction(timezone.now)


class PasswordEntryFactory(DjangoModelFactory):
    """Factory for creating PasswordEntry instances."""

    class Meta:
        model = PasswordEntry

    id = factory.LazyFunction(uuid.uuid4)
    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Entry {n}")
    site = factory.Faker("url")
    username = factory.Faker("user_name")
    notes = factory.Faker("text", max_nb_chars=200)
    expires_at = None
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)
    last_accessed = None
    folder = None
    is_favorite = False

    @factory.lazy_attribute
    def encrypted_password(self):
        """Generate encrypted password."""
        master_password = "MasterPassword123!"
        encrypted, salt = encryption_service.encrypt_password(
            "test-password-123", master_password
        )
        return encrypted

    @factory.lazy_attribute
    def encryption_salt(self):
        """Generate encryption salt."""
        master_password = "MasterPassword123!"
        _, salt = encryption_service.encrypt_password(
            "test-password-123", master_password
        )
        return salt


class PasswordEntryWithExpirationFactory(PasswordEntryFactory):
    """Factory for password entries with expiration."""

    expires_at = factory.LazyFunction(
        lambda: timezone.now() + timedelta(days=30)
    )


class ExpiredPasswordEntryFactory(PasswordEntryFactory):
    """Factory for expired password entries."""

    expires_at = factory.LazyFunction(
        lambda: timezone.now() - timedelta(days=1)
    )


class FavoritePasswordEntryFactory(PasswordEntryFactory):
    """Factory for favorite password entries."""

    is_favorite = True


class PasswordShareLinkFactory(DjangoModelFactory):
    """Factory for creating PasswordShareLink instances."""

    class Meta:
        model = PasswordShareLink

    id = factory.LazyFunction(uuid.uuid4)
    password_entry = factory.SubFactory(PasswordEntryFactory)
    created_by = factory.SelfAttribute("password_entry.user")
    share_token = factory.LazyFunction(uuid.uuid4)
    max_views = 1
    current_views = 0
    expires_at = factory.LazyFunction(
        lambda: timezone.now() + timedelta(hours=24)
    )
    require_authentication = False
    allowed_email = ""
    created_at = factory.LazyFunction(timezone.now)
    last_accessed = None
    accessed_by_ip = None


class ExpiredShareLinkFactory(PasswordShareLinkFactory):
    """Factory for expired share links."""

    expires_at = factory.LazyFunction(
        lambda: timezone.now() - timedelta(hours=1)
    )


class PasswordEntryHistoryFactory(DjangoModelFactory):
    """Factory for creating PasswordEntryHistory instances."""

    class Meta:
        model = PasswordEntryHistory

    id = factory.LazyFunction(uuid.uuid4)
    password_entry = factory.SubFactory(PasswordEntryFactory)
    encrypted_password = factory.SelfAttribute("password_entry.encrypted_password")
    encryption_salt = factory.SelfAttribute("password_entry.encryption_salt")
    changed_at = factory.LazyFunction(timezone.now)
    changed_by = factory.SelfAttribute("password_entry.user")
    change_reason = "User update"


class PasswordAccessLogFactory(DjangoModelFactory):
    """Factory for creating PasswordAccessLog instances."""

    class Meta:
        model = PasswordAccessLog

    id = factory.LazyFunction(uuid.uuid4)
    password_entry = factory.SubFactory(PasswordEntryFactory)
    user = factory.SelfAttribute("password_entry.user")
    action = fuzzy.FuzzyChoice(["view", "copy", "update", "share", "delete"])
    ip_address = factory.Faker("ipv4")
    user_agent = factory.Faker("user_agent")
    timestamp = factory.LazyFunction(timezone.now)


class PasswordExpirationNotificationFactory(DjangoModelFactory):
    """Factory for creating PasswordExpirationNotification instances."""

    class Meta:
        model = PasswordExpirationNotification

    id = factory.LazyFunction(uuid.uuid4)
    password_entry = factory.SubFactory(PasswordEntryWithExpirationFactory)
    notification_type = fuzzy.FuzzyChoice(["3_days", "1_day", "expired"])
    sent_at = factory.LazyFunction(timezone.now)
    email_sent_successfully = True
