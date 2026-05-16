"""
Integration tests for password decryption and master password verification.
"""

import pytest
import json


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordDecrypt:

    def test_decrypt_password_success(self, authenticated_client, password_entry, test_password):
        decrypt_data = {
            "master_password": test_password,
        }

        response = authenticated_client.post(
            f"/api/passwords/entries/{password_entry.id}/decrypt",
            data=json.dumps(decrypt_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert "password" in data
        assert "strength" in data
        assert data["password"] == "test-password-123"

    def test_decrypt_password_returns_strength(self, authenticated_client, password_entry, test_password):
        decrypt_data = {
            "master_password": test_password,
        }

        response = authenticated_client.post(
            f"/api/passwords/entries/{password_entry.id}/decrypt",
            data=json.dumps(decrypt_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert "strength" in data
        assert isinstance(data["strength"], dict)

    def test_decrypt_password_wrong_master_password(self, authenticated_client, password_entry):
        decrypt_data = {
            "master_password": "WrongPassword123!",
        }

        response = authenticated_client.post(
            f"/api/passwords/entries/{password_entry.id}/decrypt",
            data=json.dumps(decrypt_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "master password" in response.json()["detail"].lower()

    def test_decrypt_password_not_found(self, authenticated_client, test_password):
        decrypt_data = {
            "master_password": test_password,
        }

        response = authenticated_client.post(
            "/api/passwords/entries/00000000-0000-0000-0000-000000000000/decrypt",
            data=json.dumps(decrypt_data),
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_decrypt_password_other_user(self, authenticated_client, multiple_users, test_password):
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        encrypted_password, salt = encryption_service.encrypt_password(
            "other-password", test_password
        )
        other_entry = PasswordEntry.objects.create(
            user=multiple_users[0],
            name="Other User Entry",
            encrypted_password=encrypted_password,
            encryption_salt=salt,
        )

        decrypt_data = {
            "master_password": test_password,
        }

        response = authenticated_client.post(
            f"/api/passwords/entries/{other_entry.id}/decrypt",
            data=json.dumps(decrypt_data),
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_decrypt_password_without_authentication(self, api_client, password_entry, test_password):
        decrypt_data = {
            "master_password": test_password,
        }

        response = api_client.post(
            f"/api/passwords/entries/{password_entry.id}/decrypt",
            data=json.dumps(decrypt_data),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_decrypt_password_logs_access(self, authenticated_client, password_entry, user, test_password):
        from authentication.models import PasswordAccessLog

        decrypt_data = {
            "master_password": test_password,
        }

        response = authenticated_client.post(
            f"/api/passwords/entries/{password_entry.id}/decrypt",
            data=json.dumps(decrypt_data),
            content_type="application/json",
        )

        assert response.status_code == 200

        log = PasswordAccessLog.objects.filter(
            password_entry=password_entry,
            action="copy",
            user=user,
        ).first()
        assert log is not None

    def test_decrypt_password_invalid_uuid(self, authenticated_client, test_password):
        from django.core.exceptions import ValidationError

        decrypt_data = {
            "master_password": test_password,
        }

        try:
            response = authenticated_client.post(
                "/api/passwords/entries/invalid-uuid/decrypt",
                data=json.dumps(decrypt_data),
                content_type="application/json",
            )
            assert response.status_code in [400, 404, 422]
        except ValidationError:
            pass

    def test_decrypt_password_missing_master_password(self, authenticated_client, password_entry):
        decrypt_data = {}

        response = authenticated_client.post(
            f"/api/passwords/entries/{password_entry.id}/decrypt",
            data=json.dumps(decrypt_data),
            content_type="application/json",
        )

        assert response.status_code == 422

    def test_decrypt_password_multiple_times(self, authenticated_client, password_entry, test_password):
        decrypt_data = {
            "master_password": test_password,
        }

        for _ in range(3):
            response = authenticated_client.post(
                f"/api/passwords/entries/{password_entry.id}/decrypt",
                data=json.dumps(decrypt_data),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = response.json()
            assert data["password"] == "test-password-123"


@pytest.mark.integration
@pytest.mark.django_db
class TestMasterPasswordVerification:

    def test_verify_master_password_correct(self, user, test_password):
        from authentication.utils import verify_master_password

        result = verify_master_password(user, test_password)
        assert result is True

    def test_verify_master_password_incorrect(self, user):
        from authentication.utils import verify_master_password

        result = verify_master_password(user, "WrongPassword123!")
        assert result is False

    def test_verify_master_password_empty(self, user):
        from authentication.utils import verify_master_password

        result = verify_master_password(user, "")
        assert result is False

    def test_verify_master_password_none(self, user):
        from authentication.utils import verify_master_password

        result = verify_master_password(user, None)
        assert result is False

    def test_verify_master_password_case_sensitive(self, user, test_password):
        from authentication.utils import verify_master_password

        wrong_case = test_password.swapcase()
        if wrong_case != test_password:
            result = verify_master_password(user, wrong_case)
            assert result is False

    def test_verify_master_password_similar_but_different(self, user, test_password):
        from authentication.utils import verify_master_password

        result = verify_master_password(user, test_password + "extra")
        assert result is False

        result = verify_master_password(user, test_password[:-1])
        assert result is False


@pytest.mark.integration
@pytest.mark.django_db
class TestEncryptionDecryption:

    def test_encrypt_decrypt_roundtrip(self, test_password):
        from authentication.encryption_service import encryption_service

        original_password = "MySecretPassword123!"
        encrypted, salt = encryption_service.encrypt_password(original_password, test_password)

        assert encrypted != original_password
        assert salt is not None
        assert isinstance(salt, bytes)

        decrypted = encryption_service.decrypt_password(encrypted, test_password, salt)
        assert decrypted == original_password

    def test_encrypt_same_password_different_salts(self, test_password):
        from authentication.encryption_service import encryption_service

        password = "SamePassword123!"
        encrypted1, salt1 = encryption_service.encrypt_password(password, test_password)
        encrypted2, salt2 = encryption_service.encrypt_password(password, test_password)

        assert salt1 != salt2
        assert encrypted1 != encrypted2

    def test_decrypt_with_wrong_master_password(self, test_password):
        from authentication.encryption_service import encryption_service

        original_password = "MySecretPassword123!"
        encrypted, salt = encryption_service.encrypt_password(original_password, test_password)

        decrypted = encryption_service.decrypt_password(encrypted, "WrongPassword123!", salt)
        assert decrypted is None or decrypted != original_password

    def test_decrypt_with_wrong_salt(self, test_password):
        from authentication.encryption_service import encryption_service

        original_password = "MySecretPassword123!"
        encrypted, salt = encryption_service.encrypt_password(original_password, test_password)

        wrong_salt = b"wrong_salt_value_here_1234567890123456"
        decrypted = encryption_service.decrypt_password(encrypted, test_password, wrong_salt)
        assert decrypted is None or decrypted != original_password

    def test_encrypt_special_characters(self, test_password):
        from authentication.encryption_service import encryption_service

        special_password = "P@$$w0rd!#%&*()[]{}|\\:;\"'<>,.?/~`"
        encrypted, salt = encryption_service.encrypt_password(special_password, test_password)
        decrypted = encryption_service.decrypt_password(encrypted, test_password, salt)

        assert decrypted == special_password

    def test_encrypt_unicode_characters(self, test_password):
        from authentication.encryption_service import encryption_service

        unicode_password = "密码🔒Пароль"
        encrypted, salt = encryption_service.encrypt_password(unicode_password, test_password)
        decrypted = encryption_service.decrypt_password(encrypted, test_password, salt)

        assert decrypted == unicode_password

    def test_encrypt_long_password(self, test_password):
        from authentication.encryption_service import encryption_service

        long_password = "A" * 1000
        encrypted, salt = encryption_service.encrypt_password(long_password, test_password)
        decrypted = encryption_service.decrypt_password(encrypted, test_password, salt)

        assert decrypted == long_password

    def test_encrypt_empty_password(self, test_password):
        from authentication.encryption_service import encryption_service

        empty_password = ""
        encrypted, salt = encryption_service.encrypt_password(empty_password, test_password)
        decrypted = encryption_service.decrypt_password(encrypted, test_password, salt)

        assert decrypted == empty_password

    def test_password_strength_weak(self):
        from authentication.encryption_service import encryption_service

        strength = encryption_service.check_password_strength("weak")
        assert isinstance(strength, dict)

    def test_password_strength_strong(self):
        from authentication.encryption_service import encryption_service

        strength = encryption_service.check_password_strength("VeryStr0ng!P@ssw0rd123")
        assert isinstance(strength, dict)


@pytest.mark.integration
@pytest.mark.django_db
class TestMasterPasswordChange:

    def test_change_master_password_success(self, authenticated_client, user, test_password, password_entry):
        change_data = {
            "current_master_password": test_password,
            "new_master_password": "NewMasterPass123!",
            "confirm_master_password": "NewMasterPass123!",
        }

        response = authenticated_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert "re-encrypted" in response.json()["message"].lower()

    def test_change_master_password_wrong_current(self, authenticated_client, user):
        change_data = {
            "current_master_password": "WrongPassword123!",
            "new_master_password": "NewMasterPass123!",
            "confirm_master_password": "NewMasterPass123!",
        }

        response = authenticated_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "master password" in response.json()["detail"].lower()

    def test_change_master_password_mismatch(self, authenticated_client, test_password):
        change_data = {
            "current_master_password": test_password,
            "new_master_password": "NewMasterPass123!",
            "confirm_master_password": "DifferentPass123!",
        }

        response = authenticated_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code in [400, 422]

    def test_change_master_password_re_encrypts_entries(self, authenticated_client, user, test_password):
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        encrypted1, salt1 = encryption_service.encrypt_password("password1", test_password)
        entry1 = PasswordEntry.objects.create(
            user=user,
            name="Entry 1",
            encrypted_password=encrypted1,
            encryption_salt=salt1,
        )

        encrypted2, salt2 = encryption_service.encrypt_password("password2", test_password)
        entry2 = PasswordEntry.objects.create(
            user=user,
            name="Entry 2",
            encrypted_password=encrypted2,
            encryption_salt=salt2,
        )

        new_master = "NewMasterPass123!"
        change_data = {
            "current_master_password": test_password,
            "new_master_password": new_master,
            "confirm_master_password": new_master,
        }

        response = authenticated_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        response_data = response.json()
        assert "re-encrypted" in response_data["message"].lower()
        assert "2" in response_data["message"]

    def test_change_master_password_without_authentication(self, api_client, test_password):
        change_data = {
            "current_master_password": test_password,
            "new_master_password": "NewMasterPass123!",
            "confirm_master_password": "NewMasterPass123!",
        }

        response = api_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_change_master_password_updates_user_password(self, authenticated_client, user, test_password):
        new_password = "NewMasterPass123!"
        change_data = {
            "current_master_password": test_password,
            "new_master_password": new_password,
            "confirm_master_password": new_password,
        }

        response = authenticated_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code == 200

        user.refresh_from_db()
        assert user.check_password(new_password)
        assert not user.check_password(test_password)

    def test_change_master_password_decrypt_with_new_password(
        self, authenticated_client, user, test_password
    ):
        """Test that passwords can be decrypted with new master password after change."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        original_password = "MySecretPassword123!"
        encrypted, salt = encryption_service.encrypt_password(original_password, test_password)
        entry = PasswordEntry.objects.create(
            user=user,
            name="Test Entry",
            encrypted_password=encrypted,
            encryption_salt=salt,
        )

        new_master = "NewMasterPass456!"
        change_data = {
            "current_master_password": test_password,
            "new_master_password": new_master,
            "confirm_master_password": new_master,
        }

        response = authenticated_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code == 200

        entry.refresh_from_db()

        from authentication.db_utils import convert_salt_to_bytes
        salt_bytes = convert_salt_to_bytes(entry.encryption_salt)
        decrypted = encryption_service.decrypt_password(
            entry.encrypted_password, new_master, salt_bytes
        )
        assert decrypted == original_password

    def test_change_master_password_cannot_decrypt_with_old_password(
        self, authenticated_client, user, test_password
    ):
        """Test that passwords cannot be decrypted with old master password after change."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        original_password = "MySecretPassword123!"
        encrypted, salt = encryption_service.encrypt_password(original_password, test_password)
        entry = PasswordEntry.objects.create(
            user=user,
            name="Test Entry",
            encrypted_password=encrypted,
            encryption_salt=salt,
        )

        new_master = "NewMasterPass456!"
        change_data = {
            "current_master_password": test_password,
            "new_master_password": new_master,
            "confirm_master_password": new_master,
        }

        authenticated_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        entry.refresh_from_db()

        from authentication.db_utils import convert_salt_to_bytes
        salt_bytes = convert_salt_to_bytes(entry.encryption_salt)
        decrypted = encryption_service.decrypt_password(
            entry.encrypted_password, test_password, salt_bytes
        )
        assert decrypted is None or decrypted != original_password

    def test_change_master_password_multiple_entries(
        self, authenticated_client, user, test_password
    ):
        """Test re-encryption of multiple entries with different passwords."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        passwords = ["Password1!", "Password2!", "Password3!", "Password4!", "Password5!"]
        entries = []

        for i, pwd in enumerate(passwords):
            encrypted, salt = encryption_service.encrypt_password(pwd, test_password)
            entry = PasswordEntry.objects.create(
                user=user,
                name=f"Entry {i+1}",
                encrypted_password=encrypted,
                encryption_salt=salt,
            )
            entries.append((entry, pwd))

        new_master = "NewMasterPass789!"
        change_data = {
            "current_master_password": test_password,
            "new_master_password": new_master,
            "confirm_master_password": new_master,
        }

        response = authenticated_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert "5" in response.json()["message"]

        from authentication.db_utils import convert_salt_to_bytes

        for entry, original_pwd in entries:
            entry.refresh_from_db()
            salt_bytes = convert_salt_to_bytes(entry.encryption_salt)
            decrypted = encryption_service.decrypt_password(
                entry.encrypted_password, new_master, salt_bytes
            )
            assert decrypted == original_pwd

    def test_change_master_password_with_no_entries(
        self, authenticated_client, user, test_password
    ):
        """Test changing master password when user has no password entries."""
        new_master = "NewMasterPass123!"
        change_data = {
            "current_master_password": test_password,
            "new_master_password": new_master,
            "confirm_master_password": new_master,
        }

        response = authenticated_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert "0" in response.json()["message"]

        user.refresh_from_db()
        assert user.check_password(new_master)

    def test_change_master_password_preserves_metadata(
        self, authenticated_client, user, test_password
    ):
        """Test that entry metadata is preserved during re-encryption."""
        from authentication.models import PasswordEntry, PasswordFolder, PasswordTag
        from authentication.encryption_service import encryption_service

        folder = PasswordFolder.objects.create(user=user, name="Work")
        tag1 = PasswordTag.objects.create(user=user, name="important")
        tag2 = PasswordTag.objects.create(user=user, name="finance")

        encrypted, salt = encryption_service.encrypt_password("password", test_password)
        entry = PasswordEntry.objects.create(
            user=user,
            name="Important Entry",
            site="https://example.com",
            username="testuser",
            notes="Important notes",
            folder=folder,
            is_favorite=True,
            encrypted_password=encrypted,
            encryption_salt=salt,
        )
        entry.tags.add(tag1, tag2)

        original_created_at = entry.created_at
        original_updated_at = entry.updated_at

        new_master = "NewMasterPass123!"
        change_data = {
            "current_master_password": test_password,
            "new_master_password": new_master,
            "confirm_master_password": new_master,
        }

        authenticated_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        entry.refresh_from_db()

        assert entry.name == "Important Entry"
        assert entry.site == "https://example.com"
        assert entry.username == "testuser"
        assert entry.notes == "Important notes"
        assert entry.folder == folder
        assert entry.is_favorite is True
        assert entry.tags.count() == 2
        assert tag1 in entry.tags.all()
        assert tag2 in entry.tags.all()
        assert entry.created_at == original_created_at

    def test_change_master_password_api_decrypt_works(
        self, authenticated_client, user, test_password
    ):
        """Test that API decrypt endpoint works with new master password."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        original_password = "ApiTestPassword123!"
        encrypted, salt = encryption_service.encrypt_password(original_password, test_password)
        entry = PasswordEntry.objects.create(
            user=user,
            name="API Test Entry",
            encrypted_password=encrypted,
            encryption_salt=salt,
        )

        new_master = "NewMasterPass123!"
        change_data = {
            "current_master_password": test_password,
            "new_master_password": new_master,
            "confirm_master_password": new_master,
        }

        authenticated_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        decrypt_data = {"master_password": new_master}
        response = authenticated_client.post(
            f"/api/passwords/entries/{entry.id}/decrypt",
            data=json.dumps(decrypt_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.json()["password"] == original_password

    def test_change_master_password_export_works(
        self, authenticated_client, user, test_password
    ):
        """Test that export works with new master password after change."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service
        import base64

        original_password = "ExportTestPassword123!"
        encrypted, salt = encryption_service.encrypt_password(original_password, test_password)
        PasswordEntry.objects.create(
            user=user,
            name="Export Test Entry",
            encrypted_password=encrypted,
            encryption_salt=salt,
        )

        new_master = "NewMasterPass123!"
        change_data = {
            "current_master_password": test_password,
            "new_master_password": new_master,
            "confirm_master_password": new_master,
        }

        authenticated_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        export_data = {
            "format": "json",
            "master_password": new_master,
            "include_passwords": True,
        }

        response = authenticated_client.post(
            "/api/passwords/export",
            data=json.dumps(export_data),
            content_type="application/json",
        )

        assert response.status_code == 200

        decoded_data = base64.b64decode(response.json()["data"]).decode()
        export_json = json.loads(decoded_data)

        assert len(export_json) == 1
        assert export_json[0]["password"] == original_password

    def test_change_master_password_weak_new_password(
        self, authenticated_client, test_password
    ):
        """Test that weak new master password is rejected."""
        change_data = {
            "current_master_password": test_password,
            "new_master_password": "weak",
            "confirm_master_password": "weak",
        }

        response = authenticated_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code in [400, 422]

    def test_change_master_password_same_as_current(
        self, authenticated_client, test_password
    ):
        """Test changing master password to the same password."""
        change_data = {
            "current_master_password": test_password,
            "new_master_password": test_password,
            "confirm_master_password": test_password,
        }

        response = authenticated_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code in [200, 400]

    def test_change_master_password_special_characters(
        self, authenticated_client, user, test_password
    ):
        """Test changing to a master password with special characters."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        original_password = "TestPassword123!"
        encrypted, salt = encryption_service.encrypt_password(original_password, test_password)
        entry = PasswordEntry.objects.create(
            user=user,
            name="Special Char Test",
            encrypted_password=encrypted,
            encryption_salt=salt,
        )

        new_master = "N3w!@#$%^&*()_+-=[]{}|;:,.<>?M@st3r"
        change_data = {
            "current_master_password": test_password,
            "new_master_password": new_master,
            "confirm_master_password": new_master,
        }

        response = authenticated_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code == 200

        entry.refresh_from_db()
        from authentication.db_utils import convert_salt_to_bytes
        salt_bytes = convert_salt_to_bytes(entry.encryption_salt)
        decrypted = encryption_service.decrypt_password(
            entry.encrypted_password, new_master, salt_bytes
        )
        assert decrypted == original_password

    def test_change_master_password_unicode_characters(
        self, authenticated_client, user, test_password
    ):
        """Test changing to a master password with unicode characters."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        original_password = "TestPassword123!"
        encrypted, salt = encryption_service.encrypt_password(original_password, test_password)
        entry = PasswordEntry.objects.create(
            user=user,
            name="Unicode Test",
            encrypted_password=encrypted,
            encryption_salt=salt,
        )

        new_master = "M@st3r密码🔒Пароль!"
        change_data = {
            "current_master_password": test_password,
            "new_master_password": new_master,
            "confirm_master_password": new_master,
        }

        response = authenticated_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code == 200

        entry.refresh_from_db()
        from authentication.db_utils import convert_salt_to_bytes
        salt_bytes = convert_salt_to_bytes(entry.encryption_salt)
        decrypted = encryption_service.decrypt_password(
            entry.encrypted_password, new_master, salt_bytes
        )
        assert decrypted == original_password

    def test_change_master_password_long_password(
        self, authenticated_client, user, test_password
    ):
        """Test changing to a very long master password."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        original_password = "TestPassword123!"
        encrypted, salt = encryption_service.encrypt_password(original_password, test_password)
        entry = PasswordEntry.objects.create(
            user=user,
            name="Long Password Test",
            encrypted_password=encrypted,
            encryption_salt=salt,
        )

        new_master = "A" * 100 + "1!Bb"
        change_data = {
            "current_master_password": test_password,
            "new_master_password": new_master,
            "confirm_master_password": new_master,
        }

        response = authenticated_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code == 200

        entry.refresh_from_db()
        from authentication.db_utils import convert_salt_to_bytes
        salt_bytes = convert_salt_to_bytes(entry.encryption_salt)
        decrypted = encryption_service.decrypt_password(
            entry.encrypted_password, new_master, salt_bytes
        )
        assert decrypted == original_password

    def test_change_master_password_entries_with_special_chars(
        self, authenticated_client, user, test_password
    ):
        """Test that entries with special character passwords are correctly re-encrypted."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        special_passwords = [
            "P@$$w0rd!#%",
            "密码🔒Test",
            "Пароль!@#",
            "Test\n\t\r",
            "Test'\"<>",
        ]

        entries = []
        for i, pwd in enumerate(special_passwords):
            encrypted, salt = encryption_service.encrypt_password(pwd, test_password)
            entry = PasswordEntry.objects.create(
                user=user,
                name=f"Special Entry {i+1}",
                encrypted_password=encrypted,
                encryption_salt=salt,
            )
            entries.append((entry, pwd))

        new_master = "NewMasterPass123!"
        change_data = {
            "current_master_password": test_password,
            "new_master_password": new_master,
            "confirm_master_password": new_master,
        }

        response = authenticated_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        assert response.status_code == 200

        from authentication.db_utils import convert_salt_to_bytes

        for entry, original_pwd in entries:
            entry.refresh_from_db()
            salt_bytes = convert_salt_to_bytes(entry.encryption_salt)
            decrypted = encryption_service.decrypt_password(
                entry.encrypted_password, new_master, salt_bytes
            )
            assert decrypted == original_pwd

    def test_change_master_password_old_api_decrypt_fails(
        self, authenticated_client, user, test_password, password_entry
    ):
        """Test that API decrypt with old master password fails after change."""
        new_master = "NewMasterPass123!"
        change_data = {
            "current_master_password": test_password,
            "new_master_password": new_master,
            "confirm_master_password": new_master,
        }

        authenticated_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        decrypt_data = {"master_password": test_password}
        response = authenticated_client.post(
            f"/api/passwords/entries/{password_entry.id}/decrypt",
            data=json.dumps(decrypt_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "master password" in response.json()["detail"].lower()

    def test_change_master_password_old_export_fails(
        self, authenticated_client, test_password, password_entry
    ):
        """Test that export with old master password fails after change."""
        new_master = "NewMasterPass123!"
        change_data = {
            "current_master_password": test_password,
            "new_master_password": new_master,
            "confirm_master_password": new_master,
        }

        authenticated_client.post(
            "/api/passwords/master-password/change",
            data=json.dumps(change_data),
            content_type="application/json",
        )

        export_data = {
            "format": "json",
            "master_password": test_password,
            "include_passwords": True,
        }

        response = authenticated_client.post(
            "/api/passwords/export",
            data=json.dumps(export_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "master password" in response.json()["detail"].lower()
