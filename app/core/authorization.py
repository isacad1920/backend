"""Authorization helpers (roadmap item 7).

Provides dependency builders to enforce permission checks in a consistent
and declarative way, reducing repetitive role/permission logic scattered
across routes.
"""
from __future__ import annotations

from collections.abc import Callable
from functools import wraps

from fastapi import Depends, HTTPException

from app.core.dependencies import get_current_active_user, get_db
from app.core.permissions import check_permission as rbac_check_permission, get_user_effective_permissions
from app.core.config import UserRole


def require_permissions(*permissions: str, any_of: bool = False):
    """Return a FastAPI dependency that enforces the given permissions.

    Usage (parameter form):
        async def route(..., _auth = Depends(require_permissions('sales:write'))):

    Or as a decorator (wraps the endpoint function):
        @with_permissions('sales:write')
        async def route(...):
            ...
    """

    async def _dep(
        current_user = Depends(get_current_active_user),
        db = Depends(get_db),  # noqa: F841 (future: custom permissions from DB)
    ):
        role = getattr(current_user, 'role', None)
        if role == UserRole.ADMIN:
            return
        # Check each required permission
        effective = await get_user_effective_permissions(int(current_user.id), db)
        if any_of:
            allowed = any(p in effective for p in permissions)
        else:
            allowed = all(p in effective for p in permissions)
        if not allowed:
            needed = " or ".join(permissions) if any_of else ", ".join(permissions)
            raise HTTPException(status_code=403, detail=f"Missing permission: {needed}")

    return _dep


def with_permissions(*permissions: str, any_of: bool = False):
    """Decorator variant wrapping an endpoint function.

    Injects `current_user` and `db` via dependencies then enforces the rules
    before calling the wrapped function. Keeps original signature for docs.
    """

    def _outer(func: Callable):
        @wraps(func)
        async def _wrapped(
            *args,
            current_user = Depends(get_current_active_user),
            db = Depends(get_db),
            **kwargs,
        ):
            role = getattr(current_user, 'role', None)
            if role != UserRole.ADMIN:
                effective = await get_user_effective_permissions(int(current_user.id), db)
                if any_of:
                    ok = any(p in effective for p in permissions)
                else:
                    ok = all(p in effective for p in permissions)
                if not ok:
                    needed = " or ".join(permissions) if any_of else ", ".join(permissions)
                    raise HTTPException(status_code=403, detail=f"Missing permission: {needed}")
            return await func(*args, current_user=current_user, db=db, **kwargs)

        return _wrapped

    return _outer


__all__ = [
    'require_permissions',
    'with_permissions',
]
