from ninja import Router, Query
from ninja.errors import HttpError
from django.http import HttpRequest
from django.db import transaction
from django.db.models import Q, Count
from django.utils import timezone
import json
import csv
import io
import base64
from typing import Any

from .endpoints import auth_jwt, get_user_from_auth
from .utils import verify_master_password
from .models import (
    PasswordEntry,
    PasswordFolder,
    PasswordTag,
    PasswordShareLink,
    PasswordEntryHistory,
    PasswordAccessLog,
)
from .schemas import (
    PasswordEntryIn,
    PasswordEntryOut,
    PasswordEntryUpdate,
    PasswordDecryptRequest,
    PasswordDecryptResponse,
    PasswordGenerateRequest,
    PasswordGenerateResponse,
    FolderIn,
    FolderOut,
    FolderUpdate,
    TagIn,
    TagOut,
    ShareLinkIn,
    ShareLinkOut,
    PasswordBulkDeleteRequest,
    MasterPasswordChangeRequest,
    PasswordImportRequest,
    PasswordExportRequest,
    MessageOut,
    ErrorOut,
)
from .db_utils import convert_salt_to_bytes, log_password_access
from .consts import PasswordManagerConstants
from .encryption_service import encryption_service

password_router = Router(tags=["Password Manager"])


@password_router.post(
    "/entries", response={201: PasswordEntryOut, 400: ErrorOut}, auth=auth_jwt
)
@transaction.atomic
def create_password_entry(
    request: HttpRequest, data: PasswordEntryIn
) -> tuple[int, PasswordEntry]:
    user = get_user_from_auth(request.auth)

    if not verify_master_password(user, data.master_password):
        raise HttpError(400, "Invalid master password")

    if PasswordEntry.objects.filter(user=user, name=data.name, site=data.site).exists():
        raise HttpError(400, "An entry with this name and site already exists")

    encrypted_password, salt = encryption_service.encrypt_password(
        data.password, data.master_password
    )
    entry = PasswordEntry.objects.create(
        user=user,
        name=data.name,
        site=data.site or "",
        username=data.username or "",
        encrypted_password=encrypted_password,
        encryption_salt=salt,
        notes=data.notes or "",
        expires_at=data.expires_at,
        is_favorite=data.is_favorite,
    )

    if data.folder_id:
        try:
            folder = PasswordFolder.objects.get(id=data.folder_id, user=user)
            entry.folder = folder
            entry.save()
        except PasswordFolder.DoesNotExist:
            pass

    if data.tags:
        for tag_name in data.tags:
            tag, _ = PasswordTag.objects.get_or_create(user=user, name=tag_name)
            entry.tags.add(tag)

    log_password_access(entry, user, "create", request)

    return 201, entry


@password_router.get("/entries", response=list[PasswordEntryOut], auth=auth_jwt)
def list_password_entries(
    request: HttpRequest,
    query: str | None = None,
    folder_id: str | None = None,
    tags: str | None = None,
    show_expired: bool | None = None,
    show_favorites_only: bool | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list:
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"[DEBUG LIST_ENTRIES] Called with params: query={query}, folder_id={folder_id}, tags={tags}, show_expired={show_expired}, show_favorites_only={show_favorites_only}, sort_by={sort_by}, sort_order={sort_order}, limit={limit}, offset={offset}")
    logger.error(f"[DEBUG LIST_ENTRIES] Request type: {type(request)}, Request: {request}")
    logger.error(f"[DEBUG LIST_ENTRIES] Request auth: {request.auth}")

    user = get_user_from_auth(request.auth)
    logger.error(f"[DEBUG LIST_ENTRIES] User: {user}")

    entries = (
        PasswordEntry.objects.filter(user=user)
        .select_related("folder")
        .prefetch_related("tags")
    )

    # Handle query parameter
    if query:
        entries = entries.filter(
            Q(name__icontains=query)
            | Q(site__icontains=query)
            | Q(username__icontains=query)
            | Q(notes__icontains=query)
        )

    # Handle folder_id
    if folder_id:
        entries = entries.filter(folder_id=folder_id)

    # Handle tags filtering
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',')]
        for tag in tag_list:
            entries = entries.filter(tags__name=tag)

    # Handle show_expired (default to False if not specified)
    if show_expired is None or not show_expired:
        entries = entries.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        )

    # Handle show_favorites_only
    if show_favorites_only:
        entries = entries.filter(is_favorite=True)

    # Handle sort_by (default to updated_at)
    if sort_by is None:
        sort_by = "updated_at"
    if sort_by not in PasswordManagerConstants.VALID_SORT_FIELDS.value:
        sort_by = PasswordManagerConstants.DEFAULT_SORT_FIELD.value

    # Handle sort_order (default to desc)
    if sort_order is None:
        sort_order = "desc"

    order_field = sort_by
    if sort_order == "desc":
        order_field = f"-{order_field}"
    entries = entries.order_by(order_field)

    # Handle pagination (defaults: limit=50, offset=0)
    if limit is None:
        limit = 50
    if offset is None:
        offset = 0
    entries = entries[offset : offset + limit]

    return list(entries)


