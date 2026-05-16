"""
Integration tests for password statistics endpoint.
"""

import pytest
from datetime import timedelta
from django.utils import timezone


@pytest.mark.integration
@pytest.mark.django_db
class TestPasswordStatistics:

    def test_stats_with_empty_database(self, authenticated_client):
        """Test stats endpoint with no data."""
        response = authenticated_client.get("/api/passwords/stats")

        assert response.status_code == 200
        data = response.json()

        assert data["total_passwords"] == 0
        assert data["expired_passwords"] == 0
        assert data["expiring_soon"] == 0
        assert data["favorite_count"] == 0
        assert data["folder_count"] == 0
        assert data["tag_count"] == 0
        assert data["recent_entries"] == []
        assert data["recently_accessed"] == []

    def test_stats_basic_counts(self, authenticated_client, user, test_password):
        """Test basic password, folder, and tag counts."""
        from authentication.models import PasswordEntry, PasswordFolder, PasswordTag
        from authentication.encryption_service import encryption_service

        # Create folders
        PasswordFolder.objects.create(user=user, name="Work")
        PasswordFolder.objects.create(user=user, name="Personal")

        # Create tags
        PasswordTag.objects.create(user=user, name="important")
        PasswordTag.objects.create(user=user, name="finance")
        PasswordTag.objects.create(user=user, name="social")

        # Create password entries
        for i in range(5):
            encrypted, salt = encryption_service.encrypt_password(f"password{i}", test_password)
            PasswordEntry.objects.create(
                user=user,
                name=f"Entry {i}",
                encrypted_password=encrypted,
                encryption_salt=salt,
            )

        response = authenticated_client.get("/api/passwords/stats")

        assert response.status_code == 200
        data = response.json()

        assert data["total_passwords"] == 5
        assert data["folder_count"] == 2
        assert data["tag_count"] == 3

    def test_stats_expired_passwords(self, authenticated_client, user, test_password):
        """Test counting expired passwords."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        now = timezone.now()

        # Create expired entries
        for i in range(3):
            encrypted, salt = encryption_service.encrypt_password(f"password{i}", test_password)
            PasswordEntry.objects.create(
                user=user,
                name=f"Expired Entry {i}",
                encrypted_password=encrypted,
                encryption_salt=salt,
                expires_at=now - timedelta(days=i + 1),  # Expired 1-3 days ago
            )

        # Create non-expired entries
        for i in range(2):
            encrypted, salt = encryption_service.encrypt_password(f"password{i}", test_password)
            PasswordEntry.objects.create(
                user=user,
                name=f"Valid Entry {i}",
                encrypted_password=encrypted,
                encryption_salt=salt,
                expires_at=now + timedelta(days=60),  # Expires in 60 days
            )

        response = authenticated_client.get("/api/passwords/stats")

        assert response.status_code == 200
        data = response.json()

        assert data["total_passwords"] == 5
        assert data["expired_passwords"] == 3

    def test_stats_expiring_soon(self, authenticated_client, user, test_password):
        """Test counting passwords expiring within 30 days."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        now = timezone.now()

        # Create entries expiring soon (within 30 days)
        for days in [5, 15, 25]:
            encrypted, salt = encryption_service.encrypt_password(f"password{days}", test_password)
            PasswordEntry.objects.create(
                user=user,
                name=f"Expiring Soon {days}",
                encrypted_password=encrypted,
                encryption_salt=salt,
                expires_at=now + timedelta(days=days),
            )

        # Create entries not expiring soon (> 30 days)
        for days in [40, 60, 90]:
            encrypted, salt = encryption_service.encrypt_password(f"password{days}", test_password)
            PasswordEntry.objects.create(
                user=user,
                name=f"Not Expiring Soon {days}",
                encrypted_password=encrypted,
                encryption_salt=salt,
                expires_at=now + timedelta(days=days),
            )

        # Create already expired entry (should not count in expiring_soon)
        encrypted, salt = encryption_service.encrypt_password("expired", test_password)
        PasswordEntry.objects.create(
            user=user,
            name="Already Expired",
            encrypted_password=encrypted,
            encryption_salt=salt,
            expires_at=now - timedelta(days=1),
        )

        response = authenticated_client.get("/api/passwords/stats")

        assert response.status_code == 200
        data = response.json()

        assert data["expiring_soon"] == 3
        assert data["expired_passwords"] == 1

    def test_stats_favorite_count(self, authenticated_client, user, test_password):
        """Test counting favorite passwords."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        # Create favorite entries
        for i in range(4):
            encrypted, salt = encryption_service.encrypt_password(f"password{i}", test_password)
            PasswordEntry.objects.create(
                user=user,
                name=f"Favorite Entry {i}",
                encrypted_password=encrypted,
                encryption_salt=salt,
                is_favorite=True,
            )

        # Create non-favorite entries
        for i in range(6):
            encrypted, salt = encryption_service.encrypt_password(f"password{i}", test_password)
            PasswordEntry.objects.create(
                user=user,
                name=f"Regular Entry {i}",
                encrypted_password=encrypted,
                encryption_salt=salt,
                is_favorite=False,
            )

        response = authenticated_client.get("/api/passwords/stats")

        assert response.status_code == 200
        data = response.json()

        assert data["total_passwords"] == 10
        assert data["favorite_count"] == 4

    def test_stats_recent_entries(self, authenticated_client, user, test_password):
        """Test recent entries list (last 5 by created_at)."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service
        import time

        # Create 7 entries with slight delays to ensure different created_at times
        entries = []
        for i in range(7):
            encrypted, salt = encryption_service.encrypt_password(f"password{i}", test_password)
            entry = PasswordEntry.objects.create(
                user=user,
                name=f"Entry {i}",
                encrypted_password=encrypted,
                encryption_salt=salt,
            )
            entries.append(entry)
            if i < 6:  # Don't sleep after last one
                time.sleep(0.01)  # Small delay to ensure different timestamps

        response = authenticated_client.get("/api/passwords/stats")

        assert response.status_code == 200
        data = response.json()

        # Should return last 5 entries
        assert len(data["recent_entries"]) == 5

        # Verify entries are ordered by created_at descending (most recent first)
        recent_ids = [e["id"] for e in data["recent_entries"]]
        # Last 5 created should be entries 6, 5, 4, 3, 2 (in that order)
        expected_ids = [str(entries[i].id) for i in range(6, 1, -1)]
        assert recent_ids == expected_ids

        # Verify structure
        for entry_data in data["recent_entries"]:
            assert "id" in entry_data
            assert "name" in entry_data
            assert "created_at" in entry_data

    def test_stats_recently_accessed(self, authenticated_client, user, test_password):
        """Test recently accessed entries list."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        now = timezone.now()

        # Create entries with different last_accessed times
        entries_with_access = []
        for i in range(3):
            encrypted, salt = encryption_service.encrypt_password(f"password{i}", test_password)
            entry = PasswordEntry.objects.create(
                user=user,
                name=f"Accessed Entry {i}",
                encrypted_password=encrypted,
                encryption_salt=salt,
                last_accessed=now - timedelta(hours=i),  # 0, 1, 2 hours ago
            )
            entries_with_access.append(entry)

        # Create entries never accessed (last_accessed is None)
        for i in range(2):
            encrypted, salt = encryption_service.encrypt_password(f"password{i}", test_password)
            PasswordEntry.objects.create(
                user=user,
                name=f"Never Accessed Entry {i}",
                encrypted_password=encrypted,
                encryption_salt=salt,
                last_accessed=None,
            )

        response = authenticated_client.get("/api/passwords/stats")

        assert response.status_code == 200
        data = response.json()

        # Should only return entries that have been accessed
        assert len(data["recently_accessed"]) == 3

        # Verify entries are ordered by last_accessed descending (most recent first)
        accessed_ids = [e["id"] for e in data["recently_accessed"]]
        expected_ids = [str(entry.id) for entry in entries_with_access]
        assert accessed_ids == expected_ids

        # Verify structure
        for entry_data in data["recently_accessed"]:
            assert "id" in entry_data
            assert "name" in entry_data
            assert "last_accessed" in entry_data
            assert entry_data["last_accessed"] is not None

    def test_stats_user_isolation(self, authenticated_client, user, multiple_users, test_password):
        """Test that stats only show current user's data."""
        from authentication.models import PasswordEntry, PasswordFolder
        from authentication.encryption_service import encryption_service

        # authenticated_client uses the 'user' fixture
        current_user = user
        other_user = multiple_users[0]

        # Create data for current user
        encrypted, salt = encryption_service.encrypt_password("password1", test_password)
        PasswordEntry.objects.create(
            user=current_user,
            name="Current User Entry",
            encrypted_password=encrypted,
            encryption_salt=salt,
        )
        PasswordFolder.objects.create(user=current_user, name="Current User Folder")

        # Create data for other user
        encrypted, salt = encryption_service.encrypt_password("password2", test_password)
        PasswordEntry.objects.create(
            user=other_user,
            name="Other User Entry",
            encrypted_password=encrypted,
            encryption_salt=salt,
        )
        PasswordFolder.objects.create(user=other_user, name="Other User Folder")

        response = authenticated_client.get("/api/passwords/stats")

        assert response.status_code == 200
        data = response.json()

        # Should only see current user's data
        assert data["total_passwords"] == 1
        assert data["folder_count"] == 1

    def test_stats_without_authentication(self, api_client):
        """Test stats endpoint requires authentication."""
        response = api_client.get("/api/passwords/stats")
        assert response.status_code == 401

    def test_stats_comprehensive_scenario(self, authenticated_client, user, test_password):
        """Test stats with comprehensive realistic scenario."""
        from authentication.models import PasswordEntry, PasswordFolder, PasswordTag
        from authentication.encryption_service import encryption_service

        now = timezone.now()

        # Create folders
        work_folder = PasswordFolder.objects.create(user=user, name="Work")
        personal_folder = PasswordFolder.objects.create(user=user, name="Personal")

        # Create tags
        important_tag = PasswordTag.objects.create(user=user, name="important")
        finance_tag = PasswordTag.objects.create(user=user, name="finance")

        # Create various password entries
        # 1. Expired password
        encrypted, salt = encryption_service.encrypt_password("expired_pwd", test_password)
        PasswordEntry.objects.create(
            user=user,
            name="Expired Bank Login",
            encrypted_password=encrypted,
            encryption_salt=salt,
            folder=work_folder,
            expires_at=now - timedelta(days=10),
            is_favorite=False,
        )

        # 2. Expiring soon password
        encrypted, salt = encryption_service.encrypt_password("expiring_pwd", test_password)
        PasswordEntry.objects.create(
            user=user,
            name="Expiring Email",
            encrypted_password=encrypted,
            encryption_salt=salt,
            folder=personal_folder,
            expires_at=now + timedelta(days=15),
            is_favorite=True,
        )

        # 3. Valid favorite password with last_accessed
        encrypted, salt = encryption_service.encrypt_password("favorite_pwd", test_password)
        PasswordEntry.objects.create(
            user=user,
            name="Favorite Social",
            encrypted_password=encrypted,
            encryption_salt=salt,
            is_favorite=True,
            last_accessed=now - timedelta(hours=2),
        )

        # 4-6. Regular valid passwords
        for i in range(3):
            encrypted, salt = encryption_service.encrypt_password(f"pwd{i}", test_password)
            PasswordEntry.objects.create(
                user=user,
                name=f"Regular Entry {i}",
                encrypted_password=encrypted,
                encryption_salt=salt,
                expires_at=now + timedelta(days=90),
            )

        response = authenticated_client.get("/api/passwords/stats")

        assert response.status_code == 200
        data = response.json()

        # Verify all counts
        assert data["total_passwords"] == 6
        assert data["expired_passwords"] == 1
        assert data["expiring_soon"] == 1
        assert data["favorite_count"] == 2
        assert data["folder_count"] == 2
        assert data["tag_count"] == 2

        # Verify recent entries
        assert len(data["recent_entries"]) == 5  # Maximum 5

        # Verify recently accessed
        assert len(data["recently_accessed"]) == 1  # Only one has last_accessed

    def test_stats_with_no_expiry_dates(self, authenticated_client, user, test_password):
        """Test stats when entries have no expiry dates."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        # Create entries without expiry dates
        for i in range(5):
            encrypted, salt = encryption_service.encrypt_password(f"password{i}", test_password)
            PasswordEntry.objects.create(
                user=user,
                name=f"No Expiry Entry {i}",
                encrypted_password=encrypted,
                encryption_salt=salt,
                expires_at=None,  # No expiry
            )

        response = authenticated_client.get("/api/passwords/stats")

        assert response.status_code == 200
        data = response.json()

        assert data["total_passwords"] == 5
        assert data["expired_passwords"] == 0
        assert data["expiring_soon"] == 0

    def test_stats_edge_case_exactly_30_days(self, authenticated_client, user, test_password):
        """Test edge case of password expiring at 30 days boundary."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        now = timezone.now()

        # Entry expiring in slightly less than 30 days (should be included)
        encrypted, salt = encryption_service.encrypt_password("password30minus", test_password)
        PasswordEntry.objects.create(
            user=user,
            name="Just Under 30 Days",
            encrypted_password=encrypted,
            encryption_salt=salt,
            expires_at=now + timedelta(days=29, hours=23),
        )

        # Entry expiring in 29 days (should be included)
        encrypted, salt = encryption_service.encrypt_password("password29", test_password)
        PasswordEntry.objects.create(
            user=user,
            name="29 Days",
            encrypted_password=encrypted,
            encryption_salt=salt,
            expires_at=now + timedelta(days=29),
        )

        # Entry expiring in slightly more than 30 days (should not be included)
        encrypted, salt = encryption_service.encrypt_password("password30plus", test_password)
        PasswordEntry.objects.create(
            user=user,
            name="Just Over 30 Days",
            encrypted_password=encrypted,
            encryption_salt=salt,
            expires_at=now + timedelta(days=30, hours=1),
        )

        # Entry expiring in 31 days (should not be included)
        encrypted, salt = encryption_service.encrypt_password("password31", test_password)
        PasswordEntry.objects.create(
            user=user,
            name="31 Days",
            encrypted_password=encrypted,
            encryption_salt=salt,
            expires_at=now + timedelta(days=31),
        )

        response = authenticated_client.get("/api/passwords/stats")

        assert response.status_code == 200
        data = response.json()

        # Should include entries expiring in less than 30 days from now
        # Due to timing differences between test and endpoint execution,
        # we verify the 29-day and just-under-30-day entries are included
        assert data["expiring_soon"] == 2

    def test_stats_more_than_5_recent_entries(self, authenticated_client, user, test_password):
        """Test that recent_entries limits to 5 even with more entries."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service
        import time

        # Create 10 entries
        for i in range(10):
            encrypted, salt = encryption_service.encrypt_password(f"password{i}", test_password)
            PasswordEntry.objects.create(
                user=user,
                name=f"Entry {i}",
                encrypted_password=encrypted,
                encryption_salt=salt,
            )
            if i < 9:
                time.sleep(0.01)

        response = authenticated_client.get("/api/passwords/stats")

        assert response.status_code == 200
        data = response.json()

        assert data["total_passwords"] == 10
        assert len(data["recent_entries"]) == 5  # Should limit to 5

    def test_stats_more_than_5_recently_accessed(self, authenticated_client, user, test_password):
        """Test that recently_accessed limits to 5 even with more accessed entries."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service

        now = timezone.now()

        # Create 10 accessed entries
        for i in range(10):
            encrypted, salt = encryption_service.encrypt_password(f"password{i}", test_password)
            PasswordEntry.objects.create(
                user=user,
                name=f"Accessed Entry {i}",
                encrypted_password=encrypted,
                encryption_salt=salt,
                last_accessed=now - timedelta(hours=i),
            )

        response = authenticated_client.get("/api/passwords/stats")

        assert response.status_code == 200
        data = response.json()

        assert data["total_passwords"] == 10
        assert len(data["recently_accessed"]) == 5  # Should limit to 5
