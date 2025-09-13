"""Route-level financial integrity decorator.

Applies reconciliation / integrity checks before returning responses for
critical financial endpoints. Designed to be lightweight and explicit.

Usage:

    @financial_integrity(validate=[Validate.TRANSACTION_TOTAL])
    async def get_sale_details(...):
        ... return success_response(data=sale_dict)

Validation strategies map to functions in app.modules.financial.integrity.
Failures raise HTTPException 500 with structured error details for auditability.
"""
from __future__ import annotations

from functools import wraps
from typing import Any, Awaitable, Callable, Iterable

from fastapi import HTTPException

from app.modules.financial.integrity import (
    IntegrityError,
    validate_no_unbalanced_journal,
    validate_transaction_total,
)
from app.utils.decimal_utils import to_decimal, serialize_decimal, quantize_money

class Validate:
    TRANSACTION_TOTAL = 'transaction_total'
    JOURNAL_BALANCED = 'journal_balanced'

Validator = Callable[[dict[str, Any], dict[str, Any]], None]

def _apply_transaction_total(payload: dict[str, Any], context: dict[str, Any]):
    tx = context.get('transaction_obj')
    line_items = context.get('line_items', [])
    if tx is None:
        return
    validate_transaction_total(tx, line_items)
    # Optionally rewrite payload monetary fields to serialized decimals
    for field in ('total_amount', 'total', 'net_total'):
        if field in payload:
            try:
                payload[field] = serialize_decimal(to_decimal(payload[field]))
            except Exception:
                pass

def _apply_journal_balanced(payload: dict[str, Any], context: dict[str, Any]):
    lines = context.get('journal_lines') or []
    if not lines:
        return
    validate_no_unbalanced_journal(lines)

STRATEGY_MAP: dict[str, Callable[[dict[str, Any], dict[str, Any]], None]] = {
    Validate.TRANSACTION_TOTAL: _apply_transaction_total,
    Validate.JOURNAL_BALANCED: _apply_journal_balanced,
}

def financial_integrity(validate: Iterable[str] | None = None, context_provider: Callable[..., Awaitable[dict[str, Any]]] | None = None):
    """Decorator to enforce financial integrity before returning response.

    Args:
        validate: Iterable of validation strategy keys (see Validate class)
        context_provider: async callable that receives the same args/kwargs
            as the route handler and returns a dict with any required objects
            (e.g. {'transaction_obj': sale, 'line_items': sale.items}).
    """
    strategies = list(validate or [])

    def decorator(func: Callable[..., Awaitable[Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ctx: dict[str, Any] = {}
            if context_provider:
                try:
                    ctx = await context_provider(*args, **kwargs) or {}
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Integrity context failure: {e}")
            try:
                result = await func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

            # If the handler returned a JSONResponse already we cannot mutate easily
            # Expect success_response style dict or JSONResponse. If JSONResponse, pass-through.
            from fastapi.responses import JSONResponse
            if isinstance(result, JSONResponse):
                return result

            # Assume success_response payload shape if dict with keys
            payload = result
            if not isinstance(payload, dict):
                return result  # non-standard; skip

            data_section = payload.get('data') if 'data' in payload else payload

            for strat in strategies:
                applier = STRATEGY_MAP.get(strat)
                if not applier:
                    continue
                try:
                    applier(data_section if isinstance(data_section, dict) else {}, ctx)
                except IntegrityError as ie:
                    raise HTTPException(status_code=500, detail={
                        'message': str(ie),
                        'details': ie.details
                    })

            return result
        return wrapper
    return decorator

__all__ = [
    'financial_integrity',
    'Validate'
]
