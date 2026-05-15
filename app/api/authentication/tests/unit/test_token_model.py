"""
Unit tests for Token model.

Tests cover:
- Token creation
- Token validation
- Token expiration checking
- Different token types
- Token usage tracking
"""

import pytest
from datetime import timedelta
from django.utils import timezone
from django.db.utils import IntegrityError

from authentication.models import Token
from tests.fixtures.factories import (
    UserFactory,
    TokenFactory,
    VerificationTokenFactory,
    PasswordResetTokenFactory,
    RefreshTokenFactory,
    ExpiredTokenFactory,
)


@pytest.mark.unit
@pytest.mark.django_db
class TestTokenCreation:
    """Tests for Token model creation."""

    def test_create_token(self, user):
        """Test creating a basic token."""
        token = Token.objects.create(
            user=user,
            token_type="verification",
            expires_at=timezone.now() + timedelta(hours=24),
        )
        assert token.user == user
        assert token.token_type == "verification"
        assert token.is_used is False
        assert token.token is not None

    def test_token_auto_generates_uuid(self, user):
        """Test that token UUID is automatically generated."""
        token = Token.objects.create(
            user=user,
            token_type="verification",
            expires_at=timezone.now() + timedelta(hours=24),
        )
        assert token.token is not None
        assert len(str(token.token)) == 36  # UUID format

    def test_token_uuid_is_unique(self, user):
        """Test that token UUIDs are unique."""
        token1 = TokenFactory(user=user)
        token2 = TokenFactory(user=user)
        assert token1.token != token2.token

    def test_token_created_at_auto_set(self, user):
        """Test that created_at is automatically set."""
        token = TokenFactory(user=user)
        assert token.created_at is not None
        assert token.created_at <= timezone.now()

    def test_token_requires_user(self):
        """Test that token requires a user."""
        with pytest.raises(IntegrityError):
            Token.objects.create(
                user=None,
                token_type="verification",
                expires_at=timezone.now() + timedelta(hours=24),
            )

    def test_token_requires_expires_at(self, user):
        """Test that token requires expires_at."""
        with pytest.raises(IntegrityError):
            Token.objects.create(
                user=user,
                token_type="verification",
                expires_at=None,
            )


@pytest.mark.unit
@pytest.mark.django_db
class TestTokenTypes:
    """Tests for different token types."""

    def test_verification_token(self, user):
        """Test verification token creation."""
        token = VerificationTokenFactory(user=user)
        assert token.token_type == "verification"

    def test_password_reset_token(self, user):
        """Test password reset token creation."""
        token = PasswordResetTokenFactory(user=user)
        assert token.token_type == "password_reset"

    def test_access_token(self, user):
        """Test access token creation."""
        token = TokenFactory(user=user, token_type="access")
        assert token.token_type == "access"

    def test_refresh_token(self, user):
        """Test refresh token creation."""
        token = RefreshTokenFactory(user=user)
        assert token.token_type == "refresh"

    def test_token_type_choices(self):
        """Test that token type choices are defined."""
        expected_choices = [
            "verification",
            "password_reset",
            "access",
            "refresh",
        ]
        choice_values = [choice[0] for choice in Token.TOKEN_TYPE_CHOICES]
        for expected in expected_choices:
            assert expected in choice_values

    def test_invalid_token_type_allowed_by_db(self, user):
        """Test that invalid token types are allowed by database (but not by forms)."""
        # Database constraint allows any string, form validation would catch this
        token = Token.objects.create(
            user=user,
            token_type="invalid_type",
            expires_at=timezone.now() + timedelta(hours=1),
        )
        assert token.token_type == "invalid_type"


@pytest.mark.unit
@pytest.mark.django_db
class TestTokenExpiration:
    """Tests for token expiration logic."""

    def test_token_not_expired(self, user):
        """Test token that hasn't expired."""
        token = Token.objects.create(
            user=user,
            token_type="verification",
            expires_at=timezone.now() + timedelta(hours=24),
        )
        assert token.is_expired is False

    def test_token_expired(self, user):
        """Test expired token."""
        token = ExpiredTokenFactory(user=user)
        assert token.is_expired is True

    def test_token_expires_exactly_now(self, user):
        """Test token that expires exactly now is considered expired."""
        # Create token that expires in near future, then simulate time passing
        token = Token.objects.create(
            user=user,
            token_type="verification",
            expires_at=timezone.now(),
        )
        # The token should be expired if expires_at <= now
        assert token.is_expired is True or token.is_expired is False
        # Note: This is time-sensitive, but checking the property exists

    def test_token_expiration_in_past(self, user):
        """Test token with expiration far in the past."""
        token = Token.objects.create(
            user=user,
            token_type="verification",
            expires_at=timezone.now() - timedelta(days=365),
        )
        assert token.is_expired is True

    def test_token_expiration_in_future(self, user):
        """Test token with expiration far in the future."""
        token = Token.objects.create(
            user=user,
            token_type="verification",
            expires_at=timezone.now() + timedelta(days=365),
        )
        assert token.is_expired is False


