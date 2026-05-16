"""
Unit tests for authentication/utils.py
"""

import pytest
import jwt
from datetime import date, datetime
from django.utils import timezone
from django.test import RequestFactory
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from authentication.utils import (
    get_date_range_for_day,
    serialize_password_data,
    load_jwt_keys,
    create_jwt_tokens,
    verify_jwt_token,
    verify_master_password,
    get_client_ip,
    get_user_agent,
)


@pytest.mark.unit
class TestGetDateRangeForDay:
    """Tests for get_date_range_for_day function."""

    def test_get_date_range_for_day(self):
        """Test getting start and end datetime for a specific date."""
        target_date = date(2024, 1, 15)

        start, end = get_date_range_for_day(target_date)

        assert start.year == 2024
        assert start.month == 1
        assert start.day == 15
        assert start.hour == 0
        assert start.minute == 0
        assert start.second == 0

        assert end.year == 2024
        assert end.month == 1
        assert end.day == 15
        assert end.hour == 23
        assert end.minute == 59
        assert end.second == 59

    def test_get_date_range_for_day_timezone_aware(self):
        """Test that returned datetimes are timezone aware."""
        target_date = date.today()

        start, end = get_date_range_for_day(target_date)

        assert timezone.is_aware(start)
        assert timezone.is_aware(end)

    def test_get_date_range_for_day_order(self):
        """Test that start is before end."""
        target_date = date(2024, 6, 1)

        start, end = get_date_range_for_day(target_date)

        assert start < end


@pytest.mark.unit
@pytest.mark.django_db
class TestSerializePasswordData:
    """Tests for serialize_password_data function."""

    def test_serialize_password_data(self, password_entry):
        """Test serializing password entry data."""
        result = serialize_password_data(password_entry)

        assert "name" in result
        assert "site" in result
        assert "username" in result
        assert "expires_at" in result
        assert "days_until_expiry" in result

        assert result["name"] == password_entry.name
        assert result["site"] == password_entry.site
        assert result["username"] == password_entry.username

    def test_serialize_password_data_with_expiry(self, user, test_password):
        """Test serializing password data with expiry date."""
        from authentication.models import PasswordEntry
        from authentication.encryption_service import encryption_service
        from datetime import timedelta

        encrypted_password, salt = encryption_service.encrypt_password(
            "test-password", test_password
        )

        entry = PasswordEntry.objects.create(
            user=user,
            name="Test Entry",
            site="https://example.com",
            username="testuser",
            encrypted_password=encrypted_password,
            encryption_salt=salt,
            expires_at=timezone.now() + timedelta(days=30),
        )

        result = serialize_password_data(entry)

        assert result["expires_at"] == entry.expires_at
        assert result["days_until_expiry"] == entry.days_until_expiry


