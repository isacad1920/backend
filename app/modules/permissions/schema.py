"""
Permission management schemas for custom permission overrides.
"""
from pydantic import BaseModel
from app.core.base_schema import ApiBaseModel
from typing import List, Optional
from app.core.config import UserRole


class PermissionGrantRequest(ApiBaseModel):
    """Request to grant custom permission to a user."""
    user_id: int
    permissions: List[str]
    reason: Optional[str] = None


class PermissionRevokeRequest(ApiBaseModel):
    """Request to revoke custom permission from a user."""
    user_id: int
    permissions: List[str]
    reason: Optional[str] = None


class UserPermissionResponse(ApiBaseModel):
    """Response showing user's complete permissions."""
    user_id: int
    role: UserRole
    role_permissions: List[str]
    custom_permissions: List[str]
    total_permissions: List[str]


class AvailablePermissionsResponse(ApiBaseModel):
    """Response with all available permissions in the system."""
    permissions: List[str]
    grouped_permissions: dict


class PermissionAuditLog(ApiBaseModel):
    """Audit log for permission changes."""
    user_id: int
    admin_id: int
    action: str  # "grant" or "revoke"
    permissions: List[str]
    reason: Optional[str]
    timestamp: str
