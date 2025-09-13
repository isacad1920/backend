"""
Stock request schemas for request/response validation.
"""
from pydantic import BaseModel
from app.core.base_schema import ApiBaseModel
from typing import List, Dict, Any, Optional
from app.core.stock_requests import StockRequestPriority, StockRequestStatus


class StockRequestItemSchema(ApiBaseModel):
    """Schema for stock request item."""
    product_id: str
    product_name: str
    quantity: int
    current_stock: int = 0
    reason: str = ""


class CreateStockRequestSchema(ApiBaseModel):
    """Schema for creating stock request."""
    items: List[StockRequestItemSchema]
    priority: StockRequestPriority = StockRequestPriority.NORMAL
    notes: str = ""


class ApproveStockRequestSchema(ApiBaseModel):
    """Schema for approving stock request."""
    approved_items: Dict[str, int]  # product_id -> approved_quantity
    notes: str = ""


class ShipStockRequestSchema(ApiBaseModel):
    """Schema for shipping stock request."""
    tracking_number: str
    notes: str = ""


class ReceiveStockRequestSchema(ApiBaseModel):
    """Schema for receiving stock request."""
    received_items: Dict[str, int]  # product_id -> received_quantity
    notes: str = ""


class StockRequestResponseSchema(ApiBaseModel):
    """Schema for stock request response."""
    id: str
    requester_name: str
    requester_branch: str
    status: StockRequestStatus
    priority: StockRequestPriority
    items: List[StockRequestItemSchema]
    notes: str = ""
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
