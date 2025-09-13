"""
Utility functions for financial services.
"""
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal, InvalidOperation
from typing import Optional, List, Dict, Any, Union, Tuple
from app.core.exceptions import (
    ValidationError, 
    AuthorizationError,
    DatabaseError
)

logger = logging.getLogger(__name__)


class DateUtils:
    """Utility class for date operations."""
    
    @staticmethod
    def validate_date_range(start_date: Optional[date], end_date: Optional[date]) -> Tuple[date, date]:
        """
        Validate and normalize date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Tuple of (start_date, end_date)
            
        Raises:
            ValidationError: If date range is invalid
        """
        # Set defaults if not provided
        if not start_date:
            start_date = date.today().replace(day=1)  # First day of current month
        if not end_date:
            end_date = date.today()
        
        # Validate date range
        if start_date > end_date:
            raise ValidationError(
                message="Start date cannot be after end date",
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )
        
        # Check for reasonable date range (not more than 5 years)
        max_days = 5 * 365  # 5 years
        if (end_date - start_date).days > max_days:
            raise ValidationError(
                message="Date range too large (maximum 5 years allowed)",
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )
        
        return start_date, end_date
    
    @staticmethod
    def get_period_dates(period: str) -> Tuple[date, date]:
        """
        Get start and end dates for predefined periods.
        
        Args:
            period: Period string ('today', 'week', 'month', 'quarter', 'year')
            
        Returns:
            Tuple of (start_date, end_date)
        """
        today = date.today()
        
        if period.lower() == 'today':
            return today, today
        elif period.lower() in ['week', 'this_week']:
            start_date = today - timedelta(days=today.weekday())
            return start_date, today
        elif period.lower() in ['month', 'this_month']:
            start_date = today.replace(day=1)
            return start_date, today
        elif period.lower() in ['quarter', 'this_quarter']:
            quarter_start_month = ((today.month - 1) // 3) * 3 + 1
            start_date = today.replace(month=quarter_start_month, day=1)
            return start_date, today
        elif period.lower() in ['year', 'this_year']:
            start_date = today.replace(month=1, day=1)
            return start_date, today
        else:
            raise ValidationError(
                message="Invalid period specified",
                field="period",
                value=period
            )
    
    @staticmethod
    def get_previous_period(start_date: date, end_date: date) -> Tuple[date, date]:
        """
        Get the previous period of the same duration.
        
        Args:
            start_date: Current period start date
            end_date: Current period end date
            
        Returns:
            Tuple of (previous_start_date, previous_end_date)
        """
        duration = end_date - start_date
        previous_end = start_date - timedelta(days=1)
        previous_start = previous_end - duration
        return previous_start, previous_end


class NumberUtils:
    """Utility class for number operations."""
    
    @staticmethod
    def safe_decimal(value: Union[str, int, float, Decimal]) -> Decimal:
        """
        Safely convert value to Decimal.
        
        Args:
            value: Value to convert
            
        Returns:
            Decimal value
            
        Raises:
            ValidationError: If conversion fails
        """
        try:
            if value is None:
                return Decimal('0')
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError) as e:
            raise ValidationError(
                message="Invalid numeric value",
                field="amount",
                value=str(value)
            )
    
    @staticmethod
    def safe_divide(numerator: Union[Decimal, float], denominator: Union[Decimal, float]) -> Decimal:
        """
        Safely divide two numbers, handling division by zero.
        
        Args:
            numerator: Numerator value
            denominator: Denominator value
            
        Returns:
            Division result or 0 if denominator is 0
        """
        try:
            num = NumberUtils.safe_decimal(numerator)
            den = NumberUtils.safe_decimal(denominator)
            
            if den == 0:
                return Decimal('0')
            
            return num / den
        except Exception:
            return Decimal('0')
    
    @staticmethod
    def calculate_percentage(part: Union[Decimal, float], total: Union[Decimal, float]) -> Decimal:
        """
        Calculate percentage safely.
        
        Args:
            part: Part value
            total: Total value
            
        Returns:
            Percentage (0-100)
        """
        if total == 0:
            return Decimal('0')
        
        part_decimal = NumberUtils.safe_decimal(part)
        total_decimal = NumberUtils.safe_decimal(total)
        
        return (part_decimal / total_decimal) * 100
    
    @staticmethod
    def format_currency(amount: Union[Decimal, float], currency: str = "USD") -> str:
        """
        Format amount as currency string.
        
        Args:
            amount: Amount to format
            currency: Currency code
            
        Returns:
            Formatted currency string
        """
        try:
            amount_decimal = NumberUtils.safe_decimal(amount)
            if currency.upper() == "USD":
                return f"${amount_decimal:,.2f}"
            else:
                return f"{amount_decimal:,.2f} {currency}"
        except Exception:
            return f"0.00 {currency}"


