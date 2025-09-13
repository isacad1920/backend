"""
Security utilities for authentication, authorization, and password management.
"""
from typing import Optional, Dict, Any, List, Union, Set
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import ValidationError
import secrets
import string
import re
from enum import Enum
import hashlib
import hmac
from app.core.config import settings, UserRole
import logging
from generated.prisma import Prisma

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt", "bcrypt_sha256"],
    deprecated="auto",
    bcrypt__rounds=12
)

# JWT Bearer token scheme
security = HTTPBearer(auto_error=False)

class TokenType(str, Enum):
    """Types of JWT tokens."""
    ACCESS = "access"
    REFRESH = "refresh"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"

class PasswordValidator:
    """Password validation utility."""
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """
        Validate password strength.
        
        Returns:
            Dict with 'valid' boolean and 'errors' list
        """
        errors = []
        
        if len(password) < settings.pwd_min_length:
            errors.append(f"Password must be at least {settings.pwd_min_length} characters long")
        
        if settings.pwd_require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if settings.pwd_require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if settings.pwd_require_numbers and not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        if settings.pwd_require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        # Check for common passwords
        common_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if password.lower() in common_passwords:
            errors.append("Password is too common")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'strength': PasswordValidator._calculate_strength(password)
        }
    
    @staticmethod
    def _calculate_strength(password: str) -> str:
        """Calculate password strength score."""
        score = 0
        
        # Length bonus
        score += min(len(password) * 2, 20)
        
        # Character variety bonus
        if re.search(r'[a-z]', password):
            score += 5
        if re.search(r'[A-Z]', password):
            score += 5
        if re.search(r'\d', password):
            score += 5
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 10
        
        # Deduct for patterns
        if re.search(r'(.)\1{2,}', password):  # Repeated characters
            score -= 10
        if re.search(r'(012|123|234|345|456|567|678|789|890)', password):  # Sequential numbers
            score -= 10
        
        if score >= 50:
            return "Strong"
        elif score >= 30:
            return "Medium"
        else:
            return "Weak"
    
    @staticmethod
    def generate_password(length: int = 12) -> str:
        """Generate a secure random password."""
        if length < 8:
            length = 8
        
        # Ensure at least one character from each required category
        password = []
        
        if settings.pwd_require_uppercase:
            password.append(secrets.choice(string.ascii_uppercase))
        if settings.pwd_require_lowercase:
            password.append(secrets.choice(string.ascii_lowercase))
        if settings.pwd_require_numbers:
            password.append(secrets.choice(string.digits))
        if settings.pwd_require_special:
            password.append(secrets.choice('!@#$%^&*(),.?":{}|<>'))
        
        # Fill the rest with random characters
        all_chars = string.ascii_letters + string.digits + '!@#$%^&*(),.?":{}|<>'
        for _ in range(length - len(password)):
            password.append(secrets.choice(all_chars))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        return ''.join(password)

