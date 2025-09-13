"""Audit log listing endpoints."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import UserRole
from app.core.dependencies import get_current_active_user, require_role
from app.core.response import paginated_response
from app.db.prisma import get_db
from generated.prisma import Prisma

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/logs")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    action: str | None = Query(None, description="Filter by action enum (e.g. CREATE_USER)"),
    entity_type: str | None = Query(None, description="Filter by entity type"),
    user_id: int | None = Query(None, description="Filter by user id"),
    severity: str | None = Query(None, description="Severity level"),
    search: str | None = Query(None, description="Search entity id contains"),
    current_user = Depends(get_current_active_user),
    # Restrict to admin and manager roles (SUPER_ADMIN not defined in UserRole enum)
    _role = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER))
    ,db: Prisma = Depends(get_db),
):
    try:
        where: dict[str, Any] = {}
        if action:
            where['action'] = action
        if entity_type:
            where['entityType'] = {'contains': entity_type, 'mode': 'insensitive'}
        if user_id is not None:
            where['userId'] = user_id
        if severity:
            where['severity'] = severity
        if search:
            where['entityId'] = {'contains': search, 'mode': 'insensitive'}
        skip = (page - 1) * page_size
        total = await db.auditlog.count(where=where)
        rows = await db.auditlog.find_many(
            where=where,
            order={'createdAt': 'desc'},
            skip=skip,
            take=page_size,
            include={'user': True}
        )
        items = []
        for r in rows:
            items.append({
                'id': r.id,
                'timestamp': r.createdAt,
                'action': r.action,
                'entity_type': r.entityType,
                'entity_id': r.entityId,
                'user_id': r.userId,
                'username': r.user.username if r.user else None,
                'severity': r.severity,
            })
        return paginated_response(
            items=items,
            total=total,
            page=page,
            limit=page_size,
            message="Audit logs retrieved",
            meta_extra={
                'filters': {k: v for k, v in {
                    'action': action,
                    'entity_type': entity_type,
                    'user_id': user_id,
                    'severity': severity,
                    'search': search
                }.items() if v is not None},
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list audit logs: {e}")