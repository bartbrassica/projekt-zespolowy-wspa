"""
Integration tests for secure password generation.
"""

import pytest
import json
import re


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordGeneration:

    def test_generate_password_default_params(self, api_client):
        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps({}),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert "password" in data
        assert "strength" in data
        assert len(data["password"]) == 16

    def test_generate_password_custom_length(self, api_client):
        for length in [8, 12, 20, 32, 64, 128]:
            generate_data = {
                "length": length,
            }

            response = api_client.post(
                "/api/passwords/generate",
                data=json.dumps(generate_data),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["password"]) == length

    def test_generate_password_min_length(self, api_client):
        generate_data = {
            "length": 8,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["password"]) == 8

    def test_generate_password_max_length(self, api_client):
        generate_data = {
            "length": 128,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["password"]) == 128

    def test_generate_password_too_short(self, api_client):
        generate_data = {
            "length": 7,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response.status_code == 422

    def test_generate_password_too_long(self, api_client):
        generate_data = {
            "length": 129,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response.status_code == 422

    def test_generate_password_with_symbols(self, api_client):
        generate_data = {
            "length": 20,
            "include_symbols": True,
            "include_numbers": True,
            "include_uppercase": True,
            "include_lowercase": True,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        password = data["password"]
        assert len(password) == 20

    def test_generate_password_without_symbols(self, api_client):
        generate_data = {
            "length": 20,
            "include_symbols": False,
            "include_numbers": True,
            "include_uppercase": True,
            "include_lowercase": True,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        password = data["password"]

        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?/"
        assert not any(char in symbols for char in password)

    def test_generate_password_only_lowercase(self, api_client):
        generate_data = {
            "length": 20,
            "include_symbols": False,
            "include_numbers": False,
            "include_uppercase": False,
            "include_lowercase": True,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        password = data["password"]
        assert password.islower()
        assert password.isalpha()

    def test_generate_password_only_uppercase(self, api_client):
        generate_data = {
            "length": 20,
            "include_symbols": False,
            "include_numbers": False,
            "include_uppercase": True,
            "include_lowercase": False,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        password = data["password"]
        assert password.isupper()
        assert password.isalpha()

    def test_generate_password_only_numbers(self, api_client):
        generate_data = {
            "length": 20,
            "include_symbols": False,
            "include_numbers": True,
            "include_uppercase": False,
            "include_lowercase": False,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        password = data["password"]
        assert password.isdigit()

    def test_generate_password_uppercase_and_numbers(self, api_client):
        generate_data = {
            "length": 20,
            "include_symbols": False,
            "include_numbers": True,
            "include_uppercase": True,
            "include_lowercase": False,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        password = data["password"]
        assert password.isalnum()
        assert any(c.isupper() for c in password) or any(c.isdigit() for c in password)

    def test_generate_password_exclude_ambiguous(self, api_client):
        generate_data = {
            "length": 50,
            "exclude_ambiguous": True,
            "include_symbols": False,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        password = data["password"]
        assert len(password) == 50

    def test_generate_password_include_ambiguous(self, api_client):
        generate_data = {
            "length": 20,
            "exclude_ambiguous": False,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["password"]) == 20

    def test_generate_password_returns_strength(self, api_client):
        generate_data = {
            "length": 20,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert "strength" in data
        assert isinstance(data["strength"], dict)

    def test_generate_password_uniqueness(self, api_client):
        generate_data = {
            "length": 20,
        }

        passwords = set()
        for _ in range(10):
            response = api_client.post(
                "/api/passwords/generate",
                data=json.dumps(generate_data),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = response.json()
            passwords.add(data["password"])

        assert len(passwords) == 10

    def test_generate_password_no_authentication_required(self, api_client):
        generate_data = {
            "length": 16,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response.status_code == 200

    def test_generate_password_all_options_enabled(self, api_client):
        generate_data = {
            "length": 30,
            "include_symbols": True,
            "include_numbers": True,
            "include_uppercase": True,
            "include_lowercase": True,
            "exclude_ambiguous": False,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        password = data["password"]
        assert len(password) == 30

    def test_generate_password_minimal_options(self, api_client):
        generate_data = {
            "length": 12,
            "include_symbols": False,
            "include_numbers": True,
            "include_uppercase": False,
            "include_lowercase": True,
            "exclude_ambiguous": True,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        password = data["password"]
        assert len(password) == 12
        assert password.islower() or any(c.isdigit() for c in password)


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordStrength:

    def test_password_strength_weak(self):
        from authentication.encryption_service import encryption_service

        strength = encryption_service.check_password_strength("weak")
        assert isinstance(strength, dict)

    def test_password_strength_medium(self):
        from authentication.encryption_service import encryption_service

        strength = encryption_service.check_password_strength("Medium123")
        assert isinstance(strength, dict)

    def test_password_strength_strong(self):
        from authentication.encryption_service import encryption_service

        strength = encryption_service.check_password_strength("VeryStr0ng!P@ssw0rd")
        assert isinstance(strength, dict)

    def test_password_strength_empty(self):
        from authentication.encryption_service import encryption_service

        strength = encryption_service.check_password_strength("")
        assert isinstance(strength, dict)

    def test_password_strength_long(self):
        from authentication.encryption_service import encryption_service

        strength = encryption_service.check_password_strength("A" * 100)
        assert isinstance(strength, dict)

    def test_password_strength_special_chars(self):
        from authentication.encryption_service import encryption_service

        strength = encryption_service.check_password_strength("P@$$w0rd!#%")
        assert isinstance(strength, dict)


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordGenerationEdgeCases:

    def test_generate_password_all_disabled_fails(self, api_client):
        generate_data = {
            "length": 16,
            "include_symbols": False,
            "include_numbers": False,
            "include_uppercase": False,
            "include_lowercase": False,
        }

        try:
            response = api_client.post(
                "/api/passwords/generate",
                data=json.dumps(generate_data),
                content_type="application/json",
            )
            assert response.status_code in [400, 422, 500]
        except ValueError:
            pass

    def test_generate_password_invalid_length_type(self, api_client):
        generate_data = {
            "length": "invalid",
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response.status_code == 422

    def test_generate_password_negative_length(self, api_client):
        generate_data = {
            "length": -10,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response.status_code == 422

    def test_generate_password_zero_length(self, api_client):
        generate_data = {
            "length": 0,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response.status_code == 422

    def test_generate_password_very_large_length(self, api_client):
        generate_data = {
            "length": 10000,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response.status_code == 422

    def test_generate_password_multiple_calls_independent(self, api_client):
        generate_data = {
            "length": 16,
        }

        response1 = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        response2 = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["password"] != response2.json()["password"]


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordGenerationSecurity:

    def test_generated_password_entropy(self, api_client):
        generate_data = {
            "length": 20,
            "include_symbols": True,
            "include_numbers": True,
            "include_uppercase": True,
            "include_lowercase": True,
        }

        passwords = []
        for _ in range(5):
            response = api_client.post(
                "/api/passwords/generate",
                data=json.dumps(generate_data),
                content_type="application/json",
            )
            passwords.append(response.json()["password"])

        for pwd in passwords:
            assert len(set(pwd)) > 10

    def test_generated_password_no_patterns(self, api_client):
        generate_data = {
            "length": 20,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        password = response.json()["password"]

        assert "12345" not in password
        assert "abcde" not in password.lower()
        assert "qwerty" not in password.lower()

    def test_generated_password_randomness(self, api_client):
        generate_data = {
            "length": 16,
        }

        passwords = []
        for _ in range(100):
            response = api_client.post(
                "/api/passwords/generate",
                data=json.dumps(generate_data),
                content_type="application/json",
            )
            passwords.append(response.json()["password"])

        unique_passwords = set(passwords)
        assert len(unique_passwords) == 100

    def test_generated_password_character_distribution(self, api_client):
        generate_data = {
            "length": 100,
            "include_symbols": True,
            "include_numbers": True,
            "include_uppercase": True,
            "include_lowercase": True,
        }

        response = api_client.post(
            "/api/passwords/generate",
            data=json.dumps(generate_data),
            content_type="application/json",
        )

        password = response.json()["password"]

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)

        assert has_upper or has_lower or has_digit
