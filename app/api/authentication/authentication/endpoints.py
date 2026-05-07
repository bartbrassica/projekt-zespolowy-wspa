from ninja import Router
from ninja.security import HttpBearer
from ninja.errors import HttpError
from django.http import HttpRequest
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db import transaction
from django.conf import settings
import jwt
import uuid
import datetime
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend

from .models import User, Token, UserSession, LoginAttempt
from .schemas import (
    UserIn, UserOut, UserUpdate, LoginIn, TokenOut, RefreshTokenIn,
    PasswordChangeIn, PasswordResetRequestIn, PasswordResetConfirmIn,
    EmailVerificationIn, SessionListOut, ErrorOut, MessageOut
)

auth_router = Router(tags=["Authentication"])


# Load ES512 private and public keys
def load_keys():
    keys_dir = Path(settings.BASE_DIR) / 'keys'

    # Create directory if it doesn't exist
    keys_dir.mkdir(exist_ok=True)

    private_key_path = keys_dir / 'jwt-private.pem'
    public_key_path = keys_dir / 'jwt-public.pem'

    # Generate keys if they don't exist
    if not private_key_path.exists() or not public_key_path.exists():
        # Generate a new EC key
        private_key = ec.generate_private_key(
            curve=ec.SECP521R1(),
            backend=default_backend()
        )

        # Serialize private key
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Serialize public key
        public_key = private_key.public_key()
        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Write keys to files
        with open(private_key_path, 'wb') as f:
            f.write(pem_private)
        
        with open(public_key_path, 'wb') as f:
            f.write(pem_public)

    # Read private key
    with open(private_key_path, 'rb') as f:
        private_key = f.read()

    # Read public key
    with open(public_key_path, 'rb') as f:
        public_key = f.read()

    return private_key, public_key


# JWT Authentication
class JWTAuth(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> User | None:
        try:
            # Load public key for verification
            _, public_key = load_keys()
            
            # Decode and verify the token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["ES512"]
            )
            
            user_id = payload.get("user_id")
            exp = payload.get("exp")
            
            # Check if required fields are present
            if not user_id or not exp:
                return None
            
            # Check if token is expired
            if exp < timezone.now().timestamp():
                return None
            
            # Get user from database
            user = User.objects.filter(id=user_id).first()
            return user
            
        except jwt.ExpiredSignatureError:
            # Token has expired
            return None
        except jwt.InvalidTokenError:
            # Token is invalid (malformed, wrong signature, etc.)
            return None
        except Exception:
            # Any other error (database, key loading, etc.)
            return None

auth_jwt = JWTAuth()




# Helper function to verify master password
def verify_master_password(user, master_password: str) -> bool:
    """Verify user's master password"""
    return user.check_password(master_password)


# Helper function to get user from auth
def get_user_from_auth(auth):
    """Get User object from auth parameter"""
    if not auth:
        raise HttpError(401, "Authentication required")
    
    # If auth is already a User object, return it
    if hasattr(auth, 'check_password'):
        return auth
    
    # If auth is a string ID, fetch the user
    if isinstance(auth, str):
        try:
            return User.objects.get(id=auth)
        except User.DoesNotExist:
            raise HttpError(401, "Invalid authentication")
    
    raise HttpError(401, "Invalid authentication")


# Generate JWT tokens
def create_tokens(user: User) -> dict:
    # Load private key for signing
    private_key, _ = load_keys()

    access_token_expiry = timezone.now() + datetime.timedelta(minutes=15)
    refresh_token_expiry = timezone.now() + datetime.timedelta(days=14)

    access_payload = {
        "user_id": str(user.id),
        "exp": access_token_expiry.timestamp(),
        "iat": timezone.now().timestamp(),
        "token_type": "access"
    }

    jti = str(uuid.uuid4())

    refresh_payload = {
        "user_id": str(user.id),
        "exp": refresh_token_expiry.timestamp(),
        "iat": timezone.now().timestamp(),
        "token_type": "refresh",
        "jti": jti  # Add JTI for revocation
    }

    access_token = jwt.encode(
        access_payload,
        private_key,
        algorithm="ES512"
    )

    refresh_token = jwt.encode(
        refresh_payload,
        private_key,
        algorithm="ES512"
    )

    # Save refresh token in database
    Token.objects.create(
        user=user,
        token=jti,
        token_type='refresh',
        expires_at=refresh_token_expiry
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 15 * 60  # 15 minutes in seconds
    }