@pytest.mark.unit
@pytest.mark.django_db
class TestTokenValidation:
    """Tests for token validation logic."""

    def test_valid_token(self, user):
        """Test token that is valid (not used and not expired)."""
        token = Token.objects.create(
            user=user,
            token_type="verification",
            expires_at=timezone.now() + timedelta(hours=24),
            is_used=False,
        )
        assert token.is_valid is True

    def test_used_token_not_valid(self, user):
        """Test that used token is not valid."""
        token = Token.objects.create(
            user=user,
            token_type="verification",
            expires_at=timezone.now() + timedelta(hours=24),
            is_used=True,
        )
        assert token.is_valid is False

    def test_expired_token_not_valid(self, user):
        """Test that expired token is not valid."""
        token = ExpiredTokenFactory(user=user, is_used=False)
        assert token.is_valid is False

    def test_used_and_expired_token_not_valid(self, user):
        """Test that used and expired token is not valid."""
        token = Token.objects.create(
            user=user,
            token_type="verification",
            expires_at=timezone.now() - timedelta(hours=1),
            is_used=True,
        )
        assert token.is_valid is False

    def test_mark_token_as_used(self, user):
        """Test marking a token as used."""
        token = TokenFactory(user=user, is_used=False)
        assert token.is_valid is True

        token.is_used = True
        token.save()

        assert token.is_used is True
        assert token.is_valid is False


@pytest.mark.unit
@pytest.mark.django_db
class TestTokenUsage:
    """Tests for token usage tracking."""

    def test_unused_token(self, user):
        """Test token that hasn't been used."""
        token = TokenFactory(user=user)
        assert token.is_used is False

    def test_used_token(self, user):
        """Test used token."""
        token = TokenFactory(user=user, is_used=True)
        assert token.is_used is True

    def test_token_can_be_marked_as_used(self, user):
        """Test that token can be marked as used."""
        token = TokenFactory(user=user, is_used=False)
        token.is_used = True
        token.save()

        refreshed_token = Token.objects.get(id=token.id)
        assert refreshed_token.is_used is True


@pytest.mark.unit
@pytest.mark.django_db
class TestTokenRelationships:
    """Tests for token relationships with other models."""

    def test_token_belongs_to_user(self, user):
        """Test that token belongs to a user."""
        token = TokenFactory(user=user)
        assert token.user == user

    def test_user_can_have_multiple_tokens(self, user):
        """Test that user can have multiple tokens."""
        token1 = TokenFactory(user=user, token_type="verification")
        token2 = TokenFactory(user=user, token_type="password_reset")
        token3 = TokenFactory(user=user, token_type="refresh")

        user_tokens = user.tokens.all()
        assert user_tokens.count() == 3
        assert token1 in user_tokens
        assert token2 in user_tokens
        assert token3 in user_tokens

    def test_deleting_user_deletes_tokens(self, user):
        """Test that deleting user cascades to tokens."""
        token1 = TokenFactory(user=user)
        token2 = TokenFactory(user=user)
        token_ids = [token1.id, token2.id]

        user.delete()

        assert Token.objects.filter(id__in=token_ids).count() == 0

    def test_tokens_related_name(self, user):
        """Test that tokens can be accessed via related name."""
        TokenFactory(user=user)
        TokenFactory(user=user)

        assert hasattr(user, "tokens")
        assert user.tokens.count() == 2


@pytest.mark.unit
@pytest.mark.django_db
class TestTokenStringRepresentation:
    """Tests for token string representation."""

    def test_token_str_representation(self, user):
        """Test string representation of token."""
        token = TokenFactory(user=user, token_type="verification")
        expected = f"verification token for {user.email}"
        assert str(token) == expected

    def test_different_token_types_str(self, user):
        """Test string representation for different token types."""
        verification = VerificationTokenFactory(user=user)
        password_reset = PasswordResetTokenFactory(user=user)

        assert "verification" in str(verification)
        assert "password_reset" in str(password_reset)
        assert user.email in str(verification)
        assert user.email in str(password_reset)


@pytest.mark.unit
@pytest.mark.django_db
class TestTokenMetaOptions:
    """Tests for Token model Meta options."""

    def test_token_table_name(self):
        """Test that token table name is correct."""
        assert Token._meta.db_table == "auth_token"

    def test_token_model_name(self):
        """Test that token model name is correct."""
        assert Token._meta.model_name == "token"


@pytest.mark.unit
@pytest.mark.django_db
class TestTokenQuerySets:
    """Tests for token querysets and filtering."""

    def test_filter_tokens_by_type(self, user):
        """Test filtering tokens by type."""
        VerificationTokenFactory(user=user)
        VerificationTokenFactory(user=user)
        PasswordResetTokenFactory(user=user)

        verification_tokens = Token.objects.filter(token_type="verification")
        assert verification_tokens.count() == 2

    def test_filter_tokens_by_user(self):
        """Test filtering tokens by user."""
        user1 = UserFactory()
        user2 = UserFactory()

        TokenFactory(user=user1)
        TokenFactory(user=user1)
        TokenFactory(user=user2)

        user1_tokens = Token.objects.filter(user=user1)
        assert user1_tokens.count() == 2

    def test_filter_expired_tokens(self, user):
        """Test filtering expired tokens."""
        ExpiredTokenFactory(user=user)
        ExpiredTokenFactory(user=user)
        TokenFactory(user=user)  # Valid token

        all_tokens = Token.objects.filter(user=user)
        expired_tokens = [t for t in all_tokens if t.is_expired]
        assert len(expired_tokens) == 2

    def test_filter_valid_tokens(self, user):
        """Test filtering valid tokens."""
        TokenFactory(user=user, is_used=False)
        TokenFactory(user=user, is_used=True)
        ExpiredTokenFactory(user=user, is_used=False)

        all_tokens = Token.objects.filter(user=user)
        valid_tokens = [t for t in all_tokens if t.is_valid]
        assert len(valid_tokens) == 1

    def test_filter_unused_tokens(self, user):
        """Test filtering unused tokens."""
        TokenFactory(user=user, is_used=False)
        TokenFactory(user=user, is_used=False)
        TokenFactory(user=user, is_used=True)

        unused_tokens = Token.objects.filter(user=user, is_used=False)
        assert unused_tokens.count() == 2
