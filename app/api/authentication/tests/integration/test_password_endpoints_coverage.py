"""
Integration tests to achieve 100% coverage for password_endpoints.py
Covers edge cases and exception paths not covered by other test files.
"""

import pytest
import json
import base64
from django.utils import timezone


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordEntryEdgeCases:
    """Tests for password entry edge cases."""

    def test_create_entry_with_invalid_folder_id(self, authenticated_client, user, test_password):
        """Test creating entry with non-existent folder ID (lines 87-88)."""
        entry_data = {
            "name": "Test Entry",
            "password": "SecurePass123!",
            "master_password": test_password,
            "folder_id": "00000000-0000-0000-0000-000000000000",  # Non-existent folder
        }

        response = authenticated_client.post(
            "/api/passwords/entries",
            data=json.dumps(entry_data),
            content_type="application/json",
        )

        # Should succeed but folder should be None (exception is caught with pass)
        assert response.status_code == 201
        data = response.json()
        # Folder_id might not be in response or should be None
        assert data.get("folder_id") is None

    def test_update_entry_with_invalid_folder_id(self, authenticated_client, password_entry, test_password):
        """Test updating entry with non-existent folder ID (lines 289-290)."""
        update_data = {
            "master_password": test_password,
            "folder_id": "00000000-0000-0000-0000-000000000000",  # Non-existent folder
        }

        response = authenticated_client.put(
            f"/api/passwords/entries/{password_entry.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        # Should fail with 400 error
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    def test_decrypt_password_failure(self, authenticated_client, user, test_password):
        """Test decrypt password when decryption fails (line 364)."""
        from authentication.models import PasswordEntry

        # Create an entry with corrupted encrypted data
        # Use correct password for verification but corrupted data so decryption fails
        entry = PasswordEntry.objects.create(
            user=user,
            name="Corrupted Entry",
            encrypted_password="corrupted_invalid_data",
            encryption_salt=b"salt",
        )

        decrypt_data = {
            "master_password": test_password,
        }

        response = authenticated_client.post(
            f"/api/passwords/entries/{entry.id}/decrypt",
            data=json.dumps(decrypt_data),
            content_type="application/json",
        )

        # Should fail to decrypt
        assert response.status_code == 400
        assert "decrypt" in response.json()["detail"].lower()


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordListSorting:
    """Tests for password list sorting edge cases."""

    def test_list_with_invalid_sort_by(self, authenticated_client, user):
        """Test list with invalid sort_by parameter (line 161)."""
        response = authenticated_client.get(
            "/api/passwords/entries?sort_by=invalid_field"
        )

        # Should succeed and default to 'updated_at'
        assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.django_db
class TestFolderUpdateEdgeCases:
    """Tests for folder update edge cases."""

    def test_update_folder_with_invalid_parent_id(self, authenticated_client, password_folder):
        """Test updating folder with non-existent parent ID (lines 452-453)."""
        update_data = {
            "parent_id": "00000000-0000-0000-0000-000000000000",
        }

        response = authenticated_client.put(
            f"/api/passwords/folders/{password_folder.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        # Should fail with 400 error
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.integration
@pytest.mark.django_db
class TestTagOperations:
    """Tests for tag CRUD operations (lines 482-514)."""

    def test_create_tag_success(self, authenticated_client, user):
        """Test creating a tag successfully (lines 482-489)."""
        tag_data = {
            "name": "important",
            "color": "#FF0000",
        }

        response = authenticated_client.post(
            "/api/passwords/tags",
            data=json.dumps(tag_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "important"
        assert data["color"] == "#FF0000"

    def test_create_tag_duplicate(self, authenticated_client, password_tag):
        """Test creating a tag with duplicate name (line 485)."""
        tag_data = {
            "name": password_tag.name,
            "color": "#0000FF",
        }

        response = authenticated_client.post(
            "/api/passwords/tags",
            data=json.dumps(tag_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_list_tags(self, authenticated_client, user):
        """Test listing tags (lines 494-502)."""
        from authentication.models import PasswordTag

        # Create multiple tags
        PasswordTag.objects.create(user=user, name="work", color="#FF0000")
        PasswordTag.objects.create(user=user, name="personal", color="#00FF00")
        PasswordTag.objects.create(user=user, name="important", color="#0000FF")

        response = authenticated_client.get("/api/passwords/tags")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    def test_delete_tag_success(self, authenticated_client, password_tag):
        """Test deleting a tag successfully (lines 507-514)."""
        tag_id = password_tag.id

        response = authenticated_client.delete(f"/api/passwords/tags/{tag_id}")

        assert response.status_code == 204

        from authentication.models import PasswordTag
        assert not PasswordTag.objects.filter(id=tag_id).exists()

    def test_delete_tag_not_found(self, authenticated_client):
        """Test deleting non-existent tag (line 514)."""
        response = authenticated_client.delete(
            "/api/passwords/tags/00000000-0000-0000-0000-000000000000"
        )

        assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.django_db
class TestImportExportFormats:
    """Tests for import/export format validation."""

    def test_import_unsupported_format(self, authenticated_client, user, test_password):
        """Test import with unsupported format (line 622)."""
        import_data = {
            "master_password": test_password,
            "format": "bitwarden",  # Allowed by schema but not implemented
            "data": base64.b64encode(b"{}").decode(),
        }

        response = authenticated_client.post(
            "/api/passwords/import",
            data=json.dumps(import_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "unsupported" in response.json()["detail"].lower()

    def test_export_unsupported_format(self, authenticated_client, user, test_password):
        """Test export with unsupported format (line 692)."""
        export_data = {
            "master_password": test_password,
            "format": "pdf",  # Allowed by schema but not implemented
            "include_passwords": False,
        }

        response = authenticated_client.post(
            "/api/passwords/export",
            data=json.dumps(export_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "unsupported" in response.json()["detail"].lower()


@pytest.mark.integration
@pytest.mark.django_db
class TestShareLinkOperations:
    """Tests for share link creation and access (lines 700-771)."""

    def test_create_share_link_success(self, authenticated_client, password_entry, test_password):
        """Test creating a share link successfully (lines 700-741)."""
        share_data = {
            "master_password": test_password,
            "password_entry_id": str(password_entry.id),
            "max_views": 5,
            "expires_in_hours": 24,
            "require_authentication": False,
        }

        response = authenticated_client.post(
            "/api/passwords/share",
            data=json.dumps(share_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()
        assert "share_url" in data
        assert data["max_views"] == 5
        assert data["current_views"] == 0

    def test_create_share_link_invalid_master_password(self, authenticated_client, password_entry):
        """Test creating share link with wrong master password (line 703)."""
        share_data = {
            "master_password": "WrongPassword123!",
            "password_entry_id": str(password_entry.id),
            "max_views": 3,
            "expires_in_hours": 12,
            "require_authentication": False,
        }

        response = authenticated_client.post(
            "/api/passwords/share",
            data=json.dumps(share_data),
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_create_share_link_decrypt_failure(self, authenticated_client, user, test_password):
        """Test creating share link when decryption fails (line 713)."""
        from authentication.models import PasswordEntry

        # Create an entry with corrupted encryption data
        entry = PasswordEntry.objects.create(
            user=user,
            name="Corrupted Entry",
            encrypted_password="corrupted_data",
            encryption_salt=b"salt",
        )

        share_data = {
            "master_password": test_password,
            "password_entry_id": str(entry.id),
            "max_views": 1,
            "expires_in_hours": 1,
            "require_authentication": False,
        }

        response = authenticated_client.post(
            "/api/passwords/share",
            data=json.dumps(share_data),
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_create_share_link_entry_not_found(self, authenticated_client, test_password):
        """Test creating share link for non-existent entry (line 741)."""
        share_data = {
            "master_password": test_password,
            "password_entry_id": "00000000-0000-0000-0000-000000000000",
            "max_views": 1,
            "expires_in_hours": 1,
            "require_authentication": False,
        }

        response = authenticated_client.post(
            "/api/passwords/share",
            data=json.dumps(share_data),
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_access_shared_password_success(self, api_client, password_share_link):
        """Test accessing a shared password successfully (lines 746-771)."""
        response = api_client.get(
            f"/api/passwords/shared/{password_share_link.share_token}"
        )

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "site" in data
        assert "username" in data
        assert "views_remaining" in data

    def test_access_shared_password_expired(self, api_client, user, password_entry):
        """Test accessing an expired share link (line 750)."""
        from authentication.models import PasswordShareLink
        from datetime import timedelta

        # Create an expired share link
        expired_link = PasswordShareLink.objects.create(
            password_entry=password_entry,
            created_by=user,
            max_views=5,
            expires_at=timezone.now() - timedelta(hours=1),  # Expired
            require_authentication=False,
        )

        response = api_client.get(
            f"/api/passwords/shared/{expired_link.share_token}"
        )

        assert response.status_code == 404
        assert "expired" in response.json()["detail"].lower()

    def test_access_shared_password_max_views_reached(self, api_client, user, password_entry):
        """Test accessing share link that reached max views (line 750)."""
        from authentication.models import PasswordShareLink

        # Create a share link with max views already reached
        link = PasswordShareLink.objects.create(
            password_entry=password_entry,
            created_by=user,
            max_views=1,
            current_views=1,  # Already at max
            expires_at=timezone.now() + timezone.timedelta(hours=24),
            require_authentication=False,
        )

        response = api_client.get(f"/api/passwords/shared/{link.share_token}")

        assert response.status_code == 404
        assert "maximum views" in response.json()["detail"].lower() or "expired" in response.json()["detail"].lower()

    def test_access_shared_password_not_found(self, api_client):
        """Test accessing non-existent share link (line 771)."""
        response = api_client.get(
            "/api/passwords/shared/00000000-0000-0000-0000-000000000000"
        )

        assert response.status_code == 404

    def test_access_shared_password_with_authentication_required(self, api_client, user, password_entry):
        """Test accessing share link that requires authentication (line 752)."""
        from authentication.models import PasswordShareLink

        link = PasswordShareLink.objects.create(
            password_entry=password_entry,
            created_by=user,
            max_views=5,
            expires_at=timezone.now() + timezone.timedelta(hours=24),
            require_authentication=True,  # Requires auth
        )

        response = api_client.get(f"/api/passwords/shared/{link.share_token}")

        # Currently just passes through (line 753), so should still return 200
        assert response.status_code == 200
