"""
Simple utility functions for common error handling patterns across all modules.
"""
from typing import Any, Dict, Optional
from app.core.exceptions import (
    ValidationError, NotFoundError, AlreadyExistsError, 
    AuthorizationError, InsufficientStockError, PaymentError,
    DatabaseError, BusinessRuleError, ErrorMessages
)


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
    """
    Validate that all required fields are present and not empty.
    
    Args:
        data: Data dictionary to validate
        required_fields: List of required field names
        
    Raises:
        ValidationError: If any required field is missing or empty
    """
    missing_fields = []
    empty_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            empty_fields.append(field)
    
    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}",
            details={"missing_fields": missing_fields}
        )
    
    if empty_fields:
        raise ValidationError(
            f"Empty required fields: {', '.join(empty_fields)}",
            details={"empty_fields": empty_fields}
        )


def validate_positive_number(value: Any, field_name: str) -> None:
    """
    Validate that a value is a positive number.
    
    Args:
        value: Value to validate
        field_name: Field name for error message
        
    Raises:
        ValidationError: If value is not a positive number
    """
    try:
        num_value = float(value)
        if num_value <= 0:
            raise ValidationError(
                f"{field_name} must be a positive number",
                field=field_name,
                details={"value": value, "constraint": "positive_number"}
            )
    except (TypeError, ValueError):
        raise ValidationError(
            f"{field_name} must be a valid number",
            field=field_name,
            details={"value": value, "constraint": "valid_number"}
        )


def validate_positive_integer(value: Any, field_name: str) -> None:
    """
    Validate that a value is a positive integer.
    
    Args:
        value: Value to validate
        field_name: Field name for error message
        
    Raises:
        ValidationError: If value is not a positive integer
    """
    try:
        int_value = int(value)
        if int_value <= 0:
            raise ValidationError(
                f"{field_name} must be a positive integer",
                field=field_name,
                details={"value": value, "constraint": "positive_integer"}
            )
    except (TypeError, ValueError):
        raise ValidationError(
            f"{field_name} must be a valid integer",
            field=field_name,
            details={"value": value, "constraint": "valid_integer"}
        )


def validate_email(email: str) -> None:
    """
    Simple email validation.
    
    Args:
        email: Email to validate
        
    Raises:
        ValidationError: If email format is invalid
    """
    if not email or "@" not in email or "." not in email:
        raise ValidationError(
            ErrorMessages.INVALID_EMAIL,
            field="email",
            details={"value": email}
        )


def check_resource_exists(resource: Any, resource_name: str, identifier: Any = None) -> None:
    """
    Check if a resource exists, raise NotFoundError if not.
    
    Args:
        resource: Resource object (None if not found)
        resource_name: Name of the resource type
        identifier: Resource identifier (ID, name, etc.)
        
    Raises:
        NotFoundError: If resource doesn't exist
    """
    if not resource:
        message = f"{resource_name.capitalize()} not found"
        if identifier:
            message += f" with identifier: {identifier}"
        
        raise NotFoundError(
            message,
            resource=resource_name,
            details={"identifier": identifier} if identifier else {}
        )


def check_unique_constraint(existing_resource: Any, field_name: str, value: Any) -> None:
    """
    Check unique constraint - raise error if resource with same value exists.
    
    Args:
        existing_resource: Existing resource (None if doesn't exist)
        field_name: Field name that should be unique
        value: Value that should be unique
        
    Raises:
        AlreadyExistsError: If resource with same value already exists
    """
    if existing_resource:
        raise AlreadyExistsError(
            f"Resource with {field_name} '{value}' already exists",
            details={"field": field_name, "value": value}
        )


