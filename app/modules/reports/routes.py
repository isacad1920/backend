"""Unified reports dispatcher (v1 consolidation).

Endpoint: GET /reports or POST /reports
Params:
  type=inventory_valuation|inventory_turnover|sales_daily|ar_aging|income_statement|balance_sheet|cash_flow
  format=json|csv|xlsx|pdf (non-json are placeholders returning message stub)
  async=true -> creates in-memory job record

Jobs:
  GET /reports/jobs
  GET /reports/jobs/{job_id}

Simplified implementation focusing on quick integration; financial report generation delegates
where possible to existing financial ReportService for income_statement/balance_sheet/cash_flow.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query

from app.core.dependencies import get_current_active_user
from app.core.response import paginated_response, success_response
from app.db.prisma import get_db
from app.modules.financial.services.report_service import ReportService
from generated.prisma import Prisma

router = APIRouter(prefix="/reports", tags=["📈 Reports"])

_REPORT_JOBS: dict[str, dict[str, Any]] = {}

SUPPORTED_TYPES = {
    'inventory_valuation',
    'inventory_turnover',
    'sales_daily',
    'ar_aging',
    'income_statement',
    'balance_sheet',
    'cash_flow'
}

NON_JSON_FORMATS = {'csv','xlsx','pdf'}

async def _build_report(*, rtype: str, db: Prisma, current_user, params: dict[str, Any]) -> Any:
    # Minimal branching; placeholders for inventory/sales metrics
    if rtype == 'income_statement':
        svc = ReportService(db)
        return (await svc.generate_income_statement()) .model_dump()  # type: ignore
    if rtype == 'balance_sheet':
        svc = ReportService(db)
        return (await svc.generate_balance_sheet()).model_dump()  # type: ignore
    if rtype == 'cash_flow':
        svc = ReportService(db)
        from datetime import date
        today = date.today()
        return (await svc.generate_cash_flow_statement(start_date=today.replace(day=1), end_date=today, branch_id=None, current_user=current_user)).model_dump()  # type: ignore
    # Placeholders for others
    if rtype == 'inventory_valuation':
        # Could call InventoryService. Keep light.
        return {'report_type': rtype, 'generated_at': datetime.utcnow().isoformat(), 'items': []}
    if rtype == 'inventory_turnover':
        return {'report_type': rtype, 'generated_at': datetime.utcnow().isoformat(), 'rows': []}
    if rtype == 'sales_daily':
        return {'report_type': rtype, 'generated_at': datetime.utcnow().isoformat(), 'series': []}
    if rtype == 'ar_aging':
        return {'report_type': rtype, 'generated_at': datetime.utcnow().isoformat(), 'aging_buckets': {}}
    raise HTTPException(status_code=400, detail='Unsupported report type')

@router.get('')
@router.get('/')
async def dispatch_report_get(
    type: str = Query(..., description='Report type'),
    format: str = Query('json', pattern='^(json|csv|xlsx|pdf)$'),
    async_job: bool = Query(False, alias='async'),
    current_user = Depends(get_current_active_user),
    db: Prisma = Depends(get_db),
):
    if type not in SUPPORTED_TYPES:
        raise HTTPException(status_code=400, detail='Unsupported report type')
    if async_job:
        # Create and immediately (synchronously) complete the job for now
        job_id = str(uuid4())
        _REPORT_JOBS[job_id] = {
            'id': job_id,
            'type': type,
            'status': 'pending',
            'submitted_at': datetime.utcnow().isoformat(),
            'format': format,
            'result': None,
        }
        try:
            data = await _build_report(rtype=type, db=db, current_user=current_user, params={})
            _REPORT_JOBS[job_id].update({
                'status': 'completed',
                'completed_at': datetime.utcnow().isoformat(),
                'result': data if format == 'json' else {'message': 'Generated (placeholder)'}
            })
        except Exception as e:
            _REPORT_JOBS[job_id].update({
                'status': 'failed',
                'error': str(e),
                'completed_at': datetime.utcnow().isoformat()
            })
        return success_response(data={'job_id': job_id, 'status': _REPORT_JOBS[job_id]['status']}, message='Report job submitted')

    # Direct synchronous generation path
    data = await _build_report(rtype=type, db=db, current_user=current_user, params={})
    if format == 'json':
        return success_response(data=data, message='Report generated')
    return success_response(data={'format': format, 'message': 'Report generated (placeholder)', 'type': type}, message='Report generated')

@router.post('')
@router.post('/')
async def dispatch_report_post(
    body: dict[str, Any] = Body(...),
    current_user = Depends(get_current_active_user),
    db: Prisma = Depends(get_db),
):
    type = body.get('type')
    format = body.get('format','json')
    async_job = body.get('async', False)
    if type not in SUPPORTED_TYPES:
        raise HTTPException(status_code=400, detail='Unsupported report type')
    if async_job:
        job_id = str(uuid4())
        _REPORT_JOBS[job_id] = {
            'id': job_id,
            'type': type,
            'status': 'pending',
            'submitted_at': datetime.utcnow().isoformat(),
            'format': format,
            'result': None,
        }
        try:
            data = await _build_report(rtype=type, db=db, current_user=current_user, params=body)
            _REPORT_JOBS[job_id].update({
                'status': 'completed',
                'completed_at': datetime.utcnow().isoformat(),
                'result': data if format == 'json' else {'message': 'Generated (placeholder)'}
            })
        except Exception as e:
            _REPORT_JOBS[job_id].update({
                'status': 'failed',
                'error': str(e),
                'completed_at': datetime.utcnow().isoformat()
            })
        return success_response(data={'job_id': job_id, 'status': _REPORT_JOBS[job_id]['status']}, message='Report job submitted')

    data = await _build_report(rtype=type, db=db, current_user=current_user, params=body)
    if format == 'json':
        return success_response(data=data, message='Report generated')
    return success_response(data={'format': format, 'message': 'Report generated (placeholder)', 'type': type}, message='Report generated')

@router.get('/jobs')
async def list_report_jobs():
    jobs = list(_REPORT_JOBS.values())
    return paginated_response(items=jobs, total=len(jobs), page=1, limit=len(jobs) or 1, message='Report jobs listed')

@router.get('/jobs/{job_id}')
async def get_report_job(job_id: str = Path(...)):
    job = _REPORT_JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Job not found')
    return success_response(data=job, message='Report job retrieved')
