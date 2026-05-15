"""
Unit tests for User model.

Tests cover:
- User creation
- User authentication
- User properties (get_full_name, get_short_name)
- Email uniqueness
- Password hashing
- User permissions
"""

import pytest
from django.contrib.auth import authenticate
from django.db.utils import IntegrityError
from django.utils import timezone

from authentication.models import User
from tests.fixtures.factories import (
    UserFactory,
    UnverifiedUserFactory,
    InactiveUserFactory,
)


@pytest.mark.unit
@pytest.mark.django_db
class TestUserCreation:
    """Tests for User model creation."""

    def test_create_user_with_email(self):
        """Test creating a user with email."""
        user = User.objects.create_user(
            email="test@example.com", password="TestPass123!"
        )
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_verified is False
        assert user.check_password("TestPass123!")

    def test_create_user_with_all_fields(self):
        """Test creating a user with all fields."""
        user = User.objects.create_user(
            email="test@example.com",
            password="TestPass123!",
            first_name="Test",
            last_name="User",
            phone_number="+1234567890",
            username="testuser",
        )
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.phone_number == "+1234567890"
        assert user.username == "testuser"

    def test_create_user_without_password(self):
        """Test creating a user without password sets unusable password."""
        user = User.objects.create_user(email="test@example.com")
        assert not user.has_usable_password()

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            email="admin@example.com", password="AdminPass123!"
        )
        assert user.is_superuser is True
        assert user.is_staff is True
        assert user.is_active is True

    def test_user_id_is_uuid(self):
        """Test that user ID is a UUID."""
        user = UserFactory()
        assert user.id is not None
        assert len(str(user.id)) == 36  # UUID format

    def test_email_is_required(self):
        """Test that email is required."""
        with pytest.raises(ValueError):
            User.objects.create_user(email="", password="TestPass123!")

    def test_email_is_unique(self):
        """Test that email must be unique."""
        UserFactory(email="test@example.com")
        with pytest.raises(IntegrityError):
            UserFactory(email="test@example.com")

    def test_username_can_be_blank(self):
        """Test that username can be blank."""
        user = User.objects.create_user(
            email="test@example.com", password="TestPass123!"
        )
        assert user.username in [None, ""]

    def test_date_joined_auto_set(self):
        """Test that date_joined is automatically set."""
        user = UserFactory()
        assert user.date_joined is not None
        assert user.date_joined <= timezone.now()

    def test_last_login_initially_none(self):
        """Test that last_login is initially None."""
        user = UserFactory()
        assert user.last_login is None


@pytest.mark.unit
@pytest.mark.django_db
class TestUserAuthentication:
    """Tests for User authentication."""

    def test_authenticate_with_valid_credentials(self, user, test_password):
        """Test authentication with valid credentials."""
        authenticated_user = authenticate(
            email=user.email, password=test_password
        )
        assert authenticated_user is not None
        assert authenticated_user.id == user.id

    def test_authenticate_with_invalid_password(self, user):
        """Test authentication with invalid password."""
        authenticated_user = authenticate(
            email=user.email, password="WrongPassword123!"
        )
        assert authenticated_user is None

    def test_authenticate_with_invalid_email(self):
        """Test authentication with non-existent email."""
        authenticated_user = authenticate(
            email="nonexistent@example.com", password="TestPass123!"
        )
        assert authenticated_user is None

    def test_authenticate_inactive_user(self, inactive_user, test_password):
        """Test that inactive users cannot authenticate."""
        authenticated_user = authenticate(
            email=inactive_user.email, password=test_password
        )
        assert authenticated_user is None

    def test_authenticate_unverified_user(self, unverified_user, test_password):
        """Test that unverified users can authenticate."""
        authenticated_user = authenticate(
            email=unverified_user.email, password=test_password
        )
        # Unverified users can authenticate but is_verified flag is False
        assert authenticated_user is not None
        assert authenticated_user.is_verified is False

    def test_check_password_with_correct_password(self, user, test_password):
        """Test check_password with correct password."""
        assert user.check_password(test_password) is True

    def test_check_password_with_incorrect_password(self, user):
        """Test check_password with incorrect password."""
        assert user.check_password("WrongPassword123!") is False

    def test_set_password(self, user):
        """Test setting a new password."""
        new_password = "NewPassword123!"
        user.set_password(new_password)
        user.save()
        assert user.check_password(new_password) is True

    def test_password_is_hashed(self, user, test_password):
        """Test that password is hashed, not stored in plain text."""
        assert user.password != test_password
        assert len(user.password) > 50  # Hashed password is longer