# Endpoint for user registration
@auth_router.post("/register", response={201: UserOut, 400: ErrorOut})
@transaction.atomic
def register_user(request: HttpRequest, data: UserIn):
    # Check if user already exists
    if User.objects.filter(email=data.email).exists():
        raise HttpError(400, "User with this email already exists")

    # Create user
    user = User.objects.create_user(
        email=data.email,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name
    )

    # Create verification token
    expiry = timezone.now() + datetime.timedelta(days=3)
    _ = Token.objects.create(
        user=user,
        token_type='verification',
        expires_at=expiry
    )

    # Send verification email (implement your email sending logic here)
    # send_verification_email(user.email, verification_token.token)

    return 201, user


# Endpoint for login
@auth_router.post("/login", response={200: TokenOut, 400: ErrorOut, 401: ErrorOut})
def login_user(request: HttpRequest, data: LoginIn):
    # Get user IP and user agent
    ip_address = request.META.get('REMOTE_ADDR', None)
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    # Log login attempt
    login_attempt = LoginAttempt(
        email=data.email,
        ip_address=ip_address,
        user_agent=user_agent
    )

    # Authenticate user
    user = authenticate(email=data.email, password=data.password)
    if not user:
        login_attempt.successful = False
        login_attempt.save()
        raise HttpError(401, "Invalid credentials")

    # Check if user is active
    if not user.is_active:
        login_attempt.user = user
        login_attempt.successful = False
        login_attempt.save()
        raise HttpError(401, "User account is disabled")

    # Log successful login
    login_attempt.user = user
    login_attempt.successful = True
    login_attempt.save()

    # Create session
    UserSession.objects.create(
        user=user,
        session_key=str(uuid.uuid4()),
        ip_address=ip_address,
        user_agent=user_agent
    )

    # Update last login
    user.last_login = timezone.now()
    user.save()

    # Create tokens
    tokens = create_tokens(user)

    # Set session cookies if remember_me is True
    if data.remember_me:
        request.session.set_expiry(14 * 24 * 60 * 60)  # 14 days in seconds
    else:
        request.session.set_expiry(0)  # Browser session

    # Log in user to Django session
    login(request, user)

    return tokens


@auth_router.post("/token/refresh", response={200: TokenOut, 401: ErrorOut}, auth=auth_jwt)
def refresh_token(request: HttpRequest, data: RefreshTokenIn):
    try:
        # Load public key for verification
        _, public_key = load_keys()
        
        payload = jwt.decode(
            data.refresh_token,
            public_key,
            algorithms=["ES512"]
        )
        
        # Check if token type is refresh
        if payload.get("token_type") != "refresh":
            raise HttpError(401, "Invalid token type")
            
        # Check if token is expired
        if payload.get("exp") < timezone.now().timestamp():
            raise HttpError(401, "Token expired")
            
        # Get user first
        user_id = payload.get("user_id")
        user = User.objects.filter(id=user_id).first()
        
        if not user:
            raise HttpError(401, "User not found")
            
        # Check for JTI
        jti = payload.get("jti")
        if not jti:
            raise HttpError(401, "Invalid token format")
            
        # Verify token exists and is valid
        token_record = Token.objects.filter(
            token=jti,
            user=user,
            token_type='refresh',
            is_used=False,
            expires_at__gt=timezone.now()
        ).first()
        
        if not token_record:
            raise HttpError(401, "Invalid or revoked token")
            
        # Mark old token as used to prevent reuse
        token_record.is_used = True
        token_record.save()
        
        # Create new tokens
        tokens = create_tokens(user)
        
        return tokens
        
    except jwt.PyJWTError:
        raise HttpError(401, "Invalid token")

