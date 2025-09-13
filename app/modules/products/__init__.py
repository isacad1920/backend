"""
Products module initialization.
"""
from fastapi import APIRouter

from .model import CategoryModel, ProductModel
from .routes import category_router, product_router
from .schema import (
    CategoryCreateSchema,
    CategoryResponseSchema,
    CategoryUpdateSchema,
    ProductCreateSchema,
    ProductResponseSchema,
    ProductUpdateSchema,
)
from .service import create_category_service, create_product_service

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
