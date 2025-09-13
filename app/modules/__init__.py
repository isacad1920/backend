"""
Modules package initialization.
"""
from app.modules.users import router as users_router, auth_router
from app.modules.branches import router as branches_router  
from app.modules.products import product_router, category_router
from app.modules.sales import router as sales_router

__all__ = [
    "users_router", 
    "auth_router",
    "branches_router",
    "product_router", 
    "category_router",
    "sales_router"
]
