"""
Unit tests for authentication/schemas.py
"""

import pytest
from pydantic import ValidationError
import uuid
from datetime import datetime

from authentication.schemas import (
    UserIn,
    UserOut,
    PasswordChangeIn,
    PasswordEntryOut,
    TagOut,
    ShareLinkOut,
)


@pytest.mark.unit
class TestUserInPasswordValidation:
    """Tests for UserIn schema password validation."""

    def test_password_missing_uppercase(self):
        """Test password validation when uppercase letter is missing - line 21."""
        with pytest.raises(ValidationError) as exc_info:
            UserIn(
                email="test@example.com",
                password="lowercase123!",  # Missing uppercase
            )

        errors = exc_info.value.errors()
        assert any("uppercase" in str(error["msg"]).lower() for error in errors)

    def test_password_missing_lowercase(self):
        """Test password validation when lowercase letter is missing - line 23."""
        with pytest.raises(ValidationError) as exc_info:
            UserIn(
                email="test@example.com",
                password="UPPERCASE123!",  # Missing lowercase
            )

        errors = exc_info.value.errors()
        assert any("lowercase" in str(error["msg"]).lower() for error in errors)

    def test_password_missing_number(self):
        """Test password validation when number is missing - line 25."""
        with pytest.raises(ValidationError) as exc_info:
            UserIn(
                email="test@example.com",
                password="PasswordOnly!",  # Missing number
            )

        errors = exc_info.value.errors()
        assert any("number" in str(error["msg"]).lower() for error in errors)

    def test_password_missing_special_character(self):
        """Test password validation when special character is missing - line 27."""
        with pytest.raises(ValidationError) as exc_info:
            UserIn(
                email="test@example.com",
                password="Password123",  # Missing special character
            )

        errors = exc_info.value.errors()
        assert any("special" in str(error["msg"]).lower() for error in errors)

    def test_password_valid(self):
        """Test password validation with valid password."""
        user = UserIn(
            email="test@example.com",
            password="ValidPass123!",
        )

        assert user.password == "ValidPass123!"


@pytest.mark.unit
class TestUserOutUUIDConversion:
    """Tests for UserOut schema UUID conversion."""

    def test_convert_uuid_to_string(self):
        """Test UUID conversion to string."""
        test_uuid = uuid.uuid4()

        user = UserOut(
            id=test_uuid,
            email="test@example.com",
            is_verified=True,
            date_joined=datetime.now(),
        )

        assert isinstance(user.id, str)
        assert user.id == str(test_uuid)

    def test_convert_string_id_returns_as_is(self):
        """Test that string ID is returned as-is - line 47."""
        string_id = "already-a-string-id"

        user = UserOut(
            id=string_id,
            email="test@example.com",
            is_verified=True,
            date_joined=datetime.now(),
        )

        assert user.id == string_id


@pytest.mark.unit
class TestPasswordChangeInValidation:
    """Tests for PasswordChangeIn schema password validation."""

    def test_new_password_missing_uppercase(self):
        """Test new password validation when uppercase letter is missing - line 104."""
        with pytest.raises(ValidationError) as exc_info:
            PasswordChangeIn(
                current_password="OldPass123!",
                new_password="lowercase123!",  # Missing uppercase
                confirm_password="lowercase123!",
            )

        errors = exc_info.value.errors()
        assert any("uppercase" in str(error["msg"]).lower() for error in errors)

    def test_new_password_missing_lowercase(self):
        """Test new password validation when lowercase letter is missing - line 106."""
        with pytest.raises(ValidationError) as exc_info:
            PasswordChangeIn(
                current_password="OldPass123!",
                new_password="UPPERCASE123!",  # Missing lowercase
                confirm_password="UPPERCASE123!",
            )

        errors = exc_info.value.errors()
        assert any("lowercase" in str(error["msg"]).lower() for error in errors)

    def test_new_password_missing_number(self):
        """Test new password validation when number is missing - line 108."""
        with pytest.raises(ValidationError) as exc_info:
            PasswordChangeIn(
                current_password="OldPass123!",
                new_password="PasswordOnly!",  # Missing number
                confirm_password="PasswordOnly!",
            )

        errors = exc_info.value.errors()
        assert any("number" in str(error["msg"]).lower() for error in errors)

    def test_new_password_missing_special_character(self):
        """Test new password validation when special character is missing - line 110."""
        with pytest.raises(ValidationError) as exc_info:
            PasswordChangeIn(
                current_password="OldPass123!",
                new_password="Password123",  # Missing special character
                confirm_password="Password123",
            )

        errors = exc_info.value.errors()
        assert any("special" in str(error["msg"]).lower() for error in errors)

    def test_passwords_do_not_match(self):
        """Test password validation when confirm doesn't match."""
        with pytest.raises(ValidationError) as exc_info:
            PasswordChangeIn(
                current_password="OldPass123!",
                new_password="NewPass123!",
                confirm_password="DifferentPass123!",
            )

        errors = exc_info.value.errors()
        assert any("do not match" in str(error["msg"]).lower() for error in errors)

    def test_valid_password_change(self):
        """Test valid password change."""
        change = PasswordChangeIn(
            current_password="OldPass123!",
            new_password="NewPass123!",
            confirm_password="NewPass123!",
        )

        assert change.new_password == "NewPass123!"
        assert change.confirm_password == "NewPass123!"


