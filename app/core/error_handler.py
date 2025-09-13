"""Centralized error normalization.

Wraps HTTPException and unexpected exceptions into the standardized envelope
using failure_response helper. Attach as a middleware or via exception handlers
inside FastAPI app factory.
"""
import logging
from collections.abc import Callable

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.response import failure_response
from app.core.exceptions import APIError

logger = logging.getLogger(__name__)


class NormalizedErrorMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next: Callable):  # type: ignore[override]
		try:
			response = await call_next(request)
		except APIError as ae:  # First: our structured API errors
			resp = failure_response(
				message=ae.message,
				status_code=ae.status_code,
				errors=ae.details or None,
				code=ae.error_code,
			)
			resp.headers['x-normalized-error'] = '1'
			return resp
		except HTTPException as he:  # FastAPI HTTP errors
			code = None
			detail = he.detail
			details_dict = {}
			if isinstance(detail, dict):
				message = detail.get('message') or detail.get('msg') or detail.get('detail') or 'Request failed'
				if 'code' in detail and isinstance(detail['code'], str):
					code = detail['code']
				details_dict = {k: v for k, v in detail.items() if k not in ('message','msg','detail','code')}
			else:
				message = str(detail) if detail else 'Request failed'
			resp = failure_response(message=message, status_code=he.status_code, errors=details_dict or None, code=code)
			resp.headers['x-normalized-error'] = '1'
			return resp
		except Exception as e:  # Unhandled exceptions -> 500 envelope
			logger.exception("Unhandled exception")
			return failure_response(message="Internal server error", status_code=500, errors={'exc': str(e)}, code='INTERNAL_ERROR')

		# Post-process non-enveloped error responses (e.g., 404 for unknown route)
		try:
			if response.status_code >= 400:
				# If already normalized (our middleware created it), return as-is
				if response.headers.get('x-normalized-error') == '1':
					return response
				body_bytes = getattr(response, 'body', None)
				if body_bytes:
					import json
					try:
						parsed = json.loads(body_bytes)
					except Exception:
						return failure_response(message=f"HTTP {response.status_code}", status_code=response.status_code)
					if isinstance(parsed, dict):
						# Already standardized failure envelope
						if parsed.get('success') is False and 'error' in parsed:
							return response
						# New success envelope: {'success': True, 'message':..., 'data': ...}
						if parsed.get('success') is True and 'data' in parsed and 'error' in parsed:
							return response
						# FastAPI default error format
						if 'detail' in parsed:
							return failure_response(message=str(parsed.get('detail')), status_code=response.status_code)
				# Fallback
				return failure_response(message=f"HTTP {response.status_code}", status_code=response.status_code)
		except Exception:  # pragma: no cover - defensive
			logger.exception("Post-processing error normalization failed")
		return response


def register_error_middleware(app):
	"""Helper to register the middleware (called in app factory)."""
	app.add_middleware(NormalizedErrorMiddleware)
	return app

