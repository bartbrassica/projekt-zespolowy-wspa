# authentication/authentication/password_manager_models.py

from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid


class PasswordEntry(models.Model):
    """Model for storing encrypted passwords"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='password_entries')
    
    # Entry metadata
    name = models.CharField(max_length=255, help_text="Name or title for this password")
    site = models.URLField(max_length=500, blank=True, help_text="Website URL")
    username = models.CharField(max_length=255, blank=True, help_text="Username/email for this account")
    
    # Encrypted password storage
    encrypted_password = models.TextField()
    encryption_salt = models.BinaryField(max_length=32)  # Salt for key derivation
    
    # Additional fields
    notes = models.TextField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="When this password expires")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    # Organization
    folder = models.ForeignKey('PasswordFolder', on_delete=models.SET_NULL, null=True, blank=True, related_name='entries')
    tags = models.ManyToManyField('PasswordTag', blank=True, related_name='entries')
    is_favorite = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'password_entries'
        ordering = ['-is_favorite', '-updated_at']
        indexes = [
            models.Index(fields=['user', 'name']),
            models.Index(fields=['user', 'site']),
            models.Index(fields=['expires_at']),
        ]
        unique_together = [['user', 'name', 'site']]
    
    def __str__(self):
        return f"{self.name} - {self.user.email}"
    
    @property
    def is_expired(self):
        """Check if password has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def days_until_expiry(self):
        """Calculate days until password expires"""
        if self.expires_at:
            delta = self.expires_at - timezone.now()
            return delta.days if delta.days > 0 else 0
        return None


class PasswordFolder(models.Model):
    """Organize passwords into folders"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='password_folders')
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, blank=True, help_text="Hex color code")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'password_folders'
        unique_together = [['user', 'name', 'parent']]
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.user.email}"


class PasswordTag(models.Model):
    """Tags for categorizing passwords"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='password_tags')
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, blank=True, help_text="Hex color code")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'password_tags'
        unique_together = [['user', 'name']]
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PasswordShareLink(models.Model):
    """Secure temporary sharing of passwords"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    password_entry = models.ForeignKey(PasswordEntry, on_delete=models.CASCADE, related_name='share_links')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_shares')
    
    # Share settings
    share_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    max_views = models.IntegerField(default=1, help_text="Maximum number of times this can be viewed")
    current_views = models.IntegerField(default=0)
    expires_at = models.DateTimeField()
    require_authentication = models.BooleanField(default=False)
    allowed_email = models.EmailField(blank=True, help_text="Restrict access to specific email")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    accessed_by_ip = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'password_share_links'
        indexes = [
            models.Index(fields=['share_token']),
            models.Index(fields=['expires_at']),
        ]
    
    @property
    def is_valid(self):
        """Check if share link is still valid"""
        return (
            self.current_views < self.max_views and
            timezone.now() < self.expires_at
        )


class PasswordEntryHistory(models.Model):
    """Track password changes for entries"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    password_entry = models.ForeignKey(PasswordEntry, on_delete=models.CASCADE, related_name='password_history')
    encrypted_password = models.TextField()
    encryption_salt = models.BinaryField(max_length=32)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    change_reason = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'password_entry_history'
        ordering = ['-changed_at']


class PasswordAccessLog(models.Model):
    """Log access to passwords for security auditing"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    password_entry = models.ForeignKey(PasswordEntry, on_delete=models.CASCADE, related_name='access_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=[
        ('view', 'Viewed'),
        ('copy', 'Copied'),
        ('update', 'Updated'),
        ('share', 'Shared'),
        ('delete', 'Deleted'),
    ])
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'password_access_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['password_entry', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]
