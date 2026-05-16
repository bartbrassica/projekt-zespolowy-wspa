"""
Unit tests for authentication/db_utils.py functions.
"""

import base64
import pytest
from authentication.db_utils import convert_salt_to_bytes


@pytest.mark.unit
class TestConvertSaltToBytes:
    """Tests for convert_salt_to_bytes function."""

    def test_convert_memoryview_to_bytes(self):
        """Test converting memoryview to bytes."""
        original_bytes = b"test_salt_data"
        salt = memoryview(original_bytes)
        result = convert_salt_to_bytes(salt)
        assert result == original_bytes
        assert isinstance(result, bytes)

    def test_convert_valid_base64_string_to_bytes(self):
        """Test converting valid base64 string to bytes."""
        original_bytes = b"test_salt_data"
        base64_string = base64.b64encode(original_bytes).decode("utf-8")
        result = convert_salt_to_bytes(base64_string)
        assert result == original_bytes
        assert isinstance(result, bytes)

    def test_convert_invalid_base64_string_to_bytes(self):
        """Test converting invalid base64 string falls back to UTF-8 encoding."""
        invalid_base64_string = "not a valid base64 string!!!"
        result = convert_salt_to_bytes(invalid_base64_string)
        assert result == invalid_base64_string.encode("utf-8")
        assert isinstance(result, bytes)

    def test_convert_plain_string_to_bytes(self):
        """Test converting plain string that's not base64 encoded."""
        plain_string = "plain_text_salt"
        result = convert_salt_to_bytes(plain_string)
        # Should try base64 decode first, fail, then encode as UTF-8
        assert result == plain_string.encode("utf-8")
        assert isinstance(result, bytes)

    def test_convert_bytes_to_bytes(self):
        """Test that bytes are returned as-is."""
        salt = b"already_bytes"
        result = convert_salt_to_bytes(salt)
        assert result == salt
        assert result is salt  # Should be the same object
        assert isinstance(result, bytes)

    def test_convert_bytearray_to_bytes(self):
        """Test converting bytearray to bytes."""
        salt = bytearray(b"bytearray_salt")
        result = convert_salt_to_bytes(salt)
        assert result == bytes(salt)
        assert isinstance(result, bytes)

    def test_convert_list_to_bytes(self):
        """Test converting list of integers to bytes."""
        salt = [65, 66, 67, 68]  # ASCII for 'ABCD'
        result = convert_salt_to_bytes(salt)
        assert result == bytes(salt)
        assert isinstance(result, bytes)
        assert result == b"ABCD"

    def test_convert_empty_string_to_bytes(self):
        """Test converting empty string to bytes."""
        result = convert_salt_to_bytes("")
        assert result == b""
        assert isinstance(result, bytes)

    def test_convert_empty_bytes_to_bytes(self):
        """Test converting empty bytes to bytes."""
        result = convert_salt_to_bytes(b"")
        assert result == b""
        assert isinstance(result, bytes)
