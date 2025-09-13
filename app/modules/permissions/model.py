"""
Permissions module data models.

This module contains the data models used by the permissions module.
"""

from generated.prisma.models import User

# Re-export models for convenience
__all__ = [
    "User"
]

# Model type aliases for better code documentation  
PermissionUser = User
