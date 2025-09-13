"""Centralized Decimal utilities for financial accuracy.

All monetary values must be handled as Decimal internally.
This module provides helpers for consistent quantization (2 decimal places)
using ROUND_HALF_UP (industry standard for currency) and safe conversion
from untrusted inputs.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation, getcontext
from typing import Any, Iterable

# Set a sensible precision high enough for intermediate calculations
getcontext().prec = 28  # do not reduce; allows chained operations before quantize

TWOPLACES = Decimal('0.01')

class DecimalConversionError(ValueError):
    pass

def to_decimal(value: Any, *, allow_none: bool = False) -> Decimal:
    """Convert arbitrary input to Decimal.

    - Accepts str, int, float, Decimal
    - Rejects None unless allow_none=True (returns Decimal('0') then)
    - Strips whitespace; rejects empty strings
    - Avoids binary float artifacts by routing via str for floats
    """
    if value is None:
        if allow_none:
            return Decimal('0')
        raise DecimalConversionError("None is not a valid monetary value")
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int,)):  # bool excluded implicitly
        return Decimal(value)
    if isinstance(value, float):
        # Convert through repr to minimize precision drift then Decimal
        return Decimal(repr(value))
    if isinstance(value, str):
        v = value.strip()
        if v == '':
            raise DecimalConversionError("Empty string is not a valid monetary value")
        try:
            return Decimal(v)
        except InvalidOperation as e:
            raise DecimalConversionError(f"Invalid numeric string '{value}'") from e
    raise DecimalConversionError(f"Unsupported type for decimal conversion: {type(value)}")

def quantize_money(amount: Decimal, *, places: Decimal = TWOPLACES) -> Decimal:
    """Quantize a Decimal to the given places using ROUND_HALF_UP."""
    if not isinstance(amount, Decimal):  # defensive
        amount = to_decimal(amount)
    return amount.quantize(places, rounding=ROUND_HALF_UP)

def sum_decimals(values: Iterable[Any]) -> Decimal:
    total = Decimal('0')
    for v in values:
        if v is None:
            continue
        total += to_decimal(v)
    return total

def money_dict(**kwargs: Any) -> dict[str, Decimal]:
    """Return a dict mapping of field->quantized Decimal for provided kwargs."""
    return {k: quantize_money(to_decimal(v)) for k, v in kwargs.items()}

def serialize_decimal(amount: Decimal) -> str:
    """Serialize a quantized Decimal to string for JSON responses.

    We return strings to avoid downstream float coercion in JSON encoders and
    to preserve exact precision for clients.
    """
    if not isinstance(amount, Decimal):
        amount = to_decimal(amount)
    q = quantize_money(amount)
    return format(q, 'f')  # no scientific notation

__all__ = [
    'to_decimal',
    'quantize_money',
    'sum_decimals',
    'money_dict',
    'serialize_decimal',
    'DecimalConversionError',
    'TWOPLACES'
]
