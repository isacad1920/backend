"""
Financial report generation service.
"""
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from generated.prisma import Prisma
from app.modules.financial.schema import (
    IncomeStatementSchema,
    BalanceSheetSchema,
    CashFlowStatementSchema,
    TaxReportSchema,
    ReportPeriod,
    TransactionCategory
)
from app.core.exceptions import (
    ValidationError,
    AuthorizationError,
    DatabaseError,
    ExportError
)
from app.modules.financial.utils import (
    DateUtils,
    NumberUtils,
    ValidationUtils,
    DataAggregationUtils,
    ErrorHandler,
    validate_financial_permission,
    safe_decimal_sum
)

logger = logging.getLogger(__name__)

class ReportService:
    """Service for generating financial reports."""
    
    def __init__(self, db: Prisma):
        """Initialize report service.
        
        Args:
            db: Prisma database client
        """
        self.db = db
    
    async def generate_income_statement(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        branch_id: Optional[int] = None,
        current_user: Dict[str, Any] = None
    ) -> IncomeStatementSchema:
        """Generate income statement for specified period.
        
        Args:
            start_date: Period start date
            end_date: Period end date
            branch_id: Optional branch filter
            current_user: Current authenticated user
            
        Returns:
            Income statement data
            
        Raises:
            AuthorizationError: If user lacks permissions
            ValidationError: If invalid date range
            ExportError: If report generation fails
        """
        try:
            # Validate permissions
            validate_financial_permission(current_user, 'read')
            ValidationUtils.validate_branch_access(current_user, branch_id)
            
            # Validate and normalize dates
            start_date, end_date = DateUtils.validate_date_range(start_date, end_date)
            
            # Build date range filter
            date_filter = {
                'createdAt': {
                    'gte': datetime.combine(start_date, datetime.min.time()),
                    'lte': datetime.combine(end_date, datetime.max.time())
                }
            }
            
            if branch_id:
                date_filter['branchId'] = branch_id
            
            # Get revenue data
            revenue_data = await self._get_revenue_data(date_filter)
            
            # Get expense data
            expense_data = await self._get_expense_data(date_filter)
            
            # Get cost of goods sold
            cogs_data = await self._get_cogs_data(date_filter)
            
            # Validate sufficient data
            ValidationUtils.validate_required_data(
                revenue_data + expense_data + cogs_data, 
                "transaction", 
                minimum_required=0
            )
            
            # Calculate totals using safe decimal operations
            total_revenue = safe_decimal_sum([item['amount'] for item in revenue_data])
            total_expenses = safe_decimal_sum([item['amount'] for item in expense_data])
            total_cogs = safe_decimal_sum([item['amount'] for item in cogs_data])
            
            gross_profit = total_revenue - total_cogs
            operating_profit = gross_profit - total_expenses
            net_profit = operating_profit  # Simplified for now
            
            return IncomeStatementSchema(
                period_start=start_date,
                period_end=end_date,
                revenue=revenue_data,
                total_revenue=float(total_revenue),
                cost_of_goods_sold=cogs_data,
                total_cogs=float(total_cogs),
                gross_profit=float(gross_profit),
                expenses=expense_data,
                total_expenses=float(total_expenses),
                operating_profit=float(operating_profit),
                net_profit=float(net_profit),
                generated_at=datetime.utcnow()
            )
            
        except (AuthorizationError, ValidationError, ValidationError):
            raise
        except Exception as e:
            ErrorHandler.log_and_raise(
                ExportError,
                f"Failed to generate income statement: {str(e)}",
                report_type="income_statement",
                start_date=start_date.isoformat() if start_date else None,
                end_date=end_date.isoformat() if end_date else None
            )
    
    async def generate_balance_sheet(
        self,
        as_of_date: Optional[date] = None,
        branch_id: Optional[int] = None,
        current_user: Dict[str, Any] = None
    ) -> BalanceSheetSchema:
        """Generate balance sheet as of specific date.
        
        Args:
            as_of_date: Balance sheet date (defaults to today)
            branch_id: Optional branch filter
            current_user: Current authenticated user
            
        Returns:
            Balance sheet data
            
        Raises:
            AuthorizationError: If user lacks permissions
            ExportError: If report generation fails
        """
        try:
            # Validate permissions
            validate_financial_permission(current_user, 'read')
            ValidationUtils.validate_branch_access(current_user, branch_id)
            
            # Default to today if no date specified
            if not as_of_date:
                as_of_date = date.today()
            
            # Build date filter
            date_filter = {
                'createdAt': {
                    'lte': datetime.combine(as_of_date, datetime.max.time())
                }
            }
            
            if branch_id:
                date_filter['branchId'] = branch_id
            
            # Get assets
            assets_list = await self._get_assets_data(date_filter)
            
            # Get liabilities
            liabilities_list = await self._get_liabilities_data(date_filter)
            
            # Get equity
            equity_list = await self._get_equity_data(date_filter)
            
            # Transform to dictionary format expected by schema
            assets_data = {
                'current_assets': {},
                'fixed_assets': {},
                'total_current_assets': 0,
                'total_fixed_assets': 0
            }
            
            # Process assets
            for asset in assets_list:
                if asset['category'] == 'CURRENT_ASSETS':
                    key = asset['description'].lower().replace(' ', '_').replace('_and_', '_')
                    assets_data['current_assets'][key] = str(asset['amount'])
                    assets_data['total_current_assets'] += asset['amount']
                elif asset['category'] == 'FIXED_ASSETS':
                    key = asset['description'].lower().replace(' ', '_').replace('_and_', '_')
                    assets_data['fixed_assets'][key] = str(asset['amount'])
                    assets_data['total_fixed_assets'] += asset['amount']
            
            # Transform liabilities and equity (simplified for now since they return empty lists)
            liabilities_data = {
                'current_liabilities': {},
                'long_term_liabilities': {},
                'total_current_liabilities': 0,
                'total_long_term_liabilities': 0
            }
            
            equity_data = {
                'capital': '0',
                'retained_earnings': '0'
            }
            
            # Calculate totals
            total_assets = sum(asset['amount'] for asset in assets_list)
            total_liabilities = sum(liability['amount'] for liability in liabilities_list)  
            total_equity = sum(equity['amount'] for equity in equity_list)
            
            return BalanceSheetSchema(
                as_of_date=as_of_date,
                assets=assets_data,
                total_assets=float(total_assets),
                liabilities=liabilities_data,
                total_liabilities=float(total_liabilities),
                equity=equity_data,
                total_equity=float(total_equity),
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error generating balance sheet: {e}")
            raise
    
    async def generate_cash_flow_statement(
        self,
        start_date: date,
        end_date: date,
        branch_id: Optional[int] = None,
        current_user: Dict[str, Any] = None
    ) -> CashFlowStatementSchema:
        """Generate cash flow statement for specified period.
        
        Args:
            start_date: Period start date
            end_date: Period end date
            branch_id: Optional branch filter
            current_user: Current authenticated user
            
        Returns:
            Cash flow statement data
        """
        try:
            # Check permissions
            if not self._check_financial_permission(current_user, 'read'):
                raise ValueError("Insufficient permissions to generate cash flow statement")
            
            # Build date filter
            date_filter = {
                'createdAt': {
                    'gte': datetime.combine(start_date, datetime.min.time()),
                    'lte': datetime.combine(end_date, datetime.max.time())
                }
            }
            
            if branch_id:
                date_filter['branchId'] = branch_id
            
            # Get operating activities
            operating_activities = await self._get_operating_cash_flow(date_filter)
            
            # Get investing activities
            investing_activities = await self._get_investing_cash_flow(date_filter)
            
            # Get financing activities
            financing_activities = await self._get_financing_cash_flow(date_filter)
            
            # Calculate totals
            operating_total = sum(item['amount'] for item in operating_activities)
            investing_total = sum(item['amount'] for item in investing_activities)
            financing_total = sum(item['amount'] for item in financing_activities)
            
            net_cash_flow = operating_total + investing_total + financing_total
            
            # Get opening and closing balances
            opening_balance = await self._get_opening_cash_balance(start_date, branch_id)
            closing_balance = opening_balance + net_cash_flow
            
            return CashFlowStatementSchema(
                period_start=start_date,
                period_end=end_date,
                operating_activities=operating_activities,
                operating_total=float(operating_total),
                investing_activities=investing_activities,
                investing_total=float(investing_total),
                financing_activities=financing_activities,
                financing_total=float(financing_total),
                net_cash_flow=float(net_cash_flow),
                opening_cash_balance=float(opening_balance),
                closing_cash_balance=float(closing_balance),
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error generating cash flow statement: {e}")
            raise
    
    async def generate_tax_report(
        self,
        start_date: date,
        end_date: date,
        branch_id: Optional[int] = None,
        current_user: Dict[str, Any] = None
    ) -> TaxReportSchema:
        """Generate tax report for specified period.
        
        Args:
            start_date: Period start date
            end_date: Period end date
            branch_id: Optional branch filter
            current_user: Current authenticated user
            
        Returns:
            Tax report data
        """
        try:
            # Check permissions
            if not self._check_financial_permission(current_user, 'read'):
                raise ValueError("Insufficient permissions to generate tax report")
            
            # Build date filter
            date_filter = {
                'createdAt': {
                    'gte': datetime.combine(start_date, datetime.min.time()),
                    'lte': datetime.combine(end_date, datetime.max.time())
                }
            }
            
            if branch_id:
                date_filter['branchId'] = branch_id
            
            # Get taxable income data
            taxable_income = await self._get_taxable_income(date_filter)
            
            # Get tax deductions
            deductions = await self._get_tax_deductions(date_filter)
            
            # Calculate tax liability
            total_taxable_income = sum(item['amount'] for item in taxable_income)
            total_deductions = sum(item['amount'] for item in deductions)
            
            adjusted_taxable_income = total_taxable_income - total_deductions
            
            # Calculate tax amounts (simplified calculation)
            tax_rate = 0.25  # 25% tax rate (should be configurable)
            tax_liability = adjusted_taxable_income * tax_rate
            
            # Get payments made
            payments_made = await self._get_tax_payments(date_filter)
            total_payments = sum(payment['amount'] for payment in payments_made)
            
            balance_due = tax_liability - total_payments
            
            return TaxReportSchema(
                period_start=start_date,
                period_end=end_date,
                taxable_income=taxable_income,
                total_taxable_income=float(total_taxable_income),
                deductions=deductions,
                total_deductions=float(total_deductions),
                adjusted_taxable_income=float(adjusted_taxable_income),
                tax_rate=tax_rate,
                tax_liability=float(tax_liability),
                payments_made=payments_made,
                total_payments=float(total_payments),
                balance_due=float(balance_due),
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error generating tax report: {e}")
            raise
    
    # Helper methods for data retrieval
    async def _get_revenue_data(self, date_filter: Dict) -> List[Dict[str, Any]]:
        """Get revenue data for the period."""
        sales = await self.db.sale.find_many(
            where=date_filter,
            include={'items': {'include': {'stock': {'include': {'product': True}}}}}
        )
        
        revenue_data = []
        for sale in sales:
            total_amount = sum(float(item.price) * item.quantity for item in sale.items)
            revenue_data.append({
                'description': f'Sale #{sale.id}',
                'amount': total_amount,
                'date': sale.createdAt.date(),
                'category': 'SALES'
            })
        
        return revenue_data
    
    async def _get_expense_data(self, date_filter: Dict) -> List[Dict[str, Any]]:
        """Get expense data for the period."""
        expenses = await self.db.expense.find_many(where=date_filter)
        
        return [
            {
                'description': expense.description,
                'amount': float(expense.amount),
                'date': expense.createdAt.date(),
                'category': expense.category
            }
            for expense in expenses
        ]
    
    async def _get_cogs_data(self, date_filter: Dict) -> List[Dict[str, Any]]:
        """Get cost of goods sold data."""
        sales = await self.db.sale.find_many(
            where=date_filter,
            include={'items': {'include': {'stock': {'include': {'product': True}}}}}
        )
        
        cogs_data = []
        for sale in sales:
            total_cost = sum(float(item.stock.product.costPrice) * item.quantity for item in sale.items)
            cogs_data.append({
                'description': f'COGS for Sale #{sale.id}',
                'amount': total_cost,
                'date': sale.createdAt.date(),
                'category': 'COGS'
            })
        
        return cogs_data
    
    async def _get_assets_data(self, date_filter: Dict) -> List[Dict[str, Any]]:
        """Get assets data."""
        # This is simplified - in a real system, you'd have specific asset tracking
        assets = []
        
        # Cash and cash equivalents
        cash_balance = await self._get_total_cash_balance(date_filter)
        assets.append({
            'description': 'Cash and Cash Equivalents',
            'amount': cash_balance,
            'category': 'CURRENT_ASSETS'
        })
        
        # Inventory
        inventory_value = await self._get_inventory_value(date_filter)
        assets.append({
            'description': 'Inventory',
            'amount': inventory_value,
            'category': 'CURRENT_ASSETS'
        })
        
        return assets
    
    async def _get_liabilities_data(self, date_filter: Dict) -> List[Dict[str, Any]]:
        """Get liabilities data."""
        # This is simplified - in a real system, you'd have specific liability tracking
        return []
    
    async def _get_equity_data(self, date_filter: Dict) -> List[Dict[str, Any]]:
        """Get equity data."""
        # This is simplified - in a real system, you'd have specific equity tracking
        return []
    
    async def _get_operating_cash_flow(self, date_filter: Dict) -> List[Dict[str, Any]]:
        """Get operating cash flow activities."""
        # Simplified implementation
        return []
    
    async def _get_investing_cash_flow(self, date_filter: Dict) -> List[Dict[str, Any]]:
        """Get investing cash flow activities."""
        return []
    
    async def _get_financing_cash_flow(self, date_filter: Dict) -> List[Dict[str, Any]]:
        """Get financing cash flow activities."""
        return []
    
    async def _get_opening_cash_balance(self, start_date: date, branch_id: Optional[int]) -> float:
        """Get opening cash balance."""
        return 0.0  # Simplified
    
    async def _get_taxable_income(self, date_filter: Dict) -> List[Dict[str, Any]]:
        """Get taxable income data."""
        return await self._get_revenue_data(date_filter)
    
    async def _get_tax_deductions(self, date_filter: Dict) -> List[Dict[str, Any]]:
        """Get tax deductions."""
        return await self._get_expense_data(date_filter)
    
    async def _get_tax_payments(self, date_filter: Dict) -> List[Dict[str, Any]]:
        """Get tax payments made."""
        return []  # Simplified
    
    async def _get_total_cash_balance(self, date_filter: Dict) -> float:
        """Get total cash balance."""
        return 10000.0  # Simplified
    
    async def _get_inventory_value(self, date_filter: Dict) -> float:
        """Get total inventory value."""
        stocks = await self.db.stock.find_many(
            include={'product': True}
        )
        
        total_value = sum(
            float(stock.product.costPrice) * stock.quantity 
            for stock in stocks
        )
        
        return total_value
    
    def _check_financial_permission(self, user: Dict[str, Any], action: str) -> bool:
        """Check if user has financial permission for specified action.
        
        Args:
            user: Current user data
            action: Required action (read, write, etc.)
            
        Returns:
            True if permission granted, False otherwise
        """
        if not user:
            return False
        
        # Check if user has required permissions
        # This is simplified - implement based on your permission system
        user_role = user.get('role', 'CASHIER')
        
        if action == 'read':
            return user_role in ['MANAGER', 'ADMIN', 'ACCOUNTANT']
        elif action == 'write':
            return user_role in ['MANAGER', 'ADMIN', 'ACCOUNTANT']
        
        return False
