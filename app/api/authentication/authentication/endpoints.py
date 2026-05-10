from ninja import Router
from ninja.security import HttpBearer
from ninja.errors import HttpError
from django.http import HttpRequest
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db import transaction
from typing import Any

from .models import User, Token
from .schemas import (
    UserIn,
    UserOut,
    UserUpdate,
    LoginIn,
    TokenOut,
    RefreshTokenIn,
    PasswordChangeIn,
    PasswordResetRequestIn,
    PasswordResetConfirmIn,
    EmailVerificationIn,
    SessionListOut,
    ErrorOut,
    MessageOut,
)
from .email_service import EmailService
from .utils import create_jwt_tokens, verify_jwt_token
from .db_utils import (
    create_user_session,
    log_login_attempt,
    create_verification_token,
    create_password_reset_token,
    create_refresh_token,
    create_user_with_verification,
    get_valid_token,
    mark_token_used,
    get_user_active_sessions,
    terminate_user_session,
)
from .consts import AuthenticationConstants, JWTConstants

auth_router = Router(tags=["Authentication"])


class JWTAuth(HttpBearer):
    """JWT Authentication handler."""

    def authenticate(self, request: HttpRequest, token: str) -> User | None:
        """
        Authenticate user from JWT token.

        :param request: HTTP request
        :param token: JWT token string
        :return: User instance or None if authentication fails
        """
        payload = verify_jwt_token(token)
        if not payload:
            return None

        user_id = payload.get("user_id")
        exp = payload.get("exp")

        if not user_id or not exp:
            return None

        if exp < timezone.now().timestamp():
            return None

        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None


auth_jwt = JWTAuth()


def get_user_from_auth(auth: Any) -> User:
    """
    Get User object from auth parameter.

    :param auth: Authentication object
    :return: User instance
    :raises HttpError: If authentication is invalid
    """
    if not auth:
        raise HttpError(401, "Authentication required")

    if hasattr(auth, "check_password"):
        return auth

    if isinstance(auth, str):
        try:
            return User.objects.get(id=auth)
        except User.DoesNotExist:
            raise HttpError(401, "Invalid authentication")

    raise HttpError(401, "Invalid authentication")


@auth_router.post("/register", response={201: UserOut, 400: ErrorOut})
@transaction.atomic
def register_user(request: HttpRequest, data: UserIn) -> tuple[int, User]:
    """Register a new user."""
    if User.objects.filter(email=data.email).exists():
        raise HttpError(400, "User with this email already exists")

    user, verification_token = create_user_with_verification(
        email=data.email,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
    )

    EmailService.send_verification_email(user, verification_token)
    return 201, user


@auth_router.post("/login", response={200: TokenOut, 400: ErrorOut, 401: ErrorOut})
def login_user(request: HttpRequest, data: LoginIn) -> dict[str, Any]:
    """User login endpoint."""
    user = authenticate(email=data.email, password=data.password)

    if not user:
        log_login_attempt(data.email, None, False, request)
        raise HttpError(401, "Invalid credentials")

    if not user.is_active:
        log_login_attempt(data.email, user, False, request)
        raise HttpError(401, "User account is disabled")

    if not user.is_verified:
        log_login_attempt(data.email, user, False, request)
        raise HttpError(401, "Please verify your email address before logging in")

    log_login_attempt(data.email, user, True, request)
    create_user_session(user, request)

    user.last_login = timezone.now()
    user.save(update_fields=["last_login"])

    tokens = create_jwt_tokens(user)
    create_refresh_token(user, tokens["jti"])

    if data.remember_me:
        request.session.set_expiry(
            AuthenticationConstants.SESSION_EXPIRY_DAYS * 24 * 60 * 60
        )
    else:
        request.session.set_expiry(0)

    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": tokens["token_type"],
        "expires_in": tokens["expires_in"],
    }


@auth_router.post("/token/refresh", response={200: TokenOut, 401: ErrorOut})
def refresh_token(request: HttpRequest, data: RefreshTokenIn) -> dict[str, Any]:
    """Refresh JWT token."""
    payload = verify_jwt_token(data.refresh_token)
    if not payload:
        raise HttpError(401, "Invalid refresh token")

    if payload.get("token_type") != JWTConstants.REFRESH_TOKEN_TYPE.value:
        raise HttpError(401, "Invalid token type")

    jti = payload.get("jti")
    if not jti:
        raise HttpError(401, "Invalid token format")

    token = get_valid_token(jti, "refresh")
    if not token:
        raise HttpError(401, "Token not found or expired")

    user = token.user
    if not user.is_active:
        raise HttpError(401, "User account is disabled")

    mark_token_used(token)
    tokens = create_jwt_tokens(user)
    create_refresh_token(user, tokens["jti"])

    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": tokens["token_type"],
        "expires_in": tokens["expires_in"],
    }


@auth_router.post("/logout", response={200: MessageOut}, auth=auth_jwt)
def logout_user(request: HttpRequest) -> dict[str, str]:
    """User logout endpoint."""
    user = get_user_from_auth(request.auth)

    Token.objects.filter(user=user, token_type="refresh", is_used=False).update(
        is_used=True
    )

    return {"message": "Successfully logged out"}


@auth_router.get("/me", response={200: UserOut, 401: ErrorOut}, auth=auth_jwt)
def get_current_user(request: HttpRequest) -> User:
    """Get current user profile."""
    return get_user_from_auth(request.auth)


