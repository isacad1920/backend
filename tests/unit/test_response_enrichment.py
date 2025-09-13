import json
from fastapi.responses import JSONResponse
from app.core.response import build_success_payload, success_response
from app.core.config import settings


def test_build_success_payload_infers_error_object_from_detail():
    data = {"detail": {"msg": "Not allowed", "type": "permission", "extra": 1}}
    payload = build_success_payload(data=data, message="Forbidden", status_code=403)
    assert payload["success"] is False
    assert payload["error"]["code"] == "permission"
    assert payload["error"]["message"] == "Not allowed"
    assert payload["error"]["details"]["extra"] == 1


def test_build_success_payload_error_simple_string_detail():
    data = {"detail": "Something broke"}
    payload = build_success_payload(data=data, message="Error", status_code=500)
    assert payload["success"] is False
    assert payload["error"]["message"] == "Something broke"


def test_enrichment_meta_included_when_enabled(monkeypatch):
    monkeypatch.setenv("ENABLE_RESPONSE_ENRICHMENT", "true")
    monkeypatch.setenv("INCLUDE_APP_VERSION_META", "true")
    p = build_success_payload(data={}, status_code=200)
    # app_version should appear when enrichment on
    assert "app_version" in p["meta"]

