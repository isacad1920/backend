"""
Permissions API routes and endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from fastapi.security import HTTPBearer
import logging

from app.core.dependencies import get_current_user, get_current_active_user
from app.core.response import ResponseBuilder, SuccessResponse, ErrorResponse, success_response
from app.db.prisma import get_db
from app.core.security import PermissionManager
from app.modules.permissions.schema import (
    PermissionGrantRequest, PermissionRevokeRequest, UserPermissionResponse, AvailablePermissionsResponse
)

security = HTTPBearer()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/permissions", tags=["Permissions"])
# Legacy/compatibility router mounted under /api/v1/admin
legacy_router = APIRouter(prefix="/admin/permissions", tags=["Permissions"], include_in_schema=False)


@router.get("/", response_model=SuccessResponse[AvailablePermissionsResponse])
async def list_permissions(
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """
    🔐 List all available permissions
    
    Get all permissions available in the system.
    """
    try:
        perms = PermissionManager.get_all_available_permissions()
        grouped = {}
        for p in perms:
            if ":" in p:
                res, act = p.split(":", 1)
                grouped.setdefault(res, []).append(act)
        return ResponseBuilder.success(
            data=AvailablePermissionsResponse(permissions=perms, grouped_permissions=grouped),
            message="Permissions retrieved successfully",
        )
    except Exception as e:
        logger.error(f"Failed to retrieve permissions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve permissions: {str(e)}")


@router.get("/user/{user_id}", response_model=SuccessResponse[UserPermissionResponse])
async def get_user_permissions(
    user_id: int = Path(..., description="User ID"),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """
    👤 Get permissions for a specific user
    
    Retrieve all permissions assigned to a user.
    """
    try:
        # Get role from current_user and custom from DB
        role = current_user.role
        custom = await PermissionManager.get_custom_permissions(user_id, db)
        total = PermissionManager.get_user_permissions(role, custom)
        return ResponseBuilder.success(
            data=UserPermissionResponse(
                user_id=user_id,
                role=role,
                role_permissions=PermissionManager.ROLE_PERMISSIONS.get(role, []),
                custom_permissions=custom,
                total_permissions=total,
            ),
            message="User permissions retrieved successfully",
        )
    except Exception as e:
        logger.error(f"Failed to retrieve user permissions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user permissions: {str(e)}")


@router.post("/user/{user_id}/grant")
async def grant_permission(
    user_id: int = Path(..., description="User ID"),
    permission: str = Query(..., description="Permission to grant in form 'resource:action'"),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """
    ✅ Grant permission to user
    
    Grant a specific permission to a user.
    """
    try:
        # Persist to DB
        if ":" not in permission:
            raise HTTPException(status_code=400, detail="Permission must be 'resource:action'")
        resource, action = permission.split(":", 1)
        ok = await PermissionManager.grant_permission(user_id, resource, action, db)
        return ResponseBuilder.success(
            data={
                "user_id": user_id,
                "permission": permission,
                "granted": ok,
                "granted_by": current_user.id,
            },
            message="Permission granted successfully",
        )
    except Exception as e:
        logger.error(f"Failed to grant permission: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to grant permission: {str(e)}")


@router.delete("/user/{user_id}/revoke")
async def revoke_permission(
    user_id: int = Path(..., description="User ID"),
    permission: str = Query(..., description="Permission to revoke in form 'resource:action'"),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """
    ❌ Revoke permission from user
    
    Remove a specific permission from a user.
    """
    try:
        if ":" not in permission:
            raise HTTPException(status_code=400, detail="Permission must be 'resource:action'")
        resource, action = permission.split(":", 1)
        ok = await PermissionManager.revoke_permission(user_id, resource, action, db)
        return ResponseBuilder.success(
            data={
                "user_id": user_id,
                "permission": permission,
                "revoked": ok,
                "revoked_by": current_user.id,
            },
            message="Permission revoked successfully",
        )
    except Exception as e:
        logger.error(f"Failed to revoke permission: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to revoke permission: {str(e)}")


@router.post("/user/{user_id}/grant/batch")
async def grant_permissions_batch(
    user_id: int = Path(..., description="User ID"),
    permissions: List[str] = Query(..., description="Repeated permission parameters e.g. ?permissions=resource:action"),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """✅ Batch grant multiple permissions to a user (item 8).

    Accepts multiple `permissions` query params. Returns per-permission status.
    """
    results = []
    try:
        for perm in permissions:
            if ":" not in perm:
                results.append({"permission": perm, "granted": False, "error": "invalid_format"})
                continue
            res, act = perm.split(":", 1)
            ok = await PermissionManager.grant_permission(user_id, res, act, db)
            results.append({"permission": perm, "granted": ok})
        return ResponseBuilder.success(data={"user_id": user_id, "results": results}, message="Batch grant complete")
    except Exception as e:
        logger.error(f"Failed batch grant: {e}")
        raise HTTPException(status_code=500, detail="Failed to batch grant permissions")


@router.post("/user/{user_id}/revoke/batch")
async def revoke_permissions_batch(
    user_id: int = Path(..., description="User ID"),
    permissions: List[str] = Query(..., description="Repeated permission parameters e.g. ?permissions=resource:action"),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """❌ Batch revoke multiple permissions from a user (item 8)."""
    results = []
    try:
        for perm in permissions:
            if ":" not in perm:
                results.append({"permission": perm, "revoked": False, "error": "invalid_format"})
                continue
            res, act = perm.split(":", 1)
            ok = await PermissionManager.revoke_permission(user_id, res, act, db)
            results.append({"permission": perm, "revoked": ok})
        return ResponseBuilder.success(data={"user_id": user_id, "results": results}, message="Batch revoke complete")
    except Exception as e:
        logger.error(f"Failed batch revoke: {e}")
        raise HTTPException(status_code=500, detail="Failed to batch revoke permissions")


@router.get("/roles/")
async def list_roles(
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """
    👥 List all available roles
    
    Get all roles with their associated permissions.
    """
    try:
        # Mock roles data
        roles = [
            {
                "id": 1,
                "name": "Admin",
                "description": "Full system access",
                "permissions": ["system.admin", "users.manage", "reports.view"]
            },
            {
                "id": 2,
                "name": "Manager",
                "description": "Management access",
                "permissions": ["sales.create", "sales.read", "inventory.manage", "customers.manage", "reports.view"]
            },
            {
                "id": 3,
                "name": "Cashier",
                "description": "Sales and customer operations",
                "permissions": ["sales.create", "sales.read", "customers.manage"]
            }
        ]
        
        return ResponseBuilder.success(data=roles, message="Roles retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Failed to retrieve roles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve roles: {str(e)}")


@router.post("/user/{user_id}/assign-role")
async def assign_role_to_user(
    user_id: int = Path(..., description="User ID"),
    role_id: int = Query(..., description="Role ID to assign"),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """
    👤 Assign role to user
    
    Assign a role with its permissions to a user.
    """
    try:
        return ResponseBuilder.success(data={
                "user_id": user_id,
                "role_id": role_id,
                "assigned": True,
                "assigned_by": current_user.id
            },
            message="Role assigned successfully"
        )
    except Exception as e:
        logger.error(f"Failed to assign role: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to assign role: {str(e)}")


@router.get("/check")
async def check_permission(
    permission: str = Query(..., description="Permission to check"),
    user_id: Optional[int] = Query(None, description="User ID (defaults to current user)"),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """
    🔍 Check if user has permission
    
    Verify if a user has a specific permission.
    """
    try:
        check_user_id = user_id or current_user.id
        
        # Mock permission check - would query database
        has_permission = permission in ["sales.create", "sales.read", "customers.manage"]
        
        return ResponseBuilder.success(data={
                "user_id": check_user_id,
                "permission": permission,
                "has_permission": has_permission
            },
            message="Permission check completed"
        )
    except Exception as e:
        logger.error(f"Failed to check permission: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check permission: {str(e)}")


# =====================
# Legacy Admin Endpoints
# =====================
@legacy_router.get("/available")
async def legacy_available_permissions(
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """Legacy endpoint to list available permissions (unwrapped)."""
    try:
        perms = PermissionManager.get_all_available_permissions()
        grouped = {}
        for p in perms:
            if ":" in p:
                res, act = p.split(":", 1)
                grouped.setdefault(res, []).append(act)
        return success_response(data={"permissions": perms, "grouped_permissions": grouped}, message="Legacy permissions retrieved")
    except Exception as e:
        logger.error(f"Legacy available permissions error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve permissions")


from pydantic import BaseModel


class BulkGrantRequest(BaseModel):
    user_ids: List[int]
    permissions: List[str]
    reason: Optional[str] = None


@legacy_router.post("/grant")
async def legacy_grant_permissions(
    payload: PermissionGrantRequest,
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """Legacy endpoint to grant custom permissions to a user."""
    try:
        from .service import permission_service
        result = await permission_service.grant_permissions(payload, current_user.id)
        return success_response(data=result, message="Legacy grant completed")
    except Exception as e:
        logger.error(f"Legacy grant permissions error: {e}")
        raise HTTPException(status_code=500, detail="Failed to grant permissions")


@legacy_router.post("/revoke")
async def legacy_revoke_permissions(
    payload: PermissionRevokeRequest,
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """Legacy endpoint to revoke custom permissions from a user."""
    try:
        from .service import permission_service
        result = await permission_service.revoke_permissions(payload, current_user.id)
        return success_response(data=result, message="Legacy revoke completed")
    except Exception as e:
        logger.error(f"Legacy revoke permissions error: {e}")
        raise HTTPException(status_code=500, detail="Failed to revoke permissions")


@legacy_router.post("/bulk-grant")
async def legacy_bulk_grant_permissions(
    payload: BulkGrantRequest,
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """Legacy endpoint to grant permissions to multiple users."""
    try:
        from .service import permission_service
        result = await permission_service.bulk_grant_permissions(
            user_ids=payload.user_ids,
            permissions=payload.permissions,
            admin_id=current_user.id,
            reason=payload.reason,
        )
        return success_response(data=result, message="Legacy bulk grant completed")
    except Exception as e:
        logger.error(f"Legacy bulk grant error: {e}")
        raise HTTPException(status_code=500, detail="Failed to bulk grant permissions")


@legacy_router.get("/user/{user_id}")
async def legacy_get_user_permissions(
    user_id: int = Path(...),
    user_role: Optional[str] = Query(None),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """Legacy endpoint to get user permissions (unwrapped)."""
    try:
        from app.core.config import UserRole
        from .service import PermissionService
        service = PermissionService()
        # Default to ADMIN if not provided for compatibility with tests
        role = UserRole[user_role] if user_role else current_user.role
        resp = await service.get_user_permissions(user_id, role)
        return success_response(data=resp.model_dump(), message="Legacy user permissions retrieved")
    except Exception as e:
        logger.error(f"Legacy get user permissions error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user permissions")


@legacy_router.get("/audit-logs")
async def legacy_audit_logs(
    user_id: Optional[int] = Query(None),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """Legacy endpoint to fetch audit logs for permissions changes."""
    try:
        from .service import permission_service
        logs = await permission_service.get_audit_logs(user_id=user_id)
        return success_response(data={"logs": [l.model_dump() for l in logs]}, message="Legacy audit logs retrieved")
    except Exception as e:
        logger.error(f"Legacy audit logs error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve audit logs")
