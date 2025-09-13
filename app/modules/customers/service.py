"""
Customer business logic service.
"""
import logging
from decimal import Decimal
from typing import Any

from app.modules.customers.model import CustomerModel
from app.modules.customers.schema import (
    BulkOperationResponseSchema,
    CustomerCreateSchema,
    CustomerDetailResponseSchema,
    CustomerListResponseSchema,
    CustomerPurchaseHistoryListSchema,
    CustomerPurchaseHistorySchema,
    CustomerResponseSchema,
    CustomerStatsSchema,
    CustomerStatus,
    CustomerType,
    CustomerUpdateSchema,
)

logger = logging.getLogger(__name__)

class CustomerService:
    """Customer service for business logic operations."""
    
    def __init__(self, customer_model: CustomerModel):
        """Initialize customer service.
        
        Args:
            customer_model: Customer model instance
        """
        self.customer_model = customer_model
    
    async def create_customer(self, customer_data: CustomerCreateSchema, current_user: dict[str, Any]) -> CustomerResponseSchema:
        """Create a new customer.
        
        Args:
            customer_data: Customer data to create
            current_user: Current authenticated user
            
        Returns:
            Created customer data
            
        Raises:
            ValueError: If customer data is invalid
            Exception: If customer creation fails
        """
        try:
            # Check permissions
            if not self._check_customer_permission(current_user, 'create'):
                raise ValueError("Insufficient permissions to create customers")
            
            # Validate unique email if provided
            if customer_data.email:
                existing_customer = await self.customer_model.get_customer_by_email(customer_data.email)
                if existing_customer:
                    raise ValueError(f"Customer with email {customer_data.email} already exists")
            
            # Validate unique phone if provided
            if customer_data.phone:
                existing_customer = await self.customer_model.get_customer_by_phone(customer_data.phone)
                if existing_customer:
                    raise ValueError(f"Customer with phone {customer_data.phone} already exists")
            
            # Create customer
            customer = await self.customer_model.create_customer(customer_data)
            
            logger.info(f"Customer created by user {getattr(current_user, 'id', 'unknown')}: {customer['id']}")
            return CustomerResponseSchema.model_validate(customer)
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            raise Exception(f"Failed to create customer: {str(e)}")
    
    async def get_customer(self, customer_id: int, current_user: dict[str, Any]) -> CustomerDetailResponseSchema | None:
        """Get customer by ID with detailed information.
        
        Args:
            customer_id: Customer ID
            current_user: Current authenticated user
            
        Returns:
            Customer data with details or None if not found
        """
        try:
            # Check permissions
            if not self._check_customer_permission(current_user, 'read'):
                raise ValueError("Insufficient permissions to view customers")
            
            customer = await self.customer_model.get_customer_by_id(customer_id)
            
            if not customer:
                return None
            
            return CustomerDetailResponseSchema.model_validate(customer)
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error getting customer {customer_id}: {str(e)}")
            raise Exception(f"Failed to get customer: {str(e)}")
    
    async def get_customers(
        self, 
        page: int = 1, 
        size: int = 10,
        status: CustomerStatus | None = None,
        customer_type: CustomerType | None = None,
        search: str | None = None,
        current_user: dict[str, Any] = None
    ) -> CustomerListResponseSchema:
        """Get paginated list of customers with filtering.
        
        Args:
            page: Page number (1-based)
            size: Page size
            status: Filter by customer status
            customer_type: Filter by customer type
            search: Search term
            current_user: Current authenticated user
            
        Returns:
            Paginated customer list
        """
        try:
            # Check permissions
            if not self._check_customer_permission(current_user, 'read'):
                raise ValueError("Insufficient permissions to view customers")
            
            # Validate pagination parameters
            if page < 1:
                raise ValueError("Page number must be greater than 0")
            if size < 1 or size > 100:
                raise ValueError("Page size must be between 1 and 100")
            
            skip = (page - 1) * size
            
            customers, total = await self.customer_model.get_customers(
                skip=skip,
                limit=size,
                status=status,
                customer_type=customer_type,
                search=search
            )
            
            # Convert to response schema
            customer_items = [CustomerResponseSchema.model_validate(customer) for customer in customers]
            
            pages = (total + size - 1) // size  # Ceiling division
            
            return CustomerListResponseSchema(
                items=customer_items,
                total=total,
                page=page,
                size=size,
                pages=pages
            )
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error getting customers: {str(e)}")
            raise Exception(f"Failed to get customers: {str(e)}")
    
    async def update_customer(
        self, 
        customer_id: int, 
        customer_data: CustomerUpdateSchema, 
        current_user: dict[str, Any]
    ) -> CustomerResponseSchema | None:
        """Update customer information.
        
        Args:
            customer_id: Customer ID to update
            update_data: Data to update
            current_user: Current authenticated user
            
        Returns:
            Updated customer data or None if not found
        """
        try:
            # Check permissions
            if not self._check_customer_permission(current_user, 'update'):
                raise ValueError("Insufficient permissions to update customers")
            
            # Validate unique email if being updated
            if customer_data.email:
                existing_customer = await self.customer_model.get_customer_by_email(customer_data.email)
                if existing_customer and existing_customer['id'] != customer_id:
                    raise ValueError(f"Customer with email {customer_data.email} already exists")
            
            # Validate unique phone if being updated
            if customer_data.phone:
                existing_customer = await self.customer_model.get_customer_by_phone(customer_data.phone)
                if existing_customer and existing_customer['id'] != customer_id:
                    raise ValueError(f"Customer with phone {customer_data.phone} already exists")
            
            customer = await self.customer_model.update_customer(customer_id, customer_data)
            
            if not customer:
                return None
            
            logger.info(f"Customer updated by user {getattr(current_user, 'id', 'unknown')}: {customer_id}")
            return CustomerResponseSchema.model_validate(customer)
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating customer {customer_id}: {str(e)}")
            raise Exception(f"Failed to update customer: {str(e)}")
    
    async def delete_customer(self, customer_id: int, current_user: dict[str, Any]) -> bool:
        """Delete a customer.
        
        Args:
            customer_id: Customer ID to delete
            current_user: Current authenticated user
            
        Returns:
            True if deleted successfully, False if not found
        """
        try:
            # Check permissions
            if not self._check_customer_permission(current_user, 'delete'):
                raise ValueError("Insufficient permissions to delete customers")
            
            # Check if customer has outstanding balance
            customer = await self.customer_model.get_customer_by_id(customer_id)
            if customer and customer['balance'] != 0:
                raise ValueError("Cannot delete customer with outstanding balance")
            
            result = await self.customer_model.delete_customer(customer_id)
            
            if result:
                logger.info(f"Customer deleted by user {getattr(current_user, 'id', 'unknown')}: {customer_id}")
            
            return result
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error deleting customer {customer_id}: {str(e)}")
            raise Exception(f"Failed to delete customer: {str(e)}")
    
    async def get_customer_purchase_history(
        self,
        customer_id: int,
        page: int = 1,
        size: int = 10,
        current_user: dict[str, Any] = None
    ) -> CustomerPurchaseHistoryListSchema:
        """Get customer purchase history.
        
        Args:
            customer_id: Customer ID
            page: Page number (1-based)
            size: Page size
            current_user: Current authenticated user
            
        Returns:
            Paginated purchase history
        """
        try:
            # Check permissions
            if not self._check_customer_permission(current_user, 'read'):
                raise ValueError("Insufficient permissions to view customer purchase history")
            
            # Validate customer exists
            customer = await self.customer_model.get_customer_by_id(customer_id)
            if not customer:
                raise ValueError("Customer not found")
            
            # Validate pagination parameters
            if page < 1:
                raise ValueError("Page number must be greater than 0")
            if size < 1 or size > 100:
                raise ValueError("Page size must be between 1 and 100")
            
            skip = (page - 1) * size
            
            history, total = await self.customer_model.get_customer_purchase_history(
                customer_id, skip, size
            )
            
            # Convert to response schema
            history_items = [CustomerPurchaseHistorySchema.model_validate(item) for item in history]
            
            pages = (total + size - 1) // size  # Ceiling division
            
            return CustomerPurchaseHistoryListSchema(
                items=history_items,
                total=total,
                page=page,
                size=size,
                pages=pages
            )
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error getting customer purchase history {customer_id}: {str(e)}")
            raise Exception(f"Failed to get customer purchase history: {str(e)}")
    
    async def get_customer_statistics(self, current_user: dict[str, Any]) -> CustomerStatsSchema:
        """Get customer statistics.
        
        Args:
            current_user: Current authenticated user
            
        Returns:
            Customer statistics
        """
        try:
            # Check permissions
            if not self._check_customer_permission(current_user, 'read'):
                raise ValueError("Insufficient permissions to view customer statistics")
            
            stats = await self.customer_model.get_customer_statistics()
            
            return CustomerStatsSchema.model_validate(stats)
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error getting customer statistics: {str(e)}")
            raise Exception(f"Failed to get customer statistics: {str(e)}")
    
    async def bulk_update_customers(
        self,
        customer_ids: list[int],
    update_data: CustomerUpdateSchema,
        current_user: dict[str, Any]
    ) -> BulkOperationResponseSchema:
        """Bulk update multiple customers.
        
        Args:
            customer_ids: List of customer IDs to update
            update_data: Data to update
            current_user: Current authenticated user
            
        Returns:
            Bulk operation results
        """
        try:
            # Check permissions
            if not self._check_customer_permission(current_user, 'update'):
                raise ValueError("Insufficient permissions to bulk update customers")
            
            # Validate input
            if not customer_ids:
                raise ValueError("No customer IDs provided")
            
            if len(customer_ids) > 100:
                raise ValueError("Cannot update more than 100 customers at once")
            
            # Perform bulk update
            result = await self.customer_model.bulk_update_customers(customer_ids, update_data)
            
            logger.info(f"Bulk customer update by user {current_user['id']}: {result['success_count']} successful")
            
            return BulkOperationResponseSchema.model_validate(result)
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error in bulk customer update: {str(e)}")
            raise Exception(f"Failed to bulk update customers: {str(e)}")
    
    async def bulk_update_customer_status(
        self,
        customer_ids: list[int],
        status: CustomerStatus,
        current_user: dict[str, Any]
    ) -> BulkOperationResponseSchema:
        """Bulk update customer status.
        
        Args:
            customer_ids: List of customer IDs to update
            status: New status for all customers
            current_user: Current authenticated user
            
        Returns:
            Bulk operation results
        """
        try:
            # Check permissions
            if not self._check_customer_permission(current_user, 'update'):
                raise ValueError("Insufficient permissions to bulk update customer status")
            
            # Validate input
            if not customer_ids:
                raise ValueError("No customer IDs provided")
            
            if len(customer_ids) > 100:
                raise ValueError("Cannot update more than 100 customers at once")
            
            # Perform bulk status update
            result = await self.customer_model.bulk_update_customer_status(customer_ids, status)
            
            logger.info(f"Bulk customer status update by user {current_user['id']}: {result['success_count']} successful")
            
            return BulkOperationResponseSchema.model_validate(result)
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error in bulk customer status update: {str(e)}")
            raise Exception(f"Failed to bulk update customer status: {str(e)}")
    
    async def update_customer_balance(
        self,
        customer_id: int,
        amount_change: Decimal,
        current_user: dict[str, Any]
    ) -> bool:
        """Update customer balance (for payments, credits, etc.).
        
        Args:
            customer_id: Customer ID
            amount_change: Amount to add/subtract from balance
            current_user: Current authenticated user
            
        Returns:
            True if updated successfully
        """
        try:
            # Check permissions
            if not self._check_customer_permission(current_user, 'update'):
                raise ValueError("Insufficient permissions to update customer balance")
            
            # Validate customer exists
            customer = await self.customer_model.get_customer_by_id(customer_id)
            if not customer:
                raise ValueError("Customer not found")
            
            # Check if new balance would be negative (if we're decreasing)
            if amount_change < 0:
                current_balance = Decimal(str(customer['balance']))
                new_balance = current_balance + amount_change
                if new_balance < 0:
                    raise ValueError("Insufficient customer balance for this operation")
            
            result = await self.customer_model.update_customer_balance(customer_id, amount_change)
            
            logger.info(f"Customer balance updated by user {current_user['id']}: {customer_id}, change: {amount_change}")
            
            return result
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating customer balance {customer_id}: {str(e)}")
            raise Exception(f"Failed to update customer balance: {str(e)}")
    
    async def process_customer_purchase(
        self,
        customer_id: int,
        purchase_amount: Decimal,
        current_user: dict[str, Any]
    ) -> bool:
        """Process a customer purchase (update balances and totals).
        
        Args:
            customer_id: Customer ID
            purchase_amount: Purchase amount
            current_user: Current authenticated user
            
        Returns:
            True if processed successfully
        """
        try:
            # Check permissions
            if not self._check_customer_permission(current_user, 'update'):
                raise ValueError("Insufficient permissions to process customer purchase")
            
            # Validate customer exists
            customer = await self.customer_model.get_customer_by_id(customer_id)
            if not customer:
                raise ValueError("Customer not found")
            
            # Update total purchases
            await self.customer_model.update_customer_purchases(customer_id, purchase_amount)
            
            logger.info(f"Customer purchase processed by user {current_user['id']}: {customer_id}, amount: {purchase_amount}")
            
            return True
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error processing customer purchase {customer_id}: {str(e)}")
            raise Exception(f"Failed to process customer purchase: {str(e)}")
    
    async def validate_customer_credit_limit(self, customer_id: int, additional_amount: Decimal) -> bool:
        """Validate if customer can make a purchase within credit limit.
        
        Args:
            customer_id: Customer ID
            additional_amount: Additional amount to check against credit limit
            
        Returns:
            True if within credit limit, False otherwise
        """
        try:
            customer = await self.customer_model.get_customer_by_id(customer_id)
            if not customer:
                return False
            
            current_balance = Decimal(str(customer['balance']))
            credit_limit = Decimal(str(customer['credit_limit']))
            
            # Check if new balance would exceed credit limit
            new_balance = current_balance + additional_amount
            
            return new_balance <= credit_limit
            
        except Exception as e:
            logger.error(f"Error validating customer credit limit {customer_id}: {str(e)}")
            return False
    
    def _check_customer_permission(self, user, action: str) -> bool:
        """Check if user has permission for customer action.
        
        Args:
            user: User object (from database or dict)
            action: Action to check permission for
            
        Returns:
            True if user has permission
        """
        if not user:
            return False
        
        # Handle both User model and dict
        if hasattr(user, 'role'):
            user_role = user.role.upper() if user.role else ''
        elif isinstance(user, dict):
            user_role = user.get('role', '').upper()
        else:
            return False
        
        # Define permissions by role
        permissions = {
            'ADMIN': ['create', 'read', 'update', 'delete'],
            'MANAGER': ['create', 'read', 'update', 'delete'],
            'CASHIER': ['create', 'read', 'update'],
            'USER': ['read']
        }
        
        role_permissions = permissions.get(user_role, [])
        return action in role_permissions


def create_customer_service(customer_model: CustomerModel) -> CustomerService:
    """Factory function to create customer service.
    
    Args:
        customer_model: Customer model instance
        
    Returns:
        Customer service instance
    """
    return CustomerService(customer_model)
