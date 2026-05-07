# authentication/authentication/password_endpoints.py

from ninja import Router, Query
from ninja.errors import HttpError
from django.http import HttpRequest
from django.db import transaction
from django.db.models import Q, Count
from django.utils import timezone
from typing import List
import json
import csv
import io
import base64

from .endpoints import auth_jwt, verify_master_password, get_user_from_auth
from .password_manager_models import (
    PasswordEntry, PasswordFolder, PasswordTag, 
    PasswordShareLink, PasswordEntryHistory, PasswordAccessLog
)
from .password_schemas import (
    PasswordEntryIn, PasswordEntryOut, PasswordEntryUpdate,
    PasswordDecryptRequest, PasswordDecryptResponse,
    PasswordGenerateRequest, PasswordGenerateResponse,
    FolderIn, FolderOut, FolderUpdate,
    TagIn, TagOut,
    ShareLinkIn, ShareLinkOut,
    PasswordBulkDeleteRequest,
    MasterPasswordChangeRequest,
    PasswordImportRequest, PasswordExportRequest
)
from .encryption_service import encryption_service
from .schemas import MessageOut, ErrorOut

password_router = Router(tags=["Password Manager"])


# Password Entry Endpoints
@password_router.post("/entries", response={201: PasswordEntryOut, 400: ErrorOut}, auth=auth_jwt)
@transaction.atomic
def create_password_entry(request: HttpRequest, data: PasswordEntryIn):
    """Create a new password entry"""
    
    # Get the authenticated user
    user = get_user_from_auth(request.auth)
    
    # Verify master password
    if not verify_master_password(user, data.master_password):
        raise HttpError(400, "Invalid master password")
    
    # Check for duplicate
    if PasswordEntry.objects.filter(
        user=user, 
        name=data.name, 
        site=data.site
    ).exists():
        raise HttpError(400, "An entry with this name and site already exists")
    
    # Encrypt the password
    encrypted_password, salt = encryption_service.encrypt_password(
        data.password, 
        data.master_password
    )
    
    # Create the entry
    entry = PasswordEntry.objects.create(
        user=user,
        name=data.name,
        site=data.site or "",
        username=data.username or "",
        encrypted_password=encrypted_password,
        encryption_salt=salt,
        notes=data.notes or "",
        expires_at=data.expires_at,
        is_favorite=data.is_favorite
    )
    
    # Add folder if specified
    if data.folder_id:
        try:
            folder = PasswordFolder.objects.get(id=data.folder_id, user=user)
            entry.folder = folder
            entry.save()
        except PasswordFolder.DoesNotExist:
            pass
    
    # Add tags if specified
    if data.tags:
        for tag_name in data.tags:
            tag, _ = PasswordTag.objects.get_or_create(
                user=user,
                name=tag_name
            )
            entry.tags.add(tag)
    
    # Log the creation
    PasswordAccessLog.objects.create(
        password_entry=entry,
        user=user,
        action='create',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    return 201, entry


@password_router.get("/entries", response=List[PasswordEntryOut], auth=auth_jwt)
def list_password_entries(
    request: HttpRequest,
    query: str = None,
    folder_id: str = None,
    tags: List[str] = Query(None),  # Use Query for list parameters
    show_expired: bool = False,
    show_favorites_only: bool = False,
    sort_by: str = "updated_at",
    sort_order: str = "desc",
    limit: int = 50,
    offset: int = 0
):
    """List all password entries for the user"""
    # Get the authenticated user
    user = get_user_from_auth(request.auth)
    
    entries = PasswordEntry.objects.filter(user=user).select_related('folder').prefetch_related('tags')
    
    # Apply search filters
    if query:
        entries = entries.filter(
            Q(name__icontains=query) |
            Q(site__icontains=query) |
            Q(username__icontains=query) |
            Q(notes__icontains=query)
        )
    
    if folder_id:
        entries = entries.filter(folder_id=folder_id)
    
    if tags:
        for tag in tags:
            entries = entries.filter(tags__name=tag)
    
    if not show_expired:
        entries = entries.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        )
    
    if show_favorites_only:
        entries = entries.filter(is_favorite=True)
    
    # Apply sorting
    valid_sort_fields = ["name", "site", "created_at", "updated_at", "expires_at"]
    if sort_by not in valid_sort_fields:
        sort_by = "updated_at"
    
    order_field = sort_by
    if sort_order == 'desc':
        order_field = f'-{order_field}'
    entries = entries.order_by(order_field)
    
    # Apply pagination
    entries = entries[offset:offset + limit]
    
    return list(entries)


