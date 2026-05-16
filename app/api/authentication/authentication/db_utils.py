from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import uuid
from typing import Any

from .models import User, Token, UserSession, LoginAttempt
from .consts import AuthenticationConstants


def create_user_session(user: User, request: Any) -> UserSession:
    """
    Create a new user session.

    :param user: User instance
    :param request: HTTP request object
    :return: Created UserSession instance
    """
    ip_address = request.META.get("REMOTE_ADDR", None)
    user_agent = request.META.get("HTTP_USER_AGENT", "")

    return UserSession.objects.create(
        user=user,
        session_key=str(uuid.uuid4()),
        ip_address=ip_address,
        user_agent=user_agent,
    )


def log_login_attempt(
    email: str, user: User | None, successful: bool, request: Any
) -> LoginAttempt:
    """
    Log a login attempt.

    :param email: Email used for login
    :param user: User instance if found
    :param successful: Whether login was successful
    :param request: HTTP request object
    :return: Created LoginAttempt instance
    """
    ip_address = request.META.get("REMOTE_ADDR", None)
    user_agent = request.META.get("HTTP_USER_AGENT", "")

    return LoginAttempt.objects.create(
        user=user,
        email=email,
        ip_address=ip_address,
        user_agent=user_agent,
        successful=successful,
    )


def create_verification_token(user: User) -> Token:
    """
    Create an email verification token.

    :param user: User instance
    :return: Created Token instance
    """
    expiry = timezone.now() + timedelta(
        days=AuthenticationConstants.VERIFICATION_TOKEN_DAYS
    )
    return Token.objects.create(user=user, token_type="verification", expires_at=expiry)


def create_password_reset_token(user: User) -> Token:
    """
    Create a password reset token.

    :param user: User instance
    :return: Created Token instance
    """
    expiry = timezone.now() + timedelta(
        hours=AuthenticationConstants.PASSWORD_RESET_HOURS
    )
    return Token.objects.create(
        user=user, token_type="password_reset", expires_at=expiry
    )


def create_refresh_token(user: User, jti: str) -> Token:
    """
    Create a refresh token in database.

    :param user: User instance
    :param jti: JWT ID
    :return: Created Token instance
    """
    expiry = timezone.now() + timedelta(days=AuthenticationConstants.REFRESH_TOKEN_DAYS)
    return Token.objects.create(
        user=user, token=jti, token_type="refresh", expires_at=expiry
    )


@transaction.atomic
def create_user_with_verification(
    email: str,
    password: str,
    first_name: str | None = None,
    last_name: str | None = None,
) -> tuple[User, Token]:
    """
    Create a new user with verification token.

    :param email: User email
    :param password: User password
    :param first_name: User first name
    :param last_name: User last name
    :return: Tuple of (User, verification_token)
    """
    user = User.objects.create_user(
        email=email, password=password, first_name=first_name, last_name=last_name
    )

    verification_token = create_verification_token(user)
    return user, verification_token


def get_valid_token(token_str: str, token_type: str) -> Token | None:
    """
    Get a valid token by string and type.

    :param token_str: Token string
    :param token_type: Token type
    :return: Token instance or None if invalid
    """
    try:
        token = Token.objects.get(token=token_str, token_type=token_type, is_used=False)
        if token.is_expired:
            return None
        return token
    except Token.DoesNotExist:
        return None


def mark_token_used(token: Token) -> None:
    """
    Mark token as used.

    :param token: Token instance
    """
    token.is_used = True
    token.save(update_fields=["is_used"])


def get_user_active_sessions(user: User) -> list[UserSession]:
    """
    Get all active sessions for a user.

    :param user: User instance
    :return: List of active UserSession instances
    """
    return list(
        UserSession.objects.filter(user=user, is_active=True).order_by("-last_activity")
    )


def terminate_user_session(user: User, session_id: str) -> bool:
    """
    Terminate a specific user session.

    :param user: User instance
    :param session_id: Session ID to terminate
    :return: True if session was terminated, False if not found
    """
    try:
        session = UserSession.objects.get(id=session_id, user=user)
        session.is_active = False
        session.save(update_fields=["is_active"])
        return True
    except (UserSession.DoesNotExist, ValueError):
        # ValueError occurs when session_id is not a valid integer
        return False


def convert_salt_to_bytes(salt: Any) -> bytes:
    """
    Convert salt from any format to bytes.

    :param salt: Salt in various formats
    :return: Salt as bytes
    """
    if isinstance(salt, memoryview):
        return salt.tobytes()
    elif isinstance(salt, str):
        import base64

        try:
            return base64.b64decode(salt)
        except Exception:
            return salt.encode("utf-8")
    elif isinstance(salt, bytes):
        return salt
    else:
        return bytes(salt)


def log_password_access(
    password_entry: Any, user: User, action: str, request: Any
) -> Any:
    """
    Log password entry access.

    :param password_entry: PasswordEntry instance
    :param user: User instance
    :param action: Action performed
    :param request: HTTP request object
    :return: Created PasswordAccessLog instance
    """
    from .models import PasswordAccessLog

    return PasswordAccessLog.objects.create(
        password_entry=password_entry,
        user=user,
        action=action,
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
    )
