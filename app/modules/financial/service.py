"""
Financial service orchestrator.
"""
import logging
from datetime import date, timedelta
from typing import Any

from app.core.exceptions import AuthorizationError, DatabaseError, ValidationError
from app.modules.financial.schema import (
    BalanceSheetSchema,
    CashFlowStatementSchema,
    DashboardSummarySchema,
    FinancialAlertsSchema,
    FinancialSummarySchema,
    IncomeStatementSchema,
    InventoryAnalyticsSchema,
    ReportPeriod,
    SalesAnalyticsSchema,
    TaxReportSchema,
)
from app.modules.financial.services import AnalyticsService, ExportService, ReportService
from app.modules.financial.utils import (
    ErrorHandler,
    ValidationUtils,
    validate_financial_permission,
)
from generated.prisma import Prisma

logger = logging.getLogger(__name__)

class FinancialService:
    """Main financial service orchestrator."""
    
    def __init__(self, db: Prisma):
        """Initialize financial service.
        
        Args:
            db: Prisma database client
        """
        self.db = db
        self.report_service = ReportService(db)
        self.export_service = ExportService(db)
        self.analytics_service = AnalyticsService(db)
    
    # Analytics Methods (delegated to AnalyticsService)
    async def get_financial_summary(
        self, 
        start_date: date | None = None,
        end_date: date | None = None,
        branch_id: int | None = None,
        current_user: dict[str, Any] = None
    ) -> FinancialSummarySchema:
        """Get financial summary for a given period.
        
        Raises:
            AuthorizationError: If user lacks permissions
            DatabaseError: If service operation fails
        """
        try:
            # Validate permissions
            validate_financial_permission(current_user, 'read')
            ValidationUtils.validate_branch_access(current_user, branch_id)
            
            return await self.analytics_service.get_financial_summary(
                start_date, end_date, branch_id, current_user
            )
        except (AuthorizationError, ValidationError):
            raise
        except Exception as e:
            ErrorHandler.log_and_raise(
                DatabaseError,
                f"Failed to get financial summary: {str(e)}"
            )
    
    async def get_sales_analytics(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        branch_id: int | None = None,
        current_user: dict[str, Any] = None
    ) -> SalesAnalyticsSchema:
        """Get detailed sales analytics."""
        return await self.analytics_service.get_sales_analytics(
            start_date, end_date, branch_id, current_user
        )
    
    async def get_inventory_analytics(
        self,
        branch_id: int | None = None,
        current_user: dict[str, Any] = None
    ) -> InventoryAnalyticsSchema:
        """Get inventory analytics."""
        return await self.analytics_service.get_inventory_analytics(
            branch_id, current_user
        )
    
    async def get_dashboard_summary(
        self,
        current_user: dict[str, Any] = None
    ) -> DashboardSummarySchema:
        """Get dashboard summary for quick overview."""
        return await self.analytics_service.get_dashboard_summary(current_user)
    
    async def get_financial_alerts(
        self,
        current_user: dict[str, Any] = None
    ) -> FinancialAlertsSchema:
        """Get financial alerts and warnings."""
        return await self.analytics_service.get_financial_alerts(current_user)
    
    # Report Methods (delegated to ReportService)
    async def generate_income_statement(
        self,
        start_date: date,
        end_date: date,
        branch_id: int | None = None,
        current_user: dict[str, Any] = None
    ) -> IncomeStatementSchema:
        """Generate income statement for specified period."""
        return await self.report_service.generate_income_statement(
            start_date, end_date, branch_id, current_user
        )
    
    async def generate_balance_sheet(
        self,
        as_of_date: date,
        branch_id: int | None = None,
        current_user: dict[str, Any] = None
    ) -> BalanceSheetSchema:
        """Generate balance sheet as of specific date."""
        return await self.report_service.generate_balance_sheet(
            as_of_date, branch_id, current_user
        )
    
    async def generate_cash_flow_statement(
        self,
        start_date: date,
        end_date: date,
        branch_id: int | None = None,
        current_user: dict[str, Any] = None
    ) -> CashFlowStatementSchema:
        """Generate cash flow statement for specified period."""
        return await self.report_service.generate_cash_flow_statement(
            start_date, end_date, branch_id, current_user
        )
    
    async def generate_tax_report(
        self,
        start_date: date,
        end_date: date,
        branch_id: int | None = None,
        current_user: dict[str, Any] = None
    ) -> TaxReportSchema:
        """Generate tax report for specified period."""
        return await self.report_service.generate_tax_report(
            start_date, end_date, branch_id, current_user
        )
    
    # Export Methods (delegated to ExportService)
    async def export_financial_report(
        self,
        report_type: str,
        format: str,
        start_date: date | None = None,
        end_date: date | None = None,
        branch_id: int | None = None,
        current_user: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Export financial report in specified format."""
        return await self.export_service.export_financial_report(
            report_type, format, start_date, end_date, branch_id, current_user
        )
    
    # Utility method for period calculations
    def _get_period_dates(self, period: ReportPeriod) -> tuple[date, date]:
        """Get start and end dates for a report period.
        
        Args:
            period: Report period enum
            
        Returns:
            Tuple of (start_date, end_date)
        """
        today = date.today()
        
        if period == ReportPeriod.TODAY:
            return (today, today)
        elif period == ReportPeriod.THIS_WEEK:
            start_date = today - timedelta(days=today.weekday())
            return (start_date, today)
        elif period == ReportPeriod.THIS_MONTH:
            start_date = today.replace(day=1)
            return (start_date, today)
        elif period == ReportPeriod.THIS_QUARTER:
            quarter_start_month = ((today.month - 1) // 3) * 3 + 1
            start_date = today.replace(month=quarter_start_month, day=1)
            return (start_date, today)
        elif period == ReportPeriod.THIS_YEAR:
            start_date = today.replace(month=1, day=1)
            return (start_date, today)
        else:
            # Default to current month
            start_date = today.replace(day=1)
            return (start_date, today)


def create_financial_service(db: Prisma) -> FinancialService:
    """Factory function to create FinancialService instance.
    
    Args:
        db: Prisma database client
        
    Returns:
        FinancialService instance
    """
    return FinancialService(db)
