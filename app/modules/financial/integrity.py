"""Financial integrity and reconciliation utilities.

These functions recompute authoritative financial figures from base ledger
data (journal lines, transactions) and compare them with stored aggregates.
They are designed to be lightweight and callable inside request handlers
prior to emitting responses for critical endpoints.

Contract:
    - All returned dicts use quantized Decimal values (serialized later)
    - Raise IntegrityError on mismatches beyond tolerance
    - Provide remediation metadata (fields mismatching, expected, actual)
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Iterable

from app.utils.decimal_utils import to_decimal, quantize_money, sum_decimals

TOLERANCE = Decimal('0.00')  # strict; set to 0.01 if minor rounding drift allowed

class IntegrityError(Exception):
    def __init__(self, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.details = details or {}

@dataclass
class BalanceSnapshot:
    account_id: int
    debit: Decimal
    credit: Decimal
    balance: Decimal  # debit - credit (standard sign convention)

def recompute_account_balance(journal_lines: Iterable[Any]) -> tuple[Decimal, Decimal, Decimal]:
    debit_total = Decimal('0')
    credit_total = Decimal('0')
    for line in journal_lines:
        # Expect attributes debit, credit (already Decimal or convertible)
        d = to_decimal(getattr(line, 'debit', 0) or 0)
        c = to_decimal(getattr(line, 'credit', 0) or 0)
        debit_total += d
        credit_total += c
    bal = debit_total - credit_total
    return quantize_money(debit_total), quantize_money(credit_total), quantize_money(bal)

def validate_account_snapshot(account_obj: Any, journal_lines: Iterable[Any]):
    stored_debit = to_decimal(getattr(account_obj, 'total_debit', 0) or 0)
    stored_credit = to_decimal(getattr(account_obj, 'total_credit', 0) or 0)
    stored_balance = to_decimal(getattr(account_obj, 'balance', stored_debit - stored_credit))
    recomputed_debit, recomputed_credit, recomputed_balance = recompute_account_balance(journal_lines)
    mismatches: dict[str, dict[str, str]] = {}
    def _chk(label: str, stored: Decimal, recomputed: Decimal):
        if (stored - recomputed).copy_abs() > TOLERANCE:
            mismatches[label] = {
                'stored': str(quantize_money(stored)),
                'expected': str(recomputed)
            }
    _chk('total_debit', stored_debit, recomputed_debit)
    _chk('total_credit', stored_credit, recomputed_credit)
    _chk('balance', stored_balance, recomputed_balance)
    if mismatches:
        raise IntegrityError("Account balance integrity violation", details=mismatches)
    return {
        'total_debit': str(recomputed_debit),
        'total_credit': str(recomputed_credit),
        'balance': str(recomputed_balance)
    }

def validate_transaction_total(transaction_obj: Any, line_items: Iterable[Any]):
    stored_total = to_decimal(getattr(transaction_obj, 'total_amount', getattr(transaction_obj, 'total', 0)) or 0)
    lines_total = sum_decimals(getattr(li, 'amount', 0) or 0 for li in line_items)
    lines_total_q = quantize_money(lines_total)
    if (stored_total - lines_total_q).copy_abs() > TOLERANCE:
        raise IntegrityError("Transaction total mismatch", details={
            'stored_total': str(stored_total),
            'expected': str(lines_total_q)
        })
    return {'total_amount': str(lines_total_q)}

def validate_no_unbalanced_journal(lines: Iterable[Any]):
    total_debit = sum_decimals(getattr(l, 'debit', 0) or 0 for l in lines)
    total_credit = sum_decimals(getattr(l, 'credit', 0) or 0 for l in lines)
    if (total_debit - total_credit).copy_abs() > TOLERANCE:
        raise IntegrityError("Journal not balanced", details={
            'total_debit': str(quantize_money(total_debit)),
            'total_credit': str(quantize_money(total_credit))
        })
    return {
        'total_debit': str(quantize_money(total_debit)),
        'total_credit': str(quantize_money(total_credit))
    }

__all__ = [
    'IntegrityError',
    'validate_account_snapshot',
    'validate_transaction_total',
    'validate_no_unbalanced_journal',
    'recompute_account_balance'
]
