"""
Middleware de correlación de peticiones (plan fase 8).

Asigna un request_id por petición, lo propaga a través de un contextvar
(para que app/logging_config.py lo incluya en cada línea de log emitida
durante esa petición, sin tener que pasarlo explícitamente por cada
función) y lo devuelve en la cabecera X-Request-ID de la respuesta.
"""

from __future__ import annotations

import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

_request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def get_request_id() -> str | None:
    return _request_id_ctx.get()


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        token = _request_id_ctx.set(request_id)
        try:
            response = await call_next(request)
        finally:
            _request_id_ctx.reset(token)

        response.headers["X-Request-ID"] = request_id
        return response
