"""
Integration tests for user profile endpoints: GET /me, PUT /me.
"""

import pytest
import json

from authentication.models import User


@pytest.mark.integration
@pytest.mark.django_db
class TestGetUserProfileEndpoint:

    def test_get_current_user_success(self, authenticated_client, user):
        response = authenticated_client.get("/api/me")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(user.id)
        assert data["email"] == user.email
        assert data["first_name"] == user.first_name
        assert data["last_name"] == user.last_name
        assert data["is_verified"] == user.is_verified
        assert "date_joined" in data
        assert "password" not in data

    def test_get_current_user_without_authentication(self, api_client):
        response = api_client.get("/api/me")
        assert response.status_code == 401

    def test_get_current_user_with_invalid_token(self, api_client):
        api_client.defaults["HTTP_AUTHORIZATION"] = "Bearer invalid.token"
        response = api_client.get("/api/me")
        assert response.status_code == 401

    def test_get_current_user_returns_correct_user(self, api_client, multiple_users, test_password):
        for user in multiple_users[:2]:
            login_data = {"email": user.email, "password": test_password}
            login_response = api_client.post(
                "/api/login",
                data=json.dumps(login_data),
                content_type="application/json",
            )
            tokens = login_response.json()

            api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {tokens['access_token']}"
            me_response = api_client.get("/api/me")

            assert me_response.status_code == 200
            assert me_response.json()["email"] == user.email

    def test_get_user_profile_fields(self, authenticated_client, user):
        response = authenticated_client.get("/api/me")

        assert response.status_code == 200
        data = response.json()

        required_fields = ["id", "email", "first_name", "last_name", "is_verified", "date_joined"]
        for field in required_fields:
            assert field in data

        sensitive_fields = ["password", "hashed_password"]
        for field in sensitive_fields:
            assert field not in data