@pytest.mark.unit
@pytest.mark.django_db
class TestUserProperties:
    """Tests for User model properties."""

    def test_get_full_name_with_both_names(self):
        """Test get_full_name with first and last name."""
        user = UserFactory(first_name="John", last_name="Doe")
        assert user.get_full_name() == "John Doe"

    def test_get_full_name_with_first_name_only(self):
        """Test get_full_name with only first name."""
        user = UserFactory(first_name="John", last_name="")
        assert user.get_full_name() == "John"

    def test_get_full_name_with_last_name_only(self):
        """Test get_full_name with only last name."""
        user = UserFactory(first_name="", last_name="Doe")
        assert user.get_full_name() == "Doe"

    def test_get_full_name_with_no_names(self):
        """Test get_full_name with no names falls back to email."""
        user = UserFactory(first_name="", last_name="", email="test@example.com")
        assert user.get_full_name() == "test@example.com"

    def test_get_short_name_with_first_name(self):
        """Test get_short_name with first name."""
        user = UserFactory(first_name="John", email="john@example.com")
        assert user.get_short_name() == "John"

    def test_get_short_name_without_first_name(self):
        """Test get_short_name without first name falls back to email prefix."""
        user = UserFactory(first_name="", email="john.doe@example.com")
        assert user.get_short_name() == "john.doe"

    def test_str_representation(self):
        """Test string representation of user."""
        user = UserFactory(email="test@example.com")
        assert str(user) == "test@example.com"

    def test_username_field_is_email(self):
        """Test that USERNAME_FIELD is set to email."""
        assert User.USERNAME_FIELD == "email"


@pytest.mark.unit
@pytest.mark.django_db
class TestUserPermissions:
    """Tests for User permissions."""

    def test_superuser_has_all_permissions(self):
        """Test that superuser has all permissions."""
        user = User.objects.create_superuser(
            email="admin@example.com", password="AdminPass123!"
        )
        assert user.is_superuser is True
        assert user.has_perm("any_permission") is True

    def test_regular_user_permissions(self):
        """Test regular user permissions."""
        user = UserFactory()
        assert user.is_superuser is False
        assert user.is_staff is False

    def test_staff_user_is_staff(self):
        """Test staff user has is_staff flag."""
        user = UserFactory(is_staff=True)
        assert user.is_staff is True
        assert user.is_superuser is False


@pytest.mark.unit
@pytest.mark.django_db
class TestUserStates:
    """Tests for User state management."""

    def test_verified_user(self):
        """Test verified user state."""
        user = UserFactory(is_verified=True)
        assert user.is_verified is True

    def test_unverified_user(self):
        """Test unverified user state."""
        user = UnverifiedUserFactory()
        assert user.is_verified is False
        assert user.is_active is True

    def test_inactive_user(self):
        """Test inactive user state."""
        user = InactiveUserFactory()
        assert user.is_active is False

    def test_active_user(self):
        """Test active user state."""
        user = UserFactory(is_active=True)
        assert user.is_active is True


@pytest.mark.unit
@pytest.mark.django_db
class TestUserManager:
    """Tests for UserManager."""

    def test_create_user_normalizes_email(self):
        """Test that email is normalized."""
        user = User.objects.create_user(
            email="Test@EXAMPLE.COM", password="TestPass123!"
        )
        assert user.email == "Test@example.com"  # Domain is lowercased

    def test_create_user_with_empty_email_raises_error(self):
        """Test that creating user without email raises error."""
        with pytest.raises(ValueError, match="Users must have an email address"):
            User.objects.create_user(email="", password="TestPass123!")

    def test_create_superuser_with_is_staff_false_raises_error(self):
        """Test that creating superuser with is_staff=False raises error."""
        with pytest.raises(ValueError, match="Superuser must have is_staff=True"):
            User.objects.create_superuser(
                email="admin@example.com",
                password="AdminPass123!",
                is_staff=False,
            )

    def test_create_superuser_with_is_superuser_false_raises_error(self):
        """Test that creating superuser with is_superuser=False raises error."""
        with pytest.raises(ValueError, match="Superuser must have is_superuser=True"):
            User.objects.create_superuser(
                email="admin@example.com",
                password="AdminPass123!",
                is_superuser=False,
            )


@pytest.mark.unit
@pytest.mark.django_db
class TestUserMetaOptions:
    """Tests for User model Meta options."""

    def test_user_table_name(self):
        """Test that user table name is correct."""
        assert User._meta.db_table == "auth_user"

    def test_user_model_name(self):
        """Test that user model name is correct."""
        assert User._meta.model_name == "user"

    def test_user_app_label(self):
        """Test that user app label is correct."""
        assert User._meta.app_label == "authentication"