def handle_common_db_errors(e: Exception, operation: str, resource_name: str) -> None:
    """
    Handle common database errors and convert to appropriate exceptions.
    
    Args:
        e: Original database exception
        operation: Database operation (create, update, delete)
        resource_name: Resource name being operated on
        
    Raises:
        AlreadyExistsError: For unique constraint violations
        NotFoundError: For foreign key constraint violations
        DatabaseError: For other database errors
    """
    error_str = str(e).lower()
    
    if "unique constraint" in error_str or "duplicate" in error_str:
        raise AlreadyExistsError(f"{resource_name.capitalize()} already exists")
    elif "foreign key constraint" in error_str or "referenced record" in error_str:
        raise ValidationError("Referenced record does not exist")
    elif "not found" in error_str:
        raise NotFoundError(f"{resource_name.capitalize()} not found")
    else:
        raise DatabaseError(
            f"Database error during {operation}",
            details={"operation": operation, "resource": resource_name}
        )


def validate_stock_availability(current_stock: int, requested_quantity: int, product_name: str = None) -> None:
    """
    Validate stock availability for a product.
    
    Args:
        current_stock: Current available stock
        requested_quantity: Requested quantity
        product_name: Product name (optional)
        
    Raises:
        InsufficientStockError: If insufficient stock available
    """
    if current_stock < requested_quantity:
        message = f"Insufficient stock available. Available: {current_stock}, Requested: {requested_quantity}"
        if product_name:
            message = f"Insufficient stock for {product_name}. Available: {current_stock}, Requested: {requested_quantity}"
        
        raise InsufficientStockError(
            message,
            product=product_name,
            details={
                "available_stock": current_stock,
                "requested_quantity": requested_quantity
            }
        )


def validate_payment_amount(total_amount: float, payment_amount: float) -> None:
    """
    Validate payment amount against total.
    
    Args:
        total_amount: Total amount due
        payment_amount: Payment amount received
        
    Raises:
        PaymentError: If payment amount is insufficient
    """
    if payment_amount < total_amount:
        raise PaymentError(
            f"Insufficient payment. Total: {total_amount}, Paid: {payment_amount}",
            details={
                "total_amount": total_amount,
                "payment_amount": payment_amount,
                "shortfall": total_amount - payment_amount
            }
        )


def validate_business_hours(hour: int) -> None:
    """
    Simple business hours validation.
    
    Args:
        hour: Hour to validate (0-23)
        
    Raises:
        BusinessRuleError: If operation is outside business hours
    """
    if hour < 6 or hour > 22:  # 6 AM to 10 PM
        raise BusinessRuleError(
            "Operation not allowed outside business hours (6 AM - 10 PM)",
            details={"current_hour": hour, "business_hours": "6 AM - 10 PM"}
        )


def validate_date_range(start_date, end_date) -> None:
    """
    Validate that start date is before end date.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Raises:
        ValidationError: If date range is invalid
    """
    if start_date and end_date and start_date > end_date:
        raise ValidationError(
            "Start date cannot be after end date",
            details={
                "start_date": start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date),
                "end_date": end_date.isoformat() if hasattr(end_date, 'isoformat') else str(end_date)
            }
        )


def safe_convert_to_int(value: Any, field_name: str) -> int:
    """
    Safely convert value to integer.
    
    Args:
        value: Value to convert
        field_name: Field name for error message
        
    Returns:
        Integer value
        
    Raises:
        ValidationError: If conversion fails
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError(
            f"{field_name} must be a valid integer",
            field=field_name,
            details={"value": value}
        )


def safe_convert_to_float(value: Any, field_name: str) -> float:
    """
    Safely convert value to float.
    
    Args:
        value: Value to convert
        field_name: Field name for error message
        
    Returns:
        Float value
        
    Raises:
        ValidationError: If conversion fails
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValidationError(
            f"{field_name} must be a valid number",
            field=field_name,
            details={"value": value}
        )


# Convenience functions for common patterns
def not_found(resource_name: str, identifier: Any = None):
    """Raise NotFoundError for resource."""
    check_resource_exists(None, resource_name, identifier)


def already_exists(field_name: str, value: Any):
    """Raise AlreadyExistsError for duplicate resource."""
    check_unique_constraint(True, field_name, value)


def insufficient_stock(product_name: str, available: int, requested: int):
    """Raise InsufficientStockError for stock shortage."""
    validate_stock_availability(available, requested, product_name)


def invalid_input(message: str, field: str = None):
    """Raise ValidationError for invalid input."""
    raise ValidationError(message, field=field)
