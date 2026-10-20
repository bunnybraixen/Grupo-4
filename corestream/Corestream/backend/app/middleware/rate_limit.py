"""
Rate limiting sencillo basado en Redis (plan 3.5).

No se usa slowapi ni ninguna dependencia nueva: un contador de ventana fija
por clave (IP, o IP+email) es suficiente para lo que hace falta aquí —
frenar fuerza bruta contra /auth/login — y Redis ya está disponible en toda
la aplicación.

Antes: 25 intentos de login fallidos consecutivos, todos respondidos con 401,
ninguno bloqueado. Verificado en la auditoría inicial.
"""

from __future__ import annotations

import logging

from fastapi import HTTPException, Request, status
from redis.exceptions import RedisError

from app.redis_client import get_redis

_PREFIX = "corestream:ratelimit:"

logger = logging.getLogger("corestream.rate_limit")

# Límites de /auth/login (intentos fallidos por ventana de 5 minutos)
_LOGIN_WINDOW = 300
_LOGIN_MAX_PER_IP = 20
_LOGIN_MAX_PER_EMAIL = 8


def _client_ip(request: Request) -> str:
    # Sin proxy delante todavía (fase 6): request.client.host es la IP real.
    # Cuando haya Nginx, esto deberá leer X-Forwarded-For — lo señala el plan
    # en la entrega a sistemas (fase 10): uvicorn necesita --forwarded-allow-ips
    # para que X-Forwarded-For sea de fiar y no lo pueda falsear el cliente.
    return request.client.host if request.client else "desconocido"


def _login_keys(request: Request, email: str | None) -> list[tuple[str, int]]:
    keys = [(f"login:ip:{_client_ip(request)}", _LOGIN_MAX_PER_IP)]
    if email:
        keys.append((f"login:email:{email.lower().strip()}", _LOGIN_MAX_PER_EMAIL))
    return keys


async def rate_limit_login(request: Request, email: str | None = None) -> None:
    """
    Rechaza con 429 el login si la IP o la cuenta ya agotaron sus intentos
    fallidos. No incrementa nada: solo cuentan los fallos
    (ver `record_failed_login`), así los logins correctos —p. ej. los tests
    E2E— no bloquean a nadie.

    Por IP: 20 fallos/5min contra cualquier cuenta (frena el barrido de
    credenciales). Por cuenta: 8 fallos/5min desde cualquier IP (frena el
    ataque distribuido contra una sola cuenta).

    Si Redis no responde se deja pasar (fail-open) y se registra: es
    preferible a dejar a todos sin poder iniciar sesión.
    """
    try:
        redis = await get_redis()
        for key, max_attempts in _login_keys(request, email):
            full_key = f"{_PREFIX}{key}"
            count = int(await redis.get(full_key) or 0)
            if count >= max_attempts:
                ttl = await redis.ttl(full_key)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Demasiados intentos. Intenta de nuevo más tarde.",
                    headers={"Retry-After": str(max(ttl, 1))},
                )
    except RedisError:
        logger.warning("Rate limit de login no disponible (Redis)", exc_info=True)


async def record_failed_login(request: Request, email: str | None = None) -> None:
    """Suma un intento fallido a los contadores de IP y de cuenta."""
    try:
        redis = await get_redis()
        for key, _ in _login_keys(request, email):
            full_key = f"{_PREFIX}{key}"
            if await redis.incr(full_key) == 1:
                await redis.expire(full_key, _LOGIN_WINDOW)
    except RedisError:
        logger.warning("No se pudo registrar el login fallido (Redis)", exc_info=True)
