"""
Financial management Pydantic schemas for POS system.
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from app.core.base_schema import ApiBaseModel
from enum import Enum

class ReportType(str, Enum):
    """Financial report type enumeration."""
    INCOME_STATEMENT = "INCOME_STATEMENT"
    BALANCE_SHEET = "BALANCE_SHEET"
    CASH_FLOW = "CASH_FLOW"
    SALES_SUMMARY = "SALES_SUMMARY"
    INVENTORY_REPORT = "INVENTORY_REPORT"
    CUSTOMER_REPORT = "CUSTOMER_REPORT"
    TAX_REPORT = "TAX_REPORT"
    PROFIT_LOSS = "PROFIT_LOSS"

class ReportPeriod(str, Enum):
    """Report period enumeration."""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"
    CUSTOM = "CUSTOM"

class TransactionCategory(str, Enum):
    """Transaction category enumeration."""
    SALES_REVENUE = "SALES_REVENUE"
    PRODUCT_COST = "PRODUCT_COST"
    OPERATING_EXPENSE = "OPERATING_EXPENSE"
    MARKETING_EXPENSE = "MARKETING_EXPENSE"
    ADMINISTRATIVE_EXPENSE = "ADMINISTRATIVE_EXPENSE"
    TAXES = "TAXES"
    INTEREST = "INTEREST"
    OTHER_INCOME = "OTHER_INCOME"
    OTHER_EXPENSE = "OTHER_EXPENSE"

# Financial summary schemas
class FinancialSummarySchema(ApiBaseModel):
    """Schema for financial summary data."""
    total_revenue: Decimal = Field(..., description="Total revenue")
    total_expenses: Decimal = Field(..., description="Total expenses")
    gross_profit: Decimal = Field(..., description="Gross profit")
    net_profit: Decimal = Field(..., description="Net profit")
    profit_margin: Decimal = Field(..., description="Profit margin percentage")
    total_sales_count: int = Field(..., description="Total number of sales")
    average_sale_value: Decimal = Field(..., description="Average sale value")
    
    class Config:
        from_attributes = True

class SalesAnalyticsSchema(ApiBaseModel):
    """Schema for sales analytics data."""
    daily_sales: List[Dict[str, Any]] = Field(..., description="Daily sales data")
    monthly_sales: List[Dict[str, Any]] = Field(..., description="Monthly sales data")
    top_products: List[Dict[str, Any]] = Field(..., description="Top selling products")
    sales_by_category: List[Dict[str, Any]] = Field(..., description="Sales by product category")
    sales_by_branch: List[Dict[str, Any]] = Field(..., description="Sales by branch")
    sales_trends: Dict[str, Any] = Field(..., description="Sales trend analysis")
    
    class Config:
        from_attributes = True

class InventoryAnalyticsSchema(ApiBaseModel):
    """Schema for inventory analytics data."""
    total_inventory_value: Decimal = Field(..., description="Total inventory value")
    low_stock_items: List[Dict[str, Any]] = Field(..., description="Low stock items")
    out_of_stock_items: List[Dict[str, Any]] = Field(..., description="Out of stock items")
    inventory_turnover: Decimal = Field(..., description="Inventory turnover ratio")
    dead_stock_items: List[Dict[str, Any]] = Field(..., description="Dead stock items")
    inventory_by_category: List[Dict[str, Any]] = Field(..., description="Inventory by category")
    
    class Config:
        from_attributes = True

class CustomerAnalyticsSchema(ApiBaseModel):
    """Schema for customer analytics data."""
    total_customers: int = Field(..., description="Total number of customers")
    new_customers_this_month: int = Field(..., description="New customers this month")
    customer_acquisition_rate: Decimal = Field(..., description="Customer acquisition rate")
    customer_retention_rate: Decimal = Field(..., description="Customer retention rate")
    average_customer_value: Decimal = Field(..., description="Average customer lifetime value")
    top_customers: List[Dict[str, Any]] = Field(..., description="Top customers by purchase value")
    customer_segments: List[Dict[str, Any]] = Field(..., description="Customer segmentation data")
    
    class Config:
        from_attributes = True

class FinancialRatiosSchema(ApiBaseModel):
    """Schema for financial ratios."""
    gross_profit_margin: Decimal = Field(..., description="Gross profit margin")
    net_profit_margin: Decimal = Field(..., description="Net profit margin")
    return_on_investment: Decimal = Field(..., description="Return on investment")
    inventory_turnover_ratio: Decimal = Field(..., description="Inventory turnover ratio")
    current_ratio: Decimal = Field(..., description="Current ratio")
    quick_ratio: Decimal = Field(..., description="Quick ratio")
    debt_to_equity_ratio: Decimal = Field(..., description="Debt to equity ratio")
    
    class Config:
        from_attributes = True

# Report request schemas
class FinancialReportRequestSchema(ApiBaseModel):
    """Schema for financial report requests."""
    report_type: ReportType = Field(..., description="Type of report to generate")
    period: ReportPeriod = Field(ReportPeriod.MONTHLY, description="Report period")
    start_date: Optional[date] = Field(None, description="Start date for custom period")
    end_date: Optional[date] = Field(None, description="End date for custom period")
    branch_id: Optional[int] = Field(None, description="Specific branch ID for branch reports")
    include_details: bool = Field(False, description="Include detailed breakdown")
    
    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        """Validate end date is after start date."""
        if v is not None and info.data.get('start_date') is not None:
            if v < info.data['start_date']:
                raise ValueError('End date must be after start date')
        return v

class IncomeStatementSchema(ApiBaseModel):
    """Schema for income statement data."""
    period_start: date = Field(..., description="Period start date")
    period_end: date = Field(..., description="Period end date")
    revenue: Dict[str, Decimal] = Field(..., description="Revenue breakdown")
    cost_of_goods_sold: Dict[str, Decimal] = Field(..., description="COGS breakdown")
    gross_profit: Decimal = Field(..., description="Gross profit")
    operating_expenses: Dict[str, Decimal] = Field(..., description="Operating expenses breakdown")
    operating_income: Decimal = Field(..., description="Operating income")
    other_income: Dict[str, Decimal] = Field(..., description="Other income sources")
    other_expenses: Dict[str, Decimal] = Field(..., description="Other expenses")
    net_income: Decimal = Field(..., description="Net income")
    
    class Config:
        from_attributes = True

class BalanceSheetSchema(ApiBaseModel):
    """Schema for balance sheet data."""
    as_of_date: date = Field(..., description="Balance sheet date")
    assets: Dict[str, Any] = Field(..., description="Assets breakdown")
    liabilities: Dict[str, Any] = Field(..., description="Liabilities breakdown")
    equity: Dict[str, Any] = Field(..., description="Equity breakdown")
    total_assets: Decimal = Field(..., description="Total assets")
    total_liabilities: Decimal = Field(..., description="Total liabilities")
    total_equity: Decimal = Field(..., description="Total equity")
    
    class Config:
        from_attributes = True

class CashFlowStatementSchema(ApiBaseModel):
    """Schema for cash flow statement data."""
    period_start: date = Field(..., description="Period start date")
    period_end: date = Field(..., description="Period end date")
    operating_activities: Dict[str, Decimal] = Field(..., description="Operating activities cash flow")
    investing_activities: Dict[str, Decimal] = Field(..., description="Investing activities cash flow")
    financing_activities: Dict[str, Decimal] = Field(..., description="Financing activities cash flow")
    net_cash_flow: Decimal = Field(..., description="Net cash flow")
    beginning_cash: Decimal = Field(..., description="Beginning cash balance")
    ending_cash: Decimal = Field(..., description="Ending cash balance")
    
    class Config:
        from_attributes = True

class TaxReportSchema(ApiBaseModel):
    """Schema for tax report data."""
    period_start: date = Field(..., description="Period start date")
    period_end: date = Field(..., description="Period end date")
    taxable_sales: Decimal = Field(..., description="Total taxable sales")
    tax_collected: Decimal = Field(..., description="Total tax collected")
    tax_exempt_sales: Decimal = Field(..., description="Tax exempt sales")
    tax_rate: Decimal = Field(..., description="Average tax rate")
    sales_by_tax_rate: List[Dict[str, Any]] = Field(..., description="Sales breakdown by tax rate")
    
    class Config:
        from_attributes = True

class BudgetComparisonSchema(ApiBaseModel):
    """Schema for budget vs actual comparison."""
    period_start: date = Field(..., description="Period start date")
    period_end: date = Field(..., description="Period end date")
    budget_items: List[Dict[str, Any]] = Field(..., description="Budget vs actual items")
    total_budgeted: Decimal = Field(..., description="Total budgeted amount")
    total_actual: Decimal = Field(..., description="Total actual amount")
    variance: Decimal = Field(..., description="Total variance")
    variance_percentage: Decimal = Field(..., description="Variance percentage")
    
    class Config:
        from_attributes = True

class ProfitLossAnalysisSchema(ApiBaseModel):
    """Schema for profit and loss analysis."""
    period_start: date = Field(..., description="Period start date")
    period_end: date = Field(..., description="Period end date")
    revenue_analysis: Dict[str, Any] = Field(..., description="Revenue analysis")
    cost_analysis: Dict[str, Any] = Field(..., description="Cost analysis")
    expense_analysis: Dict[str, Any] = Field(..., description="Expense analysis")
    profitability_ratios: Dict[str, Decimal] = Field(..., description="Profitability ratios")
    period_comparison: Dict[str, Any] = Field(..., description="Comparison with previous periods")
    
    class Config:
        from_attributes = True

# Dashboard schemas
class DashboardSummarySchema(ApiBaseModel):
    """Schema for dashboard summary data."""
    today_sales: Decimal = Field(..., description="Today's sales")
    monthly_sales: Decimal = Field(..., description="This month's sales")
    yearly_sales: Decimal = Field(..., description="This year's sales")
    total_customers: int = Field(..., description="Total customers")
    active_products: int = Field(..., description="Active products count")
    low_stock_alerts: int = Field(..., description="Low stock alerts count")
    pending_orders: int = Field(..., description="Pending orders count")
    cash_on_hand: Decimal = Field(..., description="Current cash on hand")
    
    class Config:
        from_attributes = True

class PerformanceMetricsSchema(ApiBaseModel):
    """Schema for performance metrics."""
    sales_growth: Decimal = Field(..., description="Sales growth rate")
    customer_growth: Decimal = Field(..., description="Customer growth rate")
    inventory_turnover: Decimal = Field(..., description="Inventory turnover rate")
    profit_margin: Decimal = Field(..., description="Current profit margin")
    customer_acquisition_cost: Decimal = Field(..., description="Customer acquisition cost")
    customer_lifetime_value: Decimal = Field(..., description="Customer lifetime value")
    
    class Config:
        from_attributes = True

class AlertSchema(ApiBaseModel):
    """Schema for financial alerts."""
    id: str = Field(..., description="Alert ID")
    type: str = Field(..., description="Alert type")
    priority: str = Field(..., description="Alert priority")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional alert data")
    created_at: datetime = Field(..., description="Alert creation time")
    
    class Config:
        from_attributes = True

class FinancialAlertsSchema(ApiBaseModel):
    """Schema for financial alerts summary."""
    alerts: List[AlertSchema] = Field(..., description="List of active alerts")
    total_alerts: int = Field(..., description="Total number of alerts")
    high_priority_count: int = Field(..., description="High priority alerts count")
    medium_priority_count: int = Field(..., description="Medium priority alerts count")
    low_priority_count: int = Field(..., description="Low priority alerts count")
    
    class Config:
        from_attributes = True
