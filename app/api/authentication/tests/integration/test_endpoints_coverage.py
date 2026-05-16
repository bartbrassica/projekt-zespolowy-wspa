"""
Integration tests to achieve 100% coverage for endpoints.py
Covers edge cases and exception paths not covered by other test files.
"""

import pytest
import json
import jwt
from unittest.mock import patch, MagicMock
from django.utils import timezone
from datetime import timedelta


@pytest.mark.integration
@pytest.mark.django_db
class TestJWTAuthEdgeCases:
    """Tests for JWTAuth authentication edge cases."""

    def test_jwt_auth_missing_user_id(self, api_client):
        """Test JWT authentication with missing user_id (line 65)."""
        from authentication.utils import load_jwt_keys

        # Create a token without user_id
        private_key, _ = load_jwt_keys()

        payload = {
            "exp": (timezone.now() + timedelta(minutes=15)).timestamp(),
            "iat": timezone.now().timestamp(),
            "token_type": "access",
            # Missing user_id
        }

        token = jwt.encode(payload, private_key, algorithm="ES512")

        # Try to access a protected endpoint
        response = api_client.get(
            "/api/me",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        assert response.status_code == 401

    def test_jwt_auth_missing_exp(self, api_client, user):
        """Test JWT authentication with missing exp (line 65)."""
        from authentication.utils import load_jwt_keys

        # Create a token without exp
        private_key, _ = load_jwt_keys()

        payload = {
            "user_id": str(user.id),
            "iat": timezone.now().timestamp(),
            "token_type": "access",
            # Missing exp
        }

        token = jwt.encode(payload, private_key, algorithm="ES512")

        # Try to access a protected endpoint
        response = api_client.get(
            "/api/me",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        assert response.status_code == 401

    @patch('authentication.endpoints.verify_jwt_token')
    def test_jwt_auth_expired_token(self, mock_verify, api_client, user):
        """Test JWT authentication with expired token (line 68)."""
        # Mock verify_jwt_token to return a payload with expired timestamp
        # This bypasses JWT library's expiration check to test our defensive code
        mock_verify.return_value = {
            "user_id": str(user.id),
            "exp": (timezone.now() - timedelta(hours=1)).timestamp(),  # Expired
            "iat": (timezone.now() - timedelta(hours=2)).timestamp(),
            "token_type": "access",
        }

        # Try to access a protected endpoint with any token
        response = api_client.get(
            "/api/me",
            HTTP_AUTHORIZATION="Bearer fake-token"
        )

        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.django_db
class TestLoginEdgeCases:
    """Tests for login endpoint edge cases."""

    @patch('authentication.endpoints.authenticate')
    def test_login_inactive_user(self, mock_authenticate, api_client, inactive_user, test_password):
        """Test login with inactive user (lines 131-132)."""
        # Mock authenticate to return the inactive user
        # This bypasses Django's default behavior of returning None for inactive users
        mock_authenticate.return_value = inactive_user

        login_data = {
            "email": inactive_user.email,
            "password": test_password,
        }

        response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )

        assert response.status_code == 401
        assert "disabled" in response.json()["detail"].lower()


@pytest.mark.integration
@pytest.mark.django_db
class TestRefreshTokenEdgeCases:
    """Tests for refresh token endpoint edge cases."""

    def test_refresh_token_missing_jti(self, api_client, user):
        """Test refresh token with missing jti (line 174)."""
        from authentication.utils import load_jwt_keys

        # Create a refresh token without jti
        private_key, _ = load_jwt_keys()

        payload = {
            "user_id": str(user.id),
            "exp": (timezone.now() + timedelta(days=14)).timestamp(),
            "iat": timezone.now().timestamp(),
            "token_type": "refresh",
            # Missing jti
        }

        token = jwt.encode(payload, private_key, algorithm="ES512")

        refresh_data = {
            "refresh_token": token,
        }

        response = api_client.post(
            "/api/token/refresh",
            data=json.dumps(refresh_data),
            content_type="application/json",
        )

        assert response.status_code == 401
        assert "invalid token format" in response.json()["detail"].lower()
