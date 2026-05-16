from ninja import Schema
from pydantic import EmailStr, Field, field_validator, HttpUrl
from datetime import datetime
import re
import uuid


class UserIn(Schema):
    """Schema for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserOut(Schema):
    """Schema for user output."""

    id: str
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    is_verified: bool
    date_joined: datetime

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid_to_string(cls, v: uuid.UUID | str) -> str:
        if isinstance(v, uuid.UUID):
            return str(v)
        return v


class UserUpdate(Schema):
    """Schema for user profile updates."""

    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    phone_number: str | None = None


class LoginIn(Schema):
    """Schema for user login."""

    email: EmailStr
    password: str
    remember_me: bool | None = False


class TokenOut(Schema):
    """Schema for authentication token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenIn(Schema):
    """Schema for refresh token request."""

    refresh_token: str


class PasswordChangeIn(Schema):
    """Schema for password change request."""

    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if (
            hasattr(info, "data")
            and "new_password" in info.data
            and v != info.data["new_password"]
        ):
            raise ValueError("Passwords do not match")
        return v

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class PasswordResetRequestIn(Schema):
    """Schema for password reset request."""

    email: EmailStr


class PasswordResetConfirmIn(Schema):
    """Schema for password reset confirmation."""

    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if (
            hasattr(info, "data")
            and "new_password" in info.data
            and v != info.data["new_password"]
        ):
            raise ValueError("Passwords do not match")
        return v


class EmailVerificationIn(Schema):
    """Schema for email verification."""

    token: str


class SessionOut(Schema):
    """Schema for user session output."""

    id: str
    device_name: str | None
    ip_address: str | None
    user_agent: str | None
    created_at: datetime
    last_activity: datetime
    is_active: bool

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_string(cls, v: int | str) -> str:
        """Convert integer ID to string."""
        return str(v)


class SessionListOut(Schema):
    """Schema for session list output."""

    sessions: list[SessionOut]


class TwoFactorSetupOut(Schema):
    """Schema for 2FA setup output."""

    secret: str
    qr_code_url: str


class TwoFactorVerifyIn(Schema):
    """Schema for 2FA verification."""

    code: str


class TwoFactorLoginIn(Schema):
    """Schema for 2FA login."""

    email: EmailStr
    password: str
    code: str


class PasswordEntryIn(Schema):
    """Schema for creating a new password entry."""

    name: str = Field(..., min_length=1, max_length=255)
    site: HttpUrl | None = None
    username: str | None = Field(None, max_length=255)
    password: str = Field(..., min_length=1)
    notes: str | None = None
    expires_at: datetime | None = None
    folder_id: str | None = None
    tags: list[str] | None = []
    is_favorite: bool = False

    # Master password for encryption
    master_password: str = Field(
        ..., description="User's master password for encryption"
    )


class PasswordEntryUpdate(Schema):
    """Schema for updating a password entry."""

    name: str | None = Field(None, min_length=1, max_length=255)
    site: HttpUrl | None = None
    username: str | None = Field(None, max_length=255)
    password: str | None = Field(None, min_length=1)
    notes: str | None = None
    expires_at: datetime | None = None
    folder_id: str | None = None
    tags: list[str] | None = None
    is_favorite: bool | None = None

    # Master password required for re-encryption if password changes
    master_password: str = Field(
        ..., description="User's master password for encryption"
    )


class PasswordEntryOut(Schema):
    """Schema for password entry output (without decrypted password)."""

    id: str
    name: str
    site: str | None = None
    username: str | None = None
    notes: str | None = None
    expires_at: datetime | None = None
    is_expired: bool
    days_until_expiry: int | None = None
    folder: "FolderOut | None" = None
    tags: list["TagOut"] = []
    is_favorite: bool
    created_at: datetime
    updated_at: datetime
    last_accessed: datetime | None = None

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid_to_string(cls, v: uuid.UUID | str) -> str:
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    @field_validator("site", mode="before")
    @classmethod
    def convert_url_to_string(cls, v: HttpUrl | str | None) -> str | None:
        """Convert HttpUrl object to string."""
        if v is None:
            return None
        # If it's an HttpUrl object, convert to string
        if hasattr(v, "__str__"):
            return str(v)
        return v


class PasswordDecryptRequest(Schema):
    """Schema for requesting password decryption."""

    master_password: str = Field(
        ..., description="User's master password for decryption"
    )


class PasswordDecryptResponse(Schema):
    """Schema for decrypted password response."""

    password: str
    strength: dict[str, str | int | bool]


class PasswordGenerateRequest(Schema):
    """Schema for password generation request."""

    length: int = Field(16, ge=8, le=128)
    include_symbols: bool = True
    include_numbers: bool = True
    include_uppercase: bool = True
    include_lowercase: bool = True
    exclude_ambiguous: bool = True


