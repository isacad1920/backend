"""
Product and Category Pydantic schemas for request/response validation.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import Field, field_validator

from app.core.base_schema import ApiBaseModel


class ProductStatus(str, Enum):
    """Product status enumeration."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DISCONTINUED = "DISCONTINUED"

class StockStatus(str, Enum):
    """Stock status enumeration."""
    IN_STOCK = "IN_STOCK"
    LOW_STOCK = "LOW_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"

# Category schemas
class CategoryBaseSchema(ApiBaseModel):
    """Base schema for category data."""
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: str | None = Field(None, max_length=255, description="Category description")

class CategoryCreateSchema(CategoryBaseSchema):
    """Schema for creating a new category."""
    pass

class CategoryUpdateSchema(ApiBaseModel):
    """Schema for updating category data."""
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=255)

class CategoryResponseSchema(CategoryBaseSchema):
    """Schema for category response data."""
    id: int = Field(..., description="Category ID")
    status: str | None = Field(None, description="Category status")
    createdAt: datetime = Field(..., description="Created timestamp")
    updatedAt: datetime = Field(..., description="Updated timestamp")
    product_count: int = Field(0, description="Number of products in category")
    
    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }

# Product schemas
class ProductBaseSchema(ApiBaseModel):
    """Base schema for product data."""
    name: str = Field(..., min_length=1, max_length=100, description="Product name")
    description: str | None = Field(None, max_length=500, description="Product description")
    sku: str = Field(..., min_length=1, max_length=50, description="Stock Keeping Unit")
    barcode: str | None = Field(None, max_length=50, description="Product barcode")
    categoryId: int | None = Field(None, description="Category ID")
    # Accept legacy input keys via validation_alias for compatibility with tests
    costPrice: Decimal = Field(..., description="Cost price", validation_alias='cost')
    sellingPrice: Decimal = Field(..., description="Selling price", validation_alias='price')
    
    @field_validator('sellingPrice')
    @classmethod
    def validate_selling_price(cls, v, info):
        """Validate that selling price is greater than cost price."""
        if 'costPrice' in info.data and v < info.data['costPrice']:
            raise ValueError('Selling price must be greater than or equal to cost price')
        return v
    
    model_config = {
        "populate_by_name": True
    }

class ProductCreateSchema(ProductBaseSchema):
    """Schema for creating a new product."""
    # Accept legacy 'stockQuantity' for initial stock
    initial_stock: int = Field(0, ge=0, description="Initial stock quantity", validation_alias='stockQuantity')

class ProductUpdateSchema(ApiBaseModel):
    """Schema for updating product data."""
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    sku: str | None = Field(None, min_length=1, max_length=50)
    barcode: str | None = Field(None, max_length=50)
    categoryId: int | None = Field(None)
    # Accept legacy input keys via validation_alias
    costPrice: Decimal | None = Field(None, ge=0, validation_alias='cost')
    sellingPrice: Decimal | None = Field(None, ge=0, validation_alias='price')
    status: ProductStatus | None = Field(None)
    
    @field_validator('sellingPrice')
    @classmethod
    def validate_selling_price(cls, v, info):
        """Validate that selling price is greater than or equal to cost price when both are provided."""
        if v is None:
            return v
        cost_price = info.data.get('costPrice')
        if cost_price is not None and v < cost_price:
            raise ValueError('Selling price must be greater than or equal to cost price')
        return v

class ProductResponseSchema(ProductBaseSchema):
    """Schema for product response data."""
    id: int = Field(..., description="Product ID")
    stockStatus: StockStatus = Field(..., description="Current stock status")
    profitMargin: Decimal = Field(..., description="Profit margin percentage")
    createdAt: datetime = Field(..., description="Creation timestamp")
    updatedAt: datetime = Field(..., description="Last update timestamp")
    categoryName: str | None = Field(None, description="Category name")
    
    class Config:
        from_attributes = True

class ProductDetailResponseSchema(ProductResponseSchema):
    """Schema for detailed product response with additional info."""
    totalSales: Decimal = Field(Decimal('0'), description="Total sales amount")
    totalSold: int = Field(0, description="Total quantity sold")
    lastSaleDate: datetime | None = Field(None, description="Last sale date")
    lastStockUpdate: datetime | None = Field(None, description="Last stock update date")
    createdByName: str | None = Field(None, description="Creator name")

class ProductListResponseSchema(ApiBaseModel):
    """Schema for paginated product list response."""
    items: list[ProductResponseSchema] = Field(..., description="List of products")
    total: int = Field(..., description="Total number of products")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Page size")

# Stock management schemas
class StockAdjustmentSchema(ApiBaseModel):
    """Schema for stock adjustment."""
    product_id: int = Field(..., description="Product ID")
    quantity_change: int = Field(..., description="Quantity change (positive for increase, negative for decrease)")
    reason: str = Field(..., min_length=1, max_length=255, description="Reason for adjustment")
    notes: str | None = Field(None, max_length=500, description="Additional notes")

class BulkStockAdjustmentSchema(ApiBaseModel):
    """Schema for bulk stock adjustments."""
    adjustments: list[StockAdjustmentSchema] = Field(..., min_length=1, description="List of stock adjustments")

class StockResponseSchema(ApiBaseModel):
    """Schema for stock movement response."""
    id: int = Field(..., description="Movement ID")
    product_id: int = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    movement_type: str = Field(..., description="Movement type")
    quantity: int = Field(..., description="Quantity moved")
    reason: str = Field(..., description="Movement reason")
    notes: str | None = Field(None, description="Movement notes")
    created_at: datetime = Field(..., description="Movement timestamp")
    created_by_id: int | None = Field(None, description="User who made the movement")
    created_by_name: str | None = Field(None, description="User name")

# Statistics schemas
class ProductStatsSchema(ApiBaseModel):
    """Schema for product statistics."""
    totalProducts: int = Field(..., description="Total number of products")
    categoriesCount: int = Field(..., description="Number of categories")
    productsByCategory: dict[str, int] = Field(..., description="Products count by category")

class CategoryStatsSchema(ApiBaseModel):
    """Schema for category statistics."""
    total_categories: int = Field(..., description="Total number of categories")
    categories_with_products: int = Field(..., description="Categories with products")
    top_categories: list[dict[str, Any]] = Field(..., description="Top categories by product count")

# Bulk operations schemas
class BulkProductUpdateSchema(ApiBaseModel):
    """Schema for bulk product updates."""
    product_ids: list[int] = Field(..., min_length=1, description="List of product IDs")
    updates: ProductUpdateSchema = Field(..., description="Updates to apply")

class BulkOperationResponseSchema(ApiBaseModel):
    """Schema for bulk operation response."""
    success_count: int = Field(..., description="Number of successful operations")
    error_count: int = Field(..., description="Number of failed operations")
    errors: list[str] = Field(default_factory=list, description="Error messages")
