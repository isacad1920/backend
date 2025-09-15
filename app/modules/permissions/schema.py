"""
Permission management schemas for custom permission overrides.
"""

from app.core.base_schema import ApiBaseModel
from app.core.config import UserRole


# --- Core Permission Models ---
class PermissionCreate(ApiBaseModel):
    resource: str
    action: str


class PermissionRead(ApiBaseModel):
    id: int
    resource: str
    action: str


class PermissionListResponse(ApiBaseModel):
    permissions: list[PermissionRead]


# --- Role Permission Models ---
class RolePermissionAssignResponse(ApiBaseModel):
    role: UserRole
    permission_id: int
    assigned: bool


class RolePermissionList(ApiBaseModel):
    role: UserRole
    permissions: list[PermissionRead]


# --- User Override Models ---
class UserOverrideRequest(ApiBaseModel):
    type: str  # 'ALLOW' | 'DENY'


class UserOverrideResponse(ApiBaseModel):
    user_id: int
    permission_id: int
    type: str
    applied: bool


class UserPermissionDetail(ApiBaseModel):
    user_id: int
    role: UserRole
    effective: list[str]
    allowed_overrides: list[str]
    denied_overrides: list[str]
    role_permissions: list[str]


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
