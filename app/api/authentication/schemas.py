from ninja import Schema
from pydantic import EmailStr, Field, field_validator
from datetime import datetime
import re
import uuid


class UserIn(Schema):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    
    @field_validator('password')
    def password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[^A-Za-z0-9]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserOut(Schema):
    id: str
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    is_verified: bool
    date_joined: datetime
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_string(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v


class UserUpdate(Schema):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    phone_number: str | None = None


class LoginIn(Schema):
    email: EmailStr
    password: str
    remember_me: bool | None = False


class TokenOut(Schema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenIn(Schema):
    refresh_token: str


class PasswordChangeIn(Schema):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @field_validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @field_validator('new_password')
    def password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[^A-Za-z0-9]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class PasswordResetRequestIn(Schema):
    email: EmailStr


class PasswordResetConfirmIn(Schema):
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @field_validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class EmailVerificationIn(Schema):
    token: str


class SessionOut(Schema):
    id: str
    device_name: str | None
    ip_address: str | None
    user_agent: str | None
    created_at: datetime
    last_activity: datetime
    is_active: bool


class SessionListOut(Schema):
    sessions: list[SessionOut]


class ErrorOut(Schema):
    message: str
    code: str | None = None
    details: dict | None = None


class MessageOut(Schema):
    message: str


class PermissionOut(Schema):
    name: str
    granted: bool
    expires_at: datetime | None = None


class PermissionListOut(Schema):
    permissions: list[PermissionOut]


class TwoFactorSetupOut(Schema):
    secret: str
    qr_code_url: str


class TwoFactorVerifyIn(Schema):
    code: str


class TwoFactorLoginIn(Schema):
    email: EmailStr
    password: str
    code: str
