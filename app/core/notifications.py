"""
Real-time notification system for inventory management.
"""
from typing import Dict, List, Set, Any
from datetime import datetime
from fastapi import WebSocket
from enum import Enum
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    """Types of notifications."""
    STOCK_REQUEST = "stock_request"
    STOCK_APPROVED = "stock_approved"
    STOCK_REJECTED = "stock_rejected"
    STOCK_SHIPPED = "stock_shipped"
    STOCK_RECEIVED = "stock_received"
    LOW_STOCK_ALERT = "low_stock_alert"
    INVENTORY_UPDATE = "inventory_update"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification:
    """Notification data model."""
    
    def __init__(
        self,
        id: str,
        type: NotificationType,
        title: str,
        message: str,
        data: Dict[str, Any],
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        recipient_roles: List[str] = None,
        recipient_users: List[int] = None,
        branch_id: str = None
    ):
        self.id = id
        self.type = type
        self.title = title
        self.message = message
        self.data = data
        self.priority = priority
        self.recipient_roles = recipient_roles or []
        self.recipient_users = recipient_users or []
        self.branch_id = branch_id
        self.timestamp = datetime.utcnow().isoformat()
        self.read_by: Set[int] = set()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert notification to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "message": self.message,
            "data": self.data,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "read": False  # Will be set per user
        }