@password_router.get("/entries/{entry_id}", response={200: PasswordEntryOut, 404: ErrorOut}, auth=auth_jwt)
def get_password_entry(request: HttpRequest, entry_id: str):
    """Get a specific password entry"""
    
    # Get the authenticated user
    user = get_user_from_auth(request.auth)
    
    try:
        entry = PasswordEntry.objects.get(id=entry_id, user=user)
        
        # Log access
        PasswordAccessLog.objects.create(
            password_entry=entry,
            user=user,
            action='view',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Update last accessed
        entry.last_accessed = timezone.now()
        entry.save(update_fields=['last_accessed'])
        
        return entry
    except PasswordEntry.DoesNotExist:
        raise HttpError(404, "Password entry not found")


@password_router.put("/entries/{entry_id}", response={200: PasswordEntryOut, 404: ErrorOut}, auth=auth_jwt)
@transaction.atomic
def update_password_entry(request: HttpRequest, entry_id: str, data: PasswordEntryUpdate):
    """Update a password entry"""
    
    # Get the authenticated user
    user = get_user_from_auth(request.auth)
    
    # Verify master password
    if not verify_master_password(user, data.master_password):
        raise HttpError(400, "Invalid master password")
    
    try:
        entry = PasswordEntry.objects.get(id=entry_id, user=user)
        
        # Save to history if password is changing
        if data.password is not None:
            PasswordEntryHistory.objects.create(
                password_entry=entry,
                encrypted_password=entry.encrypted_password,
                encryption_salt=entry.encryption_salt,
                changed_by=user,
                change_reason="User update"
            )
            
            # Re-encrypt with new password
            encrypted_password, salt = encryption_service.encrypt_password(
                data.password,
                data.master_password
            )
            entry.encrypted_password = encrypted_password
            entry.encryption_salt = salt
        
        # Update other fields
        if data.name is not None:
            entry.name = data.name
        if data.site is not None:
            entry.site = data.site
        if data.username is not None:
            entry.username = data.username
        if data.notes is not None:
            entry.notes = data.notes
        if data.expires_at is not None:
            entry.expires_at = data.expires_at
        if data.is_favorite is not None:
            entry.is_favorite = data.is_favorite
        
        # Update folder
        if data.folder_id is not None:
            if data.folder_id:
                try:
                    folder = PasswordFolder.objects.get(id=data.folder_id, user=user)
                    entry.folder = folder
                except PasswordFolder.DoesNotExist:
                    raise HttpError(400, "Folder not found")
            else:
                entry.folder = None
        
        # Update tags
        if data.tags is not None:
            entry.tags.clear()
            for tag_name in data.tags:
                tag, _ = PasswordTag.objects.get_or_create(
                    user=user,
                    name=tag_name
                )
                entry.tags.add(tag)
        
        entry.save()
        
        # Log the update
        PasswordAccessLog.objects.create(
            password_entry=entry,
            user=user,
            action='update',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return entry
    except PasswordEntry.DoesNotExist:
        raise HttpError(404, "Password entry not found")


@password_router.delete("/entries/{entry_id}", response={204: None, 404: ErrorOut}, auth=auth_jwt)
@transaction.atomic
def delete_password_entry(request: HttpRequest, entry_id: str):
    """Delete a password entry"""
    
    # Get the authenticated user
    user = get_user_from_auth(request.auth)
    
    try:
        entry = PasswordEntry.objects.get(id=entry_id, user=user)
        
        # Log the deletion
        PasswordAccessLog.objects.create(
            password_entry=entry,
            user=user,
            action='delete',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        entry.delete()
        return 204, None
    except PasswordEntry.DoesNotExist:
        raise HttpError(404, "Password entry not found")

def convert_salt_to_bytes(salt):
    """Convert salt from any format to bytes"""
    if isinstance(salt, memoryview):
        return salt.tobytes()
    elif isinstance(salt, str):
        import base64
        try:
            return base64.b64decode(salt)
        except Exception:
            return salt.encode('utf-8')
    elif isinstance(salt, bytes):
        return salt
    else:
        return bytes(salt)

@password_router.post("/entries/{entry_id}/decrypt", response={200: PasswordDecryptResponse, 400: ErrorOut}, auth=auth_jwt)
def decrypt_password(request: HttpRequest, entry_id: str, data: PasswordDecryptRequest):
    """Decrypt a password entry"""
    # Get the authenticated user
    user = get_user_from_auth(request.auth)
    
    # Verify master password
    if not verify_master_password(user, data.master_password):
        raise HttpError(400, "Invalid master password")
    
    try:
        entry = PasswordEntry.objects.get(id=entry_id, user=user)
        
        # Convert salt to bytes if it's stored as string
        salt = convert_salt_to_bytes(entry.encryption_salt)
        
        # Decrypt the password
        decrypted = encryption_service.decrypt_password(
            entry.encrypted_password,
            data.master_password,
            salt
        )
        
        if not decrypted:
            raise HttpError(400, "Failed to decrypt password")
        
        # Check password strength
        strength = encryption_service.check_password_strength(decrypted)
        
        # Log access
        PasswordAccessLog.objects.create(
            password_entry=entry,
            user=user,
            action='copy',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return {
            "password": decrypted,
            "strength": strength
        }
    except PasswordEntry.DoesNotExist:
        raise HttpError(404, "Password entry not found")


# Password Generation
@password_router.post("/generate", response=PasswordGenerateResponse)
def generate_password(request: HttpRequest, data: PasswordGenerateRequest):
    """Generate a secure random password"""
    password = encryption_service.generate_secure_password(
        length=data.length,
        include_symbols=data.include_symbols,
        include_numbers=data.include_numbers,
        include_uppercase=data.include_uppercase,
        include_lowercase=data.include_lowercase,
        exclude_ambiguous=data.exclude_ambiguous
    )
    
    strength = encryption_service.check_password_strength(password)
    
    return {
        "password": password,
        "strength": strength
    }


# Folder Management
@password_router.post("/folders", response={201: FolderOut}, auth=auth_jwt)
def create_folder(request: HttpRequest, data: FolderIn):
    """Create a new folder"""
    
    # Get the authenticated user
    user = get_user_from_auth(request.auth)
    
    # Check for duplicate
    parent = None
    if data.parent_id:
        try:
            parent = PasswordFolder.objects.get(id=data.parent_id, user=user)
        except PasswordFolder.DoesNotExist:
            raise HttpError(400, "Parent folder not found")
    
    if PasswordFolder.objects.filter(
        user=user,
        name=data.name,
        parent=parent
    ).exists():
        raise HttpError(400, "A folder with this name already exists in this location")
    
    folder = PasswordFolder.objects.create(
        user=user,
        name=data.name,
        parent=parent,
        icon=data.icon or "",
        color=data.color or ""
    )
    
    return 201, folder


@password_router.get("/folders", response=List[FolderOut], auth=auth_jwt)
def list_folders(request: HttpRequest):
    """List all folders for the user"""
    
    # Get the authenticated user
    user = get_user_from_auth(request.auth)
    
    folders = PasswordFolder.objects.filter(user=user).annotate(
        entry_count=Count('entries')
    ).order_by('name')
    
    return list(folders)


@password_router.put("/folders/{folder_id}", response={200: FolderOut}, auth=auth_jwt)
def update_folder(request: HttpRequest, folder_id: str, data: FolderUpdate):
    """Update a folder"""
    
    # Get the authenticated user
    user = get_user_from_auth(request.auth)
    
    try:
        folder = PasswordFolder.objects.get(id=folder_id, user=user)
        
        if data.name is not None:
            folder.name = data.name
        if data.icon is not None:
            folder.icon = data.icon
        if data.color is not None:
            folder.color = data.color
        if data.parent_id is not None:
            if data.parent_id:
                try:
                    parent = PasswordFolder.objects.get(id=data.parent_id, user=user)
                    # Prevent circular references
                    if parent.id != folder.id:
                        folder.parent = parent
                except PasswordFolder.DoesNotExist:
                    raise HttpError(400, "Parent folder not found")
            else:
                folder.parent = None
        
        folder.save()
        return folder
    except PasswordFolder.DoesNotExist:
        raise HttpError(404, "Folder not found")


@password_router.delete("/folders/{folder_id}", response={204: None}, auth=auth_jwt)
def delete_folder(request: HttpRequest, folder_id: str):
    """Delete a folder (moves entries to root)"""
    
    # Get the authenticated user
    user = get_user_from_auth(request.auth)
    
    try:
        folder = PasswordFolder.objects.get(id=folder_id, user=user)
        
        # Move all entries to root
        PasswordEntry.objects.filter(folder=folder).update(folder=None)
        
        # Move subfolders to root
        PasswordFolder.objects.filter(parent=folder).update(parent=None)
        
        folder.delete()
        return 204, None
    except PasswordFolder.DoesNotExist:
        raise HttpError(404, "Folder not found")


# Tag Management
@password_router.post("/tags", response={201: TagOut}, auth=auth_jwt)
def create_tag(request: HttpRequest, data: TagIn):
    """Create a new tag"""
    
    # Get the authenticated user
    user = get_user_from_auth(request.auth)
    
    if PasswordTag.objects.filter(user=user, name=data.name).exists():
        raise HttpError(400, "A tag with this name already exists")
    
    tag = PasswordTag.objects.create(
        user=user,
        name=data.name,
        color=data.color or ""
    )
    
    return 201, tag


@password_router.get("/tags", response=List[TagOut], auth=auth_jwt)
def list_tags(request: HttpRequest):
    """List all tags for the user"""
    
    # Get the authenticated user
    user = get_user_from_auth(request.auth)
    
    tags = PasswordTag.objects.filter(user=user).annotate(
        entry_count=Count('entries')
    ).order_by('name')
    
    return list(tags)


@password_router.delete("/tags/{tag_id}", response={204: None}, auth=auth_jwt)
def delete_tag(request: HttpRequest, tag_id: str):
    """Delete a tag"""
    
    # Get the authenticated user
    user = get_user_from_auth(request.auth)
    
    try:
        tag = PasswordTag.objects.get(id=tag_id, user=user)
        tag.delete()
        return 204, None
    except PasswordTag.DoesNotExist:
        raise HttpError(404, "Tag not found")


# Bulk Operations
@password_router.post("/entries/bulk-delete", response={200: MessageOut}, auth=auth_jwt)
@transaction.atomic
def bulk_delete_entries(request: HttpRequest, data: PasswordBulkDeleteRequest):
    """Bulk delete password entries"""
    
    # Get the authenticated user
    user = get_user_from_auth(request.auth)
    
    # Verify master password
    if not verify_master_password(user, data.master_password):
        raise HttpError(400, "Invalid master password")
    
    entries = PasswordEntry.objects.filter(
        id__in=data.entry_ids,
        user=user
    )
    
    count = entries.count()
    
    # Log deletions
    for entry in entries:
        PasswordAccessLog.objects.create(
            password_entry=entry,
            user=user,
            action='delete',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
    
    entries.delete()
    
    return {"message": f"Successfully deleted {count} entries"}


# Master Password Change
@password_router.post("/master-password/change", response={200: MessageOut}, auth=auth_jwt)
@transaction.atomic
def change_master_password(request: HttpRequest, data: MasterPasswordChangeRequest):
    """Change master password and re-encrypt all entries"""
    
    # Get the authenticated user
    user = get_user_from_auth(request.auth)
    
    # Verify current master password
    if not verify_master_password(user, data.current_master_password):
        raise HttpError(400, "Invalid current master password")
    
    # Get all password entries
    entries = PasswordEntry.objects.filter(user=user)
    
    # Re-encrypt each entry
    for entry in entries:
        result = encryption_service.re_encrypt_password(
            entry.encrypted_password,
            data.current_master_password,
            data.new_master_password,
            entry.encryption_salt
        )
        
        if result:
            encrypted_password, salt = result
            entry.encrypted_password = encrypted_password
            entry.encryption_salt = salt
            entry.save(update_fields=['encrypted_password', 'encryption_salt'])
    
    # Update user's password
    user.set_password(data.new_master_password)
    user.save()
    
    return {"message": f"Successfully re-encrypted {entries.count()} passwords with new master password"}


# Import/Export Operations
@password_router.post("/import", response={200: MessageOut}, auth=auth_jwt)
@transaction.atomic
def import_passwords(request: HttpRequest, data: PasswordImportRequest):
    """Import passwords from various formats"""
    
    # Get the authenticated user
    user = get_user_from_auth(request.auth)
    
    # Verify master password
    if not verify_master_password(user, data.master_password):
        raise HttpError(400, "Invalid master password")
    
    try:
        # Decode the base64 data
        file_content = base64.b64decode(data.data).decode('utf-8')
        
        imported_count = 0
        
        if data.format == 'csv':
            # Parse CSV
            reader = csv.DictReader(io.StringIO(file_content))
            for row in reader:
                # Check required fields
                if 'name' not in row or 'password' not in row:
                    continue
                
                # Check for duplicate
                if PasswordEntry.objects.filter(
                    user=user,
                    name=row['name'],
                    site=row.get('url', '') or row.get('site', '')
                ).exists():
                    continue
                
                # Encrypt password
                encrypted_password, salt = encryption_service.encrypt_password(
                    row['password'],
                    data.master_password
                )
                
                # Create entry
                PasswordEntry.objects.create(
                    user=user,
                    name=row['name'],
                    site=row.get('url', '') or row.get('site', ''),
                    username=row.get('username', '') or row.get('email', ''),
                    encrypted_password=encrypted_password,
                    encryption_salt=salt,
                    notes=row.get('notes', '')
                )
                imported_count += 1
        
        elif data.format == 'json':
            # Parse JSON
            entries = json.loads(file_content)
            if not isinstance(entries, list):
                entries = [entries]
            
            for entry in entries:
                # Check required fields
                if 'name' not in entry or 'password' not in entry:
                    continue
                
                # Check for duplicate
                if PasswordEntry.objects.filter(
                    user=user,
                    name=entry['name'],
                    site=entry.get('site', '')
                ).exists():
                    continue
                
                # Encrypt password
                encrypted_password, salt = encryption_service.encrypt_password(
                    entry['password'],
                    data.master_password
                )
                
                # Create entry
                PasswordEntry.objects.create(
                    user=user,
                    name=entry['name'],
                    site=entry.get('site', ''),
                    username=entry.get('username', ''),
                    encrypted_password=encrypted_password,
                    encryption_salt=salt,
                    notes=entry.get('notes', '')
                )
                imported_count += 1
        
        else:
            raise HttpError(400, f"Unsupported import format: {data.format}")
        
        return {"message": f"Successfully imported {imported_count} passwords"}
    
    except Exception as e:
        raise HttpError(400, f"Import failed: {str(e)}")


@password_router.post("/export", response={200: dict}, auth=auth_jwt)
def export_passwords(request: HttpRequest, data: PasswordExportRequest):
    """Export passwords to various formats"""
    
    # Get the authenticated user
    user = get_user_from_auth(request.auth)
    
    # Verify master password
    if not verify_master_password(user, data.master_password):
        raise HttpError(400, "Invalid master password")
    
    # Get entries to export
    entries = PasswordEntry.objects.filter(user=user)
    
    if data.folder_id:
        entries = entries.filter(folder_id=data.folder_id)
    
    if data.tag_ids:
        entries = entries.filter(tags__id__in=data.tag_ids)
    
    entries = entries.distinct()
    
    export_data = []
    
    for entry in entries:
        entry_data = {
            "name": entry.name,
            "site": entry.site,
            "username": entry.username,
            "notes": entry.notes
        }
        
        # Include password if requested
        if data.include_passwords:
            decrypted = encryption_service.decrypt_password(
                entry.encrypted_password,
                data.master_password,
                entry.encryption_salt
            )
            if decrypted:
                entry_data["password"] = decrypted
        
        export_data.append(entry_data)
    
    if data.format == 'json':
        return {
            "format": "json",
            "data": base64.b64encode(json.dumps(export_data, indent=2).encode()).decode(),
            "filename": "passwords_export.json"
        }
    
    elif data.format == 'csv':
        output = io.StringIO()
        if export_data:
            writer = csv.DictWriter(output, fieldnames=export_data[0].keys())
            writer.writeheader()
            writer.writerows(export_data)
        
        return {
            "format": "csv",
            "data": base64.b64encode(output.getvalue().encode()).decode(),
            "filename": "passwords_export.csv"
        }
    
    else:
        raise HttpError(400, f"Unsupported export format: {data.format}")


# Share Link Operations
@password_router.post("/share", response={201: ShareLinkOut}, auth=auth_jwt)
@transaction.atomic
def create_share_link(request: HttpRequest, data: ShareLinkIn):
    """Create a temporary share link for a password"""
    
    # Get the authenticated user
    user = get_user_from_auth(request.auth)
    
    # Verify master password
    if not verify_master_password(user, data.master_password):
        raise HttpError(400, "Invalid master password")
    
    try:
        # Get the password entry
        entry = PasswordEntry.objects.get(id=data.password_entry_id, user=user)
        
        # Decrypt the password
        decrypted = encryption_service.decrypt_password(
            entry.encrypted_password,
            data.master_password,
            entry.encryption_salt
        )
        
        if not decrypted:
            raise HttpError(400, "Failed to decrypt password")
        
        # Create share link with re-encrypted password using a temporary key
        expires_at = timezone.now() + timezone.timedelta(hours=data.expires_in_hours)
        
        share_link = PasswordShareLink.objects.create(
            password_entry=entry,
            created_by=user,
            max_views=data.max_views,
            expires_at=expires_at,
            require_authentication=data.require_authentication,
            allowed_email=data.allowed_email or ""
        )
        
        # Log the share action
        PasswordAccessLog.objects.create(
            password_entry=entry,
            user=user,
            action='share',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Build share URL
        share_url = f"{request.build_absolute_uri('/api/passwords/shared/')}{share_link.share_token}"
        
        return 201, {
            "id": str(share_link.id),
            "share_url": share_url,
            "max_views": share_link.max_views,
            "current_views": share_link.current_views,
            "expires_at": share_link.expires_at,
            "require_authentication": share_link.require_authentication,
            "allowed_email": share_link.allowed_email,
            "created_at": share_link.created_at
        }
    
    except PasswordEntry.DoesNotExist:
        raise HttpError(404, "Password entry not found")


@password_router.get("/shared/{share_token}", response={200: dict, 404: ErrorOut})
def access_shared_password(request: HttpRequest, share_token: str):
    """Access a shared password via share link"""
    
    try:
        # Get share link
        share_link = PasswordShareLink.objects.get(share_token=share_token)
        
        # Check if valid
        if not share_link.is_valid:
            raise HttpError(404, "Share link is expired or has reached maximum views")
        
        # Check if authentication required
        if share_link.require_authentication:
            # Would need to implement authentication check here
            pass
        
        # Update view count
        share_link.current_views += 1
        share_link.last_accessed = timezone.now()
        share_link.accessed_by_ip = request.META.get('REMOTE_ADDR')
        share_link.save()
        
        # Get the password entry
        entry = share_link.password_entry
        
        # Note: In a real implementation, you'd need to handle the decryption
        # differently for share links, possibly using a temporary encryption key
        
        return {
            "name": entry.name,
            "site": entry.site,
            "username": entry.username,
            "views_remaining": share_link.max_views - share_link.current_views,
            "expires_at": share_link.expires_at
        }
    
    except PasswordShareLink.DoesNotExist:
        raise HttpError(404, "Invalid share link")


# Statistics and Analytics
@password_router.get("/stats", response={200: dict}, auth=auth_jwt)
def get_password_stats(request: HttpRequest):
    """Get statistics about user's passwords"""
    
    # Get the authenticated user
    user = get_user_from_auth(request.auth)
    
    total_passwords = PasswordEntry.objects.filter(user=user).count()
    
    expired_passwords = PasswordEntry.objects.filter(
        user=user,
        expires_at__lt=timezone.now()
    ).count()
    
    expiring_soon = PasswordEntry.objects.filter(
        user=user,
        expires_at__gt=timezone.now(),
        expires_at__lt=timezone.now() + timezone.timedelta(days=30)
    ).count()
    
    favorite_count = PasswordEntry.objects.filter(
        user=user,
        is_favorite=True
    ).count()
    
    folder_count = PasswordFolder.objects.filter(user=user).count()
    tag_count = PasswordTag.objects.filter(user=user).count()
    
    # Recent activity
    recent_entries = PasswordEntry.objects.filter(
        user=user
    ).order_by('-created_at')[:5]
    
    recently_accessed = PasswordEntry.objects.filter(
        user=user,
        last_accessed__isnull=False
    ).order_by('-last_accessed')[:5]
    
    return {
        "total_passwords": total_passwords,
        "expired_passwords": expired_passwords,
        "expiring_soon": expiring_soon,
        "favorite_count": favorite_count,
        "folder_count": folder_count,
        "tag_count": tag_count,
        "recent_entries": [
            {"id": str(e.id), "name": e.name, "created_at": e.created_at}
            for e in recent_entries
        ],
        "recently_accessed": [
            {"id": str(e.id), "name": e.name, "last_accessed": e.last_accessed}
            for e in recently_accessed
        ]
    }
