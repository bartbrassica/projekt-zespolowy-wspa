"""
Unit tests for authentication/encryption_service.py
"""

import pytest
import base64
from unittest.mock import patch, MagicMock
from authentication.encryption_service import PasswordEncryptionService, encryption_service


@pytest.mark.unit
class TestPasswordEncryptionService:
    """Tests for PasswordEncryptionService class."""

    def test_generate_salt(self):
        """Test salt generation."""
        service = PasswordEncryptionService()
        salt = service.generate_salt()

        assert isinstance(salt, bytes)
        assert len(salt) == 32  # Default salt length

    def test_derive_key(self):
        """Test key derivation from master password."""
        service = PasswordEncryptionService()
        master_password = "MasterPassword123!"
        salt = service.generate_salt()

        key = service.derive_key(master_password, salt)

        assert isinstance(key, bytes)
        assert len(key) == 44  # Base64 encoded 32-byte key

    def test_derive_key_deterministic(self):
        """Test that same password and salt produce same key."""
        service = PasswordEncryptionService()
        master_password = "MasterPassword123!"
        salt = service.generate_salt()

        key1 = service.derive_key(master_password, salt)
        key2 = service.derive_key(master_password, salt)

        assert key1 == key2

    def test_encrypt_password(self):
        """Test password encryption."""
        service = PasswordEncryptionService()
        password = "MySecretPassword123!"
        master_password = "MasterPassword123!"

        encrypted, salt = service.encrypt_password(password, master_password)

        assert isinstance(encrypted, str)
        assert isinstance(salt, bytes)
        assert len(salt) == 32
        assert encrypted != password

    def test_decrypt_password_success(self):
        """Test successful password decryption."""
        service = PasswordEncryptionService()
        password = "MySecretPassword123!"
        master_password = "MasterPassword123!"

        encrypted, salt = service.encrypt_password(password, master_password)
        decrypted = service.decrypt_password(encrypted, master_password, salt)

        assert decrypted == password

    def test_decrypt_password_wrong_master_password(self):
        """Test decryption with wrong master password (InvalidToken exception)."""
        service = PasswordEncryptionService()
        password = "MySecretPassword123!"
        master_password = "MasterPassword123!"
        wrong_password = "WrongMasterPassword123!"

        encrypted, salt = service.encrypt_password(password, master_password)
        decrypted = service.decrypt_password(encrypted, wrong_password, salt)

        assert decrypted is None

    def test_decrypt_password_invalid_base64(self):
        """Test decryption with invalid base64 encoding (ValueError exception)."""
        service = PasswordEncryptionService()
        master_password = "MasterPassword123!"
        salt = service.generate_salt()

        # Invalid base64 string that will cause ValueError
        invalid_encrypted = "not-valid-base64!!!"

        decrypted = service.decrypt_password(invalid_encrypted, master_password, salt)

        assert decrypted is None

    def test_decrypt_password_corrupted_data(self):
        """Test decryption with corrupted encrypted data."""
        service = PasswordEncryptionService()
        master_password = "MasterPassword123!"
        salt = service.generate_salt()

        # Valid base64 but invalid Fernet token
        corrupted_data = base64.b64encode(b"corrupted data").decode("utf-8")

        decrypted = service.decrypt_password(corrupted_data, master_password, salt)

        assert decrypted is None

    @patch('authentication.encryption_service.base64.b64decode')
    def test_decrypt_password_unexpected_exception(self, mock_b64decode):
        """Test decryption with unexpected exception."""
        service = PasswordEncryptionService()
        master_password = "MasterPassword123!"
        salt = service.generate_salt()

        # Make b64decode raise an unexpected exception
        mock_b64decode.side_effect = RuntimeError("Unexpected error")

        decrypted = service.decrypt_password("anything", master_password, salt)

        assert decrypted is None

    def test_re_encrypt_password_success(self):
        """Test successful re-encryption with new master password."""
        service = PasswordEncryptionService()
        password = "MySecretPassword123!"
        old_master = "OldMaster123!"
        new_master = "NewMaster123!"

        # Encrypt with old master
        encrypted, salt = service.encrypt_password(password, old_master)

        # Re-encrypt with new master
        result = service.re_encrypt_password(encrypted, old_master, new_master, salt)

        assert result is not None
        new_encrypted, new_salt = result

        # Verify we can decrypt with new master
        decrypted = service.decrypt_password(new_encrypted, new_master, new_salt)
        assert decrypted == password

    def test_re_encrypt_password_failure_wrong_old_master(self):
        """Test re-encryption failure when old master password is wrong."""
        service = PasswordEncryptionService()
        password = "MySecretPassword123!"
        old_master = "OldMaster123!"
        wrong_old_master = "WrongOldMaster123!"
        new_master = "NewMaster123!"

        # Encrypt with old master
        encrypted, salt = service.encrypt_password(password, old_master)

        # Try to re-encrypt with wrong old master
        result = service.re_encrypt_password(encrypted, wrong_old_master, new_master, salt)

        assert result is None

    def test_validate_password_params_valid(self):
        """Test password parameter validation with valid params."""
        service = PasswordEncryptionService()

        # Should not raise any exception
        service._validate_password_params(
            length=10,
            include_symbols=True,
            include_numbers=True,
            include_uppercase=True,
            include_lowercase=True
        )

    def test_validate_password_params_length_zero(self):
        """Test password parameter validation with length 0."""
        service = PasswordEncryptionService()

        with pytest.raises(ValueError, match="Password length must be at least 1"):
            service._validate_password_params(
                length=0,
                include_symbols=True,
                include_numbers=True,
                include_uppercase=True,
                include_lowercase=True
            )

    def test_validate_password_params_length_negative(self):
        """Test password parameter validation with negative length."""
        service = PasswordEncryptionService()

        with pytest.raises(ValueError, match="Password length must be at least 1"):
            service._validate_password_params(
                length=-5,
                include_symbols=True,
                include_numbers=True,
                include_uppercase=True,
                include_lowercase=True
            )

    def test_validate_password_params_no_character_types(self):
        """Test password parameter validation with no character types."""
        service = PasswordEncryptionService()

        with pytest.raises(ValueError, match="At least one character type must be included"):
            service._validate_password_params(
                length=10,
                include_symbols=False,
                include_numbers=False,
                include_uppercase=False,
                include_lowercase=False
            )

    def test_build_character_set_all_types(self):
        """Test character set building with all types included."""
        service = PasswordEncryptionService()

        charset = service._build_character_set(
            include_symbols=True,
            include_numbers=True,
            include_uppercase=True,
            include_lowercase=True,
            exclude_ambiguous=False
        )

        assert len(charset) > 0
        assert any(c.islower() for c in charset)
        assert any(c.isupper() for c in charset)
        assert any(c.isdigit() for c in charset)
        assert any(not c.isalnum() for c in charset)

    def test_build_character_set_exclude_ambiguous(self):
        """Test character set building with ambiguous characters excluded."""
        service = PasswordEncryptionService()

        charset = service._build_character_set(
            include_symbols=False,
            include_numbers=True,
            include_uppercase=True,
            include_lowercase=True,
            exclude_ambiguous=True
        )

        # Should not contain ambiguous characters like 0, O, l, 1, I
        assert '0' not in charset
        assert 'O' not in charset
        assert 'l' not in charset
        assert '1' not in charset
        assert 'I' not in charset

    def test_generate_secure_password_default(self):
        """Test secure password generation with default parameters."""
        service = PasswordEncryptionService()

        password = service.generate_secure_password()

        assert len(password) == 16  # Default length
        assert any(c.islower() for c in password)
        assert any(c.isupper() for c in password)
        assert any(c.isdigit() for c in password)
        assert any(not c.isalnum() for c in password)

    def test_generate_secure_password_custom_length(self):
        """Test secure password generation with custom length."""
        service = PasswordEncryptionService()

        password = service.generate_secure_password(length=20)

        assert len(password) == 20

    def test_generate_secure_password_numbers_only(self):
        """Test secure password generation with numbers only."""
        service = PasswordEncryptionService()

        password = service.generate_secure_password(
            length=10,
            include_symbols=False,
            include_numbers=True,
            include_uppercase=False,
            include_lowercase=False,
            exclude_ambiguous=False
        )

        assert len(password) == 10
        assert all(c.isdigit() for c in password)

    def test_calculate_length_score(self):
        """Test length score calculation."""
        service = PasswordEncryptionService()

        assert service._calculate_length_score(4) == 0
        assert service._calculate_length_score(8) == 1
        assert service._calculate_length_score(12) == 2
        assert service._calculate_length_score(16) == 3

    def test_calculate_character_type_score(self):
        """Test character type score calculation."""
        service = PasswordEncryptionService()

        # All types
        score, lower, upper, nums, syms = service._calculate_character_type_score("Abc123!@")
        assert score == 4
        assert lower is True
        assert upper is True
        assert nums is True
        assert syms is True

        # Only lowercase
        score, lower, upper, nums, syms = service._calculate_character_type_score("abcdef")
        assert score == 1
        assert lower is True
        assert upper is False

    def test_determine_strength_label_very_weak(self):
        """Test strength label determination for very weak password."""
        service = PasswordEncryptionService()

        label = service._determine_strength_label(0)
        assert label == "Very Weak"

        label = service._determine_strength_label(2)
        assert label == "Very Weak"

    def test_determine_strength_label_weak(self):
        """Test strength label determination for weak password."""
        service = PasswordEncryptionService()

        label = service._determine_strength_label(3)
        assert label == "Weak"

    def test_determine_strength_label_medium(self):
        """Test strength label determination for medium password."""
        service = PasswordEncryptionService()

        label = service._determine_strength_label(4)
        assert label == "Medium"

        label = service._determine_strength_label(5)
        assert label == "Medium"

    def test_determine_strength_label_strong(self):
        """Test strength label determination for strong password."""
        service = PasswordEncryptionService()

        label = service._determine_strength_label(6)
        assert label == "Strong"

    def test_determine_strength_label_very_strong(self):
        """Test strength label determination for very strong password."""
        service = PasswordEncryptionService()

        label = service._determine_strength_label(7)
        assert label == "Very Strong"

        label = service._determine_strength_label(10)
        assert label == "Very Strong"

    def test_check_password_strength_very_weak(self):
        """Test password strength check for very weak password."""
        service = PasswordEncryptionService()

        result = service.check_password_strength("abc")

        assert result["score"] == 1  # Length < 8 (0) + lowercase only (1)
        assert result["length"] == 3
        assert result["has_lowercase"] is True
        assert result["has_uppercase"] is False
        assert result["has_numbers"] is False
        assert result["has_symbols"] is False
        assert result["strength_label"] == "Very Weak"

    def test_check_password_strength_weak(self):
        """Test password strength check for weak password."""
        service = PasswordEncryptionService()

        # 8 characters, lowercase and uppercase = score 3 (Weak)
        result = service.check_password_strength("Abcdefgh")

        assert result["score"] == 3  # Length 8 (1) + lowercase (1) + uppercase (1)
        assert result["length"] == 8
        assert result["has_lowercase"] is True
        assert result["has_uppercase"] is True
        assert result["has_numbers"] is False
        assert result["has_symbols"] is False
        assert result["strength_label"] == "Weak"

    def test_check_password_strength_medium(self):
        """Test password strength check for medium password."""
        service = PasswordEncryptionService()

        # 12 chars with lower, upper, numbers = score 5 (Medium)
        result = service.check_password_strength("Abcdefgh1234")

        assert result["score"] == 5  # Length 12 (2) + 3 char types (3)
        assert result["strength_label"] == "Medium"

    def test_check_password_strength_strong(self):
        """Test password strength check for strong password."""
        service = PasswordEncryptionService()

        # 12 chars with all types = score 6 (Strong)
        result = service.check_password_strength("Abcd1234!@#$")

        assert result["score"] == 6  # Length 12 (2) + 4 char types (4)
        assert result["strength_label"] == "Strong"

    def test_check_password_strength_very_strong(self):
        """Test password strength check for very strong password."""
        service = PasswordEncryptionService()

        # 16+ chars with all types = score 7+ (Very Strong)
        result = service.check_password_strength("Abcd1234!@#$efgh")

        assert result["score"] == 7  # Length 16 (3) + 4 char types (4)
        assert result["has_lowercase"] is True
        assert result["has_uppercase"] is True
        assert result["has_numbers"] is True
        assert result["has_symbols"] is True
        assert result["strength_label"] == "Very Strong"

    def test_encryption_service_singleton(self):
        """Test that encryption_service singleton is available."""
        assert encryption_service is not None
        assert isinstance(encryption_service, PasswordEncryptionService)
