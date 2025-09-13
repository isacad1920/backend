"""
Inventory Management Module

This module provides comprehensive inventory management capabilities including:
- Real-time stock level monitoring
- Low stock alerts and notifications
- Inventory valuation and reporting
- Stock adjustment workflows
- Dead stock analysis
- Reorder point management
- Inventory turnover analytics
"""

from .routes import router
from .service import InventoryService, create_inventory_service
from .schema import (
    StockLevelSchema,
    InventoryReportSchema,
    StockAdjustmentSchema,
    LowStockAlertSchema,
    InventoryValuationSchema,
    DeadStockAnalysisSchema,
    ReorderPointSchema
)

__all__ = [
    "router",
    "InventoryService",
    "create_inventory_service",
    "StockLevelSchema",
    "InventoryReportSchema", 
    "StockAdjustmentSchema",
    "LowStockAlertSchema",
    "InventoryValuationSchema",
    "DeadStockAnalysisSchema",
    "ReorderPointSchema"
]
