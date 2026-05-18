from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.conf import settings
import uuid

from .services import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "auth_user"

    def __str__(self) -> str:
        return self.email

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def get_short_name(self) -> str:
        return self.first_name or self.email.split("@")[0]


class Token(models.Model):
    TOKEN_TYPE_CHOICES = [
        ("verification", "Email Verification"),
        ("password_reset", "Password Reset"),
        ("access", "API Access"),
        ("refresh", "Refresh Token"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tokens")
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = "auth_token"

    def __str__(self) -> str:
        return f"{self.token_type} token for {self.user.email}"

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    @property
    def is_valid(self) -> bool:
        return not self.is_used and not self.is_expired


class LoginAttempt(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="login_attempts", null=True
    )
    email = models.EmailField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    successful = models.BooleanField(default=False)

    class Meta:
        db_table = "auth_login_attempt"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["email", "timestamp"]),
            models.Index(fields=["ip_address", "timestamp"]),
        ]

    def __str__(self) -> str:
        status = "successful" if self.successful else "failed"
        return f"{status.title()} login attempt for {self.email} at {self.timestamp}"


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "auth_user_session"
        ordering = ["-last_activity"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["last_activity"]),
        ]

    def __str__(self) -> str:
        return (
            f"Session for {self.user.email} on {self.device_name or 'unknown device'}"
        )


class PasswordHistory(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="password_history"
    )
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "auth_password_history"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Password change for {self.user.email} at {self.created_at}"


class UserPermissionOverride(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="permission_overrides"
    )
    permission_name = models.CharField(max_length=255)
    is_granted = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "permission_name")
        db_table = "auth_permission_override"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        status = "granted" if self.is_granted else "denied"
        return f"{self.permission_name} ({status}) for {self.user.email}"

    @property
    def is_expired(self) -> bool:
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @property
    def is_active(self) -> bool:
        return self.is_granted and not self.is_expired


class PasswordEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_entries",
    )

    name = models.CharField(max_length=255)
    site = models.URLField(max_length=500, blank=True)
    username = models.CharField(max_length=255, blank=True)

    encrypted_password = models.TextField()
    encryption_salt = models.BinaryField(max_length=32)

    notes = models.TextField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_accessed = models.DateTimeField(null=True, blank=True)

    folder = models.ForeignKey(
        "PasswordFolder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entries",
    )
    tags = models.ManyToManyField("PasswordTag", blank=True, related_name="entries")
    is_favorite = models.BooleanField(default=False)

    class Meta:
        db_table = "password_entries"
        ordering = ["-is_favorite", "-updated_at"]
        indexes = [
            models.Index(fields=["user", "name"]),
            models.Index(fields=["user", "site"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["user", "is_favorite"]),
        ]
        unique_together = [["user", "name", "site"]]

    def __str__(self) -> str:
        return f"{self.name} - {self.user.email}"

    @property
    def is_expired(self) -> bool:
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @property
    def days_until_expiry(self) -> int | None:
        if self.expires_at:
            delta = self.expires_at - timezone.now()
            return delta.days if delta.days > 0 else 0
        return None

    def mark_accessed(self) -> None:
        """Update last accessed timestamp."""
        self.last_accessed = timezone.now()
        self.save(update_fields=["last_accessed"])


class PasswordExpirationNotification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ("3_days", "3 Days Before"),
        ("1_day", "1 Day Before"),
        ("expired", "Expired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    password_entry = models.ForeignKey(
        PasswordEntry, on_delete=models.CASCADE, related_name="expiration_notifications"
    )
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPE_CHOICES
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    email_sent_successfully = models.BooleanField(default=False)

    class Meta:
        db_table = "password_expiration_notifications"
        unique_together = [["password_entry", "notification_type"]]
        ordering = ["-sent_at"]
        indexes = [
            models.Index(fields=["password_entry", "notification_type"]),
            models.Index(fields=["sent_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.notification_type} notification for {self.password_entry.name}"


class PasswordFolder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_folders",
    )
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subfolders",
    )
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "password_folders"
        unique_together = [["user", "name", "parent"]]
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} - {self.user.email}"

    @property
    def entry_count(self) -> int:
        """Get count of entries in this folder.

        If the instance was annotated with entry_count in the queryset,
        return that value. Otherwise, calculate it dynamically.
        """
        # Check if entry_count was added via queryset annotation
        # Django adds it as a direct attribute when using .annotate()
        if 'entry_count' in self.__dict__:
            return self.__dict__['entry_count']
        # Otherwise calculate it dynamically
        return self.entries.count()

    @entry_count.setter
    def entry_count(self, value: int) -> None:
        """Allow Django ORM to set entry_count from annotations."""
        self.__dict__['entry_count'] = value

    @property
    def full_path(self) -> str:
        """Get full path of folder including parent folders."""
        if self.parent:
            return f"{self.parent.full_path}/{self.name}"
        return self.name


class PasswordTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="password_tags"
    )
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "password_tags"
        unique_together = [["user", "name"]]
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    @property
    def entry_count(self) -> int:
        """Get count of entries with this tag.

        If the instance has an annotated entry_count (from queryset annotation),
        use that. Otherwise, calculate it dynamically.
        """
        # Check if entry_count was set via annotation
        if hasattr(self, '_entry_count'):
            return self._entry_count
        # Otherwise calculate it
        return self.entries.count()

    @entry_count.setter
    def entry_count(self, value: int) -> None:
        """Allow Django ORM to set entry_count from annotations."""
        self._entry_count = value


class PasswordShareLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    password_entry = models.ForeignKey(
        PasswordEntry, on_delete=models.CASCADE, related_name="share_links"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_shares",
    )

    share_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    max_views = models.IntegerField(default=1)
    current_views = models.IntegerField(default=0)
    expires_at = models.DateTimeField()
    require_authentication = models.BooleanField(default=False)
    allowed_email = models.EmailField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    accessed_by_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = "password_share_links"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["share_token"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["created_by"]),
        ]

    def __str__(self) -> str:
        return f"Share link for {self.password_entry.name}"

    @property
    def is_valid(self) -> bool:
        return self.current_views < self.max_views and timezone.now() < self.expires_at

    def increment_views(self) -> None:
        """Increment view count and update last accessed."""
        self.current_views += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=["current_views", "last_accessed"])


class PasswordEntryHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    password_entry = models.ForeignKey(
        PasswordEntry, on_delete=models.CASCADE, related_name="password_history"
    )
    encrypted_password = models.TextField()
    encryption_salt = models.BinaryField(max_length=32)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    change_reason = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "password_entry_history"
        ordering = ["-changed_at"]
        indexes = [
            models.Index(fields=["password_entry", "changed_at"]),
        ]

    def __str__(self) -> str:
        return f"Password history for {self.password_entry.name} at {self.changed_at}"


class PasswordAccessLog(models.Model):
    ACTION_CHOICES = [
        ("view", "Viewed"),
        ("copy", "Copied"),
        ("update", "Updated"),
        ("share", "Shared"),
        ("delete", "Deleted"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    password_entry = models.ForeignKey(
        PasswordEntry, on_delete=models.CASCADE, related_name="access_logs"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "password_access_logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["password_entry", "timestamp"]),
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["action", "timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} on {self.password_entry.name} by {self.user.email if self.user else 'unknown'}"