class ValidationUtils:
    """Utility class for data validation."""
    
    @staticmethod
    def validate_user_permissions(user: Dict[str, Any], required_action: str, resource: str = "financial") -> None:
        """
        Validate user has required permissions.
        
        Args:
            user: User data dictionary
            required_action: Required action (read, write, admin)
            resource: Resource being accessed
            
        Raises:
            AuthorizationError: If user lacks permissions
        """
        if not user:
            raise AuthorizationError("Authentication required")
        
        user_role = user.get('role', 'CASHIER').upper()
        
        # Define role permissions
        role_permissions = {
            'ADMIN': ['read', 'write', 'admin'],
            'MANAGER': ['read', 'write'],
            'ACCOUNTANT': ['read', 'write'] if resource == 'financial' else ['read'],
            'INVENTORY_CLERK': ['read'] if resource == 'financial' else ['read', 'write'],
            'CASHIER': ['read'] if resource in ['financial', 'sales'] else []
        }
        
        allowed_actions = role_permissions.get(user_role, [])
        
        if required_action not in allowed_actions:
            raise AuthorizationError(
                message=f"Insufficient permissions for {required_action} access to {resource}",
                required_role=f"Role with {required_action} permissions",
                user_role=user_role
            )
    
    @staticmethod
    def validate_branch_access(user: Dict[str, Any], branch_id: Optional[int]) -> None:
        """
        Validate user has access to specified branch.
        
        Args:
            user: User data dictionary
            branch_id: Branch ID to validate
            
        Raises:
            AuthorizationError: If user lacks branch access
        """
        if not branch_id:
            return  # No specific branch requested
        
        user_role = user.get('role', 'CASHIER').upper()
        user_branch_id = user.get('branchId')
        
        # Admins and managers can access all branches
        if user_role in ['ADMIN', 'MANAGER']:
            return
        
        # Other roles can only access their own branch
        if user_branch_id != branch_id:
            raise AuthorizationError(
                message="Access denied to specified branch",
                user_role=user_role
            )
    
    @staticmethod
    def validate_required_data(data: List[Any], data_type: str, minimum_required: int = 1) -> None:
        """
        Validate that sufficient data exists for analysis.
        
        Args:
            data: Data list to validate
            data_type: Type of data being validated
            minimum_required: Minimum number of records required
            
        Raises:
            ValidationError: If insufficient data
        """
        if not data or len(data) < minimum_required:
            raise ValidationError(
                message=f"Insufficient {data_type} data for analysis",
                data_type=data_type,
                minimum_required=minimum_required
            )


class DataAggregationUtils:
    """Utility class for data aggregation operations."""
    
    @staticmethod
    def group_by_date(data: List[Dict], date_field: str = 'date') -> Dict[str, List[Dict]]:
        """
        Group data by date.
        
        Args:
            data: List of data dictionaries
            date_field: Field name containing date
            
        Returns:
            Dictionary with date as key and list of records as value
        """
        grouped = {}
        for record in data:
            date_val = record.get(date_field)
            if date_val:
                date_key = date_val.isoformat() if hasattr(date_val, 'isoformat') else str(date_val)
                if date_key not in grouped:
                    grouped[date_key] = []
                grouped[date_key].append(record)
        return grouped
    
    @staticmethod
    def calculate_totals(data: List[Dict], amount_field: str = 'amount') -> Dict[str, Decimal]:
        """
        Calculate various totals from data.
        
        Args:
            data: List of data dictionaries
            amount_field: Field name containing amount
            
        Returns:
            Dictionary with total, average, min, max values
        """
        if not data:
            return {
                'total': Decimal('0'),
                'average': Decimal('0'),
                'min': Decimal('0'),
                'max': Decimal('0'),
                'count': 0
            }
        
        amounts = [NumberUtils.safe_decimal(record.get(amount_field, 0)) for record in data]
        total = sum(amounts)
        
        return {
            'total': total,
            'average': total / len(amounts) if amounts else Decimal('0'),
            'min': min(amounts) if amounts else Decimal('0'),
            'max': max(amounts) if amounts else Decimal('0'),
            'count': len(amounts)
        }
    
    @staticmethod
    def calculate_growth_rate(current: Union[Decimal, float], previous: Union[Decimal, float]) -> Decimal:
        """
        Calculate growth rate between two periods.
        
        Args:
            current: Current period value
            previous: Previous period value
            
        Returns:
            Growth rate as percentage
        """
        current_decimal = NumberUtils.safe_decimal(current)
        previous_decimal = NumberUtils.safe_decimal(previous)
        
        if previous_decimal == 0:
            return Decimal('0') if current_decimal == 0 else Decimal('100')
        
        return ((current_decimal - previous_decimal) / previous_decimal) * 100


class ErrorHandler:
    """Utility class for error handling and logging."""
    
    @staticmethod
    def log_and_raise(exception_class, message: str, **kwargs):
        """
        Log error and raise exception.
        
        Args:
            exception_class: Exception class to raise
            message: Error message
            **kwargs: Additional exception parameters
        """
        logger.error(f"{exception_class.__name__}: {message}")
        raise exception_class(message, **kwargs)
    
    @staticmethod
    def handle_database_error(operation: str, table: str, original_error: Exception):
        """
        Handle database errors with proper logging and exception raising.
        
        Args:
            operation: Database operation that failed
            table: Table name involved
            original_error: Original exception
        """
        error_msg = f"Database {operation} failed on {table}: {str(original_error)}"
        logger.error(error_msg)
        
        raise DatabaseError(f"Failed to {operation} {table} data")
    
    @staticmethod
    def safe_execute(func, default_return=None, log_errors: bool = True):
        """
        Safely execute a function with error handling.
        
        Args:
            func: Function to execute
            default_return: Default return value on error
            log_errors: Whether to log errors
            
        Returns:
            Function result or default_return on error
        """
        try:
            return func()
        except Exception as e:
            if log_errors:
                logger.error(f"Safe execution failed: {str(e)}")
            return default_return


# Convenience functions for common operations
def validate_financial_permission(user: Dict[str, Any], action: str = 'read') -> None:
    """Validate user has financial permissions."""
    ValidationUtils.validate_user_permissions(user, action, 'financial')


def safe_decimal_sum(values: List[Union[str, int, float, Decimal]]) -> Decimal:
    """Safely sum a list of values as Decimal."""
    return sum(NumberUtils.safe_decimal(v) for v in values if v is not None)


def format_financial_amount(amount: Union[Decimal, float]) -> str:
    """Format amount for financial display."""
    return NumberUtils.format_currency(amount)
