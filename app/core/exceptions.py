"""
Global custom exceptions for SOFinance POS System.
Simple, consistent error handling across all endpoints.
"""
from datetime import datetime
from typing import Any


class APIError(Exception):
    """Base API exception class."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "API_ERROR",
        details: dict[str, Any] | None = None
    ):
        """Initialize API error.
        
        Args:
            message: Human-readable error message
            status_code: HTTP status code
            error_code: Unique error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for JSON response."""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details
            },
            "timestamp": self.timestamp.isoformat() + "Z",
            "success": False
        }


# Authentication & Authorization Errors
class AuthenticationError(APIError):
    """Authentication failed."""
    
    def __init__(self, message: str = "Authentication required", **kwargs):
        super().__init__(message, status_code=401, error_code="AUTH_REQUIRED", **kwargs)


class AuthorizationError(APIError):
    """Authorization failed - user lacks permissions."""
    
    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(message, status_code=403, error_code="ACCESS_DENIED", **kwargs)


class TokenError(APIError):
    """Invalid or expired token."""
    
    def __init__(self, message: str = "Invalid or expired token", **kwargs):
        super().__init__(message, status_code=401, error_code="INVALID_TOKEN", **kwargs)


# Validation Errors
class ValidationError(APIError):
    """Input validation failed."""
    
    def __init__(self, message: str = "Validation failed", field: str = None, **kwargs):
        details = kwargs.pop('details', {})  # Remove from kwargs to avoid conflict
        if field:
            details['field'] = field
        super().__init__(message, status_code=400, error_code="VALIDATION_ERROR", details=details, **kwargs)


class InvalidInputError(APIError):
    """Invalid input data."""
    
    def __init__(self, message: str = "Invalid input", **kwargs):
        super().__init__(message, status_code=400, error_code="INVALID_INPUT", **kwargs)


# Resource Errors
class NotFoundError(APIError):
    """Resource not found."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        resource: str = None,
        error_code: str | None = None,
        **kwargs
    ):
        # Gracefully handle callers that pass 'detail' instead of message
        details = kwargs.pop('details', {})  # Remove from kwargs to avoid conflict
        detail_msg = kwargs.pop('detail', None)
        if detail_msg and (not message or message == "Resource not found"):
            message = detail_msg
        if resource:
            details['resource'] = resource
        final_error_code = error_code or "NOT_FOUND"
        super().__init__(message, status_code=404, error_code=final_error_code, details=details)


class AlreadyExistsError(APIError):
    """Resource already exists."""
    
    def __init__(self, message: str = "Resource already exists", error_code: str | None = None, **kwargs):
        # Allow 'detail' kwarg to provide the message
        details = kwargs.pop('details', {})
        detail_msg = kwargs.pop('detail', None)
        if detail_msg and (not message or message == "Resource already exists"):
            message = detail_msg
        final_error_code = error_code or "ALREADY_EXISTS"
        super().__init__(message, status_code=409, error_code=final_error_code, details=details)


class ConflictError(APIError):
    """Request conflicts with current state."""
    
    def __init__(self, message: str = "Request conflict", **kwargs):
        super().__init__(message, status_code=409, error_code="CONFLICT", **kwargs)


# Business Logic Errors
class BusinessRuleError(APIError):
    """Business rule violation."""
    
    def __init__(self, message: str = "Business rule violation", **kwargs):
        super().__init__(message, status_code=400, error_code="BUSINESS_RULE_VIOLATION", **kwargs)


class InsufficientStockError(APIError):
    """Insufficient stock for operation."""
    
    def __init__(self, message: str = "Insufficient stock", product: str = None, **kwargs):
        details = kwargs.pop('details', {})  # Remove from kwargs to avoid conflict
        if product:
            details['product'] = product
        super().__init__(message, status_code=400, error_code="INSUFFICIENT_STOCK", details=details, **kwargs)


class PaymentError(APIError):
    """Payment processing error."""
    
    def __init__(self, message: str = "Payment processing failed", **kwargs):
        super().__init__(message, status_code=400, error_code="PAYMENT_ERROR", **kwargs)


