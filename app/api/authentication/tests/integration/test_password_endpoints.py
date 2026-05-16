"""
Integration tests for password change and reset endpoints.
"""

import pytest
import json
from django.core import mail

from authentication.models import Token


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordChangeEndpoint:

    def test_change_password_success(self, authenticated_client, user, test_password):
        change_data = {
            "current_password": test_password,
            "new_password": "NewSecurePass123!",
            "confirm_password": "NewSecurePass123!",
        }

        response = authenticated_client.post(
            "/api/password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert "changed successfully" in response.json()["message"].lower()

        user.refresh_from_db()
        assert user.check_password("NewSecurePass123!")
        assert not user.check_password(test_password)

    def test_change_password_invalidates_refresh_tokens(self, authenticated_client, user, test_password):
        from authentication.utils import create_jwt_tokens
        from authentication.db_utils import create_refresh_token

        tokens = create_jwt_tokens(user)
        create_refresh_token(user, tokens["jti"])

        change_data = {
            "current_password": test_password,
            "new_password": "NewSecurePass123!",
            "confirm_password": "NewSecurePass123!",
        }

        authenticated_client.post(
            "/api/password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        active_tokens = Token.objects.filter(
            user=user, token_type="refresh", is_used=False
        ).count()
        assert active_tokens == 0

    def test_change_password_wrong_current_password(self, authenticated_client, user):
        change_data = {
            "current_password": "WrongPassword123!",
            "new_password": "NewSecurePass123!",
            "confirm_password": "NewSecurePass123!",
        }

        response = authenticated_client.post(
            "/api/password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "incorrect" in response.json()["detail"].lower()

    def test_change_password_without_authentication(self, api_client):
        change_data = {
            "current_password": "OldPass123!",
            "new_password": "NewSecurePass123!",
            "confirm_password": "NewSecurePass123!",
        }

        response = api_client.post(
            "/api/password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_change_password_weak_new_password(self, authenticated_client, user, test_password):
        change_data = {
            "current_password": test_password,
            "new_password": "weak",
            "confirm_password": "weak",
        }

        response = authenticated_client.post(
            "/api/password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code in [400, 422]

    def test_change_password_mismatched_confirmation(self, authenticated_client, user, test_password):
        change_data = {
            "current_password": test_password,
            "new_password": "NewSecurePass123!",
            "confirm_password": "DifferentPass123!",
        }

        response = authenticated_client.post(
            "/api/password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code in [400, 422]

    def test_change_password_same_as_current(self, authenticated_client, user, test_password):
        change_data = {
            "current_password": test_password,
            "new_password": test_password,
            "confirm_password": test_password,
        }

        response = authenticated_client.post(
            "/api/password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code in [200, 400]

    def test_login_with_new_password(self, api_client, verified_user, test_password):
        from authentication.utils import create_jwt_tokens

        tokens = create_jwt_tokens(verified_user)
        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {tokens['access_token']}"

        change_data = {
            "current_password": test_password,
            "new_password": "BrandNewPass123!",
            "confirm_password": "BrandNewPass123!",
        }

        api_client.post(
            "/api/password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        login_data = {"email": verified_user.email, "password": "BrandNewPass123!"}
        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )

        assert login_response.status_code == 200

    def test_old_password_no_longer_works(self, api_client, verified_user, test_password):
        from authentication.utils import create_jwt_tokens

        tokens = create_jwt_tokens(verified_user)
        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {tokens['access_token']}"

        change_data = {
            "current_password": test_password,
            "new_password": "BrandNewPass123!",
            "confirm_password": "BrandNewPass123!",
        }

        api_client.post(
            "/api/password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        login_data = {"email": verified_user.email, "password": test_password}
        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )

        assert login_response.status_code == 401


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordResetRequestEndpoint:

    def test_request_password_reset_success(self, api_client, verified_user, clear_emails):
        reset_data = {"email": verified_user.email}

        response = api_client.post(
            "/api/password/reset/request",
            data=json.dumps(reset_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert "email" in response.json()["message"].lower()

        assert len(mail.outbox) == 1
        assert verified_user.email in mail.outbox[0].to

        token = Token.objects.filter(
            user=verified_user, token_type="password_reset"
        ).first()
        assert token is not None
        assert token.is_used is False

    def test_request_password_reset_nonexistent_email(self, api_client, clear_emails):
        reset_data = {"email": "nonexistent@example.com"}

        response = api_client.post(
            "/api/password/reset/request",
            data=json.dumps(reset_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert len(mail.outbox) == 0

    def test_request_password_reset_inactive_user(self, api_client, inactive_user, clear_emails):
        reset_data = {"email": inactive_user.email}

        response = api_client.post(
            "/api/password/reset/request",
            data=json.dumps(reset_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert len(mail.outbox) == 0

    def test_request_password_reset_invalid_email_format(self, api_client):
        reset_data = {"email": "invalid-email"}

        response = api_client.post(
            "/api/password/reset/request",
            data=json.dumps(reset_data),
            content_type="application/json",
        )

        assert response.status_code == 422

    def test_multiple_password_reset_requests(self, api_client, verified_user, clear_emails):
        reset_data = {"email": verified_user.email}

        for _ in range(3):
            response = api_client.post(
                "/api/password/reset/request",
                data=json.dumps(reset_data),
                content_type="application/json",
            )
            assert response.status_code == 200

        assert len(mail.outbox) == 3


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordResetConfirmEndpoint:

    def test_confirm_password_reset_success(self, api_client, verified_user, password_reset_token):
        confirm_data = {
            "token": str(password_reset_token.token),
            "new_password": "ResetPassword123!",
            "confirm_password": "ResetPassword123!",
        }

        response = api_client.post(
            "/api/password/reset/confirm",
            data=json.dumps(confirm_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert "reset successfully" in response.json()["message"].lower()

        verified_user.refresh_from_db()
        assert verified_user.check_password("ResetPassword123!")

    def test_confirm_password_reset_marks_token_used(self, api_client, verified_user, password_reset_token):
        confirm_data = {
            "token": str(password_reset_token.token),
            "new_password": "ResetPassword123!",
            "confirm_password": "ResetPassword123!",
        }

        api_client.post(
            "/api/password/reset/confirm",
            data=json.dumps(confirm_data),
            content_type="application/json",
        )

        password_reset_token.refresh_from_db()
        assert password_reset_token.is_used is True

    def test_confirm_password_reset_invalid_token(self, api_client):
        confirm_data = {
            "token": "00000000-0000-0000-0000-000000000000",
            "new_password": "ResetPassword123!",
            "confirm_password": "ResetPassword123!",
        }

        response = api_client.post(
            "/api/password/reset/confirm",
            data=json.dumps(confirm_data),
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_confirm_password_reset_expired_token(self, api_client, expired_token):
        confirm_data = {
            "token": str(expired_token.token),
            "new_password": "ResetPassword123!",
            "confirm_password": "ResetPassword123!",
        }

        response = api_client.post(
            "/api/password/reset/confirm",
            data=json.dumps(confirm_data),
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_confirm_password_reset_used_token(self, api_client, verified_user, password_reset_token):
        confirm_data = {
            "token": str(password_reset_token.token),
            "new_password": "ResetPassword123!",
            "confirm_password": "ResetPassword123!",
        }

        api_client.post(
            "/api/password/reset/confirm",
            data=json.dumps(confirm_data),
            content_type="application/json",
        )

        response = api_client.post(
            "/api/password/reset/confirm",
            data=json.dumps(confirm_data),
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_confirm_password_reset_mismatched_passwords(self, api_client, password_reset_token):
        confirm_data = {
            "token": str(password_reset_token.token),
            "new_password": "ResetPassword123!",
            "confirm_password": "DifferentPassword123!",
        }

        response = api_client.post(
            "/api/password/reset/confirm",
            data=json.dumps(confirm_data),
            content_type="application/json",
        )

        assert response.status_code in [400, 422]

    def test_confirm_password_reset_weak_password(self, api_client, password_reset_token):
        confirm_data = {
            "token": str(password_reset_token.token),
            "new_password": "weak",
            "confirm_password": "weak",
        }

        response = api_client.post(
            "/api/password/reset/confirm",
            data=json.dumps(confirm_data),
            content_type="application/json",
        )

        assert response.status_code in [400, 422]

    def test_confirm_password_reset_invalidates_refresh_tokens(self, api_client, verified_user, password_reset_token):
        from authentication.utils import create_jwt_tokens
        from authentication.db_utils import create_refresh_token

        tokens = create_jwt_tokens(verified_user)
        create_refresh_token(verified_user, tokens["jti"])

        confirm_data = {
            "token": str(password_reset_token.token),
            "new_password": "ResetPassword123!",
            "confirm_password": "ResetPassword123!",
        }

        api_client.post(
            "/api/password/reset/confirm",
            data=json.dumps(confirm_data),
            content_type="application/json",
        )

        active_tokens = Token.objects.filter(
            user=verified_user, token_type="refresh", is_used=False
        ).count()
        assert active_tokens == 0


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordResetFlow:

    def test_complete_password_reset_flow(self, api_client, verified_user, clear_emails):
        reset_data = {"email": verified_user.email}
        api_client.post(
            "/api/password/reset/request",
            data=json.dumps(reset_data),
            content_type="application/json",
        )

        token = Token.objects.filter(
            user=verified_user, token_type="password_reset"
        ).first()

        confirm_data = {
            "token": str(token.token),
            "new_password": "CompletelyNewPass123!",
            "confirm_password": "CompletelyNewPass123!",
        }

        confirm_response = api_client.post(
            "/api/password/reset/confirm",
            data=json.dumps(confirm_data),
            content_type="application/json",
        )

        assert confirm_response.status_code == 200

        login_data = {"email": verified_user.email, "password": "CompletelyNewPass123!"}
        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )

        assert login_response.status_code == 200

    def test_password_reset_flow_with_unverified_user(self, api_client, unverified_user, clear_emails):
        reset_data = {"email": unverified_user.email}
        api_client.post(
            "/api/password/reset/request",
            data=json.dumps(reset_data),
            content_type="application/json",
        )

        token = Token.objects.filter(
            user=unverified_user, token_type="password_reset"
        ).first()

        if token:
            confirm_data = {
                "token": str(token.token),
                "new_password": "NewPassword123!",
                "confirm_password": "NewPassword123!",
            }

            api_client.post(
                "/api/password/reset/confirm",
                data=json.dumps(confirm_data),
                content_type="application/json",
            )

            unverified_user.refresh_from_db()
            assert unverified_user.check_password("NewPassword123!")