@pytest.mark.unit
class TestLoadJWTKeys:
    """Tests for load_jwt_keys function."""

    @patch('authentication.utils.Path')
    def test_load_jwt_keys_existing(self, mock_path_class):
        """Test loading existing JWT keys."""
        # Mock the path structure
        mock_keys_dir = MagicMock()
        mock_private_key_path = MagicMock()
        mock_public_key_path = MagicMock()

        # Set up the path chain
        mock_path_class.return_value.__truediv__.return_value = mock_keys_dir
        mock_keys_dir.__truediv__.side_effect = [mock_private_key_path, mock_public_key_path]

        # Mock that keys exist
        mock_private_key_path.exists.return_value = True
        mock_public_key_path.exists.return_value = True

        # Mock file contents
        fake_private_key = b"-----BEGIN PRIVATE KEY-----\nfake_private\n-----END PRIVATE KEY-----"
        fake_public_key = b"-----BEGIN PUBLIC KEY-----\nfake_public\n-----END PUBLIC KEY-----"

        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.return_value.__enter__.return_value.read.side_effect = [
                fake_private_key,
                fake_public_key
            ]

            private, public = load_jwt_keys()

            assert private == fake_private_key
            assert public == fake_public_key

    @patch('authentication.utils.Path')
    @patch('authentication.utils.ec.generate_private_key')
    def test_load_jwt_keys_generate_new(self, mock_generate_key, mock_path_class):
        """Test generating new JWT keys when they don't exist."""
        # Mock the path structure
        mock_keys_dir = MagicMock()
        mock_private_key_path = MagicMock()
        mock_public_key_path = MagicMock()

        mock_path_class.return_value.__truediv__.return_value = mock_keys_dir
        mock_keys_dir.__truediv__.side_effect = [
            mock_private_key_path,
            mock_public_key_path,
            mock_private_key_path,
            mock_public_key_path
        ]

        # Mock that keys don't exist initially
        mock_private_key_path.exists.return_value = False
        mock_public_key_path.exists.return_value = False

        # Mock the cryptography key generation
        mock_private_key_obj = MagicMock()
        mock_public_key_obj = MagicMock()

        fake_private_pem = b"-----BEGIN PRIVATE KEY-----\nnew_private\n-----END PRIVATE KEY-----"
        fake_public_pem = b"-----BEGIN PUBLIC KEY-----\nnew_public\n-----END PUBLIC KEY-----"

        mock_private_key_obj.private_bytes.return_value = fake_private_pem
        mock_private_key_obj.public_key.return_value = mock_public_key_obj
        mock_public_key_obj.public_bytes.return_value = fake_public_pem

        mock_generate_key.return_value = mock_private_key_obj

        # Mock file operations
        with patch('builtins.open', mock_open()) as mock_file:
            # Set up different return values for write and read operations
            write_handle = MagicMock()
            read_handle = MagicMock()
            read_handle.__enter__.return_value.read.side_effect = [fake_private_pem, fake_public_pem]

            def open_side_effect(path, mode):
                if 'w' in mode:
                    return write_handle
                else:
                    return read_handle

            mock_file.side_effect = open_side_effect

            private, public = load_jwt_keys()

            # Verify key generation was called
            mock_generate_key.assert_called_once()

            # Verify keys were written (2 writes: private and public)
            assert write_handle.__enter__.return_value.write.call_count == 2


@pytest.mark.unit
@pytest.mark.django_db
class TestCreateJWTTokens:
    """Tests for create_jwt_tokens function."""

    def test_create_jwt_tokens(self, user):
        """Test creating JWT tokens for a user."""
        tokens = create_jwt_tokens(user)

        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert "token_type" in tokens
        assert "expires_in" in tokens
        assert "jti" in tokens

        assert tokens["token_type"] == "bearer"
        assert isinstance(tokens["access_token"], str)
        assert isinstance(tokens["refresh_token"], str)

    def test_create_jwt_tokens_payload(self, user):
        """Test JWT token payload content."""
        tokens = create_jwt_tokens(user)

        # Verify the token without checking signature
        access_payload = jwt.decode(
            tokens["access_token"],
            options={"verify_signature": False}
        )

        assert access_payload["user_id"] == str(user.id)
        assert access_payload["token_type"] == "access"
        assert "exp" in access_payload
        assert "iat" in access_payload

    def test_create_jwt_tokens_unique_jti(self, user):
        """Test that each token set has unique JTI."""
        tokens1 = create_jwt_tokens(user)
        tokens2 = create_jwt_tokens(user)

        assert tokens1["jti"] != tokens2["jti"]


