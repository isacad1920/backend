"""Legacy PermissionService (DEPRECATED).

All functionality has moved to normalized RBAC endpoints and utilities in
`app/core/permissions.py` and `app/modules/permissions/routes.py`.

This file is retained temporarily to avoid import errors during the migration
window. Any attempt to instantiate or use the old service will raise an error.
Remove this file once all legacy references are purged.
"""

class PermissionService:  # pragma: no cover - deprecated shim
    def __init__(self, *_, **__):  # noqa: D401
        raise RuntimeError(
            "PermissionService is deprecated. Use RBAC tables & routes instead."
        )


# Backwards compatibility symbol (will raise if touched)
permission_service = PermissionService  # type: ignore
