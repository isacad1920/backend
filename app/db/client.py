"""
Database client configuration and connection management.
"""
from ..db.prisma import prisma, connect_db, disconnect_db, get_db_session, get_db

# Database lifecycle management
async def init_db() -> None:
    await connect_db()

async def close_db() -> None:
    await disconnect_db()