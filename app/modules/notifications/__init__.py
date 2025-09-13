"""
Notifications module for real-time WebSocket notifications.
"""

from app.modules.notifications.routes import router
from app.modules.notifications.schema import ConnectedUserSchema, NotificationSchema
from app.modules.notifications.service import NotificationService

__all__ = [
    "router",
    "NotificationService", 
    "NotificationSchema",
    "ConnectedUserSchema"
]
