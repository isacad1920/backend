# SOFinance Financial Integrity & Accuracy Contract

This document defines the mandatory rules ensuring every financial API response
is audit-ready, precise, and derived strictly from persisted data.

## 1. Monetary Representation
| Aspect | Rule |
|-------|------|
| Internal type | Python `Decimal` (context precision 28) |
| Rounding | `ROUND_HALF_UP` |
| Scale | 2 decimal places unless domain explicitly differs (e.g. FX rates) |
| JSON serialization | String (never float) via `serialize_decimal()` |
| Summations | `sum_decimals()` / `safe_decimal_sum()` |
| Prohibited | Binary float arithmetic in domain logic or response shaping |

## 2. Data Provenance
All monetary and balance fields in responses MUST originate from persisted
database state or be recomputable deterministically from persisted components.

Prohibited:
- Heuristic / placeholder values (aging buckets, projected receivables) unless gated.
- Cached approximations that diverge from ledger truth without reconciliation.

## 3. Reconciliation & Validation
Integrity checks are applied for critical endpoints using the decorator
`@financial_integrity` (see `app/middlewares/financial_integrity.py`).

Available strategies:
- `TRANSACTION_TOTAL`: Recompute sum(line_items.amount) == transaction.total.
- `JOURNAL_BALANCED`: Enforce Σ(debit) == Σ(credit) per journal batch.
- (Planned) `ACCOUNT_SNAPSHOT`: Compare stored aggregate vs derived lines.

Violations raise HTTP 500 with structured body:
```
{
  "success": false,
  "error": { "code": "INTEGRITY_ERROR", "details": { ... } }
}
```

## 4. Timestamp Policy
| Aspect | Rule |
|--------|------|
| Storage | Persist native timestamptz in DB (UTC) |
| Serialization | ISO 8601 with `Z` suffix (e.g. `2025-09-14T12:30:00Z`) |
| Source | Always the persisted event timestamp (no regeneration) |
| Helper | `iso_utc()` in `app/core/response.py` |

## 5. Negative Values
Allowed only where business semantics require (e.g. returns, contra accounts).
Validation rules (future work) will map entity → permitted sign patterns.

## 6. Testing Requirements
| Test Category | Purpose |
|---------------|---------|
| Integrity Decorator | Ensure mismatches trigger 500 and successes pass through |
| Decimal Serialization | Assert monetary fields are stringified quantized Decimals |
| Recompute Parity | Re-derive totals (journal, transaction) == response payload |
| Timestamp Shape | Verify all datetime fields end with `Z` and lack offset noise |

## 7. Developer Workflow Checklist
1. Compute all monetary intermediates in `Decimal`.
2. Quantize only at response boundary (avoid early rounding cascade errors).
3. Serialize via `serialize_decimal()`.
4. Apply `@financial_integrity` with appropriate context provider for critical routes.
5. Add or extend tests when introducing new monetary fields.
6. If introducing a derived metric, document the deterministic derivation path.

## 8. Future Enhancements
- Account snapshot validator strategy.
- Automated lint rule scanning for `float(` in financial modules.
- Periodic background integrity audit job with reporting.
- Configurable tolerance (currently strict 0.00) for external rounding discrepancies.

## 9. Glossary
| Term | Definition |
|------|------------|
| Integrity | State where reported values match recomputed ledger truth |
| Reconciliation | Process of deriving authoritative totals from primitive records |
| Quantization | Rounding to a fixed number of decimal places using defined mode |

---
For questions or proposing amendments, open a PR modifying this file and tag
the finance/backend reviewers.
