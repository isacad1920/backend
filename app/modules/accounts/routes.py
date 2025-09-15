"""Account management API routes."""
from fastapi import APIRouter, Depends, Query
from typing import Optional, Any
from app.core.dependencies import get_current_active_user, require_role
from app.core.config import UserRole
from app.core.response import success_response, paginated_response
from app.db.prisma import get_db
from generated.prisma import Prisma
from .schema import AccountCreate, AccountUpdate
from .service import AccountService
from app.core.audit import AuditAction, AuditSeverity
from app.core.audit_decorator import audit_log
from app.core.response import iso_utc

router = APIRouter(prefix="/accounts", tags=["🏦 Accounts"]) 

# Helpers
async def get_service(db: Prisma = Depends(get_db)) -> AccountService:
    return AccountService(db)

@router.post("/", summary="Create account")
@audit_log(AuditAction.CREATE, "account", AuditSeverity.INFO)
async def create_account(payload: AccountCreate, svc: AccountService = Depends(get_service), current_user = Depends(get_current_active_user), _role = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER, UserRole.ACCOUNTANT))):
    rec = await svc.create_account(payload.model_dump())
    return success_response(data={
        "id": rec.id,
        "name": rec.name,
        "type": rec.type,
        "currency": rec.currency,
        "balance": str(rec.balance),
    "active": getattr(rec, 'isActive', True),
        "branch_id": getattr(rec, 'branchId', None),
        "created_at": iso_utc(rec.createdAt),
        "updated_at": iso_utc(rec.updatedAt),
    }, message="Account created")

@router.get("/", summary="List accounts")
async def list_accounts(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = None,
    type: Optional[str] = Query(None, alias="type"),
    branch_id: Optional[int] = None,
    active: Optional[bool] = None,
    svc: AccountService = Depends(get_service),
    _user = Depends(get_current_active_user),
    _role = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER, UserRole.ACCOUNTANT))
):
    total, rows = await svc.list_accounts(page=page, limit=limit, search=search, type_=type, branch_id=branch_id, active=active)
    items = [{
        "id": r.id,
        "name": r.name,
        "type": r.type,
        "currency": r.currency,
        "balance": str(r.balance),
    "active": getattr(r, 'isActive', True),
        "branch_id": getattr(r, 'branchId', None),
        "created_at": iso_utc(r.createdAt),
        "updated_at": iso_utc(r.updatedAt),
    } for r in rows]
    return paginated_response(items=items, total=total, page=page, limit=limit, message="Accounts listed", meta_extra={"filters": {k: v for k, v in {"search": search, "type": type, "branch_id": branch_id, "active": active}.items() if v is not None}})

@router.get("/{account_id}", summary="Get account")
async def get_account(account_id: int, svc: AccountService = Depends(get_service), _user = Depends(get_current_active_user), _role = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER, UserRole.ACCOUNTANT))):
    r = await svc.get_account(account_id)
    return success_response(data={
        "id": r.id,
        "name": r.name,
        "type": r.type,
        "currency": r.currency,
        "balance": str(r.balance),
    "active": getattr(r, 'isActive', True),
        "branch_id": getattr(r, 'branchId', None),
        "created_at": iso_utc(r.createdAt),
        "updated_at": iso_utc(r.updatedAt),
    }, message="Account retrieved")

@router.patch("/{account_id}", summary="Update account")
@audit_log(AuditAction.UPDATE, "account", AuditSeverity.INFO)
async def update_account(account_id: int, payload: AccountUpdate, svc: AccountService = Depends(get_service), _user = Depends(get_current_active_user), _role = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER, UserRole.ACCOUNTANT))):
    r = await svc.update_account(account_id, payload.model_dump())
    return success_response(data={
        "id": r.id,
        "name": r.name,
        "type": r.type,
        "currency": r.currency,
        "balance": str(r.balance),
    "active": getattr(r, 'isActive', True),
        "branch_id": getattr(r, 'branchId', None),
        "created_at": iso_utc(r.createdAt),
        "updated_at": iso_utc(r.updatedAt),
    }, message="Account updated")

@router.post("/{account_id}/close", summary="Close (deactivate) account")
@audit_log(AuditAction.UPDATE, "account", AuditSeverity.WARNING)
async def close_account(account_id: int, svc: AccountService = Depends(get_service), _user = Depends(get_current_active_user), _role = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER, UserRole.ACCOUNTANT))):
    r = await svc.close_account(account_id)
    return success_response(data={
        "id": r.id,
        "name": r.name,
        "type": r.type,
        "currency": r.currency,
        "balance": str(r.balance),
        # Underlying model uses isActive; maintain response key 'active' for backward compatibility
        "active": getattr(r, 'isActive', True),
        "branch_id": getattr(r, 'branchId', None),
        "created_at": iso_utc(r.createdAt),
        "updated_at": iso_utc(r.updatedAt),
    }, message="Account closed")

@router.get("/{account_id}/entries", summary="List journal entries for account")
async def list_account_entries(account_id: int, page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200), svc: AccountService = Depends(get_service), _user = Depends(get_current_active_user), _role = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER, UserRole.ACCOUNTANT))):
    total, rows = await svc.list_entries(account_id, page, limit)
    items = []
    for ln in rows:
        items.append({
            "id": ln.id,
            "entry_id": ln.entryId,
            "debit": str(ln.debit),
            "credit": str(ln.credit),
            "description": ln.description,
            "created_at": None,  # journal line has no direct timestamp, use entry date
            "entry_date": iso_utc(ln.entry.date),
        })
    return paginated_response(items=items, total=total, page=page, limit=limit, message="Account entries listed")
