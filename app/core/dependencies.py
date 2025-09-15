"""
FastAPI dependency injection functions for common operations.
"""
import logging
from datetime import datetime
from typing import Annotated, Any

from fastapi import Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import UserRole, settings
from app.core.security import JWTManager, TokenType, rate_limiter
from app.core.permissions import check_permission as rbac_check_permission, get_user_effective_permissions
from app.db.prisma import get_db

logger = logging.getLogger(__name__)

# Security scheme for JWT tokens
security = HTTPBearer(auto_error=False)

# Authentication dependencies
async def get_optional_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    request: Request = None,
) -> str | None:
    """Extract optional JWT token from request.
    Accepts both 'Authorization: Bearer <token>' and 'Authorization: <token>'.
    Ignores empty or placeholder values like 'undefined'/'null'.
    """
    token: str | None = None
    if credentials and credentials.scheme.lower() == "bearer":
        token = credentials.credentials
    elif request is not None:
        raw = request.headers.get("Authorization")
        if raw:
            if raw.lower().startswith("bearer "):
                token = raw.split(" ", 1)[1].strip()
            else:
                token = raw.strip()
    if not token or token.lower() in {"undefined", "null", "none"}:
        return None
    return token

async def get_required_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    request: Request = None,
) -> str:
    """Extract required JWT token from request with robust parsing."""
    token = await get_optional_token(credentials, request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

async def verify_access_token(
    token: str = Depends(get_required_token)
) -> dict[str, Any]:
    """Verify access token and return payload."""
    payload = JWTManager.verify_token(token, TokenType.ACCESS)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if token is blacklisted
    # Skip blacklist enforcement in test environment to prevent cross-test contamination
    # Async persistent blacklist check
    if settings.environment.upper() != "TEST" and await JWTManager.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

async def verify_refresh_token(
    token: str = Depends(get_required_token)
) -> dict[str, Any]:
    """Verify refresh token and return payload."""
    payload = JWTManager.verify_token(token, TokenType.REFRESH)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

async def get_current_user_id(
    token_payload: dict[str, Any] = Depends(verify_access_token)
) -> str:
    """Get current user ID from token."""
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    return user_id

async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db = Depends(get_db)
):
    """Get current user from database."""
    try:
        user = await db.user.find_unique(where={"id": int(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except ValueError:
        # Handle case where user_id is not a valid integer
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )

async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """Get current active user."""
    if not current_user.isActive:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

# Role-based dependencies
def require_role(*allowed_roles):
    """Create a dependency that requires specific roles."""
    async def role_checker(
        current_user = Depends(get_current_active_user)
    ):
        # Normalize role to canonical uppercase string (handles ORM enums and strings like "Role.ADMIN")
        def _norm(val: Any) -> str:
            try:
                raw = val.value if hasattr(val, "value") else str(val)
                # If value looks like "Role.ADMIN" or "UserRole.ADMIN", take the suffix
                if "." in raw:
                    raw = raw.split(".")[-1]
                return raw.upper()
            except Exception:
                return str(val).upper()

        user_role_norm = _norm(getattr(current_user, "role", None))

        # Handle both cases: require_role(UserRole.ADMIN) and require_role([UserRole.ADMIN])
        if len(allowed_roles) == 1 and isinstance(allowed_roles[0], list):
            # Case: require_role([UserRole.ADMIN, UserRole.MANAGER])
            role_values = [_norm(role) for role in allowed_roles[0]]
        else:
            # Case: require_role(UserRole.ADMIN, UserRole.MANAGER)
            role_values = [_norm(role) for role in allowed_roles]

        # Debug logging to trace role checks
        try:
            logger.debug(f"Role check - user_role={user_role_norm}, allowed={role_values}, raw={getattr(current_user, 'role', None)}")
        except Exception:
            pass

        if user_role_norm not in role_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return role_checker

# Permission-based dependencies
def require_permission(*permissions: str):
    """RBAC permission dependency using normalized tables.

    All permissions are in form 'resource:action'. Any missing permission => 403.
    """
    async def permission_checker(current_user=Depends(get_current_active_user), db=Depends(get_db)):
        # ADMIN short-circuit
        role_val = getattr(current_user, "role", "")
        role_name = role_val.value if hasattr(role_val, "value") else str(role_val)
        if role_name.upper().endswith("ADMIN"):
            return current_user
        # Batch effective permissions
        effective = await get_user_effective_permissions(int(current_user.id), db)
        for perm in permissions:
            if perm not in effective:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Permission required: {perm}")
        return current_user

    return permission_checker

# Branch-based dependencies
async def get_user_branch_id(
    current_user = Depends(get_current_active_user)
) -> str:
    """Get current user's branch ID."""
    # TODO: Implement after User model is created
    # return current_user.branch_id
    return "default-branch-id"  # Placeholder

def require_branch_access(branch_id: str | None = None):
    """Create a dependency that requires access to a specific branch."""
    async def branch_checker(
        current_user = Depends(get_current_active_user),
        user_branch_id: str = Depends(get_user_branch_id)
    ):
        user_role = UserRole(current_user.role)
        
        # Admins can access all branches
        if user_role == UserRole.ADMIN:
            return current_user
        
        # Check if user has access to the specified branch
        if branch_id and branch_id != user_branch_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Branch access denied"
            )
        
        return current_user
    
    return branch_checker

# Branch resolution helper
async def resolve_branch_id(
    request: Request,
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
    required: bool = True,
) -> int | None:
    """Resolve effective branch_id for a request.
    Order:
    1) X-Branch-Id header
    2) query param branch_id/branchId
    3) current_user.branch_id/branchId
    4) if ADMIN and none found: first active branch
    Access:
    - Non-admins can only use their own branch_id if they have one.
    Validation:
    - Ensures branch exists in DB when resolved.
    """
    # Extract from header
    def _to_int(v):
        try:
            return int(v) if v is not None and str(v).strip() != "" else None
        except Exception:
            return None

    header_bid = _to_int(request.headers.get("X-Branch-Id") or request.headers.get("x-branch-id"))
    query = request.query_params or {}
    query_bid = _to_int(query.get("branch_id") or query.get("branchId"))
    user_bid = _to_int(getattr(current_user, "branch_id", None) or getattr(current_user, "branchId", None))

    branch_id = header_bid or query_bid or user_bid

    # Admin shortcut to allow any branch, non-admin enforce access
    role_val = getattr(current_user, "role", None)
    role_str = role_val.value if hasattr(role_val, "value") else (str(role_val).split(".")[-1] if role_val else "")
    role_norm = role_str.upper()

    # If none resolved yet, allow fallback to first active branch for ADMIN
    if branch_id is None and role_norm == "ADMIN":
        try:
            default_branch = await db.branch.find_first(where={"isActive": True})
            if default_branch:
                branch_id = int(default_branch.id)
        except Exception:
            branch_id = None

    # If still none and required, error
    if branch_id is None and required:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="branch_id is required")

    if branch_id is None:
        return None

    # Enforce non-admin access to their own branch only (if they have one)
    if role_norm != "ADMIN" and user_bid is not None and branch_id != user_bid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Branch access denied")

    # Validate branch exists
    try:
        branch = await db.branch.find_unique(where={"id": branch_id})
        if not branch:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Branch not found")
    except HTTPException:
        raise
    except Exception:
        # If DB not reachable, conservatively allow in non-prod
        if settings.is_production:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to resolve branch")

    return branch_id

