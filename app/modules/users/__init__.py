"""
User module package initialization.
"""
from .model import UserModel, create_user_model
from .routes import auth_router, router
from .schema import (
    LoginRequestSchema,
    LoginResponseSchema,
    UserCreateSchema,
    UserDetailResponseSchema,
    UserListResponseSchema,
    UserResponseSchema,
    UserStatsSchema,
    UserUpdateSchema,
)
from .service import UserService, create_user_service

__all__ = [
    "router",
    "auth_router", 
    "UserService",
    "create_user_service",
    "UserModel",
    "create_user_model",
    "UserCreateSchema",
    "UserUpdateSchema", 
    "UserResponseSchema",
    "LoginRequestSchema",
    "LoginResponseSchema",
    "UserListResponseSchema",
    "UserDetailResponseSchema",
    "UserStatsSchema"
]
