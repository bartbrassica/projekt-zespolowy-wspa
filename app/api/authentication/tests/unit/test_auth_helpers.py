"""
Unit tests for authentication helper functions and classes.
Tests for JWTAuth class and get_user_from_auth utility.
"""

import pytest
import jwt
from datetime import datetime, timedelta, timezone as dt_timezone
from unittest.mock import MagicMock
from django.conf import settings
from django.utils import timezone
from ninja.errors import HttpError

from authentication.endpoints import JWTAuth, get_user_from_auth
from authentication.models import User


@pytest.mark.unit
@pytest.mark.django_db
class TestJWTAuthClass:
    """Test JWTAuth authentication class."""

    def test_authenticate_with_valid_token(self, user):
        """Test authentication with a valid JWT token."""
        from authentication.utils import create_jwt_tokens

        tokens = create_jwt_tokens(user)
        auth = JWTAuth()
        request = MagicMock()

        authenticated_user = auth.authenticate(request, tokens["access_token"])

        assert authenticated_user is not None
        assert authenticated_user.id == user.id
        assert authenticated_user.email == user.email

    def test_authenticate_with_invalid_token(self):
        """Test authentication with an invalid token."""
        auth = JWTAuth()
        request = MagicMock()

        result = auth.authenticate(request, "invalid.token.here")

        assert result is None

    def test_authenticate_with_token_missing_user_id(self):
        """Test authentication with token missing user_id field."""
        payload = {
            "exp": (datetime.now(dt_timezone.utc) + timedelta(hours=1)).timestamp(),
            "iat": datetime.now(dt_timezone.utc).timestamp(),
            "token_type": "access",
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        auth = JWTAuth()
        request = MagicMock()

        result = auth.authenticate(request, token)

        assert result is None

    def test_authenticate_with_token_missing_exp(self, user):
        """Test authentication with token missing exp field."""
        payload = {
            "user_id": str(user.id),
            "iat": datetime.now(dt_timezone.utc).timestamp(),
            "token_type": "access",
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        auth = JWTAuth()
        request = MagicMock()

        result = auth.authenticate(request, token)

        assert result is None

    def test_authenticate_with_token_missing_both_user_id_and_exp(self):
        """Test authentication with token missing both user_id and exp."""
        payload = {
            "iat": datetime.now(dt_timezone.utc).timestamp(),
            "token_type": "access",
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        auth = JWTAuth()
        request = MagicMock()

        result = auth.authenticate(request, token)

        assert result is None

    def test_authenticate_with_expired_token(self, user):
        """Test authentication with expired token."""
        payload = {
            "user_id": str(user.id),
            "exp": (datetime.now(dt_timezone.utc) - timedelta(hours=1)).timestamp(),
            "iat": (datetime.now(dt_timezone.utc) - timedelta(hours=2)).timestamp(),
            "token_type": "access",
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        auth = JWTAuth()
        request = MagicMock()

        result = auth.authenticate(request, token)

        assert result is None

    def test_authenticate_with_just_expired_token(self, user):
        """Test authentication with token that just expired."""
        # Token expired 1 second ago
        payload = {
            "user_id": str(user.id),
            "exp": (datetime.now(dt_timezone.utc) - timedelta(seconds=1)).timestamp(),
            "iat": (datetime.now(dt_timezone.utc) - timedelta(hours=1)).timestamp(),
            "token_type": "access",
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        auth = JWTAuth()
        request = MagicMock()

        result = auth.authenticate(request, token)

        assert result is None

    def test_authenticate_with_nonexistent_user(self):
        """Test authentication with token for user that doesn't exist."""
        fake_user_id = "00000000-0000-0000-0000-000000000000"
        payload = {
            "user_id": fake_user_id,
            "exp": (datetime.now(dt_timezone.utc) + timedelta(hours=1)).timestamp(),
            "iat": datetime.now(dt_timezone.utc).timestamp(),
            "token_type": "access",
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        auth = JWTAuth()
        request = MagicMock()

        result = auth.authenticate(request, token)

        assert result is None

    def test_authenticate_with_deleted_user(self, user):
        """Test authentication with token for user that was deleted."""
        from authentication.utils import create_jwt_tokens

        tokens = create_jwt_tokens(user)
        user_id = user.id

        user.delete()

        auth = JWTAuth()
        request = MagicMock()

        result = auth.authenticate(request, tokens["access_token"])

        assert result is None

    def test_authenticate_with_malformed_token(self):
        """Test authentication with malformed token."""
        auth = JWTAuth()
        request = MagicMock()

        malformed_tokens = [
            "not-a-jwt",
            "header.payload",  # Missing signature
            "header.payload.signature.extra",  # Too many parts
            "",  # Empty string
        ]

        for token in malformed_tokens:
            result = auth.authenticate(request, token)
            assert result is None

    def test_authenticate_with_token_wrong_signature(self, user):
        """Test authentication with token signed with wrong key."""
        payload = {
            "user_id": str(user.id),
            "exp": (datetime.now(dt_timezone.utc) + timedelta(hours=1)).timestamp(),
            "iat": datetime.now(dt_timezone.utc).timestamp(),
            "token_type": "access",
        }
        # Sign with different secret
        token = jwt.encode(payload, "wrong-secret-key", algorithm="HS256")

        auth = JWTAuth()
        request = MagicMock()

        result = auth.authenticate(request, token)

        assert result is None

    def test_authenticate_returns_user_object(self, user):
        """Test that authenticate returns a proper User object."""
        from authentication.utils import create_jwt_tokens

        tokens = create_jwt_tokens(user)
        auth = JWTAuth()
        request = MagicMock()

        authenticated_user = auth.authenticate(request, tokens["access_token"])

        assert isinstance(authenticated_user, User)
        assert hasattr(authenticated_user, "email")
        assert hasattr(authenticated_user, "check_password")


@pytest.mark.unit
@pytest.mark.django_db
class TestGetUserFromAuth:
    """Test get_user_from_auth utility function."""

    def test_get_user_from_auth_with_user_object(self, user):
        """Test getting user when auth is a User object."""
        result = get_user_from_auth(user)

        assert result == user
        assert result.id == user.id

    def test_get_user_from_auth_with_no_auth(self):
        """Test getting user when auth is None."""
        with pytest.raises(HttpError) as exc_info:
            get_user_from_auth(None)

        assert exc_info.value.status_code == 401
        assert "Authentication required" in str(exc_info.value)

    def test_get_user_from_auth_with_empty_auth(self):
        """Test getting user when auth is empty."""
        with pytest.raises(HttpError) as exc_info:
            get_user_from_auth("")

        assert exc_info.value.status_code == 401
        assert "Authentication required" in str(exc_info.value)

    def test_get_user_from_auth_with_false_auth(self):
        """Test getting user when auth is False."""
        with pytest.raises(HttpError) as exc_info:
            get_user_from_auth(False)

        assert exc_info.value.status_code == 401
        assert "Authentication required" in str(exc_info.value)

    def test_get_user_from_auth_with_string_user_id(self, user):
        """Test getting user when auth is a string user ID."""
        result = get_user_from_auth(str(user.id))

        assert result.id == user.id
        assert result.email == user.email

    def test_get_user_from_auth_with_string_nonexistent_user_id(self):
        """Test getting user when auth is a string ID for nonexistent user."""
        fake_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(HttpError) as exc_info:
            get_user_from_auth(fake_id)

        assert exc_info.value.status_code == 401
        assert "Invalid authentication" in str(exc_info.value)

    def test_get_user_from_auth_with_invalid_string_id(self):
        """Test getting user when auth is an invalid UUID string."""
        with pytest.raises(HttpError) as exc_info:
            get_user_from_auth("not-a-valid-uuid")

        assert exc_info.value.status_code == 401
        assert "Invalid authentication" in str(exc_info.value)

    def test_get_user_from_auth_with_integer(self):
        """Test getting user when auth is an integer."""
        with pytest.raises(HttpError) as exc_info:
            get_user_from_auth(12345)

        assert exc_info.value.status_code == 401
        assert "Invalid authentication" in str(exc_info.value)

    def test_get_user_from_auth_with_dict(self):
        """Test getting user when auth is a dictionary."""
        with pytest.raises(HttpError) as exc_info:
            get_user_from_auth({"user_id": "test"})

        assert exc_info.value.status_code == 401
        assert "Invalid authentication" in str(exc_info.value)

    def test_get_user_from_auth_with_list(self):
        """Test getting user when auth is a list."""
        with pytest.raises(HttpError) as exc_info:
            get_user_from_auth(["user"])

        assert exc_info.value.status_code == 401
        assert "Invalid authentication" in str(exc_info.value)

    def test_get_user_from_auth_with_mock_user_object(self, user):
        """Test that get_user_from_auth checks for check_password attribute."""
        # This tests the hasattr(auth, "check_password") path
        result = get_user_from_auth(user)

        assert result == user
        assert hasattr(result, "check_password")

    def test_get_user_from_auth_with_object_without_check_password(self):
        """Test with an object that doesn't have check_password."""
        class FakeAuth:
            pass

        fake_auth = FakeAuth()

        with pytest.raises(HttpError) as exc_info:
            get_user_from_auth(fake_auth)

        assert exc_info.value.status_code == 401
        assert "Invalid authentication" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.django_db
class TestAuthenticationIntegration:
    """Test integration between JWTAuth and get_user_from_auth."""

    def test_full_authentication_flow(self, user):
        """Test complete authentication flow from token to user."""
        from authentication.utils import create_jwt_tokens

        # Create tokens
        tokens = create_jwt_tokens(user)

        # Authenticate with JWT
        auth = JWTAuth()
        request = MagicMock()
        authenticated_user = auth.authenticate(request, tokens["access_token"])

        # Get user from auth result
        final_user = get_user_from_auth(authenticated_user)

        assert final_user.id == user.id
        assert final_user.email == user.email

    def test_authentication_flow_with_invalid_token(self):
        """Test authentication flow with invalid token."""
        auth = JWTAuth()
        request = MagicMock()

        # Authentication fails, returns None
        authenticated_user = auth.authenticate(request, "invalid.token")

        # Trying to get user from None should raise error
        with pytest.raises(HttpError) as exc_info:
            get_user_from_auth(authenticated_user)

        assert exc_info.value.status_code == 401
        assert "Authentication required" in str(exc_info.value)

    def test_authentication_with_multiple_users(self, multiple_users):
        """Test that authentication correctly identifies different users."""
        from authentication.utils import create_jwt_tokens

        user1, user2, user3 = multiple_users

        # Create tokens for each user
        tokens1 = create_jwt_tokens(user1)
        tokens2 = create_jwt_tokens(user2)

        auth = JWTAuth()
        request = MagicMock()

        # Authenticate each token
        auth_user1 = auth.authenticate(request, tokens1["access_token"])
        auth_user2 = auth.authenticate(request, tokens2["access_token"])

        # Get users from auth
        final_user1 = get_user_from_auth(auth_user1)
        final_user2 = get_user_from_auth(auth_user2)

        # Verify correct users
        assert final_user1.id == user1.id
        assert final_user2.id == user2.id
        assert final_user1.id != final_user2.id

    def test_authentication_with_inactive_user(self, user):
        """Test authentication with token for inactive user."""
        from authentication.utils import create_jwt_tokens

        # Create token while user is active
        tokens = create_jwt_tokens(user)

        # Deactivate user
        user.is_active = False
        user.save()

        # Token should still authenticate (deactivation checked at endpoint level)
        auth = JWTAuth()
        request = MagicMock()
        authenticated_user = auth.authenticate(request, tokens["access_token"])

        # Authentication succeeds even for inactive user
        assert authenticated_user is not None
        assert authenticated_user.id == user.id
        assert authenticated_user.is_active is False
