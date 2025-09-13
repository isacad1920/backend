"""
Financial analytics service.
"""
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from generated.prisma import Prisma
from app.modules.financial.schema import (
    FinancialSummarySchema,
    SalesAnalyticsSchema,
    InventoryAnalyticsSchema,
    CustomerAnalyticsSchema,
    DashboardSummarySchema,
    PerformanceMetricsSchema,
    FinancialAlertsSchema,
    AlertSchema,
    ReportPeriod
)

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for financial analytics and insights."""
    
    def __init__(self, db: Prisma):
        """Initialize analytics service.
        
        Args:
            db: Prisma database client
        """
        self.db = db
    
    async def get_financial_summary(
        self, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        branch_id: Optional[int] = None,
        current_user: Dict[str, Any] = None
    ) -> FinancialSummarySchema:
        """Get financial summary for a given period.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            branch_id: Specific branch ID
            current_user: Current authenticated user
            
        Returns:
            Financial summary data
        """
        try:
            # Check permissions
            if not self._check_financial_permission(current_user, 'read'):
                raise ValueError("Insufficient permissions to view financial reports")
            
            # Set default period if not provided (current month)
            if not start_date:
                start_date = date.today().replace(day=1)
            if not end_date:
                end_date = date.today()
            
            # Build filters
            filters = {
                'createdAt': {
                    'gte': datetime.combine(start_date, datetime.min.time()),
                    'lte': datetime.combine(end_date, datetime.max.time())
                }
            }
            
            if branch_id:
                filters['branch_id'] = branch_id
            
            # Get sales data
            sales_data = await self.db.sale.find_many(
                where=filters,
                include={
                    'items': {
                        'include': {
                            'stock': {
                                'include': {
                                    'product': True
                                }
                            }
                        }
                    }
                }
            )
            
            # Calculate metrics
            total_revenue = sum(
                sum(float(item.price) * item.quantity for item in sale.items)
                for sale in sales_data
            )
            
            total_sales_count = len(sales_data)
            
            total_cost = sum(
                sum(float(item.stock.product.costPrice) * item.quantity for item in sale.items)
                for sale in sales_data
            )
            
            gross_profit = total_revenue - total_cost
            profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            # Get expenses
            expenses = await self.db.expense.find_many(where=filters)
            total_expenses = sum(float(expense.amount) for expense in expenses)
            
            net_profit = gross_profit - total_expenses
            
            # Calculate trends (compare with previous period)
            previous_start = start_date - (end_date - start_date)
            previous_end = start_date - timedelta(days=1)
            
            previous_filters = {
                'createdAt': {
                    'gte': datetime.combine(previous_start, datetime.min.time()),
                    'lte': datetime.combine(previous_end, datetime.max.time())
                }
            }
            
            if branch_id:
                previous_filters['branch_id'] = branch_id
            
            previous_sales = await self.db.sale.find_many(
                where=previous_filters,
                include={
                    'items': {
                        'include': {
                            'stock': {
                                'include': {
                                    'product': True
                                }
                            }
                        }
                    }
                }
            )
            
            previous_revenue = sum(
                sum(float(item.price) * item.quantity for item in sale.items)
                for sale in previous_sales
            )
            
            revenue_growth = ((total_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
            
            return FinancialSummarySchema(
                period_start=start_date,
                period_end=end_date,
                total_revenue=total_revenue,
                total_sales=total_sales_count,
                total_expenses=total_expenses,
                gross_profit=gross_profit,
                net_profit=net_profit,
                profit_margin=profit_margin,
                revenue_growth=revenue_growth,
                top_selling_products=self._get_top_products(sales_data),
                sales_by_category=self._get_sales_by_category(sales_data),
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error generating financial summary: {e}")
            raise
    
    async def get_sales_analytics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        branch_id: Optional[int] = None,
        current_user: Dict[str, Any] = None
    ) -> SalesAnalyticsSchema:
        """Get detailed sales analytics.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            branch_id: Specific branch ID
            current_user: Current authenticated user
            
        Returns:
            Sales analytics data
        """
        try:
            # Check permissions
            if not self._check_financial_permission(current_user, 'read'):
                raise ValueError("Insufficient permissions to view sales analytics")
            
            # Set default dates
            if not start_date:
                start_date = date.today().replace(day=1)
            if not end_date:
                end_date = date.today()
            
            # Build filters
            filters = {
                'createdAt': {
                    'gte': datetime.combine(start_date, datetime.min.time()),
                    'lte': datetime.combine(end_date, datetime.max.time())
                }
            }
            
            if branch_id:
                filters['branchId'] = branch_id
            
            # Get sales data
            sales_data = await self.db.sale.find_many(
                where=filters,
                include={
                    'items': {
                        'include': {
                            'stock': {
                                'include': {
                                    'product': True
                                }
                            }
                        }
                    },
                    'branch': True
                }
            )
            
            # Calculate metrics
            total_sales = len(sales_data)
            total_revenue = sum(
                sum(float(item.price) * item.quantity for item in sale.items)
                for sale in sales_data
            )
            
            average_order_value = total_revenue / total_sales if total_sales > 0 else 0
            
            # Analyze trends
            daily_sales = self._analyze_daily_sales(sales_data)
            monthly_sales = self._analyze_monthly_sales(sales_data)
            
            # Top performers
            top_products = self._analyze_top_products(sales_data)
            sales_by_category = self._analyze_sales_by_category(sales_data)
            sales_by_branch = self._analyze_sales_by_branch(sales_data)
            
            # Trends analysis
            sales_trends = self._analyze_sales_trends(sales_data)
            
            return SalesAnalyticsSchema(
                period_start=start_date,
                period_end=end_date,
                total_sales=total_sales,
                total_revenue=total_revenue,
                average_order_value=average_order_value,
                daily_sales=daily_sales,
                monthly_sales=monthly_sales,
                top_products=top_products,
                sales_by_category=sales_by_category,
                sales_by_branch=sales_by_branch,
                sales_trends=sales_trends,
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error generating sales analytics: {e}")
            raise
    
    async def get_inventory_analytics(
        self,
        branch_id: Optional[int] = None,
        current_user: Dict[str, Any] = None
    ) -> InventoryAnalyticsSchema:
        """Get inventory analytics.
        
        Args:
            branch_id: Specific branch ID
            current_user: Current authenticated user
            
        Returns:
            Inventory analytics data
        """
        try:
            # Check permissions
            if not self._check_financial_permission(current_user, 'read'):
                raise ValueError("Insufficient permissions to view inventory analytics")
            
            # Get stock data
            stock_filters = {}
            if branch_id:
                stock_filters['branchId'] = branch_id
            
            stocks = await self.db.stock.find_many(
                where=stock_filters,
                include={'product': True}
            )
            
            # Calculate metrics
            total_products = len(set(stock.productId for stock in stocks))
            total_stock_value = sum(
                float(stock.product.costPrice) * stock.quantity for stock in stocks
            )
            
            # Low stock items (less than 10 units)
            low_stock_items = [
                {
                    'product_name': stock.product.name,
                    'sku': stock.product.sku,
                    'current_stock': stock.quantity,
                    'reorder_level': 10  # This should come from product settings
                }
                for stock in stocks
                if stock.quantity < 10
            ]
            
            # High value items
            high_value_items = sorted([
                {
                    'product_name': stock.product.name,
                    'sku': stock.product.sku,
                    'value': float(stock.product.costPrice) * stock.quantity
                }
                for stock in stocks
            ], key=lambda x: x['value'], reverse=True)[:10]
            
            # Stock turnover analysis (simplified)
            stock_turnover_data = []  # Would require historical sales data
            
            return InventoryAnalyticsSchema(
                total_products=total_products,
                total_stock_value=total_stock_value,
                low_stock_items=low_stock_items,
                high_value_items=high_value_items,
                stock_turnover=stock_turnover_data,
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error generating inventory analytics: {e}")
            raise
    
    async def get_dashboard_summary(
        self,
        current_user: Dict[str, Any] = None
    ) -> DashboardSummarySchema:
        """Get dashboard summary for quick overview.
        
        Args:
            current_user: Current authenticated user
            
        Returns:
            Dashboard summary data
        """
        try:
            # Check permissions
            if not self._check_financial_permission(current_user, 'read'):
                raise ValueError("Insufficient permissions to view dashboard")
            
            today = date.today()
            month_start = today.replace(day=1)
            
            # Today's metrics
            today_filters = {
                'createdAt': {
                    'gte': datetime.combine(today, datetime.min.time()),
                    'lte': datetime.combine(today, datetime.max.time())
                }
            }
            
            today_sales = await self.db.sale.find_many(
                where=today_filters,
                include={
                    'items': {
                        'include': {
                            'stock': {
                                'include': {
                                    'product': True
                                }
                            }
                        }
                    }
                }
            )
            
            today_revenue = sum(
                sum(float(item.price) * item.quantity for item in sale.items)
                for sale in today_sales
            )
            
            # This month's metrics
            month_filters = {
                'createdAt': {
                    'gte': datetime.combine(month_start, datetime.min.time()),
                    'lte': datetime.combine(today, datetime.max.time())
                }
            }
            
            month_sales = await self.db.sale.find_many(
                where=month_filters,
                include={
                    'items': {
                        'include': {
                            'stock': {
                                'include': {
                                    'product': True
                                }
                            }
                        }
                    }
                }
            )
            
            month_revenue = sum(
                sum(float(item.price) * item.quantity for item in sale.items)
                for sale in month_sales
            )
            
            # Inventory summary
            total_products = await self.db.product.count()
            low_stock_count = await self.db.stock.count(where={'quantity': {'lt': 10}})
            
            # Recent activities (last 5 sales)
            recent_activities = await self.db.sale.find_many(
                take=5,
                order={'createdAt': 'desc'},
                include={
                    'items': {
                        'include': {
                            'stock': {
                                'include': {
                                    'product': True
                                }
                            }
                        }
                    }
                }
            )
            
            activities = [
                {
                    'type': 'sale',
                    'description': f'Sale #{sale.id}',
                    'amount': sum(float(item.price) * item.quantity for item in sale.items),
                    'timestamp': sale.createdAt
                }
                for sale in recent_activities
            ]
            
            return DashboardSummarySchema(
                today_sales=len(today_sales),
                today_revenue=today_revenue,
                month_sales=len(month_sales),
                month_revenue=month_revenue,
                total_products=total_products,
                low_stock_alerts=low_stock_count,
                recent_activities=activities,
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error generating dashboard summary: {e}")
            raise
    
    async def get_financial_alerts(
        self,
        current_user: Dict[str, Any] = None
    ) -> FinancialAlertsSchema:
        """Get financial alerts and warnings.
        
        Args:
            current_user: Current authenticated user
            
        Returns:
            Financial alerts data
        """
        try:
            # Check permissions
            if not self._check_financial_permission(current_user, 'read'):
                raise ValueError("Insufficient permissions to view financial alerts")
            
            alerts = []
            
            # Low stock alerts
            low_stock_items = await self.db.stock.find_many(
                where={'quantity': {'lt': 10}},
                include={'product': True}
            )
            
            for stock in low_stock_items:
                alerts.append(AlertSchema(
                    type='LOW_STOCK',
                    severity='WARNING',
                    title=f'Low Stock: {stock.product.name}',
                    message=f'Product {stock.product.name} has only {stock.quantity} units remaining',
                    action_required=True,
                    created_at=datetime.utcnow()
                ))
            
            # Revenue alerts (if today's revenue is significantly lower than average)
            today = date.today()
            today_filters = {
                'createdAt': {
                    'gte': datetime.combine(today, datetime.min.time()),
                    'lte': datetime.combine(today, datetime.max.time())
                }
            }
            
            today_sales = await self.db.sale.find_many(
                where=today_filters,
                include={
                    'items': {
                        'include': {
                            'stock': {
                                'include': {
                                    'product': True
                                }
                            }
                        }
                    }
                }
            )
            
            today_revenue = sum(
                sum(float(item.price) * item.quantity for item in sale.items)
                for sale in today_sales
            )
            
            # Get average daily revenue for comparison
            week_ago = today - timedelta(days=7)
            week_filters = {
                'createdAt': {
                    'gte': datetime.combine(week_ago, datetime.min.time()),
                    'lte': datetime.combine(today - timedelta(days=1), datetime.max.time())
                }
            }
            
            week_sales = await self.db.sale.find_many(
                where=week_filters,
                include={
                    'items': {
                        'include': {
                            'stock': {
                                'include': {
                                    'product': True
                                }
                            }
                        }
                    }
                }
            )
            
            week_revenue = sum(
                sum(float(item.price) * item.quantity for item in sale.items)
                for sale in week_sales
            )
            
            average_daily_revenue = week_revenue / 7 if week_revenue > 0 else 0
            
            # Alert if today's revenue is 50% below average
            if today_revenue < (average_daily_revenue * 0.5) and average_daily_revenue > 0:
                alerts.append(AlertSchema(
                    type='LOW_REVENUE',
                    severity='WARNING',
                    title='Low Revenue Alert',
                    message=f"Today's revenue ({today_revenue:.2f}) is significantly below average ({average_daily_revenue:.2f})",
                    action_required=True,
                    created_at=datetime.utcnow()
                ))
            
            return FinancialAlertsSchema(
                alerts=alerts,
                total_alerts=len(alerts),
                critical_alerts=len([a for a in alerts if a.severity == 'CRITICAL']),
                warning_alerts=len([a for a in alerts if a.severity == 'WARNING']),
                info_alerts=len([a for a in alerts if a.severity == 'INFO']),
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error generating financial alerts: {e}")
            raise
    
    # Helper methods for analytics calculations
    def _analyze_daily_sales(self, sales_data: List) -> List[Dict[str, Any]]:
        """Analyze sales data by day."""
        daily_data = {}
        
        for sale in sales_data:
            day = sale.createdAt.date()
            if day not in daily_data:
                daily_data[day] = {'sales': 0, 'revenue': 0}
            
            daily_data[day]['sales'] += 1
            daily_data[day]['revenue'] += sum(
                float(item.price) * item.quantity for item in sale.items
            )
        
        return [
            {
                'date': day.isoformat(),
                'sales': data['sales'],
                'revenue': data['revenue']
            }
            for day, data in sorted(daily_data.items())
        ]
    
    def _analyze_monthly_sales(self, sales_data: List) -> List[Dict[str, Any]]:
        """Analyze sales data by month."""
        monthly_data = {}
        
        for sale in sales_data:
            month_key = sale.createdAt.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {'sales': 0, 'revenue': 0}
            
            monthly_data[month_key]['sales'] += 1
            monthly_data[month_key]['revenue'] += sum(
                float(item.price) * item.quantity for item in sale.items
            )
        
        return [
            {
                'month': month,
                'sales': data['sales'],
                'revenue': data['revenue']
            }
            for month, data in sorted(monthly_data.items())
        ]
    
    def _analyze_top_products(self, sales_data: List, limit: int = 10) -> List[Dict[str, Any]]:
        """Analyze top-selling products."""
        product_data = {}
        
        for sale in sales_data:
            for item in sale.items:
                product_id = item.stock.product.id
                if product_id not in product_data:
                    product_data[product_id] = {
                        'product': item.stock.product,
                        'quantity': 0,
                        'revenue': 0
                    }
                
                product_data[product_id]['quantity'] += item.quantity
                product_data[product_id]['revenue'] += float(item.price) * item.quantity
        
        # Sort by revenue and return top products
        sorted_products = sorted(
            product_data.values(),
            key=lambda x: x['revenue'],
            reverse=True
        )[:limit]
        
        return [
            {
                'product_name': data['product'].name,
                'sku': data['product'].sku,
                'quantity_sold': data['quantity'],
                'revenue': data['revenue']
            }
            for data in sorted_products
        ]
    
    def _analyze_sales_by_category(self, sales_data: List) -> List[Dict[str, Any]]:
        """Analyze sales by product category."""
        category_data = {}
        
        for sale in sales_data:
            for item in sale.items:
                product = item.stock.product
                category_id = product.categoryId or 0
                category_name = product.category.name if product.category else 'Uncategorized'
                
                if category_id not in category_data:
                    category_data[category_id] = {
                        'category_name': category_name,
                        'sales': 0,
                        'revenue': 0
                    }
                
                category_data[category_id]['sales'] += item.quantity
                category_data[category_id]['revenue'] += float(item.price) * item.quantity
        
        return [
            {
                'category': data['category_name'],
                'sales': data['sales'],
                'revenue': data['revenue']
            }
            for data in category_data.values()
        ]
    
    def _analyze_sales_by_branch(self, sales_data: List) -> List[Dict[str, Any]]:
        """Analyze sales by branch."""
        branch_data = {}
        
        for sale in sales_data:
            branch_id = sale.branchId or 0
            branch_name = sale.branch.name if sale.branch else 'Unknown'
            
            if branch_id not in branch_data:
                branch_data[branch_id] = {
                    'branch_name': branch_name,
                    'sales': 0,
                    'revenue': 0
                }
            
            branch_data[branch_id]['sales'] += 1
            branch_data[branch_id]['revenue'] += sum(
                float(item.price) * item.quantity for item in sale.items
            )
        
        return [
            {
                'branch': data['branch_name'],
                'sales': data['sales'],
                'revenue': data['revenue']
            }
            for data in branch_data.values()
        ]
    
    def _analyze_sales_trends(self, sales_data: List) -> Dict[str, Any]:
        """Analyze sales trends and patterns."""
        if not sales_data:
            return {'trend': 'stable', 'growth_rate': 0, 'pattern': 'insufficient_data'}
        
        # Simple trend analysis based on chronological order
        sorted_sales = sorted(sales_data, key=lambda x: x.createdAt)
        
        # Calculate growth rate (simplified)
        if len(sorted_sales) >= 2:
            first_half = sorted_sales[:len(sorted_sales)//2]
            second_half = sorted_sales[len(sorted_sales)//2:]
            
            first_half_revenue = sum(
                sum(float(item.price) * item.quantity for item in sale.items)
                for sale in first_half
            )
            
            second_half_revenue = sum(
                sum(float(item.price) * item.quantity for item in sale.items)
                for sale in second_half
            )
            
            if first_half_revenue > 0:
                growth_rate = ((second_half_revenue - first_half_revenue) / first_half_revenue) * 100
            else:
                growth_rate = 0
            
            if growth_rate > 10:
                trend = 'growing'
            elif growth_rate < -10:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
            growth_rate = 0
        
        return {
            'trend': trend,
            'growth_rate': growth_rate,
            'pattern': 'normal'  # Could be enhanced with more sophisticated analysis
        }
    
    def _get_top_products(self, sales_data: List, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top-selling products for summary."""
        return self._analyze_top_products(sales_data, limit)
    
    def _get_sales_by_category(self, sales_data: List) -> List[Dict[str, Any]]:
        """Get sales by category for summary."""
        return self._analyze_sales_by_category(sales_data)
    
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
