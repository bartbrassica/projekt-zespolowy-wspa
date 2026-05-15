"""
Unit tests for PasswordShareLink model.

Tests cover:
- PasswordShareLink creation (CRUD operations)
- Share link validation
- View counting and limits
- Expiration checking
- Authentication requirements
"""

import pytest
from datetime import timedelta
from django.utils import timezone
import ipaddress

from authentication.models import PasswordShareLink
from tests.fixtures.factories import (
    UserFactory,
    PasswordEntryFactory,
    PasswordShareLinkFactory,
    ExpiredShareLinkFactory,
)


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordShareLinkCreation:
    """Tests for PasswordShareLink model creation (CRUD)."""

    def test_create_share_link(self, user):
        """Test creating a basic share link."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLink.objects.create(
            password_entry=entry,
            created_by=user,
            max_views=5,
            expires_at=timezone.now() + timedelta(hours=24),
            require_authentication=False,
        )

        assert share_link.password_entry == entry
        assert share_link.created_by == user
        assert share_link.max_views == 5
        assert share_link.current_views == 0
        assert share_link.require_authentication is False

    def test_create_share_link_with_factory(self, user):
        """Test creating share link with factory."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLinkFactory(
            password_entry=entry, created_by=user
        )

        assert share_link.password_entry == entry
        assert share_link.created_by == user

    def test_share_link_id_is_uuid(self):
        """Test that share link ID is UUID."""
        share_link = PasswordShareLinkFactory()
        assert share_link.id is not None
        assert len(str(share_link.id)) == 36  # UUID format

    def test_share_token_auto_generated(self, user):
        """Test that share token is automatically generated."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLink.objects.create(
            password_entry=entry,
            created_by=user,
            max_views=1,
            expires_at=timezone.now() + timedelta(hours=24),
        )

        assert share_link.share_token is not None
        assert len(str(share_link.share_token)) == 36  # UUID format

    def test_share_token_is_unique(self, user):
        """Test that share tokens are unique."""
        entry = PasswordEntryFactory(user=user)
        link1 = PasswordShareLinkFactory(password_entry=entry, created_by=user)
        link2 = PasswordShareLinkFactory(password_entry=entry, created_by=user)

        assert link1.share_token != link2.share_token

    def test_read_share_link(self, password_share_link):
        """Test reading a share link."""
        retrieved = PasswordShareLink.objects.get(id=password_share_link.id)
        assert retrieved.id == password_share_link.id
        assert retrieved.share_token == password_share_link.share_token

    def test_update_share_link(self, password_share_link):
        """Test updating a share link."""
        password_share_link.max_views = 10
        password_share_link.require_authentication = True
        password_share_link.save()

        updated = PasswordShareLink.objects.get(id=password_share_link.id)
        assert updated.max_views == 10
        assert updated.require_authentication is True

    def test_delete_share_link(self, password_share_link):
        """Test deleting a share link."""
        link_id = password_share_link.id
        password_share_link.delete()

        assert PasswordShareLink.objects.filter(id=link_id).count() == 0

    def test_created_at_auto_set(self):
        """Test that created_at is automatically set."""
        share_link = PasswordShareLinkFactory()
        assert share_link.created_at is not None


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordShareLinkValidation:
    """Tests for share link validation."""

    def test_valid_share_link(self, user):
        """Test share link that is valid (not expired, views remaining)."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLink.objects.create(
            password_entry=entry,
            created_by=user,
            max_views=5,
            current_views=0,
            expires_at=timezone.now() + timedelta(hours=24),
        )

        assert share_link.is_valid is True

    def test_expired_share_link_not_valid(self, user):
        """Test that expired share link is not valid."""
        entry = PasswordEntryFactory(user=user)
        share_link = ExpiredShareLinkFactory(
            password_entry=entry, created_by=user
        )

        assert share_link.is_valid is False

    def test_max_views_reached_not_valid(self, user):
        """Test that share link with max views reached is not valid."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLink.objects.create(
            password_entry=entry,
            created_by=user,
            max_views=5,
            current_views=5,
            expires_at=timezone.now() + timedelta(hours=24),
        )

        assert share_link.is_valid is False

    def test_views_exceeded_not_valid(self, user):
        """Test that share link with views exceeded is not valid."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLink.objects.create(
            password_entry=entry,
            created_by=user,
            max_views=5,
            current_views=6,
            expires_at=timezone.now() + timedelta(hours=24),
        )

        assert share_link.is_valid is False

    def test_one_view_remaining_is_valid(self, user):
        """Test that share link with one view remaining is valid."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLink.objects.create(
            password_entry=entry,
            created_by=user,
            max_views=5,
            current_views=4,
            expires_at=timezone.now() + timedelta(hours=24),
        )

        assert share_link.is_valid is True


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordShareLinkViewCounting:
    """Tests for share link view counting."""

    def test_initial_view_count_is_zero(self, user):
        """Test that initial view count is zero."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLinkFactory(
            password_entry=entry, created_by=user
        )

        assert share_link.current_views == 0

    def test_increment_views(self, user):
        """Test incrementing view count."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLinkFactory(
            password_entry=entry, created_by=user, max_views=5
        )

        assert share_link.current_views == 0

        share_link.increment_views()

        refreshed = PasswordShareLink.objects.get(id=share_link.id)
        assert refreshed.current_views == 1

    def test_increment_views_multiple_times(self, user):
        """Test incrementing view count multiple times."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLinkFactory(
            password_entry=entry, created_by=user, max_views=5
        )

        share_link.increment_views()
        share_link.increment_views()
        share_link.increment_views()

        refreshed = PasswordShareLink.objects.get(id=share_link.id)
        assert refreshed.current_views == 3

    def test_increment_views_updates_last_accessed(self, user):
        """Test that increment_views updates last_accessed."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLinkFactory(
            password_entry=entry, created_by=user
        )

        assert share_link.last_accessed is None

        share_link.increment_views()

        refreshed = PasswordShareLink.objects.get(id=share_link.id)
        assert refreshed.last_accessed is not None
        assert refreshed.last_accessed <= timezone.now()

    def test_increment_views_beyond_max(self, user):
        """Test incrementing views beyond max_views."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLinkFactory(
            password_entry=entry, created_by=user, max_views=2
        )

        share_link.increment_views()
        share_link.increment_views()

        assert share_link.current_views == 2
        assert share_link.is_valid is False

        # Can still increment, but link becomes invalid
        share_link.increment_views()

        refreshed = PasswordShareLink.objects.get(id=share_link.id)
        assert refreshed.current_views == 3
        assert refreshed.is_valid is False


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordShareLinkExpiration:
    """Tests for share link expiration."""

    def test_share_link_not_expired(self, user):
        """Test share link that hasn't expired."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLinkFactory(
            password_entry=entry,
            created_by=user,
            expires_at=timezone.now() + timedelta(hours=24),
        )

        assert timezone.now() < share_link.expires_at

    def test_share_link_expired(self, user):
        """Test expired share link."""
        entry = PasswordEntryFactory(user=user)
        share_link = ExpiredShareLinkFactory(
            password_entry=entry, created_by=user
        )

        assert timezone.now() >= share_link.expires_at

    def test_share_link_expires_in_future(self, user):
        """Test share link that expires in the future."""
        entry = PasswordEntryFactory(user=user)
        expires_at = timezone.now() + timedelta(days=7)
        share_link = PasswordShareLink.objects.create(
            password_entry=entry,
            created_by=user,
            max_views=10,
            expires_at=expires_at,
        )

        assert share_link.expires_at == expires_at


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordShareLinkAuthentication:
    """Tests for share link authentication requirements."""

    def test_share_link_without_authentication(self, user):
        """Test share link that doesn't require authentication."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLinkFactory(
            password_entry=entry,
            created_by=user,
            require_authentication=False,
        )

        assert share_link.require_authentication is False

    def test_share_link_with_authentication(self, user):
        """Test share link that requires authentication."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLinkFactory(
            password_entry=entry,
            created_by=user,
            require_authentication=True,
        )

        assert share_link.require_authentication is True

    def test_share_link_with_allowed_email(self, user):
        """Test share link with allowed email."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLink.objects.create(
            password_entry=entry,
            created_by=user,
            max_views=5,
            expires_at=timezone.now() + timedelta(hours=24),
            require_authentication=True,
            allowed_email="recipient@example.com",
        )

        assert share_link.allowed_email == "recipient@example.com"

    def test_share_link_without_allowed_email(self, user):
        """Test share link without allowed email."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLinkFactory(
            password_entry=entry, created_by=user
        )

        assert share_link.allowed_email == ""


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordShareLinkRelationships:
    """Tests for share link relationships."""

    def test_share_link_belongs_to_password_entry(self, password_share_link):
        """Test that share link belongs to a password entry."""
        assert password_share_link.password_entry is not None

    def test_share_link_has_creator(self, password_share_link):
        """Test that share link has a creator."""
        assert password_share_link.created_by is not None

    def test_password_entry_can_have_multiple_share_links(self, user):
        """Test that password entry can have multiple share links."""
        entry = PasswordEntryFactory(user=user)
        link1 = PasswordShareLinkFactory(password_entry=entry, created_by=user)
        link2 = PasswordShareLinkFactory(password_entry=entry, created_by=user)
        link3 = PasswordShareLinkFactory(password_entry=entry, created_by=user)

        assert entry.share_links.count() == 3
        assert link1 in entry.share_links.all()
        assert link2 in entry.share_links.all()
        assert link3 in entry.share_links.all()

    def test_user_can_create_multiple_share_links(self, user):
        """Test that user can create multiple share links."""
        entry1 = PasswordEntryFactory(user=user)
        entry2 = PasswordEntryFactory(user=user)

        link1 = PasswordShareLinkFactory(
            password_entry=entry1, created_by=user
        )
        link2 = PasswordShareLinkFactory(
            password_entry=entry2, created_by=user
        )

        user_links = user.created_shares.all()
        assert user_links.count() == 2
        assert link1 in user_links
        assert link2 in user_links

    def test_deleting_password_entry_deletes_share_links(self, user):
        """Test that deleting password entry cascades to share links."""
        entry = PasswordEntryFactory(user=user)
        link1 = PasswordShareLinkFactory(password_entry=entry, created_by=user)
        link2 = PasswordShareLinkFactory(password_entry=entry, created_by=user)
        link_ids = [link1.id, link2.id]

        entry.delete()

        assert PasswordShareLink.objects.filter(id__in=link_ids).count() == 0

    def test_deleting_user_deletes_share_links(self, user):
        """Test that deleting user cascades to share links."""
        entry = PasswordEntryFactory(user=user)
        link1 = PasswordShareLinkFactory(password_entry=entry, created_by=user)
        link2 = PasswordShareLinkFactory(password_entry=entry, created_by=user)
        link_ids = [link1.id, link2.id]

        user.delete()

        assert PasswordShareLink.objects.filter(id__in=link_ids).count() == 0


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordShareLinkStringRepresentation:
    """Tests for share link string representation."""

    def test_share_link_str_representation(self, user):
        """Test string representation of share link."""
        entry = PasswordEntryFactory(user=user, name="Test Entry")
        share_link = PasswordShareLinkFactory(
            password_entry=entry, created_by=user
        )

        expected = f"Share link for Test Entry"
        assert str(share_link) == expected


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordShareLinkMetaOptions:
    """Tests for PasswordShareLink model Meta options."""

    def test_share_link_table_name(self):
        """Test that share link table name is correct."""
        assert PasswordShareLink._meta.db_table == "password_share_links"

    def test_share_link_ordering(self):
        """Test that share links are ordered by created_at descending."""
        user = UserFactory()
        entry = PasswordEntryFactory(user=user)

        link1 = PasswordShareLinkFactory(password_entry=entry, created_by=user)
        link2 = PasswordShareLinkFactory(password_entry=entry, created_by=user)
        link3 = PasswordShareLinkFactory(password_entry=entry, created_by=user)

        links = PasswordShareLink.objects.filter(password_entry=entry)
        # Most recent should be first
        assert links[0].created_at >= links[1].created_at >= links[2].created_at


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordShareLinkQuerySets:
    """Tests for share link querysets and filtering."""

    def test_filter_share_links_by_password_entry(self, user):
        """Test filtering share links by password entry."""
        entry1 = PasswordEntryFactory(user=user)
        entry2 = PasswordEntryFactory(user=user)

        PasswordShareLinkFactory(password_entry=entry1, created_by=user)
        PasswordShareLinkFactory(password_entry=entry1, created_by=user)
        PasswordShareLinkFactory(password_entry=entry2, created_by=user)

        entry1_links = PasswordShareLink.objects.filter(password_entry=entry1)
        assert entry1_links.count() == 2

    def test_filter_share_links_by_creator(self):
        """Test filtering share links by creator."""
        user1 = UserFactory()
        user2 = UserFactory()
        entry = PasswordEntryFactory(user=user1)

        PasswordShareLinkFactory(password_entry=entry, created_by=user1)
        PasswordShareLinkFactory(password_entry=entry, created_by=user1)

        user1_links = PasswordShareLink.objects.filter(created_by=user1)
        assert user1_links.count() == 2

    def test_filter_valid_share_links(self, user):
        """Test filtering valid share links."""
        entry = PasswordEntryFactory(user=user)

        valid_link = PasswordShareLinkFactory(
            password_entry=entry,
            created_by=user,
            max_views=5,
            current_views=0,
            expires_at=timezone.now() + timedelta(hours=24),
        )
        expired_link = ExpiredShareLinkFactory(
            password_entry=entry, created_by=user
        )

        all_links = PasswordShareLink.objects.filter(password_entry=entry)
        valid_links = [link for link in all_links if link.is_valid]

        assert len(valid_links) == 1
        assert valid_link in valid_links

    def test_filter_expired_share_links(self, user):
        """Test filtering expired share links."""
        entry = PasswordEntryFactory(user=user)

        PasswordShareLinkFactory(
            password_entry=entry,
            created_by=user,
            expires_at=timezone.now() + timedelta(hours=24),
        )
        ExpiredShareLinkFactory(password_entry=entry, created_by=user)
        ExpiredShareLinkFactory(password_entry=entry, created_by=user)

        expired = PasswordShareLink.objects.filter(
            password_entry=entry, expires_at__lt=timezone.now()
        )
        assert expired.count() == 2


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordShareLinkEdgeCases:
    """Tests for share link edge cases."""

    def test_share_link_with_zero_max_views(self, user):
        """Test share link with zero max views."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLink.objects.create(
            password_entry=entry,
            created_by=user,
            max_views=0,
            expires_at=timezone.now() + timedelta(hours=24),
        )

        assert share_link.is_valid is False

    def test_share_link_with_unlimited_views(self, user):
        """Test share link with very high max views."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLink.objects.create(
            password_entry=entry,
            created_by=user,
            max_views=999999,
            expires_at=timezone.now() + timedelta(hours=24),
        )

        assert share_link.is_valid is True

    def test_share_link_accessed_by_ip_tracking(self, user):
        """Test that accessed_by_ip can be set."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLinkFactory(
            password_entry=entry, created_by=user
        )

        share_link.accessed_by_ip = "192.168.1.1"
        share_link.save()

        refreshed = PasswordShareLink.objects.get(id=share_link.id)
        assert refreshed.accessed_by_ip == "192.168.1.1"

    def test_share_link_with_ipv6_address(self, user):
        """Test share link with IPv6 address."""
        entry = PasswordEntryFactory(user=user)
        share_link = PasswordShareLinkFactory(
            password_entry=entry, created_by=user
        )

        share_link.accessed_by_ip = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        share_link.save()

        refreshed = PasswordShareLink.objects.get(id=share_link.id)
        
        assert (
            ipaddress.ip_address(refreshed.accessed_by_ip)
            == ipaddress.ip_address("2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        )
