"""
Sales Pydantic schemas for request/response validation.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import Field, field_validator

from app.core.base_schema import ApiBaseModel


class SaleStatus(str, Enum):
    """Sale status enumeration."""
    COMPLETED = "COMPLETED"
    PENDING = "PENDING"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"

class PaymentMethod(str, Enum):
    """Payment method enumeration."""
    CASH = "CASH"
    CARD = "CARD"
    MOBILE_PAYMENT = "MOBILE_PAYMENT"
    BANK_TRANSFER = "BANK_TRANSFER"

class PaymentCreateSchema(ApiBaseModel):
    """Schema for creating a payment line for a sale."""
    accountId: int | None = Field(None, description="Account ID to credit", alias="account_id")
    amount: Decimal = Field(..., ge=0, description="Payment amount")
    currency: str | None = Field("USD", description="Currency code")
    reference: str | None = Field(None, description="External reference/txn id")
    model_config = {"populate_by_name": True}

# Sale item schemas
class SaleItemBaseSchema(ApiBaseModel):
    """Base schema for sale item data.
    Accepts either stock_id (preferred) or product_id. One must be provided.
    """
    stockId: int | None = Field(None, description="Stock ID", alias="stock_id")
    productId: int | None = Field(None, description="Product ID", alias="product_id")
    quantity: int = Field(..., gt=0, description="Quantity sold")
    price: Decimal = Field(..., ge=0, description="Unit price at time of sale")
    subtotal: Decimal = Field(..., ge=0, description="Subtotal amount")

    model_config = {"populate_by_name": True}

class SaleItemCreateSchema(SaleItemBaseSchema):
    """Schema for creating sale items."""
    pass

class SaleItemResponseSchema(SaleItemBaseSchema):
    """Schema for sale item response data."""
    id: int = Field(..., description="Sale item ID")
    sale_id: int = Field(..., description="Sale ID")
    product_name: str = Field(..., description="Product name")
    product_sku: str = Field(..., description="Product SKU")
    subtotal: Decimal = Field(..., description="Subtotal (quantity * unit_price - discount)")
    
    class Config:
        from_attributes = True

# Sale schemas
class SaleBaseSchema(ApiBaseModel):
    """Base schema for sale data.
    payment_type (alias paymentType) historically accepted values like CASH/CARD but
    now supports logical settlement types used by POS (FULL, PARTIAL, UNPAID, SPLIT).
    We treat SPLIT as FULL for storage while keeping original for downstream logic.
    """
    branchId: int | None = Field(None, alias="branch_id")
    totalAmount: Decimal = Field(..., alias="total_amount")
    discount: Decimal = Field(Decimal('0'), ge=0, description="Discount amount")
    paymentType: str | None = Field(None, description="Payment type (FULL, PARTIAL, UNPAID, SPLIT)", alias="payment_type")
    customerId: int | None = Field(None, alias="customer_id")
    userId: int | None = Field(None, alias="user_id")

    model_config = {"populate_by_name": True}

    @field_validator("paymentType", mode="before")
    @classmethod
    def normalize_payment_type(cls, v):
        if v is None:
            return None
        # Accept common legacy variants
        if isinstance(v, str):
            up = v.strip().upper()
            mapping = {
                "SPLIT": "FULL",  # treat split allocation as fully paid at creation; individual lines captured via payments
                "PAID": "FULL",
            }
            return mapping.get(up, up)
        return v

class SaleCreateSchema(SaleBaseSchema):
    """Schema for creating a new sale.
    All monetary fields can be recomputed server-side; we accept partial payloads.
    """
    branchId: int | None = Field(None, alias="branch_id")
    totalAmount: Decimal | None = Field(None, alias="total_amount")
    customerId: int | None = Field(None, alias="customer_id")
    userId: int | None = Field(None, alias="user_id")
    items: list[SaleItemCreateSchema] = Field(..., min_length=1, description="Sale items")
    payment: PaymentCreateSchema | None = Field(None, description="Single payment line")
    payments: list[PaymentCreateSchema] | None = Field(None, description="Multiple payment lines")
    customer_name: str | None = Field(None, max_length=100, description="Customer full name (pay later)")
    customer_email: str | None = Field(None, max_length=120, description="Customer email (pay later)")
    customer_phone: str | None = Field(None, max_length=30, description="Customer phone (pay later)")

    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        if not v:
            raise ValueError('Sale must have at least one item')
        for item in v:
            stock_id = getattr(item, 'stock_id', None) or getattr(item, 'stockId', None)
            product_id = getattr(item, 'product_id', None) or getattr(item, 'productId', None)
            if stock_id is None and product_id is None:
                raise ValueError('Each item must include stock_id or product_id')
        keys = [
            (getattr(item, 'stock_id', None) or getattr(item, 'stockId', None) or f"p:{getattr(item, 'product_id', None) or getattr(item, 'productId', None)}")
            for item in v
        ]
        if len(keys) != len(set(keys)):
            raise ValueError('Duplicate sale items detected')
        return v

class SaleUpdateSchema(ApiBaseModel):
    """Schema for updating sale data."""
    customer_name: str | None = Field(None, max_length=100)
    customer_email: str | None = Field(None, max_length=100)
    customer_phone: str | None = Field(None, max_length=20)
    discount_amount: Decimal | None = Field(None, ge=0)
    tax_amount: Decimal | None = Field(None, ge=0)
    notes: str | None = Field(None, max_length=500)
    status: SaleStatus | None = Field(None)

class SaleResponseSchema(ApiBaseModel):
    """Simplified schema matching actual response construction in service/routes."""
    id: int
    branch_id: int = Field(..., alias="branchId")
    branch_name: str | None = None
    total_amount: Decimal
    discount: Decimal
    payment_type: str | None = Field(None, alias="paymentType")
    customer_id: int | None = Field(None, alias="customerId")
    customer_name: str | None = None
    cashier_id: int = Field(..., alias="cashierId")
    cashier_name: str | None = None
    items_count: int
    status: SaleStatus
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    # Computed financial fields (not persisted directly)
    paid_amount: Decimal | None = Field(None, description="Sum of associated payments")
    outstanding_amount: Decimal | None = Field(None, description="Remaining receivable (total - paid)")

    model_config = {"populate_by_name": True}

class SaleDetailResponseSchema(SaleResponseSchema):
    """Schema for detailed sale response with items."""
    items: list[SaleItemResponseSchema] = Field(..., description="Sale items")
    items_count: int = Field(..., description="Number of items")
    total_quantity: int = Field(..., description="Total quantity of all items")
    payments: list[dict[str, Any]] | None = Field(default=None, description="Associated payments")

class SaleListResponseSchema(ApiBaseModel):
    """Schema for paginated sale list response."""
    sales: list[SaleResponseSchema] = Field(..., description="List of sales")
    total: int = Field(..., description="Total number of sales")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    total_amount: Decimal = Field(Decimal('0'), description="Total amount of all sales")

# Refund schemas
class RefundItemSchema(ApiBaseModel):
    """Schema for refund item data."""
    sale_item_id: int = Field(..., description="Sale item ID to refund")
    quantity: int = Field(..., gt=0, description="Quantity to refund")
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        """Validate refund quantity."""
        if v <= 0:
            raise ValueError('Refund quantity must be greater than 0')
        return v

class RefundCreateSchema(ApiBaseModel):
    """Schema for creating a refund."""
    sale_id: int = Field(..., description="Sale ID to refund")
    items: list[RefundItemSchema] = Field(..., min_length=1, description="Items to refund")
    reason: str = Field(..., min_length=1, max_length=255, description="Refund reason")
    notes: str | None = Field(None, max_length=500, description="Refund notes")

class RefundResponseSchema(ApiBaseModel):
    """Schema for refund response data."""
    id: int = Field(..., description="Refund ID")
    original_sale_id: int = Field(..., description="Original sale ID")
    branch_name: str = Field(..., description="Branch name")
    total_refund_amount: Decimal = Field(..., description="Total refund amount")
    reason: str | None = Field(None, description="Refund reason")
    items: list[dict[str, Any]] = Field(..., description="Refunded items")
    created_at: datetime = Field(..., description="Refund timestamp")
    
    class Config:
        from_attributes = True

class RefundListResponseSchema(ApiBaseModel):
    """Schema for paginated refund list response."""
    items: list[RefundResponseSchema] = Field(..., description="List of refunds")
    total: int = Field(..., description="Total number of refunds")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    
    class Config:
        from_attributes = True

# Statistics schemas
class SalesStatsSchema(ApiBaseModel):
    """Schema for sales statistics."""
    total_sales: int = Field(..., description="Total number of sales")
    total_revenue: float = Field(..., description="Total revenue")
    total_discount: float = Field(..., description="Total discount given")
    average_sale_value: float = Field(..., description="Average sale amount")
    payment_method_breakdown: dict[str, dict[str, Any]] = Field(..., description="Payment method breakdown")

class DailySalesSchema(ApiBaseModel):
    """Schema for daily sales summary."""
    date: datetime = Field(..., description="Sales date")
    total_sales: int = Field(..., description="Total sales count")
    total_revenue: Decimal = Field(..., description="Total revenue")
    total_items: int = Field(..., description="Total items sold")

class SalesReportSchema(ApiBaseModel):
    """Schema for sales report."""
    period_start: datetime = Field(..., description="Report period start")
    period_end: datetime = Field(..., description="Report period end")
    total_sales: int = Field(..., description="Total sales in period")
    total_revenue: Decimal = Field(..., description="Total revenue in period")
    daily_breakdown: list[DailySalesSchema] = Field(..., description="Daily sales breakdown")
    top_products: list[dict[str, Any]] = Field(..., description="Top selling products")
    payment_method_breakdown: dict[str, Decimal] = Field(..., description="Revenue by payment method")

# Receipt schemas
class ReceiptSchema(ApiBaseModel):
    """Schema for sale receipt."""
    sale: SaleDetailResponseSchema = Field(..., description="Sale details")
    company_info: dict[str, str] = Field(..., description="Company information")
    receipt_number: str = Field(..., description="Receipt number")
    qr_code: str | None = Field(None, description="QR code data")
    
class ReceiptPrintSchema(ApiBaseModel):
    """Schema for receipt printing request."""
    sale_id: int = Field(..., description="Sale ID to print")
    format: str = Field("thermal", description="Receipt format (thermal, a4, etc.)")
    email: str | None = Field(None, description="Email to send receipt")
