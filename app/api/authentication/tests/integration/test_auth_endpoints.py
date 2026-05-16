"""
Integration tests for authentication endpoints: register, login, logout.
"""

import pytest
import json
from django.core import mail

from authentication.models import User, Token, UserSession


@pytest.mark.integration
@pytest.mark.django_db
class TestRegisterEndpoint:

    def test_register_user_success(self, api_client, clear_emails):
        data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = api_client.post(
            "/api/register",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 201
        response_data = response.json()

        assert "id" in response_data
        assert response_data["email"] == data["email"]
        assert response_data["first_name"] == data["first_name"]
        assert response_data["last_name"] == data["last_name"]
        assert response_data["is_verified"] is False
        assert "password" not in response_data

        user = User.objects.get(email=data["email"])
        assert user.check_password(data["password"])

        assert len(mail.outbox) == 1
        assert data["email"] in mail.outbox[0].to

        token = Token.objects.filter(user=user, token_type="verification").first()
        assert token is not None
        assert token.is_used is False

    def test_register_duplicate_email(self, api_client, user):
        data = {
            "email": user.email,
            "password": "SecurePass123!",
            "first_name": "Jane",
            "last_name": "Doe",
        }

        response = api_client.post(
            "/api/register",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_register_invalid_email(self, api_client):
        data = {
            "email": "invalid-email",
            "password": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = api_client.post(
            "/api/register",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 422

    def test_register_missing_required_fields(self, api_client):
        test_cases = [
            {},
            {"email": "test@example.com"},
            {"password": "SecurePass123!"},
        ]

        for data in test_cases:
            response = api_client.post(
                "/api/register",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert response.status_code in [400, 422]

    def test_register_with_minimal_data(self, api_client, clear_emails):
        data = {
            "email": "minimal@example.com",
            "password": "SecurePass123!",
            "first_name": "Min",
            "last_name": "User",
        }

        response = api_client.post(
            "/api/register",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 201


@pytest.mark.integration
@pytest.mark.django_db
class TestLoginEndpoint:

    def test_login_success(self, api_client, verified_user, test_password):
        data = {"email": verified_user.email, "password": test_password}

        response = api_client.post(
            "/api/login",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = response.json()

        assert "access_token" in response_data
        assert "refresh_token" in response_data
        assert "token_type" in response_data
        assert "expires_in" in response_data
        assert response_data["token_type"] == "bearer"

        assert len(response_data["access_token"]) > 50
        assert len(response_data["refresh_token"]) > 50

        session = UserSession.objects.filter(user=verified_user).first()
        assert session is not None

        refresh_token = Token.objects.filter(
            user=verified_user, token_type="refresh"
        ).first()
        assert refresh_token is not None

    def test_login_with_remember_me(self, api_client, verified_user, test_password):
        data = {
            "email": verified_user.email,
            "password": test_password,
            "remember_me": True,
        }

        response = api_client.post(
            "/api/login",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200

    def test_login_invalid_credentials(self, api_client, verified_user):
        data = {"email": verified_user.email, "password": "WrongPassword123!"}

        response = api_client.post(
            "/api/login",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, api_client):
        data = {"email": "nonexistent@example.com", "password": "SomePassword123!"}

        response = api_client.post(
            "/api/login",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_login_unverified_user(self, api_client, unverified_user, test_password):
        data = {"email": unverified_user.email, "password": test_password}

        response = api_client.post(
            "/api/login",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 401
        assert "verify" in response.json()["detail"].lower()

    def test_login_inactive_user(self, api_client, inactive_user, test_password):
        data = {"email": inactive_user.email, "password": test_password}

        response = api_client.post(
            "/api/login",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 401
        detail = response.json()["detail"].lower()
        assert "disabled" in detail or "invalid" in detail

    def test_login_missing_credentials(self, api_client):
        test_cases = [
            {},
            {"email": "test@example.com"},
            {"password": "password123"},
        ]

        for data in test_cases:
            response = api_client.post(
                "/api/login",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert response.status_code in [400, 422]

    def test_login_empty_credentials(self, api_client):
        data = {"email": "", "password": ""}

        response = api_client.post(
            "/api/login",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code in [400, 401, 422]

    def test_login_updates_last_login(self, api_client, verified_user, test_password):
        original_last_login = verified_user.last_login
        data = {"email": verified_user.email, "password": test_password}

        response = api_client.post(
            "/api/login",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200

        verified_user.refresh_from_db()
        assert verified_user.last_login is not None
        if original_last_login:
            assert verified_user.last_login > original_last_login


@pytest.mark.integration
@pytest.mark.django_db
class TestLogoutEndpoint:

    def test_logout_success(self, authenticated_client, user):
        from authentication.utils import create_jwt_tokens
        from authentication.db_utils import create_refresh_token

        tokens = create_jwt_tokens(user)
        create_refresh_token(user, tokens["jti"])

        response = authenticated_client.post("/api/logout")

        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()

        active_tokens = Token.objects.filter(
            user=user, token_type="refresh", is_used=False
        ).count()
        assert active_tokens == 0

    def test_logout_without_authentication(self, api_client):
        response = api_client.post("/api/logout")
        assert response.status_code == 401

    def test_logout_with_invalid_token(self, api_client):
        api_client.defaults["HTTP_AUTHORIZATION"] = "Bearer invalid_token_here"
        response = api_client.post("/api/logout")
        assert response.status_code == 401

    def test_logout_with_expired_token(self, api_client, user):
        import jwt
        from datetime import datetime, timedelta
        from django.conf import settings

        payload = {
            "user_id": str(user.id),
            "exp": (datetime.utcnow() - timedelta(hours=1)).timestamp(),
            "iat": (datetime.utcnow() - timedelta(hours=2)).timestamp(),
            "token_type": "access",
        }

        expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {expired_token}"

        response = api_client.post("/api/logout")
        assert response.status_code == 401

    def test_logout_multiple_sessions(self, authenticated_client, user):
        from authentication.utils import create_jwt_tokens
        from authentication.db_utils import create_refresh_token

        for _ in range(3):
            tokens = create_jwt_tokens(user)
            create_refresh_token(user, tokens["jti"])

        active_count_before = Token.objects.filter(
            user=user, token_type="refresh", is_used=False
        ).count()
        assert active_count_before >= 3

        response = authenticated_client.post("/api/logout")
        assert response.status_code == 200

        active_count_after = Token.objects.filter(
            user=user, token_type="refresh", is_used=False
        ).count()
        assert active_count_after == 0

    def test_logout_malformed_authorization_header(self, api_client):
        test_cases = [
            "InvalidFormat token",
            "Bearer",
            "Bearer ",
            "token_without_bearer",
            "",
        ]

        for auth_header in test_cases:
            api_client.defaults["HTTP_AUTHORIZATION"] = auth_header
            response = api_client.post("/api/logout")
            assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.django_db
class TestAuthenticationFlow:

    def test_register_login_logout_flow(self, api_client, clear_emails):
        register_data = {
            "email": "flowtest@example.com",
            "password": "SecurePass123!",
            "first_name": "Flow",
            "last_name": "Test",
        }

        register_response = api_client.post(
            "/api/register",
            data=json.dumps(register_data),
            content_type="application/json",
        )
        assert register_response.status_code == 201

        user = User.objects.get(email=register_data["email"])
        user.is_verified = True
        user.save()

        login_data = {
            "email": register_data["email"],
            "password": register_data["password"],
        }

        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )
        assert login_response.status_code == 200
        tokens = login_response.json()

        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {tokens['access_token']}"
        logout_response = api_client.post("/api/logout")
        assert logout_response.status_code == 200

    def test_multiple_users_login_isolation(
        self, api_client, multiple_users, test_password
    ):
        tokens_list = []

        for user in multiple_users:
            data = {"email": user.email, "password": test_password}

            response = api_client.post(
                "/api/login",
                data=json.dumps(data),
                content_type="application/json",
            )

            assert response.status_code == 200
            tokens_list.append(response.json())

        access_tokens = [t["access_token"] for t in tokens_list]
        assert len(set(access_tokens)) == len(access_tokens)

    def test_login_after_failed_attempts(self, api_client, verified_user, test_password):
        for _ in range(3):
            data = {"email": verified_user.email, "password": "WrongPassword"}
            response = api_client.post(
                "/api/login",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert response.status_code == 401

        data = {"email": verified_user.email, "password": test_password}
        response = api_client.post(
            "/api/login",
            data=json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code in [200, 429]
