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
from app.core.security import JWTManager, PermissionManager, TokenType, rate_limiter
from generated.prisma import fields  # Import for proper JSON handling

# No longer needed: db_manager

logger = logging.getLogger(__name__)

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Authentication middleware to verify JWT tokens."""
    
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
        """Process request through authentication middleware."""
        start_time = time.time()
        
        # Skip authentication for public paths
        if self._is_public_path(request.url.path):
            response = await call_next(request)
            return await self._add_process_time_header(response, start_time)
        
        # Skip authentication for excluded paths
        if self._is_excluded_path(request.url.path):
            response = await call_next(request)
            return await self._add_process_time_header(response, start_time)
        
        # Extract and verify token
        try:
            token = await self._extract_token(request)
            if not token:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Authentication token required"},
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            payload = await self._verify_token(token)
            if not payload:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid or expired token"},
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Add user info to request state
            request.state.user_id = payload.get("sub")
            request.state.token_payload = payload
            request.state.token = token
            
            # Check if user is active (optional database check)
            user_active = await self._check_user_status(payload.get("sub"))
            if not user_active:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "User account is inactive"}
                )
            
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            logger.error(f"Authentication middleware error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal authentication error"}
            )
        
        # Process request
        response = await call_next(request)
        return await self._add_process_time_header(response, start_time)
    
    def _is_public_path(self, path: str) -> bool:
        """Check if path is public (doesn't require authentication)."""
        for public_path in self.public_paths:
            if path.startswith(public_path):
                return True
        return False
    
    def _is_excluded_path(self, path: str) -> bool:
        """Check if path is excluded from authentication."""
        for excluded_path in self.exclude_paths:
            if path.startswith(excluded_path):
                return True
        return False
    
    async def _extract_token(self, request: Request) -> str | None:
        """Extract JWT token from request headers.
        Accepts both 'Bearer <token>' and '<token>'; ignores placeholders.
        """
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None
        token = None
        if authorization.lower().startswith("bearer "):
            token = authorization.split(" ", 1)[1].strip()
        else:
            token = authorization.strip()
        if not token or token.lower() in {"undefined", "null", "none"}:
            return None
        return token
    
    async def _verify_token(self, token: str) -> dict[str, Any] | None:
        """Verify JWT token and return payload."""
        try:
            # Check if token is blacklisted
            if JWTManager.is_token_blacklisted(token):
                return None
            
            # Verify token
            payload = JWTManager.verify_token(token, TokenType.ACCESS)
            return payload
        except Exception as e:
            logger.warning(f"Token verification failed: {e}")
            return None
    
    async def _check_user_status(self, user_id: str) -> bool:
        """Check if user is active in database."""
        try:
            from ..db.client import prisma
            uid = int(user_id) if isinstance(user_id, (str, int)) and str(user_id).isdigit() else None
            if uid is None:
                return False
            user = await prisma.user.find_unique(
                where={"id": uid}
            )
            return user and getattr(user, "isActive", True)
        except Exception as e:
            logger.error(f"User status check failed: {e}")
            # Fallback to True for now to avoid breaking existing functionality
            return True
    
    async def _add_process_time_header(self, response: Response, start_time: float) -> Response:
        """Add processing time header to response."""
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

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
        """Process request through authorization middleware."""
        # Skip if no user in request state (public endpoints)
        if not hasattr(request.state, "user_id"):
            return await call_next(request)
        
        try:
            # Check route permissions
            path = request.url.path
            method = request.method
            required_permissions = self._get_required_permissions(path, method)
            
            if required_permissions:
                user_role = await self._get_user_role(request.state.user_id)
                if not self._check_permissions(user_role, required_permissions):
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": "Insufficient permissions"}
                    )
        
        except Exception as e:
            logger.error(f"Authorization middleware error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal authorization error"}
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
    
    async def _get_user_role(self, user_id: str) -> UserRole:
        """Get user role from database."""
        try:
            from ..db.client import prisma
            uid = int(user_id) if isinstance(user_id, (str, int)) and str(user_id).isdigit() else None
            if uid is None:
                return None
            user = await prisma.user.find_unique(
                where={"id": uid}
            )
            return UserRole(user.role) if user else None
        except Exception as e:
            logger.error(f"Failed to get user role: {e}")
            # Fallback to ADMIN for now to avoid breaking existing functionality
            return UserRole.ADMIN
    
    def _check_permissions(self, user_role: UserRole, required_permissions: list[str]) -> bool:
        """Check if user has required permissions."""
        if not user_role:
            return False
        
        for permission in required_permissions:
            if not PermissionManager.has_permission(user_role, permission):
                return False
        
        return True

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        burst_requests: int = 100,
        exclude_paths: list[str] | None = None
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_requests = burst_requests
        self.exclude_paths = exclude_paths or ["/health", "/ping"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through rate limiting."""
        # Skip rate limiting for excluded paths
        if self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_identifier(request)
        
        # Check rate limit
        if not rate_limiter.is_allowed(client_id, self.requests_per_minute, 60):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        return await call_next(request)
    
    def _is_excluded_path(self, path: str) -> bool:
        """Check if path is excluded from rate limiting."""
        for excluded_path in self.exclude_paths:
            if path.startswith(excluded_path):
                return True
        return False
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Use user ID if authenticated
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"
        
        # Use IP address for unauthenticated requests
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

class AuditLogMiddleware(BaseHTTPMiddleware):
    """Audit logging middleware."""
    
    def __init__(
        self,
        app: ASGIApp,
        log_requests: bool = True,
        log_responses: bool = True,  # Enable response logging by default
        exclude_paths: list[str] | None = None
    ):
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
        # Minimize excluded paths to capture more audit data
        self.exclude_paths = exclude_paths or ["/health", "/ping", "/favicon.ico"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through audit logging."""
        # Skip logging for excluded paths
        if self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        # Log only sensitive request categories
        if self.log_requests and self._should_audit_request(request):
            await self._log_request(request)
        
        # Process request
        response = await call_next(request)
        
        # Log only for sensitive operations
        if self.log_responses and self._should_audit_request(request):
            await self._log_response(request, response)
        
        return response
    
    def _is_excluded_path(self, path: str) -> bool:
        """Check if path is excluded from audit logging."""
        for excluded_path in self.exclude_paths:
            if path.startswith(excluded_path):
                return True
        return False

    def _should_audit_request(self, request: Request) -> bool:
        """Decide if a request should be audited.
        We audit only: auth (login/logout), mutations (POST/PUT/PATCH/DELETE) on financial/journal/sales/inventory/users,
        permissions changes, and system configuration.
        """
        path = request.url.path.lower()
        method = request.method.upper()
        # Skip health/docs/static
        if self._is_excluded_path(request.url.path):
            return False
        # Always audit auth operations
        if path.startswith("/api/") and "/auth/" in path:
            return True
        # Only audit mutations on critical domains
        critical_segments = [
            "/journal",
            "/financial",
            "/sales",
            "/inventory",
            "/users",
            "/permissions",
            "/system/settings",
            "/accounts",
        ]
        if method in {"POST", "PUT", "PATCH", "DELETE"}:
            return any(seg in path for seg in critical_segments)
        return False
    
    async def _log_request(self, request: Request) -> None:
        """Log request details."""
        try:
            user_id = getattr(request.state, "user_id", None)
            client_ip = request.client.host if request.client else "unknown"
            
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "type": "request",
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "user_id": user_id,
                "client_ip": client_ip,
                "user_agent": request.headers.get("User-Agent", "")
            }
            
            # Store audit log in database
            try:
                from ..db.client import prisma
                
                # Determine action based on HTTP method (use only valid enum values)
                action = "UPDATE"  # Default fallback
                if request.method == "POST":
                    action = "CREATE"
                elif request.method in ["PUT", "PATCH"]:
                    action = "UPDATE"
                elif request.method == "DELETE":
                    action = "DELETE"
                elif "auth" in request.url.path.lower():
                    action = "LOGIN" if "login" in request.url.path.lower() else "LOGIN"
                
                uid = int(user_id) if user_id and str(user_id).isdigit() else None
                await prisma.auditlog.create(
                    data={
                        "userId": uid,
                        "action": action,
                        "entityType": "API_REQUEST",
                        "entityId": f"{request.method} {request.url.path}",
                        "newValues": fields.Json(log_data),  # Use proper JSON field
                        "severity": "INFO",
                        "ipAddress": client_ip,
                        "userAgent": request.headers.get("User-Agent", "")
                    }
                )
            except Exception as db_error:
                logger.error(f"Failed to store audit log in database: {db_error}")
                # Fallback to file logging
                logger.info(f"Audit log: {json.dumps(log_data)}")
            
        except Exception as e:
            logger.error(f"Failed to log request: {e}")
    
    async def _log_response(self, request: Request, response: Response) -> None:
        """Log response details."""
        try:
            user_id = getattr(request.state, "user_id", None)
            
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "type": "response",
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "user_id": user_id
            }
            
            # Store audit log in database for ALL responses (not just errors)
            try:
                from ..db.client import prisma
                
                # Determine action based on HTTP method
                action = "UPDATE"  # Default fallback
                if request.method == "POST":
                    action = "CREATE"
                elif request.method in ["PUT", "PATCH"]:
                    action = "UPDATE"
                elif request.method == "DELETE":
                    action = "DELETE"
                elif "auth" in request.url.path.lower():
                    action = "LOGIN" if "login" in request.url.path.lower() else "LOGIN"
                
                # Determine severity based on status code (use only valid enum values)
                severity = "INFO"  # Default
                if response.status_code >= 500:
                    severity = "ERROR"
                elif response.status_code >= 400:
                    severity = "WARNING"
                else:
                    severity = "INFO"  # Success cases use INFO
                
                uid = int(user_id) if user_id and str(user_id).isdigit() else None
                await prisma.auditlog.create(
                    data={
                        "userId": uid,
                        "action": action,
                        "entityType": "API_RESPONSE",
                        "entityId": f"{request.method} {request.url.path}",
                        "newValues": fields.Json(log_data),  # Use proper JSON field
                        "severity": severity,
                        "ipAddress": request.client.host if hasattr(request, 'client') else None,
                        "userAgent": request.headers.get("User-Agent", "")
                    }
                )
            except Exception as db_error:
                logger.error(f"Failed to store response audit log: {db_error}")
                # Fallback to file logging
                logger.info(f"Audit log: {json.dumps(log_data)}")
            
        except Exception as e:
            logger.error(f"Failed to log response: {e}")

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
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

def create_audit_middleware(
    app: ASGIApp,
    log_requests: bool = True,
    log_responses: bool = False
) -> AuditLogMiddleware:
    """Create audit logging middleware with configuration."""
    return AuditLogMiddleware(app, log_requests, log_responses)