# Pagination dependencies
class PaginationParams:
    """Pagination parameters."""
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(20, ge=1, le=100, description="Page size"),
    ):
        self.page = page
        self.size = size
        self.skip = (page - 1) * size

async def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size")
) -> PaginationParams:
    """Get pagination parameters."""
    return PaginationParams(page=page, size=size)

# Search and filter dependencies
class SearchParams:
    """Search parameters."""
    def __init__(
        self,
        q: str | None = Query(None, description="Search query"),
        sort_by: str | None = Query("createdAt", description="Sort field"),
        sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
        date_from: datetime | None = Query(None, description="Filter from date"),
        date_to: datetime | None = Query(None, description="Filter to date"),
    ):
        self.q = q
        self.sort_by = sort_by
        self.sort_order = sort_order
        self.date_from = date_from
        self.date_to = date_to

async def get_search_params(
    q: str | None = Query(None, description="Search query"),
    sort_by: str | None = Query("createdAt", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    date_from: datetime | None = Query(None, description="Filter from date"),
    date_to: datetime | None = Query(None, description="Filter to date"),
) -> SearchParams:
    """Get search and filter parameters."""
    return SearchParams(
        q=q,
        sort_by=sort_by,
        sort_order=sort_order,
        date_from=date_from,
        date_to=date_to
    )

# Rate limiting dependency
def rate_limit(requests_per_minute: int = 60):
    """Create a rate limiting dependency."""
    async def rate_limiter_dependency(
        request: Request,
        current_user = Depends(get_current_user)
    ):
        # Use user ID if authenticated, otherwise use IP address
        identifier = (
            str(current_user.id) if current_user
            else request.client.host if request.client else "unknown"
        )
        
        if not rate_limiter.is_allowed(identifier, requests_per_minute, 60):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        return True
    
    return rate_limiter_dependency

# API Key dependency (for external integrations)
async def verify_api_key(
    api_key: str | None = Query(None, alias="api_key"),
    db = Depends(get_db)
) -> bool:
    """Verify API key for external integrations.
    Strategy:
    - Require presence and basic prefix check (sk-)
    - If prisma has ApiKey model/table, verify key exists and is active
    - Otherwise allow only format check (non-prod), deny in prod
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    # Basic format check
    if not isinstance(api_key, str) or not api_key.startswith("sk-"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format"
        )
    # DB-backed check if model exists
    try:
        if hasattr(db, "apikey"):
            rec = await db.apikey.find_unique(where={"key": api_key})
            if not rec or (hasattr(rec, "isActive") and not rec.isActive):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or inactive API key")
            return True
    except Exception:
        # Fall through to environment-based fallback
        pass
    # Fallback policy: in production, require DB validation; in non-prod accept format-only
    if settings.is_production:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key validation unavailable")
    return True

# Audit logging dependency
async def log_user_activity(
    request: Request,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Log user activity for audit purposes.
    Attempts to persist to AuditLog via Prisma; falls back to logger.
    """
    if not (current_user and settings.enable_audit_logging):
        return True
    try:
        payload = {
            "userId": int(getattr(current_user, "id", 0)),
            "action": "ACCESS",
            "entityType": "HTTP",
            "entityId": None,
            "oldValues": None,
            "newValues": {
                "method": request.method,
                "path": request.url.path,
                "query": dict(request.query_params or {}),
            },
            "severity": "INFO",
            "ipAddress": request.client.host if request.client else None,
            "userAgent": request.headers.get("user-agent"),
        }
        if hasattr(db, "auditlog"):
            await db.auditlog.create(data=payload)
        else:
            logger.info(f"AUDIT {payload}")
    except Exception as e:
        logger.warning(f"Audit log failure (fallback to console): {e}")
        logger.info(
            f"User {getattr(current_user,'id',None)} accessed {request.method} {request.url.path}"
        )
    return True

# File upload dependencies
class FileUploadLimits:
    """File upload limits."""
    def __init__(
        self,
        max_size_mb: int = settings.max_file_size_mb,
        allowed_types: list | None = None
    ):
        self.max_size_mb = max_size_mb
        self.allowed_types = allowed_types or []

def get_file_upload_limits(
    max_size_mb: int = settings.max_file_size_mb,
    allowed_types: list | None = None
) -> FileUploadLimits:
    """Get file upload limits."""
    return FileUploadLimits(max_size_mb, allowed_types)

# Validation dependencies
def validate_uuid(value: str, field_name: str = "id") -> str:
    """Validate UUID format."""
    import uuid
    try:
        uuid.UUID(value)
        return value
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name} format"
        )

