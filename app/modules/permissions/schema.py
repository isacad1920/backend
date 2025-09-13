"""
Permission management schemas for custom permission overrides.
"""

from app.core.base_schema import ApiBaseModel
from app.core.config import UserRole


class PermissionGrantRequest(ApiBaseModel):
    """Request to grant custom permission to a user."""
    user_id: int
    permissions: list[str]
    reason: str | None = None


class PermissionRevokeRequest(ApiBaseModel):
    """Request to revoke custom permission from a user."""
    user_id: int
    permissions: list[str]
    reason: str | None = None


class UserPermissionResponse(ApiBaseModel):
    """Response showing user's complete permissions."""
    user_id: int
    role: UserRole
    role_permissions: list[str]
    custom_permissions: list[str]
    total_permissions: list[str]


class AvailablePermissionsResponse(ApiBaseModel):
    """Response with all available permissions in the system."""
    permissions: list[str]
    grouped_permissions: dict


class PermissionAuditLog(ApiBaseModel):
    """Audit log for permission changes."""
    user_id: int
    admin_id: int
    action: str  # "grant" or "revoke"
    permissions: list[str]
    reason: str | None
    timestamp: str
