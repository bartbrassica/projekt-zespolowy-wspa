"""
Integration tests for Password Entry CRUD operations.
"""

import pytest
import json
from datetime import timedelta
from django.utils import timezone

from authentication.models import PasswordEntry, PasswordAccessLog, PasswordEntryHistory


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordEntryCreate:

    def test_create_password_entry_success(self, authenticated_client, user, test_password):
        entry_data = {
            "name": "GitHub Account",
            "site": "https://github.com",
            "username": "testuser",
            "password": "SecurePass123!",
            "notes": "My GitHub account",
            "master_password": test_password,
            "is_favorite": False,
        }

        response = authenticated_client.post(
            "/api/passwords/entries",
            data=json.dumps(entry_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "GitHub Account"
        assert data["site"] in ["https://github.com", "https://github.com/"]
        assert data["username"] == "testuser"
        assert data["notes"] == "My GitHub account"
        assert "encrypted_password" not in data
        assert "id" in data

        entry = PasswordEntry.objects.get(id=data["id"])
        assert entry.user == user
        assert entry.encrypted_password

    def test_create_password_entry_with_folder(self, authenticated_client, user, test_password, password_folder):
        entry_data = {
            "name": "Social Media",
            "site": "https://twitter.com",
            "username": "myhandle",
            "password": "TwitterPass123!",
            "master_password": test_password,
            "folder_id": str(password_folder.id),
        }

        response = authenticated_client.post(
            "/api/passwords/entries",
            data=json.dumps(entry_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()
        assert data["folder"]["id"] == str(password_folder.id)
        assert data["folder"]["name"] == password_folder.name

    def test_create_password_entry_with_tags(self, authenticated_client, user, test_password):
        entry_data = {
            "name": "Work Email",
            "site": "https://mail.company.com",
            "username": "employee@company.com",
            "password": "WorkPass123!",
            "master_password": test_password,
            "tags": ["work", "email", "important"],
        }

        response = authenticated_client.post(
            "/api/passwords/entries",
            data=json.dumps(entry_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data["tags"]) == 3
        tag_names = [tag["name"] for tag in data["tags"]]
        assert "work" in tag_names
        assert "email" in tag_names
        assert "important" in tag_names

    def test_create_password_entry_with_expiration(self, authenticated_client, user, test_password):
        expires_at = (timezone.now() + timedelta(days=90)).isoformat()
        entry_data = {
            "name": "Temporary Account",
            "site": "https://temp.com",
            "username": "tempuser",
            "password": "TempPass123!",
            "master_password": test_password,
            "expires_at": expires_at,
        }

        response = authenticated_client.post(
            "/api/passwords/entries",
            data=json.dumps(entry_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()
        assert data["expires_at"] is not None
        assert data["is_expired"] is False

    def test_create_password_entry_as_favorite(self, authenticated_client, user, test_password):
        entry_data = {
            "name": "Important Site",
            "site": "https://important.com",
            "username": "user",
            "password": "ImportantPass123!",
            "master_password": test_password,
            "is_favorite": True,
        }

        response = authenticated_client.post(
            "/api/passwords/entries",
            data=json.dumps(entry_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()
        assert data["is_favorite"] is True

    def test_create_password_entry_invalid_master_password(self, authenticated_client, user):
        entry_data = {
            "name": "Test",
            "site": "https://test.com",
            "username": "test",
            "password": "TestPass123!",
            "master_password": "WrongPassword123!",
        }

        response = authenticated_client.post(
            "/api/passwords/entries",
            data=json.dumps(entry_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "master password" in response.json()["detail"].lower()

    def test_create_password_entry_duplicate(self, authenticated_client, user, test_password):
        entry_data = {
            "name": "Duplicate",
            "site": "https://duplicate.com",
            "username": "user",
            "password": "Pass123!",
            "master_password": test_password,
        }

        response1 = authenticated_client.post(
            "/api/passwords/entries",
            data=json.dumps(entry_data),
            content_type="application/json",
        )
        assert response1.status_code == 201

        response2 = authenticated_client.post(
            "/api/passwords/entries",
            data=json.dumps(entry_data),
            content_type="application/json",
        )
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"].lower()

    def test_create_password_entry_without_authentication(self, api_client, test_password):
        entry_data = {
            "name": "Test",
            "site": "https://test.com",
            "username": "test",
            "password": "TestPass123!",
            "master_password": test_password,
        }

        response = api_client.post(
            "/api/passwords/entries",
            data=json.dumps(entry_data),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_create_password_entry_minimal_data(self, authenticated_client, user, test_password):
        entry_data = {
            "name": "Minimal Entry",
            "password": "MinimalPass123!",
            "master_password": test_password,
        }

        response = authenticated_client.post(
            "/api/passwords/entries",
            data=json.dumps(entry_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Entry"

    def test_create_password_entry_logs_access(self, authenticated_client, user, test_password):
        entry_data = {
            "name": "Logged Entry",
            "site": "https://logged.com",
            "username": "user",
            "password": "LoggedPass123!",
            "master_password": test_password,
        }

        response = authenticated_client.post(
            "/api/passwords/entries",
            data=json.dumps(entry_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        entry_id = response.json()["id"]

        log = PasswordAccessLog.objects.filter(
            password_entry_id=entry_id,
            action="create",
        ).first()
        assert log is not None
        assert log.user == user


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordEntryList:

    def test_list_password_entries_success(self, authenticated_client, user):
        for i in range(3):
            PasswordEntry.objects.create(
                user=user,
                name=f"Entry {i}",
                site=f"https://site{i}.com",
                username=f"user{i}",
                encrypted_password="encrypted",
                encryption_salt=b"salt",
            )

        response = authenticated_client.get("/api/passwords/entries")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_password_entries_empty(self, authenticated_client, user):
        response = authenticated_client.get("/api/passwords/entries")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_list_password_entries_with_search_query(self, authenticated_client, user):
        PasswordEntry.objects.create(
            user=user,
            name="GitHub Account",
            site="https://github.com",
            username="githubuser",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )
        PasswordEntry.objects.create(
            user=user,
            name="Gmail Account",
            site="https://gmail.com",
            username="gmailuser",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )

        response = authenticated_client.get("/api/passwords/entries", {"query": "github"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "GitHub Account"

    def test_list_password_entries_filter_by_folder(self, authenticated_client, user, password_folder):
        PasswordEntry.objects.create(
            user=user,
            name="In Folder",
            site="https://infolder.com",
            username="user",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
            folder=password_folder,
        )
        PasswordEntry.objects.create(
            user=user,
            name="Not In Folder",
            site="https://notinfolder.com",
            username="user",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )

        response = authenticated_client.get("/api/passwords/entries", {"folder_id": str(password_folder.id)})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "In Folder"

    def test_list_password_entries_filter_by_tags(self, authenticated_client, user, password_tag):
        entry = PasswordEntry.objects.create(
            user=user,
            name="Tagged Entry",
            site="https://tagged.com",
            username="user",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )
        entry.tags.add(password_tag)

        PasswordEntry.objects.create(
            user=user,
            name="Untagged Entry",
            site="https://untagged.com",
            username="user",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )

        response = authenticated_client.get("/api/passwords/entries", {"tags": password_tag.name})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Tagged Entry"

    def test_list_password_entries_show_favorites_only(self, authenticated_client, user):
        PasswordEntry.objects.create(
            user=user,
            name="Favorite",
            site="https://fav.com",
            username="user",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
            is_favorite=True,
        )
        PasswordEntry.objects.create(
            user=user,
            name="Not Favorite",
            site="https://notfav.com",
            username="user",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
            is_favorite=False,
        )

        response = authenticated_client.get("/api/passwords/entries", {"show_favorites_only": True})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Favorite"

    def test_list_password_entries_exclude_expired(self, authenticated_client, user):
        PasswordEntry.objects.create(
            user=user,
            name="Valid Entry",
            site="https://valid.com",
            username="user",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
            expires_at=timezone.now() + timedelta(days=30),
        )
        PasswordEntry.objects.create(
            user=user,
            name="Expired Entry",
            site="https://expired.com",
            username="user",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
            expires_at=timezone.now() - timedelta(days=1),
        )

        response = authenticated_client.get("/api/passwords/entries")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Valid Entry"

    def test_list_password_entries_include_expired(self, authenticated_client, user):
        PasswordEntry.objects.create(
            user=user,
            name="Valid Entry",
            site="https://valid.com",
            username="user",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
            expires_at=timezone.now() + timedelta(days=30),
        )
        PasswordEntry.objects.create(
            user=user,
            name="Expired Entry",
            site="https://expired.com",
            username="user",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
            expires_at=timezone.now() - timedelta(days=1),
        )

        response = authenticated_client.get("/api/passwords/entries", {"show_expired": True})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_password_entries_sorting(self, authenticated_client, user):
        PasswordEntry.objects.create(
            user=user,
            name="A Entry",
            site="https://a.com",
            username="user",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )
        PasswordEntry.objects.create(
            user=user,
            name="Z Entry",
            site="https://z.com",
            username="user",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )

        response = authenticated_client.get("/api/passwords/entries", {"sort_by": "name", "sort_order": "asc"})
        assert response.status_code == 200
        data = response.json()
        assert data[0]["name"] == "A Entry"
        assert data[1]["name"] == "Z Entry"

        response = authenticated_client.get("/api/passwords/entries", {"sort_by": "name", "sort_order": "desc"})
        assert response.status_code == 200
        data = response.json()
        assert data[0]["name"] == "Z Entry"
        assert data[1]["name"] == "A Entry"

    def test_list_password_entries_pagination(self, authenticated_client, user):
        for i in range(10):
            PasswordEntry.objects.create(
                user=user,
                name=f"Entry {i:02d}",
                site=f"https://site{i}.com",
                username="user",
                encrypted_password="encrypted",
                encryption_salt=b"salt",
            )

        response = authenticated_client.get("/api/passwords/entries", {"limit": 5})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

        response = authenticated_client.get("/api/passwords/entries", {"limit": 5, "offset": 5})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_list_password_entries_isolation(self, authenticated_client, user, multiple_users):
        PasswordEntry.objects.create(
            user=user,
            name="My Entry",
            site="https://mine.com",
            username="user",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )

        for other_user in multiple_users:
            PasswordEntry.objects.create(
                user=other_user,
                name="Other Entry",
                site="https://other.com",
                username="user",
                encrypted_password="encrypted",
                encryption_salt=b"salt",
            )

        response = authenticated_client.get("/api/passwords/entries")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "My Entry"

    def test_list_password_entries_without_authentication(self, api_client):
        response = api_client.get("/api/passwords/entries")
        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordEntryGet:

    def test_get_password_entry_success(self, authenticated_client, user):
        entry = PasswordEntry.objects.create(
            user=user,
            name="Test Entry",
            site="https://test.com",
            username="testuser",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
            notes="Test notes",
        )

        response = authenticated_client.get(f"/api/passwords/entries/{entry.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(entry.id)
        assert data["name"] == "Test Entry"
        assert data["site"] == "https://test.com"
        assert data["username"] == "testuser"
        assert data["notes"] == "Test notes"

    def test_get_password_entry_not_found(self, authenticated_client, user):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = authenticated_client.get(f"/api/passwords/entries/{fake_id}")

        assert response.status_code == 404

    def test_get_password_entry_from_another_user(self, authenticated_client, multiple_users):
        other_user = multiple_users[0]
        entry = PasswordEntry.objects.create(
            user=other_user,
            name="Other User Entry",
            site="https://other.com",
            username="other",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )

        response = authenticated_client.get(f"/api/passwords/entries/{entry.id}")

        assert response.status_code == 404

    def test_get_password_entry_updates_last_accessed(self, authenticated_client, user):
        entry = PasswordEntry.objects.create(
            user=user,
            name="Test Entry",
            site="https://test.com",
            username="testuser",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )

        assert entry.last_accessed is None

        response = authenticated_client.get(f"/api/passwords/entries/{entry.id}")
        assert response.status_code == 200

        entry.refresh_from_db()
        assert entry.last_accessed is not None

    def test_get_password_entry_logs_access(self, authenticated_client, user):
        entry = PasswordEntry.objects.create(
            user=user,
            name="Test Entry",
            site="https://test.com",
            username="testuser",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )

        response = authenticated_client.get(f"/api/passwords/entries/{entry.id}")
        assert response.status_code == 200

        log = PasswordAccessLog.objects.filter(
            password_entry=entry,
            action="view",
        ).first()
        assert log is not None
        assert log.user == user

    def test_get_password_entry_without_authentication(self, api_client, user):
        entry = PasswordEntry.objects.create(
            user=user,
            name="Test Entry",
            site="https://test.com",
            username="testuser",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )

        response = api_client.get(f"/api/passwords/entries/{entry.id}")
        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordEntryUpdate:

    def test_update_password_entry_name(self, authenticated_client, password_entry, test_password):
        update_data = {
            "name": "Updated Name",
            "master_password": test_password,
        }

        response = authenticated_client.put(
            f"/api/passwords/entries/{password_entry.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

        password_entry.refresh_from_db()
        assert password_entry.name == "Updated Name"

    def test_update_password_entry_multiple_fields(self, authenticated_client, password_entry, test_password):
        update_data = {
            "name": "New Name",
            "site": "https://newsite.com",
            "username": "newuser",
            "notes": "Updated notes",
            "is_favorite": True,
            "master_password": test_password,
        }

        response = authenticated_client.put(
            f"/api/passwords/entries/{password_entry.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["site"] in ["https://newsite.com", "https://newsite.com/"]
        assert data["username"] == "newuser"
        assert data["notes"] == "Updated notes"
        assert data["is_favorite"] is True

    def test_update_password_entry_password(self, authenticated_client, password_entry, test_password):
        initial_encrypted = password_entry.encrypted_password

        update_data = {
            "password": "NewSecurePassword123!",
            "master_password": test_password,
        }

        response = authenticated_client.put(
            f"/api/passwords/entries/{password_entry.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200

        password_entry.refresh_from_db()
        assert password_entry.encrypted_password != initial_encrypted

        history = PasswordEntryHistory.objects.filter(
            password_entry=password_entry
        ).first()
        assert history is not None
        assert history.encrypted_password == initial_encrypted

    def test_update_password_entry_with_folder(self, authenticated_client, password_entry, password_folder, test_password):
        update_data = {
            "folder_id": str(password_folder.id),
            "master_password": test_password,
        }

        response = authenticated_client.put(
            f"/api/passwords/entries/{password_entry.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["folder"]["id"] == str(password_folder.id)

    def test_update_password_entry_remove_folder(self, authenticated_client, user, password_folder, test_password):
        entry = PasswordEntry.objects.create(
            user=user,
            name="Test Entry",
            site="https://test.com",
            username="user",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
            folder=password_folder,
        )

        update_data = {
            "folder_id": "",
            "master_password": test_password,
        }

        response = authenticated_client.put(
            f"/api/passwords/entries/{entry.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["folder"] is None

    def test_update_password_entry_with_tags(self, authenticated_client, password_entry, test_password):
        update_data = {
            "tags": ["work", "important", "urgent"],
            "master_password": test_password,
        }

        response = authenticated_client.put(
            f"/api/passwords/entries/{password_entry.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["tags"]) == 3
        tag_names = [tag["name"] for tag in data["tags"]]
        assert "work" in tag_names
        assert "important" in tag_names
        assert "urgent" in tag_names

    def test_update_password_entry_invalid_master_password(self, authenticated_client, password_entry):
        update_data = {
            "name": "Should Fail",
            "master_password": "WrongPassword123!",
        }

        response = authenticated_client.put(
            f"/api/passwords/entries/{password_entry.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "master password" in response.json()["detail"].lower()

    def test_update_password_entry_not_found(self, authenticated_client, test_password):
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {
            "name": "Should Fail",
            "master_password": test_password,
        }

        response = authenticated_client.put(
            f"/api/passwords/entries/{fake_id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_update_password_entry_from_another_user(self, authenticated_client, multiple_users, test_password):
        other_user = multiple_users[0]
        entry = PasswordEntry.objects.create(
            user=other_user,
            name="Other User Entry",
            site="https://other.com",
            username="other",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )

        update_data = {
            "name": "Should Fail",
            "master_password": test_password,
        }

        response = authenticated_client.put(
            f"/api/passwords/entries/{entry.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_update_password_entry_without_authentication(self, api_client, user, test_password):
        entry = PasswordEntry.objects.create(
            user=user,
            name="Test Entry",
            site="https://test.com",
            username="user",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )

        update_data = {
            "name": "Should Fail",
            "master_password": test_password,
        }

        response = api_client.put(
            f"/api/passwords/entries/{entry.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_update_password_entry_logs_access(self, authenticated_client, password_entry, test_password):
        update_data = {
            "name": "Updated Name",
            "master_password": test_password,
        }

        response = authenticated_client.put(
            f"/api/passwords/entries/{password_entry.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200

        log = PasswordAccessLog.objects.filter(
            password_entry=password_entry,
            action="update",
        ).first()
        assert log is not None

    def test_update_password_entry_with_expiration(self, authenticated_client, password_entry, test_password):
        new_expiry = (timezone.now() + timedelta(days=60)).isoformat()
        update_data = {
            "expires_at": new_expiry,
            "master_password": test_password,
        }

        response = authenticated_client.put(
            f"/api/passwords/entries/{password_entry.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["expires_at"] is not None


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordEntryDelete:

    def test_delete_password_entry_success(self, authenticated_client, user):
        entry = PasswordEntry.objects.create(
            user=user,
            name="To Delete",
            site="https://delete.com",
            username="user",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )
        entry_id = entry.id

        response = authenticated_client.delete(f"/api/passwords/entries/{entry_id}")

        assert response.status_code == 204
        assert not PasswordEntry.objects.filter(id=entry_id).exists()

    def test_delete_password_entry_not_found(self, authenticated_client):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = authenticated_client.delete(f"/api/passwords/entries/{fake_id}")

        assert response.status_code == 404

    def test_delete_password_entry_from_another_user(self, authenticated_client, multiple_users):
        other_user = multiple_users[0]
        entry = PasswordEntry.objects.create(
            user=other_user,
            name="Other User Entry",
            site="https://other.com",
            username="other",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )

        response = authenticated_client.delete(f"/api/passwords/entries/{entry.id}")

        assert response.status_code == 404
        assert PasswordEntry.objects.filter(id=entry.id).exists()

    def test_delete_password_entry_without_authentication(self, api_client, user):
        entry = PasswordEntry.objects.create(
            user=user,
            name="Test Entry",
            site="https://test.com",
            username="user",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )

        response = api_client.delete(f"/api/passwords/entries/{entry.id}")

        assert response.status_code == 401
        assert PasswordEntry.objects.filter(id=entry.id).exists()

    def test_delete_password_entry_logs_access(self, authenticated_client, user):
        entry = PasswordEntry.objects.create(
            user=user,
            name="To Delete",
            site="https://delete.com",
            username="user",
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )
        entry_id = entry.id

        response = authenticated_client.delete(f"/api/passwords/entries/{entry_id}")

        assert response.status_code == 204