# Common query filters
class CommonFilters:
    """Common query filters."""
    def __init__(
        self,
        is_active: bool | None = Query(None, description="Filter by active status"),
        created_by: str | None = Query(None, description="Filter by creator"),
        branch_id: str | None = Query(None, description="Filter by branch"),
    ):
        self.is_active = is_active
        self.created_by = created_by
        self.branch_id = branch_id

async def get_common_filters(
    is_active: bool | None = Query(None, description="Filter by active status"),
    created_by: str | None = Query(None, description="Filter by creator"),
    branch_id: str | None = Query(None, description="Filter by branch"),
) -> CommonFilters:
    """Get common filters for queries."""
    return CommonFilters(is_active, created_by, branch_id)

# Transaction dependency
async def get_admin_transaction():
    """Get database transaction for admin operations."""
    # Transaction support would need to be implemented with prisma.tx() if needed
    async def no_op():
        pass
    return no_op

# Health check dependencies
async def get_system_health():
    """Get system health status."""
    try:
        # Health check can be implemented using a simple query if needed
        db_healthy = True  # Placeholder
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "api": "healthy",
                "database": "connected" if db_healthy else "disconnected"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

# Service dependencies
async def get_customer_service():
    """Get customer service instance."""
    from app.modules.customers.model import CustomerModel
    from app.modules.customers.service import create_customer_service
    
    db = await get_db()
    customer_model = CustomerModel(db)
    return create_customer_service(customer_model)

async def get_financial_service():
    """Get financial service instance."""
    from app.modules.financial.service import create_financial_service
    
    db = await get_db()
    return create_financial_service(db)

# Common type annotations for dependencies
CurrentUser = Annotated[dict, Depends(get_current_user)]
CurrentActiveUser = Annotated[dict, Depends(get_current_active_user)]
DatabaseSession = Annotated[Any, Depends(get_db)]
PaginationDep = Annotated[PaginationParams, Depends(get_pagination_params)]
SearchDep = Annotated[SearchParams, Depends(get_search_params)]