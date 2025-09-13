from generated.prisma import Prisma
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging
import asyncio

logger = logging.getLogger(__name__)

# Create a global Prisma client instance
prisma = Prisma()

# Track the event loop that opened the Prisma HTTP client session to avoid
# "Event is bound to a different event loop" errors under pytest/ASGI.
_prisma_loop_id: int | None = None

async def connect_db():
    """Connect to database with error handling"""
    try:
        await prisma.connect()
        # Record the current running loop ID for later validation
        try:
            loop = asyncio.get_running_loop()
            global _prisma_loop_id
            _prisma_loop_id = id(loop)
        except RuntimeError:
            # No running loop (unlikely here); leave as-is
            pass
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

async def disconnect_db():
    """Disconnect from database with error handling"""
    try:
        await prisma.disconnect()
        # Clear loop binding marker
        global _prisma_loop_id
        _prisma_loop_id = None
        logger.info("Database disconnected successfully")
    except Exception as e:
        logger.error(f"Failed to disconnect from database: {e}")

@asynccontextmanager
async def get_db_session() -> AsyncGenerator[None, None]:
    """Get database session with automatic connection management"""
    await _ensure_connection_for_current_loop()
    try:
        yield prisma
    except Exception as e:
        logger.error(f"Database operation failed: {e}")
        raise

async def get_db() -> Prisma:
    """Get database instance for FastAPI dependency injection"""
    await _ensure_connection_for_current_loop()
    return prisma

async def _ensure_connection_for_current_loop() -> None:
    """Ensure prisma is connected and bound to the current event loop.

    Under pytest/httpx ASGI tests, event loops can differ across requests.
    If the prisma HTTP client was created on a different loop, close and
    reconnect so the underlying httpx.AsyncClient is re-bound correctly.
    """
    global _prisma_loop_id
    try:
        loop = asyncio.get_running_loop()
        current_loop_id = id(loop)
    except RuntimeError:
        current_loop_id = None

    # Connect if not connected
    if not prisma.is_connected():
        await connect_db()
        return

    # If connected but loop changed, recycle the connection
    if _prisma_loop_id is not None and current_loop_id is not None and current_loop_id != _prisma_loop_id:
        try:
            logger.info("Detected event loop change for Prisma client; reconnecting to re-bind HTTP session")
            await disconnect_db()
        except Exception as e:
            logger.warning(f"Error while disconnecting prisma on loop change: {e}")
        await connect_db()
