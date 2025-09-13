"""
Customer Pydantic schemas for request/response validation.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import AliasChoices, EmailStr, Field, field_validator, model_validator

from app.core.base_schema import ApiBaseModel


class CustomerType(str, Enum):
    """Customer type enumeration."""
    INDIVIDUAL = "INDIVIDUAL"
    COMPANY = "COMPANY"

class CustomerStatus(str, Enum):
    """Customer status enumeration."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BLACKLISTED = "BLACKLISTED"

# Base customer schemas
class CustomerBaseSchema(ApiBaseModel):
    """Base schema for customer data."""
    name: str = Field(..., min_length=1, max_length=255, description="Customer name")
    email: EmailStr | None = Field(None, description="Customer email address")
    phone: str | None = Field(None, max_length=20, description="Customer phone number")
    address: str | None = Field(None, max_length=500, description="Customer address")
    # accept legacy alias customer_type
    type: CustomerType = Field(
        CustomerType.INDIVIDUAL,
        description="Customer type",
        validation_alias=AliasChoices("customer_type", "type"),
    )
    credit_limit: Decimal | None = Field(
        Decimal('0'), ge=0, description="Credit limit",
        validation_alias=AliasChoices("credit_limit", "creditLimit")
    )
    balance: Decimal = Field(Decimal('0'), description="Current balance")
    total_purchases: Decimal = Field(
        Decimal('0'), description="Total purchases",
        validation_alias=AliasChoices("total_purchases", "totalPurchases")
    )
    status: CustomerStatus = Field(CustomerStatus.ACTIVE, description="Customer status")
    notes: str | None = Field(None, max_length=1000, description="Additional notes")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format."""
        if v is not None and v.strip():
            # Remove common phone number characters
            cleaned = ''.join(char for char in v if char.isdigit() or char in ['+', '-', '(', ')', ' '])
            if len(cleaned.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')) < 10:
                raise ValueError('Phone number must be at least 10 digits')
        return v
    
    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

class CustomerCreateSchema(CustomerBaseSchema):
    """Schema for creating new customers with legacy field support."""
    # accept legacy first/last name inputs
    first_name: str | None = Field(default=None, validation_alias=AliasChoices("firstName", "first_name"))
    last_name: str | None = Field(default=None, validation_alias=AliasChoices("lastName", "last_name"))

    @model_validator(mode="before")
    @classmethod
    def build_name_from_parts(cls, values):
        # If name missing but first/last provided, compose it
        if isinstance(values, dict):
            name = values.get("name")
            if not name:
                first = values.get("firstName") or values.get("first_name") or values.get("first_name") or values.get("first_name")
                last = values.get("lastName") or values.get("last_name")
                if first or last:
                    values["name"] = (f"{first or ''} {last or ''}").strip() or "Customer"
        return values

class CustomerUpdateSchema(ApiBaseModel):
    """Schema for updating customer information."""
    name: str | None = Field(None, min_length=1, max_length=255, description="Customer name")
    email: EmailStr | None = Field(None, description="Customer email address")
    phone: str | None = Field(None, max_length=20, description="Customer phone number")
    address: str | None = Field(None, max_length=500, description="Customer address")
    type: CustomerType | None = Field(None, description="Customer type")
    credit_limit: Decimal | None = Field(None, ge=0, description="Credit limit")
    status: CustomerStatus | None = Field(None, description="Customer status")
    notes: str | None = Field(None, max_length=1000, description="Additional notes")
    # legacy fields
    first_name: str | None = Field(default=None, validation_alias=AliasChoices("firstName", "first_name"))
    last_name: str | None = Field(default=None, validation_alias=AliasChoices("lastName", "last_name"))
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format."""
        if v is not None and v.strip():
            cleaned = ''.join(char for char in v if char.isdigit() or char in ['+', '-', '(', ')', ' '])
            if len(cleaned.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')) < 10:
                raise ValueError('Phone number must be at least 10 digits')
        return v

    @model_validator(mode="before")
    @classmethod
    def merge_name_from_legacy(cls, values):
        if isinstance(values, dict):
            # Only compose if name not explicitly provided
            name = values.get("name")
            if not name:
                first = values.get("firstName") or values.get("first_name")
                last = values.get("lastName") or values.get("last_name")
                if first or last:
                    values["name"] = (f"{first or ''} {last or ''}").strip()
        return values

class CustomerResponseSchema(CustomerBaseSchema):
    """Schema for customer response data."""
    id: int = Field(..., description="Customer ID")
    status: CustomerStatus = Field(..., description="Customer status")
    balance: Decimal = Field(..., description="Current account balance")
    total_purchases: Decimal = Field(Decimal('0'), description="Total purchase amount")
    last_purchase_date: datetime | None = Field(None, description="Last purchase date")
    created_at: datetime = Field(..., description="Customer creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True

class CustomerDetailResponseSchema(CustomerResponseSchema):
    """Schema for detailed customer response with purchase history."""
    purchase_count: int = Field(0, description="Total number of purchases")
    average_purchase: Decimal = Field(Decimal('0'), description="Average purchase amount")
    last_30_days_purchases: Decimal = Field(Decimal('0'), description="Purchases in last 30 days")
    
    class Config:
        from_attributes = True

class CustomerListResponseSchema(ApiBaseModel):
    """Schema for paginated customer list response."""
    items: list[CustomerResponseSchema] = Field(..., description="List of customers")
    total: int = Field(..., description="Total number of customers")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    
    class Config:
        from_attributes = True

class CustomerStatsSchema(ApiBaseModel):
    """Schema for customer statistics."""
    total_customers: int = Field(..., description="Total number of customers")
    active_customers: int = Field(..., description="Number of active customers")
    inactive_customers: int = Field(..., description="Number of inactive customers")
    business_customers: int = Field(..., description="Number of business customers")
    individual_customers: int = Field(..., description="Number of individual customers")
    customers_with_credit: int = Field(..., description="Number of customers with credit limits")
    total_customer_balance: Decimal = Field(..., description="Total customer balance")
    average_purchase_per_customer: Decimal = Field(..., description="Average purchase amount per customer")
    top_customers: list[dict[str, Any]] = Field(..., description="Top customers by purchase amount")
    
    class Config:
        from_attributes = True

class BulkCustomerUpdateSchema(ApiBaseModel):
    """Schema for bulk customer updates."""
    customer_ids: list[int] = Field(..., min_length=1, description="List of customer IDs to update")
    # accept test payload key `update_data`
    update_data: CustomerUpdateSchema = Field(..., description="Updates to apply", alias="update_data")
    
    @field_validator('customer_ids')
    @classmethod
    def validate_customer_ids(cls, v):
        """Validate customer IDs list."""
        if len(v) > 100:
            raise ValueError('Cannot update more than 100 customers at once')
        return v
    
    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

class BulkCustomerStatusUpdateSchema(ApiBaseModel):
    """Schema for bulk customer status updates."""
    customer_ids: list[int] = Field(..., min_length=1, description="List of customer IDs")
    status: CustomerStatus = Field(..., description="New status for all customers")
    
    @field_validator('customer_ids')
    @classmethod
    def validate_customer_ids(cls, v):
        """Validate customer IDs list."""
        if len(v) > 100:
            raise ValueError('Cannot update more than 100 customers at once')
        return v

class BulkOperationResponseSchema(ApiBaseModel):
    """Schema for bulk operation response."""
    success_count: int = Field(..., description="Number of successful operations")
    failure_count: int = Field(..., description="Number of failed operations")
    total_count: int = Field(..., description="Total number of operations attempted")
    errors: list[dict[str, str]] = Field([], description="List of errors encountered")
    
    class Config:
        from_attributes = True

class CustomerPurchaseHistorySchema(ApiBaseModel):
    """Schema for customer purchase history."""
    sale_id: int = Field(..., description="Sale ID")
    total_amount: Decimal = Field(..., description="Total purchase amount")
    items_count: int = Field(..., description="Number of items purchased")
    purchase_date: datetime = Field(..., description="Purchase date")
    branch_name: str = Field(..., description="Branch name")
    
    class Config:
        from_attributes = True

class CustomerPurchaseHistoryListSchema(ApiBaseModel):
    """Schema for paginated customer purchase history."""
    items: list[CustomerPurchaseHistorySchema] = Field(..., description="List of purchases")
    total: int = Field(..., description="Total number of purchases")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    
    class Config:
        from_attributes = True
