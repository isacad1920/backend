"""
Modules package initialization.
"""
from app.modules.branches import router as branches_router
from app.modules.products import category_router, product_router
from app.modules.sales import router as sales_router
from app.modules.users import auth_router, router as users_router

__all__ = [
    "users_router", 
    "auth_router",
    "branches_router",
    "product_router", 
    "category_router",
    "sales_router"
]
