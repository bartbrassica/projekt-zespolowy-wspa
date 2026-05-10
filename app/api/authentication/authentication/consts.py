from enum import Enum, IntEnum


class EncryptionConstants(IntEnum):
    """Encryption-related constants."""

    PBKDF2_ITERATIONS = 200_000
    SALT_LENGTH = 32
    KEY_LENGTH = 32
    DEFAULT_PASSWORD_LENGTH = 16


class PasswordStrengthScore(IntEnum):
    """Password strength score thresholds."""

    VERY_WEAK_MAX = 2
    WEAK_MAX = 3
    MEDIUM_MAX = 5
    STRONG_MAX = 6


class PasswordStrengthLabel(Enum):
    """Password strength labels."""

    VERY_WEAK = "Very Weak"
    WEAK = "Weak"
    MEDIUM = "Medium"
    STRONG = "Strong"
    VERY_STRONG = "Very Strong"


class CharacterSets(Enum):
    """Character sets for password generation."""

    LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
    LOWERCASE_NO_AMBIGUOUS = "abcdefghijkmnopqrstuvwxyz"
    UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    UPPERCASE_NO_AMBIGUOUS = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    NUMBERS = "0123456789"
    NUMBERS_NO_AMBIGUOUS = "23456789"
    SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"


class EmailConstants(Enum):
    """Email-related constants."""

    VERIFICATION_SUBJECT = "Verify Your Digital Lockbox Account"
    PASSWORD_RESET_SUBJECT = "Reset Your Digital Lockbox Password"
    WELCOME_SUBJECT = "Welcome to Digital Lockbox!"

    VERIFICATION_TEMPLATE_HTML = "emails/account_verification.html"
    VERIFICATION_TEMPLATE_TXT = "emails/account_verification.txt"

    TEAM_SIGNATURE = "Digital Lockbox Team"


class EmailMessages(Enum):
    """Email message templates."""

    PASSWORD_RESET_BODY = """
Hello {user_name},

You requested to reset your password for your Digital Lockbox account.

Click the link below to reset your password:
{reset_url}

This link will expire in 24 hours. If you didn't request this password reset, please ignore this email.

---
{team_signature}
"""

    WELCOME_BODY = """
Hello {user_name},

Welcome to Digital Lockbox! Your account has been successfully verified.

You can now start using Digital Lockbox to securely store and manage your passwords.

Get started: {app_url}

Features you can now use:
- Store unlimited passwords securely
- Generate strong, unique passwords
- Access your passwords from any device
- Organize passwords with folders and tags

Thank you for choosing Digital Lockbox to keep your digital life secure!

---
{team_signature}
"""


class PasswordExpirationConstants(Enum):
    """Password expiration constants."""

    WARNING_DAYS_3 = 3
    WARNING_DAYS_1 = 1

    NOTIFICATION_TYPE_3_DAYS = "3_days"
    NOTIFICATION_TYPE_1_DAY = "1_day"
    NOTIFICATION_TYPE_EXPIRED = "expired"

    SUBJECT_3_DAYS = "Password Expiration Warning - 3 Days Remaining"
    SUBJECT_1_DAY = "Password Expiration Alert - 1 Day Remaining"
    SUBJECT_EXPIRED = "Password Expired - Immediate Action Required"

    TEMPLATE_3_DAYS = "emails/password_expiring_3_days"
    TEMPLATE_1_DAY = "emails/password_expiring_1_day"
    TEMPLATE_EXPIRED = "emails/password_expired"


class AuthenticationConstants(IntEnum):
    """Authentication-related constants."""

    ACCESS_TOKEN_MINUTES = 15
    REFRESH_TOKEN_DAYS = 14
    VERIFICATION_TOKEN_DAYS = 3
    PASSWORD_RESET_HOURS = 24
    SESSION_EXPIRY_DAYS = 14


class JWTConstants(Enum):
    """JWT-related constants."""

    ALGORITHM = "ES512"
    CURVE_TYPE = "SECP521R1"
    ACCESS_TOKEN_TYPE = "access"
    REFRESH_TOKEN_TYPE = "refresh"


class FileConstants(Enum):
    """File and path constants."""

    KEYS_DIR = "keys"
    PRIVATE_KEY_FILE = "jwt-private.pem"
    PUBLIC_KEY_FILE = "jwt-public.pem"


class PasswordManagerConstants(Enum):
    """Password manager related constants."""

    VALID_SORT_FIELDS = ["name", "site", "created_at", "updated_at", "expires_at"]
    DEFAULT_SORT_FIELD = "updated_at"
    DEFAULT_PASSWORD_EXPIRY_WARNING_DAYS = 30
