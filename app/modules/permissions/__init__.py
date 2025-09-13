"""
Permission management module for custom permission overrides.
"""
from app.modules.permissions.routes import legacy_router, router

__all__ = ["router", "legacy_router"]