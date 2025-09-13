"""
Notifications module service layer.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.notifications import connection_manager
from app.db.prisma import Prisma
from app.modules.notifications.schema import NotificationSchema

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing notifications with DB persistence and realtime push."""

    def __init__(self, db: Optional[Prisma] = None):
        self.db = db

    async def get_user_notifications(self, user_id: int, unread_only: bool = False, limit: int = 50, cursor: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get notifications for a user with stable ordering and optional cursor (createdAt based).

        Cursor format: ISO timestamp or notification ID convertible to int for DB ordering. Falls back to createdAt.
        """
        results: List[Dict[str, Any]] = []

        # 1) Fetch from DB (best-effort)
        if self.db and hasattr(self.db, "notification"):
            try:
                where = {"userId": user_id}
                if unread_only:
                    where["read"] = False
                query_args: Dict[str, Any] = {
                    "where": where,
                    "order": {"createdAt": "desc"},
                    "take": limit,
                }
                if cursor:
                    try:
                        # Attempt to treat cursor as ID to anchor pagination
                        cid = int(cursor)
                        # Need the createdAt of cursor row to emulate createdAt cursor pagination
                        cur_row = await self.db.notification.find_unique(where={"id": cid})
                        if cur_row:
                            query_args["skip"] = 1
                            query_args["cursor"] = {"id": cid}
                    except Exception:
                        # If not numeric, ignore
                        pass
                items = await self.db.notification.find_many(**query_args)
                for it in items:
                    dto = NotificationSchema.from_orm_any(it)
                    results.append(dto.dump_snake())
            except Exception as e:
                logger.error(f"DB error getting notifications for user {user_id}: {e}")

        # 2) Merge with in-memory (for live session notifications not persisted yet)
        mem = connection_manager.get_user_notifications(user_id, unread_only)
        existing_ids = {str(r.get("id")) for r in results}

        def parse_iso_datetime(value: Any) -> Optional[datetime]:
            if isinstance(value, datetime):
                return value
            if isinstance(value, str) and value:
                try:
                    # datetime.fromisoformat supports the format used by our code
                    return datetime.fromisoformat(value.replace("Z", "+00:00"))
                except Exception:
                    return None
            return None

        for m in mem:
            # Normalize in-memory payload to schema shape
            mid = str(m.get("id", ""))
            if mid in existing_ids:
                continue
            created_dt = parse_iso_datetime(m.get("created_at") or m.get("timestamp")) or datetime.utcnow()
            try:
                dto = NotificationSchema(
                    id=mid,
                    type=str(m.get("type", "info")),
                    title=m.get("title", "Notification"),
                    message=m.get("message", ""),
                    userId=user_id,
                    read=bool(m.get("read", False)),
                    createdAt=created_dt,
                )
                results.append(dto.dump_snake())
                existing_ids.add(mid)
            except Exception as e:
                # Last-resort: include raw dict but ensure minimal required fields
                normalized = {
                    "id": mid,
                    "type": str(m.get("type", "info")),
                    "title": m.get("title", "Notification"),
                    "message": m.get("message", ""),
                    "user_id": user_id,
                    "read": bool(m.get("read", False)),
                    "created_at": created_dt,
                }
                results.append(normalized)
                existing_ids.add(mid)

        # 3) Sort robustly by created_at/timestamp (newest first)
        def sort_key(x: Dict[str, Any]) -> float:
            dt = parse_iso_datetime(x.get("created_at") or x.get("timestamp") or x.get("createdAt"))
            try:
                return dt.timestamp() if dt else 0.0
            except Exception:
                return 0.0

        results.sort(key=sort_key, reverse=True)
        return results[:limit]

    async def mark_notification_read(self, user_id: int, notification_id: str) -> bool:
        """Mark a notification as read in both memory and DB."""
        try:
            # Try DB update if numeric id
            if self.db and hasattr(self.db, "notification"):
                if notification_id.isdigit():
                    try:
                        updated = await self.db.notification.update(
                            where={"id": int(notification_id)},
                            data={"read": True},
                        )
                        if updated:
                            return True
                    except Exception:
                        # ignore and fallback
                        pass
                else:
                    # Try string-based ID as fallback (e.g., UUID)
                    try:
                        updated = await self.db.notification.update(
                            where={"id": notification_id},
                            data={"read": True},
                        )
                        if updated:
                            return True
                    except Exception:
                        # ignore and fallback
                        pass
            # Fallback to in-memory
            connection_manager.mark_notification_read(user_id, notification_id)
            return True
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False

    async def send_notification(self, user_id: int, notification: Dict[str, Any]) -> bool:
        """Send a notification to a user and persist in DB if available."""
        try:
            # Persist to DB
            notif_id: Optional[int] = None
            created_at_iso: Optional[str] = None
            if self.db and hasattr(self.db, "notification"):
                try:
                    created = await self.db.notification.create(
                        data={
                            "userId": user_id,
                            "type": str(notification.get("type", "info")),
                            "title": notification.get("title", "Notification"),
                            "message": notification.get("message", ""),
                            "data": notification.get("data"),
                        }
                    )
                    notif_id = created.id
                    created_at_iso = getattr(created, "createdAt").isoformat() if getattr(created, "createdAt", None) else None
                except Exception:
                    notif_id = None

            # Push realtime message (snake_case on the wire)
            payload = {
                "id": str(notif_id) if notif_id is not None else str(notification.get("id", "")),
                "type": notification.get("type", "info"),
                "title": notification.get("title", "Notification"),
                "message": notification.get("message", ""),
                "user_id": user_id,
                "read": False,
                "created_at": created_at_iso or datetime.utcnow().isoformat(),
            }
            if notification.get("data") is not None:
                payload["data"] = notification.get("data")
            await connection_manager.send_personal_message(user_id, payload)
            return True
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False

    def get_connected_users(self) -> List[Dict[str, Any]]:
        """Get list of connected users from in-memory manager."""
        try:
            users = connection_manager.get_connected_users()
            # Convert dict to list
            return [
                {
                    "user_id": uid,
                    **meta,
                }
                for uid, meta in users.items()
            ]
        except Exception as e:
            logger.error(f"Error getting connected users: {e}")
            return []
