"""Central logging configuration utilities.

Provides setup_logging() to configure structured logging for production and
human-readable logging for development. Uses Python's logging.config.dictConfig.
"""
from __future__ import annotations
import logging
from logging.config import dictConfig
from typing import Literal

_FORMATTER_PLAIN = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # pragma: no cover - trivial
        import json, time
        base = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            base["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(base, ensure_ascii=False)

def setup_logging(level: str = "INFO", json: bool = False) -> None:
    """Configure global logging.

    Parameters
    ----------
    level: str
        Logging level name.
    json: bool
        If True, emit JSON logs suitable for production ingestion.
    """
    lvl = getattr(logging, level.upper(), logging.INFO)
    if json:
        formatter = {
            "()": f"{__name__}._JsonFormatter",
        }
    else:
        formatter = {"format": _FORMATTER_PLAIN}

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"default": formatter},
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": lvl,
            }
        },
        "root": {"handlers": ["console"], "level": lvl},
    }
    dictConfig(config)
