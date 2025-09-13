"""
System module for managing system information, configuration, and backups.
"""

from app.modules.system.routes import router
from app.modules.system.backup_routes import backup_router
from app.modules.system.service import SystemService
from app.modules.system.backup_service import BackupService
from app.modules.system.schema import (
    SystemInfoSchema,
    SystemInfoUpdateSchema,
    SystemInfoResponseSchema,
    BackupSchema,
    BackupResponseSchema,
    BackupType,
    BackupStatus
)

__all__ = [
    "router",
    "SystemService",
    "BackupService",
    "SystemInfoSchema",
    "SystemInfoUpdateSchema", 
    "SystemInfoResponseSchema",
    "BackupSchema",
    "BackupResponseSchema",
    "BackupType",
    "BackupStatus",
    "backup_router"
]