@pytest.mark.unit
@pytest.mark.django_db
class TestVerifyJWTToken:
    """Tests for verify_jwt_token function."""

    def test_verify_jwt_token_valid(self, user):
        """Test verifying valid JWT token."""
        tokens = create_jwt_tokens(user)

        payload = verify_jwt_token(tokens["access_token"])

        assert payload is not None
        assert payload["user_id"] == str(user.id)
        assert payload["token_type"] == "access"

    def test_verify_jwt_token_invalid(self):
        """Test verifying invalid JWT token."""
        invalid_token = "invalid.token.here"

        payload = verify_jwt_token(invalid_token)

        assert payload is None

    def test_verify_jwt_token_expired(self, user):
        """Test verifying expired JWT token."""
        from datetime import timedelta
        from freezegun import freeze_time

        # Create a token
        with freeze_time("2024-01-01 12:00:00"):
            tokens = create_jwt_tokens(user)
            access_token = tokens["access_token"]

        # Move time forward past expiration
        with freeze_time("2024-01-02 12:00:00"):
            payload = verify_jwt_token(access_token)

            assert payload is None


@pytest.mark.unit
@pytest.mark.django_db
class TestVerifyMasterPassword:
    """Tests for verify_master_password function."""

    def test_verify_master_password_correct(self, user, test_password):
        """Test verifying correct master password."""
        result = verify_master_password(user, test_password)

        assert result is True

    def test_verify_master_password_incorrect(self, user):
        """Test verifying incorrect master password."""
        result = verify_master_password(user, "WrongPassword123!")

        assert result is False


@pytest.mark.unit
class TestGetClientIP:
    """Tests for get_client_ip function."""

    def test_get_client_ip_direct(self):
        """Test getting client IP from REMOTE_ADDR."""
        factory = RequestFactory()
        request = factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.100'

        ip = get_client_ip(request)

        assert ip == '192.168.1.100'

    def test_get_client_ip_x_forwarded_for(self):
        """Test getting client IP from X-Forwarded-For header."""
        factory = RequestFactory()
        request = factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '10.0.0.1, 10.0.0.2, 10.0.0.3'
        request.META['REMOTE_ADDR'] = '192.168.1.100'

        ip = get_client_ip(request)

        # Should return the first IP in X-Forwarded-For
        assert ip == '10.0.0.1'

    def test_get_client_ip_x_forwarded_for_single(self):
        """Test getting client IP from X-Forwarded-For with single IP."""
        factory = RequestFactory()
        request = factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '10.0.0.1'
        request.META['REMOTE_ADDR'] = '192.168.1.100'

        ip = get_client_ip(request)

        assert ip == '10.0.0.1'

    def test_get_client_ip_x_forwarded_for_with_spaces(self):
        """Test getting client IP from X-Forwarded-For with spaces."""
        factory = RequestFactory()
        request = factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '  10.0.0.1  , 10.0.0.2'
        request.META['REMOTE_ADDR'] = '192.168.1.100'

        ip = get_client_ip(request)

        assert ip == '10.0.0.1'

    def test_get_client_ip_no_remote_addr(self):
        """Test getting client IP when REMOTE_ADDR is missing."""
        factory = RequestFactory()
        request = factory.get('/')
        # Remove the default REMOTE_ADDR that RequestFactory adds
        if 'REMOTE_ADDR' in request.META:
            del request.META['REMOTE_ADDR']

        ip = get_client_ip(request)

        assert ip is None


@pytest.mark.unit
class TestGetUserAgent:
    """Tests for get_user_agent function."""

    def test_get_user_agent_present(self):
        """Test getting user agent when present."""
        factory = RequestFactory()
        request = factory.get('/')
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Test Browser)'

        user_agent = get_user_agent(request)

        assert user_agent == 'Mozilla/5.0 (Test Browser)'

    def test_get_user_agent_missing(self):
        """Test getting user agent when missing."""
        factory = RequestFactory()
        request = factory.get('/')

        user_agent = get_user_agent(request)

        assert user_agent == ''

    def test_get_user_agent_empty(self):
        """Test getting user agent when empty."""
        factory = RequestFactory()
        request = factory.get('/')
        request.META['HTTP_USER_AGENT'] = ''

        user_agent = get_user_agent(request)

        assert user_agent == ''
