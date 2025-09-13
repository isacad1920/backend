"""
Inventory management service layer with comprehensive business logic.
"""
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from app.modules.inventory.schema import (
    AdjustmentType,
    DeadStockAnalysisSchema,
    InventoryDashboardSchema,
    InventoryValuationSchema,
    LowStockAlertSchema,
    StockAdjustmentCreateSchema,
    StockAdjustmentSchema,
    StockLevelSchema,
    StockStatus,
)
from generated.prisma import Prisma

logger = logging.getLogger(__name__)

class InventoryService:
    """Comprehensive inventory management service."""
    
    def __init__(self, db: Prisma):
        self.db = db

    async def get_stock_levels(
        self,
        product_ids: list[int] | None = None,
        status_filter: StockStatus | None = None,
        category_id: int | None = None,
        low_stock_only: bool = False
    ) -> list[StockLevelSchema]:
        """Get current stock levels with filtering options."""
        try:
            where_conditions = {}
            
            if product_ids:
                where_conditions['productId'] = {'in': product_ids}
            
            if category_id is not None:
                # Try to coerce to int; if invalid, skip filter to avoid Prisma errors
                try:
                    cat_id = int(category_id)  # type: ignore[arg-type]
                    # Relation filter uses `is` on Prisma Python
                    where_conditions['product'] = {
                        'is': {'categoryId': cat_id}
                    }
                except Exception:
                    # Ignore invalid category filter
                    pass
            
            stocks = await self.db.stock.find_many(
                where=where_conditions,
                include={
                    'product': {
                        'include': {
                            'category': True
                        }
                    }
                },
                order={'updatedAt': 'desc'}
            )
            
            stock_levels = []
            for stock in stocks:
                # Calculate stock status
                stock_status = self._calculate_stock_status(
                    stock.quantity, 
                    getattr(stock.product, 'reorderLevel', 10)
                )
                
                # Filter by status if specified
                if status_filter and stock_status != status_filter:
                    continue
                
                # Filter low stock only
                if low_stock_only and stock_status not in [StockStatus.LOW_STOCK, StockStatus.OUT_OF_STOCK]:
                    continue
                
                # Calculate available quantity (total - reserved)
                reserved_qty = await self._get_reserved_quantity(stock.productId)
                available_qty = max(0, stock.quantity - reserved_qty)
                
                # Calculate days of stock remaining
                days_of_stock = await self._calculate_days_of_stock(stock.productId, available_qty)
                
                stock_level = StockLevelSchema(
                    id=stock.id,
                    product_id=stock.productId,
                    product_name=stock.product.name,
                    product_sku=stock.product.sku,
                    category_name=stock.product.category.name if stock.product.category else None,
                    current_quantity=stock.quantity,
                    reserved_quantity=reserved_qty,
                    available_quantity=available_qty,
                    reorder_level=getattr(stock.product, 'reorderLevel', 10),
                    unit_cost=stock.product.costPrice,
                    unit_price=stock.product.sellingPrice,
                    stock_status=stock_status,
                    days_of_stock=days_of_stock,
                    last_restocked=stock.lastRestocked,
                    created_at=stock.createdAt,
                    updated_at=stock.updatedAt
                )
                stock_levels.append(stock_level)
            
            return stock_levels
            
        except Exception as e:
            logger.error(f"Error getting stock levels: {str(e)}")
            raise

    async def create_stock_adjustment(
        self,
        adjustment_data: StockAdjustmentCreateSchema,
        user_id: int
    ) -> StockAdjustmentSchema:
        """Create a stock adjustment record and update stock levels (persistent)."""
        try:
            # Get current stock
            stock = await self.db.stock.find_unique(
                where={'productId': adjustment_data.product_id},
                include={'product': True}
            )
            
            if not stock:
                raise ValueError(f"Stock record not found for product ID {adjustment_data.product_id}")
            
            quantity_before = stock.quantity
            
            # Calculate new quantity based on adjustment type
            if adjustment_data.adjustment_type == AdjustmentType.INCREASE:
                quantity_after = quantity_before + adjustment_data.quantity
            elif adjustment_data.adjustment_type == AdjustmentType.DECREASE:
                quantity_after = max(0, quantity_before - adjustment_data.quantity)
            else:  # RECOUNT
                quantity_after = adjustment_data.quantity
            
            # Update stock quantity
            updated_stock = await self.db.stock.update(
                where={'id': stock.id},
                data={
                    'quantity': quantity_after,
                    'lastRestocked': datetime.utcnow() if adjustment_data.adjustment_type == AdjustmentType.INCREASE else stock.lastRestocked
                }
            )
            # Persist adjustment record
            adj_row = await self.db.stockadjustment.create(
                data={
                    'productId': adjustment_data.product_id,
                    'adjustmentType': adjustment_data.adjustment_type.name if hasattr(adjustment_data.adjustment_type, 'name') else adjustment_data.adjustment_type,
                    'reason': adjustment_data.reason,
                    'quantityBefore': quantity_before,
                    'quantityAfter': quantity_after,
                    'adjustmentQty': adjustment_data.quantity,
                    'notes': adjustment_data.notes,
                    'referenceNumber': adjustment_data.reference_number,
                    'createdById': user_id,
                },
                include={'product': True, 'createdBy': True}
            )

            adjustment = StockAdjustmentSchema(
                id=adj_row.id,
                product_id=adj_row.productId,
                product_name=adj_row.product.name if adj_row.product else '',
                adjustment_type=adjustment_data.adjustment_type,
                quantity_before=adj_row.quantityBefore,
                quantity_after=adj_row.quantityAfter,
                adjustment_quantity=adj_row.adjustmentQty,
                reason=adjustment_data.reason,  # already enum/string
                notes=adj_row.notes,
                reference_number=adj_row.referenceNumber,
                created_by=adj_row.createdById if hasattr(adj_row, 'createdById') else user_id,
                created_at=adj_row.createdAt
            )
            
            logger.info(f"Stock adjustment created: Product {adjustment_data.product_id}, {quantity_before} -> {quantity_after}")
            
            return adjustment
            
        except Exception as e:
            logger.error(f"Error creating stock adjustment: {str(e)}")
            raise

    async def get_low_stock_alerts(
        self,
        threshold: int | None = None,
        search: str | None = None,
        category_id: int | None = None
    ) -> list[LowStockAlertSchema]:
        """Get products that are below (<=) the provided threshold.

        If a threshold is not provided the system default from settings is used.
        """
        try:
            from app.core.config import settings  # Local import to avoid circulars
            effective_threshold = threshold if threshold is not None else settings.default_low_stock_threshold
            where: dict[str, Any] = {
                'quantity': {'lte': effective_threshold}
            }
            # Category relation filter
            if category_id is not None:
                try:
                    where['product'] = {'is': {'categoryId': int(category_id)}}
                except Exception:
                    pass
            # Basic search on product name or sku (Prisma OR condition)
            if search:
                pattern = f"%{search}%"
                where['product'] = {
                    'is': {
                        **(where.get('product', {}).get('is', {})),
                        'OR': [
                            {'name': {'contains': search, 'mode': 'insensitive'}},
                            {'sku': {'contains': search, 'mode': 'insensitive'}}
                        ]
                    }
                }
            stocks = await self.db.stock.find_many(
                where=where,
                include={
                    'product': {
                        'include': {
                            'category': True
                        }
                    }
                },
                order={'quantity': 'asc'}
            )

            alerts: list[LowStockAlertSchema] = []
            for stock in stocks:
                suggested_qty = await self._calculate_suggested_order_quantity(stock.productId)
                avg_daily_sales = await self._get_average_daily_sales(stock.productId)
                days_out = await self._calculate_days_until_out_of_stock(stock.productId, stock.quantity)
                last_sale = await self._get_last_sale_date(stock.productId)
                alerts.append(LowStockAlertSchema(
                    product_id=stock.productId,
                    product_name=stock.product.name,
                    product_sku=stock.product.sku,
                    current_quantity=stock.quantity,
                    reorder_level=effective_threshold,
                    suggested_order_quantity=suggested_qty,
                    days_out_of_stock=days_out,
                    last_sale_date=last_sale,
                    average_daily_sales=avg_daily_sales
                ))
            return alerts
        except Exception as e:
            logger.error(f"Error getting low stock alerts: {str(e)}")
            raise

    async def get_inventory_valuation(
        self,
        category_id: int | None = None,
        product_ids: list[int] | None = None
    ) -> list[InventoryValuationSchema]:
        """Get inventory valuation with cost and retail values."""
        try:
            where_conditions = {}
            
            if category_id is not None:
                try:
                    cat_id = int(category_id)  # type: ignore[arg-type]
                    where_conditions['product'] = {
                        'is': {'categoryId': cat_id}
                    }
                except Exception:
                    # Skip invalid category filters
                    pass
            
            if product_ids:
                where_conditions['productId'] = {'in': product_ids}
            
            stocks = await self.db.stock.find_many(
                where=where_conditions,
                include={'product': True}
            )
            
            valuations = []
            for stock in stocks:
                if stock.quantity <= 0:
                    continue
                
                total_cost = Decimal(str(stock.product.costPrice)) * Decimal(str(stock.quantity))
                total_retail = Decimal(str(stock.product.sellingPrice)) * Decimal(str(stock.quantity))
                potential_profit = total_retail - total_cost
                profit_margin = (potential_profit / total_retail * 100) if total_retail > 0 else Decimal('0')
                
                valuation = InventoryValuationSchema(
                    product_id=stock.productId,
                    product_name=stock.product.name,
                    product_sku=stock.product.sku,
                    quantity=stock.quantity,
                    unit_cost=stock.product.costPrice,
                    unit_price=stock.product.sellingPrice,
                    total_cost_value=total_cost,
                    total_retail_value=total_retail,
                    potential_profit=potential_profit,
                    profit_margin_percent=profit_margin
                )
                valuations.append(valuation)
            
            return valuations
            
        except Exception as e:
            logger.error(f"Error getting inventory valuation: {str(e)}")
            raise

    async def get_dead_stock_analysis(
        self,
        days_threshold: int = 90
    ) -> list[DeadStockAnalysisSchema]:
        """Identify dead stock items (no sales in specified days)."""
        try:
            # Get all products with stock
            stocks = await self.db.stock.find_many(
                where={'quantity': {'gt': 0}},
                include={'product': True}
            )
            
            dead_stock_items = []
            cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)
            
            for stock in stocks:
                # Check if product has recent sales
                recent_sales = await self.db.saleitem.find_many(
                    where={
                        'stockId': stock.id,
                        'sale': {
                            'createdAt': {'gte': cutoff_date}
                        }
                    },
                    include={'sale': True}
                )
                
                if len(recent_sales) == 0:  # No recent sales
                    # Get last sale date
                    last_sale = await self._get_last_sale_date(stock.productId)
                    days_since_last_sale = None
                    
                    if last_sale:
                        days_since_last_sale = (datetime.utcnow() - last_sale).days
                    
                    total_cost = Decimal(str(stock.product.costPrice)) * Decimal(str(stock.quantity))
                    
                    # Determine suggested action and priority
                    suggested_action, priority_level = self._get_dead_stock_recommendations(
                        days_since_last_sale, total_cost
                    )
                    
                    dead_stock = DeadStockAnalysisSchema(
                        product_id=stock.productId,
                        product_name=stock.product.name,
                        product_sku=stock.product.sku,
                        quantity=stock.quantity,
                        last_sale_date=last_sale,
                        days_since_last_sale=days_since_last_sale,
                        total_cost_value=total_cost,
                        suggested_action=suggested_action,
                        priority_level=priority_level
                    )
                    dead_stock_items.append(dead_stock)
            
            return dead_stock_items
            
        except Exception as e:
            logger.error(f"Error analyzing dead stock: {str(e)}")
            raise

    async def get_inventory_dashboard(self) -> InventoryDashboardSchema:
        """Get comprehensive inventory dashboard data."""
        try:
            # Get summary statistics
            total_products = await self.db.product.count()
            # Prisma Python may not support aggregate on this client; sum manually
            stock_rows = await self.db.stock.find_many()
            total_stock_quantity = sum(getattr(row, "quantity", 0) for row in stock_rows)
            
            # Get stock status counts
            stock_levels = await self.get_stock_levels()
            low_stock_count = len([s for s in stock_levels if s.stock_status == StockStatus.LOW_STOCK])
            out_of_stock_count = len([s for s in stock_levels if s.stock_status == StockStatus.OUT_OF_STOCK])
            
            # Get total inventory value
            valuations = await self.get_inventory_valuation()
            total_cost_value = sum(v.total_cost_value for v in valuations)
            total_retail_value = sum(v.total_retail_value for v in valuations)
            
            summary = {
                'total_products': total_products,
                'total_stock_items': total_stock_quantity,
                'total_inventory_cost': total_cost_value,
                'total_inventory_retail': total_retail_value,
                'low_stock_items': low_stock_count,
                'out_of_stock_items': out_of_stock_count,
                'inventory_turnover': await self._calculate_overall_turnover()
            }
            
            # Get recent data
            low_stock_alerts = await self.get_low_stock_alerts()
            dead_stock_items = await self.get_dead_stock_analysis()
            
            # Recent adjustments (last 10)
            recent_adj_rows = []
            try:
                recent_adj_rows = await self.db.stockadjustment.find_many(
                    order={'createdAt': 'desc'},
                    take=10,
                    include={'product': True}
                )
            except Exception:
                recent_adj_rows = []
            recent_adjustments: list[StockAdjustmentSchema] = []
            for r in recent_adj_rows:
                try:
                    recent_adjustments.append(StockAdjustmentSchema(
                        id=r.id,
                        product_id=r.productId,
                        product_name=r.product.name if r.product else '',
                        adjustment_type=AdjustmentType[r.adjustmentType] if r.adjustmentType in AdjustmentType.__members__ else AdjustmentType.RECOUNT,
                        quantity_before=r.quantityBefore,
                        quantity_after=r.quantityAfter,
                        adjustment_quantity=r.adjustmentQty,
                        reason=r.reason,
                        notes=r.notes,
                        reference_number=r.referenceNumber,
                        created_by=r.createdById if hasattr(r, 'createdById') else 0,
                        created_at=r.createdAt
                    ))
                except Exception:
                    continue

            dashboard = InventoryDashboardSchema(
                summary=summary,
                low_stock_alerts=low_stock_alerts[:10],  # Top 10 alerts
                recent_adjustments=recent_adjustments,
                top_selling_products=await self._get_top_selling_products(),
                dead_stock_items=dead_stock_items[:5],  # Top 5 dead stock items
                inventory_trends=await self._get_inventory_trends()
            )
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error getting inventory dashboard: {str(e)}")
            raise

    async def get_sales_timeseries(
        self,
        product_id: int,
        days: int = 14
    ) -> list[dict[str, Any]]:
        """Return daily sales quantity for a product over the past N days (inclusive).

        Sparse days (no sales) are returned with quantity 0 for consistent sparkline plotting.
        """
        try:
            cutoff = datetime.utcnow() - timedelta(days=days - 1)
            sales = await self.db.saleitem.find_many(
                where={
                    'stock': {'productId': product_id},
                    'sale': {'createdAt': {'gte': cutoff}}
                },
                include={'sale': True}
            )
            buckets: dict[str, int] = {}
            for s in sales:
                day = s.sale.createdAt.date().isoformat()
                buckets[day] = buckets.get(day, 0) + s.quantity
            out: list[dict[str, Any]] = []
            for i in range(days):
                d = (datetime.utcnow() - timedelta(days=days - 1 - i)).date().isoformat()
                out.append({'date': d, 'quantity': buckets.get(d, 0)})
            return out
        except Exception as e:
            logger.error(f"Error building sales timeseries for product {product_id}: {e}")
            return []

    # Helper methods
    def _calculate_stock_status(self, current_qty: int, reorder_level: int) -> StockStatus:
        """Determine stock status based on quantity and reorder level."""
        if current_qty == 0:
            return StockStatus.OUT_OF_STOCK
        elif current_qty <= reorder_level:
            return StockStatus.LOW_STOCK
        elif current_qty > reorder_level * 3:  # Arbitrary overstock threshold
            return StockStatus.OVERSTOCK
        else:
            return StockStatus.IN_STOCK

    async def _get_reserved_quantity(self, product_id: int) -> int:
        """Calculate reserved quantity for pending orders."""
        # This would calculate quantities in pending sales, transfers, etc.
        # For now, return 0
        return 0

    async def _calculate_days_of_stock(self, product_id: int, available_qty: int) -> int | None:
        """Calculate estimated days of stock remaining based on sales velocity."""
        avg_daily_sales = await self._get_average_daily_sales(product_id)
        
        if avg_daily_sales and avg_daily_sales > 0:
            return int(available_qty / float(avg_daily_sales))
        
        return None

    async def _get_average_daily_sales(self, product_id: int, days: int = 30) -> Decimal | None:
        """Calculate average daily sales for a product."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get sales in the last N days
            sales = await self.db.saleitem.find_many(
                where={
                    'stock': {'productId': product_id},
                    'sale': {
                        'createdAt': {'gte': cutoff_date}
                    }
                }
            )
            
            total_qty = sum(sale.quantity for sale in sales)
            return Decimal(str(total_qty / days)) if total_qty > 0 else None
            
        except Exception:
            return None

    async def _calculate_suggested_order_quantity(self, product_id: int) -> int:
        """Calculate suggested order quantity based on sales velocity."""
        avg_daily_sales = await self._get_average_daily_sales(product_id)
        lead_time_days = 7  # Default lead time
        safety_stock = 5   # Default safety stock
        
        if avg_daily_sales:
            return int(float(avg_daily_sales) * lead_time_days) + safety_stock
        
        return 20  # Default order quantity

    async def _calculate_days_until_out_of_stock(self, product_id: int, current_qty: int) -> int | None:
        """Calculate estimated days until product runs out of stock."""
        avg_daily_sales = await self._get_average_daily_sales(product_id)
        
        if avg_daily_sales and avg_daily_sales > 0:
            return max(0, int(current_qty / float(avg_daily_sales)))
        
        return None

    async def _get_last_sale_date(self, product_id: int) -> datetime | None:
        """Get the date of the last sale for a product."""
        try:
            last_sale = await self.db.saleitem.find_first(
                where={'stock': {'productId': product_id}},
                include={'sale': True},
                order={'sale': {'createdAt': 'desc'}}
            )
            
            return last_sale.sale.createdAt if last_sale else None
            
        except Exception:
            return None

    def _get_dead_stock_recommendations(
        self, 
        days_since_last_sale: int | None, 
        cost_value: Decimal
    ) -> tuple[str, str]:
        """Get recommendations for dead stock items."""
        if not days_since_last_sale:
            return "Monitor closely", "LOW"
        
        if days_since_last_sale > 365:
            if cost_value > 1000:
                return "Consider liquidation or return to supplier", "HIGH"
            else:
                return "Mark down for clearance sale", "MEDIUM"
        elif days_since_last_sale > 180:
            return "Apply discount or bundle with fast-moving items", "MEDIUM"
        else:
            return "Monitor and consider promotional pricing", "LOW"

    async def _calculate_overall_turnover(self) -> float:
        """Calculate overall inventory turnover ratio.

        Approximation: (Cost of goods sold last 30 days) / (Average inventory cost value over same period)
        We approximate COGS as sum(costPrice * quantity) from sale items within period.
        Average inventory value approximated by current valuation (no historical snapshots) – fallback to 1 to avoid div0.
        """
        try:
            period_days = 30
            cutoff = datetime.utcnow() - timedelta(days=period_days)
            # Fetch sale items with product cost
            sale_items = await self.db.saleitem.find_many(
                where={'sale': {'createdAt': {'gte': cutoff}}},
                include={'stock': {'include': {'product': True}}, 'sale': True}
            )
            cogs = 0.0
            for si in sale_items:
                cost_price = float(getattr(si.stock.product, 'costPrice', 0) or 0)
                cogs += cost_price * si.quantity
            valuations = await self.get_inventory_valuation()
            total_cost_now = float(sum(float(v.total_cost_value) for v in valuations) or 0)
            if total_cost_now <= 0:
                return 0.0
            turnover = cogs / total_cost_now
            return round(turnover, 4)
        except Exception as e:
            logger.warning(f"Turnover calc fallback due to error: {e}")
            return 0.0

    async def _get_top_selling_products(self, limit: int = 5) -> list[dict[str, Any]]:
        """Get top selling products by quantity."""
        try:
            # Get sales data for the last 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            # This is a simplified query - in practice you'd want to aggregate properly
            sales = await self.db.saleitem.find_many(
                where={
                    'sale': {
                        'createdAt': {'gte': cutoff_date}
                    }
                },
                include={
                    'stock': {
                        'include': {'product': True}
                    }
                }
            )
            
            # Group by product and sum quantities
            product_sales = {}
            for sale in sales:
                product_id = sale.stock.productId
                if product_id not in product_sales:
                    product_sales[product_id] = {
                        'product_name': sale.stock.product.name,
                        'total_quantity': 0,
                        'total_revenue': Decimal('0')
                    }
                product_sales[product_id]['total_quantity'] += sale.quantity
                product_sales[product_id]['total_revenue'] += sale.subtotal
            
            # Sort by quantity sold and take top N
            sorted_products = sorted(
                product_sales.items(),
                key=lambda x: x[1]['total_quantity'],
                reverse=True
            )
            
            return [
                {
                    'product_id': product_id,
                    'product_name': data['product_name'],
                    'quantity_sold': data['total_quantity'],
                    'revenue': float(data['total_revenue'])
                }
                for product_id, data in sorted_products[:limit]
            ]
            
        except Exception:
            return []

    async def _get_inventory_trends(self) -> dict[str, Any]:
        """Get lightweight inventory trend indicators based on last 30 vs previous 30 day windows."""
        try:
            now = datetime.utcnow()
            win = 30
            cur_start = now - timedelta(days=win)
            prev_start = now - timedelta(days=win*2)
            # Sales based stock movement proxy
            cur_sales = await self.db.saleitem.find_many(where={'sale': {'createdAt': {'gte': cur_start}}}, include={'sale': True, 'stock': {'include': {'product': True}}})
            prev_sales = await self.db.saleitem.find_many(where={'sale': {'createdAt': {'gte': prev_start, 'lt': cur_start}}}, include={'sale': True, 'stock': {'include': {'product': True}}})
            def totals(items):
                qty = sum(it.quantity for it in items)
                revenue = 0.0
                for it in items:
                    revenue += float(getattr(it, 'subtotal', 0) or 0)
                return qty, revenue
            cur_qty, cur_rev = totals(cur_sales)
            prev_qty, prev_rev = totals(prev_sales)
            qty_trend = 'flat'
            if prev_qty > 0:
                change = (cur_qty - prev_qty) / prev_qty * 100
                qty_trend = 'up' if change > 5 else 'down' if change < -5 else 'flat'
            rev_trend = 'flat'
            if prev_rev > 0:
                rchange = (cur_rev - prev_rev) / prev_rev * 100
                rev_trend = 'up' if rchange > 5 else 'down' if rchange < -5 else 'flat'
            turnover = await self._calculate_overall_turnover()
            turnover_trend = 'flat'
            # crude classification vs 1.0 baseline
            if turnover > 1.05:
                turnover_trend = 'up'
            elif turnover < 0.95:
                turnover_trend = 'down'
            return {
                'sales_quantity_trend': qty_trend,
                'sales_revenue_trend': rev_trend,
                'turnover_trend': turnover_trend,
                'period_days': win
            }
        except Exception as e:
            logger.warning(f"Trend calc fallback: {e}")
            return {'sales_quantity_trend': 'flat', 'sales_revenue_trend': 'flat', 'turnover_trend': 'flat'}


def create_inventory_service(db: Prisma) -> InventoryService:
    """Factory function to create inventory service instance."""
    return InventoryService(db)