@password_router.post("/entries/bulk-delete", response={200: MessageOut}, auth=auth_jwt)
@transaction.atomic
def bulk_delete_entries(
    request: HttpRequest, data: PasswordBulkDeleteRequest
) -> dict[str, str]:
    user = get_user_from_auth(request.auth)

    if not verify_master_password(user, data.master_password):
        raise HttpError(400, "Invalid master password")

    # Filter out invalid UUIDs to prevent ValidationError
    from django.core.exceptions import ValidationError
    import uuid

    valid_ids = []
    for entry_id in data.entry_ids:
        try:
            uuid.UUID(entry_id)
            valid_ids.append(entry_id)
        except (ValueError, ValidationError):
            continue

    entries = PasswordEntry.objects.filter(id__in=valid_ids, user=user)

    count = entries.count()

    for entry in entries:
        log_password_access(entry, user, "delete", request)

    entries.delete()

    return {"message": f"Successfully deleted {count} entries"}


@password_router.get(
    "/entries/{entry_id}",
    response={200: PasswordEntryOut, 404: ErrorOut},
    auth=auth_jwt,
)
def get_password_entry(request: HttpRequest, entry_id: str) -> PasswordEntry:
    user = get_user_from_auth(request.auth)

    try:
        entry = PasswordEntry.objects.get(id=entry_id, user=user)

        log_password_access(entry, user, "view", request)

        entry.last_accessed = timezone.now()
        entry.save(update_fields=["last_accessed"])

        return entry
    except PasswordEntry.DoesNotExist:
        raise HttpError(404, "Password entry not found")


