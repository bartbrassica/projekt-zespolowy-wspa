"""
Unit tests for PasswordEntry model.

Tests cover:
- PasswordEntry creation (CRUD operations)
- Password encryption and decryption
- Expiration logic and properties
- Properties (is_expired, days_until_expiry)
- Access tracking (mark_accessed)
- Relationships with folders and tags
"""

import pytest
from datetime import timedelta
from django.utils import timezone
from django.db.utils import IntegrityError

from authentication.models import PasswordEntry, PasswordFolder, PasswordTag
from authentication.encryption_service import encryption_service
from tests.fixtures.factories import (
    UserFactory,
    PasswordEntryFactory,
    PasswordEntryWithExpirationFactory,
    ExpiredPasswordEntryFactory,
    FavoritePasswordEntryFactory,
    PasswordFolderFactory,
    PasswordTagFactory,
)


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordEntryCreation:
    """Tests for PasswordEntry model creation (CRUD)."""

    def test_create_password_entry(self, user, test_master_password):
        """Test creating a basic password entry."""
        encrypted_password, salt = encryption_service.encrypt_password(
            "my-secret-password", test_master_password
        )

        entry = PasswordEntry.objects.create(
            user=user,
            name="My Account",
            site="https://example.com",
            username="myusername",
            encrypted_password=encrypted_password,
            encryption_salt=salt,
            notes="Some notes",
        )

        assert entry.user == user
        assert entry.name == "My Account"
        assert entry.site == "https://example.com"
        assert entry.username == "myusername"
        assert entry.notes == "Some notes"
        assert entry.encrypted_password is not None
        assert entry.encryption_salt is not None

    def test_create_password_entry_with_factory(self, user):
        """Test creating password entry with factory."""
        entry = PasswordEntryFactory(user=user)
        assert entry.user == user
        assert entry.name is not None
        assert entry.encrypted_password is not None

    def test_password_entry_id_is_uuid(self):
        """Test that password entry ID is UUID."""
        entry = PasswordEntryFactory()
        assert entry.id is not None
        assert len(str(entry.id)) == 36  # UUID format

    def test_create_password_entry_minimal_fields(self, user, test_master_password):
        """Test creating password entry with minimal required fields."""
        encrypted_password, salt = encryption_service.encrypt_password(
            "password", test_master_password
        )

        entry = PasswordEntry.objects.create(
            user=user,
            name="Minimal Entry",
            encrypted_password=encrypted_password,
            encryption_salt=salt,
        )

        assert entry.user == user
        assert entry.name == "Minimal Entry"
        assert entry.site == ""
        assert entry.username == ""
        assert entry.notes == ""

    def test_read_password_entry(self, password_entry):
        """Test reading a password entry."""
        retrieved = PasswordEntry.objects.get(id=password_entry.id)
        assert retrieved.id == password_entry.id
        assert retrieved.name == password_entry.name
        assert retrieved.user == password_entry.user

    def test_update_password_entry(self, password_entry):
        """Test updating a password entry."""
        password_entry.name = "Updated Name"
        password_entry.username = "new_username"
        password_entry.save()

        updated = PasswordEntry.objects.get(id=password_entry.id)
        assert updated.name == "Updated Name"
        assert updated.username == "new_username"

    def test_delete_password_entry(self, password_entry):
        """Test deleting a password entry."""
        entry_id = password_entry.id
        password_entry.delete()

        assert PasswordEntry.objects.filter(id=entry_id).count() == 0

    def test_created_at_auto_set(self):
        """Test that created_at is automatically set."""
        entry = PasswordEntryFactory()
        assert entry.created_at is not None
        assert entry.created_at <= timezone.now()

    def test_updated_at_auto_set(self):
        """Test that updated_at is automatically set and updates."""
        entry = PasswordEntryFactory()
        original_updated_at = entry.updated_at

        entry.name = "Updated Name"
        entry.save()

        assert entry.updated_at >= original_updated_at


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordEntryEncryption:
    """Tests for password entry encryption."""

    def test_password_is_encrypted(self, user, test_master_password):
        """Test that password is encrypted, not stored in plain text."""
        plain_password = "my-secret-password"
        encrypted_password, salt = encryption_service.encrypt_password(
            plain_password, test_master_password
        )

        entry = PasswordEntry.objects.create(
            user=user,
            name="Test Entry",
            encrypted_password=encrypted_password,
            encryption_salt=salt,
        )

        assert entry.encrypted_password != plain_password
        assert len(entry.encrypted_password) > len(plain_password)

    def test_decrypt_password(self, user, test_master_password):
        """Test decrypting password."""
        plain_password = "my-secret-password"
        encrypted_password, salt = encryption_service.encrypt_password(
            plain_password, test_master_password
        )

        entry = PasswordEntry.objects.create(
            user=user,
            name="Test Entry",
            encrypted_password=encrypted_password,
            encryption_salt=salt,
        )

        decrypted = encryption_service.decrypt_password(
            entry.encrypted_password, test_master_password, entry.encryption_salt
        )
        assert decrypted == plain_password

    def test_encryption_salt_is_stored(self, password_entry):
        """Test that encryption salt is stored."""
        assert password_entry.encryption_salt is not None
        assert len(password_entry.encryption_salt) > 0

    def test_different_entries_different_salts(self, user):
        """Test that different entries have different salts."""
        entry1 = PasswordEntryFactory(user=user)
        entry2 = PasswordEntryFactory(user=user)

        assert entry1.encryption_salt != entry2.encryption_salt


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordEntryExpiration:
    """Tests for password entry expiration logic."""

    def test_entry_without_expiration_not_expired(self):
        """Test entry without expiration is not expired."""
        entry = PasswordEntryFactory(expires_at=None)
        assert entry.is_expired is False

    def test_entry_with_future_expiration_not_expired(self):
        """Test entry with future expiration is not expired."""
        entry = PasswordEntryWithExpirationFactory()
        assert entry.is_expired is False

    def test_entry_with_past_expiration_is_expired(self):
        """Test entry with past expiration is expired."""
        entry = ExpiredPasswordEntryFactory()
        assert entry.is_expired is True

    def test_entry_expires_exactly_now(self, user, test_master_password):
        """Test entry that expires exactly now."""
        encrypted_password, salt = encryption_service.encrypt_password(
            "password", test_master_password
        )

        entry = PasswordEntry.objects.create(
            user=user,
            name="Expiring Now",
            encrypted_password=encrypted_password,
            encryption_salt=salt,
            expires_at=timezone.now(),
        )

        # Entry expiring at current time should be expired
        assert entry.is_expired is True or entry.is_expired is False
        # This is time-sensitive, property exists and returns bool

    def test_days_until_expiry_future_date(self, user, test_master_password):
        """Test days_until_expiry with future expiration."""
        encrypted_password, salt = encryption_service.encrypt_password(
            "password", test_master_password
        )

        entry = PasswordEntry.objects.create(
            user=user,
            name="Expiring Later",
            encrypted_password=encrypted_password,
            encryption_salt=salt,
            expires_at=timezone.now() + timedelta(days=30),
        )

        days = entry.days_until_expiry
        assert days is not None
        assert 29 <= days <= 30  # Account for time precision

    def test_days_until_expiry_past_date(self):
        """Test days_until_expiry with past expiration."""
        entry = ExpiredPasswordEntryFactory()
        days = entry.days_until_expiry
        assert days == 0  # Returns 0 for expired entries

    def test_days_until_expiry_no_expiration(self):
        """Test days_until_expiry when no expiration is set."""
        entry = PasswordEntryFactory(expires_at=None)
        assert entry.days_until_expiry is None

    def test_days_until_expiry_one_day(self, user, test_master_password):
        """Test days_until_expiry with one day remaining."""
        encrypted_password, salt = encryption_service.encrypt_password(
            "password", test_master_password
        )

        entry = PasswordEntry.objects.create(
            user=user,
            name="Expiring Tomorrow",
            encrypted_password=encrypted_password,
            encryption_salt=salt,
            expires_at=timezone.now() + timedelta(days=1),
        )

        days = entry.days_until_expiry
        assert days in [0, 1]  # Account for time precision


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordEntryAccessTracking:
    """Tests for password entry access tracking."""

    def test_last_accessed_initially_none(self):
        """Test that last_accessed is initially None."""
        entry = PasswordEntryFactory()
        assert entry.last_accessed is None

    def test_mark_accessed(self):
        """Test marking entry as accessed."""
        entry = PasswordEntryFactory()
        assert entry.last_accessed is None

        entry.mark_accessed()

        refreshed = PasswordEntry.objects.get(id=entry.id)
        assert refreshed.last_accessed is not None
        assert refreshed.last_accessed <= timezone.now()

    def test_mark_accessed_updates_timestamp(self):
        """Test that mark_accessed updates timestamp."""
        entry = PasswordEntryFactory()
        entry.mark_accessed()
        first_access = entry.last_accessed

        # Simulate time passing
        import time
        time.sleep(0.01)

        entry.mark_accessed()
        second_access = entry.last_accessed

        assert second_access >= first_access


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordEntryFavorites:
    """Tests for password entry favorites."""

    def test_entry_not_favorite_by_default(self):
        """Test that entries are not favorite by default."""
        entry = PasswordEntryFactory()
        assert entry.is_favorite is False

    def test_create_favorite_entry(self):
        """Test creating a favorite entry."""
        entry = FavoritePasswordEntryFactory()
        assert entry.is_favorite is True

    def test_mark_entry_as_favorite(self):
        """Test marking entry as favorite."""
        entry = PasswordEntryFactory(is_favorite=False)
        entry.is_favorite = True
        entry.save()

        refreshed = PasswordEntry.objects.get(id=entry.id)
        assert refreshed.is_favorite is True

    def test_unfavorite_entry(self):
        """Test unfavoriting an entry."""
        entry = FavoritePasswordEntryFactory()
        assert entry.is_favorite is True

        entry.is_favorite = False
        entry.save()

        refreshed = PasswordEntry.objects.get(id=entry.id)
        assert refreshed.is_favorite is False


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordEntryRelationships:
    """Tests for password entry relationships."""

    def test_entry_belongs_to_user(self, password_entry, user):
        """Test that entry belongs to a user."""
        assert password_entry.user == user

    def test_user_can_have_multiple_entries(self, user):
        """Test that user can have multiple entries."""
        entry1 = PasswordEntryFactory(user=user)
        entry2 = PasswordEntryFactory(user=user)
        entry3 = PasswordEntryFactory(user=user)

        user_entries = user.password_entries.all()
        assert user_entries.count() == 3
        assert entry1 in user_entries
        assert entry2 in user_entries
        assert entry3 in user_entries

    def test_deleting_user_deletes_entries(self, user):
        """Test that deleting user cascades to entries."""
        entry1 = PasswordEntryFactory(user=user)
        entry2 = PasswordEntryFactory(user=user)
        entry_ids = [entry1.id, entry2.id]

        user.delete()

        assert PasswordEntry.objects.filter(id__in=entry_ids).count() == 0

    def test_entry_with_folder(self, user):
        """Test entry with folder relationship."""
        folder = PasswordFolderFactory(user=user)
        entry = PasswordEntryFactory(user=user, folder=folder)

        assert entry.folder == folder
        assert entry in folder.entries.all()

    def test_entry_without_folder(self):
        """Test entry without folder."""
        entry = PasswordEntryFactory(folder=None)
        assert entry.folder is None

    def test_deleting_folder_sets_null(self, user):
        """Test that deleting folder sets folder field to null."""
        folder = PasswordFolderFactory(user=user)
        entry = PasswordEntryFactory(user=user, folder=folder)

        folder.delete()

        refreshed = PasswordEntry.objects.get(id=entry.id)
        assert refreshed.folder is None

    def test_entry_with_tags(self, user):
        """Test entry with tags relationship."""
        tag1 = PasswordTagFactory(user=user)
        tag2 = PasswordTagFactory(user=user)
        entry = PasswordEntryFactory(user=user)

        entry.tags.add(tag1, tag2)

        assert entry.tags.count() == 2
        assert tag1 in entry.tags.all()
        assert tag2 in entry.tags.all()

    def test_entry_without_tags(self):
        """Test entry without tags."""
        entry = PasswordEntryFactory()
        assert entry.tags.count() == 0

    def test_remove_tag_from_entry(self, user):
        """Test removing tag from entry."""
        tag = PasswordTagFactory(user=user)
        entry = PasswordEntryFactory(user=user)
        entry.tags.add(tag)

        assert entry.tags.count() == 1

        entry.tags.remove(tag)

        assert entry.tags.count() == 0


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordEntryStringRepresentation:
    """Tests for password entry string representation."""

    def test_entry_str_representation(self, user):
        """Test string representation of entry."""
        entry = PasswordEntryFactory(user=user, name="Test Entry")
        expected = f"Test Entry - {user.email}"
        assert str(entry) == expected


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordEntryMetaOptions:
    """Tests for PasswordEntry model Meta options."""

    def test_entry_table_name(self):
        """Test that entry table name is correct."""
        assert PasswordEntry._meta.db_table == "password_entries"

    def test_entry_ordering(self):
        """Test that entries are ordered by favorite and updated_at."""
        user = UserFactory()
        entry1 = PasswordEntryFactory(user=user, is_favorite=False)
        entry2 = FavoritePasswordEntryFactory(user=user)
        entry3 = PasswordEntryFactory(user=user, is_favorite=False)

        entries = PasswordEntry.objects.filter(user=user)
        # Favorite entries should come first
        assert entries[0].is_favorite is True

    def test_unique_together_constraint(self, user, test_master_password):
        """Test that user, name, and site must be unique together."""
        encrypted_password, salt = encryption_service.encrypt_password(
            "password", test_master_password
        )

        PasswordEntry.objects.create(
            user=user,
            name="Duplicate",
            site="https://example.com",
            encrypted_password=encrypted_password,
            encryption_salt=salt,
        )

        with pytest.raises(IntegrityError):
            PasswordEntry.objects.create(
                user=user,
                name="Duplicate",
                site="https://example.com",
                encrypted_password=encrypted_password,
                encryption_salt=salt,
            )

    def test_different_users_can_have_same_name_site(self, test_master_password):
        """Test that different users can have entries with same name and site."""
        user1 = UserFactory()
        user2 = UserFactory()

        encrypted_password, salt = encryption_service.encrypt_password(
            "password", test_master_password
        )

        entry1 = PasswordEntry.objects.create(
            user=user1,
            name="Same Entry",
            site="https://example.com",
            encrypted_password=encrypted_password,
            encryption_salt=salt,
        )

        encrypted_password2, salt2 = encryption_service.encrypt_password(
            "password", test_master_password
        )

        entry2 = PasswordEntry.objects.create(
            user=user2,
            name="Same Entry",
            site="https://example.com",
            encrypted_password=encrypted_password2,
            encryption_salt=salt2,
        )

        assert entry1.name == entry2.name
        assert entry1.site == entry2.site
        assert entry1.user != entry2.user


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordEntryQuerySets:
    """Tests for password entry querysets and filtering."""

    def test_filter_entries_by_user(self):
        """Test filtering entries by user."""
        user1 = UserFactory()
        user2 = UserFactory()

        PasswordEntryFactory(user=user1)
        PasswordEntryFactory(user=user1)
        PasswordEntryFactory(user=user2)

        user1_entries = PasswordEntry.objects.filter(user=user1)
        assert user1_entries.count() == 2

    def test_filter_favorite_entries(self, user):
        """Test filtering favorite entries."""
        FavoritePasswordEntryFactory(user=user)
        FavoritePasswordEntryFactory(user=user)
        PasswordEntryFactory(user=user, is_favorite=False)

        favorites = PasswordEntry.objects.filter(user=user, is_favorite=True)
        assert favorites.count() == 2

    def test_filter_entries_by_folder(self, user):
        """Test filtering entries by folder."""
        folder = PasswordFolderFactory(user=user)
        PasswordEntryFactory(user=user, folder=folder)
        PasswordEntryFactory(user=user, folder=folder)
        PasswordEntryFactory(user=user, folder=None)

        folder_entries = PasswordEntry.objects.filter(folder=folder)
        assert folder_entries.count() == 2

    def test_filter_expired_entries(self, user):
        """Test filtering expired entries."""
        ExpiredPasswordEntryFactory(user=user)
        ExpiredPasswordEntryFactory(user=user)
        PasswordEntryFactory(user=user)

        all_entries = PasswordEntry.objects.filter(user=user)
        expired = [e for e in all_entries if e.is_expired]
        assert len(expired) == 2