class ConnectionManager:
    """Manages WebSocket connections for real-time notifications."""
    
    def __init__(self):
        # Active connections: {user_id: {connection_id: websocket}}
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}
        
        # User metadata: {user_id: {role, branch_id, username}}
        self.user_metadata: Dict[int, Dict[str, str]] = {}
        
        # Notification history
        self.notifications: Dict[str, Notification] = {}

        # Per-connection send locks to avoid concurrent writes
        # Structure: {user_id: {connection_id: asyncio.Lock}}
        self._send_locks = {}
        # Heartbeat control
        self._heartbeat_tasks = {}
        
    async def connect(self, websocket: WebSocket, user_id: int, connection_id: str, 
                     role: str, branch_id: str, username: str):
        """Accept new WebSocket connection."""
        await websocket.accept()
        
        # Add connection
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
        self.active_connections[user_id][connection_id] = websocket
        # Init send lock for this connection
        if user_id not in self._send_locks:
            self._send_locks[user_id] = {}
        self._send_locks[user_id][connection_id] = asyncio.Lock()
        
        # Store user metadata
        self.user_metadata[user_id] = {
            "role": role,
            "branch_id": branch_id,
            "username": username
        }
        
        logger.info(f"User {username} (ID: {user_id}) connected with role {role}")
        # Note: Avoid sending an immediate message on connect to prevent race conditions
        # with client receive loops or proxies. Clients can infer readiness from the
        # successful WebSocket upgrade.
        # Start a non-blocking heartbeat to keep proxies/load balancers happy
        key = f"{user_id}:{connection_id}"
        async def _heartbeat():
            try:
                while True:
                    await asyncio.sleep(25)
                    if user_id not in self.active_connections or connection_id not in self.active_connections[user_id]:
                        break
                    try:
                        await self.try_send_to_connection(user_id, connection_id, {"type": "ping", "ts": datetime.utcnow().isoformat()})
                    except Exception:
                        break
            except asyncio.CancelledError:
                pass
        self._heartbeat_tasks[key] = asyncio.create_task(_heartbeat())
    
    def disconnect(self, user_id: int, connection_id: str):
        """Remove WebSocket connection."""
        if user_id in self.active_connections:
            if connection_id in self.active_connections[user_id]:
                del self.active_connections[user_id][connection_id]
            
            # Remove user if no more connections
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                if user_id in self.user_metadata:
                    username = self.user_metadata[user_id].get("username", str(user_id))
                    logger.info(f"User {username} (ID: {user_id}) disconnected")
                    del self.user_metadata[user_id]
        # Clean up send lock
        if user_id in self._send_locks and connection_id in self._send_locks[user_id]:
            del self._send_locks[user_id][connection_id]
            if not self._send_locks[user_id]:
                del self._send_locks[user_id]
        # Stop heartbeat
        key = f"{user_id}:{connection_id}"
        task = self._heartbeat_tasks.pop(key, None)
        if task:
            try:
                task.cancel()
            except Exception:
                pass
    
    async def _safe_send(self, websocket: WebSocket, lock: asyncio.Lock, payload: Dict[str, Any]):
        """Safely send a message over a websocket using a per-connection lock."""
        async with lock:
            await websocket.send_text(json.dumps(payload))

    async def try_send_to_connection(self, user_id: int, connection_id: str, message: Dict[str, Any]):
        """Send a message to a specific connection for a user, guarding with a lock."""
        try:
            websocket = self.active_connections[user_id][connection_id]
            lock = self._send_locks[user_id][connection_id]
        except Exception:
            return
        try:
            await self._safe_send(websocket, lock, message)
        except Exception as e:
            logger.debug(f"WebSocket send failed for user {user_id} conn {connection_id}: {e}")
            # Treat as disconnected connection
            self.disconnect(user_id, connection_id)

    async def send_personal_message(self, user_id: int, message: Dict[str, Any]):
        """Send message to specific user's all connections."""
        if user_id in self.active_connections:
            disconnected_connections = []
            
            for connection_id, websocket in self.active_connections[user_id].items():
                try:
                    lock = self._send_locks.get(user_id, {}).get(connection_id)
                    if lock is None:
                        # Initialize a lock if missing for any reason
                        self._send_locks.setdefault(user_id, {})[connection_id] = asyncio.Lock()
                        lock = self._send_locks[user_id][connection_id]
                    await self._safe_send(websocket, lock, message)
                except Exception as e:
                    logger.debug(f"Failed to send message to user {user_id} on conn {connection_id}: {e}")
                    disconnected_connections.append(connection_id)
            
            # Clean up disconnected connections
            for conn_id in disconnected_connections:
                self.disconnect(user_id, conn_id)
    
    async def broadcast_to_role(self, role: str, message: Dict[str, Any], 
                               branch_id: str = None):
        """Broadcast message to all users with specific role."""
        for user_id, metadata in self.user_metadata.items():
            if metadata["role"] == role:
                # Check branch filter if specified
                if branch_id and metadata.get("branch_id") != branch_id:
                    continue
                await self.send_personal_message(user_id, message)
    
    async def broadcast_to_users(self, user_ids: List[int], message: Dict[str, Any]):
        """Broadcast message to specific users."""
        for user_id in user_ids:
            await self.send_personal_message(user_id, message)
    
    async def send_notification(self, notification: Notification):
        """Send notification to appropriate recipients."""
        message = notification.to_dict()
        
        # Store notification
        self.notifications[notification.id] = notification
        
        # Send to specific users
        if notification.recipient_users:
            await self.broadcast_to_users(notification.recipient_users, message)
        
        # Send to users with specific roles
        if notification.recipient_roles:
            for role in notification.recipient_roles:
                await self.broadcast_to_role(role, message, notification.branch_id)
        
        logger.info(f"Notification sent: {notification.title} (ID: {notification.id})")
    
    def get_connected_users(self) -> Dict[int, Dict[str, str]]:
        """Get list of currently connected users."""
        return self.user_metadata.copy()
    
    def get_user_notifications(self, user_id: int, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get notifications for a specific user."""
        user_meta = self.user_metadata.get(user_id, {})
        user_role = user_meta.get("role")
        user_branch = user_meta.get("branch_id")
        
        notifications = []
        for notification in self.notifications.values():
            # Check if user should receive this notification
            should_receive = False
            
            if user_id in notification.recipient_users:
                should_receive = True
            elif user_role and user_role in notification.recipient_roles:
                if not notification.branch_id or notification.branch_id == user_branch:
                    should_receive = True
            
            if should_receive:
                notif_data = notification.to_dict()
                notif_data["read"] = user_id in notification.read_by
                
                if unread_only and notif_data["read"]:
                    continue
                
                notifications.append(notif_data)
        
        # Sort by timestamp (newest first)
        return sorted(notifications, key=lambda x: x["timestamp"], reverse=True)
    
    def mark_notification_read(self, user_id: int, notification_id: str):
        """Mark notification as read by user."""
        if notification_id in self.notifications:
            self.notifications[notification_id].read_by.add(user_id)


# Global connection manager instance
connection_manager = ConnectionManager()