@auth_router.put("/me", response={200: UserOut, 401: ErrorOut}, auth=auth_jwt)
def update_user(request: HttpRequest, data: UserUpdate) -> User:
    """Update user profile."""
    user = get_user_from_auth(request.auth)

    for field, value in data.dict(exclude_unset=True).items():
        if hasattr(user, field):
            setattr(user, field, value)

    user.save()
    return user


@auth_router.post(
    "/password/change",
    response={200: MessageOut, 400: ErrorOut, 401: ErrorOut},
    auth=auth_jwt,
)
def change_password(request: HttpRequest, data: PasswordChangeIn) -> dict[str, str]:
    """Change user password."""
    user = get_user_from_auth(request.auth)

    if not user.check_password(data.current_password):
        raise HttpError(400, "Current password is incorrect")

    user.set_password(data.new_password)
    user.save()

    Token.objects.filter(user=user, token_type="refresh", is_used=False).update(
        is_used=True
    )

    return {"message": "Password changed successfully"}


@auth_router.post("/password/reset/request", response={200: MessageOut, 404: ErrorOut})
def request_password_reset(
    request: HttpRequest, data: PasswordResetRequestIn
) -> dict[str, str]:
    """Request password reset."""
    try:
        user = User.objects.get(email=data.email, is_active=True)
        reset_token = create_password_reset_token(user)
        EmailService.send_password_reset_email(user, reset_token)
    except User.DoesNotExist:
        pass

    return {
        "message": "If your email is registered, you will receive password reset instructions"
    }


@auth_router.post("/password/reset/confirm", response={200: MessageOut, 400: ErrorOut})
def confirm_password_reset(
    request: HttpRequest, data: PasswordResetConfirmIn
) -> dict[str, str]:
    """Confirm password reset."""
    token = get_valid_token(data.token, "password_reset")
    if not token:
        raise HttpError(400, "Invalid or expired reset token")

    user = token.user
    user.set_password(data.new_password)
    user.save()

    mark_token_used(token)

    Token.objects.filter(user=user, token_type="refresh", is_used=False).update(
        is_used=True
    )

    return {"message": "Password reset successfully"}


@auth_router.post("/verify-email", response={200: MessageOut, 400: ErrorOut})
def verify_email_post(
    request: HttpRequest, data: EmailVerificationIn
) -> dict[str, str]:
    """Verify email address via POST."""
    token = get_valid_token(data.token, "verification")
    if not token:
        raise HttpError(400, "Invalid or expired verification token")

    user = token.user
    if user.is_verified:
        return {"message": "Email already verified"}

    user.is_verified = True
    user.save(update_fields=["is_verified"])

    mark_token_used(token)
    EmailService.send_welcome_email(user)

    return {"message": "Email verified successfully"}


@auth_router.get("/verify-email/{token}")
def verify_email_get(request: HttpRequest, token: str) -> dict[str, str]:
    """Verify email address via GET."""
    verification_token = get_valid_token(token, "verification")
    if not verification_token:
        raise HttpError(400, "Invalid or expired verification token")

    user = verification_token.user
    if user.is_verified:
        return {"message": "Email already verified"}

    user.is_verified = True
    user.save(update_fields=["is_verified"])

    mark_token_used(verification_token)
    EmailService.send_welcome_email(user)

    return {"message": "Email verified successfully"}


@auth_router.post(
    "/resend-verification", response={200: MessageOut, 400: ErrorOut}, auth=auth_jwt
)
def resend_verification_email(request: HttpRequest) -> dict[str, str]:
    """Resend verification email."""
    user = get_user_from_auth(request.auth)

    if user.is_verified:
        raise HttpError(400, "Email is already verified")

    Token.objects.filter(user=user, token_type="verification", is_used=False).update(
        is_used=True
    )

    verification_token = create_verification_token(user)
    EmailService.send_verification_email(user, verification_token)

    return {"message": "Verification email sent"}


@auth_router.get(
    "/verification-status", response={200: dict, 401: ErrorOut}, auth=auth_jwt
)
def get_verification_status(request: HttpRequest) -> dict[str, Any]:
    """Get user verification status."""
    user = get_user_from_auth(request.auth)

    pending_token = Token.objects.filter(
        user=user, token_type="verification", is_used=False
    ).first()

    return {
        "is_verified": user.is_verified,
        "verification_pending": pending_token is not None,
        "verification_sent_at": pending_token.created_at if pending_token else None,
    }


@auth_router.get(
    "/sessions", response={200: SessionListOut, 401: ErrorOut}, auth=auth_jwt
)
def list_sessions(request: HttpRequest) -> dict[str, list]:
    """List user sessions."""
    user = get_user_from_auth(request.auth)
    sessions = get_user_active_sessions(user)
    return {"sessions": sessions}


@auth_router.delete(
    "/sessions/{session_id}",
    response={200: MessageOut, 401: ErrorOut, 404: ErrorOut},
    auth=auth_jwt,
)
def terminate_session(request: HttpRequest, session_id: str) -> dict[str, str]:
    """Terminate a specific session."""
    user = get_user_from_auth(request.auth)

    if not terminate_user_session(user, session_id):
        raise HttpError(404, "Session not found")

    return {"message": "Session terminated successfully"}
