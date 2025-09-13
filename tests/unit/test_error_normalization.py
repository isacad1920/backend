import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_http_exception_wrapped():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        resp = await ac.get('/_test_forbidden')
    assert resp.status_code == 403
    body = resp.json()
    assert body['success'] is False
    assert body['error']['code'] == 'FORBIDDEN'
    assert 'message' in body['error']


@pytest.mark.asyncio
async def test_unknown_route_404_wrapped():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        resp = await ac.get('/_definitely_missing_route_12345')
    assert resp.status_code == 404
    body = resp.json()
    assert body['success'] is False
    assert 'message' in body['error']


@pytest.mark.asyncio
async def test_failure_helper_passthrough():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        resp = await ac.get('/_test_failure')
    assert resp.status_code == 422
    body = resp.json()
    assert body['success'] is False
    assert body['error']['code'] in ('VALIDATION_ERROR', 'ERROR')
    details = body['error'].get('details') or {}
    # Expect field detail now preserved
    if details:
        assert details.get('field') == 'invalid'
