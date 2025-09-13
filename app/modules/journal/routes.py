"""
Journal API routes and endpoints.
"""
from typing import List, Optional, Dict, Any
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from fastapi.security import HTTPBearer
import logging

from app.core.dependencies import get_current_user, get_current_active_user
from app.core.response import ResponseBuilder, SuccessResponse, ErrorResponse
from app.db.prisma import get_db
from app.modules.journal.service import create_journal_service
from app.utils.pdf import generate_simple_pdf
from fastapi.responses import StreamingResponse
from app.modules.journal.schema import (
    JournalEntryCreateSchema,
    JournalEntryUpdateSchema,
    JournalEntrySchema,
    JournalEntryListSchema,
    TrialBalanceSchema,
)

security = HTTPBearer()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/journal", tags=["Journal"])


@router.get("/entries", response_model=SuccessResponse[JournalEntryListSchema])
async def get_journal_entries(
    start_date: Optional[date] = Query(None, description="Filter entries from this date"),
    end_date: Optional[date] = Query(None, description="Filter entries up to this date"),
    entry_type: Optional[str] = Query(None, description="Filter by entry type"),
    limit: int = Query(50, description="Number of entries to return"),
    offset: int = Query(0, description="Number of entries to skip"),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """
    📖 Get journal entries
    
    Retrieve accounting journal entries with filtering options.
    """
    try:
        service = create_journal_service(db)
        page = (offset // limit) + 1 if limit > 0 else 1
        entries = await service.get_journal_entries(
            page=page,
            size=limit,
            reference_type=entry_type,
            start_date=start_date,
            end_date=end_date,
        )
        return ResponseBuilder.success(data=entries, message="Journal entries retrieved successfully")
    except Exception as e:
        logger.error(f"Failed to retrieve journal entries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve journal entries: {str(e)}")


@router.get("/entries/{entry_id}", response_model=SuccessResponse[JournalEntrySchema])
async def get_journal_entry_details(
    entry_id: int = Path(..., description="Journal entry ID"),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """
    📄 Get journal entry details
    
    Retrieve detailed information for a specific journal entry.
    """
    try:
        service = create_journal_service(db)
        entry = await service.get_journal_entry(entry_id)
        return ResponseBuilder.success(data=entry, message="Journal entry details retrieved successfully")
    except Exception as e:
        logger.error(f"Failed to retrieve journal entry details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve journal entry details: {str(e)}")


@router.post("/entries", response_model=SuccessResponse[JournalEntrySchema], status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    entry_data: JournalEntryCreateSchema,
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """
    ✍️ Create a new journal entry
    
    Create a manual journal entry for accounting purposes.
    """
    try:
        # Server-side enforcement: Account transfers branch rules
        # Non-admin users can only transfer between accounts within their own branch.
        # Admins can transfer across branches.
        ref_type_norm = (entry_data.reference_type or "").upper().replace("-", "_")
        if ref_type_norm == "ACCOUNT_TRANSFER":
            # Normalize role
            role_val = getattr(current_user, "role", None)
            role_str = role_val.value if hasattr(role_val, "value") else (str(role_val).split(".")[-1] if role_val else "")
            is_admin = role_str.upper() == "ADMIN"

            if not is_admin:
                # Resolve user's branch id
                user_branch_id = getattr(current_user, "branchId", None) or getattr(current_user, "branch_id", None)
                try:
                    user_branch_id = int(user_branch_id) if user_branch_id is not None else None
                except Exception:
                    user_branch_id = None

                if user_branch_id is None:
                    raise HTTPException(status_code=403, detail="Branch is required for transfers")

                # Collect involved account IDs from lines
                account_ids = sorted({int(l.account_id) for l in entry_data.lines if l.account_id is not None})
                if len(account_ids) < 2:
                    raise HTTPException(status_code=400, detail="Transfer must involve at least two accounts")

                # Fetch accounts and validate branch membership
                accounts = await db.account.find_many(where={"id": {"in": account_ids}})
                if not accounts or len(accounts) != len(account_ids):
                    raise HTTPException(status_code=400, detail="One or more accounts not found")

                # All accounts must belong to the user's branch
                mismatches = [a.id for a in accounts if getattr(a, "branchId", None) != user_branch_id]
                if mismatches:
                    raise HTTPException(status_code=403, detail="Inter-branch transfers require admin role")

        service = create_journal_service(db)
        entry = await service.create_journal_entry(entry_data, created_by_user_id=current_user.id)
        return ResponseBuilder.success(data=entry, message="Journal entry created successfully")
    except Exception as e:
        logger.error(f"Failed to create journal entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create journal entry: {str(e)}")

@router.put("/entries/{entry_id}", response_model=SuccessResponse[JournalEntrySchema])
async def update_journal_entry(
    entry_id: int = Path(..., description="Journal entry ID"),
    update_data: JournalEntryUpdateSchema = ..., 
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """
    ✏️ Update a journal entry
    """
    try:
        service = create_journal_service(db)
        entry = await service.update_journal_entry(entry_id, update_data)
        return ResponseBuilder.success(data=entry, message="Journal entry updated successfully")
    except Exception as e:
        logger.error(f"Failed to update journal entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update journal entry: {str(e)}")

@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_journal_entry(
    entry_id: int = Path(..., description="Journal entry ID"),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """
    🗑️ Delete a journal entry
    """
    try:
        service = create_journal_service(db)
        await service.delete_journal_entry(entry_id)
        return ResponseBuilder.success(data=None, message="Journal entry deleted")
    except Exception as e:
        logger.error(f"Failed to delete journal entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete journal entry: {str(e)}")


@router.get("/trial-balance", response_model=SuccessResponse[TrialBalanceSchema])
async def get_trial_balance(
    as_of_date: Optional[date] = Query(None, description="Trial balance as of this date"),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """
    ⚖️ Generate trial balance
    
    Create a trial balance report showing all account balances.
    """
    try:
        service = create_journal_service(db)
        tb = await service.get_trial_balance(as_of_date=as_of_date)
        return ResponseBuilder.success(data=tb, message="Trial balance generated successfully")
    except Exception as e:
        logger.error(f"Failed to generate trial balance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate trial balance: {str(e)}")

@router.get("/entries/{entry_id}/export.pdf")
async def export_journal_entry_pdf(entry_id: int, current_user = Depends(get_current_active_user), db = Depends(get_db)):
    """Generate a PDF for the journal entry."""
    try:
        service = create_journal_service(db)
        entry = await service.get_journal_entry(entry_id)
        lines = [
            f"Date: {entry.date}",
            f"Reference: {entry.reference_type} {entry.reference_id}",
            "",
            "Lines:",
        ] + [f"{l.account_name or l.account_id}: DR {l.debit}  CR {l.credit}   {l.description or ''}" for l in entry.lines] + [
            "",
            f"Balanced: {entry.is_balanced}",
        ]
        pdf = generate_simple_pdf(title=f"Journal Entry #{entry.id}", lines=lines)
        filename = f"journal_entry_{entry.id}.pdf"
        return StreamingResponse(iter([pdf]), media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename={filename}"
        })
    except Exception as e:
        logger.error(f"Failed to export journal entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export journal entry: {str(e)}")

@router.get("/trial-balance/export.pdf")
async def export_trial_balance_pdf(as_of_date: Optional[date] = None, current_user = Depends(get_current_active_user), db = Depends(get_db)):
    """Generate a PDF for the trial balance."""
    try:
        service = create_journal_service(db)
        tb = await service.get_trial_balance(as_of_date=as_of_date)
        lines = [
            "",
        ] + [f"{l.account_name}: DR {l.debit_balance}   CR {l.credit_balance}" for l in tb.lines] + [
            "",
            f"Total Debits: {tb.total_debits}",
            f"Total Credits: {tb.total_credits}",
            f"Balanced: {tb.is_balanced}",
        ]
        pdf = generate_simple_pdf(title=f"Trial Balance", subtitle=f"As of {tb.as_of_date}", lines=lines)
        return StreamingResponse(iter([pdf]), media_type="application/pdf", headers={
            "Content-Disposition": "attachment; filename=trial_balance.pdf"
        })
    except Exception as e:
        logger.error(f"Failed to export trial balance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export trial balance: {str(e)}")


@router.get("/chart-of-accounts")
async def get_chart_of_accounts(
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """
    📊 Get chart of accounts
    
    Retrieve the complete chart of accounts structure.
    """
    try:
        # Pull accounts from DB
        accounts = await db.account.find_many(order={"id": "asc"})
        data = [
            {
                "id": a.id,
                "name": a.name,
                "type": a.type,
                "branch_id": a.branchId,
            }
            for a in accounts
        ]
        return ResponseBuilder.success(data=data, message="Chart of accounts retrieved successfully")
    except Exception as e:
        logger.error(f"Failed to retrieve chart of accounts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chart of accounts: {str(e)}")


@router.get("/account-balances")
async def get_account_balances(
    account_code: Optional[str] = Query(None, description="Specific account code"),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """
    💰 Get account balances
    
    Retrieve current balances for all accounts or a specific account.
    """
    try:
        # Compute balances from journal lines
        lines = await db.journalentryline.find_many(include={"account": True})
        totals: dict[int, Dict[str, Any]] = {}
        for l in lines:
            aid = l.accountId
            if aid not in totals:
                totals[aid] = {
                    "account_id": aid,
                    "account_name": l.account.name if l.account else str(aid),
                    "debit": 0,
                    "credit": 0,
                }
            totals[aid]["debit"] += float(l.debit)
            totals[aid]["credit"] += float(l.credit)
        data = []
        for aid, t in totals.items():
            balance = t["debit"] - t["credit"]
            data.append({
                "account_id": aid,
                "account_name": t["account_name"],
                "balance": balance,
                "balance_type": "debit" if balance >= 0 else "credit",
            })
        if account_code:
            # account_code maps poorly; allow filtering by id as string
            data = [d for d in data if str(d["account_id"]) == account_code]
            if not data:
                raise HTTPException(status_code=404, detail="Account not found")
        return ResponseBuilder.success(data=data, message="Account balances retrieved successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve account balances: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve account balances: {str(e)}")


@router.get("/audit-trail")
async def get_audit_trail(
    start_date: Optional[date] = Query(None, description="Audit trail start date"),
    end_date: Optional[date] = Query(None, description="Audit trail end date"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    limit: int = Query(100, description="Number of audit entries to return"),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db),
):
    """
    🔍 Get audit trail
    
    Retrieve audit trail of all journal entry changes and transactions.
    """
    try:
        # Read from AuditLog table
        where = {}
        if user_id:
            where["userId"] = user_id
        if start_date or end_date:
            where["createdAt"] = {}
            if start_date:
                where["createdAt"]["gte"] = start_date
            if end_date:
                where["createdAt"]["lte"] = end_date
        logs = await db.auditlog.find_many(
            where=where,
            take=limit,
            order={"createdAt": "desc"},
            include={"user": True},
        )
        audit_entries = [
            {
                "id": l.id,
                "timestamp": l.createdAt,
                "user_id": l.userId,
                "user_name": f"{l.user.firstName} {l.user.lastName}" if l.user else None,
                "action": l.action,
                "entity_type": l.entityType,
                "entity_id": l.entityId,
                "description": None,
                "old_values": l.oldValues,
                "new_values": l.newValues,
            }
            for l in logs
        ]
        return ResponseBuilder.success(
            data={
                "audit_entries": audit_entries,
                "total_count": len(audit_entries),
                "filters": {"start_date": start_date, "end_date": end_date, "user_id": user_id},
            },
            message="Audit trail retrieved successfully",
        )
    except Exception as e:
        logger.error(f"Failed to retrieve audit trail: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve audit trail: {str(e)}")
