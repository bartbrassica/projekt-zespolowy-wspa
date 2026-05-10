from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import secrets
import logging
from typing import Tuple
from cryptography.fernet import InvalidToken
from .consts import (
    EncryptionConstants,
    PasswordStrengthScore,
    PasswordStrengthLabel,
    CharacterSets,
)

logger = logging.getLogger(__name__)


class PasswordEncryptionService:
    """
    Service for encrypting and decrypting passwords using Fernet (symmetric encryption)
    with PBKDF2 for key derivation from user's master password.
    """

    def __init__(self) -> None:
        self.iterations = EncryptionConstants.PBKDF2_ITERATIONS
        self.backend = default_backend()

    def generate_salt(self) -> bytes:
        """
        Generate a random salt for key derivation.

        :return: 32-byte random salt
        :rtype: bytes
        """
        return secrets.token_bytes(EncryptionConstants.SALT_LENGTH)

    def derive_key(self, master_password: str, salt: bytes) -> bytes:
        """
        Derive an encryption key from the user's master password using PBKDF2.

        :param master_password: User's master password
        :param salt: Random salt for this specific password entry
        :return: 32-byte encryption key
        :rtype: bytes
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=EncryptionConstants.KEY_LENGTH,
            salt=salt,
            iterations=self.iterations,
            backend=self.backend,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        return key

    def encrypt_password(
        self, password: str, master_password: str
    ) -> Tuple[str, bytes]:
        """
        Encrypt a password using the user's master password.

        :param password: The password to encrypt
        :param master_password: User's master password for key derivation
        :return: Tuple of (encrypted_password, salt)
        :rtype: Tuple[str, bytes]
        """
        salt = self.generate_salt()

        key = self.derive_key(master_password, salt)

        f = Fernet(key)
        encrypted = f.encrypt(password.encode())

        return base64.b64encode(encrypted).decode("utf-8"), salt

    def decrypt_password(
        self, encrypted_password: str, master_password: str, salt: bytes
    ) -> str | None:
        """
        Decrypt a password using the user's master password.

        :param encrypted_password: The encrypted password (base64 encoded)
        :param master_password: User's master password for key derivation
        :param salt: The salt used during encryption
        :return: Decrypted password or None if decryption fails
        """
        try:
            key = self.derive_key(master_password, salt)

            f = Fernet(key)
            encrypted_bytes = base64.b64decode(encrypted_password)
            decrypted = f.decrypt(encrypted_bytes)

            return decrypted.decode("utf-8")
        except InvalidToken:
            logger.error("Invalid token: Wrong master password or corrupted data")
            return None
        except ValueError as e:
            logger.error(f"Invalid base64 encoding: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected decryption error: {e}")
            return None

    def re_encrypt_password(
        self, encrypted_password: str, old_master: str, new_master: str, salt: bytes
    ) -> Tuple[str, bytes] | None:
        """
        Re-encrypt a password when the master password changes.

        :param encrypted_password: Currently encrypted password
        :param old_master: Old master password
        :param new_master: New master password
        :param salt: Current salt
        :return: Tuple of (new_encrypted_password, new_salt) or None if fails
        """
        decrypted = self.decrypt_password(encrypted_password, old_master, salt)
        if not decrypted:
            return None

        return self.encrypt_password(decrypted, new_master)

    def _validate_password_params(
        self,
        length: int,
        include_symbols: bool,
        include_numbers: bool,
        include_uppercase: bool,
        include_lowercase: bool,
    ) -> None:
        """
        Validate password generation parameters.

        :param length: Password length
        :param include_symbols: Include special characters
        :param include_numbers: Include numbers
        :param include_uppercase: Include uppercase letters
        :param include_lowercase: Include lowercase letters
        :raises ValueError: If parameters are invalid
        """
        if length < 1:
            raise ValueError("Password length must be at least 1")

        if not any(
            [include_symbols, include_numbers, include_uppercase, include_lowercase]
        ):
            raise ValueError("At least one character type must be included")

    def _build_character_set(
        self,
        include_symbols: bool,
        include_numbers: bool,
        include_uppercase: bool,
        include_lowercase: bool,
        exclude_ambiguous: bool,
    ) -> str:
        """
        Build character set for password generation.

        :param include_symbols: Include special characters
        :param include_numbers: Include numbers
        :param include_uppercase: Include uppercase letters
        :param include_lowercase: Include lowercase letters
        :param exclude_ambiguous: Exclude ambiguous characters
        :return: Combined character set
        """
        charset = ""

        if include_lowercase:
            charset += (
                CharacterSets.LOWERCASE_NO_AMBIGUOUS.value
                if exclude_ambiguous
                else CharacterSets.LOWERCASE.value
            )

        if include_uppercase:
            charset += (
                CharacterSets.UPPERCASE_NO_AMBIGUOUS.value
                if exclude_ambiguous
                else CharacterSets.UPPERCASE.value
            )

        if include_numbers:
            charset += (
                CharacterSets.NUMBERS_NO_AMBIGUOUS.value
                if exclude_ambiguous
                else CharacterSets.NUMBERS.value
            )

        if include_symbols:
            charset += CharacterSets.SYMBOLS.value

        return charset

    def _ensure_character_requirements(
        self,
        password_list: list,
        include_symbols: bool,
        include_numbers: bool,
        include_uppercase: bool,
        include_lowercase: bool,
        exclude_ambiguous: bool,
    ) -> list:
        """
        Ensure password contains at least one character from each required type.

        :param password_list: List of password characters
        :param include_symbols: Include special characters
        :param include_numbers: Include numbers
        :param include_uppercase: Include uppercase letters
        :param include_lowercase: Include lowercase letters
        :param exclude_ambiguous: Exclude ambiguous characters
        :return: Modified password list
        """
        required_chars = []

        if include_lowercase:
            chars = (
                CharacterSets.LOWERCASE_NO_AMBIGUOUS.value
                if exclude_ambiguous
                else CharacterSets.LOWERCASE.value
            )
            required_chars.append(secrets.choice(chars))

        if include_uppercase:
            chars = (
                CharacterSets.UPPERCASE_NO_AMBIGUOUS.value
                if exclude_ambiguous
                else CharacterSets.UPPERCASE.value
            )
            required_chars.append(secrets.choice(chars))

        if include_numbers:
            chars = (
                CharacterSets.NUMBERS_NO_AMBIGUOUS.value
                if exclude_ambiguous
                else CharacterSets.NUMBERS.value
            )
            required_chars.append(secrets.choice(chars))

        if include_symbols:
            required_chars.append(secrets.choice(CharacterSets.SYMBOLS.value))

        for i, char in enumerate(required_chars):
            if i < len(password_list):
                pos = secrets.randbelow(len(password_list))
                password_list[pos] = char

        return password_list

    def generate_secure_password(
        self,
        length: int = EncryptionConstants.DEFAULT_PASSWORD_LENGTH,
        include_symbols: bool = True,
        include_numbers: bool = True,
        include_uppercase: bool = True,
        include_lowercase: bool = True,
        exclude_ambiguous: bool = True,
    ) -> str:
        """
        Generate a cryptographically secure random password.

        :param length: Password length
        :param include_symbols: Include special characters
        :param include_numbers: Include numbers
        :param include_uppercase: Include uppercase letters
        :param include_lowercase: Include lowercase letters
        :param exclude_ambiguous: Exclude ambiguous characters (0, O, l, 1, etc.)
        :return: Generated password
        :rtype: str
        """
        self._validate_password_params(
            length,
            include_symbols,
            include_numbers,
            include_uppercase,
            include_lowercase,
        )

        charset = self._build_character_set(
            include_symbols,
            include_numbers,
            include_uppercase,
            include_lowercase,
            exclude_ambiguous,
        )

        password = "".join(secrets.choice(charset) for _ in range(length))
        password_list = list(password)

        password_list = self._ensure_character_requirements(
            password_list,
            include_symbols,
            include_numbers,
            include_uppercase,
            include_lowercase,
            exclude_ambiguous,
        )

        return "".join(password_list)

    def _calculate_length_score(self, length: int) -> int:
        """
        Calculate score points based on password length.

        :param length: Password length
        :return: Score points for length
        """
        score = 0
        if length >= 8:
            score += 1
        if length >= 12:
            score += 1
        if length >= 16:
            score += 1
        return score

    def _calculate_character_type_score(self, password: str) -> tuple:
        """
        Calculate score and flags for character type diversity.

        :param password: Password to analyze
        :return: Tuple of (score, has_lowercase, has_uppercase, has_numbers, has_symbols)
        """
        has_lowercase = bool(any(c.islower() for c in password))
        has_uppercase = bool(any(c.isupper() for c in password))
        has_numbers = bool(any(c.isdigit() for c in password))
        has_symbols = bool(any(not c.isalnum() for c in password))

        score = sum([has_lowercase, has_uppercase, has_numbers, has_symbols])
        return score, has_lowercase, has_uppercase, has_numbers, has_symbols

    def _determine_strength_label(self, score: int) -> str:
        """
        Determine strength label based on total score.

        :param score: Total password strength score
        :return: Strength label
        """
        if score <= PasswordStrengthScore.VERY_WEAK_MAX:
            return PasswordStrengthLabel.VERY_WEAK.value
        elif score <= PasswordStrengthScore.WEAK_MAX:
            return PasswordStrengthLabel.WEAK.value
        elif score <= PasswordStrengthScore.MEDIUM_MAX:
            return PasswordStrengthLabel.MEDIUM.value
        elif score <= PasswordStrengthScore.STRONG_MAX:
            return PasswordStrengthLabel.STRONG.value
        else:
            return PasswordStrengthLabel.VERY_STRONG.value

    def check_password_strength(self, password: str) -> dict:
        """
        Check the strength of a password.

        :param password: Password to check
        :return: Dictionary with strength metrics
        :rtype: dict
        """
        length = len(password)
        length_score = self._calculate_length_score(length)

        char_type_score, has_lowercase, has_uppercase, has_numbers, has_symbols = (
            self._calculate_character_type_score(password)
        )

        total_score = length_score + char_type_score

        return {
            "score": total_score,
            "length": length,
            "has_lowercase": has_lowercase,
            "has_uppercase": has_uppercase,
            "has_numbers": has_numbers,
            "has_symbols": has_symbols,
            "is_common": False,
            "strength_label": self._determine_strength_label(total_score),
        }


encryption_service = PasswordEncryptionService()
