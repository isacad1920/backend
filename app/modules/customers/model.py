"""
Customer database model for POS system.
"""
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from generated.prisma import Prisma
from app.modules.customers.schema import (
    CustomerCreateSchema,
    CustomerUpdateSchema,
    CustomerStatus,
    CustomerType
)

logger = logging.getLogger(__name__)

class CustomerModel:
    """Customer model for database operations."""
    
    def __init__(self, db: Prisma):
        """Initialize customer model with database client.
        
        Args:
            db: Prisma database client
        """
        self.db = db
    
    def _convert_customer_fields(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert camelCase Prisma fields to snake_case for Pydantic schemas.
        
        Args:
            customer_data: Raw customer data from Prisma
            
        Returns:
            Converted customer data with snake_case fields
        """
        if not customer_data:
            return customer_data
        
        # Create a copy to avoid modifying original data
        converted = customer_data.copy()
        
        # Convert camelCase to snake_case field mappings
        field_mappings = {
            'createdAt': 'created_at',
            'updatedAt': 'updated_at',
            'creditLimit': 'credit_limit',
            'totalPurchases': 'total_purchases',
            'lastPurchaseDate': 'last_purchase_date'
        }
        
        for camel_case, snake_case in field_mappings.items():
            if camel_case in converted:
                converted[snake_case] = converted[camel_case]
                del converted[camel_case]
        
        return converted
    
    async def create_customer(self, customer_data: CustomerCreateSchema) -> Dict[str, Any]:
        """Create a new customer.
        
        Args:
            customer_data: Customer data to create
            
        Returns:
            Created customer data
            
        Raises:
            Exception: If customer creation fails
        """
        try:
            customer = await self.db.customer.create(
                data={
                    'name': customer_data.name,
                    'email': customer_data.email,
                    'phone': customer_data.phone,
                    'address': customer_data.address,
                    'type': customer_data.type,
                    'creditLimit': float(customer_data.credit_limit) if customer_data.credit_limit else 0.0,
                    'balance': 0.0,
                    'totalPurchases': 0.0,
                    'status': CustomerStatus.ACTIVE,
                    'notes': customer_data.notes,
                }
            )
            
            logger.info(f"Customer created successfully: {customer.id}")
            return self._convert_customer_fields(customer.model_dump())
            
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            raise Exception(f"Failed to create customer: {str(e)}")
    
    async def get_customer_by_id(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get customer by ID with detailed information.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Customer data with statistics or None if not found
        """
        try:
            customer = await self.db.customer.find_unique(
                where={'id': customer_id},
                include={
                    'Sale': {
                        'include': {
                            'branch': True,
                            'items': True
                        }
                    }
                }
            )
            
            if not customer:
                return None
            
            # Calculate additional statistics
            customer_dict = self._convert_customer_fields(customer.model_dump())
            
            # Calculate purchase statistics
            purchase_count = len(customer.Sale) if customer.Sale else 0
            total_purchases = sum(sale.totalAmount for sale in customer.Sale) if customer.Sale else 0
            average_purchase = sum(
                sale.totalAmount for sale in customer.Sale 
                if sale.totalAmount > 0
            ) / len([sale for sale in customer.Sale if sale.totalAmount > 0]
            ) if customer.Sale else 0
            
            # Calculate last 30 days purchases
            thirty_days_ago = datetime.now() - timedelta(days=30)
            last_30_days_purchases = sum(
                sale.totalAmount for sale in customer.Sale 
                if sale.createdAt >= thirty_days_ago
            ) if customer.Sale else 0
            
            # Get last purchase date
            last_purchase_date = max(
                (sale.createdAt for sale in customer.Sale), 
                default=None
            ) if customer.Sale else None
            
            customer_dict.update({
                'purchase_count': purchase_count,
                'average_purchase': Decimal(str(average_purchase)),
                'last_30_days_purchases': Decimal(str(last_30_days_purchases)),
                'last_purchase_date': last_purchase_date,
                'total_purchases': Decimal(str(total_purchases)),
                'balance': Decimal(str(customer.balance)),
                'credit_limit': Decimal(str(customer.creditLimit))
            })
            
            return customer_dict
            
        except Exception as e:
            logger.error(f"Error getting customer {customer_id}: {str(e)}")
            raise Exception(f"Failed to get customer: {str(e)}")
    
    async def get_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get customer by email.
        
        Args:
            email: Customer email
            
        Returns:
            Customer data or None if not found
        """
        try:
            customer = await self.db.customer.find_unique(
                where={'email': email}
            )
            
            return self._convert_customer_fields(customer.model_dump()) if customer else None
            
        except Exception as e:
            logger.error(f"Error getting customer by email {email}: {str(e)}")
            raise Exception(f"Failed to get customer by email: {str(e)}")
    
    async def get_customer_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Get customer by phone number.
        
        Args:
            phone: Customer phone number
            
        Returns:
            Customer data or None if not found
        """
        try:
            customer = await self.db.customer.find_unique(
                where={'phone': phone}
            )
            
            return self._convert_customer_fields(customer.model_dump()) if customer else None
            
        except Exception as e:
            logger.error(f"Error getting customer by phone {phone}: {str(e)}")
            raise Exception(f"Failed to get customer by phone: {str(e)}")
    
    async def get_customers(
        self, 
        skip: int = 0, 
        limit: int = 10,
        status: Optional[CustomerStatus] = None,
        customer_type: Optional[CustomerType] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get paginated list of customers with filtering.
        
        Args:
            skip: Number of customers to skip
            limit: Maximum number of customers to return
            status: Filter by customer status
            customer_type: Filter by customer type
            search: Search term for name, email, or phone
            
        Returns:
            Tuple of (customers list, total count)
        """
        try:
            # Build where clause
            where_clause = {}
            
            if status:
                where_clause['status'] = status
                
            if customer_type:
                where_clause['type'] = customer_type
            
            if search:
                where_clause['OR'] = [
                    {'name': {'contains': search, 'mode': 'insensitive'}},
                    {'email': {'contains': search, 'mode': 'insensitive'}},
                    {'phone': {'contains': search, 'mode': 'insensitive'}}
                ]
            
            # Get total count
            total = await self.db.customer.count(where=where_clause)
            
            # Get customers
            customers = await self.db.customer.find_many(
                where=where_clause,
                skip=skip,
                take=limit,
                order={'createdAt': 'desc'}
            )
            
            # Process customers to add computed fields
            result_customers = []
            for customer in customers:
                customer_dict = self._convert_customer_fields(customer.model_dump())
                
                # Get last purchase date from sales
                last_sale = await self.db.sale.find_first(
                    where={'customerId': customer.id},
                    order={'createdAt': 'desc'}
                )
                last_purchase_date = last_sale.createdAt if last_sale else None
                
                customer_dict.update({
                    'last_purchase_date': last_purchase_date,
                    'balance': Decimal(str(customer.balance)),
                    'credit_limit': Decimal(str(customer.creditLimit)),
                    'total_purchases': Decimal(str(customer.totalPurchases))
                })
                
                result_customers.append(customer_dict)
            
            return result_customers, total
            
        except Exception as e:
            logger.error(f"Error getting customers: {str(e)}")
            raise Exception(f"Failed to get customers: {str(e)}")
    
    async def update_customer(self, customer_id: int, update_data: CustomerUpdateSchema) -> Optional[Dict[str, Any]]:
        """Update customer information.
        
        Args:
            customer_id: Customer ID to update
            update_data: Data to update
            
        Returns:
            Updated customer data or None if not found
        """
        try:
            # Build update data, excluding None values
            update_dict = {}
            
            if update_data.name is not None:
                update_dict['name'] = update_data.name
            if update_data.email is not None:
                update_dict['email'] = update_data.email
            if update_data.phone is not None:
                update_dict['phone'] = update_data.phone
            if update_data.address is not None:
                update_dict['address'] = update_data.address
            if update_data.type is not None:
                update_dict['type'] = update_data.type
            if update_data.credit_limit is not None:
                update_dict['creditLimit'] = float(update_data.credit_limit)
            if update_data.status is not None:
                update_dict['status'] = update_data.status
            if update_data.notes is not None:
                update_dict['notes'] = update_data.notes
            
            if not update_dict:
                # No data to update
                return await self.get_customer_by_id(customer_id)
            
            customer = await self.db.customer.update(
                where={'id': customer_id},
                data=update_dict
            )
            
            logger.info(f"Customer updated successfully: {customer_id}")
            return self._convert_customer_fields(customer.model_dump())
            
        except Exception as e:
            logger.error(f"Error updating customer {customer_id}: {str(e)}")
            if "Record to update not found" in str(e):
                return None
            raise Exception(f"Failed to update customer: {str(e)}")
    
    async def delete_customer(self, customer_id: int) -> bool:
        """Delete a customer.
        
        Args:
            customer_id: Customer ID to delete
            
        Returns:
            True if deleted successfully, False if not found
        """
        try:
            # Verify the customer exists before attempting delete to avoid treating missing as success
            existing = await self.db.customer.find_unique(where={'id': customer_id})
            if not existing:
                return False
            await self.db.customer.delete(
                where={'id': customer_id}
            )
            
            logger.info(f"Customer deleted successfully: {customer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting customer {customer_id}: {str(e)}")
            if "Record to delete does not exist" in str(e):
                return False
            raise Exception(f"Failed to delete customer: {str(e)}")
    
    async def update_customer_balance(self, customer_id: int, amount_change: Decimal) -> bool:
        """Update customer balance.
        
        Args:
            customer_id: Customer ID
            amount_change: Amount to add/subtract from balance (positive to increase, negative to decrease)
            
        Returns:
            True if updated successfully
        """
        try:
            await self.db.customer.update(
                where={'id': customer_id},
                data={
                    'balance': {
                        'increment': float(amount_change)
                    }
                }
            )
            
            logger.info(f"Customer balance updated: {customer_id}, change: {amount_change}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating customer balance {customer_id}: {str(e)}")
            raise Exception(f"Failed to update customer balance: {str(e)}")
    
    async def update_customer_purchases(self, customer_id: int, purchase_amount: Decimal) -> bool:
        """Update customer total purchases.
        
        Args:
            customer_id: Customer ID
            purchase_amount: Purchase amount to add to total
            
        Returns:
            True if updated successfully
        """
        try:
            await self.db.customer.update(
                where={'id': customer_id},
                data={
                    'totalPurchases': {
                        'increment': float(purchase_amount)
                    }
                }
            )
            
            logger.info(f"Customer purchases updated: {customer_id}, amount: {purchase_amount}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating customer purchases {customer_id}: {str(e)}")
            raise Exception(f"Failed to update customer purchases: {str(e)}")
    
    async def get_customer_purchase_history(
        self, 
        customer_id: int, 
        skip: int = 0, 
        limit: int = 10
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get customer purchase history.
        
        Args:
            customer_id: Customer ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (purchase history list, total count)
        """
        try:
            # Get total count
            total = await self.db.sale.count(where={'customerId': customer_id})
            
            # Get sales
            sales = await self.db.sale.find_many(
                where={'customerId': customer_id},
                skip=skip,
                take=limit,
                order={'createdAt': 'desc'},
                include={
                    'branch': True,
                    'items': True
                }
            )
            
            # Process sales data
            purchase_history = []
            for sale in sales:
                purchase_data = {
                    'sale_id': sale.id,
                    'total_amount': Decimal(str(sale.totalAmount)),
                    'items_count': len(sale.items) if sale.items else 0,
                    'purchase_date': sale.createdAt,
                    'branch_name': sale.branch.name if sale.branch else 'Unknown'
                }
                purchase_history.append(purchase_data)
            
            return purchase_history, total
            
        except Exception as e:
            logger.error(f"Error getting customer purchase history {customer_id}: {str(e)}")
            raise Exception(f"Failed to get customer purchase history: {str(e)}")
    
    async def get_customer_statistics(self) -> Dict[str, Any]:
        """Get customer statistics.
        
        Returns:
            Dictionary with various customer statistics
        """
        try:
            # Get basic counts
            total_customers = await self.db.customer.count()
            active_customers = await self.db.customer.count(where={'status': CustomerStatus.ACTIVE})
            inactive_customers = await self.db.customer.count(where={'status': CustomerStatus.INACTIVE})
            business_customers = await self.db.customer.count(where={'type': CustomerType.COMPANY})
            individual_customers = await self.db.customer.count(where={'type': CustomerType.INDIVIDUAL})
            
            # Get all customer data without select parameter (Prisma version compatibility)
            all_customers = await self.db.customer.find_many()
            
            # Calculate statistics manually from the data
            customers_with_credit = len([c for c in all_customers if c.creditLimit and float(c.creditLimit) > 0])
            
            # Calculate aggregate values manually
            # Calculate aggregate values manually
            active_customers_list = [c for c in all_customers if c.status == 'ACTIVE']
            total_customer_balance = sum(float(c.balance or 0) for c in active_customers_list)
            
            total_purchases = sum(float(c.totalPurchases or 0) for c in all_customers)
            average_purchase_per_customer = total_purchases / len(all_customers) if all_customers else 0
            
            # Get top customers (sorted by total_purchases)
            top_customers_sorted = sorted(all_customers, key=lambda x: float(x.totalPurchases or 0), reverse=True)[:10]
            top_customers = [
                {
                    'id': customer.id,
                    'name': customer.name,
                    'total_purchases': float(customer.totalPurchases or 0),
                    'type': customer.type
                }
                for customer in top_customers_sorted
            ]
            
            return {
                'total_customers': total_customers,
                'active_customers': active_customers,
                'inactive_customers': inactive_customers,
                'business_customers': business_customers,
                'individual_customers': individual_customers,
                'customers_with_credit': customers_with_credit,
                'total_customer_balance': float(total_customer_balance),
                'average_purchase_per_customer': float(average_purchase_per_customer),
                'top_customers': top_customers
            }
            
        except Exception as e:
            logger.error(f"Error getting customer statistics: {str(e)}")
            raise Exception(f"Failed to get customer statistics: {str(e)}")
    
    async def bulk_update_customers(self, customer_ids: List[int], update_data: CustomerUpdateSchema) -> Dict[str, Any]:
        """Bulk update multiple customers.
        
        Args:
            customer_ids: List of customer IDs to update
            update_data: Data to update
            
        Returns:
            Dictionary with operation results
        """
        try:
            # Build update data, excluding None values
            update_dict = {}
            
            if update_data.name is not None:
                update_dict['name'] = update_data.name
            if update_data.email is not None:
                update_dict['email'] = update_data.email
            if update_data.phone is not None:
                update_dict['phone'] = update_data.phone
            if update_data.address is not None:
                update_dict['address'] = update_data.address
            if update_data.type is not None:
                update_dict['type'] = update_data.type
            if update_data.credit_limit is not None:
                update_dict['creditLimit'] = float(update_data.credit_limit)
            if update_data.status is not None:
                update_dict['status'] = update_data.status
            if update_data.notes is not None:
                update_dict['notes'] = update_data.notes
            
            if not update_dict:
                return {
                    'success_count': 0,
                    'failure_count': 0,
                    'total_count': len(customer_ids),
                    'errors': [{'error': 'No data provided for update'}]
                }
            
            # Perform bulk update
            result = await self.db.customer.update_many(
                where={'id': {'in': customer_ids}},
                data=update_dict
            )
            
            success_count = result.count
            failure_count = len(customer_ids) - success_count
            
            logger.info(f"Bulk customer update completed: {success_count} successful, {failure_count} failed")
            
            return {
                'success_count': success_count,
                'failure_count': failure_count,
                'total_count': len(customer_ids),
                'errors': []
            }
            
        except Exception as e:
            logger.error(f"Error in bulk customer update: {str(e)}")
            return {
                'success_count': 0,
                'failure_count': len(customer_ids),
                'total_count': len(customer_ids),
                'errors': [{'error': str(e)}]
            }
    
    async def bulk_update_customer_status(self, customer_ids: List[int], status: CustomerStatus) -> Dict[str, Any]:
        """Bulk update customer status.
        
        Args:
            customer_ids: List of customer IDs to update
            status: New status for all customers
            
        Returns:
            Dictionary with operation results
        """
        try:
            # Perform bulk status update
            result = await self.db.customer.update_many(
                where={'id': {'in': customer_ids}},
                data={'status': status}
            )
            
            success_count = result.count
            failure_count = len(customer_ids) - success_count
            
            logger.info(f"Bulk customer status update completed: {success_count} successful, {failure_count} failed")
            
            return {
                'success_count': success_count,
                'failure_count': failure_count,
                'total_count': len(customer_ids),
                'errors': []
            }
            
        except Exception as e:
            logger.error(f"Error in bulk customer status update: {str(e)}")
            return {
                'success_count': 0,
                'failure_count': len(customer_ids),
                'total_count': len(customer_ids),
                'errors': [{'error': str(e)}]
            }
