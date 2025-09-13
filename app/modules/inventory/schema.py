"""
Inventory management schemas and data models.
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import ConfigDict, Field

from app.core.base_schema import ApiBaseModel


class StockStatus(str, Enum):
    """Stock status enumeration."""
    IN_STOCK = "IN_STOCK"
    LOW_STOCK = "LOW_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    OVERSTOCK = "OVERSTOCK"

class AdjustmentType(str, Enum):
    """Stock adjustment types."""
    INCREASE = "INCREASE"
    DECREASE = "DECREASE"
    RECOUNT = "RECOUNT"
    DAMAGED = "DAMAGED"
    EXPIRED = "EXPIRED"
    THEFT = "THEFT"
    RETURNED = "RETURNED"

class AdjustmentReason(str, Enum):
    """Reasons for stock adjustments."""
    PHYSICAL_COUNT = "physical_count"
    DAMAGE = "damage"
    EXPIRY = "expiry"
    THEFT = "theft"
    SUPPLIER_RETURN = "supplier_return"
    CUSTOMER_RETURN = "customer_return"
    CORRECTION = "correction"
    OTHER = "other"

# Base Schemas
class StockLevelSchema(ApiBaseModel):
    """Complete stock level information schema matching test expectations."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(..., description="Stock record ID")
    product_id: int = Field(..., alias="productId", description="Product ID")
    product_name: str = Field(..., description="Product name")
    product_sku: str | None = Field(default=None, description="Product SKU")
    category_name: str | None = Field(default=None, description="Product category")
    current_quantity: int = Field(..., ge=0, description="Current stock quantity")
    reserved_quantity: int = Field(default=0, ge=0, description="Reserved quantity")
    available_quantity: int = Field(..., ge=0, description="Available quantity")
    reorder_level: int = Field(default=10, ge=0, description="Reorder point threshold")
    unit_cost: Decimal = Field(..., ge=0, description="Unit cost price")
    unit_price: Decimal = Field(..., ge=0, description="Unit selling price")
    stock_status: StockStatus = Field(..., description="Current stock status")
    days_of_stock: int | None = Field(default=None, description="Estimated days of stock remaining")
    last_restocked: datetime | None = Field(default=None, description="Last restock date")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record last update timestamp")

class StockAdjustmentCreateSchema(ApiBaseModel):
    """Schema for creating stock adjustments."""
    product_id: int = Field(..., description="Product ID to adjust")
    adjustment_type: AdjustmentType = Field(..., description="Type of adjustment")
    quantity: int = Field(..., gt=0, description="Quantity to adjust")
    reason: str = Field(..., description="Reason for adjustment")
    notes: str | None = Field(default=None, max_length=500, description="Additional notes")
    reference_number: str | None = Field(default=None, max_length=100, description="Reference number")

class StockAdjustmentSchema(ApiBaseModel):
    """Schema for stock adjustment information."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Adjustment record ID")
    product_id: int = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    adjustment_type: AdjustmentType = Field(..., description="Type of adjustment")
    quantity_before: int = Field(..., description="Quantity before adjustment")
    quantity_after: int = Field(..., description="Quantity after adjustment")
    adjustment_quantity: int = Field(..., description="Adjustment quantity")
    reason: AdjustmentReason = Field(..., description="Reason for adjustment")
    notes: str | None = Field(default=None, description="Additional notes")
    reference_number: str | None = Field(default=None, description="Reference number")
    created_by: int = Field(..., description="User who made the adjustment")
    created_at: datetime = Field(..., description="Adjustment timestamp")

class LowStockAlertSchema(ApiBaseModel):
    """Schema for low stock alerts."""
    model_config = ConfigDict(from_attributes=True)
    
    product_id: int = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    product_sku: str = Field(..., description="Product SKU")
    current_quantity: int = Field(..., description="Current stock quantity")
    reorder_level: int = Field(..., description="Reorder point threshold")
    suggested_order_quantity: int = Field(..., description="Suggested order quantity")
    days_out_of_stock: int | None = Field(default=None, description="Estimated days until out of stock")
    last_sale_date: datetime | None = Field(default=None, description="Last sale date")
    average_daily_sales: Decimal | None = Field(default=None, description="Average daily sales")

class InventoryValuationSchema(ApiBaseModel):
    """Schema for inventory valuation information."""
    product_id: int = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    product_sku: str = Field(..., description="Product SKU")
    quantity: int = Field(..., description="Current stock quantity")
    unit_cost: Decimal = Field(..., description="Unit cost price")
    unit_price: Decimal = Field(..., description="Unit selling price")
    total_cost_value: Decimal = Field(..., description="Total inventory cost value")
    total_retail_value: Decimal = Field(..., description="Total inventory retail value")
    potential_profit: Decimal = Field(..., description="Potential profit")
    profit_margin_percent: Decimal = Field(..., description="Profit margin percentage")

class InventoryReportSchema(ApiBaseModel):
    """Schema for comprehensive inventory report."""
    report_date: datetime = Field(..., description="Report generation date")
    total_products: int = Field(..., description="Total number of products")
    total_stock_items: int = Field(..., description="Total stock items")
    total_inventory_cost: Decimal = Field(..., description="Total inventory cost value")
    total_inventory_retail: Decimal = Field(..., description="Total inventory retail value")
    low_stock_items: int = Field(..., description="Number of low stock items")
    out_of_stock_items: int = Field(..., description="Number of out of stock items")
    overstock_items: int = Field(..., description="Number of overstock items")
    stock_levels: list[StockLevelSchema] = Field(..., description="Detailed stock levels")
    low_stock_alerts: list[LowStockAlertSchema] = Field(..., description="Low stock alerts")

class DeadStockAnalysisSchema(ApiBaseModel):
    """Schema for dead stock analysis."""
    product_id: int = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    product_sku: str = Field(..., description="Product SKU")
    quantity: int = Field(..., description="Current stock quantity")
    last_sale_date: datetime | None = Field(default=None, description="Last sale date")
    days_since_last_sale: int | None = Field(default=None, description="Days since last sale")
    total_cost_value: Decimal = Field(..., description="Total cost value tied up")
    suggested_action: str = Field(..., description="Suggested action for dead stock")
    priority_level: str = Field(..., description="Priority level for action")

class ReorderPointSchema(ApiBaseModel):
    """Schema for reorder point calculations."""
    product_id: int = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    current_reorder_level: int = Field(..., description="Current reorder level")
    suggested_reorder_level: int = Field(..., description="Suggested reorder level")
    average_daily_demand: Decimal = Field(..., description="Average daily demand")
    lead_time_days: int = Field(..., description="Lead time in days")
    safety_stock: int = Field(..., description="Safety stock quantity")
    max_stock_level: int = Field(..., description="Maximum stock level")

class InventoryMovementSchema(ApiBaseModel):
    """Schema for inventory movement tracking."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Movement record ID")
    product_id: int = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    movement_type: str = Field(..., description="Type of movement (sale, adjustment, transfer)")
    quantity: int = Field(..., description="Quantity moved")
    reference_id: int | None = Field(default=None, description="Reference transaction ID")
    notes: str | None = Field(default=None, description="Movement notes")
    created_at: datetime = Field(..., description="Movement timestamp")

