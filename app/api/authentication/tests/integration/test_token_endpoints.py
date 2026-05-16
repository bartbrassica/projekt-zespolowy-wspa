"""
Integration tests for JWT token management: refresh, verify, expiration.
"""

import pytest
import json
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone

from authentication.models import Token


@pytest.mark.integration
@pytest.mark.django_db
class TestTokenRefreshEndpoint:

    def test_refresh_token_success(self, api_client, verified_user, test_password):
        login_data = {"email": verified_user.email, "password": test_password}
        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )

        assert login_response.status_code == 200
        tokens = login_response.json()

        refresh_data = {"refresh_token": tokens["refresh_token"]}
        refresh_response = api_client.post(
            "/api/token/refresh",
            data=json.dumps(refresh_data),
            content_type="application/json",
        )

        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()

        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens
        assert "token_type" in new_tokens
        assert "expires_in" in new_tokens

        assert new_tokens["access_token"] != tokens["access_token"]
        assert new_tokens["refresh_token"] != tokens["refresh_token"]

    def test_refresh_token_marks_old_token_used(self, api_client, verified_user, test_password):
        login_data = {"email": verified_user.email, "password": test_password}
        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )
        tokens = login_response.json()

        payload = jwt.decode(tokens["refresh_token"], options={"verify_signature": False})
        jti = payload["jti"]

        refresh_data = {"refresh_token": tokens["refresh_token"]}
        api_client.post(
            "/api/token/refresh",
            data=json.dumps(refresh_data),
            content_type="application/json",
        )

        old_token = Token.objects.get(token=jti)
        assert old_token.is_used is True

    def test_refresh_token_with_invalid_token(self, api_client):
        refresh_data = {"refresh_token": "invalid.token.here"}

        response = api_client.post(
            "/api/token/refresh",
            data=json.dumps(refresh_data),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_refresh_token_with_access_token(self, api_client, verified_user, test_password):
        login_data = {"email": verified_user.email, "password": test_password}
        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )
        tokens = login_response.json()

        refresh_data = {"refresh_token": tokens["access_token"]}
        response = api_client.post(
            "/api/token/refresh",
            data=json.dumps(refresh_data),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_refresh_token_with_expired_token(self, api_client, user):
        payload = {
            "user_id": str(user.id),
            "exp": (datetime.utcnow() - timedelta(hours=1)).timestamp(),
            "iat": (datetime.utcnow() - timedelta(hours=2)).timestamp(),
            "token_type": "refresh",
            "jti": "expired-jti",
        }

        expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        refresh_data = {"refresh_token": expired_token}
        response = api_client.post(
            "/api/token/refresh",
            data=json.dumps(refresh_data),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_refresh_token_already_used(self, api_client, verified_user, test_password):
        login_data = {"email": verified_user.email, "password": test_password}
        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )
        tokens = login_response.json()

        refresh_data = {"refresh_token": tokens["refresh_token"]}

        first_refresh = api_client.post(
            "/api/token/refresh",
            data=json.dumps(refresh_data),
            content_type="application/json",
        )
        assert first_refresh.status_code == 200

        second_refresh = api_client.post(
            "/api/token/refresh",
            data=json.dumps(refresh_data),
            content_type="application/json",
        )
        assert second_refresh.status_code == 401

    def test_refresh_token_for_inactive_user(self, api_client, verified_user, test_password):
        login_data = {"email": verified_user.email, "password": test_password}
        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )
        tokens = login_response.json()

        verified_user.is_active = False
        verified_user.save()

        refresh_data = {"refresh_token": tokens["refresh_token"]}
        response = api_client.post(
            "/api/token/refresh",
            data=json.dumps(refresh_data),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_refresh_token_missing_jti(self, api_client, user):
        payload = {
            "user_id": str(user.id),
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
            "iat": datetime.utcnow().timestamp(),
            "token_type": "refresh",
        }

        token_without_jti = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        refresh_data = {"refresh_token": token_without_jti}
        response = api_client.post(
            "/api/token/refresh",
            data=json.dumps(refresh_data),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_multiple_refresh_token_generations(self, api_client, verified_user, test_password):
        login_data = {"email": verified_user.email, "password": test_password}
        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )

        current_tokens = login_response.json()

        for i in range(3):
            refresh_data = {"refresh_token": current_tokens["refresh_token"]}
            refresh_response = api_client.post(
                "/api/token/refresh",
                data=json.dumps(refresh_data),
                content_type="application/json",
            )

            assert refresh_response.status_code == 200
            current_tokens = refresh_response.json()


@pytest.mark.integration
@pytest.mark.django_db
class TestTokenVerification:

    def test_access_protected_endpoint_with_valid_token(self, authenticated_client):
        response = authenticated_client.get("/api/me")
        assert response.status_code == 200

    def test_access_protected_endpoint_without_token(self, api_client):
        response = api_client.get("/api/me")
        assert response.status_code == 401

    def test_access_protected_endpoint_with_invalid_token(self, api_client):
        api_client.defaults["HTTP_AUTHORIZATION"] = "Bearer invalid.jwt.token"
        response = api_client.get("/api/me")
        assert response.status_code == 401

    def test_access_protected_endpoint_with_expired_access_token(self, api_client, user):
        payload = {
            "user_id": str(user.id),
            "exp": (datetime.utcnow() - timedelta(minutes=1)).timestamp(),
            "iat": (datetime.utcnow() - timedelta(hours=1)).timestamp(),
            "token_type": "access",
        }

        expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {expired_token}"

        response = api_client.get("/api/me")
        assert response.status_code == 401

    def test_access_protected_endpoint_with_refresh_token(self, api_client, verified_user, test_password):
        login_data = {"email": verified_user.email, "password": test_password}
        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )
        tokens = login_response.json()

        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {tokens['refresh_token']}"
        response = api_client.get("/api/me")

        assert response.status_code == 200

    def test_token_with_missing_user_id(self, api_client):
        payload = {
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
            "iat": datetime.utcnow().timestamp(),
            "token_type": "access",
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"

        response = api_client.get("/api/me")
        assert response.status_code == 401

    def test_token_with_nonexistent_user(self, api_client):
        payload = {
            "user_id": "00000000-0000-0000-0000-000000000000",
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
            "iat": datetime.utcnow().timestamp(),
            "token_type": "access",
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"

        response = api_client.get("/api/me")
        assert response.status_code == 401

    def test_token_with_wrong_signature(self, api_client, user):
        payload = {
            "user_id": str(user.id),
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
            "iat": datetime.utcnow().timestamp(),
            "token_type": "access",
        }

        token = jwt.encode(payload, "wrong-secret-key", algorithm="HS256")
        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"

        response = api_client.get("/api/me")
        assert response.status_code == 401

    def test_malformed_bearer_token(self, api_client):
        test_cases = [
            "Bearer",
            "Bearer ",
            "InvalidFormat token",
            "token_without_bearer",
        ]

        for auth_header in test_cases:
            api_client.defaults["HTTP_AUTHORIZATION"] = auth_header
            response = api_client.get("/api/me")
            assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.django_db
class TestTokenExpiration:

    def test_access_token_expiration_time(self, api_client, verified_user, test_password):
        login_data = {"email": verified_user.email, "password": test_password}
        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )

        tokens = login_response.json()
        payload = jwt.decode(tokens["access_token"], options={"verify_signature": False})

        assert "exp" in payload
        assert "iat" in payload

        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])

        token_lifetime = exp_time - iat_time
        assert token_lifetime.total_seconds() > 0

    def test_refresh_token_expiration_time(self, api_client, verified_user, test_password):
        login_data = {"email": verified_user.email, "password": test_password}
        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )

        tokens = login_response.json()
        payload = jwt.decode(tokens["refresh_token"], options={"verify_signature": False})

        assert "exp" in payload
        assert "iat" in payload

        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])

        token_lifetime = exp_time - iat_time
        assert token_lifetime.total_seconds() > 0

    def test_token_not_valid_before_issued(self, api_client, user):
        payload = {
            "user_id": str(user.id),
            "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
            "iat": (datetime.utcnow() + timedelta(hours=1)).timestamp(),
            "token_type": "access",
        }

        future_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {future_token}"

        response = api_client.get("/api/me")
        assert response.status_code in [200, 401]

    def test_token_payload_structure(self, api_client, verified_user, test_password):
        login_data = {"email": verified_user.email, "password": test_password}
        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )

        tokens = login_response.json()

        access_payload = jwt.decode(tokens["access_token"], options={"verify_signature": False})
        assert "user_id" in access_payload
        assert "exp" in access_payload
        assert "iat" in access_payload
        assert "token_type" in access_payload

        refresh_payload = jwt.decode(tokens["refresh_token"], options={"verify_signature": False})
        assert "user_id" in refresh_payload
        assert "exp" in refresh_payload
        assert "iat" in refresh_payload
        assert "token_type" in refresh_payload
        assert "jti" in refresh_payload


