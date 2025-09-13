"""
Customer management module for POS system.
"""

from app.modules.customers.model import CustomerModel
from app.modules.customers.service import CustomerService, create_customer_service
from app.modules.customers.routes import router
from app.modules.customers.schema import (
    CustomerCreateSchema,
    CustomerUpdateSchema,
    CustomerResponseSchema,
    CustomerDetailResponseSchema,
    CustomerListResponseSchema,
    CustomerStatsSchema,
    CustomerStatus,
    CustomerType,
    BulkCustomerUpdateSchema,
    BulkCustomerStatusUpdateSchema,
    BulkOperationResponseSchema,
    CustomerPurchaseHistorySchema,
    CustomerPurchaseHistoryListSchema
)

__all__ = [
    "CustomerModel",
    "CustomerService",
    "create_customer_service",
    "router",
    "CustomerCreateSchema",
    "CustomerUpdateSchema", 
    "CustomerResponseSchema",
    "CustomerDetailResponseSchema",
    "CustomerListResponseSchema",
    "CustomerStatsSchema",
    "CustomerStatus",
    "CustomerType",
    "BulkCustomerUpdateSchema",
    "BulkCustomerStatusUpdateSchema",
    "BulkOperationResponseSchema",
    "CustomerPurchaseHistorySchema",
    "CustomerPurchaseHistoryListSchema"
]
