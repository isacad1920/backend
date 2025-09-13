#!/usr/bin/env python3
"""Utility script to wipe all application data and insert initial seed records.

CAUTION: This irreversibly deletes ALL data from the database (development use only).

Usage:
    python scripts/reset_and_seed.py --force

Optional flags:
    --force              Skip interactive confirmation.
    --no-seed            Perform deletion only (no seed data inserted).
    --mode {minimal,full}  Choose seeding depth (default: full).
    --sales N            Generate N demo sales (full mode only, default: 1).

Seeded Data Overview:
    - Branch: Default Branch
    - Users: admin (ADMIN), manager (MANAGER)
    - Category: General
    - Product: Sample Product (with stock)
    - Customer: Walk-in Customer
    - Accounts: Cash, Sales Revenue
    - SystemInfo: default DEV system info
    - UserPermission: broad permissions for admin

This uses delete_many() on each model in a dependency-safe order instead of raw TRUNCATE
to avoid quoting/casing pitfalls with model names.
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

# Ensure project root on path when executing directly
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import settings  # type: ignore
from app.core.security import PasswordManager  # type: ignore
from app.db.prisma import prisma  # type: ignore
from generated.prisma import fields  # type: ignore

logger = logging.getLogger("reset_and_seed")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Deletion order (children before parents to satisfy FK constraints)
DELETE_ORDER: list[str] = [
    "notification",
    "revokedtoken",
    "userpermission",
    "auditlog",
    "journalentryline",
    "payment",
    "returnitem",
    "returnsale",
    "saleitem",
    "sale",
    "branchorderitem",
    "branchorder",
    "accounttransfer",
    "stock",
    "product",
    "account",
    "backup",
    "customer",
    "category",
    "journalentry",  # after lines
    "systeminfo",
    "user",
    "branch",
]

# Mapping model delegate attribute names (lowercase) to nicer label
LABELS = {name: name.capitalize() for name in DELETE_ORDER}

async def wipe_database() -> None:
    logger.info("Connecting to database...")
    if not prisma.is_connected():
        await prisma.connect()
    logger.info("Deleting data from all tables (dependency-safe order)...")
    for delegate_name in DELETE_ORDER:
        delegate = getattr(prisma, delegate_name, None)
        if delegate is None:
            logger.warning(f"Delegate not found for '{delegate_name}', skipping")
            continue
        try:
            res = await delegate.delete_many(where={})  # type: ignore
            logger.info(f"Cleared {res.count if hasattr(res,'count') else 'unknown'} rows from {delegate_name}")
        except Exception as e:
            logger.error(f"Failed clearing {delegate_name}: {e}")
            raise
    logger.info("All tables cleared.")

async def seed_database(mode: str = "full", sales_count: int = 1) -> None:
    """Insert seed data.

    Modes:
        minimal: Only core reference & auth data (branch, users, category, product, stock, accounts, system info, permissions).
        full:    Full dataset including transactional examples (sales, payments, returns, transfers, journal, orders, logs, backup, token, notification).

    sales_count applies only in full mode; creates that many simple sales spaced 1 minute apart.
    """
    logger.info(f"Seeding initial data (mode={mode}, sales_count={sales_count}) ...")

    # Branch
    branch = await prisma.branch.create(data={  # type: ignore
        "name": "Main Branch",
        "address": "HQ",
        "phone": "000-0000",
        "isActive": True,
    })

    # Users
    admin_password_plain = "AdminPassword123!"
    manager_password_plain = "ManagerPassword123!"

    admin = await prisma.user.create(data={  # type: ignore
        "username": "admin",
        "email": "admin@sofinance.local",
        "firstName": "Admin",
        "lastName": "User",
        "hashedPassword": PasswordManager.hash_password(admin_password_plain),
        "role": "ADMIN",
        "isActive": True,
        "branchId": branch.id,
    })

    manager = await prisma.user.create(data={  # type: ignore
        "username": "manager",
        "email": "manager@sofinance.local",
        "firstName": "Manager",
        "lastName": "User",
        "hashedPassword": PasswordManager.hash_password(manager_password_plain),
        "role": "MANAGER",
        "isActive": True,
        "branchId": branch.id,
    })

    # Category
    category = await prisma.category.create(data={  # type: ignore
        "name": "General",
        "description": "Default category",
        "status": "ACTIVE",
    })

    # Product
    product = await prisma.product.create(data={  # type: ignore
        "sku": "SKU-001",
        "name": "Sample Product",
        "description": "First product",
        "costPrice": Decimal("10.00"),
        "sellingPrice": Decimal("15.00"),
        "categoryId": category.id,
    })

    # Stock
    stock = await prisma.stock.create(data={  # type: ignore
        "productId": product.id,
        "quantity": 100,
    })

    # Customer
    customer = await prisma.customer.create(data={  # type: ignore
        "name": "Walk-in Customer",
        "type": "INDIVIDUAL",
        "creditLimit": Decimal("0"),
        "balance": Decimal("0"),
        "totalPurchases": Decimal("0"),
        "status": "ACTIVE",
    })

    # Accounts
    cash_account = await prisma.account.create(data={  # type: ignore
        "name": "Cash",
        "type": "ASSET",
        "currency": "USD",
        "balance": Decimal("0"),
        "branchId": branch.id,
    })

    sales_rev_account = await prisma.account.create(data={  # type: ignore
        "name": "Sales Revenue",
        "type": "REVENUE",
        "currency": "USD",
        "balance": Decimal("0"),
        "branchId": branch.id,
    })

    # System Info
    system_info = await prisma.systeminfo.create(data={  # type: ignore
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

    # Permissions for admin (broad allow)
    await prisma.userpermission.create(data={  # type: ignore
        "userId": admin.id,
        "resource": "*",
        "actions": fields.Json({"create": True, "read": True, "update": True, "delete": True}),
    })

    # ----- Extended seed for transactional tables -----
    # Create a demo sale
    if mode == "full":
        created_sales_ids = []
        for i in range(max(1, sales_count)):
            sale_total = Decimal("15.00")
            sale = await prisma.sale.create(data={  # type: ignore
                "branchId": branch.id,
                "totalAmount": sale_total,
                "discount": Decimal("0"),
                "paymentType": "FULL",
                "customerId": customer.id,
                "userId": admin.id,
            })
            created_sales_ids.append(sale.id)
            sale_item = await prisma.saleitem.create(data={  # type: ignore
                "saleId": sale.id,
                "stockId": stock.id,
                "quantity": 1,
                "price": Decimal("15.00"),
                "subtotal": Decimal("15.00"),
            })
            await prisma.payment.create(data={  # type: ignore
                "saleId": sale.id,
                "accountId": cash_account.id,
                "userId": admin.id,
                "amount": Decimal("15.00"),
                "currency": "USD",
            })
            # Only create a return for the very first sale
            if i == 0:
                return_sale = await prisma.returnsale.create(data={  # type: ignore
                    "originalId": sale.id,
                    "reason": "Customer return sample",
                })
                await prisma.returnitem.create(data={  # type: ignore
                    "returnId": return_sale.id,
                    "saleItemId": sale_item.id,
                    "quantity": 1,
                    "refundAmount": Decimal("15.00"),
                })
        logger.info(f"Created {len(created_sales_ids)} sale(s)")

    if mode == "full":
        # Accounts for transfers & journal
        bank_account = await prisma.account.create(data={  # type: ignore
            "name": "Bank",
            "type": "ASSET",
            "currency": "USD",
            "balance": Decimal("0"),
            "branchId": branch.id,
        })
        # Account transfer (cash -> bank)
        transfer = await prisma.accounttransfer.create(data={  # type: ignore
            "fromAccountId": cash_account.id,
            "toAccountId": bank_account.id,
            "amount": Decimal("50.00"),
            "currency": "USD",
            "status": "SENT",
            "note": "Initial funding move",
        })
        # Journal entry with two lines referencing first sale id if present
        reference_sale = await prisma.sale.find_first()  # type: ignore
        journal = await prisma.journalentry.create(data={  # type: ignore
            "referenceType": "Seed",
            "referenceId": reference_sale.id if reference_sale else "N/A",
        })
        await prisma.journalentryline.create(data={  # type: ignore
            "entryId": journal.id,
            "accountId": cash_account.id,
            "debit": Decimal("15.00"),
            "credit": Decimal("0"),
            "description": "Sale cash receipt",
        })
        await prisma.journalentryline.create(data={  # type: ignore
            "entryId": journal.id,
            "accountId": sales_rev_account.id,
            "debit": Decimal("0"),
            "credit": Decimal("15.00"),
            "description": "Sale revenue",
        })
        # Branch order & item
        branch_order = await prisma.branchorder.create(data={  # type: ignore
            "branchId": branch.id,
            "requestedById": admin.id,
            "approvedById": manager.id,
            "status": "APPROVED",
        })
        await prisma.branchorderitem.create(data={  # type: ignore
            "branchOrderId": branch_order.id,
            "stockId": stock.id,
            "requestedQty": 5,
            "approvedQty": 5,
            "sentQty": 5,
            "receivedQty": 5,
        })
        # Audit logs
        first_sale = await prisma.sale.find_first()  # type: ignore
        if first_sale:
            await prisma.auditlog.create(data={  # type: ignore
                "userId": admin.id,
                "action": "CREATE",
                "entityType": "Sale",
                "entityId": str(first_sale.id),
                "newValues": fields.Json({"total": "15.00"}),
                "severity": "INFO",
                "ipAddress": "127.0.0.1",
                "userAgent": "seed-script",
            })
        await prisma.auditlog.create(data={  # type: ignore
            "userId": admin.id,
            "action": "TRANSFER",
            "entityType": "AccountTransfer",
            "entityId": str(transfer.id),
            "newValues": fields.Json({"amount": "50.00"}),
            "severity": "INFO",
            "ipAddress": "127.0.0.1",
            "userAgent": "seed-script",
        })
        # Backup record placeholder
        await prisma.backup.create(data={  # type: ignore
            "type": "FULL",
            "location": "local://backups",
            "fileName": "initial_seed_backup",
            "sizeMB": 0.0,
            "status": "SUCCESS",
            "createdById": admin.id,
        })
        # Revoked token sample (expires in 1h UTC)
        await prisma.revokedtoken.create(data={  # type: ignore
            "jti": str(uuid.uuid4()),
            "token": "dummy.revoked.token",
            "reason": "Seed example",
            "expiresAt": datetime.now(UTC) + timedelta(hours=1),
            "revokedBy": admin.id,
        })
        # Notification sample
        await prisma.notification.create(data={  # type: ignore
            "userId": admin.id,
            "type": "info",
            "title": "Welcome",
            "message": "System initialized with seed data.",
            "data": fields.Json({"module": "seed"}),
        })

    logger.info("Seed data inserted successfully.")
    logger.info("Credentials:")
    logger.info(f"  Admin -> username: admin  email: admin@sofinance.local  password: {admin_password_plain}")
    logger.info(f"  Manager -> username: manager email: manager@sofinance.local password: {manager_password_plain}")

async def summarize_counts() -> None:
    """Log row counts for quick verification after seeding."""
    counts = {}
    for delegate_name in DELETE_ORDER[::-1]:  # original logical dependency order reversed back (parents first) is fine
        delegate = getattr(prisma, delegate_name, None)
        if delegate is None:
            continue
        try:
            value = await delegate.count()  # type: ignore
            counts[delegate_name] = value
        except Exception:
            counts[delegate_name] = "?"
    logger.info("Post-seed row counts:")
    for k, v in counts.items():
        logger.info(f"  {k}: {v}")

async def main(force: bool, no_seed: bool, mode: str, sales_count: int) -> None:
    if not force:
        confirm = input("THIS WILL DELETE ALL DATA. Type 'DELETE ALL' to continue: ").strip()
        if confirm != "DELETE ALL":
            print("Aborted.")
            return
    try:
        await wipe_database()
        if not no_seed:
            await seed_database(mode=mode, sales_count=sales_count)
            await summarize_counts()
    finally:
        if prisma.is_connected():
            await prisma.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset (wipe) database and seed initial data.")
    parser.add_argument("--force", action="store_true", help="Skip interactive confirmation.")
    parser.add_argument("--no-seed", action="store_true", help="Do not insert seed data after wipe.")
    parser.add_argument("--mode", choices=["minimal", "full"], default="full", help="Seed mode depth.")
    parser.add_argument("--sales", type=int, default=1, help="Number of demo sales to generate (full mode only).")
    args = parser.parse_args()
    asyncio.run(main(force=args.force, no_seed=args.no_seed, mode=args.mode, sales_count=args.sales))
