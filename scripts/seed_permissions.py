"""Seed base RBAC permissions and role assignments.

Usage:
  python scripts/seed_permissions.py

Idempotent: safe to run multiple times. Only inserts missing permissions or role mappings.

Matrix (can be tuned later):
  products: read/write/delete
  categories: read/write/delete
  sales: read/write/delete
  payments: read/write
  inventory: read/write/delete
  accounts: read/write/delete
  reports: read/generate
  customers: read/write/delete
  stock: read/write/delete
  audit: read
  system: manage

Roles:
  ADMIN: implicit all (no need to persist every mapping but we seed for clarity)
  MANAGER: broad operational (no system:manage, no audit:read, limited deletes maybe kept)
  CASHIER: sales/payments/products read, sales/write, payments/write, customers read/write
  INVENTORY_CLERK: inventory + products + stock (no deletes on accounts/payments)
  ACCOUNTANT: accounts read/write, payments read, reports read/generate, sales read

A permission string is (resource:action).
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Iterable

# Ensure project root is on sys.path when executed directly (python scripts/seed_permissions.py)
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import UserRole
from app.db.prisma import prisma, connect_db, disconnect_db

logger = logging.getLogger(__name__)

# Canonical permission catalog
PERMISSIONS: dict[str, Iterable[str]] = {
    "products": ["read", "write", "delete"],
    "categories": ["read", "write", "delete"],
    "sales": ["read", "write", "delete"],
    "payments": ["read", "write"],
    "inventory": ["read", "write", "delete"],
    "accounts": ["read", "write", "delete"],
    "reports": ["read", "generate"],
    "customers": ["read", "write", "delete"],
    "stock": ["read", "write", "delete"],
    "audit": ["read"],
    "system": ["manage"],
    # Add journal permission surfaced in ROLE_MATRIX to avoid warning during seeding
    "journal": ["read"],
}

# Role -> list of permission strings (resource:action)
ROLE_MATRIX: dict[UserRole, list[str]] = {
    UserRole.ADMIN: [f"{r}:{a}" for r, acts in PERMISSIONS.items() for a in acts],
    UserRole.MANAGER: [
        # broad operational (exclude system:manage)
        *[f"{r}:{a}" for r, acts in PERMISSIONS.items() for a in acts if r not in {"system", "audit"}],
    ],
    UserRole.CASHIER: [
        "sales:read", "sales:write",
        "payments:read", "payments:write",
        "products:read",
        "customers:read", "customers:write",
    ],
    UserRole.INVENTORY_CLERK: [
        "products:read", "products:write",
        "inventory:read", "inventory:write",
        "stock:read", "stock:write",
        "categories:read",
    ],
    UserRole.ACCOUNTANT: [
        "accounts:read", "accounts:write",
        "payments:read",
        "reports:read", "reports:generate",
        "sales:read",
        "journal:read",  # journal not yet in PERMISSIONS catalog but may appear
    ],
}

async def seed():
    await connect_db()
    try:
        # Insert permissions
        for resource, actions in PERMISSIONS.items():
            for action in actions:
                existing = await prisma.permission.find_first(
                    where={"resource": resource, "action": action}
                )
                if not existing:
                    await prisma.permission.create(
                        data={"resource": resource, "action": action}
                    )
                    logger.info("Created permission %s:%s", resource, action)
        # Map role permissions
        for role, perms in ROLE_MATRIX.items():
            for perm in perms:
                resource, action = perm.split(":", 1)
                p = await prisma.permission.find_first(
                    where={"resource": resource, "action": action}
                )
                if not p:
                    logger.warning("Permission missing unexpectedly: %s", perm)
                    continue
                existing_rp = await prisma.rolepermission.find_first(
                    where={"role": role.value, "permissionId": p.id}
                )
                if not existing_rp:
                    await prisma.rolepermission.create(
                        data={"role": role.value, "permissionId": p.id}
                    )
                    logger.info("Linked %s -> %s", role.value, perm)
        logger.info("RBAC seeding complete")
    finally:
        await disconnect_db()

if __name__ == "__main__":
    try:
        asyncio.run(seed())
    except ModuleNotFoundError as e:
        print("[RBAC Seeder] Module import failed:", e)
        print("Attempted sys.path:", sys.path)
        print("Run from project root, e.g.:\n  python scripts/seed_permissions.py\n  or\n  python -m scripts.seed_permissions")
        raise