# System Errors
class DatabaseError(APIError):
    """Database operation failed."""
    
    def __init__(self, message: str = None, *, detail: str = None, error_code: str = None, **kwargs):
        # Prefer detail if provided as a clearer message
        final_message = detail or message or "Database operation failed"
        final_error_code = error_code or "DATABASE_ERROR"
        super().__init__(final_message, status_code=500, error_code=final_error_code, **kwargs)


class ExternalServiceError(APIError):
    """External service unavailable or failed."""
    
    def __init__(self, message: str = "External service error", service: str = None, **kwargs):
        details = kwargs.pop('details', {})  # Remove from kwargs to avoid conflict
        if service:
            details['service'] = service
        super().__init__(message, status_code=503, error_code="SERVICE_ERROR", details=details, **kwargs)


class ConfigurationError(APIError):
    """System configuration error."""
    
    def __init__(self, message: str = "Configuration error", **kwargs):
        super().__init__(message, status_code=500, error_code="CONFIG_ERROR", **kwargs)


# Rate Limiting
class RateLimitError(APIError):
    """Rate limit exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(message, status_code=429, error_code="RATE_LIMIT", **kwargs)


# File/Export Errors
class FileError(APIError):
    """File operation error."""
    
    def __init__(self, message: str = "File operation failed", **kwargs):
        super().__init__(message, status_code=500, error_code="FILE_ERROR", **kwargs)


class ExportError(APIError):
    """Export operation failed."""
    
    def __init__(self, message: str = "Export failed", format: str = None, **kwargs):
        details = kwargs.pop('details', {})  # Remove from kwargs to avoid conflict
        if format:
            details['format'] = format
        super().__init__(message, status_code=500, error_code="EXPORT_ERROR", details=details, **kwargs)


# Utility function to create API errors easily
def create_error(
    message: str,
    status_code: int = 400,
    error_code: str = "API_ERROR",
    **details
) -> APIError:
    """Create a generic API error with details."""
    return APIError(
        message=message,
        status_code=status_code,
        error_code=error_code,
        details=details
    )


# Common error messages
class ErrorMessages:
    """Common error messages for consistency."""
    
    # Authentication
    AUTH_REQUIRED = "Authentication is required to access this resource"
    INVALID_CREDENTIALS = "Invalid username or password"
    TOKEN_EXPIRED = "Access token has expired"
    TOKEN_INVALID = "Invalid access token"
    
    # Authorization
    ACCESS_DENIED = "You don't have permission to access this resource"
    INSUFFICIENT_PERMISSIONS = "Your role doesn't allow this operation"
    BRANCH_ACCESS_DENIED = "You don't have access to this branch"
    
    # Validation
    REQUIRED_FIELD = "This field is required"
    INVALID_FORMAT = "Invalid data format"
    INVALID_EMAIL = "Please provide a valid email address"
    INVALID_PHONE = "Please provide a valid phone number"
    INVALID_DATE = "Please provide a valid date"
    INVALID_AMOUNT = "Please provide a valid amount"
    
    # Resources
    USER_NOT_FOUND = "User not found"
    PRODUCT_NOT_FOUND = "Product not found"
    CUSTOMER_NOT_FOUND = "Customer not found"
    ORDER_NOT_FOUND = "Order not found"
    BRANCH_NOT_FOUND = "Branch not found"
    
    # Business Rules
    INSUFFICIENT_STOCK = "Not enough stock available"
    INVALID_DISCOUNT = "Invalid discount amount"
    PAYMENT_REQUIRED = "Payment is required to complete this transaction"
    ORDER_ALREADY_COMPLETED = "This order has already been completed"
    
    # System
    DATABASE_ERROR = "A database error occurred. Please try again"
    SERVICE_UNAVAILABLE = "Service is temporarily unavailable"
    FILE_UPLOAD_ERROR = "Failed to upload file"
    EXPORT_ERROR = "Failed to export data"