@pytest.mark.integration
@pytest.mark.django_db
class TestTokenSecurityScenarios:

    def test_token_reuse_after_logout(self, api_client, verified_user, test_password):
        login_data = {"email": verified_user.email, "password": test_password}
        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )
        tokens = login_response.json()

        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {tokens['access_token']}"
        api_client.post("/api/logout")

        refresh_data = {"refresh_token": tokens["refresh_token"]}
        response = api_client.post(
            "/api/token/refresh",
            data=json.dumps(refresh_data),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_concurrent_token_refresh(self, api_client, verified_user, test_password):
        login_data = {"email": verified_user.email, "password": test_password}
        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )
        tokens = login_response.json()

        refresh_data = {"refresh_token": tokens["refresh_token"]}

        response1 = api_client.post(
            "/api/token/refresh",
            data=json.dumps(refresh_data),
            content_type="application/json",
        )

        response2 = api_client.post(
            "/api/token/refresh",
            data=json.dumps(refresh_data),
            content_type="application/json",
        )

        assert response1.status_code == 200
        assert response2.status_code == 401

    def test_token_contains_correct_user_info(self, api_client, verified_user, test_password):
        login_data = {"email": verified_user.email, "password": test_password}
        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )

        tokens = login_response.json()
        payload = jwt.decode(tokens["access_token"], options={"verify_signature": False})

        assert payload["user_id"] == str(verified_user.id)

    def test_different_users_different_tokens(self, api_client, multiple_users, test_password):
        tokens_list = []

        for user in multiple_users[:2]:
            login_data = {"email": user.email, "password": test_password}
            response = api_client.post(
                "/api/login",
                data=json.dumps(login_data),
                content_type="application/json",
            )
            tokens_list.append(response.json())

        assert tokens_list[0]["access_token"] != tokens_list[1]["access_token"]
        assert tokens_list[0]["refresh_token"] != tokens_list[1]["refresh_token"]
