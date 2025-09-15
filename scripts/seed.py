#!/usr/bin/env python3
"""Unified seed script for SOFinance.

Idempotent: safe to run multiple times. It will:
  - Ensure core reference data (branch, categories, accounts)
  - Ensure RBAC permission catalog & role mappings
  - Ensure one user per role with deterministic credentials
  - Optionally create a minimal demo sale/payment (disabled by default)

Environment variables:
  SEED_DEMO_TX=1   -> also create 1 demo sale + payment

Credentials (default):
  admin@sofinance.local / AdminPassword123!
  manager@sofinance.local / ManagerPassword123!
  cashier@sofinance.local / CashierPassword123!
  inventory@sofinance.local / InventoryPassword123!
  accountant@sofinance.local / AccountantPassword123!

Run:
  python scripts/seed.py
  or
  python -m scripts.seed
"""
from __future__ import annotations

import asyncio
import os
import sys
from decimal import Decimal
from pathlib import Path
import logging

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import UserRole, settings  # type: ignore
from app.core.security import PasswordManager  # type: ignore
from app.db.prisma import prisma, connect_db, disconnect_db  # type: ignore

logger = logging.getLogger("seed")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

PERMISSIONS = {
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
    "journal": ["read"],
}

ROLE_MATRIX = {
    UserRole.ADMIN: [f"{r}:{a}" for r, acts in PERMISSIONS.items() for a in acts],
    UserRole.MANAGER: [
        *[f"{r}:{a}" for r, acts in PERMISSIONS.items() for a in acts if r not in {"system", "audit"}]
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
        "journal:read",
    ],
}

USERS = [
    ("admin@sofinance.local", "Admin", "User", UserRole.ADMIN, "AdminPassword123!"),
    ("manager@sofinance.local", "Manager", "User", UserRole.MANAGER, "ManagerPassword123!"),
    ("cashier@sofinance.local", "Cashier", "User", UserRole.CASHIER, "CashierPassword123!"),
    ("inventory@sofinance.local", "Inventory", "User", UserRole.INVENTORY_CLERK, "InventoryPassword123!"),
    ("accountant@sofinance.local", "Accountant", "User", UserRole.ACCOUNTANT, "AccountantPassword123!"),
]

async def ensure_permissions():
    for resource, actions in PERMISSIONS.items():
        for action in actions:
            existing = await prisma.permission.find_first(where={"resource": resource, "action": action})
            if not existing:
                await prisma.permission.create(data={"resource": resource, "action": action})
                logger.info("Created permission %s:%s", resource, action)
    for role, perms in ROLE_MATRIX.items():
        for perm in perms:
            resource, action = perm.split(":", 1)
            p = await prisma.permission.find_first(where={"resource": resource, "action": action})
            if not p:
                logger.warning("Missing permission unexpectedly: %s", perm)
                continue
            existing_rp = await prisma.rolepermission.find_first(where={"role": role.value, "permissionId": p.id})
            if not existing_rp:
                await prisma.rolepermission.create(data={"role": role.value, "permissionId": p.id})
                logger.info("Linked %s -> %s", role.value, perm)

async def ensure_branch():
    branch = await prisma.branch.find_first()
    if branch:
        return branch
    return await prisma.branch.create(data={"name": "Main Branch", "address": "HQ", "phone": "000-0000", "isActive": True})

async def ensure_users(branch_id: int):
    for email, first, last, role, pwd in USERS:
        user = await prisma.user.find_first(where={"email": email})
        hashed = PasswordManager.hash_password(pwd)
        if not user:
            await prisma.user.create(data={
                "username": email.split("@")[0],
                "email": email,
                "firstName": first,
                "lastName": last,
                "hashedPassword": hashed,
                "role": role.value,
                "isActive": True,
                "branchId": branch_id,
            })
            logger.info("Created user %s (%s)", email, role.value)
        else:
            await prisma.user.update(where={"id": user.id}, data={"hashedPassword": hashed, "role": role.value, "isActive": True, "branchId": branch_id})

async def ensure_category():
    cat = await prisma.category.find_first(where={"name": "General"})
    if cat:
        return cat
    return await prisma.category.create(data={"name": "General", "description": "Default category", "status": "ACTIVE"})

async def ensure_product(category_id: int):
    prod = await prisma.product.find_first(where={"sku": "SKU-001"})
    if prod:
        return prod
    return await prisma.product.create(data={
        "sku": "SKU-001",
        "name": "Sample Product",
        "description": "Seed product",
        "costPrice": Decimal("10.00"),
        "sellingPrice": Decimal("15.00"),
        "categoryId": category_id,
    })

async def ensure_stock(product_id: int):
    stock = await prisma.stock.find_first(where={"productId": product_id})
    if stock:
        return stock
    return await prisma.stock.create(data={"productId": product_id, "quantity": 100})

async def ensure_accounts(branch_id: int):
    names = ["Cash", "Sales Revenue"]
    existing = await prisma.account.find_many(where={"name": {"in": names}})
    existing_names = {a.name for a in existing}
    created = []
    for name, acct_type in [("Cash", "ASSET"), ("Sales Revenue", "REVENUE")]:
        if name not in existing_names:
            created.append(await prisma.account.create(data={"name": name, "type": acct_type, "currency": "USD", "balance": Decimal("0"), "branchId": branch_id}))
    return existing + created

async def ensure_system_info():
    si = await prisma.systeminfo.find_first()
    if si:
        return si
    return await prisma.systeminfo.create(data={
        "systemName": settings.app_name or "SOFinance System",
        "version": settings.app_version or "v1.0.0",
        "environment": "DEV" if not settings.is_production else "PROD",
        "companyName": "SOFinance",
        "companyEmail": "info@sofinance.local",
        "companyPhone": "000-0000",
        "companyAddress": "HQ",
        "baseCurrency": "USD",
        "timezone": "UTC",
    })

async def optional_demo_sale(admin_email: str):
    admin = await prisma.user.find_first(where={"email": admin_email})
    product = await prisma.product.find_first(where={"sku": "SKU-001"})
    stock = await prisma.stock.find_first(where={"productId": product.id}) if product else None
    cash = await prisma.account.find_first(where={"name": "Cash"})
    if not all([admin, product, stock, cash]):
        return
    sale_exists = await prisma.sale.find_first()
    if sale_exists:
        return
    sale = await prisma.sale.create(data={
        "branchId": admin.branchId,
        "totalAmount": Decimal("15.00"),
        "discount": Decimal("0"),
        "paymentType": "FULL",
        "customerId": None,
        "userId": admin.id,
    })
    await prisma.saleitem.create(data={
        "saleId": sale.id,
        "stockId": stock.id,
        "quantity": 1,
        "price": Decimal("15.00"),
        "subtotal": Decimal("15.00"),
    })
    await prisma.payment.create(data={
        "saleId": sale.id,
        "accountId": cash.id,
        "userId": admin.id,
        "amount": Decimal("15.00"),
        "currency": "USD",
    })
    logger.info("Created demo sale + payment")

async def seed():
    await connect_db()
    try:
        branch = await ensure_branch()
        await ensure_permissions()
        await ensure_users(branch.id)
        cat = await ensure_category()
        prod = await ensure_product(cat.id)
        await ensure_stock(prod.id)
        await ensure_accounts(branch.id)
        await ensure_system_info()
        if os.getenv("SEED_DEMO_TX") == "1":
            await optional_demo_sale("admin@sofinance.local")
        logger.info("Unified seed complete")
    finally:
        await disconnect_db()

if __name__ == "__main__":
    asyncio.run(seed())
