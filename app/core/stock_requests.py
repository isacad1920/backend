"""
Stock request management with real-time notifications.
"""
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from app.core.notifications import (
    Notification,
    NotificationPriority,
    NotificationType,
    connection_manager,
)

logger = logging.getLogger(__name__)


class StockRequestStatus(str, Enum):
    """Stock request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SHIPPED = "shipped"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class StockRequestPriority(str, Enum):
    """Stock request priority."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class StockRequestItem:
    """Individual item in stock request."""
    
    def __init__(self, product_id: str, product_name: str, requested_quantity: int,
                 current_stock: int, reason: str = ""):
        self.product_id = product_id
        self.product_name = product_name
        self.requested_quantity = requested_quantity
        self.current_stock = current_stock
        self.reason = reason
        self.approved_quantity: int | None = None


class StockRequest:
    """Stock request from cashier/branch to inventory."""
    
    def __init__(self, requester_id: int, requester_name: str, branch_id: str,
                 branch_name: str, priority: StockRequestPriority = StockRequestPriority.NORMAL):
        self.id = str(uuid.uuid4())
        self.requester_id = requester_id
        self.requester_name = requester_name
        self.branch_id = branch_id
        self.branch_name = branch_name
        self.priority = priority
        self.status = StockRequestStatus.PENDING
        self.items: list[StockRequestItem] = []
        self.notes = ""
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.approved_by: int | None = None
        self.approved_at: datetime | None = None
        self.shipped_at: datetime | None = None
        self.received_at: datetime | None = None
        self.tracking_number: str | None = None
    
    def add_item(self, product_id: str, product_name: str, quantity: int,
                current_stock: int, reason: str = ""):
        """Add item to stock request."""
        item = StockRequestItem(product_id, product_name, quantity, current_stock, reason)
        self.items.append(item)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "requester_id": self.requester_id,
            "requester_name": self.requester_name,
            "branch_id": self.branch_id,
            "branch_name": self.branch_name,
            "priority": self.priority.value,
            "status": self.status.value,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "shipped_at": self.shipped_at.isoformat() if self.shipped_at else None,
            "received_at": self.received_at.isoformat() if self.received_at else None,
            "tracking_number": self.tracking_number,
            "items": [
                {
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "requested_quantity": item.requested_quantity,
                    "approved_quantity": item.approved_quantity,
                    "current_stock": item.current_stock,
                    "reason": item.reason
                }
                for item in self.items
            ],
            "total_items": len(self.items),
            "total_quantity": sum(item.requested_quantity for item in self.items)
        }


