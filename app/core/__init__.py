"""
Core package initialization.
"""
from .config import Constants, Currency, Environment, UserRole, settings
from .dependencies import (
    get_current_active_user,
    get_current_user,
    get_db,
    get_pagination_params,
    require_permission,
    require_role,
)
from .security import (
    JWTManager,
    PasswordManager,
    PasswordValidator,
    PermissionManager,
    SecurityUtils,
)

__all__ = [
    "settings",
    "Constants", 
    "UserRole",
    "Currency",
    "Environment",
    "get_db",
    "get_current_user",
    "get_current_active_user",
    "require_role",
    "require_permission", 
    "get_pagination_params",
    "PasswordManager",
    "JWTManager",
    "PermissionManager",
    "PasswordValidator",
    "SecurityUtils"
]
