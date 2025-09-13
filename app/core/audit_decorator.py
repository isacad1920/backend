"""
Simple audit decorators for endpoint logging.
"""
import functools
from typing import Callable, Optional
from fastapi import Request

from app.core.audit import get_audit_logger, AuditAction, AuditSeverity

def audit_log(
    action: AuditAction,
    resource_type: str,
    severity: AuditSeverity = AuditSeverity.INFO
):
    """
    Simple audit logging decorator for FastAPI endpoints.
    
    Usage:
    @audit_log(AuditAction.CREATE, "product")
    async def create_product(request: Request, current_user, ...):
        # Your endpoint logic
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request and user from parameters
            request: Optional[Request] = None
            current_user = None
            
            # Look for request and user in args and kwargs
            for arg in args:
                if hasattr(arg, 'method') and hasattr(arg, 'url'):
                    request = arg
                elif hasattr(arg, 'id') and hasattr(arg, 'username'):
                    current_user = arg
            
            for key, value in kwargs.items():
                if key == 'request' and hasattr(value, 'method'):
                    request = value
                elif key == 'current_user' and hasattr(value, 'id'):
                    current_user = value
            
            # Execute the original function
            result = await func(*args, **kwargs)
            
            # Log the action (don't let logging errors break the endpoint)
            try:
                audit_logger = get_audit_logger()
                
                details = {}
                if request:
                    details.update({
                        "endpoint": str(request.url),
                        "method": request.method
                    })
                
                # Extract resource ID from result if it's a dict with 'id'
                resource_id = None
                if isinstance(result, dict) and result.get('data', {}).get('id'):
                    resource_id = str(result['data']['id'])
                
                # Get user_id if current_user exists, otherwise None
                user_id = str(current_user.id) if current_user else None
                
                await audit_logger.log_action(
                    action=action,
                    user_id=user_id,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details=details,
                    ip_address=request.client.host if request and request.client else None,
                    severity=severity
                )
            except Exception as e:
                # Log error but don't break the endpoint
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Audit logging failed: {e}")
            
            return result
            
        return wrapper
    return decorator
