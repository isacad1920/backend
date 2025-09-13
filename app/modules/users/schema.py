"""
User module Pydantic schemas for request/response validation.
"""
from datetime import datetime
from enum import Enum

from pydantic import EmailStr, Field, field_validator

from app.core.base_schema import ApiBaseModel
from app.core.config import UserRole


class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    LOCKED = "LOCKED"

# Base schemas
class UserBase(ApiBaseModel):
    """Base user schema with common fields."""
    username: str = Field(..., min_length=1, max_length=50, description="Username")
    email: EmailStr | None = Field(None, description="User email address")
    firstName: str = Field(..., min_length=1, max_length=50, description="First name")
    lastName: str = Field(..., min_length=1, max_length=50, description="Last name")
    role: UserRole = Field(..., description="User role")
    isActive: bool = Field(True, description="User active status")
    branchId: int | None = Field(None, description="Branch ID")
    
    model_config = {
        "use_enum_values": True,
        "populate_by_name": True
    }

# Request schemas
class UserCreateSchema(ApiBaseModel):
    """Schema for creating a new user."""
    username: str | None = Field(None, min_length=1, max_length=50, description="Username")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password")
    firstName: str = Field(..., alias="first_name", min_length=1, max_length=50, description="First name")
    lastName: str = Field(..., alias="last_name", min_length=1, max_length=50, description="Last name")
    role: UserRole = Field(..., description="User role")
    isActive: bool = Field(True, description="User active status")
    branchId: int | None = Field(None, alias="branch_id", description="Branch ID")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v
    
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": ()
    }

class UserUpdateSchema(ApiBaseModel):
    """Schema for updating user information."""
    username: str | None = Field(None, min_length=1, max_length=50)
    email: EmailStr | None = None
    firstName: str | None = Field(None, alias="first_name")
    lastName: str | None = Field(None, alias="last_name")
    role: UserRole | None = None
    isActive: bool | None = None
    branchId: int | None = Field(None, alias="branch_id")
    
    model_config = {
        "populate_by_name": True,
        "protected_namespaces": ()
    }

# Response schemas  
class UserResponseSchema(ApiBaseModel):
    """Schema for user response data."""
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str | None = Field(None, description="Email")
    firstName: str = Field(..., description="First name")
    lastName: str = Field(..., description="Last name")
    role: str = Field(..., description="User role")
    isActive: bool = Field(..., description="Active status")
    branchId: int | None = Field(None, description="Branch ID")
    createdAt: datetime = Field(..., description="Created timestamp")
    updatedAt: datetime = Field(..., description="Updated timestamp")
    
    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }

class UserPasswordChangeSchema(ApiBaseModel):
    """Schema for changing user password."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        """Validate that passwords match."""
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v

class UserPasswordResetRequestSchema(ApiBaseModel):
    """Schema for password reset request."""
    email: EmailStr = Field(..., description="User email address")

class UserPasswordResetSchema(ApiBaseModel):
    """Schema for password reset."""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        """Validate that passwords match."""
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v

# Authentication schemas
class LoginRequestSchema(ApiBaseModel):
    """Schema for login request."""
    username: str | None = Field(None, description="Username")
    email: EmailStr | None = Field(None, description="Email address")
    password: str = Field(..., description="Password")
    remember_me: bool = Field(False, description="Remember me option")
    
    @field_validator('username')
    @classmethod
    def validate_login_fields(cls, v, info):
        """Ensure either username or email is provided."""
        if not v and not info.data.get('email'):
            raise ValueError('Username or email is required')
        return v

class LoginResponseSchema(ApiBaseModel):
    """Schema for login response."""
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponseSchema = Field(..., description="User information")

class RefreshTokenRequestSchema(ApiBaseModel):
    """Schema for refresh token request."""
    refresh_token: str = Field(..., description="Refresh token")

# List response schemas
class UserListResponseSchema(ApiBaseModel):
    """Schema for user list response."""
    users: list[UserResponseSchema] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(1, description="Current page number")
    limit: int = Field(10, description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

class UserDetailResponseSchema(ApiBaseModel):
    """Schema for detailed user response with additional information."""
    id: int
    username: str
    email: str | None
    firstName: str
    lastName: str
    role: UserRole
    isActive: bool
    branchId: int | None
    createdAt: datetime
    updatedAt: datetime
    lastLogin: datetime | None = None
    permissions: list[str] = Field(default_factory=list)
    
    model_config = {
        "from_attributes": True
    }

# Stats and activity schemas
class UserStatsSchema(ApiBaseModel):
    """Schema for user statistics."""
    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    inactive_users: int = Field(..., description="Number of inactive users")
    new_users_today: int = Field(..., description="New users registered today")
    new_users_this_week: int = Field(..., description="New users registered this week")
    new_users_this_month: int = Field(..., description="New users registered this month")
    users_by_role: dict[str, int] = Field(..., description="Users count by role")
    users_by_branch: dict[str, int] = Field(..., description="Users count by branch")

class UserActivitySchema(ApiBaseModel):
    """Schema for user activity."""
    user_id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    activity_type: str = Field(..., description="Activity type")
    description: str = Field(..., description="Activity description")
    timestamp: datetime = Field(..., description="Activity timestamp")
    ip_address: str | None = Field(None, description="IP address")
    user_agent: str | None = Field(None, description="User agent")

# Bulk operation schemas
class BulkUserUpdateSchema(ApiBaseModel):
    """Schema for bulk user updates."""
    user_ids: list[int] = Field(..., description="List of user IDs")
    updates: UserUpdateSchema = Field(..., description="Updates to apply")

class BulkUserStatusUpdateSchema(ApiBaseModel):
    """Schema for bulk user status updates."""
    user_ids: list[int] = Field(..., description="List of user IDs")
    is_active: bool = Field(..., description="New active status")

class BulkOperationResponseSchema(ApiBaseModel):
    """Schema for bulk operation responses."""
    success_count: int = Field(..., description="Number of successful operations")
    failed_count: int = Field(..., description="Number of failed operations")
    total_count: int = Field(..., description="Total number of operations")
    failed_ids: list[int] = Field(default_factory=list, description="List of failed user IDs")
    errors: list[str] = Field(default_factory=list, description="List of error messages")

class UserProfileUpdateSchema(ApiBaseModel):
    """Schema for user profile updates."""
    firstName: str | None = Field(None, description="First name")
    lastName: str | None = Field(None, description="Last name")
    email: EmailStr | None = Field(None, description="Email")
    phone: str | None = Field(None, description="Phone number")
    
    model_config = {
        "populate_by_name": True
    }
