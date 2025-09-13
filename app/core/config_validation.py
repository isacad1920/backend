"""Runtime configuration validation helpers.

Provides a lightweight sanity check that critical environment variables
are present and appear valid. This is intentionally minimal so as not to
block startup for non-critical warnings.
"""
from __future__ import annotations
from typing import List, Tuple
import os
import logging

logger = logging.getLogger(__name__)

REQUIRED_VARS = [
    "DATABASE_URL",
    "SECRET_KEY",
]

RECOMMENDED_VARS = [
    "BACKEND_CORS_ORIGINS",
    "REDIS_URL",
]

def validate_env(strict: bool = False) -> Tuple[bool, List[str]]:
    """Validate required environment variables.

    Returns (ok, messages). If strict and a required var is missing, raises
    an exception.
    """
    messages: List[str] = []
    ok = True
    for var in REQUIRED_VARS:
        if not os.getenv(var):
            msg = f"Missing required environment variable: {var}"
            messages.append(msg)
            ok = False
    for var in RECOMMENDED_VARS:
        if not os.getenv(var):
            messages.append(f"Recommended variable not set: {var}")
    secret = os.getenv("SECRET_KEY", "")
    if secret and len(secret) < 32:
        messages.append("SECRET_KEY should be at least 32 characters")
    if strict and not ok:
        raise RuntimeError("Environment validation failed: " + "; ".join(messages))
    return ok, messages

if __name__ == "__main__":  # Manual invocation helper
    success, msgs = validate_env()
    for m in msgs:
        level = logging.INFO if success else logging.ERROR
        # Differentiate required vs recommended issues for clarity
        if m.startswith("Missing required"):
            level = logging.ERROR
        elif m.startswith("SECRET_KEY should"):
            level = logging.WARNING
        logger.log(level, m)
    if success:
        logger.info("Environment OK")
    else:
        logger.error("Environment INVALID")
