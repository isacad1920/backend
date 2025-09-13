"""
System module data models.

This module contains the data models used by the system module for
handling system information and backup records.
"""

from generated.prisma.models import Backup, SystemInfo

# Re-export models for convenience
__all__ = [
    "SystemInfo",
    "Backup"
]


# Model type aliases for better code documentation
SystemInfoModel = SystemInfo
BackupModel = Backup
