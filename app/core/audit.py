"""
Simple and performance-optimized audit logging system for SOFinance.
"""
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.db.prisma import get_db
from generated.prisma import fields  # Import fields for proper JSON handling

logger = logging.getLogger(__name__)

class AuditAction(Enum):
    """Audit action types matching database schema."""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    TRANSFER = "TRANSFER"
    PAYMENT = "PAYMENT"
    EXPENSE = "EXPENSE"
    BACKUP = "BACKUP"
    RESTORE = "RESTORE"
    CONFIG = "CONFIG"

class AuditSeverity(Enum):
    """Audit severity levels matching database schema."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class AuditEntry:
    """Simple audit log entry."""
    action: AuditAction
    user_id: str | None
    resource_type: str
    resource_id: str | None = None
    details: dict[str, Any] | None = None
    ip_address: str | None = None
    severity: AuditSeverity = AuditSeverity.INFO

class SimpleAuditLogger:
    """Simple, performance-optimized audit logger."""
    
    async def log_action(
        self,
        action: AuditAction,
        user_id: str | None,
        resource_type: str,
        resource_id: str | None = None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
        severity: AuditSeverity = AuditSeverity.INFO
    ):
        """Log an audit action to the database."""
        try:
            db = await get_db()
            
            # Convert user_id to int if provided
            user_id_int = int(user_id) if user_id and user_id.isdigit() else None
            
            # Create audit log entry with correct schema
            await db.auditlog.create(
                data={
                    "action": action.value,
                    "userId": user_id_int,  # Note: camelCase for Prisma
                    "entityType": resource_type,
                    "entityId": resource_id,
                    "newValues": fields.Json(details) if details else None,  # Use proper JSON field
                    "severity": severity.value,
                    "ipAddress": ip_address,  # Note: camelCase for Prisma
                    "userAgent": details.get("user_agent") if details else None,
                }
            )
            
            logger.info(f"Audit log created: {action.value} by user {user_id} on {resource_type}")
            
        except Exception as e:
            # Don't let audit logging break the application
            logger.error(f"Failed to create audit log: {e}")
    
    async def get_user_actions(self, user_id: str, limit: int = 100):
        """Get recent actions by a user."""
        try:
            db = await get_db()
            
            # Convert user_id to int
            user_id_int = int(user_id) if user_id.isdigit() else None
            if not user_id_int:
                return []
            
            logs = await db.auditlog.find_many(
                where={"userId": user_id_int},  # Note: camelCase for Prisma
                order_by={"createdAt": "desc"},  # Note: camelCase for Prisma
                take=limit
            )
            
            return [
                {
                    "action": log.action,
                    "severity": log.severity,
                    "entityType": log.entityType,
                    "entityId": log.entityId,
                    "newValues": log.newValues if log.newValues else {},
                    "oldValues": log.oldValues if log.oldValues else {},
                    "ipAddress": log.ipAddress,
                    "created_at": log.createdAt
                }
                for log in logs
            ]
            
        except Exception as e:
            logger.error(f"Failed to retrieve user actions: {e}")
            return []

# Global audit logger instance
_audit_logger = None

def get_audit_logger() -> SimpleAuditLogger:
    """Get the global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = SimpleAuditLogger()
    return _audit_logger