@password_router.put(
    "/entries/{entry_id}",
    response={200: PasswordEntryOut, 404: ErrorOut},
    auth=auth_jwt,
)
@transaction.atomic
def update_password_entry(
    request: HttpRequest, entry_id: str, data: PasswordEntryUpdate
):
    """Update a password entry"""

    user = get_user_from_auth(request.auth)

    if not verify_master_password(user, data.master_password):
        raise HttpError(400, "Invalid master password")

    try:
        entry = PasswordEntry.objects.get(id=entry_id, user=user)

        if data.password is not None:
            PasswordEntryHistory.objects.create(
                password_entry=entry,
                encrypted_password=entry.encrypted_password,
                encryption_salt=entry.encryption_salt,
                changed_by=user,
                change_reason="User update",
            )

            encrypted_password, salt = encryption_service.encrypt_password(
                data.password, data.master_password
            )
            entry.encrypted_password = encrypted_password
            entry.encryption_salt = salt

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

        if data.folder_id is not None:
            if data.folder_id:
                try:
                    folder = PasswordFolder.objects.get(id=data.folder_id, user=user)
                    entry.folder = folder
                except PasswordFolder.DoesNotExist:
                    raise HttpError(400, "Folder not found")
            else:
                entry.folder = None

        if data.tags is not None:
            entry.tags.clear()
            for tag_name in data.tags:
                tag, _ = PasswordTag.objects.get_or_create(user=user, name=tag_name)
                entry.tags.add(tag)

        entry.save()

        PasswordAccessLog.objects.create(
            password_entry=entry,
            user=user,
            action="update",
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return entry
    except PasswordEntry.DoesNotExist:
        raise HttpError(404, "Password entry not found")


@password_router.delete(
    "/entries/{entry_id}", response={204: None, 404: ErrorOut}, auth=auth_jwt
)
@transaction.atomic
def delete_password_entry(request: HttpRequest, entry_id: str):
    """Delete a password entry"""

    user = get_user_from_auth(request.auth)

    try:
        entry = PasswordEntry.objects.get(id=entry_id, user=user)

        PasswordAccessLog.objects.create(
            password_entry=entry,
            user=user,
            action="delete",
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        entry.delete()
        return 204, None
    except PasswordEntry.DoesNotExist:
        raise HttpError(404, "Password entry not found")


@password_router.post(
    "/entries/{entry_id}/decrypt",
    response={200: PasswordDecryptResponse, 400: ErrorOut},
    auth=auth_jwt,
)
def decrypt_password(
    request: HttpRequest, entry_id: str, data: PasswordDecryptRequest
) -> dict[str, Any]:
    user = get_user_from_auth(request.auth)

    if not verify_master_password(user, data.master_password):
        raise HttpError(400, "Invalid master password")

    try:
        entry = PasswordEntry.objects.get(id=entry_id, user=user)

        salt = convert_salt_to_bytes(entry.encryption_salt)

        decrypted = encryption_service.decrypt_password(
            entry.encrypted_password, data.master_password, salt
        )

        if not decrypted:
            raise HttpError(400, "Failed to decrypt password")

        strength = encryption_service.check_password_strength(decrypted)

        log_password_access(entry, user, "copy", request)

        return {"password": decrypted, "strength": strength}
    except PasswordEntry.DoesNotExist:
        raise HttpError(404, "Password entry not found")


@password_router.post("/generate", response=PasswordGenerateResponse)
def generate_password(
    request: HttpRequest, data: PasswordGenerateRequest
) -> dict[str, Any]:
    password = encryption_service.generate_secure_password(
        length=data.length,
        include_symbols=data.include_symbols,
        include_numbers=data.include_numbers,
        include_uppercase=data.include_uppercase,
        include_lowercase=data.include_lowercase,
        exclude_ambiguous=data.exclude_ambiguous,
    )

    strength = encryption_service.check_password_strength(password)

    return {"password": password, "strength": strength}


@password_router.post("/folders", response={201: FolderOut}, auth=auth_jwt)
def create_folder(request: HttpRequest, data: FolderIn) -> tuple[int, PasswordFolder]:
    user = get_user_from_auth(request.auth)

    parent = None
    if data.parent_id:
        try:
            parent = PasswordFolder.objects.get(id=data.parent_id, user=user)
        except PasswordFolder.DoesNotExist:
            raise HttpError(400, "Parent folder not found")

    if PasswordFolder.objects.filter(user=user, name=data.name, parent=parent).exists():
        raise HttpError(400, "A folder with this name already exists in this location")

    folder = PasswordFolder.objects.create(
        user=user,
        name=data.name,
        parent=parent,
        icon=data.icon or "",
        color=data.color or "",
    )

    return 201, folder


@password_router.get("/folders", response=list[FolderOut], auth=auth_jwt)
def list_folders(request: HttpRequest) -> list[PasswordFolder]:
    user = get_user_from_auth(request.auth)

    folders = (
        PasswordFolder.objects.filter(user=user)
        .annotate(entry_count=Count("entries"))
        .order_by("name")
    )

    return list(folders)


@password_router.put("/folders/{folder_id}", response={200: FolderOut}, auth=auth_jwt)
def update_folder(
    request: HttpRequest, folder_id: str, data: FolderUpdate
) -> PasswordFolder:
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
def delete_folder(request: HttpRequest, folder_id: str) -> tuple[int, None]:
    user = get_user_from_auth(request.auth)

    try:
        folder = PasswordFolder.objects.get(id=folder_id, user=user)

        PasswordEntry.objects.filter(folder=folder).update(folder=None)

        PasswordFolder.objects.filter(parent=folder).update(parent=None)

        folder.delete()
        return 204, None
    except PasswordFolder.DoesNotExist:
        raise HttpError(404, "Folder not found")


@password_router.post("/tags", response={201: TagOut}, auth=auth_jwt)
def create_tag(request: HttpRequest, data: TagIn) -> tuple[int, PasswordTag]:
    user = get_user_from_auth(request.auth)

    if PasswordTag.objects.filter(user=user, name=data.name).exists():
        raise HttpError(400, "A tag with this name already exists")

    tag = PasswordTag.objects.create(user=user, name=data.name, color=data.color or "")

    return 201, tag


@password_router.get("/tags", response=list[TagOut], auth=auth_jwt)
def list_tags(request: HttpRequest) -> list[PasswordTag]:
    user = get_user_from_auth(request.auth)

    tags = (
        PasswordTag.objects.filter(user=user)
        .annotate(entry_count=Count("entries"))
        .order_by("name")
    )

    return list(tags)


@password_router.delete("/tags/{tag_id}", response={204: None}, auth=auth_jwt)
def delete_tag(request: HttpRequest, tag_id: str) -> tuple[int, None]:
    user = get_user_from_auth(request.auth)

    try:
        tag = PasswordTag.objects.get(id=tag_id, user=user)
        tag.delete()
        return 204, None
    except PasswordTag.DoesNotExist:
        raise HttpError(404, "Tag not found")


@password_router.post(
    "/master-password/change", response={200: MessageOut}, auth=auth_jwt
)
@transaction.atomic
def change_master_password(
    request: HttpRequest, data: MasterPasswordChangeRequest
) -> dict[str, str]:
    user = get_user_from_auth(request.auth)

    if not verify_master_password(user, data.current_master_password):
        raise HttpError(400, "Invalid current master password")

    entries = PasswordEntry.objects.filter(user=user)
    for entry in entries:
        salt_bytes = convert_salt_to_bytes(entry.encryption_salt)
        result = encryption_service.re_encrypt_password(
            entry.encrypted_password,
            data.current_master_password,
            data.new_master_password,
            salt_bytes,
        )

        if result:
            encrypted_password, salt = result
            entry.encrypted_password = encrypted_password
            entry.encryption_salt = salt
            entry.save(update_fields=["encrypted_password", "encryption_salt"])

    user.set_password(data.new_master_password)
    user.save()

    return {
        "message": f"Successfully re-encrypted {entries.count()} passwords with new master password"
    }


@password_router.post("/import", response={200: MessageOut}, auth=auth_jwt)
@transaction.atomic
def import_passwords(
    request: HttpRequest, data: PasswordImportRequest
) -> dict[str, str]:
    user = get_user_from_auth(request.auth)

    if not verify_master_password(user, data.master_password):
        raise HttpError(400, "Invalid master password")

    try:
        file_content = base64.b64decode(data.data).decode("utf-8")

        imported_count = 0

        if data.format == "csv":
            reader = csv.DictReader(io.StringIO(file_content))
            for row in reader:
                if not row.get("name") or not row.get("password"):
                    continue
                if PasswordEntry.objects.filter(
                    user=user,
                    name=row["name"],
                    site=row.get("url", "") or row.get("site", ""),
                ).exists():
                    continue

                encrypted_password, salt = encryption_service.encrypt_password(
                    row["password"], data.master_password
                )
                PasswordEntry.objects.create(
                    user=user,
                    name=row["name"],
                    site=row.get("url", "") or row.get("site", ""),
                    username=row.get("username", "") or row.get("email", ""),
                    encrypted_password=encrypted_password,
                    encryption_salt=salt,
                    notes=row.get("notes", ""),
                )
                imported_count += 1

        elif data.format == "json":
            entries = json.loads(file_content)
            if not isinstance(entries, list):
                entries = [entries]

            for entry in entries:
                if not entry.get("name") or not entry.get("password"):
                    continue
                if PasswordEntry.objects.filter(
                    user=user, name=entry["name"], site=entry.get("site", "")
                ).exists():
                    continue

                encrypted_password, salt = encryption_service.encrypt_password(
                    entry["password"], data.master_password
                )
                PasswordEntry.objects.create(
                    user=user,
                    name=entry["name"],
                    site=entry.get("site", ""),
                    username=entry.get("username", ""),
                    encrypted_password=encrypted_password,
                    encryption_salt=salt,
                    notes=entry.get("notes", ""),
                )
                imported_count += 1

        else:
            raise HttpError(400, f"Unsupported import format: {data.format}")

        return {"message": f"Successfully imported {imported_count} passwords"}

    except Exception as e:
        raise HttpError(400, f"Import failed: {str(e)}")


@password_router.post("/export", response={200: dict}, auth=auth_jwt)
def export_passwords(
    request: HttpRequest, data: PasswordExportRequest
) -> dict[str, Any]:
    user = get_user_from_auth(request.auth)

    if not verify_master_password(user, data.master_password):
        raise HttpError(400, "Invalid master password")

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
            "notes": entry.notes,
        }

        if data.include_passwords:
            salt = convert_salt_to_bytes(entry.encryption_salt)
            decrypted = encryption_service.decrypt_password(
                entry.encrypted_password, data.master_password, salt
            )
            if decrypted:
                entry_data["password"] = decrypted

        export_data.append(entry_data)

    if data.format == "json":
        return {
            "format": "json",
            "data": base64.b64encode(
                json.dumps(export_data, indent=2).encode()
            ).decode(),
            "filename": "passwords_export.json",
        }

    elif data.format == "csv":
        output = io.StringIO()
        if export_data:
            writer = csv.DictWriter(output, fieldnames=export_data[0].keys())
            writer.writeheader()
            writer.writerows(export_data)

        return {
            "format": "csv",
            "data": base64.b64encode(output.getvalue().encode()).decode(),
            "filename": "passwords_export.csv",
        }

    else:
        raise HttpError(400, f"Unsupported export format: {data.format}")


@password_router.post("/share", response={201: ShareLinkOut}, auth=auth_jwt)
@transaction.atomic
def create_share_link(
    request: HttpRequest, data: ShareLinkIn
) -> tuple[int, dict[str, Any]]:
    user = get_user_from_auth(request.auth)

    if not verify_master_password(user, data.master_password):
        raise HttpError(400, "Invalid master password")

    try:
        entry = PasswordEntry.objects.get(id=data.password_entry_id, user=user)
        salt = convert_salt_to_bytes(entry.encryption_salt)
        decrypted = encryption_service.decrypt_password(
            entry.encrypted_password, data.master_password, salt
        )

        if not decrypted:
            raise HttpError(400, "Failed to decrypt password")

        expires_at = timezone.now() + timezone.timedelta(hours=data.expires_in_hours)

        share_link = PasswordShareLink.objects.create(
            password_entry=entry,
            created_by=user,
            max_views=data.max_views,
            expires_at=expires_at,
            require_authentication=data.require_authentication,
            allowed_email=data.allowed_email or "",
        )

        log_password_access(entry, user, "share", request)
        share_url = f"{request.build_absolute_uri('/api/passwords/shared/')}{share_link.share_token}"

        return 201, {
            "id": str(share_link.id),
            "share_url": share_url,
            "max_views": share_link.max_views,
            "current_views": share_link.current_views,
            "expires_at": share_link.expires_at,
            "require_authentication": share_link.require_authentication,
            "allowed_email": share_link.allowed_email,
            "created_at": share_link.created_at,
        }

    except PasswordEntry.DoesNotExist:
        raise HttpError(404, "Password entry not found")


@password_router.get("/shared/{share_token}", response={200: dict, 404: ErrorOut})
def access_shared_password(request: HttpRequest, share_token: str) -> dict[str, Any]:
    try:
        share_link = PasswordShareLink.objects.get(share_token=share_token)

        if not share_link.is_valid:
            raise HttpError(404, "Share link is expired or has reached maximum views")

        if share_link.require_authentication:
            pass

        share_link.current_views += 1
        share_link.last_accessed = timezone.now()
        share_link.accessed_by_ip = request.META.get("REMOTE_ADDR")
        share_link.save()

        entry = share_link.password_entry

        return {
            "name": entry.name,
            "site": entry.site,
            "username": entry.username,
            "views_remaining": share_link.max_views - share_link.current_views,
            "expires_at": share_link.expires_at,
        }

    except PasswordShareLink.DoesNotExist:
        raise HttpError(404, "Invalid share link")


@password_router.get("/stats", response={200: dict}, auth=auth_jwt)
def get_password_stats(request: HttpRequest) -> dict[str, Any]:
    user = get_user_from_auth(request.auth)

    total_passwords = PasswordEntry.objects.filter(user=user).count()

    expired_passwords = PasswordEntry.objects.filter(
        user=user, expires_at__lt=timezone.now()
    ).count()

    expiring_soon = PasswordEntry.objects.filter(
        user=user,
        expires_at__gt=timezone.now(),
        expires_at__lt=timezone.now()
        + timezone.timedelta(
            days=PasswordManagerConstants.DEFAULT_PASSWORD_EXPIRY_WARNING_DAYS.value
        ),
    ).count()

    favorite_count = PasswordEntry.objects.filter(user=user, is_favorite=True).count()

    folder_count = PasswordFolder.objects.filter(user=user).count()
    tag_count = PasswordTag.objects.filter(user=user).count()

    recent_entries = PasswordEntry.objects.filter(user=user).order_by("-created_at")[:5]

    recently_accessed = PasswordEntry.objects.filter(
        user=user, last_accessed__isnull=False
    ).order_by("-last_accessed")[:5]

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
        ],
    }
