from fastapi.responses import JSONResponse

from app.core.response import ResponseBuilder, success_response


def extract(json_response: JSONResponse):
    import json
    return json.loads(json_response.body)


def test_success_response_infers_success_true_for_200():
    resp = success_response(data={"a": 1}, status_code=200)
    payload = extract(resp)
    assert payload["success"] is True
    assert payload["error"] is None


def test_success_response_infers_success_false_for_401():
    resp = success_response(message="Unauthorized", status_code=401)
    p = extract(resp)
    assert p["success"] is False
    # error field becomes empty dict when success False (shape consistency)
    assert p["error"] == {}


def test_success_response_force_success_override():
    resp = success_response(message="Accepted but flagged", status_code=202, force_success=False)
    p = extract(resp)
    assert p["success"] is False


def test_response_builder_success_meta_and_force():
    resp = ResponseBuilder.success(data={"x": 5}, status_code=418, meta={"note": "teapot"})
    p = extract(resp)
    assert p["success"] is False  # inferred from 418
    # Enrichment may add keys (e.g., app_version); ensure original meta survived
    assert p["meta"]["note"] == "teapot"


def test_response_builder_force_success():
    resp = ResponseBuilder.success(data=None, status_code=500, force_success=True)
    p = extract(resp)
    assert p["success"] is True
