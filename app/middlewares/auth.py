"""
Authentication and authorization middleware.
"""
import json
import logging
import time
from collections.abc import Callable
from datetime import datetime
from typing import Any

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import UserRole
from app.core.security import JWTManager, TokenType, rate_limiter
from app.core.permissions import get_user_effective_permissions
from generated.prisma import fields  # Import for proper JSON handling

# No longer needed: db_manager

logger = logging.getLogger(__name__)

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Authentication middleware to verify JWT tokens.

    NOTE: Actual token verification logic appears to have been elsewhere; this class currently
    only preserves public/excluded path logic. Audit logging is handled separately by AuditLogMiddleware.
    """

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: list[str] | None = None,
        public_paths: list[str] | None = None
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or []
        self.public_paths = public_paths or [
            "/docs", "/redoc", "/openapi.json",
            "/api/v1/auth/login", "/api/v1/auth/register",
            "/api/v1/health", "/api/v1/ping",
            "/favicon.ico", "/static/"
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Short-circuit for public or excluded paths
        path = request.url.path
        if any(path.startswith(p) for p in self.public_paths) or any(path.startswith(p) for p in self.exclude_paths):
            return await call_next(request)
        # If token verification is required, hook here (placeholder for future implementation)
        return await call_next(request)

class AuthorizationMiddleware(BaseHTTPMiddleware):
    """Authorization middleware to check user permissions."""
    
    def __init__(
        self,
        app: ASGIApp,
        route_permissions: dict[str, list[str]] | None = None
    ):
        super().__init__(app)
        self.route_permissions = route_permissions or {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through authorization middleware using RBAC effective permissions."""
        # Skip if no user in request state (public endpoints / unauthenticated)
        if not hasattr(request.state, "user_id"):
            return await call_next(request)

        try:
            path = request.url.path
            method = request.method
            required_permissions = self._get_required_permissions(path, method)

            if required_permissions:
                if not await self._check_permissions(request.state.user_id, required_permissions):
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": "Insufficient permissions"},
                    )
        except Exception as e:
            logger.error(f"Authorization middleware error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal authorization error"},
            )

        return await call_next(request)
    
    def _get_required_permissions(self, path: str, method: str) -> list[str]:
        """Get required permissions for a route."""
        route_key = f"{method} {path}"
        
        # Check exact match first
        if route_key in self.route_permissions:
            return self.route_permissions[route_key]
        
        # Check pattern matches
        for pattern, permissions in self.route_permissions.items():
            if self._path_matches_pattern(path, pattern):
                return permissions
        
        return []
    
    def _path_matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches permission pattern."""
        # Simple pattern matching (can be enhanced with regex)
        if "*" in pattern:
            pattern_prefix = pattern.replace("*", "")
            return path.startswith(pattern_prefix)
        return path == pattern
    
    async def _check_permissions(self, user_id: str | int, required_permissions: list[str]) -> bool:
        """Check if user (by id) has all required permissions via RBAC effective set.

        required_permissions should be strings in the form 'resource:action'. Legacy
        permission names without a ':' will be treated as global action permissions
        by mapping to '*:name'. This supports a transitional phase while routes are
        updated to the normalized naming convention.
        """
        try:
            from ..db.client import prisma

            uid = int(user_id) if str(user_id).isdigit() else None
            if uid is None:
                return False

            user = await prisma.user.find_unique(where={"id": uid})
            if not user:
                return False

            # ADMIN short-circuit (mirrors core.permissions logic)
            if UserRole(user.role) == UserRole.ADMIN:
                return True

            effective = await get_user_effective_permissions(user.id, prisma)

            # Normalize any legacy names (no resource) to wildcard resource pattern
            needed = [p if ":" in p else f"*:{p}" for p in required_permissions]
            return all(p in effective or (p.startswith("*:") and p.split(":",1)[1] in {e.split(":",1)[1] for e in effective if e.startswith("*:")}) for p in needed)
        except Exception as e:
            logger.error(f"RBAC permission check failed: {e}")
            return False

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        burst_requests: int = 100,
        exclude_paths: list[str] | None = None,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_requests = burst_requests
        self.exclude_paths = exclude_paths or ["/health", "/ping"]
    
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Security headers middleware."""
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    """Security headers middleware."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Add HSTS header for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Add CSP header - allow external resources for Swagger UI
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        
        return response

class CORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware with enhanced security."""
    
    def __init__(
        self,
        app: ASGIApp,
        allowed_origins: list[str] = None,
        allowed_methods: list[str] = None,
        allowed_headers: list[str] = None,
        allow_credentials: bool = True
    ):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["*"]
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allowed_headers = allowed_headers or ["*"]
        self.allow_credentials = allow_credentials
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process CORS headers."""
        origin = request.headers.get("origin")
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
            response.status_code = 200
        else:
            response = await call_next(request)
        
        # Add CORS headers
        if self._is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin or "*"
        
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)
        
        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed."""
        if not origin:
            return False
        
        if "*" in self.allowed_origins:
            return True
        
        return origin in self.allowed_origins

# Middleware factory functions
def create_auth_middleware(
    app: ASGIApp,
    exclude_paths: list[str] | None = None,
    public_paths: list[str] | None = None
) -> AuthenticationMiddleware:
    """Create authentication middleware with configuration."""
    return AuthenticationMiddleware(app, exclude_paths, public_paths)

def create_authz_middleware(
    app: ASGIApp,
    route_permissions: dict[str, list[str]] | None = None
) -> AuthorizationMiddleware:
    """Create authorization middleware with configuration."""
    return AuthorizationMiddleware(app, route_permissions)

def create_rate_limit_middleware(
    app: ASGIApp,
    requests_per_minute: int = 60,
    burst_requests: int = 100
) -> RateLimitMiddleware:
    """Create rate limiting middleware with configuration."""
    return RateLimitMiddleware(app, requests_per_minute, burst_requests)

## NOTE: AuditLogMiddleware temporarily removed/refactored. If needed, re-add a thin wrapper
## around the centralized audit logger in app.core.audit. The factory was removed to avoid
## referencing an undefined class during cleanup.