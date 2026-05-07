from ninja import Schema
from pydantic import Field, field_validator, HttpUrl
from datetime import datetime
from typing import Optional, List
import uuid


class PasswordEntryIn(Schema):
    """Schema for creating a new password entry"""
    name: str = Field(..., min_length=1, max_length=255)
    site: Optional[HttpUrl] = None
    username: Optional[str] = Field(None, max_length=255)
    password: str = Field(..., min_length=1)
    notes: Optional[str] = None
    expires_at: Optional[datetime] = None
    folder_id: Optional[str] = None
    tags: Optional[List[str]] = []
    is_favorite: bool = False
    
    # Master password for encryption
    master_password: str = Field(..., description="User's master password for encryption")


class PasswordEntryUpdate(Schema):
    """Schema for updating a password entry"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    site: Optional[HttpUrl] = None
    username: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=1)
    notes: Optional[str] = None
    expires_at: Optional[datetime] = None
    folder_id: Optional[str] = None
    tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = None
    
    # Master password required for re-encryption if password changes
    master_password: str = Field(..., description="User's master password for encryption")


class PasswordEntryOut(Schema):
    """Schema for password entry output (without decrypted password)"""
    id: str
    name: str
    site: Optional[str] = None
    username: Optional[str] = None
    notes: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_expired: bool
    days_until_expiry: Optional[int] = None
    folder: Optional['FolderOut'] = None
    tags: List['TagOut'] = []
    is_favorite: bool
    created_at: datetime
    updated_at: datetime
    last_accessed: Optional[datetime] = None
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_string(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v
    
    @field_validator('site', mode='before')
    @classmethod
    def convert_url_to_string(cls, v):
        """Convert HttpUrl object to string"""
        if v is None:
            return None
        # If it's an HttpUrl object, convert to string
        if hasattr(v, '__str__'):
            return str(v)
        return v


class PasswordDecryptRequest(Schema):
    """Schema for requesting password decryption"""
    master_password: str = Field(..., description="User's master password for decryption")


class PasswordDecryptResponse(Schema):
    """Schema for decrypted password response"""
    password: str
    strength: dict


class PasswordGenerateRequest(Schema):
    """Schema for password generation request"""
    length: int = Field(16, ge=8, le=128)
    include_symbols: bool = True
    include_numbers: bool = True
    include_uppercase: bool = True
    include_lowercase: bool = True
    exclude_ambiguous: bool = True


class PasswordGenerateResponse(Schema):
    """Schema for generated password response"""
    password: str
    strength: dict


class FolderIn(Schema):
    """Schema for creating a folder"""
    name: str = Field(..., min_length=1, max_length=100)
    parent_id: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")


class FolderUpdate(Schema):
    """Schema for updating a folder"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    parent_id: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")


class FolderOut(Schema):
    """Schema for folder output"""
    id: str
    name: str
    parent_id: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    entry_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    @field_validator('id', 'parent_id', mode='before')
    @classmethod
    def convert_uuid_to_string(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v


class TagIn(Schema):
    """Schema for creating a tag"""
    name: str = Field(..., min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")


class TagOut(Schema):
    """Schema for tag output"""
    id: str
    name: str
    color: Optional[str] = None
    entry_count: int = 0
    created_at: datetime
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_string(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v


class ShareLinkIn(Schema):
    """Schema for creating a share link"""
    password_entry_id: str
    master_password: str = Field(..., description="User's master password for decryption")
    max_views: int = Field(1, ge=1, le=100)
    expires_in_hours: int = Field(24, ge=1, le=168)  # Max 1 week
    require_authentication: bool = False
    allowed_email: Optional[str] = None


class ShareLinkOut(Schema):
    """Schema for share link output"""
    id: str
    share_url: str
    max_views: int
    current_views: int
    expires_at: datetime
    require_authentication: bool
    allowed_email: Optional[str] = None
    created_at: datetime
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_string(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v


class PasswordSearchRequest(Schema):
    """Schema for searching passwords"""
    query: Optional[str] = None
    folder_id: Optional[str] = None
    tags: Optional[List[str]] = []
    show_expired: bool = False
    show_favorites_only: bool = False
    sort_by: str = Field("updated_at", pattern="^(name|site|created_at|updated_at|expires_at)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)


class PasswordBulkDeleteRequest(Schema):
    """Schema for bulk delete request"""
    entry_ids: List[str]
    master_password: str = Field(..., description="User's master password for verification")


class MasterPasswordChangeRequest(Schema):
    """Schema for changing master password and re-encrypting all entries"""
    current_master_password: str
    new_master_password: str = Field(..., min_length=8)
    confirm_master_password: str
    
    @field_validator('confirm_master_password')
    def passwords_match(cls, v, values):
        if 'new_master_password' in values.data and v != values.data['new_master_password']:
            raise ValueError('Passwords do not match')
        return v


class PasswordImportRequest(Schema):
    """Schema for importing passwords from CSV/JSON"""
    format: str = Field(..., pattern="^(csv|json|bitwarden|lastpass|1password)$")
    data: str = Field(..., description="Base64 encoded file data")
    master_password: str = Field(..., description="User's master password for encryption")


class PasswordExportRequest(Schema):
    """Schema for exporting passwords"""
    format: str = Field(..., pattern="^(csv|json|pdf)$")
    master_password: str = Field(..., description="User's master password for decryption")
    include_passwords: bool = False
    folder_id: Optional[str] = None
    tag_ids: Optional[List[str]] = []