class StockMovementSchema(ApiBaseModel):
    """Schema for stock movement tracking."""
    id: int
    product_id: int
    product_name: str
    product_sku: str
    movement_type: str  # SALE, ADJUSTMENT, TRANSFER, RECEIPT
    quantity: int
    unit_cost: Decimal | None = None
    reference_number: str | None = None
    description: str | None = None
    created_at: datetime
    created_by: int | None = None
    running_balance: int

class InventoryTurnoverSchema(ApiBaseModel):
    """Schema for inventory turnover analysis."""
    product_id: int = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    average_inventory: Decimal = Field(..., description="Average inventory level")
    cost_of_goods_sold: Decimal = Field(..., description="Cost of goods sold")
    turnover_ratio: Decimal = Field(..., description="Inventory turnover ratio")
    days_to_sell: Decimal = Field(..., description="Average days to sell inventory")
    turnover_category: str = Field(..., description="Turnover performance category")

# Response Schemas
class InventoryDashboardSchema(ApiBaseModel):
    """Schema for inventory dashboard data."""
    summary: dict[str, Any] = Field(..., description="Inventory summary statistics")
    low_stock_alerts: list[LowStockAlertSchema] = Field(..., description="Current low stock alerts")
    recent_adjustments: list[StockAdjustmentSchema] = Field(..., description="Recent stock adjustments")
    top_selling_products: list[dict[str, Any]] = Field(..., description="Top selling products")
    dead_stock_items: list[DeadStockAnalysisSchema] = Field(..., description="Dead stock analysis")
    inventory_trends: dict[str, Any] = Field(..., description="Inventory trend data")

class BulkStockUpdateSchema(ApiBaseModel):
    """Schema for bulk stock updates."""
    updates: list[dict[str, Any]] = Field(..., description="List of stock updates")
    reason: AdjustmentReason = Field(..., description="Reason for bulk update")
    notes: str | None = Field(default=None, description="Bulk update notes")

# Export/Import Schemas
class InventoryExportSchema(ApiBaseModel):
    """Schema for inventory data export."""
    format: str = Field(default="csv", description="Export format (csv, excel, pdf)")
    include_valuation: bool = Field(default=True, description="Include valuation data")
    include_movements: bool = Field(default=False, description="Include movement history")
    date_from: date | None = Field(default=None, description="Start date for data")
    date_to: date | None = Field(default=None, description="End date for data")
    product_ids: list[int] | None = Field(default=None, description="Specific product IDs")

class InventoryImportSchema(ApiBaseModel):
    """Schema for inventory data import."""
    file_path: str = Field(..., description="Path to import file")
    import_type: str = Field(..., description="Type of import (stock_levels, adjustments)")
    validate_only: bool = Field(default=True, description="Validate only without importing")
    overwrite_existing: bool = Field(default=False, description="Overwrite existing records")
