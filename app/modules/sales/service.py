"""
Sales service layer for business logic.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from generated.prisma import Prisma

from app.core.config import UserRole
from app.core.exceptions import (
    ValidationError, NotFoundError, InsufficientStockError, PaymentError,
    AuthorizationError, DatabaseError, BusinessRuleError
)
from app.modules.sales.model import SalesModel
from app.modules.sales.schema import (
    SaleCreateSchema, SaleUpdateSchema, SaleResponseSchema,
    SaleDetailResponseSchema, SaleListResponseSchema, SalesStatsSchema,
    RefundCreateSchema, RefundResponseSchema, ReceiptSchema,
    SaleItemResponseSchema,
    DailySalesSchema,
    SaleStatus, PaymentMethod, RefundListResponseSchema
)

logger = logging.getLogger(__name__)

class SalesService:
    """Sales service class for managing sales operations."""
    
    def __init__(self, db: Prisma):
        self.db = db
        self.sales_model = SalesModel(db)
    
    async def create_sale(
        self,
        sale_data: SaleCreateSchema,
        user_id: int
    ) -> SaleDetailResponseSchema:
        """Create a new sale."""
        try:
            # Normalize field access for alias/camelCase
            branch_id = getattr(sale_data, "branch_id", getattr(sale_data, "branchId", None))
            customer_id = getattr(sale_data, "customer_id", getattr(sale_data, "customerId", None))
            # Validate branch exists; if missing or invalid, try to infer from stock items
            branch = None
            if branch_id is not None:
                branch = await self.db.branch.find_unique(where={"id": branch_id})
            if not branch:
                # Infer from items' stock branch when possible
                branch_candidates = set()
                for item in sale_data.items or []:
                    stock_id = getattr(item, 'stock_id', None) or getattr(item, 'stockId', None)
                    if stock_id is not None:
                        st = await self.db.stock.find_unique(where={"id": int(stock_id)})
                        if st:
                            inferred_branch_id = getattr(st, "branch_id", getattr(st, "branchId", None))
                            if inferred_branch_id is not None:
                                branch_candidates.add(int(inferred_branch_id))
                if len(branch_candidates) == 1:
                    branch_id = next(iter(branch_candidates))
                    # update sale_data to keep downstream layers consistent
                    try:
                        setattr(sale_data, "branch_id", branch_id)
                    except Exception:
                        pass
                    try:
                        setattr(sale_data, "branchId", branch_id)
                    except Exception:
                        pass
                    branch = await self.db.branch.find_unique(where={"id": branch_id})
                elif len(branch_candidates) > 1:
                    raise ValidationError("Sale items belong to different branches; please split the sale by branch")
                # If still not found, attempt to use a default active branch
                if not branch:
                    default_branch = await self.db.branch.find_first(where={"isActive": True})
                    if default_branch:
                        branch_id = default_branch.id
                        try:
                            setattr(sale_data, "branch_id", branch_id)
                        except Exception:
                            pass
                        try:
                            setattr(sale_data, "branchId", branch_id)
                        except Exception:
                            pass
                        branch = default_branch
                # If still not found after fallback, raise
                if not branch:
                    raise NotFoundError("Branch not found")
            
            # Validate customer if provided
            if customer_id:
                customer = await self.db.customer.find_unique(where={"id": customer_id})
                if not customer:
                    raise NotFoundError("Customer not found")
            else:
                # For credit (UNPAID/PARTIAL) sales allow inline customer creation if details provided
                payment_type_val = getattr(sale_data, "payment_type", getattr(sale_data, "paymentType", None))
                if payment_type_val in ("UNPAID", "PARTIAL") and (
                    getattr(sale_data, "customer_name", None) or getattr(sale_data, "customer_phone", None)
                ):
                    try:
                        new_customer = await self.db.customer.create(data={
                            "name": getattr(sale_data, "customer_name", None) or "Walk-in Credit Customer",
                            "email": getattr(sale_data, "customer_email", None),
                            "phone": getattr(sale_data, "customer_phone", None),
                            "type": "INDIVIDUAL",
                            "status": "ACTIVE",
                        })
                        customer_id = new_customer.id
                        try:
                            setattr(sale_data, "customer_id", customer_id)
                            setattr(sale_data, "customerId", customer_id)
                        except Exception:
                            pass
                    except Exception:
                        # Non-fatal: proceed without customer record
                        pass
            
            # Validate all products exist and are available
            if not sale_data.items:
                raise ValidationError("Sale must contain at least one item")
            
            # Validate each item
            for item in sale_data.items:
                product_id = getattr(item, 'product_id', None) or getattr(item, 'productId', None)
                stock_id = getattr(item, 'stock_id', None) or getattr(item, 'stockId', None)
                if product_id:
                    product = await self.db.product.find_unique(where={"id": product_id})
                    if not product:
                        raise NotFoundError(f"Product {product_id} not found")
                    if not product.is_active:
                        raise ValidationError(f"Product {product.name} is inactive")
                elif stock_id:
                    # basic existence check for stock; branch validated in model layer
                    st = await self.db.stock.find_unique(where={"id": int(stock_id)})
                    if not st:
                        raise NotFoundError(f"Stock {stock_id} not found")
                else:
                    raise ValidationError("Each item must include stock_id or product_id")
                
                if item.quantity <= 0:
                    raise ValidationError("Item quantity must be greater than 0")
                
                if item.price < 0:
                    raise ValidationError("Item price must be non-negative")
            
            # Ensure payment_type attribute exists (frontend may send SPLIT treated as FULL)
            try:
                pt_val = getattr(sale_data, 'payment_type', getattr(sale_data, 'paymentType', None))
                if pt_val is None:
                    # Infer from presence of payments: if payments cover total -> FULL else UNPAID
                    single = getattr(sale_data, 'payment', None)
                    multi = getattr(sale_data, 'payments', None)
                    paid = Decimal('0')
                    if single and getattr(single, 'amount', 0) > 0:
                        paid += getattr(single, 'amount')
                    if multi:
                        for p in multi:
                            if p and getattr(p, 'amount', 0) > 0:
                                paid += getattr(p, 'amount')
                    if getattr(sale_data, 'total_amount', getattr(sale_data, 'totalAmount', None)) and paid >= getattr(sale_data, 'total_amount', getattr(sale_data, 'totalAmount')):
                        pt_val = 'FULL'
                    elif paid > 0:
                        pt_val = 'PARTIAL'
                    else:
                        pt_val = 'UNPAID'
                    try:
                        setattr(sale_data, 'payment_type', pt_val)
                        setattr(sale_data, 'paymentType', pt_val)
                    except Exception:
                        pass
                elif str(pt_val).upper() == 'SPLIT':
                    try:
                        setattr(sale_data, 'payment_type', 'FULL')
                        setattr(sale_data, 'paymentType', 'FULL')
                    except Exception:
                        pass
            except Exception:
                pass

            # Create the sale
            sale = await self.sales_model.create_sale(sale_data, user_id)
            
            # Get full sale details for response
            full_sale = await self.sales_model.get_sale(sale.id)

            return SaleDetailResponseSchema(
                id=full_sale.id,
                branch_id=getattr(full_sale, "branch_id", getattr(full_sale, "branchId", None)),
                branch_name=full_sale.branch.name if getattr(full_sale, "branch", None) else None,
                total_amount=getattr(full_sale, "total_amount", getattr(full_sale, "totalAmount", None)),
                discount=full_sale.discount,
                payment_type=getattr(full_sale, "payment_type", getattr(full_sale, "paymentType", None)),
                customer_id=getattr(full_sale, "customer_id", getattr(full_sale, "customerId", None)),
                customer_name=full_sale.customer.name if getattr(full_sale, "customer", None) else None,
                cashier_id=getattr(full_sale, "user_id", getattr(full_sale, "userId", None)),
                cashier_name=f"{getattr(full_sale.user,'firstName', getattr(full_sale.user,'first_name', ''))} {getattr(full_sale.user,'lastName', getattr(full_sale.user,'last_name', ''))}" if getattr(full_sale, "user", None) else None,
                items=[
                    {
                        "id": item.id,
                        "sale_id": full_sale.id,
                        "product_id": item.stock.product.id,
                        "product_name": item.stock.product.name,
                        "product_sku": item.stock.product.sku,
                        "quantity": item.quantity,
                        "price": item.price,
                        "subtotal": item.subtotal
                    }
                    for item in full_sale.items
                ],
                payments=[
                    {
                        "id": payment.id,
                        "amount": payment.amount,
                        "currency": payment.currency,
                        "account_name": payment.account.name if payment.account else "Unknown"
                    }
                    for payment in full_sale.payments
                ],
                status=SaleStatus.COMPLETED,
                created_at=getattr(full_sale, "created_at", getattr(full_sale, "createdAt", None)),
                updated_at=getattr(full_sale, "updated_at", getattr(full_sale, "updatedAt", None)),
                items_count=len(getattr(full_sale, "items", []) or []),
                total_quantity=sum((it.quantity for it in (getattr(full_sale, "items", []) or [])), start=0),
                paid_amount=sum((p.amount for p in getattr(full_sale, 'payments', []) or []), start=Decimal('0')),
                outstanding_amount=max(Decimal('0'), (getattr(full_sale, "total_amount", getattr(full_sale, "totalAmount", Decimal('0'))) or Decimal('0')) - sum((p.amount for p in getattr(full_sale, 'payments', []) or []), start=Decimal('0'))),
            )
            
        except ValueError as e:
            raise ValidationError(str(e))
        except (ValidationError, NotFoundError):
            # bubble up expected business errors
            raise
        except Exception as e:
            logger.error(f"Error creating sale: {str(e)}")
            raise DatabaseError(detail="Failed to create sale")
    
    async def get_sale(self, sale_id: int) -> Optional[SaleDetailResponseSchema]:
        """Get sale by ID with full details."""
        try:
            sale = await self.sales_model.get_sale(sale_id)
            if not sale:
                return None
            # Ignore soft-deleted sale
            if getattr(sale, "deleted_at", None) or getattr(sale, "deletedAt", None):
                return None
            
            return SaleDetailResponseSchema(
                id=sale.id,
                branch_id=getattr(sale, "branch_id", getattr(sale, "branchId", None)),
                branch_name=sale.branch.name if getattr(sale, "branch", None) else None,
                total_amount=getattr(sale, "total_amount", getattr(sale, "totalAmount", None)),
                discount=sale.discount,
                payment_type=getattr(sale, "payment_type", getattr(sale, "paymentType", None)),
                customer_id=getattr(sale, "customer_id", getattr(sale, "customerId", None)),
                customer_name=sale.customer.name if getattr(sale, "customer", None) else None,
                cashier_id=getattr(sale, "user_id", getattr(sale, "userId", None)),
                cashier_name=f"{getattr(sale.user,'firstName', getattr(sale.user,'first_name', ''))} {getattr(sale.user,'lastName', getattr(sale.user,'last_name', ''))}" if getattr(sale, "user", None) else None,
                items=[
                    {
                        "id": item.id,
                        "sale_id": sale.id,
                        "product_id": item.stock.product.id,
                        "product_name": item.stock.product.name,
                        "product_sku": item.stock.product.sku,
                        "quantity": item.quantity,
                        "price": item.price,
                        "subtotal": item.subtotal
                    }
                    for item in sale.items
                ],
                payments=[
                    {
                        "id": payment.id,
                        "amount": payment.amount,
                        "currency": payment.currency,
                        "account_name": payment.account.name if payment.account else "Unknown"
                    }
                    for payment in sale.payments
                ],
                status=SaleStatus.COMPLETED,
                created_at=getattr(sale, "created_at", getattr(sale, "createdAt", None)),
                updated_at=getattr(sale, "updated_at", getattr(sale, "updatedAt", None)),
                items_count=len(getattr(sale, "items", []) or []),
                total_quantity=sum((it.quantity for it in (getattr(sale, "items", []) or [])), start=0),
                paid_amount=sum((p.amount for p in getattr(sale, 'payments', []) or []), start=Decimal('0')),
                outstanding_amount=max(Decimal('0'), (getattr(sale, "total_amount", getattr(sale, "totalAmount", Decimal('0'))) or Decimal('0')) - sum((p.amount for p in getattr(sale, 'payments', []) or []), start=Decimal('0'))),
            )
            
        except Exception as e:
            logger.error(f"Error getting sale {sale_id}: {str(e)}")
            raise DatabaseError(detail="Failed to retrieve sale")
    
    async def list_sales(
        self,
        page: int = 1,
        size: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> SaleListResponseSchema:
        """Get paginated list of sales."""
        try:
            skip = (page - 1) * size
            sales, total = await self.sales_model.get_sales(skip, size, filters)
            items = []
            for sale in sales:
                schema_obj = SaleResponseSchema(
                    id=sale.id,
                    branch_id=getattr(sale, "branch_id", getattr(sale, "branchId", None)),
                    branch_name=sale.branch.name if getattr(sale, "branch", None) else None,
                    total_amount=getattr(sale, "total_amount", getattr(sale, "totalAmount", None)),
                    discount=sale.discount,
                    payment_type=getattr(sale, "payment_type", getattr(sale, "paymentType", None)),
                    customer_id=getattr(sale, "customer_id", getattr(sale, "customerId", None)),
                    customer_name=sale.customer.name if getattr(sale, "customer", None) else None,
                    cashier_id=getattr(sale, "user_id", getattr(sale, "userId", None)),
                    cashier_name=f"{getattr(sale.user,'firstName', getattr(sale.user,'first_name', ''))} {getattr(sale.user,'lastName', getattr(sale.user,'last_name', ''))}",
                    items_count=len(sale.items),
                    status=SaleStatus.COMPLETED,
                    created_at=getattr(sale, "created_at", getattr(sale, "createdAt", None)),
                    updated_at=getattr(sale, "updated_at", getattr(sale, "updatedAt", None)),
                    paid_amount=sum((p.amount for p in getattr(sale, 'payments', []) or []), start=Decimal('0')),
                    outstanding_amount=max(Decimal('0'), (getattr(sale, "total_amount", getattr(sale, "totalAmount", Decimal('0'))) or Decimal('0')) - sum((p.amount for p in getattr(sale, 'payments', []) or []), start=Decimal('0'))),
                )
                try:
                    setattr(schema_obj, 'payments', getattr(sale, 'payments', []) or [])
                except Exception:
                    pass
                items.append(schema_obj)
            
            return SaleListResponseSchema(
                sales=items,
                total=total,
                page=page,
                size=size,
                pages=((total - 1) // size) + 1 if total > 0 else 0
            )
            
        except Exception as e:
            logger.error(f"Error listing sales: {str(e)}")
            raise DatabaseError(detail="Failed to retrieve sales")
    
    async def update_sale(
        self,
        sale_id: int,
        sale_data: SaleUpdateSchema
    ) -> SaleDetailResponseSchema:
        """Update sale - limited to certain fields."""
        try:
            # Check if sale exists
            existing_sale = await self.sales_model.get_sale(sale_id)
            if not existing_sale:
                raise NotFoundError(
                    error_code="NOT_FOUND",
                    detail="Sale not found"
                )
            if getattr(existing_sale, "deleted_at", None) or getattr(existing_sale, "deletedAt", None):
                raise BusinessRuleError("Cannot update a deleted sale")
            
            # Update sale
            updated_sale = await self.sales_model.update_sale(sale_id, sale_data)
            if not updated_sale:
                raise NotFoundError(
                    error_code="NOT_FOUND",
                    detail="Sale not found"
                )
            
            # Return updated sale details
            return await self.get_sale(sale_id)
            
        except Exception as e:
            logger.error(f"Error updating sale {sale_id}: {str(e)}")
            raise DatabaseError(detail="Failed to update sale")
    
    async def create_refund(
        self,
        refund_data: RefundCreateSchema,
        user_id: int
    ) -> RefundResponseSchema:
        """Create a refund for a sale."""
        try:
            # Validate original sale exists
            original_sale = await self.sales_model.get_sale(refund_data.sale_id)
            if not original_sale:
                raise NotFoundError("Original sale not found")
            
            # Validate refund items
            if not refund_data.items:
                raise ValidationError("Refund must contain at least one item")
            
            # Create refund
            refund = await self.sales_model.create_refund(refund_data, user_id)
            
            # Get full refund details
            full_refund = await self.db.returnsale.find_unique(
                where={"id": refund.id},
                include={
                    "original": {
                        "include": {"branch": True, "user": True}
                    },
                    "items": {
                        "include": {
                            "saleItem": {
                                "include": {
                                    "stock": {"include": {"product": True}}
                                }
                            }
                        }
                    },
                    "refund": True
                }
            )
            
            total_refund = sum(getattr(item, "refund_amount", getattr(item, "refundAmount", 0)) for item in full_refund.items)
            
            return RefundResponseSchema(
                id=full_refund.id,
        original_sale_id=getattr(full_refund, "original_id", getattr(full_refund, "originalId", None)),
                branch_name=full_refund.original.branch.name,
                total_refund_amount=total_refund,
                reason=full_refund.reason,
                items=[
                    {
                        "product_name": item.sale_item.stock.product.name,
                        "quantity": item.quantity,
            "refund_amount": getattr(item, "refund_amount", getattr(item, "refundAmount", 0))
                    }
                    for item in full_refund.items
                ],
        created_at=getattr(full_refund, "created_at", getattr(full_refund, "createdAt", None))
            )
            
        except ValueError as e:
            raise ValidationError(str(e))
        except Exception as e:
            logger.error(f"Error creating refund: {str(e)}")
            raise DatabaseError(detail="Failed to create refund")
    
    async def list_refunds(
        self,
        page: int = 1,
        size: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> RefundListResponseSchema:
        """Get paginated list of refunds."""
        try:
            skip = (page - 1) * size
            refunds, total = await self.sales_model.get_refunds(skip, size, filters)
            
            items = []
            for refund in refunds:
                total_refund = sum(getattr(item, "refund_amount", getattr(item, "refundAmount", 0)) for item in refund.items)
                
                items.append(RefundResponseSchema(
                    id=refund.id,
                    original_sale_id=getattr(refund, "original_id", getattr(refund, "originalId", None)),
                    branch_name=refund.original.branch.name,
                    total_refund_amount=total_refund,
                    reason=refund.reason,
                    items=[
                        {
                            "product_name": getattr(item, "saleItem", getattr(item, "sale_item", None)).stock.product.name,
                            "quantity": item.quantity,
                            "refund_amount": getattr(item, "refund_amount", getattr(item, "refundAmount", 0))
                        }
                        for item in refund.items
                    ],
                    created_at=getattr(refund, "created_at", getattr(refund, "createdAt", None))
                ))
            
            return RefundListResponseSchema(
                items=items,
                total=total,
                page=page,
                size=size,
                pages=((total - 1) // size) + 1 if total > 0 else 0
            )
            
        except Exception as e:
            logger.error(f"Error listing refunds: {str(e)}")
            raise DatabaseError(detail="Failed to retrieve refunds")
    
    async def get_sales_stats(
        self,
        branch_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> SalesStatsSchema:
        """Get sales statistics."""
        try:
            stats = await self.sales_model.get_sales_stats(branch_id, start_date, end_date)
            
            return SalesStatsSchema(
                total_sales=stats["total_sales"],
                total_revenue=stats["total_revenue"],
                total_discount=stats["total_discount"],
                average_sale_value=stats["average_sale_value"],
                payment_method_breakdown=stats["payment_method_breakdown"]
            )
            
        except Exception as e:
            logger.error(f"Error getting sales stats: {str(e)}")
            raise DatabaseError(detail="Failed to retrieve sales statistics")

    async def soft_delete_sale(self, sale_id: int, user_id: int) -> bool:
        try:
            return await self.sales_model.soft_delete_sale(sale_id, user_id)
        except NotFoundError:
            return False
        except Exception as e:
            logger.error(f"Error in service soft_delete_sale: {e}")
            raise DatabaseError(detail="Failed to delete sale")

    async def restore_sale(self, sale_id: int) -> bool:
        try:
            return await self.sales_model.restore_sale(sale_id)
        except Exception as e:
            logger.error(f"Error restoring sale {sale_id}: {e}")
            raise DatabaseError(detail="Failed to restore sale")
    
    async def generate_receipt(
        self,
        sale_id: int
    ) -> ReceiptSchema:
        """Generate receipt for a sale."""
        try:
            sale = await self.sales_model.get_sale(sale_id)
            if not sale:
                raise NotFoundError(
                    error_code="NOT_FOUND",
                    detail="Sale not found"
                )

            # Build SaleDetailResponseSchema
            sale_detail = SaleDetailResponseSchema(
                id=sale.id,
                sale_number=str(sale.id),
                subtotal=sum(item.subtotal for item in sale.items),
                total_amount=getattr(sale, "total_amount", getattr(sale, "totalAmount", None)),
                discount=getattr(sale, "discount", Decimal('0')),
                payment_type=getattr(sale, "payment_type", getattr(sale, "paymentType", None)),
                status=SaleStatus.COMPLETED,
                branch_id=getattr(sale, "branch_id", getattr(sale, "branchId", None)),
                branch_name=sale.branch.name if getattr(sale, "branch", None) else None,
                customer_id=getattr(sale, "customer_id", getattr(sale, "customerId", None)),
                customer_name=(sale.customer.name if getattr(sale, "customer", None) else None),
                cashier_id=getattr(sale, "user_id", getattr(sale, "userId", None)),
                cashier_name=(f"{getattr(sale.user,'firstName', getattr(sale.user,'first_name', ''))} {getattr(sale.user,'lastName', getattr(sale.user,'last_name', ''))}" if getattr(sale, "user", None) else None),
                created_at=getattr(sale, "created_at", getattr(sale, "createdAt", None)),
                updated_at=getattr(sale, "updated_at", getattr(sale, "updatedAt", None)),
                items=[
                    SaleItemResponseSchema(
                        id=i.id,
                        sale_id=sale.id,
                        product_name=i.stock.product.name,
                        product_sku=i.stock.product.sku,
                        stock_id=(getattr(i, "stock_id", getattr(i, "stockId", None))),
                        quantity=i.quantity,
                        price=i.price,
                        subtotal=i.subtotal,
                    )
                    for i in sale.items
                ],
                items_count=len(sale.items),
                total_quantity=sum(i.quantity for i in sale.items),
            )

            from app.core.config import settings as app_settings
            company_info = {
                "name": app_settings.company_name,
                "email": app_settings.company_email,
                "phone": app_settings.company_phone,
                "address": app_settings.company_address,
            }

            return ReceiptSchema(
                sale=sale_detail,
                company_info=company_info,
                receipt_number=f"RCPT-{sale.id}",
                qr_code=None,
            )
            
        except Exception as e:
            logger.error(f"Error generating receipt for sale {sale_id}: {str(e)}")
            raise NotFoundError(
                error_code="DATABASE_ERROR",
                detail="Failed to generate receipt"
            )

    async def get_daily_sales_report(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        branch_id: Optional[int] = None,
    ) -> List[DailySalesSchema]:
        """Compute a daily sales report grouped by day with totals and item counts."""
        try:
            # Default to today if no range provided
            if not start_date and not end_date:
                start_date = date.today()
                end_date = date.today()
            elif start_date and not end_date:
                end_date = start_date
            elif end_date and not start_date:
                start_date = end_date

            where_conditions: Dict[str, Any] = {}
            if branch_id:
                where_conditions["branch_id"] = branch_id
            if start_date and end_date:
                where_conditions["created_at"] = {
                    "gte": datetime.combine(start_date, datetime.min.time()),
                    "lte": datetime.combine(end_date, datetime.max.time()),
                }

            # Exclude soft-deleted from daily report
            sales = await self.db.sale.find_many(
                where={**where_conditions, "deletedAt": None},
                include={
                    "items": True,
                },
                order={"createdAt": "asc"}
            )

            # Group in Python
            by_day: Dict[date, Dict[str, Any]] = {}
            for s in sales:
                created = getattr(s, "created_at", getattr(s, "createdAt", None))
                d = created.date() if hasattr(created, 'date') else created
                if d not in by_day:
                    by_day[d] = {
                        "total_sales": 0,
                        "total_revenue": Decimal('0'),
                        "total_items": 0,
                    }
                by_day[d]["total_sales"] += 1
                by_day[d]["total_revenue"] += getattr(s, "total_amount", getattr(s, "totalAmount", Decimal('0')))
                by_day[d]["total_items"] += sum(item.quantity for item in s.items or [])

            # Build schema list sorted by date
            results: List[DailySalesSchema] = []
            for d in sorted(by_day.keys()):
                agg = by_day[d]
                results.append(
                    DailySalesSchema(
                        date=datetime.combine(d, datetime.min.time()),
                        total_sales=agg["total_sales"],
                        total_revenue=agg["total_revenue"],
                        total_items=agg["total_items"],
                    )
                )
            return results
        except Exception as e:
            logger.error(f"Error computing daily sales report: {str(e)}")
            raise DatabaseError(detail="Failed to compute daily sales report")

# Service factory function
def create_sales_service(db: Prisma) -> SalesService:
    """Create sales service instance."""
    return SalesService(db)
