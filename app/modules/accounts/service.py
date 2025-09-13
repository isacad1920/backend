from __future__ import annotations
from typing import Optional, List, Dict, Any
from decimal import Decimal
from fastapi import HTTPException
from generated.prisma import Prisma

class AccountService:
    def __init__(self, db: Prisma):
        self.db = db

    async def create_account(self, data: Dict[str, Any]):
        # Basic validation of type/currency could be expanded
        try:
            rec = await self.db.account.create(data={
                "name": data["name"],
                "type": data["type"],
                "currency": data.get("currency", "USD"),
                "branchId": data.get("branch_id"),
            })
            return rec
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to create account: {e}")

    async def list_accounts(self, *, page: int, limit: int, search: Optional[str], type_: Optional[str], branch_id: Optional[int], active: Optional[bool]):
        where: Dict[str, Any] = {}
        if search:
            where["name"] = {"contains": search, "mode": "insensitive"}
        if type_:
            where["type"] = type_
        if branch_id is not None:
            where["branchId"] = branch_id
        if active is not None:
            where["active"] = active
        skip = (page - 1) * limit
        total = await self.db.account.count(where=where)
        rows = await self.db.account.find_many(where=where, skip=skip, take=limit, order={"createdAt": "desc"})
        return total, rows

    async def get_account(self, account_id: int):
        acc = await self.db.account.find_unique(where={"id": account_id})
        if not acc:
            raise HTTPException(status_code=404, detail="Account not found")
        return acc

    async def update_account(self, account_id: int, data: Dict[str, Any]):
        _ = await self.get_account(account_id)
        try:
            upd = await self.db.account.update(where={"id": account_id}, data={k: v for k, v in {
                "name": data.get("name"),
            }.items() if v is not None})
            return upd
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to update account: {e}")

    async def close_account(self, account_id: int):
        acc = await self.get_account(account_id)
        # Idempotent close: if already inactive, just return
        if getattr(acc, "active", True) is False:
            return acc
        try:
            return await self.db.account.update(where={"id": account_id}, data={"active": False})
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to close account: {e}")

    async def list_entries(self, account_id: int, page: int, limit: int):
        await self.get_account(account_id)
        skip = (page - 1) * limit
        where = {"accountId": account_id}
        total = await self.db.journalentryline.count(where=where)
        rows = await self.db.journalentryline.find_many(
            where=where,
            skip=skip,
            take=limit,
            order={"id": "desc"},
            include={"entry": True}
        )
        return total, rows
