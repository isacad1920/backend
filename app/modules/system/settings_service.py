"""
Utilities for working with SystemSetting key-value store.
"""

from generated.prisma import Prisma


class SettingsKV:
    def __init__(self, db: Prisma):
        self.db = db

    async def get_all(self) -> dict[str, str]:
        rows = await self.db.systemsetting.find_many()
        return {r.key: r.value for r in rows}

    async def get(self, key: str) -> str | None:
        rec = await self.db.systemsetting.find_unique(where={"key": key})
        return rec.value if rec else None

    async def set(self, key: str, value: str) -> None:
        existing = await self.db.systemsetting.find_unique(where={"key": key})
        if existing:
            await self.db.systemsetting.update(where={"key": key}, data={"value": value})
        else:
            await self.db.systemsetting.create(data={"key": key, "value": value})
