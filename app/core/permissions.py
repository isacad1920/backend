"""RBAC permission utilities (normalized tables).

Replaces legacy PermissionManager static lists & JSON overrides.

Precedence:
 1. ADMIN role => allow
 2. User override DENY
 3. User override ALLOW
 4. RolePermission
 5. Else deny
"""
from __future__ import annotations

from typing import Iterable, Set

from fastapi import Depends, HTTPException, status

from app.core.config import UserRole
from app.db.prisma import get_db


async def _fetch_user_role_and_overrides(user_id: int, db):
    user = await db.user.find_unique(where={"id": user_id})
    if not user:
        return None, []
    overrides = await db.userpermissionoverride.find_many(
        where={"userId": user_id},
        include={"permission": True},
    )
    return user, overrides


async def _fetch_role_permissions(role: UserRole, db):
    return await db.rolepermission.find_many(
        where={"role": role.value}, include={"permission": True}
    )


async def get_user_effective_permissions(user_id: int, db) -> Set[str]:
    user, overrides = await _fetch_user_role_and_overrides(user_id, db)
    if not user:
        return set()
    role = UserRole(user.role)
    if role == UserRole.ADMIN:
        all_perms = await db.permission.find_many()
        return {f"{p.resource}:{p.action}" for p in all_perms} | {"*:*"}

    role_perms = await _fetch_role_permissions(role, db)
    base = {f"{rp.permission.resource}:{rp.permission.action}" for rp in role_perms}

    denied = set()
    allowed = set()
    for ov in overrides:
        ps = f"{ov.permission.resource}:{ov.permission.action}"
        if ov.type == "DENY":
            denied.add(ps)
        else:
            allowed.add(ps)
    return (base | allowed) - denied


async def check_permission(user, resource: str, action: str, db) -> bool:
    role = UserRole(user.role)
    if role == UserRole.ADMIN:
        return True
    permission = await db.permission.find_first(where={"resource": resource, "action": action})
    if not permission:
        return False
    override = await db.userpermissionoverride.find_first(
        where={"userId": user.id, "permissionId": permission.id}
    )
    if override:
        if override.type == "DENY":
            return False
        if override.type == "ALLOW":
            return True
    role_perm = await db.rolepermission.find_first(
        where={"role": role.value, "permissionId": permission.id}
    )
    return role_perm is not None


def require_permission(resource: str, action: str):
    # Local import to avoid circular dependency (dependencies imports this module)
    from app.core.dependencies import get_current_active_user  # type: ignore

    async def _dep(current_user=Depends(get_current_active_user), db=Depends(get_db)):
        if not await check_permission(current_user, resource, action, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission {resource}:{action}",
            )
        return True

    return _dep


async def ensure_permissions(user, required: Iterable[str], db) -> bool:
    role = UserRole(user.role)
    if role == UserRole.ADMIN:
        return True
    effective = await get_user_effective_permissions(user.id, db)
    return all(p in effective for p in required)
