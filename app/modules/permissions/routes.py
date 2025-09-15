"""RBAC Permissions Routes (normalized)."""
from fastapi import APIRouter, Depends, HTTPException, Path

from app.core.dependencies import get_current_active_user
from app.core.permissions import get_user_effective_permissions
from app.core.response import ResponseBuilder, SuccessResponse
from app.core.config import UserRole
from app.db.prisma import get_db
from app.modules.permissions.schema import (
    PermissionCreate,
    PermissionListResponse,
    PermissionRead,
    RolePermissionAssignResponse,
    RolePermissionList,
    UserOverrideRequest,
    UserOverrideResponse,
    UserPermissionDetail,
)

router = APIRouter(prefix="/permissions", tags=["🔑 Permissions"])


@router.get("", response_model=SuccessResponse[PermissionListResponse])
@router.get("/", response_model=SuccessResponse[PermissionListResponse])
async def list_permissions(current_user=Depends(get_current_active_user), db=Depends(get_db)):
    perms = await db.permission.find_many()
    data = [PermissionRead(id=p.id, resource=p.resource, action=p.action) for p in perms]
    return ResponseBuilder.success(PermissionListResponse(permissions=data), "Permissions retrieved")


@router.post("", response_model=SuccessResponse[PermissionRead])
@router.post("/", response_model=SuccessResponse[PermissionRead])
async def create_permission(payload: PermissionCreate, current_user=Depends(get_current_active_user), db=Depends(get_db)):
    # Idempotent create: if unique constraint hit, return existing
    existing = await db.permission.find_first(where={"resource": payload.resource, "action": payload.action})
    if existing:
        return ResponseBuilder.success(PermissionRead(id=existing.id, resource=existing.resource, action=existing.action), "Permission exists")
    try:
        created = await db.permission.create(data={"resource": payload.resource, "action": payload.action})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create permission: {e}")
    return ResponseBuilder.success(PermissionRead(id=created.id, resource=created.resource, action=created.action), "Permission created")


@router.delete("/{permission_id}")
async def delete_permission(permission_id: int = Path(...), current_user=Depends(get_current_active_user), db=Depends(get_db)):
    try:
        await db.permission.delete(where={"id": permission_id})
    except Exception:
        raise HTTPException(status_code=404, detail="Permission not found")
    return ResponseBuilder.success({"id": permission_id}, "Permission deleted")


@router.get("/roles/{role}", response_model=SuccessResponse[RolePermissionList])
async def list_role_permissions(role: UserRole, current_user=Depends(get_current_active_user), db=Depends(get_db)):
    rps = await db.rolepermission.find_many(where={"role": role.value}, include={"permission": True})
    perms = [PermissionRead(id=rp.permission.id, resource=rp.permission.resource, action=rp.permission.action) for rp in rps]
    return ResponseBuilder.success(RolePermissionList(role=role, permissions=perms), "Role permissions retrieved")


@router.post("/roles/{role}/{permission_id}", response_model=SuccessResponse[RolePermissionAssignResponse])
async def assign_role_permission(role: UserRole, permission_id: int, current_user=Depends(get_current_active_user), db=Depends(get_db)):
    p = await db.permission.find_unique(where={"id": permission_id})
    if not p:
        raise HTTPException(status_code=404, detail="Permission not found")
    try:
        await db.rolepermission.create(data={"role": role.value, "permissionId": permission_id})
    except Exception:
        pass
    return ResponseBuilder.success(RolePermissionAssignResponse(role=role, permission_id=permission_id, assigned=True), "Role permission assigned")


@router.delete("/roles/{role}/{permission_id}")
async def unassign_role_permission(role: UserRole, permission_id: int, current_user=Depends(get_current_active_user), db=Depends(get_db)):
    rp = await db.rolepermission.find_first(where={"role": role.value, "permissionId": permission_id})
    if not rp:
        raise HTTPException(status_code=404, detail="Role permission not found")
    await db.rolepermission.delete(where={"id": rp.id})
    return ResponseBuilder.success({"role": role, "permission_id": permission_id}, "Role permission removed")


@router.get("/users/{user_id}", response_model=SuccessResponse[UserPermissionDetail])
async def get_user_permissions(user_id: int, current_user=Depends(get_current_active_user), db=Depends(get_db)):
    user = await db.user.find_unique(where={"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    role = UserRole(user.role)
    overrides = await db.userpermissionoverride.find_many(where={"userId": user_id}, include={"permission": True})
    allowed = []
    denied = []
    for ov in overrides:
        perm_str = f"{ov.permission.resource}:{ov.permission.action}"
        if ov.type == "DENY":
            denied.append(perm_str)
        else:
            allowed.append(perm_str)
    role_perms = await db.rolepermission.find_many(where={"role": role.value}, include={"permission": True})
    role_perm_strings = [f"{rp.permission.resource}:{rp.permission.action}" for rp in role_perms]
    effective = await get_user_effective_permissions(user_id, db)
    return ResponseBuilder.success(
        UserPermissionDetail(
            user_id=user_id,
            role=role,
            effective=sorted(list(effective)),
            allowed_overrides=sorted(allowed),
            denied_overrides=sorted(denied),
            role_permissions=sorted(role_perm_strings),
        ),
        "User permissions retrieved",
    )

@router.get("/effective/{user_id}")
async def get_effective_permissions(user_id: int, current_user=Depends(get_current_active_user), db=Depends(get_db)):
    """Lightweight endpoint returning only the effective permission strings plus provenance counts.

    Useful for frontend guards without needing full role/override detail structure.
    """
    user = await db.user.find_unique(where={"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    role = UserRole(user.role)
    effective = await get_user_effective_permissions(user_id, db)
    overrides = await db.userpermissionoverride.find_many(where={"userId": user_id}, include={"permission": True})
    allowed = 0
    denied = 0
    for ov in overrides:
        if ov.type == "DENY":
            denied += 1
        else:
            allowed += 1
    return ResponseBuilder.success({
        "user_id": user_id,
        "role": role.value,
        "count": len(effective),
        "effective": sorted(list(effective)),
        "override_counts": {"allow": allowed, "deny": denied},
    }, "Effective permissions retrieved")


@router.post("/users/{user_id}/{permission_id}", response_model=SuccessResponse[UserOverrideResponse])
async def set_user_override(user_id: int, permission_id: int, payload: UserOverrideRequest, current_user=Depends(get_current_active_user), db=Depends(get_db)):
    perm = await db.permission.find_unique(where={"id": permission_id})
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
    user = await db.user.find_unique(where={"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    existing = await db.userpermissionoverride.find_first(where={"userId": user_id, "permissionId": permission_id})
    if existing:
        await db.userpermissionoverride.update(where={"id": existing.id}, data={"type": payload.type})
    else:
        await db.userpermissionoverride.create(data={"userId": user_id, "permissionId": permission_id, "type": payload.type})
    return ResponseBuilder.success(UserOverrideResponse(user_id=user_id, permission_id=permission_id, type=payload.type, applied=True), "Override applied")


@router.delete("/users/{user_id}/{permission_id}")
async def delete_user_override(user_id: int, permission_id: int, current_user=Depends(get_current_active_user), db=Depends(get_db)):
    existing = await db.userpermissionoverride.find_first(where={"userId": user_id, "permissionId": permission_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Override not found")
    await db.userpermissionoverride.delete(where={"id": existing.id})
    return ResponseBuilder.success({"user_id": user_id, "permission_id": permission_id}, "Override removed")