class StockRequestService:
    """Service for managing stock requests with real-time notifications."""
    
    def __init__(self):
        self.requests: dict[str, StockRequest] = {}
    
    async def create_request(self, requester_id: int, requester_name: str,
                           branch_id: str, branch_name: str,
                           items: list[dict[str, Any]], 
                           priority: StockRequestPriority = StockRequestPriority.NORMAL,
                           notes: str = "") -> str:
        """Create new stock request and notify inventory clerks."""
        
        # Create request
        request = StockRequest(requester_id, requester_name, branch_id, branch_name, priority)
        request.notes = notes
        
        # Add items
        for item_data in items:
            request.add_item(
                product_id=item_data["product_id"],
                product_name=item_data["product_name"],
                quantity=item_data["quantity"],
                current_stock=item_data.get("current_stock", 0),
                reason=item_data.get("reason", "")
            )
        
        # Store request
        self.requests[request.id] = request
        
        # Create notification for inventory clerks
        notification = Notification(
            id=str(uuid.uuid4()),
            type=NotificationType.STOCK_REQUEST,
            title=f"New Stock Request from {branch_name}",
            message=f"{requester_name} requested {len(items)} items with {priority.value} priority",
            data={
                "request_id": request.id,
                "requester": requester_name,
                "branch": branch_name,
                "priority": priority.value,
                "item_count": len(items),
                "total_quantity": sum(item["quantity"] for item in items)
            },
            priority=NotificationPriority.HIGH if priority == StockRequestPriority.URGENT else NotificationPriority.MEDIUM,
            recipient_roles=["INVENTORY_CLERK", "MANAGER", "ADMIN"]
        )
        
        # Send notification
        await connection_manager.send_notification(notification)
        
        logger.info(f"Stock request created: {request.id} by {requester_name}")
        return request.id
    
    async def approve_request(self, request_id: str, approver_id: int, approver_name: str,
                            approved_items: dict[str, int]) -> bool:
        """Approve stock request and notify requester."""
        
        if request_id not in self.requests:
            return False
        
        request = self.requests[request_id]
        request.status = StockRequestStatus.APPROVED
        request.approved_by = approver_id
        request.approved_at = datetime.utcnow()
        request.updated_at = datetime.utcnow()
        
        # Update approved quantities
        for item in request.items:
            if item.product_id in approved_items:
                item.approved_quantity = approved_items[item.product_id]
        
        # Notify requester
        notification = Notification(
            id=str(uuid.uuid4()),
            type=NotificationType.STOCK_APPROVED,
            title="Stock Request Approved",
            message=f"Your stock request has been approved by {approver_name}",
            data={
                "request_id": request_id,
                "approver": approver_name,
                "approved_items": len(approved_items),
                "estimated_shipping": "1-2 business days"
            },
            priority=NotificationPriority.MEDIUM,
            recipient_users=[request.requester_id]
        )
        
        await connection_manager.send_notification(notification)
        
        logger.info(f"Stock request approved: {request_id} by {approver_name}")
        return True
    
    async def ship_request(self, request_id: str, shipper_id: int, shipper_name: str,
                          tracking_number: str) -> bool:
        """Mark request as shipped and notify branch."""
        
        if request_id not in self.requests:
            return False
        
        request = self.requests[request_id]
        request.status = StockRequestStatus.SHIPPED
        request.shipped_at = datetime.utcnow()
        request.updated_at = datetime.utcnow()
        request.tracking_number = tracking_number
        
        # Notify requester and branch staff
        notification = Notification(
            id=str(uuid.uuid4()),
            type=NotificationType.STOCK_SHIPPED,
            title="Stock Request Shipped",
            message=f"Your stock order has been shipped by {shipper_name}",
            data={
                "request_id": request_id,
                "tracking_number": tracking_number,
                "shipper": shipper_name,
                "estimated_delivery": "1-2 business days"
            },
            priority=NotificationPriority.MEDIUM,
            recipient_users=[request.requester_id],
            branch_id=request.branch_id
        )
        
        await connection_manager.send_notification(notification)
        
        logger.info(f"Stock request shipped: {request_id} with tracking {tracking_number}")
        return True
    
    async def receive_request(self, request_id: str, receiver_id: int, receiver_name: str,
                            received_items: dict[str, int]) -> bool:
        """Mark request as received and update inventory."""
        
        if request_id not in self.requests:
            return False
        
        request = self.requests[request_id]
        request.status = StockRequestStatus.RECEIVED
        request.received_at = datetime.utcnow()
        request.updated_at = datetime.utcnow()
        
        # Notify inventory team about completion
        notification = Notification(
            id=str(uuid.uuid4()),
            type=NotificationType.STOCK_RECEIVED,
            title="Stock Request Completed",
            message=f"Stock delivery received at {request.branch_name} by {receiver_name}",
            data={
                "request_id": request_id,
                "receiver": receiver_name,
                "branch": request.branch_name,
                "received_items": len(received_items),
                "completion_time": datetime.utcnow().isoformat()
            },
            priority=NotificationPriority.LOW,
            recipient_roles=["INVENTORY_CLERK", "MANAGER"]
        )
        
        await connection_manager.send_notification(notification)
        
        logger.info(f"Stock request received: {request_id} at {request.branch_name}")
        return True
    
    async def reject_request(self, request_id: str, rejector_id: int, rejector_name: str,
                           reason: str) -> bool:
        """Reject stock request and notify requester."""
        
        if request_id not in self.requests:
            return False
        
        request = self.requests[request_id]
        request.status = StockRequestStatus.REJECTED
        request.updated_at = datetime.utcnow()
        request.notes += f"\n\nRejected by {rejector_name}: {reason}"
        
        # Notify requester
        notification = Notification(
            id=str(uuid.uuid4()),
            type=NotificationType.STOCK_REJECTED,
            title="Stock Request Rejected",
            message=f"Your stock request was rejected by {rejector_name}",
            data={
                "request_id": request_id,
                "rejector": rejector_name,
                "reason": reason
            },
            priority=NotificationPriority.MEDIUM,
            recipient_users=[request.requester_id]
        )
        
        await connection_manager.send_notification(notification)
        
        logger.info(f"Stock request rejected: {request_id} by {rejector_name}")
        return True
    
    def get_request(self, request_id: str) -> StockRequest | None:
        """Get stock request by ID."""
        return self.requests.get(request_id)
    
    def get_requests_by_status(self, status: StockRequestStatus) -> list[StockRequest]:
        """Get all requests with specific status."""
        return [req for req in self.requests.values() if req.status == status]
    
    def get_requests_by_branch(self, branch_id: str) -> list[StockRequest]:
        """Get all requests from specific branch."""
        return [req for req in self.requests.values() if req.branch_id == branch_id]
    
    def get_requests_by_user(self, user_id: int) -> list[StockRequest]:
        """Get all requests from specific user."""
        return [req for req in self.requests.values() if req.requester_id == user_id]


# Global stock request service
stock_request_service = StockRequestService()
