"""
Integration tests for email verification endpoints.
"""

import pytest
import json
from django.core import mail

from authentication.models import Token


@pytest.mark.integration
@pytest.mark.django_db
class TestVerifyEmailPostEndpoint:

    def test_verify_email_post_success(self, api_client, unverified_user, clear_emails):
        from authentication.db_utils import create_verification_token

        verification_token = create_verification_token(unverified_user)
        verify_data = {"token": str(verification_token.token)}

        response = api_client.post(
            "/api/verify-email",
            data=json.dumps(verify_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert "verified successfully" in response.json()["message"].lower()

        unverified_user.refresh_from_db()
        assert unverified_user.is_verified is True

        verification_token.refresh_from_db()
        assert verification_token.is_used is True

        # Check welcome email was sent
        assert len(mail.outbox) == 1
        assert "welcome" in mail.outbox[0].subject.lower()

    def test_verify_email_post_invalid_token(self, api_client):
        verify_data = {"token": "00000000-0000-0000-0000-000000000000"}

        response = api_client.post(
            "/api/verify-email",
            data=json.dumps(verify_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

    def test_verify_email_post_expired_token(self, api_client, unverified_user):
        from authentication.models import Token
        from django.utils import timezone
        from datetime import timedelta

        expired_token = Token.objects.create(
            user=unverified_user,
            token_type="verification",
            expires_at=timezone.now() - timedelta(hours=1),
        )

        verify_data = {"token": str(expired_token.token)}

        response = api_client.post(
            "/api/verify-email",
            data=json.dumps(verify_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower() or "expired" in response.json()["detail"].lower()

    def test_verify_email_post_already_verified(self, api_client, verified_user, clear_emails):
        from authentication.db_utils import create_verification_token

        verification_token = create_verification_token(verified_user)
        verify_data = {"token": str(verification_token.token)}

        response = api_client.post(
            "/api/verify-email",
            data=json.dumps(verify_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert "already verified" in response.json()["message"].lower()

        # No welcome email should be sent
        assert len(mail.outbox) == 0

    def test_verify_email_post_used_token(self, api_client, unverified_user):
        from authentication.db_utils import create_verification_token, mark_token_used

        verification_token = create_verification_token(unverified_user)
        mark_token_used(verification_token)

        verify_data = {"token": str(verification_token.token)}

        response = api_client.post(
            "/api/verify-email",
            data=json.dumps(verify_data),
            content_type="application/json",
        )

        assert response.status_code == 400


@pytest.mark.integration
@pytest.mark.django_db
class TestVerifyEmailGetEndpoint:

    def test_verify_email_get_success(self, api_client, unverified_user, clear_emails):
        from authentication.db_utils import create_verification_token

        verification_token = create_verification_token(unverified_user)

        response = api_client.get(f"/api/verify-email/{str(verification_token.token)}")

        assert response.status_code == 200
        assert "verified successfully" in response.json()["message"].lower()

        unverified_user.refresh_from_db()
        assert unverified_user.is_verified is True

        verification_token.refresh_from_db()
        assert verification_token.is_used is True

        # Check welcome email was sent
        assert len(mail.outbox) == 1
        assert "welcome" in mail.outbox[0].subject.lower()

    def test_verify_email_get_invalid_token(self, api_client):
        response = api_client.get("/api/verify-email/00000000-0000-0000-0000-000000000000")

        assert response.status_code == 400

    def test_verify_email_get_expired_token(self, api_client, unverified_user):
        from authentication.models import Token
        from django.utils import timezone
        from datetime import timedelta

        expired_token = Token.objects.create(
            user=unverified_user,
            token_type="verification",
            expires_at=timezone.now() - timedelta(hours=1),
        )

        response = api_client.get(f"/api/verify-email/{str(expired_token.token)}")

        assert response.status_code == 400

    def test_verify_email_get_already_verified(self, api_client, verified_user, clear_emails):
        from authentication.db_utils import create_verification_token

        verification_token = create_verification_token(verified_user)

        response = api_client.get(f"/api/verify-email/{str(verification_token.token)}")

        assert response.status_code == 200
        assert "already verified" in response.json()["message"].lower()

        # No welcome email should be sent
        assert len(mail.outbox) == 0


@pytest.mark.integration
@pytest.mark.django_db
class TestResendVerificationEndpoint:

    def test_resend_verification_success(self, api_client, unverified_user, clear_emails):
        from authentication.utils import create_jwt_tokens

        tokens = create_jwt_tokens(unverified_user)
        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {tokens['access_token']}"

        response = api_client.post("/api/resend-verification")

        assert response.status_code == 200
        assert "verification email sent" in response.json()["message"].lower()

        # Check verification email was sent
        assert len(mail.outbox) == 1
        assert unverified_user.email in mail.outbox[0].to

        # Check token was created
        token = Token.objects.filter(
            user=unverified_user, token_type="verification", is_used=False
        ).first()
        assert token is not None

    def test_resend_verification_already_verified(self, api_client, verified_user):
        from authentication.utils import create_jwt_tokens

        tokens = create_jwt_tokens(verified_user)
        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {tokens['access_token']}"

        response = api_client.post("/api/resend-verification")

        assert response.status_code == 400
        assert "already verified" in response.json()["detail"].lower()

    def test_resend_verification_without_authentication(self, api_client):
        response = api_client.post("/api/resend-verification")

        assert response.status_code == 401

    def test_resend_verification_invalidates_old_tokens(self, api_client, unverified_user, clear_emails):
        from authentication.utils import create_jwt_tokens
        from authentication.db_utils import create_verification_token

        # Create an old verification token
        old_token = create_verification_token(unverified_user)
        old_token_value = old_token.token

        tokens = create_jwt_tokens(unverified_user)
        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {tokens['access_token']}"

        response = api_client.post("/api/resend-verification")

        assert response.status_code == 200

        # Check old token is marked as used
        old_token.refresh_from_db()
        assert old_token.is_used is True

        # Check new token exists and is different
        new_token = Token.objects.filter(
            user=unverified_user, token_type="verification", is_used=False
        ).first()
        assert new_token is not None
        assert new_token.token != old_token_value


@pytest.mark.integration
@pytest.mark.django_db
class TestVerificationStatusEndpoint:

    def test_verification_status_verified_user(self, api_client, verified_user):
        from authentication.utils import create_jwt_tokens

        tokens = create_jwt_tokens(verified_user)
        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {tokens['access_token']}"

        response = api_client.get("/api/verification-status")

        assert response.status_code == 200
        data = response.json()
        assert data["is_verified"] is True
        assert data["verification_pending"] is False
        assert data["verification_sent_at"] is None

    def test_verification_status_unverified_user(self, api_client, unverified_user):
        from authentication.utils import create_jwt_tokens
        from authentication.db_utils import create_verification_token

        verification_token = create_verification_token(unverified_user)

        tokens = create_jwt_tokens(unverified_user)
        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {tokens['access_token']}"

        response = api_client.get("/api/verification-status")

        assert response.status_code == 200
        data = response.json()
        assert data["is_verified"] is False
        assert data["verification_pending"] is True
        assert data["verification_sent_at"] is not None

    def test_verification_status_without_authentication(self, api_client):
        response = api_client.get("/api/verification-status")

        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.django_db
class TestEmailVerificationFlow:

    def test_complete_registration_and_verification_flow(self, api_client, clear_emails):
        # Register a new user
        register_data = {
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
            "first_name": "New",
            "last_name": "User",
        }

        register_response = api_client.post(
            "/api/register",
            data=json.dumps(register_data),
            content_type="application/json",
        )

        assert register_response.status_code == 201

        # Check verification email was sent
        assert len(mail.outbox) == 1
        assert "newuser@example.com" in mail.outbox[0].to

        # Get the verification token
        from authentication.models import User
        user = User.objects.get(email="newuser@example.com")
        token = Token.objects.filter(user=user, token_type="verification").first()

        # Clear emails before verification
        mail.outbox = []

        # Verify email
        verify_response = api_client.post(
            "/api/verify-email",
            data=json.dumps({"token": str(token.token)}),
            content_type="application/json",
        )

        assert verify_response.status_code == 200

        # Check welcome email was sent
        assert len(mail.outbox) == 1
        assert "welcome" in mail.outbox[0].subject.lower()

        # Try to login
        login_data = {
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
        }

        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )

        assert login_response.status_code == 200
        assert "access_token" in login_response.json()

    def test_registration_and_resend_verification_flow(self, api_client, clear_emails):
        # Register a new user
        register_data = {
            "email": "resenduser@example.com",
            "password": "StrongPassword123!",
            "first_name": "Resend",
            "last_name": "User",
        }

        api_client.post(
            "/api/register",
            data=json.dumps(register_data),
            content_type="application/json",
        )

        # Clear initial verification email
        mail.outbox = []

        # Get JWT tokens for the unverified user
        from authentication.models import User
        from authentication.utils import create_jwt_tokens

        user = User.objects.get(email="resenduser@example.com")
        tokens = create_jwt_tokens(user)

        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {tokens['access_token']}"

        # Resend verification email
        resend_response = api_client.post("/api/resend-verification")

        assert resend_response.status_code == 200
        assert len(mail.outbox) == 1
        assert "resenduser@example.com" in mail.outbox[0].to
