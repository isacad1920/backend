"""Authorization helpers (roadmap item 7).

Provides dependency builders to enforce permission checks in a consistent
and declarative way, reducing repetitive role/permission logic scattered
across routes.
"""
from __future__ import annotations

from functools import wraps
from typing import Callable
from fastapi import Depends, HTTPException

from app.core.dependencies import get_current_active_user, get_db
from app.core.security import PermissionManager, UserRole


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
        results = [PermissionManager.has_permission(role, p) for p in permissions]
        allowed = any(results) if any_of else all(results)
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
                checks = [PermissionManager.has_permission(role, p) for p in permissions]
                if (any_of and not any(checks)) or (not any_of and not all(checks)):
                    needed = " or ".join(permissions) if any_of else ", ".join(permissions)
                    raise HTTPException(status_code=403, detail=f"Missing permission: {needed}")
            return await func(*args, current_user=current_user, db=db, **kwargs)

        return _wrapped

    return _outer


__all__ = [
    'require_permissions',
    'with_permissions',
]