@pytest.mark.integration
@pytest.mark.django_db
class TestUpdateUserProfileEndpoint:

    def test_update_user_first_name(self, authenticated_client, user):
        update_data = {"first_name": "UpdatedFirst"}

        response = authenticated_client.put(
            "/api/me",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "UpdatedFirst"

        user.refresh_from_db()
        assert user.first_name == "UpdatedFirst"

    def test_update_user_last_name(self, authenticated_client, user):
        update_data = {"last_name": "UpdatedLast"}

        response = authenticated_client.put(
            "/api/me",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["last_name"] == "UpdatedLast"

        user.refresh_from_db()
        assert user.last_name == "UpdatedLast"

    def test_update_multiple_fields(self, authenticated_client, user):
        update_data = {
            "first_name": "NewFirst",
            "last_name": "NewLast",
        }

        response = authenticated_client.put(
            "/api/me",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "NewFirst"
        assert data["last_name"] == "NewLast"

        user.refresh_from_db()
        assert user.first_name == "NewFirst"
        assert user.last_name == "NewLast"

    def test_update_user_phone_number(self, authenticated_client, user):
        update_data = {"phone_number": "+1234567890"}

        response = authenticated_client.put(
            "/api/me",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.phone_number == "+1234567890"

    def test_update_user_without_authentication(self, api_client):
        update_data = {"first_name": "Hacker"}

        response = api_client.put(
            "/api/me",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_update_user_with_invalid_token(self, api_client):
        api_client.defaults["HTTP_AUTHORIZATION"] = "Bearer invalid.token"
        update_data = {"first_name": "Hacker"}

        response = api_client.put(
            "/api/me",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_update_email_not_allowed(self, authenticated_client, user):
        original_email = user.email
        update_data = {"email": "newemail@example.com"}

        response = authenticated_client.put(
            "/api/me",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        user.refresh_from_db()
        assert user.email == original_email

    def test_update_password_not_allowed_via_profile(self, authenticated_client, user):
        update_data = {"password": "NewPassword123!"}

        response = authenticated_client.put(
            "/api/me",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        user.refresh_from_db()
        assert not user.check_password("NewPassword123!")

    def test_update_with_empty_string(self, authenticated_client, user):
        original_first_name = user.first_name
        update_data = {"first_name": ""}

        response = authenticated_client.put(
            "/api/me",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code in [200, 400, 422]

        user.refresh_from_db()
        if response.status_code == 200:
            assert user.first_name == ""
        else:
            assert user.first_name == original_first_name

    def test_update_with_empty_phone_number(self, authenticated_client, user):
        user.phone_number = "+1234567890"
        user.save()

        update_data = {"phone_number": ""}

        response = authenticated_client.put(
            "/api/me",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code in [200, 400]
        if response.status_code == 200:
            user.refresh_from_db()
            assert user.phone_number == ""

    def test_update_user_only_affects_authenticated_user(self, api_client, multiple_users, test_password):
        user1, user2 = multiple_users[0], multiple_users[1]

        login_data = {"email": user1.email, "password": test_password}
        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )
        tokens = login_response.json()

        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {tokens['access_token']}"
        update_data = {"first_name": "User1Updated"}

        response = api_client.put(
            "/api/me",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200

        user1.refresh_from_db()
        user2.refresh_from_db()

        assert user1.first_name == "User1Updated"
        assert user2.first_name != "User1Updated"

    def test_update_with_valid_max_length_name(self, authenticated_client, user):
        max_name = "A" * 30
        update_data = {"first_name": max_name}

        response = authenticated_client.put(
            "/api/me",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.first_name == max_name

    def test_update_returns_full_user_object(self, authenticated_client, user):
        update_data = {"first_name": "Updated"}

        response = authenticated_client.put(
            "/api/me",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert "email" in data
        assert "first_name" in data
        assert "last_name" in data
        assert "is_verified" in data
        assert data["first_name"] == "Updated"

    def test_update_with_no_changes(self, authenticated_client, user):
        response = authenticated_client.put(
            "/api/me",
            data=json.dumps({}),
            content_type="application/json",
        )

        assert response.status_code == 200

    def test_partial_update_preserves_other_fields(self, authenticated_client, user):
        original_last_name = user.last_name
        update_data = {"first_name": "OnlyFirstChanged"}

        response = authenticated_client.put(
            "/api/me",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200

        user.refresh_from_db()
        assert user.first_name == "OnlyFirstChanged"
        assert user.last_name == original_last_name

    def test_update_username_if_supported(self, authenticated_client, user):
        update_data = {"username": "newusername"}

        response = authenticated_client.put(
            "/api/me",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code in [200, 400, 422]

        if response.status_code == 200:
            user.refresh_from_db()
            if hasattr(user, 'username'):
                assert user.username == "newusername"


@pytest.mark.integration
@pytest.mark.django_db
class TestUserProfileIntegration:

    def test_get_after_update(self, authenticated_client, user):
        update_data = {"first_name": "Changed"}

        authenticated_client.put(
            "/api/me",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        get_response = authenticated_client.get("/api/me")

        assert get_response.status_code == 200
        assert get_response.json()["first_name"] == "Changed"

    def test_multiple_updates_sequential(self, authenticated_client, user):
        updates = [
            {"first_name": "First"},
            {"last_name": "Second"},
            {"first_name": "Third", "last_name": "Fourth"},
        ]

        for update_data in updates:
            response = authenticated_client.put(
                "/api/me",
                data=json.dumps(update_data),
                content_type="application/json",
            )
            assert response.status_code == 200

        user.refresh_from_db()
        assert user.first_name == "Third"
        assert user.last_name == "Fourth"

    def test_update_after_token_refresh(self, api_client, verified_user, test_password):
        login_data = {"email": verified_user.email, "password": test_password}
        login_response = api_client.post(
            "/api/login",
            data=json.dumps(login_data),
            content_type="application/json",
        )
        tokens = login_response.json()

        refresh_data = {"refresh_token": tokens["refresh_token"]}
        refresh_response = api_client.post(
            "/api/token/refresh",
            data=json.dumps(refresh_data),
            content_type="application/json",
        )

        new_tokens = refresh_response.json()
        api_client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {new_tokens['access_token']}"

        update_data = {"first_name": "AfterRefresh"}
        update_response = api_client.put(
            "/api/me",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert update_response.status_code == 200
        assert update_response.json()["first_name"] == "AfterRefresh"
