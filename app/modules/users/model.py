"""
User model interface and database operations.
This module provides a clean interface to interact with the Prisma User model.
"""
import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from app.core.config import UserRole
from app.core.exceptions import DatabaseError
from generated.prisma import Prisma
from generated.prisma.models import User

logger = logging.getLogger(__name__)

class UserModel:
    """User model interface for database operations."""
    
    def __init__(self, db: Prisma):
        self.db = db  # Adjusted to remove Prisma type hint
    
    async def create(
        self,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        role: UserRole,
        branch_id: str,
        phone_number: str | None = None,
        is_active: bool = True,
        created_by_id: str | None = None
    ) -> User:
        """Create a new user."""
        try:
            user_data = {
                "id": str(uuid4()),
                "email": email,
                # Prefer camelCase keys for Prisma client; fall back fields may be mapped in schema
                "hashedPassword": password_hash,
                "firstName": first_name,
                "lastName": last_name,
                "phoneNumber": phone_number,
                "role": role.value if isinstance(role, UserRole) else role,
                "branchId": branch_id,
                "isActive": is_active,
                "status": "ACTIVE",
                "loginAttempts": 0,
                "createdById": created_by_id,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            
            user = await self.db.user.create(data=user_data)
            return user
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise DatabaseError(
                detail="Failed to create user in database",
                error_code="USER_CREATION_ERROR"
            )
    
    async def get_by_id(self, user_id: str, include_relations: bool = False) -> User | None:
        """Get user by ID."""
        try:
            include_clause = None
            if include_relations:
                include_clause = {
                    "branch": True,
                    "created_by": True,
                    "created_users": True
                }
            
            user = await self.db.user.find_unique(
                where={"id": user_id},
                include=include_clause
            )
            
            return user
            
        except Exception as e:
            logger.error(f"Failed to get user by ID {user_id}: {e}")
            return None
    
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        try:
            user = await self.db.user.find_unique(
                where={"email": email}
            )
            
            return user
            
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            return None
    
    async def update(
        self,
        user_id: str,
        data: dict[str, Any]
    ) -> User | None:
        """Update user."""
        try:
            # Add updated timestamp (Prisma camelCase)
            data["updatedAt"] = datetime.utcnow()
            
            user = await self.db.user.update(
                where={"id": user_id},
                data=data
            )
            
            return user
            
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            return None
    
    async def delete(self, user_id: str) -> bool:
        """Soft delete user."""
        try:
            await self.db.user.update(
                where={"id": user_id},
                data={
                    "isActive": False,
                    "status": "INACTIVE",
                    "updatedAt": datetime.utcnow()
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            return False
    
    async def find_many(
        self,
        skip: int = 0,
        take: int = 20,
        where: dict[str, Any] | None = None,
        order_by: dict[str, str] | None = None,
        include_relations: bool = False
    ) -> list[User]:
        """Find multiple users with filters."""
        try:
            include_clause = None
            if include_relations:
                include_clause = {
                    "branch": True,
                    "created_by": True
                }
            
            users = await self.db.user.find_many(
                where=where or {},
                skip=skip,
                take=take,
                order=order_by or {"createdAt": "desc"},
                include=include_clause
            )
            
            return users
            
        except Exception as e:
            logger.error(f"Failed to find users: {e}")
            return []
    
    async def count(self, where: dict[str, Any] | None = None) -> int:
        """Count users with filters."""
        try:
            count = await self.db.user.count(
                where=where or {}
            )
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to count users: {e}")
            return 0
    
    async def exists_by_email(self, email: str, exclude_user_id: str | None = None) -> bool:
        """Check if user exists by email."""
        try:
            where_clause = {"email": email}
            
            if exclude_user_id:
                where_clause["NOT"] = {"id": exclude_user_id}
            
            user = await self.db.user.find_first(
                where=where_clause
            )
            
            return user is not None
            
        except Exception as e:
            logger.error(f"Failed to check email existence: {e}")
            return False
    
    async def get_users_by_branch(self, branch_id: str) -> list[User]:
        """Get all users in a branch."""
        try:
            users = await self.db.user.find_many(
                where={"branchId": branch_id, "isActive": True}
            )
            
            return users
            
        except Exception as e:
            logger.error(f"Failed to get users by branch {branch_id}: {e}")
            return []
    
    async def get_users_by_role(self, role: UserRole) -> list[User]:
        """Get all users with specific role."""
        try:
            users = await self.db.user.find_many(
                where={"role": role.value, "isActive": True}
            )
            
            return users
            
        except Exception as e:
            logger.error(f"Failed to get users by role {role}: {e}")
            return []
    
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp."""
        try:
            await self.db.user.update(
                where={"id": user_id},
                data={"lastLoginAt": datetime.utcnow()}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update last login for user {user_id}: {e}")
            return False
    
    async def increment_login_attempts(self, user_id: str) -> bool:
        """Increment failed login attempts."""
        try:
            user = await self.db.user.find_unique(
                where={"id": user_id}
            )
            
            if not user:
                return False
            
            login_attempts = (getattr(user, "loginAttempts", getattr(user, "login_attempts", 0)) or 0) + 1
            locked_until = None
            
            # Lock account after 5 failed attempts
            if login_attempts >= 5:
                from datetime import timedelta
                locked_until = datetime.utcnow() + timedelta(minutes=15)

            await self.db.user.update(
                where={"id": user_id},
                data={
                    "loginAttempts": login_attempts,
                    "lockedUntil": locked_until,
                    "updatedAt": datetime.utcnow()
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to increment login attempts for user {user_id}: {e}")
            return False
    
    async def reset_login_attempts(self, user_id: str) -> bool:
        """Reset failed login attempts."""
        try:
            await self.db.user.update(
                where={"id": user_id},
                data={
                    "loginAttempts": 0,
                    "lockedUntil": None,
                    "updatedAt": datetime.utcnow(),
                },
            )

            return True

        except Exception as e:
            logger.error(f"Failed to reset login attempts for user {user_id}: {e}")
            return False
    
    async def is_account_locked(self, user_id: str) -> bool:
        """Check if user account is locked."""
        try:
            user = await self.db.user.find_unique(
                where={"id": user_id}
            )
            
            locked_until_val = getattr(user, "lockedUntil", getattr(user, "locked_until", None))
            if not user or not locked_until_val:
                return False
            
            return locked_until_val > datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to check if account is locked for user {user_id}: {e}")
            return False
    
    async def update_password(self, user_id: str, password_hash: str) -> bool:
        """Update user password."""
        try:
            await self.db.user.update(
                where={"id": user_id},
                data={
                    "hashedPassword": password_hash,
                    "updatedAt": datetime.utcnow(),
                },
            )

            return True

        except Exception as e:
            logger.error(f"Failed to update password for user {user_id}: {e}")
            return False
    
    async def get_user_statistics(self) -> dict[str, Any]:
        """Get user statistics."""
        try:
            # Total users
            total_users = await self.db.user.count()
            
            # Active users
            active_users = await self.db.user.count(
                where={"isActive": True}
            )
            
            # Users by role
            roles = ["ADMIN", "MANAGER", "CASHIER", "INVENTORY_CLERK", "ACCOUNTANT"]
            users_by_role = {}
            
            for role in roles:
                count = await self.db.user.count(
                    where={"role": role}
                )
                users_by_role[role] = count
            
            # Recent logins (last 24 hours)
            from datetime import timedelta
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_logins = await self.db.user.count(
                where={
                    "lastLoginAt": {"gte": yesterday}
                }
            )
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "users_by_role": users_by_role,
                "recent_logins": recent_logins
            }
            
        except Exception as e:
            logger.error(f"Failed to get user statistics: {e}")
            return {}
    
    async def search_users(
        self,
        search_query: str,
        skip: int = 0,
        take: int = 20
    ) -> list[User]:
        """Search users by name or email."""
        try:
            users = await self.db.user.find_many(
                where={
                    "OR": [
                        {"firstName": {"contains": search_query, "mode": "insensitive"}},
                        {"lastName": {"contains": search_query, "mode": "insensitive"}},
                        {"email": {"contains": search_query, "mode": "insensitive"}}
                    ]
                },
                skip=skip,
                take=take,
                order={"createdAt": "desc"}
            )
            
            return users
            
        except Exception as e:
            logger.error(f"Failed to search users: {e}")
            return []
    
    async def bulk_update(
        self,
        user_ids: list[str],
        data: dict[str, Any]
    ) -> tuple[int, int]:
        """Bulk update users. Returns (success_count, error_count)."""
        success_count = 0
        error_count = 0

        # Add updated timestamp
        data["updatedAt"] = datetime.utcnow()

        for user_id in user_ids:
            try:
                result = await self.db.user.update(
                    where={"id": user_id},
                    data=data,
                )

                if result:
                    success_count += 1
                else:
                    error_count += 1

            except Exception as e:
                logger.error(f"Failed to update user {user_id} in bulk: {e}")
                error_count += 1

        return success_count, error_count
    
    async def get_active_users_count_by_branch(self) -> dict[str, int]:
        """Get count of active users by branch."""
        try:
            # This is a complex query that might need raw SQL
            # For now, we'll do it in Python
            users = await self.db.user.find_many(
                where={"isActive": True},
                include={"branch": True}
            )
            
            branch_counts = {}
            for user in users:
                branch_name = user.branch.name if user.branch else "Unknown"
                branch_counts[branch_name] = branch_counts.get(branch_name, 0) + 1
            
            return branch_counts
            
        except Exception as e:
            logger.error(f"Failed to get users count by branch: {e}")
            return {}
    
    async def deactivate_inactive_users(self, days_inactive: int = 90) -> int:
        """Deactivate users who haven't logged in for specified days."""
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)
            
            # Update users who haven't logged in since cutoff date
            result = await self.db.user.update_many(
                where={
                    "OR": [
                        {"lastLoginAt": {"lt": cutoff_date}},
                        {"lastLoginAt": None, "createdAt": {"lt": cutoff_date}}
                    ],
                    "isActive": True
                },
                data={
                    "isActive": False,
                    "status": "INACTIVE",
                    "updatedAt": datetime.utcnow()
                }
            )
            
            return result.count if hasattr(result, 'count') else 0
            
        except Exception as e:
            logger.error(f"Failed to deactivate inactive users: {e}")
            return 0
    
    async def validate_user_permissions(
        self,
        user_id: str,
        required_permissions: list[str]
    ) -> bool:
        """Validate if user has required permissions based on role."""
        try:
            user = await self.db.user.find_unique(
                where={"id": user_id}
            )
            
            if not user or not getattr(user, "isActive", getattr(user, "is_active", False)):
                return False
            
            from app.core.permissions import get_user_effective_permissions
            user_role = UserRole(user.role)
            if user_role == UserRole.ADMIN:
                return True
            effective = await get_user_effective_permissions(user.id, self.db)
            return all(p in effective for p in required_permissions)
            
        except Exception as e:
            logger.error(f"Failed to validate permissions for user {user_id}: {e}")
            return False

# Factory function
def create_user_model(db) -> UserModel:  # Adjusted to remove Prisma type hint
    return UserModel(db)