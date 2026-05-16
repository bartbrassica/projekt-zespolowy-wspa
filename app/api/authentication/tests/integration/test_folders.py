"""
Integration tests for folder management - CRUD, nested folders, hierarchy.
"""

import pytest
import json


@pytest.mark.integration
@pytest.mark.django_db
class TestFolderCreate:

    def test_create_folder_success(self, authenticated_client, user):
        folder_data = {
            "name": "Work",
            "icon": "briefcase",
            "color": "#FF0000",
        }

        response = authenticated_client.post(
            "/api/passwords/folders",
            data=json.dumps(folder_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Work"
        assert data["icon"] == "briefcase"
        assert data["color"] == "#FF0000"
        assert "id" in data

    def test_create_folder_minimal_data(self, authenticated_client, user):
        folder_data = {
            "name": "Personal",
        }

        response = authenticated_client.post(
            "/api/passwords/folders",
            data=json.dumps(folder_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Personal"

    def test_create_folder_with_parent(self, authenticated_client, user, password_folder):
        folder_data = {
            "name": "Subfolder",
            "parent_id": str(password_folder.id),
        }

        response = authenticated_client.post(
            "/api/passwords/folders",
            data=json.dumps(folder_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Subfolder"
        assert data["parent_id"] == str(password_folder.id)

    def test_create_folder_without_authentication(self, api_client):
        folder_data = {
            "name": "Test Folder",
        }

        response = api_client.post(
            "/api/passwords/folders",
            data=json.dumps(folder_data),
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_create_folder_missing_name(self, authenticated_client):
        folder_data = {
            "icon": "folder",
        }

        response = authenticated_client.post(
            "/api/passwords/folders",
            data=json.dumps(folder_data),
            content_type="application/json",
        )

        assert response.status_code == 422

    def test_create_folder_empty_name(self, authenticated_client):
        folder_data = {
            "name": "",
        }

        response = authenticated_client.post(
            "/api/passwords/folders",
            data=json.dumps(folder_data),
            content_type="application/json",
        )

        assert response.status_code == 422

    def test_create_folder_duplicate_name(self, authenticated_client, user, password_folder):
        folder_data = {
            "name": password_folder.name,
        }

        response = authenticated_client.post(
            "/api/passwords/folders",
            data=json.dumps(folder_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_create_folder_invalid_parent(self, authenticated_client):
        folder_data = {
            "name": "Test Folder",
            "parent_id": "00000000-0000-0000-0000-000000000000",
        }

        response = authenticated_client.post(
            "/api/passwords/folders",
            data=json.dumps(folder_data),
            content_type="application/json",
        )

        assert response.status_code == 400

    def test_create_folder_invalid_color(self, authenticated_client):
        folder_data = {
            "name": "Test Folder",
            "color": "invalid",
        }

        response = authenticated_client.post(
            "/api/passwords/folders",
            data=json.dumps(folder_data),
            content_type="application/json",
        )

        assert response.status_code == 422

    def test_create_folder_valid_hex_colors(self, authenticated_client):
        colors = ["#000000", "#FFFFFF", "#FF5733", "#C0FFEE"]

        for i, color in enumerate(colors):
            folder_data = {
                "name": f"Folder {i}",
                "color": color,
            }

            response = authenticated_client.post(
                "/api/passwords/folders",
                data=json.dumps(folder_data),
                content_type="application/json",
            )

            assert response.status_code == 201
            assert response.json()["color"] == color


@pytest.mark.integration
@pytest.mark.django_db
class TestFolderList:

    def test_list_folders_success(self, authenticated_client, user):
        from authentication.models import PasswordFolder

        PasswordFolder.objects.create(user=user, name="Folder 1")
        PasswordFolder.objects.create(user=user, name="Folder 2")
        PasswordFolder.objects.create(user=user, name="Folder 3")

        response = authenticated_client.get("/api/passwords/folders")

        assert response.status_code == 200

    def test_list_folders_empty(self, authenticated_client, user):
        response = authenticated_client.get("/api/passwords/folders")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_list_folders_with_entry_count(self, authenticated_client, user, password_folder):
        from authentication.models import PasswordEntry

        PasswordEntry.objects.create(
            user=user,
            name="Entry 1",
            folder=password_folder,
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )
        PasswordEntry.objects.create(
            user=user,
            name="Entry 2",
            folder=password_folder,
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )

        response = authenticated_client.get("/api/passwords/folders")

        assert response.status_code == 200

        password_folder.refresh_from_db()
        assert password_folder.entry_count == 2

    def test_list_folders_sorted_by_name(self, authenticated_client, user):
        from authentication.models import PasswordFolder

        PasswordFolder.objects.create(user=user, name="Zebra")
        PasswordFolder.objects.create(user=user, name="Apple")
        PasswordFolder.objects.create(user=user, name="Mango")

        response = authenticated_client.get("/api/passwords/folders")

        assert response.status_code == 200

    def test_list_folders_user_isolation(self, authenticated_client, user, multiple_users):
        from authentication.models import PasswordFolder

        PasswordFolder.objects.create(user=user, name="My Folder")
        PasswordFolder.objects.create(user=multiple_users[0], name="Other Folder")

        from django.test import RequestFactory
        from authentication.password_endpoints import list_folders

        factory = RequestFactory()
        request = factory.get("/api/passwords/folders")
        request.auth = user

        folders = list_folders(request)

        assert len(folders) == 1
        assert folders[0].name == "My Folder"

    def test_list_folders_without_authentication(self, api_client):
        response = api_client.get("/api/passwords/folders")

        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.django_db
class TestFolderUpdate:

    def test_update_folder_name(self, authenticated_client, password_folder):
        update_data = {
            "name": "Updated Name",
        }

        response = authenticated_client.put(
            f"/api/passwords/folders/{password_folder.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_update_folder_icon(self, authenticated_client, password_folder):
        update_data = {
            "icon": "star",
        }

        response = authenticated_client.put(
            f"/api/passwords/folders/{password_folder.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["icon"] == "star"

    def test_update_folder_color(self, authenticated_client, password_folder):
        update_data = {
            "color": "#00FF00",
        }

        response = authenticated_client.put(
            f"/api/passwords/folders/{password_folder.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["color"] == "#00FF00"

    def test_update_folder_multiple_fields(self, authenticated_client, password_folder):
        update_data = {
            "name": "New Name",
            "icon": "lock",
            "color": "#0000FF",
        }

        response = authenticated_client.put(
            f"/api/passwords/folders/{password_folder.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["icon"] == "lock"
        assert data["color"] == "#0000FF"

    def test_update_folder_not_found(self, authenticated_client):
        update_data = {
            "name": "Updated",
        }

        response = authenticated_client.put(
            "/api/passwords/folders/00000000-0000-0000-0000-000000000000",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_update_folder_other_user(self, authenticated_client, multiple_users):
        from authentication.models import PasswordFolder

        other_folder = PasswordFolder.objects.create(
            user=multiple_users[0],
            name="Other User Folder",
        )

        update_data = {
            "name": "Hacked",
        }

        response = authenticated_client.put(
            f"/api/passwords/folders/{other_folder.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_update_folder_without_authentication(self, api_client, password_folder):
        update_data = {
            "name": "Updated",
        }

        response = api_client.put(
            f"/api/passwords/folders/{password_folder.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.django_db
class TestFolderDelete:

    def test_delete_folder_success(self, authenticated_client, user):
        from authentication.models import PasswordFolder

        folder = PasswordFolder.objects.create(user=user, name="To Delete")
        folder_id = folder.id

        response = authenticated_client.delete(f"/api/passwords/folders/{folder_id}")

        assert response.status_code == 204
        assert not PasswordFolder.objects.filter(id=folder_id).exists()

    def test_delete_folder_moves_entries_to_root(self, authenticated_client, user):
        from authentication.models import PasswordFolder, PasswordEntry

        folder = PasswordFolder.objects.create(user=user, name="To Delete")
        entry = PasswordEntry.objects.create(
            user=user,
            name="Entry in Folder",
            folder=folder,
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )

        authenticated_client.delete(f"/api/passwords/folders/{folder.id}")

        entry.refresh_from_db()
        assert entry.folder is None

    def test_delete_folder_moves_subfolders_to_root(self, authenticated_client, user):
        from authentication.models import PasswordFolder

        parent = PasswordFolder.objects.create(user=user, name="Parent")
        child = PasswordFolder.objects.create(user=user, name="Child", parent=parent)

        authenticated_client.delete(f"/api/passwords/folders/{parent.id}")

        child.refresh_from_db()
        assert child.parent is None

    def test_delete_folder_not_found(self, authenticated_client):
        response = authenticated_client.delete(
            "/api/passwords/folders/00000000-0000-0000-0000-000000000000"
        )

        assert response.status_code == 404

    def test_delete_folder_other_user(self, authenticated_client, multiple_users):
        from authentication.models import PasswordFolder

        other_folder = PasswordFolder.objects.create(
            user=multiple_users[0],
            name="Other User Folder",
        )

        response = authenticated_client.delete(f"/api/passwords/folders/{other_folder.id}")

        assert response.status_code == 404
        assert PasswordFolder.objects.filter(id=other_folder.id).exists()

    def test_delete_folder_without_authentication(self, api_client, password_folder):
        response = api_client.delete(f"/api/passwords/folders/{password_folder.id}")

        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.django_db
class TestNestedFolders:

    def test_create_nested_folder(self, authenticated_client, user):
        from authentication.models import PasswordFolder

        parent = PasswordFolder.objects.create(user=user, name="Parent")

        child_data = {
            "name": "Child",
            "parent_id": str(parent.id),
        }

        response = authenticated_client.post(
            "/api/passwords/folders",
            data=json.dumps(child_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()
        assert data["parent_id"] == str(parent.id)

    def test_create_three_level_hierarchy(self, authenticated_client, user):
        from authentication.models import PasswordFolder

        level1 = PasswordFolder.objects.create(user=user, name="Level 1")
        level2 = PasswordFolder.objects.create(
            user=user, name="Level 2", parent=level1
        )

        level3_data = {
            "name": "Level 3",
            "parent_id": str(level2.id),
        }

        response = authenticated_client.post(
            "/api/passwords/folders",
            data=json.dumps(level3_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()
        assert data["parent_id"] == str(level2.id)

    def test_move_folder_to_different_parent(self, authenticated_client, user):
        from authentication.models import PasswordFolder

        parent1 = PasswordFolder.objects.create(user=user, name="Parent 1")
        parent2 = PasswordFolder.objects.create(user=user, name="Parent 2")
        child = PasswordFolder.objects.create(
            user=user, name="Child", parent=parent1
        )

        update_data = {
            "parent_id": str(parent2.id),
        }

        response = authenticated_client.put(
            f"/api/passwords/folders/{child.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["parent_id"] == str(parent2.id)

    def test_move_folder_to_root(self, authenticated_client, user):
        from authentication.models import PasswordFolder

        parent = PasswordFolder.objects.create(user=user, name="Parent")
        child = PasswordFolder.objects.create(
            user=user, name="Child", parent=parent
        )

        update_data = {
            "parent_id": "",
        }

        response = authenticated_client.put(
            f"/api/passwords/folders/{child.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["parent_id"] is None

    def test_cannot_move_folder_to_itself(self, authenticated_client, password_folder):
        update_data = {
            "parent_id": str(password_folder.id),
        }

        response = authenticated_client.put(
            f"/api/passwords/folders/{password_folder.id}",
            data=json.dumps(update_data),
            content_type="application/json",
        )

        assert response.status_code == 200
        password_folder.refresh_from_db()
        assert password_folder.parent is None

    def test_list_folders_with_hierarchy(self, authenticated_client, user):
        from authentication.models import PasswordFolder

        parent = PasswordFolder.objects.create(user=user, name="Parent")
        PasswordFolder.objects.create(user=user, name="Child 1", parent=parent)
        PasswordFolder.objects.create(user=user, name="Child 2", parent=parent)
        PasswordFolder.objects.create(user=user, name="Root Folder")

        from django.test import RequestFactory
        from authentication.password_endpoints import list_folders

        factory = RequestFactory()
        request = factory.get("/api/passwords/folders")
        request.auth = user

        folders = list_folders(request)

        assert len(folders) == 4

    def test_duplicate_name_different_parents(self, authenticated_client, user):
        from authentication.models import PasswordFolder

        parent1 = PasswordFolder.objects.create(user=user, name="Parent 1")
        parent2 = PasswordFolder.objects.create(user=user, name="Parent 2")

        child1_data = {
            "name": "Child",
            "parent_id": str(parent1.id),
        }
        response1 = authenticated_client.post(
            "/api/passwords/folders",
            data=json.dumps(child1_data),
            content_type="application/json",
        )

        child2_data = {
            "name": "Child",
            "parent_id": str(parent2.id),
        }
        response2 = authenticated_client.post(
            "/api/passwords/folders",
            data=json.dumps(child2_data),
            content_type="application/json",
        )

        assert response1.status_code == 201
        assert response2.status_code == 201

    def test_duplicate_name_same_parent(self, authenticated_client, user):
        from authentication.models import PasswordFolder

        parent = PasswordFolder.objects.create(user=user, name="Parent")

        child1_data = {
            "name": "Child",
            "parent_id": str(parent.id),
        }
        response1 = authenticated_client.post(
            "/api/passwords/folders",
            data=json.dumps(child1_data),
            content_type="application/json",
        )

        child2_data = {
            "name": "Child",
            "parent_id": str(parent.id),
        }
        response2 = authenticated_client.post(
            "/api/passwords/folders",
            data=json.dumps(child2_data),
            content_type="application/json",
        )

        assert response1.status_code == 201
        assert response2.status_code == 400


@pytest.mark.integration
@pytest.mark.django_db
class TestFolderHierarchy:

    def test_folder_with_entries_in_hierarchy(self, authenticated_client, user):
        from authentication.models import PasswordFolder, PasswordEntry

        parent = PasswordFolder.objects.create(user=user, name="Parent")
        child = PasswordFolder.objects.create(user=user, name="Child", parent=parent)

        PasswordEntry.objects.create(
            user=user,
            name="Entry in Parent",
            folder=parent,
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )
        PasswordEntry.objects.create(
            user=user,
            name="Entry in Child",
            folder=child,
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )

        from django.test import RequestFactory
        from authentication.password_endpoints import list_folders

        factory = RequestFactory()
        request = factory.get("/api/passwords/folders")
        request.auth = user

        folders = list_folders(request)

        parent_folder = next(f for f in folders if str(f.id) == str(parent.id))
        child_folder = next(f for f in folders if str(f.id) == str(child.id))

        assert parent_folder.entry_count == 1
        assert child_folder.entry_count == 1

    def test_delete_parent_folder_preserves_entries(self, authenticated_client, user):
        from authentication.models import PasswordFolder, PasswordEntry

        parent = PasswordFolder.objects.create(user=user, name="Parent")
        child = PasswordFolder.objects.create(user=user, name="Child", parent=parent)

        entry1 = PasswordEntry.objects.create(
            user=user,
            name="Entry 1",
            folder=parent,
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )
        entry2 = PasswordEntry.objects.create(
            user=user,
            name="Entry 2",
            folder=child,
            encrypted_password="encrypted",
            encryption_salt=b"salt",
        )

        authenticated_client.delete(f"/api/passwords/folders/{parent.id}")

        entry1.refresh_from_db()
        entry2.refresh_from_db()

        assert entry1.folder is None
        assert entry2.folder.id == child.id

    def test_complex_hierarchy(self, authenticated_client, user):
        from authentication.models import PasswordFolder

        root1 = PasswordFolder.objects.create(user=user, name="Root 1")
        root2 = PasswordFolder.objects.create(user=user, name="Root 2")

        child1_1 = PasswordFolder.objects.create(user=user, name="Child 1-1", parent=root1)
        PasswordFolder.objects.create(user=user, name="Child 1-2", parent=root1)
        PasswordFolder.objects.create(user=user, name="Child 2-1", parent=root2)
        PasswordFolder.objects.create(user=user, name="Grandchild", parent=child1_1)

        from django.test import RequestFactory
        from authentication.password_endpoints import list_folders

        factory = RequestFactory()
        request = factory.get("/api/passwords/folders")
        request.auth = user

        folders = list_folders(request)

        assert len(folders) == 6

    def test_folder_name_max_length(self, authenticated_client):
        folder_data = {
            "name": "A" * 100,
        }

        response = authenticated_client.post(
            "/api/passwords/folders",
            data=json.dumps(folder_data),
            content_type="application/json",
        )

        assert response.status_code == 201

    def test_folder_name_too_long(self, authenticated_client):
        folder_data = {
            "name": "A" * 101,
        }

        response = authenticated_client.post(
            "/api/passwords/folders",
            data=json.dumps(folder_data),
            content_type="application/json",
        )

        assert response.status_code == 422
