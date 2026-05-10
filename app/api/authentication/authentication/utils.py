from django.utils import timezone
from django.conf import settings
from django.http import HttpRequest
from datetime import datetime, timedelta, date
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
import jwt
import uuid
from typing import Any

from .models import User
from .consts import AuthenticationConstants, JWTConstants, FileConstants


def get_date_range_for_day(
    target_date: date,
) -> tuple[datetime, datetime]:
    """
    Get start and end datetime for a specific date.

    :param target_date: The target date
    :return: Tuple of (start_of_day, end_of_day) as timezone-aware datetimes
    """
    start_of_day = timezone.make_aware(
        datetime.combine(target_date, datetime.min.time())
    )
    end_of_day = timezone.make_aware(datetime.combine(target_date, datetime.max.time()))
    return start_of_day, end_of_day


def serialize_password_data(password_entry: Any) -> dict[str, Any]:
    """
    Serialize password entry data for email templates.

    :param password_entry: Password entry instance
    :return: Serialized password data dictionary
    """
    return {
        "name": password_entry.name,
        "site": password_entry.site,
        "username": password_entry.username,
        "expires_at": password_entry.expires_at,
        "days_until_expiry": password_entry.days_until_expiry,
    }


def load_jwt_keys() -> tuple[bytes, bytes]:
    """
    Load or generate JWT private and public keys.

    :return: Tuple of (private_key, public_key) as bytes
    """
    keys_dir = Path(settings.BASE_DIR) / FileConstants.KEYS_DIR.value
    keys_dir.mkdir(exist_ok=True)

    private_key_path = keys_dir / FileConstants.PRIVATE_KEY_FILE.value
    public_key_path = keys_dir / FileConstants.PUBLIC_KEY_FILE.value

    if not private_key_path.exists() or not public_key_path.exists():
        private_key = ec.generate_private_key(
            curve=ec.SECP521R1(), backend=default_backend()
        )

        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        public_key = private_key.public_key()
        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        with open(private_key_path, "wb") as f:
            f.write(pem_private)

        with open(public_key_path, "wb") as f:
            f.write(pem_public)

    with open(private_key_path, "rb") as f:
        private_key = f.read()

    with open(public_key_path, "rb") as f:
        public_key = f.read()

    return private_key, public_key


def create_jwt_tokens(user: User) -> dict[str, Any]:
    """
    Create JWT access and refresh tokens for user.

    :param user: User instance
    :return: Dictionary with token information
    """
    private_key, _ = load_jwt_keys()

    access_token_expiry = timezone.now() + timedelta(
        minutes=AuthenticationConstants.ACCESS_TOKEN_MINUTES
    )
    refresh_token_expiry = timezone.now() + timedelta(
        days=AuthenticationConstants.REFRESH_TOKEN_DAYS
    )

    access_payload = {
        "user_id": str(user.id),
        "exp": access_token_expiry.timestamp(),
        "iat": timezone.now().timestamp(),
        "token_type": JWTConstants.ACCESS_TOKEN_TYPE.value,
    }

    jti = str(uuid.uuid4())

    refresh_payload = {
        "user_id": str(user.id),
        "exp": refresh_token_expiry.timestamp(),
        "iat": timezone.now().timestamp(),
        "token_type": JWTConstants.REFRESH_TOKEN_TYPE.value,
        "jti": jti,
    }

    access_token = jwt.encode(
        access_payload, private_key, algorithm=JWTConstants.ALGORITHM.value
    )

    refresh_token = jwt.encode(
        refresh_payload, private_key, algorithm=JWTConstants.ALGORITHM.value
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": AuthenticationConstants.ACCESS_TOKEN_MINUTES * 60,
        "jti": jti,
    }


def verify_jwt_token(token: str) -> dict[str, Any] | None:
    """
    Verify and decode JWT token.

    :param token: JWT token string
    :return: Decoded payload or None if invalid
    """
    try:
        _, public_key = load_jwt_keys()
        payload = jwt.decode(
            token, public_key, algorithms=[JWTConstants.ALGORITHM.value]
        )
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def verify_master_password(user: User, master_password: str) -> bool:
    """
    Verify user's master password.

    :param user: User instance
    :param master_password: Password to verify
    :return: True if password is correct
    """
    return user.check_password(master_password)


def get_client_ip(request: HttpRequest) -> str | None:
    """
    Get client IP address from request.

    :param request: HTTP request object
    :return: IP address or None
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def get_user_agent(request: HttpRequest) -> str:
    """
    Get user agent from request.

    :param request: HTTP request object
    :return: User agent string
    """
    return request.META.get("HTTP_USER_AGENT", "")
