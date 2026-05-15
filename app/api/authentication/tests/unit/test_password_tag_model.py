"""
Unit tests for PasswordTag model.

Tests cover:
- PasswordTag creation (CRUD operations)
- Tag properties (entry_count)
- Unique constraints
- Tag-entry relationships
"""

import pytest
from django.db.utils import IntegrityError

from authentication.models import PasswordTag
from tests.fixtures.factories import (
    UserFactory,
    PasswordTagFactory,
    PasswordEntryFactory,
)


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordTagCreation:
    """Tests for PasswordTag model creation (CRUD)."""

    def test_create_tag(self, user):
        """Test creating a basic tag."""
        tag = PasswordTag.objects.create(
            user=user,
            name="work",
            color="#FF5733",
        )

        assert tag.user == user
        assert tag.name == "work"
        assert tag.color == "#FF5733"

    def test_create_tag_with_factory(self, user):
        """Test creating tag with factory."""
        tag = PasswordTagFactory(user=user)
        assert tag.user == user
        assert tag.name is not None

    def test_tag_id_is_uuid(self):
        """Test that tag ID is UUID."""
        tag = PasswordTagFactory()
        assert tag.id is not None
        assert len(str(tag.id)) == 36  # UUID format

    def test_create_tag_minimal_fields(self, user):
        """Test creating tag with minimal required fields."""
        tag = PasswordTag.objects.create(
            user=user,
            name="minimal",
        )

        assert tag.user == user
        assert tag.name == "minimal"
        assert tag.color == ""

    def test_read_tag(self, password_tag):
        """Test reading a tag."""
        retrieved = PasswordTag.objects.get(id=password_tag.id)
        assert retrieved.id == password_tag.id
        assert retrieved.name == password_tag.name
        assert retrieved.user == password_tag.user

    def test_update_tag(self, password_tag):
        """Test updating a tag."""
        password_tag.name = "updated-tag"
        password_tag.color = "#00FF00"
        password_tag.save()

        updated = PasswordTag.objects.get(id=password_tag.id)
        assert updated.name == "updated-tag"
        assert updated.color == "#00FF00"

    def test_delete_tag(self, password_tag):
        """Test deleting a tag."""
        tag_id = password_tag.id
        password_tag.delete()

        assert PasswordTag.objects.filter(id=tag_id).count() == 0

    def test_created_at_auto_set(self):
        """Test that created_at is automatically set."""
        tag = PasswordTagFactory()
        assert tag.created_at is not None


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordTagProperties:
    """Tests for tag properties."""

    def test_entry_count_no_entries(self, user):
        """Test entry_count with no entries."""
        tag = PasswordTagFactory(user=user)
        assert tag.entry_count == 0

    def test_entry_count_with_entries(self, user):
        """Test entry_count with entries."""
        tag = PasswordTagFactory(user=user)
        entry1 = PasswordEntryFactory(user=user)
        entry2 = PasswordEntryFactory(user=user)
        entry3 = PasswordEntryFactory(user=user)

        entry1.tags.add(tag)
        entry2.tags.add(tag)
        entry3.tags.add(tag)

        assert tag.entry_count == 3

    def test_entry_count_after_adding_entry(self, user):
        """Test entry_count after adding entry."""
        tag = PasswordTagFactory(user=user)
        entry = PasswordEntryFactory(user=user)

        assert tag.entry_count == 0

        entry.tags.add(tag)

        assert tag.entry_count == 1

    def test_entry_count_after_removing_entry(self, user):
        """Test entry_count after removing entry."""
        tag = PasswordTagFactory(user=user)
        entry = PasswordEntryFactory(user=user)
        entry.tags.add(tag)

        assert tag.entry_count == 1

        entry.tags.remove(tag)

        assert tag.entry_count == 0


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordTagRelationships:
    """Tests for tag relationships."""

    def test_tag_belongs_to_user(self, password_tag, user):
        """Test that tag belongs to a user."""
        assert password_tag.user == user

    def test_user_can_have_multiple_tags(self, user):
        """Test that user can have multiple tags."""
        tag1 = PasswordTagFactory(user=user)
        tag2 = PasswordTagFactory(user=user)
        tag3 = PasswordTagFactory(user=user)

        user_tags = user.password_tags.all()
        assert user_tags.count() == 3
        assert tag1 in user_tags
        assert tag2 in user_tags
        assert tag3 in user_tags

    def test_deleting_user_deletes_tags(self, user):
        """Test that deleting user cascades to tags."""
        tag1 = PasswordTagFactory(user=user)
        tag2 = PasswordTagFactory(user=user)
        tag_ids = [tag1.id, tag2.id]

        user.delete()

        assert PasswordTag.objects.filter(id__in=tag_ids).count() == 0

    def test_tag_with_multiple_entries(self, user):
        """Test tag with multiple entries."""
        tag = PasswordTagFactory(user=user)
        entry1 = PasswordEntryFactory(user=user)
        entry2 = PasswordEntryFactory(user=user)

        entry1.tags.add(tag)
        entry2.tags.add(tag)

        assert tag.entries.count() == 2
        assert entry1 in tag.entries.all()
        assert entry2 in tag.entries.all()

    def test_deleting_tag_preserves_entries(self, user):
        """Test that deleting tag doesn't delete entries."""
        tag = PasswordTagFactory(user=user)
        entry = PasswordEntryFactory(user=user)
        entry.tags.add(tag)

        entry_id = entry.id
        tag.delete()

        # Entry should still exist
        assert PasswordEntryFactory._meta.model.objects.filter(
            id=entry_id
        ).exists()

    def test_entry_can_have_multiple_tags(self, user):
        """Test that entry can have multiple tags."""
        entry = PasswordEntryFactory(user=user)
        tag1 = PasswordTagFactory(user=user)
        tag2 = PasswordTagFactory(user=user)
        tag3 = PasswordTagFactory(user=user)

        entry.tags.add(tag1, tag2, tag3)

        assert entry.tags.count() == 3
        assert tag1 in entry.tags.all()
        assert tag2 in entry.tags.all()
        assert tag3 in entry.tags.all()


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordTagStringRepresentation:
    """Tests for tag string representation."""

    def test_tag_str_representation(self, user):
        """Test string representation of tag."""
        tag = PasswordTagFactory(user=user, name="work")
        assert str(tag) == "work"


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordTagMetaOptions:
    """Tests for PasswordTag model Meta options."""

    def test_tag_table_name(self):
        """Test that tag table name is correct."""
        assert PasswordTag._meta.db_table == "password_tags"

    def test_tag_ordering(self):
        """Test that tags are ordered by name."""
        user = UserFactory()
        PasswordTagFactory(user=user, name="zebra")
        PasswordTagFactory(user=user, name="alpha")
        PasswordTagFactory(user=user, name="beta")

        tags = PasswordTag.objects.filter(user=user)
        names = [t.name for t in tags]
        assert names == sorted(names)

    def test_unique_together_constraint(self, user):
        """Test that user and name must be unique together."""
        PasswordTag.objects.create(user=user, name="duplicate")

        with pytest.raises(IntegrityError):
            PasswordTag.objects.create(user=user, name="duplicate")

    def test_different_users_can_have_same_tag_name(self):
        """Test that different users can have tags with same name."""
        user1 = UserFactory()
        user2 = UserFactory()

        tag1 = PasswordTag.objects.create(user=user1, name="work")
        tag2 = PasswordTag.objects.create(user=user2, name="work")

        assert tag1.name == tag2.name
        assert tag1.user != tag2.user


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordTagQuerySets:
    """Tests for tag querysets and filtering."""

    def test_filter_tags_by_user(self):
        """Test filtering tags by user."""
        user1 = UserFactory()
        user2 = UserFactory()

        PasswordTagFactory(user=user1)
        PasswordTagFactory(user=user1)
        PasswordTagFactory(user=user2)

        user1_tags = PasswordTag.objects.filter(user=user1)
        assert user1_tags.count() == 2

    def test_filter_tags_by_name(self, user):
        """Test filtering tags by name."""
        tag1 = PasswordTagFactory(user=user, name="work")
        PasswordTagFactory(user=user, name="personal")

        work_tags = PasswordTag.objects.filter(user=user, name="work")
        assert work_tags.count() == 1
        assert tag1 in work_tags

    def test_filter_unused_tags(self, user):
        """Test filtering tags with no entries."""
        unused1 = PasswordTagFactory(user=user)
        unused2 = PasswordTagFactory(user=user)
        used = PasswordTagFactory(user=user)

        entry = PasswordEntryFactory(user=user)
        entry.tags.add(used)

        all_tags = PasswordTag.objects.filter(user=user)
        unused_tags = [t for t in all_tags if t.entry_count == 0]
        assert len(unused_tags) == 2


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordTagEdgeCases:
    """Tests for tag edge cases."""

    def test_tag_with_long_name(self, user):
        """Test tag with long name (up to 50 chars)."""
        long_name = "a" * 50
        tag = PasswordTag.objects.create(user=user, name=long_name)
        assert tag.name == long_name

    def test_tag_with_special_characters(self, user):
        """Test tag with special characters."""
        tag = PasswordTag.objects.create(user=user, name="work-personal")
        assert tag.name == "work-personal"

    def test_tag_with_spaces(self, user):
        """Test tag with spaces."""
        tag = PasswordTag.objects.create(user=user, name="my work tag")
        assert tag.name == "my work tag"

    def test_tag_with_emoji(self, user):
        """Test tag with emoji."""
        tag = PasswordTag.objects.create(user=user, name="work 💼")
        assert tag.name == "work 💼"

    def test_tag_color_validation(self, user):
        """Test tag color field accepts hex colors."""
        tag = PasswordTag.objects.create(
            user=user,
            name="color-test",
            color="#FF5733",
        )
        assert tag.color == "#FF5733"

    def test_tag_without_color(self, user):
        """Test tag without color."""
        tag = PasswordTag.objects.create(user=user, name="no-color")
        assert tag.color == ""

    def test_case_sensitive_tag_names(self, user):
        """Test that tag names are case-sensitive."""
        tag1 = PasswordTag.objects.create(user=user, name="Work")
        tag2 = PasswordTag.objects.create(user=user, name="work")

        assert tag1.name != tag2.name
        assert PasswordTag.objects.filter(user=user).count() == 2


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordTagManyToManyOperations:
    """Tests for many-to-many operations between tags and entries."""

    def test_add_single_tag_to_entry(self, user):
        """Test adding single tag to entry."""
        entry = PasswordEntryFactory(user=user)
        tag = PasswordTagFactory(user=user)

        entry.tags.add(tag)

        assert entry.tags.count() == 1
        assert tag in entry.tags.all()

    def test_add_multiple_tags_to_entry(self, user):
        """Test adding multiple tags to entry."""
        entry = PasswordEntryFactory(user=user)
        tag1 = PasswordTagFactory(user=user)
        tag2 = PasswordTagFactory(user=user)
        tag3 = PasswordTagFactory(user=user)

        entry.tags.add(tag1, tag2, tag3)

        assert entry.tags.count() == 3

    def test_remove_tag_from_entry(self, user):
        """Test removing tag from entry."""
        entry = PasswordEntryFactory(user=user)
        tag = PasswordTagFactory(user=user)
        entry.tags.add(tag)

        assert entry.tags.count() == 1

        entry.tags.remove(tag)

        assert entry.tags.count() == 0

    def test_clear_all_tags_from_entry(self, user):
        """Test clearing all tags from entry."""
        entry = PasswordEntryFactory(user=user)
        tag1 = PasswordTagFactory(user=user)
        tag2 = PasswordTagFactory(user=user)
        entry.tags.add(tag1, tag2)

        assert entry.tags.count() == 2

        entry.tags.clear()

        assert entry.tags.count() == 0

    def test_set_tags_for_entry(self, user):
        """Test setting tags for entry (replaces existing)."""
        entry = PasswordEntryFactory(user=user)
        tag1 = PasswordTagFactory(user=user)
        tag2 = PasswordTagFactory(user=user)
        tag3 = PasswordTagFactory(user=user)

        entry.tags.add(tag1, tag2)
        assert entry.tags.count() == 2

        entry.tags.set([tag2, tag3])
        assert entry.tags.count() == 2
        assert tag1 not in entry.tags.all()
        assert tag2 in entry.tags.all()
        assert tag3 in entry.tags.all()
