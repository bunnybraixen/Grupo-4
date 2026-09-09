"""
Logging estructurado para CoreStream (plan fase 8).

Antes: print() repartido por todo app/, y el manejador global de
excepciones (main.py) registraba con logging.error(...) sin exc_info — los
500 no dejaban traza. Los tres bugs de MissingGreenlet de la fase 2 solo
salieron a la luz porque uvicorn los imprime por su cuenta, no porque
nuestro propio logging los hubiera capturado.

Este módulo configura el logger raíz una sola vez, en el arranque de la
aplicación (main.py lifespan), con salida JSON (una línea por evento, fácil
de indexar si algún día hay un colector) e incluye el request_id de
middleware.request_id cuando existe.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone

from app.middleware.request_id import get_request_id


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        request_id = get_request_id()
        if request_id:
            payload["request_id"] = request_id

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "info") -> None:
    """Reemplaza los handlers del logger raíz. Llamar una sola vez, al arrancar."""
    root = logging.getLogger()
    root.setLevel(level.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root.handlers.clear()
    root.addHandler(handler)

    # uvicorn.access ya imprime una línea por request en su propio formato;
    # dejarlo pasar por nuestro handler JSON en vez de duplicar salida.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv_logger = logging.getLogger(name)
        uv_logger.handlers.clear()
        uv_logger.propagate = True
