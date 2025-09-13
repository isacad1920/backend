"""
Products module initialization.
"""
from fastapi import APIRouter
from .routes import product_router, category_router
from .service import create_product_service, create_category_service
from .model import ProductModel, CategoryModel
from .schema import (
    ProductCreateSchema, ProductUpdateSchema, ProductResponseSchema,
    CategoryCreateSchema, CategoryUpdateSchema, CategoryResponseSchema
)

# Create a unified router for consistency with other modules
router = APIRouter()
router.include_router(product_router)
router.include_router(category_router)

__all__ = [
    "router",          # Unified router for consistency
    "product_router",
    "category_router", 
    "create_product_service",
    "create_category_service",
    "ProductModel",
    "CategoryModel",
    "ProductCreateSchema",
    "ProductUpdateSchema",
    "ProductResponseSchema",
    "CategoryCreateSchema",
    "CategoryUpdateSchema", 
    "CategoryResponseSchema"
]