class PasswordGenerateResponse(Schema):
    """Schema for generated password response."""

    password: str
    strength: dict[str, str | int | bool]


class PasswordListFilters(Schema):
    """Schema for listing/filtering passwords via query parameters."""

    query: str | None = None
    folder_id: str | None = None
    tags: list[str] | None = None
    show_expired: bool | None = None
    show_favorites_only: bool | None = None
    sort_by: str | None = None
    sort_order: str | None = None
    limit: int | None = None
    offset: int | None = None


class PasswordSearchRequest(Schema):
    """Schema for searching passwords."""

    query: str | None = None
    folder_id: str | None = None
    tags: list[str] | None = []
    show_expired: bool = False
    show_favorites_only: bool = False
    sort_by: str = Field(
        "updated_at", pattern="^(name|site|created_at|updated_at|expires_at)$"
    )
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)


class PasswordBulkDeleteRequest(Schema):
    """Schema for bulk delete request."""

    entry_ids: list[str]
    master_password: str = Field(
        ..., description="User's master password for verification"
    )


class MasterPasswordChangeRequest(Schema):
    """Schema for changing master password and re-encrypting all entries."""

    current_master_password: str
    new_master_password: str = Field(..., min_length=8)
    confirm_master_password: str

    @field_validator("confirm_master_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if (
            hasattr(info, "data")
            and "new_master_password" in info.data
            and v != info.data["new_master_password"]
        ):
            raise ValueError("Passwords do not match")
        return v


class PasswordImportRequest(Schema):
    """Schema for importing passwords from CSV/JSON."""

    format: str = Field(..., pattern="^(csv|json|bitwarden|lastpass|1password)$")
    data: str = Field(..., description="Base64 encoded file data")
    master_password: str = Field(
        ..., description="User's master password for encryption"
    )


class PasswordExportRequest(Schema):
    """Schema for exporting passwords."""

    format: str = Field(..., pattern="^(csv|json|pdf)$")
    master_password: str = Field(
        ..., description="User's master password for decryption"
    )
    include_passwords: bool = False
    folder_id: str | None = None
    tag_ids: list[str] | None = []


class FolderIn(Schema):
    """Schema for creating a folder."""

    name: str = Field(..., min_length=1, max_length=100)
    parent_id: str | None = None
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, pattern="^#[0-9A-Fa-f]{6}$")


class FolderUpdate(Schema):
    """Schema for updating a folder."""

    name: str | None = Field(None, min_length=1, max_length=100)
    parent_id: str | None = None
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, pattern="^#[0-9A-Fa-f]{6}$")


class FolderOut(Schema):
    """Schema for folder output."""

    id: str
    name: str
    parent_id: str | None = None
    icon: str | None = None
    color: str | None = None
    entry_count: int = 0
    created_at: datetime
    updated_at: datetime

    @field_validator("id", "parent_id", mode="before")
    @classmethod
    def convert_uuid_to_string(cls, v: uuid.UUID | str | None) -> str | None:
        if isinstance(v, uuid.UUID):
            return str(v)
        return v


class TagIn(Schema):
    """Schema for creating a tag."""

    name: str = Field(..., min_length=1, max_length=50)
    color: str | None = Field(None, pattern="^#[0-9A-Fa-f]{6}$")


class TagOut(Schema):
    """Schema for tag output."""

    id: str
    name: str
    color: str | None = None
    entry_count: int = 0
    created_at: datetime

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid_to_string(cls, v: uuid.UUID | str) -> str:
        if isinstance(v, uuid.UUID):
            return str(v)
        return v


class ShareLinkIn(Schema):
    """Schema for creating a share link."""

    password_entry_id: str
    master_password: str = Field(
        ..., description="User's master password for decryption"
    )
    max_views: int = Field(1, ge=1, le=100)
    expires_in_hours: int = Field(24, ge=1, le=168)  # Max 1 week
    require_authentication: bool = False
    allowed_email: str | None = None


class ShareLinkOut(Schema):
    """Schema for share link output."""

    id: str
    share_url: str
    max_views: int
    current_views: int
    expires_at: datetime
    require_authentication: bool
    allowed_email: str | None = None
    created_at: datetime

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid_to_string(cls, v: uuid.UUID | str) -> str:
        if isinstance(v, uuid.UUID):
            return str(v)
        return v


class ErrorOut(Schema):
    """Schema for error responses."""

    message: str
    code: str | None = None
    details: dict | None = None


class MessageOut(Schema):
    """Schema for simple message responses."""

    message: str


class PermissionOut(Schema):
    """Schema for permission output."""

    name: str
    granted: bool
    expires_at: datetime | None = None


class PermissionListOut(Schema):
    """Schema for permission list output."""

    permissions: list[PermissionOut]
