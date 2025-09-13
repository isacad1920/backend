"""
Notifications module schemas.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field
from app.core.base_schema import ApiBaseModel


class NotificationSchema(ApiBaseModel):
    """Schema for notification data."""
    id: str
    type: str
    title: str
    message: str
    userId: int = Field(..., alias="user_id")
    read: bool = False
    createdAt: datetime = Field(..., alias="created_at")

    # Config inherited from ApiBaseModel


class ConnectedUserSchema(ApiBaseModel):
    """Schema for connected user information."""
    userId: int = Field(..., alias="user_id")
    username: str
    role: str
    branchId: str = Field(..., alias="branch_id")
    connectionId: str = Field(..., alias="connection_id")
    connectedAt: datetime = Field(..., alias="connected_at")

    # Config inherited from ApiBaseModel
