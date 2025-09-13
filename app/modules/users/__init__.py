"""
User module package initialization.
"""
from .routes import router, auth_router
from .service import UserService, create_user_service
from .schema import (
    UserCreateSchema, UserUpdateSchema, UserResponseSchema,
    LoginRequestSchema, LoginResponseSchema, UserListResponseSchema,
    UserDetailResponseSchema, UserStatsSchema
)
from .model import UserModel, create_user_model

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
