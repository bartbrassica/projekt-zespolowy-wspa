"""
Unit tests for PasswordFolder model.

Tests cover:
- PasswordFolder creation (CRUD operations)
- Folder hierarchy (parent-child relationships)
- Properties (entry_count, full_path)
- Unique constraints
"""

import pytest
from django.db.utils import IntegrityError

from authentication.models import PasswordFolder
from tests.fixtures.factories import (
    UserFactory,
    PasswordFolderFactory,
    PasswordEntryFactory,
)


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordFolderCreation:
    """Tests for PasswordFolder model creation (CRUD)."""

    def test_create_folder(self, user):
        """Test creating a basic folder."""
        folder = PasswordFolder.objects.create(
            user=user,
            name="Work Passwords",
            icon="briefcase",
            color="#FF5733",
        )

        assert folder.user == user
        assert folder.name == "Work Passwords"
        assert folder.icon == "briefcase"
        assert folder.color == "#FF5733"
        assert folder.parent is None

    def test_create_folder_with_factory(self, user):
        """Test creating folder with factory."""
        folder = PasswordFolderFactory(user=user)
        assert folder.user == user
        assert folder.name is not None

    def test_folder_id_is_uuid(self):
        """Test that folder ID is UUID."""
        folder = PasswordFolderFactory()
        assert folder.id is not None
        assert len(str(folder.id)) == 36  # UUID format

    def test_create_folder_minimal_fields(self, user):
        """Test creating folder with minimal required fields."""
        folder = PasswordFolder.objects.create(
            user=user,
            name="Minimal Folder",
        )

        assert folder.user == user
        assert folder.name == "Minimal Folder"
        assert folder.icon == ""
        assert folder.color == ""
        assert folder.parent is None

    def test_read_folder(self, password_folder):
        """Test reading a folder."""
        retrieved = PasswordFolder.objects.get(id=password_folder.id)
        assert retrieved.id == password_folder.id
        assert retrieved.name == password_folder.name
        assert retrieved.user == password_folder.user

    def test_update_folder(self, password_folder):
        """Test updating a folder."""
        password_folder.name = "Updated Folder"
        password_folder.icon = "new-icon"
        password_folder.save()

        updated = PasswordFolder.objects.get(id=password_folder.id)
        assert updated.name == "Updated Folder"
        assert updated.icon == "new-icon"

    def test_delete_folder(self, password_folder):
        """Test deleting a folder."""
        folder_id = password_folder.id
        password_folder.delete()

        assert PasswordFolder.objects.filter(id=folder_id).count() == 0

    def test_created_at_auto_set(self):
        """Test that created_at is automatically set."""
        folder = PasswordFolderFactory()
        assert folder.created_at is not None

    def test_updated_at_auto_set(self):
        """Test that updated_at is automatically set and updates."""
        folder = PasswordFolderFactory()
        original_updated_at = folder.updated_at

        folder.name = "Updated Name"
        folder.save()

        assert folder.updated_at >= original_updated_at


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordFolderHierarchy:
    """Tests for folder hierarchy (parent-child relationships)."""

    def test_create_subfolder(self, user):
        """Test creating a subfolder."""
        parent = PasswordFolderFactory(user=user, name="Parent")
        child = PasswordFolderFactory(user=user, name="Child", parent=parent)

        assert child.parent == parent
        assert child in parent.subfolders.all()

    def test_create_nested_folders(self, user):
        """Test creating nested folder structure."""
        grandparent = PasswordFolderFactory(user=user, name="Grandparent")
        parent = PasswordFolderFactory(
            user=user, name="Parent", parent=grandparent
        )
        child = PasswordFolderFactory(user=user, name="Child", parent=parent)

        assert parent.parent == grandparent
        assert child.parent == parent
        assert parent in grandparent.subfolders.all()
        assert child in parent.subfolders.all()

    def test_folder_without_parent(self):
        """Test folder without parent (root folder)."""
        folder = PasswordFolderFactory(parent=None)
        assert folder.parent is None

    def test_deleting_parent_deletes_children(self, user):
        """Test that deleting parent folder cascades to children."""
        parent = PasswordFolderFactory(user=user)
        child1 = PasswordFolderFactory(user=user, parent=parent)
        child2 = PasswordFolderFactory(user=user, parent=parent)
        child_ids = [child1.id, child2.id]

        parent.delete()

        assert PasswordFolder.objects.filter(id__in=child_ids).count() == 0

    def test_subfolders_related_name(self, user):
        """Test accessing subfolders via related name."""
        parent = PasswordFolderFactory(user=user)
        child1 = PasswordFolderFactory(user=user, parent=parent)
        child2 = PasswordFolderFactory(user=user, parent=parent)

        assert parent.subfolders.count() == 2
        assert child1 in parent.subfolders.all()
        assert child2 in parent.subfolders.all()


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordFolderProperties:
    """Tests for folder properties."""

    def test_entry_count_empty_folder(self, user):
        """Test entry_count for empty folder."""
        folder = PasswordFolderFactory(user=user)
        assert folder.entry_count == 0

    def test_entry_count_with_entries(self, user):
        """Test entry_count with entries."""
        folder = PasswordFolderFactory(user=user)
        PasswordEntryFactory(user=user, folder=folder)
        PasswordEntryFactory(user=user, folder=folder)
        PasswordEntryFactory(user=user, folder=folder)

        assert folder.entry_count == 3

    def test_entry_count_after_adding_entry(self, user):
        """Test entry_count after adding entry."""
        folder = PasswordFolderFactory(user=user)
        assert folder.entry_count == 0

        PasswordEntryFactory(user=user, folder=folder)

        assert folder.entry_count == 1

    def test_entry_count_after_removing_entry(self, user):
        """Test entry_count after removing entry."""
        folder = PasswordFolderFactory(user=user)
        entry = PasswordEntryFactory(user=user, folder=folder)

        assert folder.entry_count == 1

        entry.folder = None
        entry.save()

        assert folder.entry_count == 0

    def test_full_path_root_folder(self, user):
        """Test full_path for root folder."""
        folder = PasswordFolderFactory(user=user, name="Root", parent=None)
        assert folder.full_path == "Root"

    def test_full_path_subfolder(self, user):
        """Test full_path for subfolder."""
        parent = PasswordFolderFactory(user=user, name="Parent", parent=None)
        child = PasswordFolderFactory(user=user, name="Child", parent=parent)

        assert child.full_path == "Parent/Child"

    def test_full_path_nested_folders(self, user):
        """Test full_path for nested folders."""
        grandparent = PasswordFolderFactory(
            user=user, name="Grandparent", parent=None
        )
        parent = PasswordFolderFactory(
            user=user, name="Parent", parent=grandparent
        )
        child = PasswordFolderFactory(user=user, name="Child", parent=parent)

        assert child.full_path == "Grandparent/Parent/Child"

    def test_full_path_with_special_characters(self, user):
        """Test full_path with special characters in names."""
        parent = PasswordFolderFactory(
            user=user, name="Parent & Work", parent=None
        )
        child = PasswordFolderFactory(
            user=user, name="Child/Test", parent=parent
        )

        assert child.full_path == "Parent & Work/Child/Test"


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordFolderRelationships:
    """Tests for folder relationships."""

    def test_folder_belongs_to_user(self, password_folder, user):
        """Test that folder belongs to a user."""
        assert password_folder.user == user

    def test_user_can_have_multiple_folders(self, user):
        """Test that user can have multiple folders."""
        folder1 = PasswordFolderFactory(user=user)
        folder2 = PasswordFolderFactory(user=user)
        folder3 = PasswordFolderFactory(user=user)

        user_folders = user.password_folders.all()
        assert user_folders.count() == 3
        assert folder1 in user_folders
        assert folder2 in user_folders
        assert folder3 in user_folders

    def test_deleting_user_deletes_folders(self, user):
        """Test that deleting user cascades to folders."""
        folder1 = PasswordFolderFactory(user=user)
        folder2 = PasswordFolderFactory(user=user)
        folder_ids = [folder1.id, folder2.id]

        user.delete()

        assert PasswordFolder.objects.filter(id__in=folder_ids).count() == 0

    def test_folder_with_entries(self, user):
        """Test folder with entries relationship."""
        folder = PasswordFolderFactory(user=user)
        entry1 = PasswordEntryFactory(user=user, folder=folder)
        entry2 = PasswordEntryFactory(user=user, folder=folder)

        assert folder.entries.count() == 2
        assert entry1 in folder.entries.all()
        assert entry2 in folder.entries.all()


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordFolderStringRepresentation:
    """Tests for folder string representation."""

    def test_folder_str_representation(self, user):
        """Test string representation of folder."""
        folder = PasswordFolderFactory(user=user, name="My Folder")
        expected = f"My Folder - {user.email}"
        assert str(folder) == expected


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordFolderMetaOptions:
    """Tests for PasswordFolder model Meta options."""

    def test_folder_table_name(self):
        """Test that folder table name is correct."""
        assert PasswordFolder._meta.db_table == "password_folders"

    def test_folder_ordering(self):
        """Test that folders are ordered by name."""
        user = UserFactory()
        PasswordFolderFactory(user=user, name="Zebra")
        PasswordFolderFactory(user=user, name="Alpha")
        PasswordFolderFactory(user=user, name="Beta")

        folders = PasswordFolder.objects.filter(user=user)
        names = [f.name for f in folders]
        assert names == sorted(names)

    def test_unique_together_constraint(self, user):
        """Test that user, name, and parent must be unique together."""
        parent = PasswordFolderFactory(user=user, name="Parent")

        PasswordFolder.objects.create(
            user=user, name="Duplicate", parent=parent
        )

        with pytest.raises(IntegrityError):
            PasswordFolder.objects.create(
                user=user, name="Duplicate", parent=parent
            )

    def test_same_name_different_parents_allowed(self, user):
        """Test that same name in different parents is allowed."""
        parent1 = PasswordFolderFactory(user=user, name="Parent1")
        parent2 = PasswordFolderFactory(user=user, name="Parent2")

        folder1 = PasswordFolder.objects.create(
            user=user, name="Same Name", parent=parent1
        )
        folder2 = PasswordFolder.objects.create(
            user=user, name="Same Name", parent=parent2
        )

        assert folder1.name == folder2.name
        assert folder1.parent != folder2.parent

    def test_different_users_can_have_same_folder_name(self):
        """Test that different users can have folders with same name."""
        user1 = UserFactory()
        user2 = UserFactory()

        folder1 = PasswordFolder.objects.create(
            user=user1, name="Same Folder"
        )
        folder2 = PasswordFolder.objects.create(
            user=user2, name="Same Folder"
        )

        assert folder1.name == folder2.name
        assert folder1.user != folder2.user


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordFolderQuerySets:
    """Tests for folder querysets and filtering."""

    def test_filter_folders_by_user(self):
        """Test filtering folders by user."""
        user1 = UserFactory()
        user2 = UserFactory()

        PasswordFolderFactory(user=user1)
        PasswordFolderFactory(user=user1)
        PasswordFolderFactory(user=user2)

        user1_folders = PasswordFolder.objects.filter(user=user1)
        assert user1_folders.count() == 2

    def test_filter_root_folders(self, user):
        """Test filtering root folders (no parent)."""
        root1 = PasswordFolderFactory(user=user, parent=None)
        root2 = PasswordFolderFactory(user=user, parent=None)
        child = PasswordFolderFactory(user=user, parent=root1)

        root_folders = PasswordFolder.objects.filter(user=user, parent=None)
        assert root_folders.count() == 2
        assert root1 in root_folders
        assert root2 in root_folders
        assert child not in root_folders

    def test_filter_folders_by_parent(self, user):
        """Test filtering folders by parent."""
        parent = PasswordFolderFactory(user=user)
        child1 = PasswordFolderFactory(user=user, parent=parent)
        child2 = PasswordFolderFactory(user=user, parent=parent)
        PasswordFolderFactory(user=user, parent=None)

        children = PasswordFolder.objects.filter(parent=parent)
        assert children.count() == 2
        assert child1 in children
        assert child2 in children

    def test_filter_empty_folders(self, user):
        """Test filtering folders with no entries."""
        empty1 = PasswordFolderFactory(user=user)
        empty2 = PasswordFolderFactory(user=user)
        with_entries = PasswordFolderFactory(user=user)
        PasswordEntryFactory(user=user, folder=with_entries)

        all_folders = PasswordFolder.objects.filter(user=user)
        empty_folders = [f for f in all_folders if f.entry_count == 0]
        assert len(empty_folders) == 2


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordFolderEdgeCases:
    """Tests for folder edge cases."""

    def test_folder_with_long_name(self, user):
        """Test folder with long name (up to 100 chars)."""
        long_name = "A" * 100
        folder = PasswordFolder.objects.create(user=user, name=long_name)
        assert folder.name == long_name

    def test_folder_with_emoji_name(self, user):
        """Test folder with emoji in name."""
        folder = PasswordFolder.objects.create(
            user=user, name="Work 💼"
        )
        assert folder.name == "Work 💼"

    def test_folder_color_validation(self, user):
        """Test folder color field accepts hex colors."""
        folder = PasswordFolder.objects.create(
            user=user,
            name="Color Test",
            color="#FF5733",
        )
        assert folder.color == "#FF5733"

    def test_deep_folder_nesting(self, user):
        """Test deep folder nesting."""
        level1 = PasswordFolderFactory(user=user, name="Level1")
        level2 = PasswordFolderFactory(user=user, name="Level2", parent=level1)
        level3 = PasswordFolderFactory(user=user, name="Level3", parent=level2)
        level4 = PasswordFolderFactory(user=user, name="Level4", parent=level3)
        level5 = PasswordFolderFactory(user=user, name="Level5", parent=level4)

        expected_path = "Level1/Level2/Level3/Level4/Level5"
        assert level5.full_path == expected_path