# Endpoint for logout
@auth_router.post("/logout", response={200: MessageOut}, auth=auth_jwt)
def logout_user(request: HttpRequest):
    # Revoke refresh tokens
    Token.objects.filter(
        user=get_user_from_auth(request.auth),
        token_type='refresh',
        is_used=False,
        expires_at__gt=timezone.now()
    ).update(is_used=True)

    # Invalidate session
    logout(request)

    return {"message": "Successfully logged out"}


# Protected endpoint to get current user
@auth_router.get("/me", response={200: UserOut, 401: ErrorOut}, auth=auth_jwt)
def get_current_user(request: HttpRequest):
    if not request.auth:
        raise HttpError(401, "Authentication required")

    return get_user_from_auth(request.auth)


# Protected endpoint to update user profile
@auth_router.put("/me", response={200: UserOut, 401: ErrorOut}, auth=auth_jwt)
def update_user(request: HttpRequest, data: UserUpdate):
    user = get_user_from_auth(request.auth)
    if data.first_name is not None:
        user.first_name = data.first_name

    if data.last_name is not None:
        user.last_name = data.last_name

    if data.username is not None:
        # Check if username already exists
        if User.objects.filter(username=data.username).exclude(id=user.id).exists():
            raise HttpError(400, "Username already exists")
        user.username = data.username

    user.save()

    return user


# Endpoint for password change
@auth_router.post("/password/change", response={200: MessageOut, 400: ErrorOut, 401: ErrorOut}, auth=auth_jwt)
def change_password(request: HttpRequest, data: PasswordChangeIn):
    user = get_user_from_auth(request.auth)
    if not user:
        raise HttpError(401, "Authentication required")

    # Check current password
    if not user.check_password(data.current_password):
        raise HttpError(400, "Current password is incorrect")

    # Check if new password matches confirmation
    if data.new_password != data.confirm_password:
        raise HttpError(400, "Passwords do not match")

    # Update password
    user.set_password(data.new_password)
    user.save()

    # Save password history
    from .models import PasswordHistory
    PasswordHistory.objects.create(
        user=user,
        password=user.password  # Already hashed by set_password
    )

    # Log out all sessions
    UserSession.objects.filter(user=user).update(is_active=False)

    return {"message": "Password changed successfully"}


# Endpoint for password reset request
@auth_router.post("/password/reset/request", response={200: MessageOut, 404: ErrorOut})
def request_password_reset(request: HttpRequest, data: PasswordResetRequestIn):
    user = User.objects.filter(email=data.email).first()

    if not user:
        # Return success even if user doesn't exist to prevent user enumeration
        return {"message": "If your email is registered, you will receive a password reset link"}

    # Create password reset token
    expiry = timezone.now() + datetime.timedelta(hours=24)
    _ = Token.objects.create(
        user=user,
        token_type='password_reset',
        expires_at=expiry
    )

    # Send password reset email (implement your email sending logic here)
    # send_password_reset_email(user.email, reset_token.token)

    return {"message": "If your email is registered, you will receive a password reset link"}


# Endpoint for password reset confirmation
@auth_router.post("/password/reset/confirm", response={200: MessageOut, 400: ErrorOut})
def confirm_password_reset(request: HttpRequest, data: PasswordResetConfirmIn):
    try:
        # Find token
        token = Token.objects.get(
            token=data.token,
            token_type='password_reset',
            is_used=False,
            expires_at__gt=timezone.now()
        )

        # Check if new password matches confirmation
        if data.new_password != data.confirm_password:
            raise HttpError(400, "Passwords do not match")

        user = token.user

        # Reset password
        user.set_password(data.new_password)
        user.save()

        # Mark token as used
        token.is_used = True
        token.save()

        # Save password history
        from .models import PasswordHistory
        PasswordHistory.objects.create(
            user=user,
            password=user.password
        )

        return {"message": "Password reset successful"}
    except Token.DoesNotExist:
        raise HttpError(400, "Invalid or expired token")


