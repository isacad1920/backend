"""
Permission management service for handling custom permission overrides.
"""
import logging
from datetime import datetime
from typing import Any

from app.core.config import UserRole
from app.core.security import PermissionManager
from app.modules.permissions.schema import (
    AvailablePermissionsResponse,
    PermissionAuditLog,
    PermissionGrantRequest,
    PermissionRevokeRequest,
    UserPermissionResponse,
)

logger = logging.getLogger(__name__)


class PermissionService:
    """Service for managing custom user permissions."""
    
    def __init__(self):
        self.audit_logs: list[PermissionAuditLog] = []
    
    async def grant_permissions(self, request: PermissionGrantRequest, admin_id: int) -> dict[str, Any]:
        """Grant custom permissions to a user."""
        try:
            granted_permissions = []
            
            # Validate permissions exist
            all_permissions = PermissionManager.get_all_available_permissions()
            invalid_permissions = [p for p in request.permissions if p not in all_permissions]
            
            if invalid_permissions:
                return {
                    "success": False,
                    "message": f"Invalid permissions: {', '.join(invalid_permissions)}",
                    "data": None
                }
            
            # Grant each permission
            for permission in request.permissions:
                if PermissionManager.grant_custom_permission(request.user_id, permission):
                    granted_permissions.append(permission)
            
            # Log the action
            audit_log = PermissionAuditLog(
                user_id=request.user_id,
                admin_id=admin_id,
                action="grant",
                permissions=granted_permissions,
                reason=request.reason,
                timestamp=datetime.utcnow().isoformat()
            )
            self.audit_logs.append(audit_log)
            
            logger.info(f"Admin {admin_id} granted permissions {granted_permissions} to user {request.user_id}")
            
            return {
                "success": True,
                "message": f"Granted {len(granted_permissions)} permissions successfully",
                "data": {
                    "granted_permissions": granted_permissions,
                    "user_id": request.user_id
                }
            }
            
        except Exception as e:
            logger.error(f"Error granting permissions: {str(e)}")
            return {
                "success": False,
                "message": f"Error granting permissions: {str(e)}",
                "data": None
            }
    
    async def revoke_permissions(self, request: PermissionRevokeRequest, admin_id: int) -> dict[str, Any]:
        """Revoke custom permissions from a user."""
        try:
            revoked_permissions = []
            
            # Revoke each permission
            for permission in request.permissions:
                if PermissionManager.revoke_custom_permission(request.user_id, permission):
                    revoked_permissions.append(permission)
            
            # Log the action
            audit_log = PermissionAuditLog(
                user_id=request.user_id,
                admin_id=admin_id,
                action="revoke",
                permissions=revoked_permissions,
                reason=request.reason,
                timestamp=datetime.utcnow().isoformat()
            )
            self.audit_logs.append(audit_log)
            
            logger.info(f"Admin {admin_id} revoked permissions {revoked_permissions} from user {request.user_id}")
            
            return {
                "success": True,
                "message": f"Revoked {len(revoked_permissions)} permissions successfully",
                "data": {
                    "revoked_permissions": revoked_permissions,
                    "user_id": request.user_id
                }
            }
            
        except Exception as e:
            logger.error(f"Error revoking permissions: {str(e)}")
            return {
                "success": False,
                "message": f"Error revoking permissions: {str(e)}",
                "data": None
            }
    
    async def get_user_permissions(self, user_id: int, user_role: UserRole) -> UserPermissionResponse:
        """Get complete permissions for a user including custom overrides."""
        role_permissions = PermissionManager.get_user_permissions(user_role)
        custom_permissions = PermissionManager.get_custom_permissions(user_id)
        total_permissions = PermissionManager.get_user_permissions(user_role, custom_permissions)
        
        return UserPermissionResponse(
            user_id=user_id,
            role=user_role,
            role_permissions=role_permissions,
            custom_permissions=custom_permissions,
            total_permissions=total_permissions
        )
    
    async def get_available_permissions(self) -> AvailablePermissionsResponse:
        """Get all available permissions in the system."""
        permissions = PermissionManager.get_all_available_permissions()
        
        # Group permissions by resource
        grouped_permissions = {}
        for permission in permissions:
            if ":" in permission:
                resource, action = permission.split(":", 1)
                if resource not in grouped_permissions:
                    grouped_permissions[resource] = []
                grouped_permissions[resource].append(action)
        
        return AvailablePermissionsResponse(
            permissions=permissions,
            grouped_permissions=grouped_permissions
        )
    
    async def get_audit_logs(self, user_id: int | None = None) -> list[PermissionAuditLog]:
        """Get permission audit logs."""
        if user_id:
            return [log for log in self.audit_logs if log.user_id == user_id]
        return self.audit_logs
    
    async def bulk_grant_permissions(self, user_ids: list[int], permissions: list[str], 
                                   admin_id: int, reason: str | None = None) -> dict[str, Any]:
        """Grant permissions to multiple users at once."""
        results = []
        
        for user_id in user_ids:
            request = PermissionGrantRequest(
                user_id=user_id,
                permissions=permissions,
                reason=reason
            )
            result = await self.grant_permissions(request, admin_id)
            results.append({
                "user_id": user_id,
                "success": result["success"],
                "message": result["message"]
            })
        
        return {
            "success": True,
            "message": f"Processed {len(user_ids)} users",
            "data": results
        }


# Global permission service instance
permission_service = PermissionService()
