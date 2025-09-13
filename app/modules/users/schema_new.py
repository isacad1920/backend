"""
User module Pydantic schemas for request/response validation.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, field_validator, Field
from datetime import datetime
from enum import Enum
import re

from app.core.config import UserRole

class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    LOCKED = "LOCKED"

# Base schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str = Field(..., min_length=1, max_length=50, description="Username")
    email: Optional[EmailStr] = Field(None, description="User email address")
    firstName: str = Field(..., min_length=1, max_length=50, description="First name")
    lastName: str = Field(..., min_length=1, max_length=50, description="Last name")
    role: UserRole = Field(..., description="User role")
    isActive: bool = Field(True, description="User active status")
    branchId: Optional[int] = Field(None, description="Branch ID")
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        """Additional email validation."""
        if v:
            # You can add domain restrictions here if needed
            pass
        return v
    
    model_config = {
        "use_enum_values": True,
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "email": "john.doe@example.com",
                "firstName": "John", 
                "lastName": "Doe",
                "phone_number": "+1234567890",
                "role": "CASHIER",
                "isActive": True
            }
        }
    }

# Request schemas
class UserCreateSchema(BaseModel):
    """Schema for creating a new user."""
    username: str = Field(..., min_length=1, max_length=50, description="Username")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password")
    firstName: str = Field(..., min_length=1, max_length=50, description="First name", alias="first_name")
    lastName: str = Field(..., min_length=1, max_length=50, description="Last name", alias="last_name")
    role: UserRole = Field(..., description="User role")
    isActive: bool = Field(True, description="User active status", alias="is_active")
    branchId: Optional[int] = Field(None, description="Branch ID", alias="branch_id")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password strength."""
        from app.core.security import PasswordValidator
        validation = PasswordValidator.validate_password(v)
        if not validation['valid']:
            raise ValueError(f"Password validation failed: {', '.join(validation['errors'])}")
        return v
    
    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "password": "SecurePass123!",
                "firstName": "John",
                "lastName": "Doe",
                "role": "CASHIER",
                "branchId": 1,
                "isActive": True
            }
        }
    }

class UserUpdateSchema(BaseModel):
    """Schema for updating user information."""
    username: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    firstName: Optional[str] = Field(None, alias="first_name")
    lastName: Optional[str] = Field(None, alias="last_name")
    role: Optional[UserRole] = None
    isActive: Optional[bool] = Field(None, alias="is_active")
    branchId: Optional[int] = Field(None, alias="branch_id")
    
    model_config = {
        "populate_by_name": True
    }

# Response schemas  
class UserResponseSchema(BaseModel):
    """Schema for user response data."""
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: Optional[str] = Field(None, description="Email")
    firstName: str = Field(..., description="First name")
    lastName: str = Field(..., description="Last name")
    role: str = Field(..., description="User role")
    isActive: bool = Field(..., description="Active status")
    branchId: Optional[int] = Field(None, description="Branch ID")
    createdAt: datetime = Field(..., description="Created timestamp")
    updatedAt: datetime = Field(..., description="Updated timestamp")
    
    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }

class UserPasswordChangeSchema(BaseModel):
    """Schema for changing user password."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., 
        min_length=8, 
        max_length=128, 
        description="New password"
    )
    confirm_password: str = Field(..., description="Confirm new password")
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        """Validate that passwords match."""
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        """Validate new password strength."""
        from app.core.security import PasswordValidator
        validation = PasswordValidator.validate_password(v)
        if not validation['valid']:
            raise ValueError(f"Password validation failed: {', '.join(validation['errors'])}")
        return v

class UserPasswordResetRequestSchema(BaseModel):
    """Schema for password reset request."""
    email: EmailStr = Field(..., description="User email address")

class UserPasswordResetSchema(BaseModel):
    """Schema for password reset."""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(
        ..., 
        min_length=8, 
        max_length=128, 
        description="New password"
    )
    confirm_password: str = Field(..., description="Confirm new password")
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        """Validate that passwords match."""
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        """Validate new password strength."""
        from app.core.security import PasswordValidator
        validation = PasswordValidator.validate_password(v)
        if not validation['valid']:
            raise ValueError(f"Password validation failed: {', '.join(validation['errors'])}")
        return v

# Authentication schemas
class LoginRequestSchema(BaseModel):
    """Schema for login request."""
    username: Optional[str] = Field(None, description="Username")
    email: Optional[EmailStr] = Field(None, description="Email address")
    password: str = Field(..., description="Password")
    remember_me: bool = Field(False, description="Remember me option")
    
    @field_validator('username')
    @classmethod
    def validate_login_fields(cls, v, info):
        """Ensure either username or email is provided."""
        if not v and not info.data.get('email'):
            raise ValueError('Either username or email must be provided')
        return v

class LoginResponseSchema(BaseModel):
    """Schema for login response."""
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponseSchema = Field(..., description="User information")

class RefreshTokenRequestSchema(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str = Field(..., description="Refresh token")

# List response schemas
class UserListResponseSchema(BaseModel):
    """Schema for user list response."""
    users: List[UserResponseSchema] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(1, description="Current page number")
    limit: int = Field(10, description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

class UserDetailResponseSchema(BaseModel):
    """Schema for detailed user response with additional information."""
    id: int
    username: str
    email: Optional[str]
    firstName: str
    lastName: str
    role: UserRole
    isActive: bool
    branchId: Optional[int]
    createdAt: datetime
    updatedAt: datetime
    lastLogin: Optional[datetime] = None
    permissions: List[str] = Field(default_factory=list)
    
    model_config = {
        "from_attributes": True
    }
