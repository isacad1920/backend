"""
User service layer for business logic and data operations.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

from app.core.config import UserRole, settings
from app.core.exceptions import (
    AlreadyExistsError,
    AuthenticationError,
    DatabaseError,
    NotFoundError,
    ValidationError,
)
from app.core.security import JWTManager, PasswordManager
from app.modules.users.schema import (
    LoginRequestSchema,
    LoginResponseSchema,
    UserCreateSchema,
    UserDetailResponseSchema,
    UserListResponseSchema,
    UserPasswordChangeSchema,
    UserPasswordResetRequestSchema,
    UserPasswordResetSchema,
    UserResponseSchema,
    UserStatsSchema,
    UserUpdateSchema,
)

logger = logging.getLogger(__name__)

class UserService:
    """User service class for managing user operations."""
    
    def __init__(self, db):
        self.db = db
    
    async def create_user(
        self, 
        user_data: UserCreateSchema, 
        created_by_id: str | None = None
    ) -> UserResponseSchema:
        """Create a new user."""
        try:
            # Check if email already exists
            existing_user = await self.db.user.find_unique(
                where={"email": user_data.email}
            )
            if existing_user:
                raise AlreadyExistsError("Email already registered")
            
            # Verify branch exists if branchId provided
            if user_data.branchId:
                branch = await self.db.branch.find_unique(
                    where={"id": user_data.branchId}
                )
                if not branch:
                    raise NotFoundError("Branch not found")
            
            # Derive username if missing
            base_username = (user_data.username or user_data.email.split("@")[0]).strip() or "user"
            # Ensure unique username by appending numeric suffix on conflict
            username = base_username
            try:
                # Prisma find_unique will return a user if username exists
                existing_by_username = await self.db.user.find_unique(where={"username": username})
                suffix = 1
                while existing_by_username is not None and suffix < 100:
                    candidate = f"{base_username}-{suffix}"
                    existing_by_username = await self.db.user.find_unique(where={"username": candidate})
                    if existing_by_username is None:
                        username = candidate
                        break
                    suffix += 1
            except Exception:
                # Best effort only; proceed with base username
                pass

            # Hash password
            hashed_password = PasswordManager.hash_password(user_data.password)
            
            # Create user
            user = await self.db.user.create(
                data={
                    "username": username,
                    "email": user_data.email,
                    "hashedPassword": hashed_password,
                    "firstName": user_data.firstName,
                    "lastName": user_data.lastName,
                    "role": user_data.role,
                    "branchId": user_data.branchId,
                    "isActive": user_data.isActive
                }
            )
            
            # Log user creation
            if settings.enable_audit_logging:
                await self._log_user_activity(
                    user_id=created_by_id,
                    action="create_user",
                    resource="user",
                    details={"created_user_id": user.id, "email": user.email}
                )
            
            return self._user_to_response_schema(user)
            
        except AlreadyExistsError:
            # Let the route map this to 409
            raise
        except NotFoundError:
            # Let the route map this to 404
            raise
        except ValidationError:
            # Let validation errors be handled by the route
            raise
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise DatabaseError("Failed to create user")
    
    
    async def login(
        self, 
        login_data: LoginRequestSchema,
        client_ip: str = "unknown"
    ) -> LoginResponseSchema:
        """Authenticate user and return tokens."""
        try:
            # Determine identifier precedence: email first if explicitly provided.
            # If only 'username' provided but it contains '@', treat it as an email attempt first.
            identifier = login_data.email or login_data.username
            user = None
            # Primary lookup path
            if login_data.email:
                # Try email, then fallback to username match if email not found (support users who use email as username)
                user = await self.db.user.find_unique(where={"email": login_data.email})
                if not user:
                    user = await self.db.user.find_unique(where={"username": login_data.email})
            elif login_data.username:
                uname = login_data.username
                # If looks like an email, try email first then username
                if '@' in uname:
                    user = await self.db.user.find_unique(where={"email": uname})
                    if not user:
                        user = await self.db.user.find_unique(where={"username": uname})
                else:
                    user = await self.db.user.find_unique(where={"username": uname})
                    if not user and '@' in uname:  # defensive, though branch won't occur
                        user = await self.db.user.find_unique(where={"email": uname})

            if not user:
                raise AuthenticationError("Invalid credentials")

            # Verify password
            if not PasswordManager.verify_password(login_data.password, user.hashedPassword):
                raise AuthenticationError("Invalid credentials")
            
            # Check if user is active
            if not user.isActive:
                raise AuthenticationError("Account is inactive")
            
            # Generate tokens
            jwt_manager = JWTManager()
            access_token = jwt_manager.create_access_token(
                subject=str(user.id), 
                additional_claims={"email": user.email}
            )
            refresh_token = jwt_manager.create_refresh_token(subject=str(user.id))
            
            # Update last login
            await self.db.user.update(
                where={"id": user.id},
                data={"updatedAt": datetime.utcnow()}
            )
            
        # Log login activity
            if settings.enable_audit_logging:
                await self._log_user_activity(
                    user_id=str(user.id),
                    action="login",
            resource="auth",
            details={"client_ip": client_ip, "identifier": identifier, "method": "email" if login_data.email else "username"}
                )
            
            return LoginResponseSchema(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.access_token_expire_minutes * 60,
                user=UserResponseSchema(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    firstName=user.firstName,
                    lastName=user.lastName,
                    role=user.role,
                    isActive=user.isActive,
                    branchId=user.branchId,
                    createdAt=user.createdAt,
                    updatedAt=user.updatedAt
                )
            )
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise AuthenticationError("Login failed")

    async def get_user_by_id(self, user_id: str) -> UserDetailResponseSchema | None:
        """Get user by ID with detailed information."""
        try:
            user = await self.db.user.find_unique(
                where={"id": int(user_id)},
                include={
                    "branch": True
                }
            )
            
            if not user:
                return None
            
            return await self._user_to_detailed_response_schema(user)
            
        except (ValueError, Exception) as e:
            logger.error(f"Failed to get user by ID {user_id}: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> UserResponseSchema | None:
        """Get user by email."""
        try:
            user = await self.db.user.find_unique(
                where={"email": email}
            )
            
            if not user:
                return None
            
            return self._user_to_response_schema(user)
            
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            return None
    
    async def update_user(
        self, 
        user_id: str, 
        user_data: UserUpdateSchema,
        updated_by_id: str | None = None
    ) -> UserResponseSchema | None:
        """Update user information."""
        try:
            # Check if user exists
            existing_user = await self.db.user.find_unique(
                where={"id": int(user_id)}
            )
            if not existing_user:
                raise ValidationError(
                    error_code="NOT_FOUND",
                    detail="User not found"
                )
            
            # Prepare update data
            update_data = {}
            for field, value in user_data.dict(exclude_unset=True).items():
                if field == "role" and isinstance(value, str):
                    update_data[field] = value
                elif value is not None:
                    update_data[field] = value
            
            # Verify branch exists if branchId is being updated
            if "branchId" in update_data:
                branch = await self.db.branch.find_unique(
                    where={"id": update_data["branchId"]}
                )
                if not branch:
                    raise ValidationError(
                        error_code="NOT_FOUND",
                        detail="Branch not found"
                    )
            # Prisma will auto-update updatedAt
            # Update user
            user = await self.db.user.update(
                where={"id": int(user_id)},
                data=update_data
            )
            
            # Log user update
            if settings.enable_audit_logging:
                await self._log_user_activity(
                    user_id=updated_by_id,
                    action="update_user",
                    resource="user",
                    details={"updated_user_id": user_id, "changes": update_data}
                )
            
            return self._user_to_response_schema(user)
            
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            raise ValidationError(
                error_code="DATABASE_ERROR",
                detail="Failed to update user"
            )
    
    async def delete_user(
        self, 
        user_id: str, 
        deleted_by_id: str | None = None
    ) -> bool:
        """Delete user (soft delete by setting is_active to False)."""
        try:
            # Check if user exists
            user = await self.db.user.find_unique(
                where={"id": int(user_id)}
            )
            if not user:
                raise ValidationError(
                    error_code="NOT_FOUND",
                    detail="User not found"
                )
            
            # Soft delete by setting is_active to False
            await self.db.user.update(
                where={"id": int(user_id)},
                data={
                    "isActive": False,
                    "updatedAt": datetime.utcnow()
                }
            )
            
            # Log user deletion
            if settings.enable_audit_logging:
                await self._log_user_activity(
                    user_id=deleted_by_id,
                    action="delete_user",
                    resource="user",
                    details={"deleted_user_id": user_id}
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            return False
    
    async def get_users(
        self,
        page: int = 1,
        size: int = 20,
        search_query: str | None = None,
        role_filter: UserRole | None = None,
        branch_filter: str | None = None,
        status_filter: str | None = None,
        sort_by: str = "createdAt",
        sort_order: str = "desc"
    ) -> UserListResponseSchema:
        """Get paginated list of users with filters."""
        try:
            # Build where clause
            where_clause = {}
            
            if search_query:
                where_clause["OR"] = [
                    {"firstName": {"contains": search_query, "mode": "insensitive"}},
                    {"lastName": {"contains": search_query, "mode": "insensitive"}},
                    {"email": {"contains": search_query, "mode": "insensitive"}},
                    {"username": {"contains": search_query, "mode": "insensitive"}}
                ]
            
            if role_filter:
                where_clause["role"] = role_filter.value
            
            if branch_filter:
                where_clause["branchId"] = branch_filter
            
            if status_filter:
                where_clause["isActive"] = status_filter == "ACTIVE"
            
            # Calculate pagination
            skip = (page - 1) * size
            
            # Get total count
            total = await self.db.user.count(where=where_clause)
            
            # Get users
            order_clause = {sort_by: sort_order}
            users = await self.db.user.find_many(
                where=where_clause,
                skip=skip,
                take=size,
                order=order_clause
            )
            
            # Convert to response schemas
            user_responses = [self._user_to_response_schema(user) for user in users]
            
            # Calculate total_pages
            total_pages = (total + size - 1) // size
            
            return UserListResponseSchema(
                users=user_responses,
                total=total,
                page=page,
                limit=size,
                total_pages=total_pages
            )
            
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            raise DatabaseError("Failed to retrieve users")
    
    async def authenticate_user(
        self, 
        login_data: LoginRequestSchema,
        client_ip: str | None = None,
        user_agent: str | None = None
    ) -> LoginResponseSchema | None:
        """Authenticate user and return login response."""
        try:
            # Get user by email
            user = await self.db.user.find_unique(
                where={"email": login_data.email}
            )
            
            if not user:
                # Log failed login attempt
                await self._log_failed_login(login_data.email, "user_not_found", client_ip)
                return None
            
            # Check if user is active
            if not (getattr(user, "isActive", getattr(user, "is_active", False))) or user.status != "ACTIVE":
                await self._log_failed_login(login_data.email, "user_inactive", client_ip)
                return None
            
            # Check if account is locked
            locked_until_val = getattr(user, "lockedUntil", getattr(user, "locked_until", None))
            if locked_until_val and locked_until_val > datetime.utcnow():
                await self._log_failed_login(login_data.email, "account_locked", client_ip)
                return None
            
            # Verify password
            if not PasswordManager.verify_password(
                login_data.password,
                getattr(user, "hashedPassword", getattr(user, "password_hash", None))
            ):
                # Increment login attempts
                await self._handle_failed_login(user.id)
                await self._log_failed_login(login_data.email, "invalid_password", client_ip)
                return None
            
            # Reset login attempts on successful login
            await self.db.user.update(
                where={"id": user.id},
                data={
                    "loginAttempts": 0,
                    "lockedUntil": None,
                    "lastLoginAt": datetime.utcnow()
                }
            )
            
            # Create tokens
            expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
            if login_data.remember_me:
                expires_delta = timedelta(days=settings.refresh_token_expire_days)
            
            access_token = JWTManager.create_access_token(
                subject=user.id,
                expires_delta=expires_delta,
                additional_claims={
                    "role": user.role,
                    "branch_id": getattr(user, "branch_id", getattr(user, "branchId", None))
                }
            )
            
            refresh_token = JWTManager.create_refresh_token(subject=user.id)
            
            # Log successful login
            if settings.enable_audit_logging:
                await self._log_user_activity(
                    user_id=user.id,
                    action="login",
                    resource="auth",
                    details={
                        "method": "email_password",
                        "remember_me": login_data.remember_me
                    },
                    ip_address=client_ip,
                    user_agent=user_agent
                )
            
            return LoginResponseSchema(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=int(expires_delta.total_seconds()),
                user=self._user_to_response_schema(user)
            )
            
        except Exception as e:
            logger.error(f"Authentication failed for {login_data.email}: {e}")
            return None
    
    async def refresh_token(self, refresh_token: str) -> dict[str, Any] | None:
        """Refresh access token using refresh token."""
        try:
            # Verify refresh token
            payload = JWTManager.verify_token(refresh_token, "REFRESH")
            if not payload:
                return None
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            # Get user
            user = await self.db.user.find_unique(
                where={"id": user_id}
            )
            
            if not user or not getattr(user, "isActive", getattr(user, "is_active", False)):
                return None

            # Create new access token
            access_token = JWTManager.create_access_token(
                subject=user.id,
                additional_claims={
                    "role": user.role,
                    "branch_id": getattr(user, "branch_id", getattr(user, "branchId", None)),
                },
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.access_token_expire_minutes * 60
            }
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return None
    
    async def change_password(
        self, 
        user_id: str, 
        password_data: UserPasswordChangeSchema
    ) -> bool:
        """Change user password."""
        try:
            # Get user
            user = await self.db.user.find_unique(
                where={"id": user_id}
            )
            
            if not user:
                raise ValidationError(
                    error_code="NOT_FOUND",
                    detail="User not found"
                )
            
            # Verify current password
            if not PasswordManager.verify_password(
                password_data.current_password,
                getattr(user, "hashedPassword", getattr(user, "password_hash", None))
            ):
                raise ValidationError(
                    error_code="VALIDATION_ERROR",
                    detail="Current password is incorrect"
                )
            
            # Hash new password
            new_password_hash = PasswordManager.hash_password(
                password_data.new_password
            )
            
            # Update password
            await self.db.user.update(
                where={"id": user_id},
                data={
                    "hashedPassword": new_password_hash,
                    "updatedAt": datetime.utcnow(),
                }
            )
            
            # Log password change
            if settings.enable_audit_logging:
                await self._log_user_activity(
                    user_id=user_id,
                    action="change_password",
                    resource="user",
                    details={"user_id": user_id}
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Password change failed for user {user_id}: {e}")
            return False
    
    async def request_password_reset(
        self, 
        reset_data: UserPasswordResetRequestSchema
    ) -> bool:
        """Request password reset."""
        try:
            # Get user by email
            user = await self.db.user.find_unique(
                where={"email": reset_data.email}
            )
            
            # Always return True for security (don't reveal if email exists)
            if not user:
                return True
            
            # Generate reset token
            reset_token = JWTManager.create_password_reset_token(user.email)
            
            # Store reset token (you might want to store this in database)
            # For now, we'll just log it (in production, send email)
            logger.info(f"Password reset token for {user.email}: {reset_token}")
            
            # Log password reset request
            if settings.enable_audit_logging:
                await self._log_user_activity(
                    user_id=user.id,
                    action="request_password_reset",
                    resource="user",
                    details={"email": user.email}
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Password reset request failed: {e}")
            return False
    
    async def reset_password(
        self, 
        reset_data: UserPasswordResetSchema
    ) -> bool:
        """Reset password using reset token."""
        try:
            # Verify reset token
            payload = JWTManager.verify_token(reset_data.token, "PASSWORD_RESET")
            if not payload:
                raise ValidationError(
                    error_code="VALIDATION_ERROR",
                    detail="Invalid or expired reset token"
                )
            
            email = payload.get("sub")
            if not email:
                raise ValidationError(
                    error_code="VALIDATION_ERROR",
                    detail="Invalid reset token"
                )
            
            # Get user
            user = await self.db.user.find_unique(
                where={"email": email}
            )
            
            if not user:
                raise ValidationError(
                    error_code="NOT_FOUND",
                    detail="User not found"
                )
            
            # Hash new password
            new_password_hash = PasswordManager.hash_password(
                reset_data.new_password
            )
            
            # Update password and reset login attempts
            await self.db.user.update(
                where={"id": user.id},
                data={
                    "hashedPassword": new_password_hash,
                    "loginAttempts": 0,
                    "lockedUntil": None,
                    "updatedAt": datetime.utcnow(),
                }
            )
            
            # Log password reset
            if settings.enable_audit_logging:
                await self._log_user_activity(
                    user_id=user.id,
                    action="reset_password",
                    resource="user",
                    details={"email": user.email}
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            return False
    
    async def get_user_stats(self) -> UserStatsSchema:
        """Get user statistics."""
        try:
            # Total users
            total_users = await self.db.user.count()
            
            # Active users
            active_users = await self.db.user.count(
                where={"isActive": True}
            )
            
            # Users by role
            roles = [role.value for role in UserRole]
            users_by_role = {}
            for role in roles:
                count = await self.db.user.count(
                    where={"role": role}
                )
                users_by_role[role] = count
            
            # Users by branch
            branches = await self.db.branch.find_many()
            users_by_branch = {}
            for branch in branches:
                count = await self.db.user.count(
                    where={"branchId": branch.id}
                )
                users_by_branch[branch.name] = count
            
            # Recent logins (last 24 hours)
            recent_logins = await self.db.user.count(
                where={
                    "lastLoginAt": {
                        "gte": datetime.utcnow() - timedelta(days=1)
                    }
                }
            )
            
            return UserStatsSchema(
                total_users=total_users,
                active_users=active_users,
                users_by_role=users_by_role,
                users_by_branch=users_by_branch,
                recent_logins=recent_logins
            )
            
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            raise ValidationError(
                error_code="DATABASE_ERROR",
                detail="Failed to get user statistics"
            )
    
    # Helper methods
    def _user_to_response_schema(self, user) -> UserResponseSchema:
        """Convert user model to response schema."""
        return UserResponseSchema(
            id=user.id,
            username=user.username,
            email=user.email,
            firstName=user.firstName,
            lastName=user.lastName,
            role=UserRole(user.role),
            isActive=user.isActive,
            branchId=getattr(user, 'branchId', None),
            createdAt=user.createdAt,
            updatedAt=user.updatedAt
        )
    
    async def _user_to_detailed_response_schema(self, user) -> UserDetailResponseSchema:
        """Convert user model to detailed response schema."""
        from app.core.security import PermissionManager
        
        # Get user permissions
        user_role = UserRole(user.role)
        permissions = PermissionManager.get_user_permissions(user_role)
        
        return UserDetailResponseSchema(
            id=user.id,
            username=user.username,
            email=user.email,
            firstName=user.firstName,
            lastName=user.lastName,
            role=user_role,
            isActive=user.isActive,
            branchId=user.branchId,
            createdAt=user.createdAt,
            updatedAt=user.updatedAt,
            permissions=permissions,
            branch_name=user.branch.name if hasattr(user, 'branch') and user.branch else None,
            created_by_name=None,  # Simplified since created_by relation doesn't exist
            login_attempts=getattr(user, 'loginAttempts', 0),
            locked_until=getattr(user, 'lockedUntil', None)
        )
    
    async def _handle_failed_login(self, user_id: str) -> None:
        """Handle failed login attempt."""
        try:
            user = await self.db.user.find_unique(
                where={"id": user_id}
            )
            
            if not user:
                return
            
            login_attempts = (user.login_attempts or 0) + 1
            locked_until = None
            
            # Lock account after max attempts
            if login_attempts >= 5:  # Maximum login attempts
                locked_until = datetime.utcnow() + timedelta(minutes=15)
            
            await self.db.user.update(
                where={"id": user_id},
                data={
                    "login_attempts": login_attempts,
                    "locked_until": locked_until
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to handle failed login for user {user_id}: {e}")
    
    async def _log_failed_login(
        self, 
        email: str, 
        reason: str, 
        client_ip: str | None = None
    ) -> None:
        """Log failed login attempt."""
        if settings.enable_audit_logging:
            logger.warning(f"Failed login attempt - Email: {email}, Reason: {reason}, IP: {client_ip}")
    
    async def _log_user_activity(
        self,
        user_id: str | None,
        action: str,
        resource: str,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> None:
        """Log user activity for audit purposes."""
        try:
            if not settings.enable_audit_logging:
                return
            
            # TODO: Store in audit log table
            # For now, just log to application logs
            log_entry = {
                "user_id": user_id,
                "action": action,
                "resource": resource,
                "details": details,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"User activity: {log_entry}")
            
        except Exception as e:
            logger.error(f"Failed to log user activity: {e}")

async def ensure_demo_user_credentials(db, email: str, password: str) -> None:
    """Ensure a specific user (by email) exists with the given password.

    Only used in development/test flows to keep tests deterministic.
    Idempotent: creates the user if missing or updates password if present.
    """
    try:
        allowed = {"demo@sofinance.com", "test@sofinance.com"}
        if email not in allowed:
            return
        user = await db.user.find_unique(where={"email": email})
        hashed = PasswordManager.hash_password(password)
        if not user:
            await db.user.create(
                data={
                    "username": email.split("@")[0],
                    "email": email,
                    "hashedPassword": hashed,
                    "firstName": "Demo",
                    "lastName": "User",
                    "role": "ADMIN",
                    "isActive": True,
                }
            )
        else:
            await db.user.update(
                where={"id": user.id},
                data={
                    "hashedPassword": hashed,
                    "isActive": True,
                    "role": "ADMIN",
                },
            )
    except Exception as e:
        logger.debug(f"ensure_demo_user_credentials skipped: {e}")

# Factory function to create user service
def create_user_service(db) -> UserService:
    """Create user service instance."""
    return UserService(db)