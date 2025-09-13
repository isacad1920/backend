"""
Financial analytics and reporting module for POS system.
"""

from app.modules.financial.routes import router
from app.modules.financial.schema import (
    AlertSchema,
    BalanceSheetSchema,
    BudgetComparisonSchema,
    CashFlowStatementSchema,
    CustomerAnalyticsSchema,
    DashboardSummarySchema,
    FinancialAlertsSchema,
    FinancialRatiosSchema,
    FinancialSummarySchema,
    IncomeStatementSchema,
    InventoryAnalyticsSchema,
    PerformanceMetricsSchema,
    ProfitLossAnalysisSchema,
    ReportPeriod,
    ReportType,
    SalesAnalyticsSchema,
    TaxReportSchema,
    TransactionCategory,
)
from app.modules.financial.service import FinancialService, create_financial_service
from app.modules.financial.utils import (
    DataAggregationUtils,
    DateUtils,
    ErrorHandler,
    NumberUtils,
    ValidationUtils,
    format_financial_amount,
    safe_decimal_sum,
    validate_financial_permission,
)

__all__ = [
    # Core Services
    "FinancialService",
    "create_financial_service",
    
    # Router
    "router",
    
    # Utilities
    "DateUtils",
    "NumberUtils",
    "ValidationUtils",
    "DataAggregationUtils",
    "ErrorHandler",
    "validate_financial_permission",
    "safe_decimal_sum",
    "format_financial_amount",
    
    # Schemas
    "FinancialSummarySchema",
    "SalesAnalyticsSchema",
    "InventoryAnalyticsSchema",
    "CustomerAnalyticsSchema",
    "FinancialRatiosSchema",
    "IncomeStatementSchema",
    "BalanceSheetSchema",
    "CashFlowStatementSchema",
    "TaxReportSchema",
    "BudgetComparisonSchema",
    "ProfitLossAnalysisSchema",
    "DashboardSummarySchema",
    "PerformanceMetricsSchema",
    "FinancialAlertsSchema",
    "AlertSchema",
    "ReportType",
    "ReportPeriod",
    "TransactionCategory"
]