@pytest.mark.unit
class TestPasswordEntryOutConversion:
    """Tests for PasswordEntryOut schema conversions."""

    def test_convert_uuid_id_to_string(self):
        """Test UUID ID conversion to string."""
        test_uuid = uuid.uuid4()

        entry = PasswordEntryOut(
            id=test_uuid,
            name="Test Entry",
            is_expired=False,
            is_favorite=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert isinstance(entry.id, str)
        assert entry.id == str(test_uuid)

    def test_convert_string_id_returns_as_is(self):
        """Test that string ID is returned as-is - line 251."""
        string_id = "already-a-string-id"

        entry = PasswordEntryOut(
            id=string_id,
            name="Test Entry",
            is_expired=False,
            is_favorite=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert entry.id == string_id

    def test_convert_url_to_string_none(self):
        """Test URL conversion when None - line 258."""
        entry = PasswordEntryOut(
            id=str(uuid.uuid4()),
            name="Test Entry",
            site=None,
            is_expired=False,
            is_favorite=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert entry.site is None

    def test_convert_url_to_string_with_string(self):
        """Test URL conversion with string."""
        url_string = "https://example.com"

        entry = PasswordEntryOut(
            id=str(uuid.uuid4()),
            name="Test Entry",
            site=url_string,
            is_expired=False,
            is_favorite=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert entry.site == url_string

    def test_convert_url_to_string_without_str_method(self):
        """Test URL conversion for object without __str__ - line 262."""
        from unittest.mock import Mock, patch
        import builtins

        # Create a mock object
        mock_value = Mock()

        # Store original hasattr
        original_hasattr = builtins.hasattr

        # Patch hasattr to simulate an object without __str__
        # This tests the else branch of the validator
        def mock_hasattr(obj, name):
            if obj is mock_value and name == "__str__":
                return False
            return original_hasattr(obj, name)

        with patch('builtins.hasattr', side_effect=mock_hasattr):
            result = PasswordEntryOut.convert_url_to_string(mock_value)

        # Should return the value as-is when it doesn't have __str__
        assert result is mock_value


@pytest.mark.unit
class TestTagOutUUIDConversion:
    """Tests for TagOut schema UUID conversion."""

    def test_convert_uuid_to_string(self):
        """Test UUID conversion to string."""
        test_uuid = uuid.uuid4()

        tag = TagOut(
            id=test_uuid,
            name="Test Tag",
            entry_count=0,
            created_at=datetime.now(),
        )

        assert isinstance(tag.id, str)
        assert tag.id == str(test_uuid)

    def test_convert_string_id_returns_as_is(self):
        """Test that string ID is returned as-is - line 437."""
        string_id = "already-a-string-id"

        tag = TagOut(
            id=string_id,
            name="Test Tag",
            entry_count=0,
            created_at=datetime.now(),
        )

        assert tag.id == string_id


@pytest.mark.unit
class TestShareLinkOutUUIDConversion:
    """Tests for ShareLinkOut schema UUID conversion."""

    def test_convert_uuid_to_string(self):
        """Test UUID conversion to string."""
        test_uuid = uuid.uuid4()

        share_link = ShareLinkOut(
            id=test_uuid,
            share_url="https://example.com/share/abc123",
            max_views=5,
            current_views=0,
            expires_at=datetime.now(),
            require_authentication=False,
            created_at=datetime.now(),
        )

        assert isinstance(share_link.id, str)
        assert share_link.id == str(test_uuid)

    def test_convert_string_id_returns_as_is(self):
        """Test that string ID is returned as-is - line 469."""
        string_id = "already-a-string-id"

        share_link = ShareLinkOut(
            id=string_id,
            share_url="https://example.com/share/abc123",
            max_views=5,
            current_views=0,
            expires_at=datetime.now(),
            require_authentication=False,
            created_at=datetime.now(),
        )

        assert share_link.id == string_id


@pytest.mark.unit
class TestAdditionalSchemaValidation:
    """Additional tests for schema validation."""

    def test_user_in_with_optional_fields(self):
        """Test UserIn with optional fields."""
        user = UserIn(
            email="test@example.com",
            password="ValidPass123!",
            first_name="John",
            last_name="Doe",
            phone_number="+1234567890",
        )

        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.phone_number == "+1234567890"

    def test_password_change_in_passwords_match(self):
        """Test PasswordChangeIn with matching passwords."""
        change = PasswordChangeIn(
            current_password="CurrentPass123!",
            new_password="NewPass123!",
            confirm_password="NewPass123!",
        )

        assert change.new_password == change.confirm_password

    def test_password_entry_out_with_all_fields(self):
        """Test PasswordEntryOut with all fields populated."""
        entry = PasswordEntryOut(
            id=str(uuid.uuid4()),
            name="Test Entry",
            site="https://example.com",
            username="testuser",
            notes="Test notes",
            expires_at=datetime.now(),
            is_expired=False,
            days_until_expiry=30,
            folder=None,
            tags=[],
            is_favorite=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            last_accessed=datetime.now(),
        )

        assert entry.name == "Test Entry"
        assert entry.is_favorite is True
