"""
Core package initialization.
"""
from .config import settings, Constants, UserRole, Currency, Environment
from .dependencies import (
    get_db, get_current_user, get_current_active_user,
    require_role, require_permission, get_pagination_params
)
from .security import (
    PasswordManager, JWTManager, PermissionManager,
    PasswordValidator, SecurityUtils
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
