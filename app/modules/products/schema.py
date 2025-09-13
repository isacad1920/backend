"""
Product and Category Pydantic schemas for request/response validation.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from app.core.base_schema import ApiBaseModel
from enum import Enum

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
    description: Optional[str] = Field(None, max_length=255, description="Category description")

class CategoryCreateSchema(CategoryBaseSchema):
    """Schema for creating a new category."""
    pass

class CategoryUpdateSchema(ApiBaseModel):
    """Schema for updating category data."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)

class CategoryResponseSchema(CategoryBaseSchema):
    """Schema for category response data."""
    id: int = Field(..., description="Category ID")
    status: Optional[str] = Field(None, description="Category status")
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
    description: Optional[str] = Field(None, max_length=500, description="Product description")
    sku: str = Field(..., min_length=1, max_length=50, description="Stock Keeping Unit")
    barcode: Optional[str] = Field(None, max_length=50, description="Product barcode")
    categoryId: Optional[int] = Field(None, description="Category ID")
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
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    sku: Optional[str] = Field(None, min_length=1, max_length=50)
    barcode: Optional[str] = Field(None, max_length=50)
    categoryId: Optional[int] = Field(None)
    # Accept legacy input keys via validation_alias
    costPrice: Optional[Decimal] = Field(None, ge=0, validation_alias='cost')
    sellingPrice: Optional[Decimal] = Field(None, ge=0, validation_alias='price')
    status: Optional[ProductStatus] = Field(None)
    
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
    categoryName: Optional[str] = Field(None, description="Category name")
    
    class Config:
        from_attributes = True

class ProductDetailResponseSchema(ProductResponseSchema):
    """Schema for detailed product response with additional info."""
    totalSales: Decimal = Field(Decimal('0'), description="Total sales amount")
    totalSold: int = Field(0, description="Total quantity sold")
    lastSaleDate: Optional[datetime] = Field(None, description="Last sale date")
    lastStockUpdate: Optional[datetime] = Field(None, description="Last stock update date")
    createdByName: Optional[str] = Field(None, description="Creator name")

class ProductListResponseSchema(ApiBaseModel):
    """Schema for paginated product list response."""
    items: List[ProductResponseSchema] = Field(..., description="List of products")
    total: int = Field(..., description="Total number of products")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Page size")

# Stock management schemas
class StockAdjustmentSchema(ApiBaseModel):
    """Schema for stock adjustment."""
    product_id: int = Field(..., description="Product ID")
    quantity_change: int = Field(..., description="Quantity change (positive for increase, negative for decrease)")
    reason: str = Field(..., min_length=1, max_length=255, description="Reason for adjustment")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")

class BulkStockAdjustmentSchema(ApiBaseModel):
    """Schema for bulk stock adjustments."""
    adjustments: List[StockAdjustmentSchema] = Field(..., min_length=1, description="List of stock adjustments")

class StockResponseSchema(ApiBaseModel):
    """Schema for stock movement response."""
    id: int = Field(..., description="Movement ID")
    product_id: int = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    movement_type: str = Field(..., description="Movement type")
    quantity: int = Field(..., description="Quantity moved")
    reason: str = Field(..., description="Movement reason")
    notes: Optional[str] = Field(None, description="Movement notes")
    created_at: datetime = Field(..., description="Movement timestamp")
    created_by_id: Optional[int] = Field(None, description="User who made the movement")
    created_by_name: Optional[str] = Field(None, description="User name")

# Statistics schemas
class ProductStatsSchema(ApiBaseModel):
    """Schema for product statistics."""
    totalProducts: int = Field(..., description="Total number of products")
    categoriesCount: int = Field(..., description="Number of categories")
    productsByCategory: Dict[str, int] = Field(..., description="Products count by category")

class CategoryStatsSchema(ApiBaseModel):
    """Schema for category statistics."""
    total_categories: int = Field(..., description="Total number of categories")
    categories_with_products: int = Field(..., description="Categories with products")
    top_categories: List[Dict[str, Any]] = Field(..., description="Top categories by product count")

# Bulk operations schemas
class BulkProductUpdateSchema(ApiBaseModel):
    """Schema for bulk product updates."""
    product_ids: List[int] = Field(..., min_length=1, description="List of product IDs")
    updates: ProductUpdateSchema = Field(..., description="Updates to apply")

class BulkOperationResponseSchema(ApiBaseModel):
    """Schema for bulk operation response."""
    success_count: int = Field(..., description="Number of successful operations")
    error_count: int = Field(..., description="Number of failed operations")
    errors: List[str] = Field(default_factory=list, description="Error messages")
