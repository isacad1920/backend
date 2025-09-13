"""
Utilities for normalizing attribute/key access across camelCase and snake_case.
"""
from typing import Any, Optional


def get_any(obj: Any, key_camel: str, key_snake: Optional[str] = None, default: Any = None) -> Any:
    """Get attribute or dict key preferring camelCase then snake_case.
    - obj can be a model or dict
    - key_snake defaults to a snake_case version of key_camel if not provided
    """
    try:
        if hasattr(obj, key_camel):
            return getattr(obj, key_camel)
    except Exception:
        pass
    key_snake = key_snake or _to_snake(key_camel)
    if isinstance(obj, dict):
        if key_camel in obj:
            return obj.get(key_camel)
        return obj.get(key_snake, default)
    try:
        if hasattr(obj, key_snake):
            return getattr(obj, key_snake)
    except Exception:
        pass
    return default


def _to_snake(name: str) -> str:
    """Convert a camelCase or PascalCase string to snake_case."""
    out = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0 and (not name[i-1].isupper()):
            out.append('_')
        out.append(ch.lower())
    return ''.join(out)
