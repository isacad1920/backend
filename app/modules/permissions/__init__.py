"""Permissions module export for normalized RBAC routes ONLY (legacy compat removed)."""
from fastapi import APIRouter
from .routes import router as _rbac_router

router = APIRouter()
router.include_router(_rbac_router)

__all__ = ["router"]