class PasswordManager:
    """Password hashing and verification manager."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    @staticmethod
    def need_rehash(hashed_password: str) -> bool:
        """Check if password needs to be rehashed (for security updates)."""
        return pwd_context.needs_update(hashed_password)

class JWTManager:
    """JWT token management utility with optional persistent blacklist (RevokedToken)."""
    _db_enabled: bool = True  # Disabled on first failure
    
    @staticmethod
    def create_access_token(
        subject: Union[str, Any],
        expires_delta: Optional[timedelta] = None,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create an access token."""
        # Determine expiration time
        if expires_delta is not None:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.access_token_expire_minutes
            )
        
        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "type": TokenType.ACCESS,
            "iat": datetime.utcnow()
        }
        
        if additional_claims:
            to_encode.update(additional_claims)
        
        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(subject: Union[str, Any]) -> str:
        """Create a refresh token."""
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        
        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "type": TokenType.REFRESH,
            "iat": datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        return encoded_jwt
    
    @staticmethod
    def create_password_reset_token(email: str) -> str:
        """Create a password reset token."""
        expire = datetime.utcnow() + timedelta(hours=1)
        
        to_encode = {
            "exp": expire,
            "sub": email,
            "type": TokenType.PASSWORD_RESET,
            "iat": datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(
        token: str,
        expected_type: Optional[TokenType] = None
    ) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            
            # Check token type if specified
            if expected_type and payload.get("type") != expected_type:
                return None
            
            return payload
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
    
    @staticmethod
    def _extract_jti(token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload.get("jti") or hashlib.sha256(token.encode()).hexdigest()
        except Exception:
            return hashlib.sha256(token.encode()).hexdigest()

    @classmethod
    async def blacklist_token(cls, token: str, reason: str = "revoked", user_id: Optional[int] = None):
        if not token:
            return
        jti = cls._extract_jti(token)
        _TOKEN_BLACKLIST.add(jti)
        if settings.environment.upper() == "TEST":
            return
        if not cls._db_enabled:
            return
        try:
            db = Prisma()
            if not db.is_connected():
                await db.connect()
            # Upsert style: ignore if exists
            existing = await db.revokedtoken.find_unique(where={"jti": jti})
            if not existing:
                expire = datetime.utcnow() + timedelta(days=7)
                await db.revokedtoken.create(data={
                    "jti": jti,
                    "token": token,
                    "reason": reason,
                    "expiresAt": expire,
                    "revokedBy": user_id
                })
        except Exception as e:
            logger.warning(f"Disabling persistent blacklist (fallback to memory): {e}")
            cls._db_enabled = False

    @classmethod
    async def is_token_blacklisted(cls, token: str) -> bool:
        jti = cls._extract_jti(token)
        if jti in _TOKEN_BLACKLIST:
            return True
        if settings.environment.upper() == "TEST" or not cls._db_enabled:
            return False
        try:
            db = Prisma()
            if not db.is_connected():
                await db.connect()
            rec = await db.revokedtoken.find_unique(where={"jti": jti})
            return rec is not None
        except Exception:
            cls._db_enabled = False
            return jti in _TOKEN_BLACKLIST

    @staticmethod
    def is_token_blacklisted_sync(token: str) -> bool:
        jti = JWTManager._extract_jti(token) or token
        return jti in _TOKEN_BLACKLIST

    @staticmethod
    def blacklist_token(token: str) -> None:
        """Add token to blacklist."""
        _TOKEN_BLACKLIST.add(token)

# Module-level in-memory token blacklist (non-persistent; suitable for tests/dev only)
_TOKEN_BLACKLIST: Set[str] = set()

class PermissionManager:
    """Manage user permissions and role-based access control."""
    
    ROLE_PERMISSIONS = {
        UserRole.ADMIN: [
            # User management
            "users:read", "users:write", "users:delete",
            # Branch management  
            "branches:read", "branches:write", "branches:delete",
            # Product management
            "products:read", "products:write", "products:delete",
            # Sales management
            "sales:read", "sales:write", "sales:delete",
            # Account management
            "accounts:read", "accounts:write", "accounts:delete",
            # Reports
            "reports:read", "reports:generate",
            # System & Audit
            "audit:read", "system:manage",
            # Inventory (Critical - was missing!)
            "inventory:read", "inventory:write", "inventory:delete",
            # Stock management
            "stock:read", "stock:write", "stock:delete",
            # Customer management
            "customers:read", "customers:write", "customers:delete",
            # Categories
            "categories:read", "categories:write", "categories:delete",
            # Payments
            "payments:read", "payments:write", "payments:delete",
            # Journal entries
            "journal:read", "journal:write", "journal:delete",
            # Notifications
            "notifications:read", "notifications:write", "notifications:delete",
            # Permissions management
            "permissions:read", "permissions:write", "permissions:delete",
            # Legacy permissions
            "view_inventory", "manage_inventory", "view_financial_reports"
        ],
        UserRole.MANAGER: [
            "users:read", "users:write",
            "products:read", "products:write",
            "sales:read", "sales:write",
            "accounts:read", "accounts:write",
            "reports:read", "reports:generate",
            "inventory:read", "inventory:write",
            "view_inventory", "manage_inventory", "view_financial_reports"
        ],
        UserRole.CASHIER: [
            "sales:read", "sales:write",
            "products:read",
            "customers:read", "customers:write",
            "payments:read", "payments:write",
            "view_inventory"
        ],
        UserRole.INVENTORY_CLERK: [
            "products:read", "products:write",
            "inventory:read", "inventory:write",
            "stock:read", "stock:write",
            "categories:read",
            "view_inventory", "manage_inventory"
        ],
        UserRole.ACCOUNTANT: [
            "accounts:read", "accounts:write",
            "sales:read",
            "reports:read", "reports:generate",
            "payments:read",
            "journal:read", "journal:write",
            "view_inventory", "view_financial_reports"
        ]
    }
    
    @classmethod
    def has_permission(cls, user_role: UserRole, permission: str, user_id: Optional[int] = None, 
                      custom_permissions: Optional[List[str]] = None) -> bool:
        """Check if a role has a specific permission with direct role-based checking."""
        
        # ADMIN can do EVERYTHING - no exceptions
        if user_role == UserRole.ADMIN:
            return True
            
        # First check custom permissions (if any)
        if custom_permissions and permission in custom_permissions:
            return True
        
        # Then check role-based permissions
        return permission in cls.ROLE_PERMISSIONS.get(user_role, [])
    
    @classmethod
    def get_user_permissions(cls, user_role: UserRole, custom_permissions: Optional[List[str]] = None) -> List[str]:
        """Get all permissions for a user role including custom permissions."""
        base_permissions = set(cls.ROLE_PERMISSIONS.get(user_role, []))
        
        # Add custom permissions granted by admin
        if custom_permissions:
            base_permissions.update(custom_permissions)
        
        return list(base_permissions)
    
    @classmethod
    def can_access_resource(cls, user_role: UserRole, resource: str, action: str, 
                           custom_permissions: Optional[List[str]] = None) -> bool:
        """Check if user can perform action on resource with direct checking."""
        
        # ADMIN can access ALL resources and perform ALL actions
        if user_role == UserRole.ADMIN:
            return True
            
        permission = f"{resource}:{action}"
        return cls.has_permission(user_role, permission, custom_permissions=custom_permissions)
    
    @classmethod
    def grant_custom_permission(cls, user_id: int, permission: str) -> bool:
        """Grant custom permission to a user (admin only function)."""
        # This would typically save to database
        # For now, we'll add to a class variable for demonstration
        if not hasattr(cls, '_custom_permissions'):
            cls._custom_permissions = {}
        
        if user_id not in cls._custom_permissions:
            cls._custom_permissions[user_id] = []
        
        if permission not in cls._custom_permissions[user_id]:
            cls._custom_permissions[user_id].append(permission)
            return True
        return False
    
    @classmethod
    def revoke_custom_permission(cls, user_id: int, permission: str) -> bool:
        """Revoke custom permission from a user (admin only function)."""
        if not hasattr(cls, '_custom_permissions'):
            return False
        
        if user_id in cls._custom_permissions and permission in cls._custom_permissions[user_id]:
            cls._custom_permissions[user_id].remove(permission)
            return True
        return False
    
    @classmethod
    async def get_custom_permissions(cls, user_id: int, db=None) -> List[str]:
        """Get custom permissions for a user from database."""
        try:
            if not db:
                from ..db.client import prisma
                db = prisma
            
            user_permissions = await db.userpermission.find_many(
                where={"userId": user_id}
            )
            
            custom_perms = []
            for user_perm in user_permissions:
                resource = user_perm.resource
                actions = user_perm.actions  # This is a JSON field
                
                # Convert actions dict to permission strings
                if isinstance(actions, dict):
                    for action, allowed in actions.items():
                        if allowed:
                            custom_perms.append(f"{resource}:{action}")
            
            return custom_perms
            
        except Exception as e:
            logger.error(f"Error getting custom permissions for user {user_id}: {e}")
            # Fallback to in-memory for backwards compatibility
            if not hasattr(cls, '_custom_permissions'):
                cls._custom_permissions = {}
            return cls._custom_permissions.get(user_id, [])
    
    @classmethod
    async def grant_permission(cls, user_id: int, resource: str, action: str, db=None) -> bool:
        """Grant a specific permission to a user in the database."""
        try:
            if not db:
                from ..db.client import prisma
                db = prisma
            
            # Check if user permission record exists for this resource
            existing = await db.userpermission.find_first(
                where={
                    "userId": user_id,
                    "resource": resource
                }
            )
            
            if existing:
                # Update existing permissions
                current_actions = existing.actions if isinstance(existing.actions, dict) else {}
                current_actions[action] = True
                
                await db.userpermission.update(
                    where={"id": existing.id},
                    data={"actions": current_actions}
                )
            else:
                # Create new permission record
                await db.userpermission.create(
                    data={
                        "userId": user_id,
                        "resource": resource,
                        "actions": {action: True}
                    }
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error granting permission {resource}:{action} to user {user_id}: {e}")
            return False
    
    @classmethod
    async def revoke_permission(cls, user_id: int, resource: str, action: str, db=None) -> bool:
        """Revoke a specific permission from a user in the database."""
        try:
            if not db:
                from ..db.client import prisma
                db = prisma
            
            # Find existing permission record
            existing = await db.userpermission.find_first(
                where={
                    "userId": user_id,
                    "resource": resource
                }
            )
            
            if existing and isinstance(existing.actions, dict):
                current_actions = existing.actions.copy()
                current_actions[action] = False
                
                await db.userpermission.update(
                    where={"id": existing.id},
                    data={"actions": current_actions}
                )
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error revoking permission {resource}:{action} from user {user_id}: {e}")
            return False
    
    @classmethod
    def get_all_available_permissions(cls) -> List[str]:
        """Get all available permissions in the system."""
        all_permissions = set()
        for permissions in cls.ROLE_PERMISSIONS.values():
            all_permissions.update(permissions)
        return sorted(list(all_permissions))

class SecurityUtils:
    """General security utilities."""
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a cryptographically secure random token."""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate an API key."""
        return f"sk-{secrets.token_urlsafe(32)}"
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def verify_signature(data: str, signature: str, secret: str) -> bool:
        """Verify HMAC signature."""
        expected_signature = hmac.new(
            secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)
    
    @staticmethod
    def create_signature(data: str, secret: str) -> str:
        """Create HMAC signature."""
        return hmac.new(
            secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def sanitize_input(input_string: str) -> str:
        """Sanitize user input to prevent injection attacks."""
        if not input_string:
            return ""
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '`', '|', ';']
        sanitized = input_string
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None

# Authentication dependencies
async def get_current_user_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """Extract JWT token from request."""
    if not credentials:
        return None
    return credentials.credentials

async def verify_token_dependency(
    token: Optional[str] = Depends(get_current_user_token)
) -> Dict[str, Any]:
    """Verify JWT token dependency."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = JWTManager.verify_token(token, TokenType.ACCESS)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if JWTManager.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

def require_permissions(*permissions: str):
    """Decorator to require specific permissions."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This would typically check user permissions from database
            # Implementation depends on how you store user data
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(*roles: UserRole):
    """Decorator to require specific roles."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This would typically check user role from database
            # Implementation depends on how you store user data
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Rate limiting utilities
class RateLimiter:
    """Rate limiting utility."""
    
    def __init__(self):
        self._requests = {}
    
    def is_allowed(self, identifier: str, limit: int, window_seconds: int) -> bool:
        """Check if request is allowed based on rate limit."""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)
        
        # Clean old requests
        self._requests[identifier] = [
            req_time for req_time in self._requests.get(identifier, [])
            if req_time > window_start
        ]
        
        # Check if under limit
        if len(self._requests.get(identifier, [])) < limit:
            self._requests.setdefault(identifier, []).append(now)
            return True
        
        return False

# Global rate limiter instance
rate_limiter = RateLimiter()

# Security headers middleware
def add_security_headers(response):
    """Add security headers to response."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response