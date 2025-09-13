"""
Permission management module for custom permission overrides.
"""
from app.modules.permissions.routes import router, legacy_router

__all__ = ["router", "legacy_router"]