# Endpoint for email verification
@auth_router.post("/verify-email", response={200: MessageOut, 400: ErrorOut})
def verify_email(request: HttpRequest, data: EmailVerificationIn):
    try:
        # Find token
        token = Token.objects.get(
            token=data.token,
            token_type='verification',
            is_used=False,
            expires_at__gt=timezone.now()
        )

        user = token.user

        # Mark user as verified
        user.is_verified = True
        user.save()

        # Mark token as used
        token.is_used = True
        token.save()

        return {"message": "Email verification successful"}
    except Token.DoesNotExist:
        raise HttpError(400, "Invalid or expired token")


# Endpoint for getting user profile
# @auth_router.get("/profile", response={200: ProfileOut, 401: ErrorOut})
# def get_profile(request: HttpRequest, auth=JWTAuth()):
#     if not auth:
#         raise HttpError(401, "Authentication required")

#     user = auth
#     profile = Profile.objects.get(user=user)

#     # Create response with avatar URL if available
#     response = {
#         "bio": profile.bio,
#         "phone_number": profile.phone_number,
#         "birth_date": profile.birth_date,
#         "avatar_url": None
#     }

#     if profile.avatar:
#         response["avatar_url"] = request.build_absolute_uri(profile.avatar.url)

#     return response


# Endpoint for updating user profile
# @auth_router.put("/profile", response={200: ProfileOut, 401: ErrorOut})
# def update_profile(request: HttpRequest, data: ProfileIn, auth=JWTAuth()):
#     if not auth:
#         raise HttpError(401, "Authentication required")

#     user = auth
#     profile = Profile.objects.get(user=user)

#     if data.bio is not None:
#         profile.bio = data.bio

#     if data.phone_number is not None:
#         profile.phone_number = data.phone_number

#     if data.birth_date is not None:
#         profile.birth_date = data.birth_date

#     profile.save()

#     # Create response with avatar URL if available
#     response = {
#         "bio": profile.bio,
#         "phone_number": profile.phone_number,
#         "birth_date": profile.birth_date,
#         "avatar_url": None
#     }

#     if profile.avatar:
#         response["avatar_url"] = request.build_absolute_uri(profile.avatar.url)

#     return response


# Endpoint for uploading avatar
# @auth_router.post("/avatar", response={200: ProfileOut, 401: ErrorOut})
# def upload_avatar(request: HttpRequest, file: UploadedFile = File(...), auth=JWTAuth()):
#     if not auth:
#         raise HttpError(401, "Authentication required")

#     profile = Profile.objects.get(user=auth)

#     # Check file type
#     valid_extensions = ['.jpg', '.jpeg', '.png']
#     ext = os.path.splitext(file.name)[1]
#     if ext.lower() not in valid_extensions:
#         raise HttpError(400, "Unsupported file type")

#     # Save avatar
#     if profile.avatar:
#         # Delete old avatar
#         if os.path.isfile(profile.avatar.path):
#             os.remove(profile.avatar.path)

#     profile.avatar.save(f"{auth.id}{ext}", file, save=True)

#     # Create response with avatar URL
#     response = {
#         "bio": profile.bio,
#         "phone_number": profile.phone_number,
#         "birth_date": profile.birth_date,
#         "avatar_url": request.build_absolute_uri(profile.avatar.url)
#     }

#     return response


# Endpoint for listing user sessions
@auth_router.get("/sessions", response={200: SessionListOut, 401: ErrorOut}, auth=auth_jwt)
def list_sessions(request: HttpRequest):
    user = get_user_from_auth(request.auth)
    if not request.auth:
        raise HttpError(401, "Authentication required")

    sessions = UserSession.objects.filter(user=user, is_active=True)

    return {"sessions": sessions}


# Endpoint for terminating a session
@auth_router.delete("/sessions/{session_id}", response={200: MessageOut, 401: ErrorOut, 404: ErrorOut}, auth=auth_jwt)
def terminate_session(request: HttpRequest, session_id: str):
    user = get_user_from_auth(request.auth)
    if not user:
        raise HttpError(401, "Authentication required")

    try:
        session = UserSession.objects.get(id=session_id, user=user)
        session.is_active = False
        session.save()
        
        return {"message": "Session terminated successfully"}
    except UserSession.DoesNotExist:
        raise HttpError(404, "Session not found")
