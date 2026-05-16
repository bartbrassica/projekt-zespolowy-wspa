"""
Integration tests for bulk operations on password entries.
"""

import pytest
import json


@pytest.mark.integration
@pytest.mark.django_db
class TestBulkDeletePasswords:

    def test_bulk_delete_success(self, authenticated_client, user, test_password):
        """Test successful bulk deletion of multiple password entries."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        # Create multiple password entries
        entries = []
        for i in range(5):
            encrypted, salt = encryption_service.encrypt_password(f"password{i}", test_password)
            entry = PasswordEntry.objects.create(
                user=user,
                name=f"Entry {i}",
                encrypted_password=encrypted,
                encryption_salt=salt,
            )
            entries.append(entry)

        entry_ids = [str(entry.id) for entry in entries[:3]]  # Delete first 3

        delete_data = {
            "entry_ids": entry_ids,
            "master_password": test_password,
        }

        response = authenticated_client.post(
            "/api/passwords/entries/bulk-delete",
            data=json.dumps(delete_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert "3" in response.json()["message"]

        # Verify entries are deleted
        assert not PasswordEntry.objects.filter(id__in=[e.id for e in entries[:3]]).exists()
        # Verify remaining entries still exist
        assert PasswordEntry.objects.filter(id__in=[e.id for e in entries[3:]]).count() == 2

    def test_bulk_delete_all_user_entries(self, authenticated_client, user, test_password):
        """Test deleting all entries for a user."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        # Create entries
        entries = []
        for i in range(3):
            encrypted, salt = encryption_service.encrypt_password(f"password{i}", test_password)
            entry = PasswordEntry.objects.create(
                user=user,
                name=f"Entry {i}",
                encrypted_password=encrypted,
                encryption_salt=salt,
            )
            entries.append(entry)

        entry_ids = [str(entry.id) for entry in entries]

        delete_data = {
            "entry_ids": entry_ids,
            "master_password": test_password,
        }

        response = authenticated_client.post(
            "/api/passwords/entries/bulk-delete",
            data=json.dumps(delete_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert PasswordEntry.objects.filter(user=user).count() == 0

    def test_bulk_delete_wrong_master_password(self, authenticated_client, user, test_password):
        """Test bulk delete with incorrect master password."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        encrypted, salt = encryption_service.encrypt_password("password", test_password)
        entry = PasswordEntry.objects.create(
            user=user,
            name="Test Entry",
            encrypted_password=encrypted,
            encryption_salt=salt,
        )

        delete_data = {
            "entry_ids": [str(entry.id)],
            "master_password": "WrongPassword123!",
        }

        response = authenticated_client.post(
            "/api/passwords/entries/bulk-delete",
            data=json.dumps(delete_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "master password" in response.json()["detail"].lower()

        # Verify entry still exists
        assert PasswordEntry.objects.filter(id=entry.id).exists()

    def test_bulk_delete_without_authentication(self, api_client, test_password):
        """Test bulk delete without authentication."""
        delete_data = {
            "entry_ids": ["00000000-0000-0000-0000-000000000000"],
            "master_password": test_password,
        }

        response = api_client.post(
            "/api/passwords/entries/bulk-delete",
            data=json.dumps(delete_data),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_bulk_delete_other_user_entries(self, authenticated_client, multiple_users, test_password):
        """Test that user cannot delete other user's entries."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        # Create entry for another user
        other_user = multiple_users[0]
        encrypted, salt = encryption_service.encrypt_password("password", test_password)
        other_entry = PasswordEntry.objects.create(
            user=other_user,
            name="Other User Entry",
            encrypted_password=encrypted,
            encryption_salt=salt,
        )

        delete_data = {
            "entry_ids": [str(other_entry.id)],
            "master_password": test_password,
        }

        response = authenticated_client.post(
            "/api/passwords/entries/bulk-delete",
            data=json.dumps(delete_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        # Should report 0 deleted since the entry doesn't belong to authenticated user
        assert "0" in response.json()["message"]

        # Verify other user's entry still exists
        assert PasswordEntry.objects.filter(id=other_entry.id).exists()

    def test_bulk_delete_empty_list(self, authenticated_client, test_password):
        """Test bulk delete with empty entry list."""
        delete_data = {
            "entry_ids": [],
            "master_password": test_password,
        }

        response = authenticated_client.post(
            "/api/passwords/entries/bulk-delete",
            data=json.dumps(delete_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert "0" in response.json()["message"]

    def test_bulk_delete_nonexistent_entries(self, authenticated_client, test_password):
        """Test bulk delete with non-existent entry IDs."""
        delete_data = {
            "entry_ids": [
                "00000000-0000-0000-0000-000000000001",
                "00000000-0000-0000-0000-000000000002",
            ],
            "master_password": test_password,
        }

        response = authenticated_client.post(
            "/api/passwords/entries/bulk-delete",
            data=json.dumps(delete_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert "0" in response.json()["message"]

    def test_bulk_delete_mixed_valid_invalid_ids(
        self, authenticated_client, user, test_password
    ):
        """Test bulk delete with mix of valid and invalid entry IDs."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        # Create valid entries
        entries = []
        for i in range(2):
            encrypted, salt = encryption_service.encrypt_password(f"password{i}", test_password)
            entry = PasswordEntry.objects.create(
                user=user,
                name=f"Entry {i}",
                encrypted_password=encrypted,
                encryption_salt=salt,
            )
            entries.append(entry)

        valid_ids = [str(entry.id) for entry in entries]
        invalid_ids = ["00000000-0000-0000-0000-000000000001"]

        delete_data = {
            "entry_ids": valid_ids + invalid_ids,
            "master_password": test_password,
        }

        response = authenticated_client.post(
            "/api/passwords/entries/bulk-delete",
            data=json.dumps(delete_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        # Should delete only the 2 valid entries
        assert "2" in response.json()["message"]

        # Verify valid entries are deleted
        assert not PasswordEntry.objects.filter(id__in=[e.id for e in entries]).exists()

    def test_bulk_delete_logs_access(
        self, authenticated_client, user, test_password
    ):
        """Test that bulk delete logs access for each deleted entry."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service
        from unittest.mock import patch
        from authentication.db_utils import log_password_access

        # Create entries
        entries = []
        for i in range(3):
            encrypted, salt = encryption_service.encrypt_password(f"password{i}", test_password)
            entry = PasswordEntry.objects.create(
                user=user,
                name=f"Entry {i}",
                encrypted_password=encrypted,
                encryption_salt=salt,
            )
            entries.append(entry)

        entry_ids = [str(entry.id) for entry in entries]

        delete_data = {
            "entry_ids": entry_ids,
            "master_password": test_password,
        }

        # Mock log_password_access to verify it's called for each entry
        with patch("authentication.password_endpoints.log_password_access") as mock_log:
            response = authenticated_client.post(
                "/api/passwords/entries/bulk-delete",
                data=json.dumps(delete_data),
                content_type="application/json",
            )

            assert response.status_code == 200
            # Verify log_password_access was called 3 times (once per entry)
            assert mock_log.call_count == 3
            # Verify each call had action="delete"
            for call in mock_log.call_args_list:
                assert call[0][2] == "delete"  # Third argument is action

    def test_bulk_delete_with_duplicate_ids(
        self, authenticated_client, user, test_password
    ):
        """Test bulk delete with duplicate entry IDs."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        encrypted, salt = encryption_service.encrypt_password("password", test_password)
        entry = PasswordEntry.objects.create(
            user=user,
            name="Test Entry",
            encrypted_password=encrypted,
            encryption_salt=salt,
        )

        # Include the same ID multiple times
        entry_id = str(entry.id)
        delete_data = {
            "entry_ids": [entry_id, entry_id, entry_id],
            "master_password": test_password,
        }

        response = authenticated_client.post(
            "/api/passwords/entries/bulk-delete",
            data=json.dumps(delete_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        # Should only delete once
        assert "1" in response.json()["message"]
        assert not PasswordEntry.objects.filter(id=entry.id).exists()

    def test_bulk_delete_large_batch(
        self, authenticated_client, user, test_password
    ):
        """Test bulk delete with a large number of entries."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        # Create 50 entries
        entries = []
        for i in range(50):
            encrypted, salt = encryption_service.encrypt_password(f"password{i}", test_password)
            entry = PasswordEntry.objects.create(
                user=user,
                name=f"Entry {i}",
                encrypted_password=encrypted,
                encryption_salt=salt,
            )
            entries.append(entry)

        entry_ids = [str(entry.id) for entry in entries]

        delete_data = {
            "entry_ids": entry_ids,
            "master_password": test_password,
        }

        response = authenticated_client.post(
            "/api/passwords/entries/bulk-delete",
            data=json.dumps(delete_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert "50" in response.json()["message"]
        assert PasswordEntry.objects.filter(user=user).count() == 0

    def test_bulk_delete_entries_with_relationships(
        self, authenticated_client, user, test_password
    ):
        """Test bulk delete of entries that have folders, tags, and history."""
        from authentication.models import (
            PasswordEntry,
            PasswordFolder,
            PasswordTag,
            PasswordEntryHistory,
        )
        from authentication.encryption_service import encryption_service

        # Create folder and tags
        folder = PasswordFolder.objects.create(user=user, name="Work")
        tag1 = PasswordTag.objects.create(user=user, name="important")
        tag2 = PasswordTag.objects.create(user=user, name="finance")

        # Create entries with relationships
        entries = []
        for i in range(2):
            encrypted, salt = encryption_service.encrypt_password(f"password{i}", test_password)
            entry = PasswordEntry.objects.create(
                user=user,
                name=f"Entry {i}",
                folder=folder,
                encrypted_password=encrypted,
                encryption_salt=salt,
            )
            entry.tags.add(tag1, tag2)

            # Add history
            PasswordEntryHistory.objects.create(
                password_entry=entry,
                encrypted_password=encrypted,
                encryption_salt=salt,
                changed_by=user,
            )
            entries.append(entry)

        entry_ids = [str(entry.id) for entry in entries]

        delete_data = {
            "entry_ids": entry_ids,
            "master_password": test_password,
        }

        response = authenticated_client.post(
            "/api/passwords/entries/bulk-delete",
            data=json.dumps(delete_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert "2" in response.json()["message"]

        # Verify entries are deleted
        assert not PasswordEntry.objects.filter(id__in=[e.id for e in entries]).exists()

        # Verify related objects still exist (folder and tags should persist)
        assert PasswordFolder.objects.filter(id=folder.id).exists()
        assert PasswordTag.objects.filter(id=tag1.id).exists()
        assert PasswordTag.objects.filter(id=tag2.id).exists()

    def test_bulk_delete_missing_master_password(
        self, authenticated_client, user, test_password
    ):
        """Test bulk delete without providing master password."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        encrypted, salt = encryption_service.encrypt_password("password", test_password)
        entry = PasswordEntry.objects.create(
            user=user,
            name="Test Entry",
            encrypted_password=encrypted,
            encryption_salt=salt,
        )

        delete_data = {
            "entry_ids": [str(entry.id)],
        }

        response = authenticated_client.post(
            "/api/passwords/entries/bulk-delete",
            data=json.dumps(delete_data),
            content_type="application/json",
        )

        assert response.status_code == 422

        # Verify entry still exists
        assert PasswordEntry.objects.filter(id=entry.id).exists()

    def test_bulk_delete_invalid_uuid_format(self, authenticated_client, test_password):
        """Test bulk delete with invalid UUID format."""
        delete_data = {
            "entry_ids": ["invalid-uuid", "not-a-uuid-at-all"],
            "master_password": test_password,
        }

        response = authenticated_client.post(
            "/api/passwords/entries/bulk-delete",
            data=json.dumps(delete_data),
            content_type="application/json",
        )

        # Should handle gracefully - either 200 with 0 deleted or validation error
        assert response.status_code in [200, 400, 422]
